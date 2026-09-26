/*
 * timer_core.c - the supply board's timer, the pure logic (L41b2).
 *
 * Every sequence is spec sec. 4 (firmware/preamp_timer/spec/timer_spec.md),
 * the LDR law spec sec. 5. Choices the spec left open are marked "L41b2" and
 * written in the spec and the L41b2 report.
 *
 * FALSO_n: a deliberate defect, compiled in only by the host tests' fake
 * builds (test/run_host_tests.sh) to prove that each test can fail.
 */
#include "timer_core.h"

#include <math.h>
#include <stddef.h>

#ifndef FALSO
#define FALSO 0
#endif

#define K_B 1.380649e-23f
#define Q_E 1.602176634e-19f
#if FALSO == 17
#undef T_FADE_US
#define T_FADE_US 3000000u                    /* Td = 3 s instead of 6 */
#endif
#define SAT_ADD(a, b) ((a) > UINT32_MAX - (b) ? UINT32_MAX : (a) + (b))

/* ------------------------------------------------------------ the law */
float timer_law_vx(float i, float t_c, const timer_cal_t *cal)
{
    const float iref = (LAW_V5 - LAW_VREF) / LAW_R_REF;
    float vt = K_B * (t_c + 273.15f) / Q_E;
#if FALSO == 11
    vt = K_B * (25.0f + 273.15f) / Q_E;      /* no temperature compensation */
#endif
    float vx = LAW_VREF + vt * logf(i / iref);
    if (cal)
        vx += cal->off + cal->r_ohm * i;
    return vx;
}

uint16_t timer_law_code(float i, float t_c, const timer_cal_t *cal)
{
    const float ga = 1.0f / LAW_R_A, gc = 1.0f / LAW_R_C;
    float vx = timer_law_vx(i, t_c, cal);
    float vdac = (vx * (ga + gc) - LAW_VREF * gc) / ga;
    float c = vdac / LAW_DAC_FS * 4096.0f;
    if (c < 0.0f)
        return 0;
    if (c > 4095.0f)
        return 4095;
    return (uint16_t)lroundf(c);
}

/* The v4 profile (ADR-039) with the top of ADR-050: log-linear between the
 * points, i.e. linear in ln I. */
typedef struct { float d, i; } punto_t;

static float interp_log(const punto_t *p, int n, float d)
{
    if (d <= p[0].d)
        return p[0].i;
    for (int k = 1; k < n; k++) {
        if (d <= p[k].d) {
            float u = (d - p[k - 1].d) / (p[k].d - p[k - 1].d);
            float l0 = logf(p[k - 1].i), l1 = logf(p[k].i);
            return expf(l0 + u * (l1 - l0));
        }
    }
    return p[n - 1].i;
}

float timer_profile_series(float d)
{
    static const punto_t s[] = {
#if FALSO == 12
        {0.0f, 20e-3f},                       /* the old top: NC-038 */
#else
        {0.0f, LDR_I_TOP},                    /* ADR-050 */
#endif
        {0.1f, 0.2e-3f}, {0.45f, 4.5e-6f},
        {0.75f, 0.19e-6f},                    /* the dark knee (ADR-039) */
        {0.8f, LDR_I_IDLE}, {1.0f, LDR_I_IDLE}};
    return interp_log(s, (int)(sizeof s / sizeof s[0]), d);
}

float timer_profile_shunt(float d)
{
    static const punto_t p[] = {
        {0.0f, LDR_I_IDLE}, {0.5f, LDR_I_IDLE}, {1.0f, LDR_I_TOP}};
    return interp_log(p, (int)(sizeof p / sizeof p[0]), d);
}

int timer_cal_fit_x(timer_cal_t *cal, float t_c,
                    float want1, float read1, float x1,
                    float want2, float read2, float x2)
{
    if (!(read1 > 0.0f) || !(read2 > 0.0f) || x1 == x2)
        return 0;
    float vt = K_B * (t_c + 273.15f) / Q_E;
    float e1 = vt * logf(want1 / read1);
    float e2 = vt * logf(want2 / read2);
    if (fabsf(e1) > CAL_E_MAX || fabsf(e2) > CAL_E_MAX)
        return 0;
    /* the two reads must be two currents, not one read twice */
    if (fmaxf(x1, x2) < 2.0f * fminf(x1, x2))
        return 0;
    float r = (e1 - e2) / (x1 - x2);
    float off = e2 - r * x2;
    /* the correction where it will be used (the wanted currents) */
    if (fabsf(off + r * want1) > CAL_E_MAX || fabsf(off + r * want2) > CAL_E_MAX)
        return 0;
#if FALSO == 13
    off = -off;                               /* the correction with the wrong sign */
#endif
    cal->off += off;
    cal->r_ohm += r;
    return 1;
}

