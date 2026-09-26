/*
 * test_sequenze.c - one test per sequence of spec sec. 4 (L41b2).
 *
 *   test_sequenze [nome ...]        run the named tests (all if none)
 *   test_sequenze --csv <dir>       also write each test's outputs to <dir>/<nome>.csv
 *
 * Exit code: the number of failed checks. Each test is also run against the
 * fake builds (FALSO_n, run_host_tests.sh) and must fail there.
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mondo.h"

static mondo_t M;                    /* 1.2 MB: static, not on the stack */
static const char *csv_dir;
static const float TICK = 1e-3f;     /* the adapter's period */

static const char *csv_per(const char *nome)
{
    static char p[512];
    if (!csv_dir)
        return NULL;
    snprintf(p, sizeof p, "%s/%s.csv", csv_dir, nome);
    return p;
}

/* The v4 table with the top of ADR-050, written again here from the ADRs
 * (not from the core): ADR-039 points, log-linear between them. */
static double tab_log(const double (*p)[2], int n, double d)
{
    if (d <= p[0][0])
        return p[0][1];
    for (int k = 1; k < n; k++)
        if (d <= p[k][0]) {
            double u = (d - p[k - 1][0]) / (p[k][0] - p[k - 1][0]);
            return exp(log(p[k - 1][1]) + u * (log(p[k][1]) - log(p[k - 1][1])));
        }
    return p[n - 1][1];
}
static double tab_serie(double d)
{
    static const double p[][2] = {{0, 12e-3}, {0.1, 0.2e-3}, {0.45, 4.5e-6}, {0.75, 0.19e-6},
                                  {0.8, 10e-9}, {1, 10e-9}};
    return tab_log(p, 6, d);
}
static double tab_deriv(double d)
{
    static const double p[][2] = {{0, 10e-9}, {0.5, 10e-9}, {1, 12e-3}};
    return tab_log(p, 3, d);
}
static double db(double a, double b) { return 20.0 * log10(a / b); }

#define VICINO(a, b, tol) (fabsf((a) - (b)) <= (tol) + 2e-5f)

