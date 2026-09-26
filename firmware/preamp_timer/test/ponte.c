/*
 * ponte.c - the core driven by the circuit (L41b2): reads what the micro's
 * pins see in a SPICE run, runs timer_step on it, writes what the pins must
 * do. With genera_tb_psu.py it closes the loop by iteration: circuit ->
 * core -> circuit, until the core's outputs no longer change (a fixed point).
 *
 *   ponte <ingressi.txt> <uscite.csv> --da <t0> [--preambolo muto|musica]
 *         [--pilota <core_prev.csv>]
 *
 * <ingressi.txt>: ngspice wrdata with wr_singlescale and wr_vecnames, the
 * columns time, v(front_in), v(mute_sw_in), v(mute_g_in), v(adc_sup_p),
 * v(adc_sup_m), v(adc_sup_vr), v(adc_md), v(adc_i_s), v(adc_i_p).
 * Before t0 the micro is held (reset, or the preamble's state, see below)
 * and the outputs are constant; from t0 timer_step runs every 1 ms, plus once
 * with dt = 0 at each falling edge of MUTE_G_IN (the pin-change interrupt).
 * Pins: digital above 2.5 V (V5 / 2); the sense pins read V / 10 ohm; an
 * ideal ADC (its errors are test_legge's budget); t_c = 25 C, the deck's.
 * --preambolo: the core first runs in the host world (mondo.c, a healthy
 * supply, a plant with L41b1's bench error at 25 C) up to MUTO or MUSICA and
 * 2 s more (its calibrations done), and holds that state until t0.
 * --pilota: the core outputs that drove this SPICE run. Where the core's
 * MUTE_REQ now differs from the one that drove the circuit, MUTE_G_IN is not
 * a measurement of THIS core: it answers an old output (in the first pass a
 * release the circuit never received; later a mute the core no longer
 * makes). There the pin is rebuilt from the supervisors the core reads -
 * MUTE_G = MUTE_REQ unless the mains, a rail or VRELAY_REG is out - and the
 * substitutions are counted. Without it the iteration kept a ghost: a fall
 * of MUTE_G caused by the previous pass's output, answered 0.1 ms later,
 * moving 0.1 ms a pass and never converging (L41b2). AT THE FIXED POINT THE
 * COUNT MUST BE 0: the driving and the resulting outputs are then the same
 * everywhere, and every pin the core read is the circuit's.
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mondo.h"

#define NCOL 10
static const char *NOMI[NCOL] = {"time", "v(front_in)", "v(mute_sw_in)", "v(mute_g_in)",
                                 "v(adc_sup_p)", "v(adc_sup_m)", "v(adc_sup_vr)", "v(adc_md)",
                                 "v(adc_i_s)", "v(adc_i_p)"};
static double *col[NCOL];
static int nrow;
static mondo_t M;

static int leggi(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "ponte: non apro %s\n", path); return 0; }
    char *riga = malloc(1 << 16);
    if (!fgets(riga, 1 << 16, f)) { fclose(f); return 0; }
    int idx[64], nh = 0;
    char *tok = strtok(riga, " \t\r\n");
    int map[NCOL];
    for (int k = 0; k < NCOL; k++) map[k] = -1;
    while (tok && nh < 64) {
        for (int k = 0; k < NCOL; k++)
            if (!strcmp(tok, NOMI[k])) map[k] = nh;
        idx[nh] = nh;
        nh++;
        tok = strtok(NULL, " \t\r\n");
    }
    (void)idx;
    for (int k = 0; k < NCOL; k++)
        if (map[k] < 0) { fprintf(stderr, "ponte: manca la colonna %s\n", NOMI[k]); return 0; }
    int cap = 1 << 16;
    for (int k = 0; k < NCOL; k++) col[k] = malloc(sizeof(double) * cap);
    double v[64];
    while (fgets(riga, 1 << 16, f)) {
        int n = 0;
        char *p = riga, *e;
        while (n < nh) {
            v[n] = strtod(p, &e);
            if (e == p) break;
            p = e;
            n++;
        }
        if (n < nh) continue;
        if (nrow == cap) {
            cap *= 2;
            for (int k = 0; k < NCOL; k++) col[k] = realloc(col[k], sizeof(double) * cap);
        }
        for (int k = 0; k < NCOL; k++) col[k][nrow] = v[map[k]];
        nrow++;
    }
    fclose(f);
    free(riga);
    return nrow > 1;
}

static int cur;                         /* the row at or before the last query */
static double a(int c, double t)
{
    while (cur + 1 < nrow && col[0][cur + 1] <= t) cur++;
    while (cur > 0 && col[0][cur] > t) cur--;
    if (cur + 1 >= nrow) return col[c][nrow - 1];
    double t0 = col[0][cur], t1 = col[0][cur + 1];
    double u = t1 > t0 ? (t - t0) / (t1 - t0) : 0;
    return col[c][cur] + u * (col[c][cur + 1] - col[c][cur]);
}

