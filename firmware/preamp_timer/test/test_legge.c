/*
 * test_legge.c - the LDR law (spec sec. 5) against the bench and the table (L41b2).
 *
 *   test_legge <repo>
 *
 * (a) codici:  the core's DAC code for every point of L41b1's bench decks
 *              (nocomp, comp, cal with cal.json) equals the code the bench's
 *              generator computed - the C law is the bench's law;
 * (b) cal_l41b1: the core's fit, given L41b1's simulated currents at 20 mA and
 *              2 mA with L41b1's abscissa (the wanted current), returns cal.json;
 * (c) tabella: the v4 table with the 12 mA top (ADR-050), at 15/25/35/45/60 C,
 *              on a plant with the bench's own error (cal.json at that T),
 *              after the core's calibration (abscissa = the read current);
 * (d) bilancio: the same with the ADC's and the sensor's errors (DS40002205A
 *              Tables 36-27, 36-28, pin leakage): printed, and the typical
 *              corner held to ADR-049's +-1 dB.
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mondo.h"

static mondo_t M;
static char repo[1024];

static const char *L41B1 = "docs/preamp/data/2026-09-26/L41b1/ldr";
static const int TEMPS[] = {15, 25, 35, 45, 60};

static FILE *apri(const char *rel)
{
    char p[2048];
    snprintf(p, sizeof p, "%s/%s", repo, rel);
    FILE *f = fopen(p, "r");
    if (!f) {
        printf("  non trovo %s\n", p);
        n_fail++;
    }
    return f;
}

/* cal.json: {"S_15": {"off": x, "r_ohm": y}, ...} - read by key */
static int leggi_cal(const char *testo, char s, int t, timer_cal_t *c)
{
    char key[16];
    snprintf(key, sizeof key, "\"%c_%d\"", s, t);
    const char *p = strstr(testo, key);
    if (!p) return 0;
    const char *o = strstr(p, "\"off\":"), *r = strstr(p, "\"r_ohm\":");
    if (!o || !r) return 0;
    c->off = strtof(o + 6, NULL);
    c->r_ohm = strtof(r + 8, NULL);
    return 1;
}

static char cal_json[8192];

static void carica_cal_json(void)
{
    char rel[512];
    snprintf(rel, sizeof rel, "%s/cal.json", L41B1);
    FILE *f = apri(rel);
    if (!f) return;
    size_t n = fread(cal_json, 1, sizeof cal_json - 1, f);
    cal_json[n] = 0;
    fclose(f);
}

/* ---------------------------------------------------------------- (a) */
static void t_codici(void)
{
    const char *logs[] = {"tb_psu_ldr.log", "tb_psu_ldr_cal.log"};
    int n = 0, uguali = 0, uno = 0, peggio = 0;
    for (int j = 0; j < 2; j++) {
        char rel[512];
        snprintf(rel, sizeof rel, "%s/%s", L41B1, logs[j]);
        FILE *f = apri(rel);
        if (!f) return;
        char riga[512];
        while (fgets(riga, sizeof riga, f)) {
            char modo[16], s, nome[32];
            int t, code;
            float i;
            if (sscanf(riga, "PUNTO %15s %c %31s %d %f %d", modo, &s, nome, &t, &i, &code) != 6)
                continue;
            if (!strcmp(modo, "dac_reset"))
                continue;
            timer_cal_t c = {0, 0};
            float t_fw = (float)t;
            if (!strcmp(modo, "nocomp"))
                t_fw = 25.0f;
            if (!strcmp(modo, "cal") && !leggi_cal(cal_json, s, t, &c)) {
                CHECK(0, "cal.json senza %c_%d", s, t);
                continue;
            }
            int mio = timer_law_code(i, t_fw, !strcmp(modo, "cal") ? &c : NULL);
            n++;
            if (mio == code) uguali++;
            else if (abs(mio - code) == 1) uno++;
            else {
                peggio++;
                if (peggio <= 5)
                    printf("  %s %c %s %d C: core %d, banco %d\n", modo, s, nome, t, mio, code);
            }
        }
        fclose(f);
    }
    CHECK(n >= 200, "letti solo %d punti dei deck di L41b1", n);
    CHECK(peggio == 0, "%d codici differiscono di piu' di 1 LSB dal banco", peggio);
    printf("  codici: %d punti dei deck di L41b1, %d uguali, %d a 1 LSB (float contro double), %d oltre\n",
           n, uguali, uno, peggio);
}