/* ---------------------------------------------------------------- 4.1 */
static void t_accensione(void)
{
    mondo_init(&M, csv_per("accensione"));
    /* from standby: the toroid off, no rails; the front switched on at t = 0 */
    M.in.v_sup_p = 0.0f;
    M.in.v_sup_m = 2.3f;
    float t_rail = -1;
    for (int k = 0; k < 9000; k++) {
        mondo_corri(&M, 1);
        if (t_rail < 0 && M.out.mains_req)
            t_rail = M.t_us * 1e-6f + 0.300f;          /* the rails come 300 ms later */
        if (t_rail > 0 && M.t_us * 1e-6f >= t_rail - 1e-6f)
            rete_sana(&M.in);
    }
    mondo_chiudi(&M);
    float t_mains = primo_fronte(&M, M.mains, 1, 0);
    float t_dac = primo_fronte(&M, M.dac, 1, 0);
    float t_vr = primo_fronte(&M, M.vrel, 1, 0);
    float t_mu = primo_fronte(&M, M.mute, 1, 0);
    float t_pe = primo_fronte(&M, M.perm, 1, 0);
    float t_mus = primo_stato(&M, ST_MUSICA, 0);
    CHECK(VICINO(t_mains, 0.020f, TICK), "MAINS_REQ a %.4f s, voluto 0,020 (debounce 20 ms)", t_mains);
    CHECK(t_dac >= t_rail + 0.100f - 1e-6f && t_dac <= t_rail + 0.100f + TICK,
          "DAC acceso %.4f s dopo i rail, voluto 100 ms (4.1 passo 2)", t_dac - t_rail);
    CHECK(VICINO(t_vr - t_dac, 0.600f, TICK), "VRELAY_EN %.4f s dopo il DAC: la calibrazione "
          "della derivazione sono 2 x 200 ms, piu' 200 ms per la cima corretta", t_vr - t_dac);
    /* the corrected top reached before VRELAY_EN (L41b2: on the circuit it
     * was not); in this world the string is instantaneous, so the check is
     * that the corrected code is held >= 200 ms before VRELAY_EN */
    {
        int kv = idx_a(&M, t_vr), k = kv;
        while (k > 0 && M.cp[k - 1] == M.cp[kv]) k--;
        CHECK(t_vr - M.t[k] >= 0.200f - 1e-5f, "la cima corretta tenuta solo %.4f s prima di VRELAY_EN",
              t_vr - M.t[k]);
    }
    CHECK(t_mu - t_vr >= 0.050f - 1e-6f && t_mu - t_vr <= 0.050f + TICK,
          "MUTE_REQ %.4f s dopo VRELAY_EN, voluto >= 50 ms (ADR-027: 13 ms)", t_mu - t_vr);
    CHECK(t_pe == t_mu, "PERMIT_REQ (%.4f) e MUTE_REQ (%.4f) nello stesso istante (4.3)", t_pe, t_mu);
    /* d moves only after the G6K's 10 ms */
    int k0 = idx_a(&M, t_mu);
    float t_d = -1;
    for (int k = k0; k < M.n; k++)
        if (M.d[k] < 1.0f) { t_d = M.t[k]; break; }
    CHECK(t_d - t_mu >= 0.010f - 1e-6f, "d si muove %.4f s dopo MUTE_REQ, voluto >= 10 ms", t_d - t_mu);
    CHECK(VICINO(t_mus - t_d, 6.0f, 2 * TICK), "rilascio in %.4f s, voluto 6 (ADR-039)", t_mus - t_d);
    /* the calibration: during it the series stays dark (ADR-038 point 3) */
    int buio = 1;
    for (int k = idx_a(&M, t_dac); k < idx_a(&M, t_vr); k++)
        if (M.is[k] > 20e-9f) buio = 0;
    CHECK(buio, "la serie accesa durante la calibrazione della derivazione");
    /* the shunt's top after the calibration, with the plant 4.5 mV and 0.43 ohm off */
    float e_top = (float)db(M.ip[idx_a(&M, t_vr + 0.02f)], 12e-3);
    CHECK(fabsf(e_top) <= 0.1f, "derivazione alla cima %+.3f dB dopo la calibrazione", e_top);
    /* the series is calibrated 1 s into MUSICA: 12 mA at d = 0 afterwards */
    float e_s = (float)db(M.is[idx_a(&M, t_mus + 1.5f)], 12e-3);
    float e_s0 = (float)db(M.is[idx_a(&M, t_mus + 0.5f)], 12e-3);
    CHECK(fabsf(e_s) <= 0.1f, "serie alla cima %+.3f dB dopo la calibrazione in MUSICA", e_s);
    printf("  accensione: MAINS_REQ %.3f, DAC %.3f, VRELAY_EN %.3f, MUTE/PERMIT_REQ %.3f, MUSICA %.3f s;"
           " cima della serie %+.2f dB prima, %+.3f dB dopo la calibrazione\n",
           t_mains, t_dac, t_vr, t_mu, t_mus, e_s0, e_s);

    /* no rails within 2 s: GUASTO, the toroid off >= 50 ms later, nothing else moved */
    mondo_init(&M, NULL);
    M.in.v_sup_p = 0.0f;
    M.in.v_sup_m = 2.3f;
    mondo_corri(&M, 4000);
    t_mains = primo_fronte(&M, M.mains, 1, 0);
    float t_g = primo_stato(&M, ST_GUASTO, 0);
    float t_off = primo_fronte(&M, M.mains, 0, t_mains);
    CHECK(VICINO(t_g - t_mains, 2.0f, TICK), "GUASTO %.4f s dopo MAINS_REQ senza rail, voluto 2 s", t_g - t_mains);
    CHECK(t_off - t_g >= 0.050f - 1e-6f && t_off > 0, "MAINS_REQ giu' %.4f s dopo GUASTO, voluto >= 50 ms", t_off - t_g);
    CHECK(primo_fronte(&M, M.vrel, 1, 0) < 0 && primo_fronte(&M, M.mute, 1, 0) < 0,
          "senza rail VRELAY_EN o MUTE_REQ si sono alzati");
}

