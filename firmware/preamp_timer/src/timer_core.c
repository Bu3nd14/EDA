/*
 * timer_core.c - the supply board's timer, the pure logic (L41b2; the mute
 * with the relays alone since L47c2a, ADR-062).
 *
 * Every sequence is spec sec. 4 (firmware/preamp_timer/spec/timer_spec.md).
 * Choices the spec left open are marked "L41b2" or "L47c2a" and written in
 * the spec and in that lot's report.
 *
 * L47c2a: the LDR law, its calibration, the fade (d) and the SPI to the DAC
 * are gone with the hardware they drove (ADR-062, L47c1). The fakes that
 * proved them went with them; see test/run_host_tests.sh for the count.
 *
 * FALSO_n: a deliberate defect, compiled in only by the host tests' fake
 * builds (test/run_host_tests.sh) to prove that each test can fail.
 */
#include "timer_core.h"

#include <stddef.h>

#ifndef FALSO
#define FALSO 0
#endif

#define SAT_ADD(a, b) ((a) > UINT32_MAX - (b) ? UINT32_MAX : (a) + (b))

/* ------------------------------------------------------- the free pins */
const timer_pin_t TIMER_PIN_LIBERI[] = {
    {'A', 1, 17}, {'A', 2, 18}, {'A', 3, 19}, {'A', 4, 2},
#if FALSO != 25
    {'B', 4, 7},                              /* FALSO 25: PB4 forgotten */
#endif
#if FALSO == 26
    {'C', 2, 14},                             /* MUTE_G_IN taken for the spare */
#else
    {'C', 3, 15},
#endif
};
const unsigned TIMER_N_PIN_LIBERI = sizeof TIMER_PIN_LIBERI / sizeof TIMER_PIN_LIBERI[0];
#if FALSO == 27
const uint8_t TIMER_PIN_LIBERI_ISC = 0x0u;    /* INTDISABLE: the buffer left on */
#else
const uint8_t TIMER_PIN_LIBERI_ISC = TIMER_ISC_INPUT_DISABLE;
#endif

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