int timer_cal_fit(timer_cal_t *cal, float t_c, float i_top_want, float i_top_read,
                  float i_lo_want, float i_lo_read)
{
    return timer_cal_fit_x(cal, t_c, i_top_want, i_top_read, i_top_read,
                           i_lo_want, i_lo_read, i_lo_read);
}

const char *timer_stato_nome(uint8_t stato)
{
    static const char *n[] = {"STANDBY", "ACCENSIONE", "MUTO", "RILASCIO", "MUSICA",
                              "INSERZIONE", "SPEGNIMENTO", "BUCO_RETE", "GUASTO"};
    return stato < sizeof n / sizeof n[0] ? n[stato] : "?";
}

/* ------------------------------------------------------------ helpers */
static void deb_update(timer_deb_t *b, uint8_t raw, uint32_t dt)
{
    if (raw == b->level) {
        b->cand = raw;
        b->t = 0;
        return;
    }
    if (raw != b->cand) {
        b->cand = raw;
        b->t = 0;
        return;
    }
    b->t = SAT_ADD(b->t, dt);
#if FALSO == 7
    if (b->t >= 2000u)                        /* 2 ms instead of 20 */
#else
    if (b->t >= T_DEBOUNCE_US)
#endif
        b->level = raw;
}

static void vai(timer_state_t *st, timer_stato_t s, uint8_t fase)
{
    st->stato = s;
    st->fase = fase;
    st->t_fase = 0;
}

static void set_permit(timer_state_t *st, uint8_t v)
{
    if (!v && st->permit_req)
        st->t_permit_low = 0;
    st->permit_req = v;
}

static int rails_ok(const timer_in_t *in)
{
    return in->v_sup_p > V_SUP_P_OK && in->v_sup_m < V_SUP_M_OK;
}

static int alim_ok(const timer_in_t *in)
{
    return rails_ok(in) && in->v_sup_vr > V_SUP_VR_OK && in->v_md <= V_MD_ABSENT;
}

static int rail_fail(const timer_in_t *in)
{
    return in->v_sup_p < V_SUP_P_FAIL || in->v_sup_m > V_SUP_M_FAIL ||
           in->v_sup_vr < V_SUP_VR_FAIL;
}

static int mains_absent(const timer_in_t *in)
{
    return in->v_md > V_MD_ABSENT;
}

static float netto(float i, float zero)
{
#if FALSO == 19
    (void)zero;
    return i;                                 /* the zero not taken off */
#else
    return i - zero;
#endif
}

static void cal_abort(timer_state_t *st)
{
    st->cal_active = 0;
    /* a calibration interrupted before its read-back is not trusted */
    if (st->cal_verifica == 1)
        st->cal_s = st->cal_prima;
    else if (st->cal_verifica == 2)
        st->cal_p = st->cal_prima;
    st->cal_verifica = 0;
}

/* fit string s (1 series, 2 shunt) and arm the read-back */
static void cal_fit(timer_state_t *st, uint8_t s, float t_c, float top_read, float lo_read)
{
    timer_cal_t *c = s == 1 ? &st->cal_s : &st->cal_p;
    st->cal_prima = *c;
    if (timer_cal_fit(c, t_c, LDR_I_TOP, top_read, LDR_I_CAL_LO, lo_read)) {
        st->cal_verifica = s;
    } else {
        st->n_cal_reject++;
        st->cal_verifica = 0;
    }
}

/* the read-back of the corrected top, after it settled; returns 1 if kept */
static int cal_verifica(timer_state_t *st, float i_letta)
{
    uint8_t s = st->cal_verifica;
    st->cal_verifica = 0;
    if (!s)
        return 0;
#if FALSO == 21
    (void)i_letta;
    return 1;
#else
    if (fabsf(i_letta / LDR_I_TOP - 1.0f) <= CAL_VERIFY_TOL)
        return 1;
    if (s == 1)
        st->cal_s = st->cal_prima;
    else
        st->cal_p = st->cal_prima;
    st->n_cal_reject++;
    return 0;
#endif
}