/* Power up to MUSICA and let the series calibrate; returns now. */
static float in_musica(const char *csv)
{
    mondo_init(&M, csv);
    porta_a(&M, ST_MUSICA);
    mondo_corri(&M, 2000);
    return M.t_us * 1e-6f;
}

static float in_muto(const char *csv)
{
    mondo_init(&M, csv);
    M.in.mute_sw_in = 1;
    porta_a(&M, ST_MUTO);
    mondo_corri(&M, 2000);
    return M.t_us * 1e-6f;
}

/* ---------------------------------------------------------------- 4.2 */
static void t_inserzione(void)
{
    float t0 = in_musica(csv_per("inserzione"));
    M.in.mute_sw_in = 1;
    mondo_corri(&M, 8000);
    mondo_chiudi(&M);
    float t_ins = primo_stato(&M, ST_INSERZIONE, t0);
    float t_d1 = -1;
    for (int k = idx_a(&M, t0); k < M.n; k++)
        if (M.d[k] >= 1.0f) { t_d1 = M.t[k]; break; }
    float t_mu = primo_fronte(&M, M.mute, 0, t0);
    float t_pe = primo_fronte(&M, M.perm, 0, t0);
    CHECK(VICINO(t_ins - t0, 0.020f, TICK), "INSERZIONE %.4f s dopo SW3, voluto 20 ms", t_ins - t0);
    CHECK(VICINO(t_d1 - t_ins, 6.0f, 2 * TICK), "d da 0 a 1 in %.4f s, voluto 6 (ADR-039)", t_d1 - t_ins);
    CHECK(t_mu - t_d1 >= 0.500f - 1e-6f && t_mu - t_d1 <= 0.500f + TICK,
          "MUTE_REQ giu' %.4f s dopo d = 1, voluto 0,5 (J3)", t_mu - t_d1);
    CHECK(t_pe - t_mu >= 0.020f - 1e-6f && t_pe - t_mu <= 0.020f + TICK,
          "PERMIT_REQ giu' %.4f s dopo MUTE_REQ, voluto 20 ms (ADR-045)", t_pe - t_mu);
    CHECK(primo_stato(&M, ST_MUTO, t0) > 0, "non arriva in MUTO");
    /* the currents against the table (after both calibrations) */
    double peggiore = 0;
    for (int k = idx_a(&M, t_ins); k < idx_a(&M, t_d1); k += 50) {
        double ds = db(M.is[k], tab_serie(M.d[k])), dp = db(M.ip[k], tab_deriv(M.d[k]));
        if (fabs(ds) > fabs(peggiore)) peggiore = ds;
        if (fabs(dp) > fabs(peggiore)) peggiore = dp;
    }
    CHECK(fabs(peggiore) <= 0.2, "correnti contro la tabella v4 (cima 12 mA): %+.3f dB", peggiore);
    printf("  inserzione: INSERZIONE +%.3f, d = 1 +%.3f, MUTE_REQ +%.3f, PERMIT_REQ +%.3f s; "
           "correnti entro %+.3f dB dalla tabella\n", t_ins - t0, t_d1 - t0, t_mu - t0, t_pe - t0, peggiore);
}

/* ---------------------------------------------------------------- 4.3 */
static void t_rilascio(void)
{
    float t0 = in_muto(csv_per("rilascio"));
    M.in.mute_sw_in = 0;
    mondo_corri(&M, 7000);
    mondo_chiudi(&M);
    float t_mu = primo_fronte(&M, M.mute, 1, t0);
    float t_pe = primo_fronte(&M, M.perm, 1, t0);
    float t_d = -1, t_0 = -1;
    for (int k = idx_a(&M, t0); k < M.n; k++) {
        if (t_d < 0 && M.d[k] < 1.0f) t_d = M.t[k];
        if (t_0 < 0 && M.d[k] <= 0.0f) t_0 = M.t[k];
    }
    CHECK(VICINO(t_mu - t0, 0.020f, TICK), "MUTE_REQ su %.4f s dopo SW3, voluto 20 ms", t_mu - t0);
    CHECK(t_pe == t_mu, "PERMIT_REQ e MUTE_REQ non insieme (%.4f, %.4f)", t_pe, t_mu);
    CHECK(t_d - t_mu >= 0.010f - 1e-6f, "d si muove %.4f s dopo i rele', voluto >= 10 ms (ADR-039)", t_d - t_mu);
    CHECK(VICINO(t_0 - t_d, 6.0f, 2 * TICK), "d da 1 a 0 in %.4f s, voluto 6", t_0 - t_d);
    printf("  rilascio: MUTE/PERMIT_REQ +%.3f, d parte +%.3f, d = 0 +%.3f s\n", t_mu - t0, t_d - t0, t_0 - t0);
}