static void pin(double t, timer_in_t *in)
{
    in->front_in = a(1, t) > 2.5;
    in->mute_sw_in = a(2, t) > 2.5;
    in->mute_g_in = a(3, t) > 2.5;
    in->v_sup_p = (float)a(4, t);
    in->v_sup_m = (float)a(5, t);
    in->v_sup_vr = (float)a(6, t);
    in->v_md = (float)a(7, t);
    in->i_s = (float)(a(8, t) / 10.0);
    in->i_p = (float)(a(9, t) / 10.0);
    in->t_c = 25.0f;
}

/* the driving outputs' MUTE_REQ, as steps */
static double *pt;
static int *pv, npil;
static int pilota_mute(double t)
{
    int v = 0;
    for (int k = 0; k < npil && pt[k] <= t + 1e-12; k++) v = pv[k];
    return v;
}
static int leggi_pilota(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) return 0;
    char r[512];
    int cap = 1024;
    pt = malloc(sizeof(double) * cap);
    pv = malloc(sizeof(int) * cap);
    while (fgets(r, sizeof r, f)) {
        double t;
        int a, b, c;
        if (sscanf(r, "%lf,%d,%d,%d", &t, &a, &b, &c) != 4) continue;
        if (npil == cap) {
            cap *= 2;
            pt = realloc(pt, sizeof(double) * cap);
            pv = realloc(pv, sizeof(int) * cap);
        }
        pt[npil] = t;
        pv[npil] = c;
        npil++;
    }
    fclose(f);
    return npil > 0;
}
static long n_sost;
static int sup_ok(const timer_in_t *in)
{
    return in->v_md <= V_MD_ABSENT && in->v_sup_p >= V_SUP_P_FAIL && in->v_sup_m <= V_SUP_M_FAIL &&
           in->v_sup_vr >= V_SUP_VR_FAIL;
}
/* MUTE_G_IN for this core at t: the circuit's, or rebuilt (see the header) */
static void correggi(double t, const timer_state_t *st, timer_in_t *in)
{
    if (!npil || pilota_mute(t) == st->mute_req)
        return;
    uint8_t v = (uint8_t)(st->mute_req && sup_ok(in));
    if (v != in->mute_g_in) n_sost++;
    in->mute_g_in = v;
}

static FILE *out;
static timer_out_t ultima;
static int prima = 1;
static void scrivi(double t, const timer_state_t *st, timer_out_t o)
{
    if (!prima && !memcmp(&o, &ultima, sizeof o))
        return;
    prima = 0;
    ultima = o;
    fprintf(out, "%.6f,%d,%d,%d,%d,%d,%d,%d,%s,%.6f\n", t, o.mains_req, o.vrelay_en, o.mute_req,
            o.permit_req, o.dac_on, o.code_s, o.code_p, timer_stato_nome(o.stato), st->d);
}