/* The immediate mute of a mains hole or a fault: no fade (spec 4.5, 4.6). */
static void mute_subito(timer_state_t *st)
{
    st->mute_req = 0;
#if FALSO != 5
    set_permit(st, 0);
#endif
    st->d = 1.0f;
    cal_abort(st);
}

static void entra_buco(timer_state_t *st, const timer_in_t *in)
{
    mute_subito(st);
    st->mains_absent = (uint8_t)mains_absent(in);
    st->rail_dipped = 0;
    vai(st, ST_BUCO_RETE, 0);
}

static void entra_guasto(timer_state_t *st)
{
    mute_subito(st);
    vai(st, ST_GUASTO, 0);
}

static void entra_muto(timer_state_t *st, uint8_t calibrated)
{
    st->cal_done_here = calibrated;
    vai(st, ST_MUTO, 0);
}

static void entra_rilascio(timer_state_t *st)
{
    /* spec 4.3 step 1: both requests at once; the hardware energises
     * PERMIT_CMD no later than MUTE_CMD (D522) */
    st->mute_req = 1;
    set_permit(st, 1);
    cal_abort(st);
    vai(st, ST_RILASCIO, 0);
}

/* The insertion of spec 4.2, shared by INSERZIONE and SPEGNIMENTO (4.4 step
 * 1): fase 0 fade, 1 hold 0.5 s, 2 Delta, then returns 1 (done). */