/* ------------------------------------------------ 4.2 step 4, 4.3 step 3 */
static void t_inversione(void)
{
    float t0 = in_musica(csv_per("inversione"));
    M.in.mute_sw_in = 1;
    mondo_corri(&M, 3000);                   /* d ~ 0.5 */
    float t_r = M.t_us * 1e-6f;
    M.in.mute_sw_in = 0;
    mondo_corri(&M, 5000);
    mondo_chiudi(&M);
    float dmax = 0;
    int kmax = 0;
    for (int k = idx_a(&M, t0); k < M.n; k++)
        if (M.d[k] > dmax) { dmax = M.d[k]; kmax = k; }
    CHECK(VICINO(M.t[kmax], t_r + 0.020f, 1.5f * TICK), "d inverte a %.4f s, voluto %.4f (SW3 + 20 ms)",
          M.t[kmax], t_r + 0.020f);
    CHECK(kmax + 2 < M.n && M.d[kmax + 2] < M.d[kmax + 1] && M.d[kmax + 1] <= M.d[kmax],
          "d non scende subito dopo l'inversione");
    CHECK(primo_fronte(&M, M.mute, 0, t0) < 0 && primo_fronte(&M, M.perm, 0, t0) < 0,
          "un rele' si e' mosso in un'inversione a meta'");
    float t_mus = primo_stato(&M, ST_MUSICA, t_r);
    CHECK(VICINO(t_mus - M.t[kmax], dmax * 6.0f, 3 * TICK), "ritorno a d = 0 in %.4f s, voluto %.4f "
          "(stessa velocita')", t_mus - M.t[kmax], dmax * 6.0f);
    printf("  inversione dell'inserzione: d max %.4f a +%.3f s, MUSICA +%.3f s, nessun rele' mosso\n",
           dmax, M.t[kmax] - t0, t_mus - t0);

    /* the release reversed half-way: back to 1, then the relays as in 4.2 */
    t0 = in_muto(NULL);
    M.in.mute_sw_in = 0;
    mondo_corri(&M, 3000);
    t_r = M.t_us * 1e-6f;
    M.in.mute_sw_in = 1;
    mondo_corri(&M, 5000);
    float dmin = 1;
    for (int k = idx_a(&M, t0); k < M.n; k++)
        if (M.d[k] < dmin) dmin = M.d[k];
    float t_d1 = -1;
    for (int k = idx_a(&M, t_r); k < M.n; k++)
        if (M.d[k] >= 1.0f) { t_d1 = M.t[k]; break; }
    float t_mu = primo_fronte(&M, M.mute, 0, t_r);
    CHECK(dmin > 0.4f && dmin < 0.6f, "il rilascio invertito scende a d = %.3f", dmin);
    CHECK(t_d1 > 0 && t_mu - t_d1 >= 0.5f - 1e-6f, "dopo l'inversione del rilascio MUTE_REQ giu' "
          "%.4f s dopo d = 1", t_mu - t_d1);
    printf("  inversione del rilascio: d min %.3f, MUTE_REQ giu' %.3f s dopo d = 1\n", dmin, t_mu - t_d1);
}

