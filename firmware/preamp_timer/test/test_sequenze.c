/*
 * test_sequenze.c - one test per sequence of spec sec. 4 (L41b2; the mute
 * with the relays alone since L47c2a, ADR-062), and the free pins (sec. 2).
 *
 *   test_sequenze [--root <repo>] [nome ...]   run the named tests (all if none)
 *   test_sequenze --csv <dir>                  also write each test's outputs to <dir>/<nome>.csv
 *
 * --root: the repository, for pin_liberi (it reads circuits/preamp/psu.net).
 * Exit code: the number of failed checks. Each test is also run against the
 * fake builds (FALSO_n, run_host_tests.sh) and must fail there.
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mondo.h"

static mondo_t M;                    /* ~0.4 MB: static, not on the stack */
static const char *csv_dir;
static const char *root;
static const float TICK = 1e-3f;     /* the adapter's period */

static const char *csv_per(const char *nome)
{
    static char p[512];
    if (!csv_dir)
        return NULL;
    snprintf(p, sizeof p, "%s/%s.csv", csv_dir, nome);
    return p;
}

#define VICINO(a, b, tol) (fabsf((a) - (b)) <= (tol) + 2e-5f)

/* ---------------------------------------------------------------- 4.1 */
static void t_accensione(void)
{
    mondo_init(&M, csv_per("accensione"));
    /* from standby: the toroid off, no rails; the front switched on at t = 0 */
    M.in.v_sup_p = 0.0f;
    M.in.v_sup_m = 2.3f;
    float t_rail = -1;
    for (int k = 0; k < 2000; k++) {
        mondo_corri(&M, 1);
        if (t_rail < 0 && M.out.mains_req)
            t_rail = M.t_us * 1e-6f + 0.300f;          /* the rails come 300 ms later */
        if (t_rail > 0 && M.t_us * 1e-6f >= t_rail - 1e-6f)
            rete_sana(&M.in);
    }
    mondo_chiudi(&M);
    float t_mains = primo_fronte(&M, M.mains, 1, 0);
    float t_vr = primo_fronte(&M, M.vrel, 1, 0);
    float t_mu = primo_fronte(&M, M.mute, 1, 0);
    float t_pe = primo_fronte(&M, M.perm, 1, 0);
    float t_mus = primo_stato(&M, ST_MUSICA, 0);
    CHECK(VICINO(t_mains, 0.020f, TICK), "MAINS_REQ a %.4f s, voluto 0,020 (debounce 20 ms)", t_mains);
    CHECK(t_vr >= t_rail + 0.100f - 1e-6f && t_vr <= t_rail + 0.100f + TICK,
          "VRELAY_EN %.4f s dopo i rail, voluto 100 ms (4.1 passo 2; niente calibrazione, ADR-062)",
          t_vr - t_rail);
    CHECK(t_mu - t_vr >= 0.050f - 1e-6f && t_mu - t_vr <= 0.050f + TICK,
          "MUTE_REQ %.4f s dopo VRELAY_EN, voluto >= 50 ms (ADR-027: 13 ms)", t_mu - t_vr);
    CHECK(t_pe == t_mu, "PERMIT_REQ (%.4f) e MUTE_REQ (%.4f) nello stesso istante (4.3)", t_pe, t_mu);
    CHECK(VICINO(t_mus - t_mu, 0.010f, TICK), "MUSICA %.4f s dopo MUTE_REQ, voluto 10 ms (il G6K)",
          t_mus - t_mu);
    printf("  accensione: MAINS_REQ %.3f, VRELAY_EN %.3f, MUTE/PERMIT_REQ %.3f, MUSICA %.3f s\n",
           t_mains, t_vr, t_mu, t_mus);

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

/* Power up to MUSICA (or MUTO) and stay 1 s; returns now. */
static float in_musica(const char *csv)
{
    mondo_init(&M, csv);
    porta_a(&M, ST_MUSICA);
    mondo_corri(&M, 1000);
    return M.t_us * 1e-6f;
}

static float in_muto(const char *csv)
{
    mondo_init(&M, csv);
    M.in.mute_sw_in = 1;
    porta_a(&M, ST_MUTO);
    mondo_corri(&M, 1000);
    return M.t_us * 1e-6f;
}

/* ---------------------------------------------------------------- 4.2 */
static void t_inserzione(void)
{
    float t0 = in_musica(csv_per("inserzione"));
    M.in.mute_sw_in = 1;
    mondo_corri(&M, 1000);
    mondo_chiudi(&M);
    float t_ins = primo_stato(&M, ST_INSERZIONE, t0);
    float t_mu = primo_fronte(&M, M.mute, 0, t0);
    float t_pe = primo_fronte(&M, M.perm, 0, t0);
    float t_muto = primo_stato(&M, ST_MUTO, t0);
    CHECK(VICINO(t_ins - t0, 0.020f, TICK), "INSERZIONE %.4f s dopo SW3, voluto 20 ms", t_ins - t0);
    CHECK(t_mu == t_ins, "MUTE_REQ giu' %.4f s dopo l'INSERZIONE, voluto nello stesso istante: "
          "i rele' subito dopo il tasto (ADR-062)", t_mu - t_ins);
    CHECK(t_pe - t_mu >= 0.020f - 1e-6f && t_pe - t_mu <= 0.020f + TICK,
          "PERMIT_REQ giu' %.4f s dopo MUTE_REQ, voluto 20 ms (ADR-045)", t_pe - t_mu);
    CHECK(t_muto == t_pe, "MUTO a %.4f, PERMIT_REQ giu' a %.4f: voluti insieme", t_muto, t_pe);
    printf("  inserzione: INSERZIONE e MUTE_REQ +%.3f, PERMIT_REQ +%.3f, MUTO +%.3f s\n",
           t_ins - t0, t_pe - t0, t_muto - t0);

    /* the switch back to music inside Delta: not reversible (ADR-062); the
     * insertion completes, then a release from MUTO */
    t0 = in_musica(NULL);
    M.in.mute_sw_in = 1;
    mondo_corri(&M, 25);                     /* MUTE_REQ low since +20 ms */
    float t_back = M.t_us * 1e-6f;
    M.in.mute_sw_in = 0;
    mondo_corri(&M, 500);
    t_mu = primo_fronte(&M, M.mute, 0, t0);
    t_pe = primo_fronte(&M, M.perm, 0, t0);
    float t_mu2 = primo_fronte(&M, M.mute, 1, t_mu);
    CHECK(t_pe - t_mu >= 0.020f - 1e-6f, "tasto tornato a musica nel Delta: PERMIT_REQ giu' %.4f s "
          "dopo MUTE_REQ, voluto 20 ms", t_pe - t_mu);
    CHECK(t_mu2 > t_pe && VICINO(t_mu2 - t_back, 0.020f, TICK),
          "tasto tornato a musica nel Delta: MUTE_REQ risale %.4f s dopo il tasto, voluto 20 ms e "
          "dopo PERMIT_REQ giu'", t_mu2 - t_back);
    printf("  inserzione con ritorno nel Delta: PERMIT_REQ giu' +%.3f, MUTE_REQ su +%.3f s dal ritorno\n",
           t_pe - t_mu, t_mu2 - t_back);
}

/* ---------------------------------------------------------------- 4.3 */
static void t_rilascio(void)
{
    float t0 = in_muto(csv_per("rilascio"));
    M.in.mute_sw_in = 0;
    mondo_corri(&M, 500);
    mondo_chiudi(&M);
    float t_mu = primo_fronte(&M, M.mute, 1, t0);
    float t_pe = primo_fronte(&M, M.perm, 1, t0);
    float t_mus = primo_stato(&M, ST_MUSICA, t0);
    CHECK(VICINO(t_mu - t0, 0.020f, TICK), "MUTE_REQ su %.4f s dopo SW3, voluto 20 ms", t_mu - t0);
    CHECK(t_pe == t_mu, "PERMIT_REQ e MUTE_REQ non insieme (%.4f, %.4f)", t_pe, t_mu);
    CHECK(VICINO(t_mus - t_mu, 0.010f, TICK), "MUSICA %.4f s dopo i rele', voluto 10 ms (il G6K)",
          t_mus - t_mu);
    printf("  rilascio: MUTE/PERMIT_REQ +%.3f, MUSICA +%.3f s\n", t_mu - t0, t_mus - t0);

    /* the hardware refuses the release (MUTE_G stays low): after the G6K's
     * 10 ms the core sees it and mutes (spec 4.5 step 1), never MUSICA */
    t0 = in_muto(NULL);
    M.mute_g_manuale = 1;
    M.in.mute_g_in = 0;
    M.in.mute_sw_in = 0;
    mondo_corri(&M, 200);
    t_mu = primo_fronte(&M, M.mute, 1, t0);
    float t_b = primo_stato(&M, ST_BUCO_RETE, t0);
    CHECK(primo_stato(&M, ST_MUSICA, t0) < 0, "rilascio rifiutato dall'hardware: il core e' andato in MUSICA");
    CHECK(t_b > 0 && VICINO(t_b - t_mu, 0.010f, TICK), "rilascio rifiutato: BUCO_RETE %.4f s dopo "
          "MUTE_REQ, voluto 10 ms", t_b - t_mu);
    CHECK(M.out.mute_req == 0 && M.out.permit_req == 0, "rilascio rifiutato: MUTE_REQ %d, PERMIT_REQ %d",
          M.out.mute_req, M.out.permit_req);
}

/* ---------------------------------------------------------------- 4.4 */
static void t_spegnimento(void)
{
    float t0 = in_musica(csv_per("spegnimento"));
    M.in.front_in = 1;
    mondo_corri(&M, 500);
    mondo_chiudi(&M);
    float t_mu = primo_fronte(&M, M.mute, 0, t0);
    float t_pe = primo_fronte(&M, M.perm, 0, t0);
    float t_vr = primo_fronte(&M, M.vrel, 0, t0);
    float t_ma = primo_fronte(&M, M.mains, 0, t0);
    float t_sb = primo_stato(&M, ST_STANDBY, t0);
    CHECK(VICINO(t_mu - t0, 0.020f, TICK), "MUTE_REQ giu' %.4f s dopo il frontale, voluto 20 ms", t_mu - t0);
    CHECK(t_pe - t_mu >= 0.020f - 1e-6f, "PERMIT_REQ %.4f s dopo MUTE_REQ, voluto 20 ms (ADR-045)",
          t_pe - t_mu);
    CHECK(t_vr - t_pe >= 0.080f - 1e-6f && t_vr - t_pe <= 0.080f + TICK,
          "VRELAY_EN giu' %.4f s dopo PERMIT_REQ, voluto 80 ms: 50 dopo PERMIT_CMD (ADR-046) "
          "piu' il Delta dell'hardware", t_vr - t_pe);
    CHECK(t_ma == t_vr, "MAINS_REQ (%.4f) e VRELAY_EN (%.4f) non insieme (4.4 passo 3)", t_ma, t_vr);
    CHECK(t_sb == t_ma, "STANDBY %.4f, rete %.4f", t_sb, t_ma);
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
    mondo_corri(&M, 500);
    CHECK(primo_fronte(&M, M.mute, 0, t0) > 0, "frontale spento con SW3 a musica: il mute non entra");
    printf("  debounce: rimbalzi di 5 ms ignorati, inserzione 20 ms dopo l'ultimo; filo rotto = mute\n");
}

/* ---------------------------------------------------------------- 4.5 */
static void t_buco_classe1(void)
{
    /* the rails ride through: the detector at +5 ms (slower than MUTE_G, so
     * the reaction can only come from MUTE_G_IN), mains back at +40 ms */
    in_musica(csv_per("buco_rete"));
    mondo_corri(&M, 0);
    M.sup_trip = 1;
    mondo_isr(&M);                         /* the pin-change interrupt */
    float t_hole = M.t_us * 1e-6f;
    CHECK(M.out.mute_req == 0 && M.out.permit_req == 0,
          "all'interruzione MUTE_REQ %d, PERMIT_REQ %d: voluti giu' subito (4.5 passo 1)",
          M.out.mute_req, M.out.permit_req);
    mondo_corri(&M, 5);
    rete_assente(&M.in);
    mondo_corri(&M, 35);
    rete_sana(&M.in);
    M.sup_trip = 0;
    float t_back = M.t_us * 1e-6f;
    mondo_corri(&M, 1000);
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

    /* the detector alone (MUTE_G still up): mute from ADC_MD */
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
    mondo_corri(&M, 1000);
    mondo_chiudi(&M);
    float t_acc = primo_stato(&M, ST_ACCENSIONE, t0);
    float t_rel = primo_fronte(&M, M.mute, 1, t0 + 0.001f);
    CHECK(t_acc > 0, "classe 2: l'accensione non si rifa'");
    CHECK(t_rel - t_ok >= 0.100f + 0.050f - 1e-6f,
          "RILASCIO %.4f s dopo i rail, voluto >= 100 + 50 ms (4.1 dal passo 2)", t_rel - t_ok);
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

/* --------------------------------------------- spec sec. 2: the free pins */
/* The ATtiny3216's SOIC-20 pinout, written again here from DS40002205A
 * (sec. 4.1, "20-Pin SOIC", p. 14), not from the core: pin -> port, bit (0 = power). */
static const struct { int pin; char port; int bit; } PINOUT[] = {
    {1, 0, 0}, {2, 'A', 4}, {3, 'A', 5}, {4, 'A', 6}, {5, 'A', 7}, {6, 'B', 5}, {7, 'B', 4},
    {8, 'B', 3}, {9, 'B', 2}, {10, 'B', 1}, {11, 'B', 0}, {12, 'C', 0}, {13, 'C', 1},
    {14, 'C', 2}, {15, 'C', 3}, {16, 'A', 0}, {17, 'A', 1}, {18, 'A', 2}, {19, 'A', 3}, {20, 0, 0}};

static void t_pin_liberi(void)
{
    /* the pins of U509 that psu.net puts on a net */
    int usato[21] = {0};
    char path[1024];
    snprintf(path, sizeof path, "%s/circuits/preamp/psu.net", root ? root : ".");
    FILE *f = fopen(path, "r");
    CHECK(f != NULL, "non apro %s", path);
    if (!f)
        return;
    char r[512];
    int dopo_u509 = 0, nodi = 0;
    while (fgets(r, sizeof r, f)) {
        int p;
        if (strstr(r, "(ref \"U509\")")) {
            dopo_u509 = 1;
            continue;
        }
        if (dopo_u509 && sscanf(r, " (pin \"%d\")", &p) == 1 && p >= 1 && p <= 20) {
            usato[p] = 1;
            nodi++;
        }
        dopo_u509 = 0;
    }
    fclose(f);
    CHECK(nodi >= 10, "psu.net: solo %d nodi di U509, il formato non e' quello atteso", nodi);

    /* every listed pin is free, matches the pinout, and every free pin is listed */
    int listato[21] = {0};
    for (unsigned k = 0; k < TIMER_N_PIN_LIBERI; k++) {
        timer_pin_t q = TIMER_PIN_LIBERI[k];
        CHECK(q.pin >= 1 && q.pin <= 20, "pin %u fuori dal contenitore", q.pin);
        if (q.pin < 1 || q.pin > 20)
            continue;
        listato[q.pin] = 1;
        CHECK(PINOUT[q.pin - 1].port == q.port && PINOUT[q.pin - 1].bit == q.bit,
              "il pin %u e' P%c%d, la lista dice P%c%u", q.pin, PINOUT[q.pin - 1].port,
              PINOUT[q.pin - 1].bit, q.port, q.bit);
        CHECK(!usato[q.pin], "P%c%u (pin %u) e' nella lista dei liberi ma psu.net lo collega",
              q.port, q.bit, q.pin);
    }
    int liberi = 0;
    for (int p = 1; p <= 20; p++) {
        if (!PINOUT[p - 1].port || usato[p])
            continue;
        liberi++;
        CHECK(listato[p], "P%c%d (pin %d) e' libero in psu.net ma manca dalla lista",
              PINOUT[p - 1].port, PINOUT[p - 1].bit, p);
    }
    /* the user's choice (L47c2a): the digital input buffer disabled */
    CHECK(TIMER_PIN_LIBERI_ISC == 0x4u, "ISC dei pin liberi %u, voluto 0x4 INPUT_DISABLE "
          "(DS40002205A sec. 16.5.11)", TIMER_PIN_LIBERI_ISC);
    printf("  pin liberi: %u nella lista, %d liberi in psu.net, ISC 0x%x\n", TIMER_N_PIN_LIBERI, liberi,
           TIMER_PIN_LIBERI_ISC);
}

/* ---------------------------------------------------------------- main */
typedef struct { const char *nome; void (*f)(void); } test_t;
static const test_t TESTS[] = {
    {"accensione", t_accensione}, {"inserzione", t_inserzione}, {"rilascio", t_rilascio},
    {"spegnimento", t_spegnimento}, {"debounce", t_debounce}, {"buco_classe1", t_buco_classe1},
    {"buco_classe2", t_buco_classe2}, {"guasto", t_guasto}, {"pin_liberi", t_pin_liberi},
};

int main(int argc, char **argv)
{
    const char *sel[32];
    int nsel = 0;
    for (int k = 1; k < argc; k++) {
        if (!strcmp(argv[k], "--csv") && k + 1 < argc)
            csv_dir = argv[++k];
        else if (!strcmp(argv[k], "--root") && k + 1 < argc)
            root = argv[++k];
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