/* ---------------------------------------------------------------- (b) */
static void t_cal_l41b1(void)
{
    char rel[512];
    snprintf(rel, sizeof rel, "%s/tb_psu_ldr.log.csv", L41B1);
    FILE *f = apri(rel);
    if (!f) return;
    float top[2][5] = {{0}}, lo[2][5] = {{0}};
    char riga[1024];
    while (fgets(riga, sizeof riga, f)) {
        char modo[16], s, nome[32];
        int t;
        float target, i;
        int code;
        if (sscanf(riga, "%15[^,],%c,%31[^,],%d,%f,%d,%f", modo, &s, nome, &t, &target, &code, &i) != 7)
            continue;
        if (strcmp(modo, "comp"))
            continue;
        int js = s == 'S' ? 0 : 1, jt = -1;
        for (int k = 0; k < 5; k++)
            if (TEMPS[k] == t) jt = k;
        if (jt < 0) continue;
        if (!strcmp(nome, js == 0 ? "d0" : "d1")) top[js][jt] = i;
        if (!strcmp(nome, "cal_2mA")) lo[js][jt] = i;
    }
    fclose(f);
    double doff = 0, dr = 0;
    for (int js = 0; js < 2; js++)
        for (int jt = 0; jt < 5; jt++) {
            timer_cal_t c = {0, 0}, ref;
            char s = js == 0 ? 'S' : 'P';
            int ok = timer_cal_fit_x(&c, (float)TEMPS[jt], 20e-3f, top[js][jt], 20e-3f,
                                     2e-3f, lo[js][jt], 2e-3f);
            CHECK(ok && leggi_cal(cal_json, s, TEMPS[jt], &ref), "fit %c %d C rifiutato", s, TEMPS[jt]);
            doff = fmax(doff, fabs(c.off - ref.off));
            dr = fmax(dr, fabs(c.r_ohm - ref.r_ohm));
        }
    CHECK(doff < 2e-6 && dr < 1e-3, "cal.json non ritrovato: off a %.2g V, r_ohm a %.2g ohm", doff, dr);
    printf("  cal di L41b1 ritrovata dal core: off entro %.2g V, r_ohm entro %.2g ohm\n", doff, dr);
}

/* ---------------------------------------------------------------- (c), (d) */
/* The table points of ADR-039 with the top of ADR-050 (from the ADRs, not the core). */
/* Each point is commanded through the core's profile at its d (L41b2: the
 * first version commanded the currents directly, and a wrong table - FALSO 12,
 * the top back at 20 mA - passed here). */
typedef struct { char s; const char *nome; float d; double i; } punto_t;
static const punto_t PUNTI[] = {
    {'S', "d0", 0.0f, 12e-3}, {'S', "d0.1", 0.1f, 0.2e-3}, {'S', "d0.45", 0.45f, 4.5e-6},
    {'S', "d0.75", 0.75f, 0.19e-6}, {'S', "riposo", 1.0f, 10e-9}, {'P', "riposo", 0.0f, 10e-9},
    {'P', "d0.75", 0.75f, 1.0954451150103323e-05}, {'P', "d1", 1.0f, 12e-3}};

static double tab_log(const double (*p)[2], int n, double d)
{
    if (d <= p[0][0]) return p[0][1];
    for (int k = 1; k < n; k++)
        if (d <= p[k][0]) {
            double u = (d - p[k - 1][0]) / (p[k][0] - p[k - 1][0]);
            return exp(log(p[k - 1][1]) + u * (log(p[k][1]) - log(p[k - 1][1])));
        }
    return p[n - 1][1];
}
static double tab_s(double d)
{
    static const double p[][2] = {{0, 12e-3}, {0.1, 0.2e-3}, {0.45, 4.5e-6}, {0.75, 0.19e-6},
                                  {0.8, 10e-9}, {1, 10e-9}};
    return tab_log(p, 6, d);
}
static double tab_p(double d)
{
    static const double p[][2] = {{0, 10e-9}, {0.5, 10e-9}, {1, 12e-3}};
    return tab_log(p, 3, d);
}