/* ---------------------------------------------------------------- 4.4 */
static void t_spegnimento(void)
{
    float t0 = in_musica(csv_per("spegnimento"));
    M.in.front_in = 1;
    mondo_corri(&M, 8000);
    mondo_chiudi(&M);
    float t_mu = primo_fronte(&M, M.mute, 0, t0);
    float t_pe = primo_fronte(&M, M.perm, 0, t0);
    float t_vr = primo_fronte(&M, M.vrel, 0, t0);
    float t_ma = primo_fronte(&M, M.mains, 0, t0);
    float t_dac = primo_fronte(&M, M.dac, 0, t0);
    float t_sb = primo_stato(&M, ST_STANDBY, t0);
    CHECK(t_pe - t_mu >= 0.020f - 1e-6f, "PERMIT_REQ %.4f s dopo MUTE_REQ", t_pe - t_mu);
    CHECK(t_vr - t_pe >= 0.080f - 1e-6f && t_vr - t_pe <= 0.080f + TICK,
          "VRELAY_EN giu' %.4f s dopo PERMIT_REQ, voluto 80 ms: 50 dopo PERMIT_CMD (ADR-046) "
          "piu' il Delta dell'hardware", t_vr - t_pe);
    CHECK(t_ma == t_vr, "MAINS_REQ (%.4f) e VRELAY_EN (%.4f) non insieme (4.4 passo 3)", t_ma, t_vr);
    CHECK(t_dac == t_ma && t_sb == t_ma, "DAC spento %.4f, STANDBY %.4f, rete %.4f", t_dac, t_sb, t_ma);
    CHECK(t_ma - t0 > 6.5f && t_ma - t0 < 7.0f, "spegnimento in %.3f s, ADR-046: ~7 s", t_ma - t0);
    CHECK(M.stato[M.n - 1] == ST_STANDBY && M.out.power_down, "non finisce in STANDBY col power-down");
    printf("  spegnimento da MUSICA: MUTE_REQ +%.3f, PERMIT_REQ +%.3f, VRELAY_EN e MAINS_REQ +%.3f s\n",
           t_mu - t0, t_pe - t0, t_ma - t0);

    t0 = in_muto(NULL);
    M.in.front_in = 1;
    mondo_corri(&M, 200);
    t_ma = primo_fronte(&M, M.mains, 0, t0);
    CHECK(VICINO(t_ma - t0, 0.020f, TICK), "da MUTO la rete si stacca %.4f s dopo il frontale, "
          "voluto 20 ms (PERMIT_REQ gia' giu' da secondi)", t_ma - t0);
    CHECK(primo_fronte(&M, M.vrel, 0, t0) == t_ma, "da MUTO VRELAY_EN e MAINS_REQ non insieme");
}

/* ---------------------------------------------------------------- 4.7 */
static void t_debounce(void)
{
    /* SW3 bouncing for 100 ms, back to music: nothing happens */
    float t0 = in_musica(NULL);
    for (int k = 0; k < 20; k++) {
        M.in.mute_sw_in = (uint8_t)(k % 2 == 0);
        mondo_corri(&M, 5);
    }
    M.in.mute_sw_in = 0;
    mondo_corri(&M, 500);
    CHECK(primo_stato(&M, ST_INSERZIONE, t0) < 0, "un rimbalzo di 5 ms ha iniziato l'inserzione");
    /* bouncing, then settled at mute: the insertion 20 ms after the last edge */
    t0 = M.t_us * 1e-6f;
    for (int k = 0; k < 12; k++) {
        M.in.mute_sw_in = (uint8_t)(k % 2 == 1);
        mondo_corri(&M, 5);
    }
    float t_last = M.t_us * 1e-6f - 0.005f;
    mondo_corri(&M, 100);
    float t_ins = primo_stato(&M, ST_INSERZIONE, t0);
    CHECK(VICINO(t_ins - t_last, 0.020f, TICK), "inserzione %.4f s dopo l'ultimo rimbalzo, voluto 20 ms",
          t_ins - t_last);
    /* the front switch glitching 10 ms in MUSICA: nothing */
    t0 = in_musica(NULL);
    M.in.front_in = 1;
    mondo_corri(&M, 10);
    M.in.front_in = 0;
    mondo_corri(&M, 500);
    CHECK(primo_stato(&M, ST_SPEGNIMENTO, t0) < 0, "un rimbalzo del frontale ha spento");
    /* SW3 open (a broken wire reads high, F10 / ADR-028): the power-up stays muted */
    mondo_init(&M, NULL);
    M.in.mute_sw_in = 1;
    mondo_corri(&M, 3000);
    CHECK(primo_stato(&M, ST_MUTO, 0) > 0 && primo_fronte(&M, M.mute, 1, 0) < 0,
          "col filo di SW3 rotto l'accensione ha rilasciato il mute");
    /* the OR: SW3 at music, front off -> the mute is inserted anyway (4.4) */
    t0 = in_musica(NULL);
    M.in.front_in = 1;
    mondo_corri(&M, 7000);
    CHECK(primo_fronte(&M, M.mute, 0, t0) > 0, "frontale spento con SW3 a musica: il mute non entra");
    printf("  debounce: rimbalzi di 5 ms ignorati, inserzione 20 ms dopo l'ultimo; filo rotto = mute\n");
}

