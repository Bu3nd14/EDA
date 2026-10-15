/*
 * mondo.h - the host tests' world: scripted pins and a recorder of the
 * core's outputs (L41b2; without the LDR strings' plant since L47c2a).
 */
#ifndef MONDO_H
#define MONDO_H

#include <stdio.h>
#include <stdint.h>

#include "../src/timer_core.h"

/* ---- the checks ---------------------------------------------------------- */
extern int n_fail, n_check;
extern const char *test_corrente;
#define CHECK(cond, ...) do { n_check++; if (!(cond)) { n_fail++; \
    printf("  FALLISCE [%s] %s:%d: ", test_corrente, __FILE__, __LINE__); \
    printf(__VA_ARGS__); printf("\n"); } } while (0)

/* ---- the world ------------------------------------------------------------ */
#define MAX_TICK 40000              /* 40 s at 1 ms */

typedef struct {
    timer_state_t st;
    timer_in_t in;
    timer_out_t out;
    uint32_t t_us;                   /* now */
    uint32_t tick_us;                /* 1000: the adapter's period */
    /* the hardware's gate (psu.py): MUTE_G follows MUTE_REQ unless a
     * supervisor pulls it down (U505, U506); the pin reads it through 1 M */
    uint8_t sup_trip;
    uint8_t mute_g_manuale;          /* 1: the test drives in.mute_g_in itself */
    /* the recorder: one row per tick */
    int n;
    float t[MAX_TICK];
    uint8_t mains[MAX_TICK], vrel[MAX_TICK], mute[MAX_TICK], perm[MAX_TICK], stato[MAX_TICK];
    FILE *csv;                       /* optional: the bridge to SPICE */
} mondo_t;

/* The CSV's header: the bridge to SPICE (genera_tb_psu.py) reads it by name. */
#define MONDO_CSV_TESTA "t,mains_req,vrelay_en,mute_req,permit_req,stato\n"

/* A world with the supply healthy, the front on, the switch at music. */
void mondo_init(mondo_t *m, const char *csv_path);
/* Advance by ms milliseconds of 1 ms ticks. */
void mondo_corri(mondo_t *m, uint32_t ms);
/* One call with dt = 0, as the pin-change interrupt makes it. */
void mondo_isr(mondo_t *m);
void mondo_chiudi(mondo_t *m);

/* Pins in one go. */
void rete_sana(timer_in_t *in);
void rete_assente(timer_in_t *in);   /* the detector above 2.5 V, rails still up */
void rail_giu(timer_in_t *in);       /* rails below |13.5 V| */

/* From a power-up to MUSICA (or MUTO), returns the time it reached it. */
float porta_a(mondo_t *m, timer_stato_t s);

/* Recorder queries. Times in seconds; -1 if never. */
float primo_fronte(const mondo_t *m, const uint8_t *sig, uint8_t v, float dopo);
float primo_stato(const mondo_t *m, timer_stato_t s, float dopo);
int idx_a(const mondo_t *m, float t);

#endif