/* One string at one temperature: the core calibrates on the plant (as in
 * ACCENSIONE: top, then 2 mA, reads through the ADC's errors), then every
 * table point is commanded; returns the worst |dB| from 0.19 uA up and the
 * idle current. */
static double una_stringa(char s, int t, float sensore, float adc_off_v, float adc_gain,
                          timer_cal_t plant, double *riposo, double *peggiore_segno)
{
    M.t_true = (float)t;
    timer_cal_t c = {0, 0};
    float t_fw = (float)t + sensore;
    float leggi[2];
    float want[2] = {LDR_I_TOP, LDR_I_CAL_LO};
    for (int k = 0; k < 2; k++) {
        uint16_t code = timer_law_code(want[k], t_fw, &c);
        float i = corrente_vera(&M, code, 1, plant.off, plant.r_ohm);
        leggi[k] = ((i * 10.0f) * (1.0f + adc_gain) + adc_off_v) / 10.0f;
    }
    int ok = timer_cal_fit(&c, t_fw, want[0], leggi[0], want[1], leggi[1]);
    CHECK(ok, "calibrazione rifiutata %c %d C", s, t);
    double peggiore = 0;
    for (size_t k = 0; k < sizeof PUNTI / sizeof PUNTI[0]; k++) {
        if (PUNTI[k].s != s) continue;
        float cmd = s == 'S' ? timer_profile_series(PUNTI[k].d) : timer_profile_shunt(PUNTI[k].d);
        uint16_t code = timer_law_code(cmd, t_fw, &c);
        double i = corrente_vera(&M, code, 1, plant.off, plant.r_ohm);
        double e = 20 * log10(i / PUNTI[k].i);
        if (!strcmp(PUNTI[k].nome, "riposo")) {
            *riposo = i;
            continue;
        }
        if (fabs(e) > fabs(peggiore)) peggiore = e;
    }
    *peggiore_segno = peggiore;
    return fabs(peggiore);
}

static void t_tabella(void)
{
    double peggiore = 0, rmin = 1, rmax = 0;
    for (int jt = 0; jt < 5; jt++)
        for (int js = 0; js < 2; js++) {
            char s = js == 0 ? 'S' : 'P';
            timer_cal_t plant;
            if (!leggi_cal(cal_json, s, TEMPS[jt], &plant)) {
                CHECK(0, "cal.json senza %c_%d", s, TEMPS[jt]);
                continue;
            }
            double rip, seg;
            double e = una_stringa(s, TEMPS[jt], 0, 0, 0, plant, &rip, &seg);
            CHECK(e <= 0.1, "%c a %d C: %+.3f dB dalla tabella v4 (cima 12 mA)", s, TEMPS[jt], seg);
            CHECK(rip >= 5e-9 && rip <= 20e-9, "%c a %d C: riposo %.3g A fuori da 5-20 nA", s, TEMPS[jt], rip);
            if (e > fabs(peggiore)) peggiore = seg;
            rmin = fmin(rmin, rip);
            rmax = fmax(rmax, rip);
        }
    printf("  tabella v4, cima 12 mA, 15-60 C, pianta = errore del banco: peggiore %+.3f dB, "
           "riposo %.2f-%.2f nA\n", peggiore, rmin * 1e9, rmax * 1e9);
}

/* The whole sequence in the world: power-up (the zeros, the shunt's
 * calibration), MUSICA (the series'), then an insertion; the currents
 * against the table along the ramp. Returns the worst dB from 0.19 uA up. */