/* ---------------------------------------------------------------- 4.5 */
static void t_buco_classe1(void)
{
    /* the rails ride through: the detector at +5 ms (slower than MUTE_G, so
     * the reaction can only come from MUTE_G_IN), mains back at +40 ms */
    in_musica(csv_per("buco_rete"));
    uint16_t top_p = timer_law_code(LDR_I_TOP, 25.0f, &M.st.cal_p);
    mondo_corri(&M, 0);
    M.sup_trip = 1;
    mondo_isr(&M);                         /* the pin-change interrupt */
    float t_hole = M.t_us * 1e-6f;
    CHECK(M.out.mute_req == 0 && M.out.permit_req == 0,
          "all'interruzione MUTE_REQ %d, PERMIT_REQ %d: voluti giu' subito (4.5 passo 1)",
          M.out.mute_req, M.out.permit_req);
    CHECK(M.out.code_p == top_p, "d = 1 non immediato: derivazione %d, voluto %d", M.out.code_p, top_p);
    mondo_corri(&M, 5);
    rete_assente(&M.in);
    mondo_corri(&M, 35);
    rete_sana(&M.in);
    M.sup_trip = 0;
    float t_back = M.t_us * 1e-6f;
    mondo_corri(&M, 7000);
    mondo_chiudi(&M);
    float t_rel = primo_fronte(&M, M.mute, 1, t_hole);
    CHECK(primo_stato(&M, ST_ACCENSIONE, t_hole) < 0, "classe 1 trattata come classe 2");
    CHECK(t_rel - t_back >= 0.500f - 1e-6f && t_rel - t_back <= 0.500f + 2 * TICK,
          "RILASCIO %.4f s dopo il ritorno della rete, voluto 500 ms (ADR-048 punto 5)", t_rel - t_back);
    CHECK(primo_stato(&M, ST_MUSICA, t_rel) > 0, "dopo il buco non torna in MUSICA");
    printf("  buco di rete, classe 1: MUTE_REQ e PERMIT_REQ giu' all'interruzione (0 ms), "
           "RILASCIO %.3f s dopo il ritorno\n", t_rel - t_back);

    /* the same without the interrupt, MUTE_G falling mid-tick: within 1 ms */
    in_musica(NULL);
    M.sup_trip = 1;                        /* between ticks: seen at the next */
    mondo_corri(&M, 1);
    CHECK(M.out.mute_req == 0, "senza interruzione MUTE_REQ ancora su dopo 1 ms");

    /* the detector alone (MUTE_G still up): mute from ADC_MD, MUTO path */
    in_musica(NULL);
    rete_assente(&M.in);
    mondo_corri(&M, 1);
    CHECK(M.out.mute_req == 0 && M.out.stato == ST_BUCO_RETE, "ADC_MD da solo non muta");
    /* a hole while muted: the release waits for 500 ms of good supply */
    in_muto(NULL);
    rete_assente(&M.in);
    mondo_corri(&M, 30);
    M.in.mute_sw_in = 0;                   /* the user asks for music in the hole */
    mondo_corri(&M, 30);
    rete_sana(&M.in);
    t_back = M.t_us * 1e-6f;
    mondo_corri(&M, 1000);
    t_rel = primo_fronte(&M, M.mute, 1, 0);
    CHECK(t_rel - t_back >= 0.5f - 1e-6f, "in MUTO durante un buco il rilascio parte %.4f s dopo "
          "il ritorno, voluto >= 500 ms", t_rel - t_back);
}