int main(int argc, char **argv)
{
    if (argc < 5) {
        fprintf(stderr, "uso: ponte <ingressi.txt> <uscite.csv> --da <t0> [--preambolo muto|musica]\n");
        return 2;
    }
    double t0 = 0;
    const char *pre = NULL;
    for (int k = 3; k < argc; k++) {
        if (!strcmp(argv[k], "--da") && k + 1 < argc) t0 = atof(argv[++k]);
        else if (!strcmp(argv[k], "--preambolo") && k + 1 < argc) pre = argv[++k];
        else if (!strcmp(argv[k], "--pilota") && k + 1 < argc) {
            if (!leggi_pilota(argv[++k])) { fprintf(stderr, "ponte: pilota illeggibile\n"); return 1; }
        }
    }
    if (!leggi(argv[1])) return 1;
    out = fopen(argv[2], "w");
    if (!out) return 1;
    fprintf(out, "t,mains_req,vrelay_en,mute_req,permit_req,dac_on,code_s,code_p,stato,d\n");

    timer_state_t st;
    timer_in_t in;
    memset(&ultima, 0, sizeof ultima);
    if (pre) {
        mondo_init(&M, NULL);
        /* the circuit's own error at 25 C, from L41b2's DC bench with the
         * 12 mA top (ldr/cal_cima12mA.json, S_25 = P_25) */
        M.off_s = M.off_p = -1.613e-4f;
        M.r_s = M.r_p = 0.6462f;
        M.in.mute_sw_in = !strcmp(pre, "muto");
        porta_a(&M, !strcmp(pre, "muto") ? ST_MUTO : ST_MUSICA);
        mondo_corri(&M, 2000);
        st = M.st;
        st.t_fase = UINT32_MAX / 2;     /* long in the state: no step pending */
        in = M.in;
        scrivi(0.0, &st, M.out);
    } else {
        pin(t0, &in);
        timer_init(&st, &in);
        timer_out_t o = {0};
        o.power_down = 1;
        scrivi(0.0, &st, o);
    }
    /* from t0: 1 ms ticks, and the interrupt at MUTE_G_IN's falling edges */
    double tfin = col[0][nrow - 1];
    double t = t0;
    int mg_prima = a(3, t0) > 2.5;
    pin(t0, &in);
    scrivi(t0, &st, timer_step(&st, &in, 0));
    const double TICK = 1e-3;
    int ks = 0;                          /* the edge search's first row */
    while (t + TICK <= tfin + 1e-12) {
        /* an interrupt inside (t, t + TICK]: find the crossing on the samples */
        double tx = -1;
        while (ks + 1 < nrow && col[0][ks + 1] <= t) ks++;
        for (int k = ks; k < nrow - 1; k++) {
            if (col[0][k] > t + TICK) break;
            int g0 = col[3][k] > 2.5, g1 = col[3][k + 1] > 2.5;
            if (g0 && !g1) {
                double u = (col[3][k] - 2.5) / (col[3][k] - col[3][k + 1]);
                double tc = col[0][k] + u * (col[0][k + 1] - col[0][k]);
                if (tc > t && tc <= t + TICK) { tx = tc; break; }
            }
        }
        /* an edge the driving outputs explain and this core did not cause is
         * not an interrupt of this core */
        /* the driving output causes an edge 0.1-0.3 ms after it falls (R513,
         * C_MUTE_G): one that fell less than 50 us before tx did not cause it
         * (without this margin the reaction alternated between the interrupt
         * and the next tick, pass after pass) */
        if (tx > 0 && mg_prima && (!npil || pilota_mute(tx - 50e-6) == st.mute_req)) {
            pin(tx, &in);
            correggi(tx, &st, &in);
            scrivi(tx, &st, timer_step(&st, &in, 0));
        }
        t += TICK;
        pin(t, &in);
        correggi(t, &st, &in);
        mg_prima = in.mute_g_in;
        scrivi(t, &st, timer_step(&st, &in, (uint32_t)lround(TICK * 1e6)));
    }
    fclose(out);
    printf("ponte: %d righe lette, core da %.3f a %.3f s, stato finale %s, sostituzioni di MUTE_G_IN %ld\n",
           nrow, t0, t, timer_stato_nome((uint8_t)st.stato), n_sost);
    return 0;
}