/* The immediate mute of a mains hole or a fault (spec 4.5, 4.6). */
static void mute_subito(timer_state_t *st)
{
    st->mute_req = 0;
#if FALSO != 5
    set_permit(st, 0);
#endif
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

static void entra_rilascio(timer_state_t *st)
{
    /* spec 4.3 step 1: both requests at once; the hardware energises
     * PERMIT_CMD no later than MUTE_CMD (D522) */
    st->mute_req = 1;
#if FALSO != 24
    set_permit(st, 1);
#endif
    vai(st, ST_RILASCIO, 0);
}

/* The insertion of spec 4.2, shared by INSERZIONE and SPEGNIMENTO (4.4 step
 * 1): fase 0 MUTE_REQ low at once (ADR-062: the relays straight after the
 * switch), fase 1 Delta, then PERMIT_REQ low and returns 1 (done). */
static int inserisci(timer_state_t *st)
{
    switch (st->fase) {
    case 0:
#if FALSO == 22
        if (st->t_fase < 500000u)             /* a hold of 0.5 s left from the fade */
            return 0;
#endif
        st->mute_req = 0;
        st->fase = 1;
        st->t_fase = 0;
        return 0;
    case 1:
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
     * transition (MUSICA -> INSERZIONE -> MUTE_REQ low) costs no extra tick */
    for (int giro = 0; giro < 4; giro++) {
    const timer_stato_t prima = st->stato;
    if (giro > 0)
        dt = 0;
    switch (st->stato) {
    case ST_STANDBY:
        st->mains_req = st->vrelay_en = st->mute_req = 0;
        set_permit(st, 0);
        if (front_on) {
            st->mains_req = 1;             /* spec 4.1 step 1 */
            vai(st, ST_ACCENSIONE, 0);
        }
        break;

    case ST_ACCENSIONE:
        if (!front_on) {
            vai(st, ST_SPEGNIMENTO, 2);
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
        case 0: /* step 2: the rails, 100 ms, within 2 s; then VRELAY on (step 3) */
#if FALSO == 28
            if (st->alim_prev) {                  /* the first good sample, not 100 ms */
#else
            if (st->t_alim_ok >= T_RAIL_OK_US) {
#endif
                st->vrelay_en = 1;
                vai(st, ST_ACCENSIONE, 1);
#if FALSO == 18
            } else if (0) {                       /* waits for the rails forever */
#else
            } else if (st->t_fase >= T_RAIL_TIMEOUT_US) {
#endif
                entra_guasto(st);
            }
            break;
        case 1: /* step 4: >= 50 ms from VRELAY_EN */
#if FALSO == 1
            if (st->t_fase >= 5000u) {         /* 5 ms: under the 13 ms of ADR-027 */
#else
            if (st->t_fase >= T_VRELAY_US) {
#endif
                if (want_music)
                    entra_rilascio(st);
                else
                    vai(st, ST_MUTO, 0);
            }
            break;
        }
        break;

    case ST_MUTO:
        if (!front_on) {
            vai(st, ST_SPEGNIMENTO, 2);
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
        if (want_music && st->t_alim_ok >= T_RAIL_OK_US)
            entra_rilascio(st);
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
        if (!want_music) {
            vai(st, ST_INSERZIONE, 0);
            break;
        }
#if FALSO == 24
        if (st->t_fase >= T_DELTA_US)         /* PERMIT_REQ 20 ms after MUTE_REQ */
            set_permit(st, 1);
#endif
        /* spec 4.3 step 2: the G6K's 10 ms, then the hardware's verdict */
        if (st->t_fase >= T_RELAY_OP_US) {
#if FALSO != 23
            if (!in->mute_g_in) {          /* the hardware refused the release */
                entra_buco(st, in);
                break;
            }
#endif
#if FALSO == 24
            if (!st->permit_req)
                break;
#endif
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
#if FALSO == 30
            vai(st, ST_SPEGNIMENTO, 2);    /* off without the insertion: no Delta */
#else
            vai(st, ST_SPEGNIMENTO, 0);
#endif
            break;
        }
        if (!want_music)
            vai(st, ST_INSERZIONE, 0);
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
        /* not reversible (ADR-062): MUTE_REQ is low from the first step, and
         * a switch back to music is a release from MUTO */
        if (inserisci(st))
            vai(st, ST_MUTO, 0);
        break;

    case ST_SPEGNIMENTO:
        if (st->fase <= 1 && hole) {
            mute_subito(st);
            st->fase = 2;
            st->t_fase = 0;
            break;
        }
        if (st->fase <= 1 && fault) {
            entra_guasto(st);
            break;
        }
        if (st->fase <= 1) {
            if (inserisci(st)) {
                st->fase = 2;
                st->t_fase = 0;
            }
            break;
        }
        /* 4.4 steps 2-3: >= 80 ms after PERMIT_REQ, VRELAY_EN and MAINS_REQ
         * together, standby */
        st->mute_req = 0;
        set_permit(st, 0);
#if FALSO == 9
        if (1) {
#else
        if (st->t_permit_low >= T_OFF_GAP_US) {
#endif
            st->vrelay_en = 0;
#if FALSO == 29
            if (st->t_permit_low < T_OFF_GAP_US + 80000u)   /* the mains 80 ms after VRELAY */
                break;
#endif
            st->mains_req = 0;
            vai(st, ST_STANDBY, 0);
        }
        break;

    case ST_BUCO_RETE:
        if (mains_absent(in))
            st->mains_absent = 1;
        if (rail_fail(in))
            st->rail_dipped = 1;
        if (!front_on) {
            vai(st, ST_SPEGNIMENTO, 2);
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
                vai(st, ST_MUTO, 0);
        }
        break;

    case ST_GUASTO:
        st->mute_req = 0;
        set_permit(st, 0);
        if (st->fase == 0) {
            if (st->t_fase >= T_FAULT_GAP_US) {
                st->mains_req = 0;         /* 4.6 step 2 */
                st->vrelay_en = 0;
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
    o.stato = (uint8_t)st->stato;
    o.power_down = st->stato == ST_STANDBY;
    return o;
}