static void t_buco_classe2(void)
{
    /* the rails fall during a long hole: the power-up again from step 2 */
    float t0 = in_musica(csv_per("buco_classe2"));
    M.sup_trip = 1;
    mondo_isr(&M);
    mondo_corri(&M, 5);
    rete_assente(&M.in);
    mondo_corri(&M, 20);
    rail_giu(&M.in);
    mondo_corri(&M, 75);
    M.in.v_md = 0.5f;                      /* mains back at +100 ms, rails still down */
    mondo_corri(&M, 50);
    rete_sana(&M.in);                      /* rails good at +150 ms */
    M.sup_trip = 0;
    float t_ok = M.t_us * 1e-6f;
    mondo_corri(&M, 8000);
    mondo_chiudi(&M);
    float t_acc = primo_stato(&M, ST_ACCENSIONE, t0);
    float t_rel = primo_fronte(&M, M.mute, 1, t0 + 0.001f);
    CHECK(t_acc > 0, "classe 2: l'accensione non si rifa'");
    CHECK(t_rel - t_ok >= 0.100f + 0.600f + 0.050f - 1e-6f,
          "RILASCIO %.4f s dopo i rail, voluto >= 100 + 600 + 50 ms (4.1 dal passo 2)", t_rel - t_ok);
    CHECK(primo_stato(&M, ST_GUASTO, t0) < 0, "classe 2 finita in GUASTO");
    printf("  buco di rete, classe 2: ACCENSIONE a +%.3f s, RILASCIO %.3f s dopo i rail\n",
           t_acc - t0, t_rel - t_ok);
}

/* ---------------------------------------------------------------- 4.6 */
static void t_guasto(void)
{
    /* the - rail out with the mains present: the supervisor drops MUTE_G */
    float t0 = in_musica(csv_per("guasto"));
    M.sup_trip = 1;
    M.in.v_sup_m = 1.40f;
    mondo_isr(&M);
    CHECK(M.out.mute_req == 0 && M.out.permit_req == 0, "guasto: MUTE_REQ o PERMIT_REQ ancora su");
    mondo_corri(&M, 10000);                /* the front stays on */
    float t_g = primo_stato(&M, ST_GUASTO, t0);
    float t_ma = primo_fronte(&M, M.mains, 0, t0);
    float t_vr = primo_fronte(&M, M.vrel, 0, t0);
    CHECK(t_g > 0 && t_g - t0 <= 0.021f, "GUASTO a +%.4f s, voluto entro la finestra di 20 ms", t_g - t0);
    CHECK(t_ma - t0 >= 0.080f - 1e-6f && t_ma == t_vr,
          "MAINS_REQ %.4f / VRELAY_EN %.4f s dopo il mute, voluti insieme e >= 80 ms", t_ma - t0, t_vr - t0);
    CHECK(primo_fronte(&M, M.mains, 1, t_ma) < 0, "la rete si riaccende col frontale ancora acceso");
    /* front off, then on: only now the power-up */
    M.in.front_in = 1;
    mondo_corri(&M, 500);
    rete_sana(&M.in);
    M.sup_trip = 0;
    float t_on = M.t_us * 1e-6f;
    M.in.front_in = 0;
    mondo_corri(&M, 100);
    mondo_chiudi(&M);
    float t_ri = primo_fronte(&M, M.mains, 1, t_on);
    CHECK(VICINO(t_ri - t_on, 0.020f, TICK), "dopo spento/acceso la rete torna %.4f s dopo, voluto 20 ms",
          t_ri - t_on);
    printf("  guasto: GUASTO +%.3f, MAINS_REQ e VRELAY_EN giu' +%.3f s, ritenuta per 10 s, "
           "riaccensione solo dopo spento/acceso\n", t_g - t0, t_ma - t0);

    /* a fault seen by the ADC alone, in MUTO (MUTE_REQ already low) */
    t0 = in_muto(NULL);
    M.in.v_sup_p = 2.0f;
    mondo_corri(&M, 100);
    CHECK(primo_stato(&M, ST_GUASTO, t0) > 0, "guasto in MUTO visto dall'ADC: non va in GUASTO");
}