static int inserisci(timer_state_t *st, uint32_t dt)
{
    switch (st->fase) {
    case 0:
        st->d += (float)dt / (float)T_FADE_US;
        if (st->d >= 1.0f) {
            st->d = 1.0f;
            st->fase = 1;
            st->t_fase = 0;
        }
        return 0;
    case 1:
#if FALSO == 3
        if (st->t_fase >= 100000u) {          /* 0.1 s instead of 0.5 */
#else
        if (st->t_fase >= T_MUTE_HOLD_US) {
#endif
            st->mute_req = 0;
            st->fase = 2;
            st->t_fase = 0;
        }
        return 0;
    case 2:
#if FALSO == 4
        if (1) {                              /* PERMIT_REQ with MUTE_REQ, no Delta */
#else
        if (st->t_fase >= T_DELTA_US) {
#endif
            set_permit(st, 0);
            return 1;
        }
        return 0;
    default:
        return 1;
    }
}

/* ------------------------------------------------------------ the core */
void timer_init(timer_state_t *st, const timer_in_t *in)
{
    (void)in;
    *st = (timer_state_t){0};
    st->stato = ST_STANDBY;
    st->d = 1.0f;
    /* a micro that boots believes "off" and "mute" until 20 ms say otherwise */
    st->front.level = st->front.cand = 1;
    st->sw.level = st->sw.cand = 1;
    st->t_permit_low = UINT32_MAX;
}

timer_out_t timer_step(timer_state_t *st, const timer_in_t *in, uint32_t dt)
{
    st->t_fase = SAT_ADD(st->t_fase, dt);
    if (!st->permit_req)
        st->t_permit_low = SAT_ADD(st->t_permit_low, dt);
    deb_update(&st->front, in->front_in, dt);
    deb_update(&st->sw, in->mute_sw_in, dt);
    const int front_on = st->front.level == 0;
#if FALSO == 16
    const int want_music = st->sw.level == 1;   /* SW3 read backwards: a broken wire plays */
#else
    const int want_music = st->sw.level == 0;
#endif

    if (alim_ok(in)) {
        st->t_alim_ok = st->alim_prev ? SAT_ADD(st->t_alim_ok, dt) : 0;
        st->alim_prev = 1;
    } else {
        st->t_alim_ok = 0;
        st->alim_prev = 0;
    }
    if (!mains_absent(in) && rail_fail(in))
        st->t_fault = SAT_ADD(st->t_fault, dt);
    else
        st->t_fault = 0;
    const int fault = st->t_fault >= T_FAULT_PERSIST_US;

    /* the hole's trigger (spec 4.5): the hardware's verdict while asking for
     * music, or the detector itself. RILASCIO fase 0 blanks MUTE_G_IN: the
     * gate rises 0.22 ms after MUTE_REQ (psu.py, C_MUTE_G). */
    int hole = mains_absent(in);
#if FALSO != 6
    if (st->mute_req && !in->mute_g_in && !(st->stato == ST_RILASCIO && st->fase == 0))
        hole = 1;
#endif

    /* a state change is evaluated again in the same instant, so a chained
     * transition (MUTO -> SPEGNIMENTO -> off) costs no extra tick */
    for (int giro = 0; giro < 4; giro++) {
    const timer_stato_t prima = st->stato;
    if (giro > 0)
        dt = 0;
    switch (st->stato) {
    case ST_STANDBY:
        st->mains_req = st->vrelay_en = st->mute_req = 0;
        set_permit(st, 0);
        st->dac_on = 0;
        st->d = 1.0f;
        if (front_on) {
            st->mains_req = 1;             /* spec 4.1 step 1 */
            vai(st, ST_ACCENSIONE, 0);
        }
        break;

    case ST_ACCENSIONE:
        if (!front_on) {
            vai(st, ST_SPEGNIMENTO, 3);
            break;
        }
        if (st->fase >= 1 && fault) {
            entra_guasto(st);
            break;
        }
        if (st->fase >= 1 && mains_absent(in)) {
            entra_buco(st, in);
            break;
        }
        switch (st->fase) {
        case 0: /* step 2: the rails, 100 ms, within 2 s */
            if (st->t_alim_ok >= T_RAIL_OK_US) {
                /* the DAC still shut down: 2-9 nA, both strings - the zeros */
                if (!st->dac_on) {
                    st->zero_s = in->i_s;
                    st->zero_p = in->i_p;
                }
                st->dac_on = 1;            /* step 3: d = 1 */
                st->d = 1.0f;
                st->cal_active = 2;        /* step 4: the shunt, the series dark */
                st->cal_i = LDR_I_TOP;
                vai(st, ST_ACCENSIONE, 1);
#if FALSO == 18
            } else if (0) {                       /* waits for the rails forever */
#else
            } else if (st->t_fase >= T_RAIL_TIMEOUT_US) {
#endif
                entra_guasto(st);
            }
            break;
        case 1: /* the top, settled */
            if (st->t_fase >= T_CAL_SETTLE_US) {
                st->cal_top_read = netto(in->i_p, st->zero_p);
                st->cal_i = LDR_I_CAL_LO;
                vai(st, ST_ACCENSIONE, 2);
            }
            break;
        case 2: /* 2 mA, settled: fit, back to the top */
            if (st->t_fase >= T_CAL_SETTLE_US) {
#if FALSO != 14
                cal_fit(st, 2, in->t_c, st->cal_top_read, netto(in->i_p, st->zero_p));
#endif
                st->cal_active = 0;
                vai(st, ST_ACCENSIONE, 3);
            }
            break;
        case 3: /* the corrected top settles (C_X), then VRELAY on (step 5).
                   L41b2: on the circuit the top was still 10.6 mA, -1 dB, when
                   the release began 50 ms after the fit */
#if FALSO == 20
            if (1) {
#else
            if (st->t_fase >= T_CAL_SETTLE_US) {
#endif
                st->cal_ok_p = (uint8_t)cal_verifica(st, netto(in->i_p, st->zero_p));
                st->vrelay_en = 1;
                vai(st, ST_ACCENSIONE, 4);
            }
            break;
        case 4: /* step 6: >= 50 ms from VRELAY_EN */
#if FALSO == 1
            if (st->t_fase >= 5000u) {         /* 5 ms: under the 13 ms of ADR-027 */
#else
            if (st->t_fase >= T_VRELAY_US) {
#endif
                if (want_music)
                    entra_rilascio(st);
                else
                    entra_muto(st, st->cal_ok_p);  /* a failed shunt calibration is retried */
            }
            break;
        }
        break;

    case ST_MUTO:
        if (!front_on) {
            cal_abort(st);
            vai(st, ST_SPEGNIMENTO, 3);
            break;
        }
        if (fault) {
            entra_guasto(st);
            break;
        }
        if (mains_absent(in)) {
            entra_buco(st, in);
            break;
        }
        if (want_music && st->t_alim_ok >= T_RAIL_OK_US) {
            entra_rilascio(st);
            break;
        }
        /* the series idles in MUTO: its zero */
        if (st->fase == 0 && st->t_fase >= T_CAL_SETTLE_US)
            st->zero_s = in->i_s;
        /* the shunt at its top in MUTO: calibrated 1 s in (spec sec. 5) */
        if (!st->cal_done_here) {
            if (st->fase == 0 && st->t_fase >= T_CAL_MUSIC_US) {
                st->cal_top_read = netto(in->i_p, st->zero_p);
                st->cal_active = 2;
                st->cal_i = LDR_I_CAL_LO;
                st->fase = 1;
                st->t_fase = 0;
            } else if (st->fase == 1 && st->t_fase >= T_CAL_SETTLE_US) {
                cal_fit(st, 2, in->t_c, st->cal_top_read, netto(in->i_p, st->zero_p));
                st->cal_active = 0;
                st->fase = 2;
                st->t_fase = 0;
            } else if (st->fase == 2 && st->t_fase >= T_CAL_SETTLE_US) {
                st->cal_ok_p = (uint8_t)cal_verifica(st, netto(in->i_p, st->zero_p));
                st->cal_done_here = 1;
                st->fase = 0;
            }
        }
        break;

    case ST_RILASCIO:
        if (hole) {
            entra_buco(st, in);
            break;
        }
        if (fault) {
            entra_guasto(st);
            break;
        }
        if (!front_on) {
            vai(st, ST_SPEGNIMENTO, 0);
            break;
        }
        if (!want_music) {                 /* reversible (4.3 step 3) */
            vai(st, ST_INSERZIONE, 0);
            break;
        }
        if (st->fase == 0) {
#if FALSO == 2
            if (1) {                           /* d moves with the relay still open */
#else
            if (st->t_fase >= T_RELAY_OP_US) {
#endif
                if (!in->mute_g_in) {      /* the hardware refused the release */
                    entra_buco(st, in);
                    break;
                }
                st->fase = 1;
                st->t_fase = 0;
            }
            break;
        }
        st->d -= (float)dt / (float)T_FADE_US;
        if (st->d <= 0.0f) {
            st->d = 0.0f;
            st->cal_done_here = 0;
            vai(st, ST_MUSICA, 0);
        }
        break;

    case ST_MUSICA:
        if (hole) {
            entra_buco(st, in);
            break;
        }
        if (fault) {
            entra_guasto(st);
            break;
        }
        if (!front_on) {
            cal_abort(st);
            vai(st, ST_SPEGNIMENTO, 0);
            break;
        }
        if (!want_music) {
            cal_abort(st);
            vai(st, ST_INSERZIONE, 0);
            break;
        }
        /* the series at its top: calibrated 1 s in, 200 ms at 2 mA (~850 ohm
         * against R_IN = 1 M: -0.007 dB), the shunt stays dark */
        if (st->fase == 0 && st->t_fase >= T_CAL_SETTLE_US)
            st->zero_p = in->i_p;          /* the shunt idles in MUSICA */
        if (!st->cal_done_here) {
            if (st->fase == 0 && st->t_fase >= T_CAL_MUSIC_US) {
                st->cal_top_read = netto(in->i_s, st->zero_s);
                st->cal_active = 1;
                st->cal_i = LDR_I_CAL_LO;
                st->fase = 1;
                st->t_fase = 0;
            } else if (st->fase == 1 && st->t_fase >= T_CAL_SETTLE_US) {
                cal_fit(st, 1, in->t_c, st->cal_top_read, netto(in->i_s, st->zero_s));
                st->cal_active = 0;
                st->fase = 2;
                st->t_fase = 0;
            } else if (st->fase == 2 && st->t_fase >= T_CAL_SETTLE_US) {
                st->cal_ok_s = (uint8_t)cal_verifica(st, netto(in->i_s, st->zero_s));
                st->cal_done_here = 1;
                st->fase = 0;
            }
        }
        break;

    case ST_INSERZIONE:
        if (hole) {
            entra_buco(st, in);
            break;
        }
        if (fault) {
            entra_guasto(st);
            break;
        }
        if (!front_on) {
            st->stato = ST_SPEGNIMENTO;    /* same step, same timer */
            break;
        }
#if FALSO != 8
        if (want_music && st->fase <= 1) { /* reversible before MUTE_REQ falls */
            st->mute_req = 1;
            vai(st, ST_RILASCIO, 1);
            break;
        }
#endif
        if (inserisci(st, dt))
            entra_muto(st, 0);
        break;

    case ST_SPEGNIMENTO:
        if (st->fase <= 2 && hole) {
            mute_subito(st);
            st->fase = 3;
            st->t_fase = 0;
            break;
        }
        if (st->fase <= 2 && fault) {
            entra_guasto(st);
            break;
        }
        if (st->fase <= 1 && front_on) {   /* back on before MUTE_REQ fell */
            if (want_music) {
                st->mute_req = 1;
                vai(st, ST_RILASCIO, 1);
            } else {
                st->stato = ST_INSERZIONE;
            }
            break;
        }
        if (st->fase <= 2) {
            if (inserisci(st, dt)) {
                st->fase = 3;
                st->t_fase = 0;
            }
            break;
        }
        /* 4.4 steps 2-4: >= 50 ms after PERMIT_REQ, VRELAY_EN and MAINS_REQ
         * together, the DAC shut down, standby */
        st->mute_req = 0;
        set_permit(st, 0);
        st->d = 1.0f;
#if FALSO == 9
        if (1) {
#else
        if (st->t_permit_low >= T_OFF_GAP_US) {
#endif
            st->vrelay_en = 0;
            st->mains_req = 0;
            st->dac_on = 0;
            vai(st, ST_STANDBY, 0);
        }
        break;

    case ST_BUCO_RETE:
        if (mains_absent(in))
            st->mains_absent = 1;
        if (rail_fail(in))
            st->rail_dipped = 1;
        if (!front_on) {
            vai(st, ST_SPEGNIMENTO, 3);
            break;
        }
        if (!st->mains_absent) {
            /* the detector has not spoken yet: wait T_CLASSIFY, then a rail
             * out with the mains present is a fault (4.5, third class); a
             * drop nothing explains is treated as a hole the rails rode */
            if (st->t_fase < T_CLASSIFY_US)
                break;
            if (fault || rail_fail(in)) {
                entra_guasto(st);
                break;
            }
            st->mains_absent = 1;          /* -> the "mains back" path below */
            st->fase = 1;
        }
        if (st->fase == 0) {
            if (!mains_absent(in))
                st->fase = 1;              /* the mains are back */
            break;
        }
#if FALSO == 10
        if (0) {
#else
        if (st->rail_dipped) {
#endif
            /* second class: redo the power-up from step 2 (4.5) */
            vai(st, ST_ACCENSIONE, 0);
            break;
        }
        if (fault) {
            entra_guasto(st);
            break;
        }
        if (mains_absent(in)) {
            st->fase = 0;                  /* gone again */
            break;
        }
        /* first class: the rails rode through; 500 ms good, then "the normal
         * sequence" (ADR-048 point 5) */
        if (st->t_alim_ok >= T_HOLE_OK_US) {
            if (want_music)
                entra_rilascio(st);
            else
                entra_muto(st, 0);
        }
        break;

    case ST_GUASTO:
        st->mute_req = 0;
        set_permit(st, 0);
        st->d = 1.0f;
        if (st->fase == 0) {
            if (st->t_fase >= T_FAULT_GAP_US) {
                st->mains_req = 0;         /* 4.6 step 2 */
                st->vrelay_en = 0;
                st->dac_on = 0;
                st->fase = 1;
                st->t_fase = 0;
            }
            break;
        }
#if FALSO != 15
        if (!front_on)                     /* 4.6 step 3: off, then on again */
#endif
            vai(st, ST_STANDBY, 0);
        break;
    }
    if (st->stato == prima)
        break;
    }

    timer_out_t o = {0};
    o.mains_req = st->mains_req;
    o.vrelay_en = st->vrelay_en;
    o.mute_req = st->mute_req;
    o.permit_req = st->permit_req;
    o.dac_on = st->dac_on;
    o.stato = (uint8_t)st->stato;
    o.power_down = st->stato == ST_STANDBY;
    if (st->dac_on) {
        float is = timer_profile_series(st->d), ip = timer_profile_shunt(st->d);
        if (st->cal_active == 1)
            is = st->cal_i;
        else if (st->cal_active == 2)
            ip = st->cal_i;
        o.code_s = timer_law_code(is, in->t_c, &st->cal_s);
        o.code_p = timer_law_code(ip, in->t_c, &st->cal_p);
    }
    return o;
}