static double sequenza(int t, float sensore, float adc_off, float adc_gain, double *rmin, double *rmax)
{
    timer_cal_t ps, pp;
    if (!leggi_cal(cal_json, 'S', t, &ps) || !leggi_cal(cal_json, 'P', t, &pp)) {
        CHECK(0, "cal.json senza %d C", t);
        return 99;
    }
    mondo_init(&M, NULL);
    M.t_true = (float)t;
    M.in.t_c = (float)t + sensore;
    M.off_s = ps.off; M.r_s = ps.r_ohm;
    M.off_p = pp.off; M.r_p = pp.r_ohm;
    M.adc_off_v = adc_off;
    M.adc_gain = adc_gain;
    porta_a(&M, ST_MUSICA);
    mondo_corri(&M, 2000);
    int k0 = M.n;
    M.in.mute_sw_in = 1;
    mondo_corri(&M, 6500);
    double w = 0;
    for (int k = k0; k < M.n; k += 20) {
        double ts = tab_s(M.d[k]), tp = tab_p(M.d[k]);
        if (ts >= 0.19e-6) {
            double e = 20 * log10(M.is[k] / ts);
            if (fabs(e) > fabs(w)) w = e;
        }
        if (tp >= 0.19e-6) {
            double e = 20 * log10(M.ip[k] / tp);
            if (fabs(e) > fabs(w)) w = e;
        }
    }
    *rmin = fmin(*rmin, fmin(M.is[M.n - 1], M.ip[k0]));
    *rmax = fmax(*rmax, fmax(M.is[M.n - 1], M.ip[k0]));
    return w;
}

static void t_bilancio(void)
{
    /* ADC on the 0.55 V reference, 10 bits: 0.537 mV per LSB at the pin.
     * EABS 3 LSB typ; EGAIN 5 LSB typ (0.49 %); the pin's leakage < 0.05 uA
     * typ through the 47k (DS40002205A Table 36-27 and the I/O table): none
     * of them has a max in the datasheet. Sensor +-3 C typ (Table 36-28).
     * The core reads each sense pin's zero while its string idles, so the
     * offset and the leakage cancel; the sensor's error does not. */
    const float lsb = 0.55f / 1024.0f;
    const float off_typ = 3 * lsb, leak = 0.05e-6f * 47e3f;
    const float gain = 5.0f / 1024.0f;
    struct { const char *nome; float off; } angoli[] = {
        {"tipico (EABS 3 LSB)", off_typ},
        {"EABS 3 LSB + perdita del pin 50 nA su 47k", off_typ + leak}};
    for (size_t a = 0; a < 2; a++) {
        double peggiore = 0, rmin = 1, rmax = 0;
        for (int jt = 0; jt < 5; jt++)
            for (int sg = -1; sg <= 1; sg += 2)
                for (int gg = -1; gg <= 1; gg += 2)
                    for (int tt = -1; tt <= 1; tt += 2) {
                        double e = sequenza(TEMPS[jt], 3.0f * tt, sg * angoli[a].off, gg * gain,
                                            &rmin, &rmax);
                        if (fabs(e) > fabs(peggiore)) peggiore = e;
                    }
        printf("  bilancio, %s, guadagno +-5 LSB, sensore +-3 C: peggiore %+.3f dB, riposo %.2f-%.2f nA\n",
               angoli[a].nome, peggiore, rmin * 1e9, rmax * 1e9);
        CHECK(fabs(peggiore) <= 1.0 && rmin >= 5e-9 && rmax <= 20e-9,
              "%s: %+.3f dB, fuori da +-1 dB (ADR-049) o dal riposo 5-20 nA", angoli[a].nome, peggiore);
    }
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "uso: test_legge <repo>\n");
        return 2;
    }
    snprintf(repo, sizeof repo, "%s", argv[1]);
    mondo_init(&M, NULL);
    carica_cal_json();
    struct { const char *nome; void (*f)(void); } T[] = {
        {"codici", t_codici}, {"cal_l41b1", t_cal_l41b1}, {"tabella", t_tabella},
        {"bilancio", t_bilancio}};
    int fallite = 0;
    for (size_t k = 0; k < sizeof T / sizeof T[0]; k++) {
        int f0 = n_fail;
        test_corrente = T[k].nome;
        T[k].f();
        printf("%s %s\n", n_fail == f0 ? "PASSA" : "FALLISCE", T[k].nome);
        if (n_fail != f0) fallite++;
    }
    printf("== test_legge: %d controlli, %d falliti, %d test falliti\n", n_check, n_fail, fallite);
    return n_fail > 255 ? 255 : n_fail;
}