/* ------------------------------------------- spec sec. 5: the calibration */
static void t_calibrazione(void)
{
    /* (a) the top's read corrupted by +50 % at the power-up (a glitch, a
     * string still moving): the read-back of the corrected top must refuse
     * it and restore the previous calibration; MUTO retries it 1 s later */
    mondo_init(&M, NULL);
    M.in.mute_sw_in = 1;
    float t_dac = -1;
    for (int k = 0; k < 4000; k++) {
        mondo_corri(&M, 1);
        float t = M.t_us * 1e-6f;
        if (t_dac < 0 && M.out.dac_on)
            t_dac = t;
        M.adc_gain = (t_dac > 0 && t >= t_dac + 0.150f && t <= t_dac + 0.210f) ? 0.5f : 0.0f;
    }
    float t_vr = primo_fronte(&M, M.vrel, 1, 0);
    float t_muto = primo_stato(&M, ST_MUTO, 0);
    CHECK(M.st.n_cal_reject >= 1, "la lettura falsata non e' stata rifiutata");
    CHECK(t_muto > 0, "non arriva in MUTO");
    /* the retry in MUTO: 1 s + 400 ms + 200 ms of read-back */
    float e = (float)db(M.ip[idx_a(&M, t_muto + 1.9f)], 12e-3);
    CHECK(M.st.cal_ok_p && fabsf(e) <= 0.1f, "dopo il ritentativo in MUTO la cima sta a %+.3f dB (cal_ok %d)",
          e, M.st.cal_ok_p);
    printf("  calibrazione: lettura falsata del 50%% rifiutata (%u rifiuti), VRELAY_EN a %.3f s, "
           "ritentata in MUTO: cima %+.3f dB\n", M.st.n_cal_reject, t_vr, e);

    /* (b) the shunt string open (J3 unplugged): no current, no calibration,
     * and never a code above the uncalibrated top */
    mondo_init(&M, NULL);
    M.in.mute_sw_in = 1;
    M.off_p = 0.5f;                     /* the plant needs 0.5 V more: ~0 A */
    mondo_corri(&M, 4000);
    uint16_t cmax = 0, lim = timer_law_code(LDR_I_TOP, 25.0f, NULL);
    for (int k = 0; k < M.n; k++)
        if (M.cp[k] > cmax) cmax = M.cp[k];
    CHECK(!M.st.cal_ok_p && M.st.n_cal_reject >= 1, "stringa aperta: calibrazione accettata");
    CHECK(cmax <= lim, "stringa aperta: codice della derivazione %u oltre la cima non calibrata %u", cmax, lim);
    printf("  calibrazione: stringa aperta, %u rifiuti, codice massimo %u (cima non calibrata %u)\n",
           M.st.n_cal_reject, cmax, lim);
}

/* ---------------------------------------------------------------- main */
typedef struct { const char *nome; void (*f)(void); } test_t;
static const test_t TESTS[] = {
    {"accensione", t_accensione}, {"inserzione", t_inserzione}, {"rilascio", t_rilascio},
    {"inversione", t_inversione}, {"spegnimento", t_spegnimento}, {"debounce", t_debounce},
    {"buco_classe1", t_buco_classe1}, {"buco_classe2", t_buco_classe2}, {"guasto", t_guasto},
    {"calibrazione", t_calibrazione},
};

int main(int argc, char **argv)
{
    const char *sel[32];
    int nsel = 0;
    for (int k = 1; k < argc; k++) {
        if (!strcmp(argv[k], "--csv") && k + 1 < argc)
            csv_dir = argv[++k];
        else if (nsel < 32)
            sel[nsel++] = argv[k];
    }
    int fallite = 0;
    for (size_t k = 0; k < sizeof TESTS / sizeof TESTS[0]; k++) {
        int run = nsel == 0;
        for (int j = 0; j < nsel; j++)
            if (!strcmp(sel[j], TESTS[k].nome)) run = 1;
        if (!run)
            continue;
        int f0 = n_fail;
        test_corrente = TESTS[k].nome;
        TESTS[k].f();
        printf("%s %s\n", n_fail == f0 ? "PASSA" : "FALLISCE", TESTS[k].nome);
        if (n_fail != f0)
            fallite++;
    }
    printf("== test_sequenze: %d controlli, %d falliti, %d test falliti\n", n_check, n_fail, fallite);
    return n_fail > 255 ? 255 : n_fail;
}
