/*
 * timer_core.h - the supply board's timer, the pure logic (L41b2; the mute
 * with the relays alone since L47c2a, ADR-062).
 *
 * Contract: firmware/preamp_timer/spec/timer_spec.md. Decisions: ADR-048
 * point 6, ADR-049, ADR-062 (the mute cuts: no fade, no LDR drive, the relays
 * straight after the switch). No registers, no globals: timer_step() takes
 * what the pins read and returns what the pins must do. The adapter
 * (main_attiny.c) calls it every millisecond, and once more with dt = 0 from
 * the pin-change interrupt on MUTE_G_IN (spec 4.5: within 1 ms).
 *
 * Safety does not depend on this code (spec sec. 1): with the micro reset,
 * stuck or tri-stated, the hardware keeps jack -> permit -> VRELAY in order.
 */
#ifndef TIMER_CORE_H
#define TIMER_CORE_H

#include <stdint.h>

/* ---- times, microseconds; each with the decision that sets it ---------- */
#define T_DEBOUNCE_US      20000u    /* spec 4.7: 20 ms stable, after the 0.1 ms RC pole */
#define T_RAIL_OK_US      100000u    /* spec 4.1 step 2: rails in regulation for 100 ms */
#define T_RAIL_TIMEOUT_US 2000000u   /* spec 4.1 step 2: no rails within 2 s -> GUASTO */
#define T_VRELAY_US        50000u    /* spec 4.1 step 4: >= 13 ms of ADR-027 plus Q505 */
#define T_RELAY_OP_US      10000u    /* spec 4.3 step 2: the G6K's operate time */
#define T_DELTA_US         20000u    /* ADR-045: PERMIT_REQ 20 ms after MUTE_REQ */
/* ADR-046: the mains relay >= 50 ms after PERMIT_CMD's release; ADR-048
 * point 5: after a fault, "the mute completed". The firmware cannot read
 * PERMIT_CMD: the hardware releases it D after PERMIT_REQ (18.8 ms nominal,
 * ~21 ms at the upper corner of C528 and R534), so from PERMIT_REQ it is
 * 50 + 21 ms, rounded up. L41b2: with 50 ms from PERMIT_REQ the circuit
 * released K501 only 33 ms after PERMIT_CMD. */
#define T_OFF_GAP_US       80000u
#define T_FAULT_GAP_US     80000u
#define T_HOLE_OK_US      500000u    /* ADR-048 point 5: rails good 500 ms after a mains hole */
#define T_CLASSIFY_US      20000u    /* L41b2: MUTE_G can fall ~1 ms before ADC_MD crosses (L41b1:
                                        jacks at +14.3 ms, the detector's 2.5 V at ~15 ms) */
#define T_FAULT_PERSIST_US  2000u    /* L41b2: a rail out for 2 ms with the mains present is a fault */

/* ---- ADC thresholds, volts at the pin (psu.py dividers, spec sec. 2) --- */
#define V_SUP_P_OK     2.55f  /* VPLUS x 10/54.2: 13.8 V, in regulation (spec 4.1) */
#define V_SUP_P_FAIL   2.49f  /* 13.5 V: the supervisor's threshold (ADR-046) */
#define V_SUP_M_OK     1.20f  /* the - rail's node: below 1.20 V = in regulation (spec 4.1) */
#define V_SUP_M_FAIL   1.25f  /* 1.25 V at -13.5 V (spec sec. 2) */
#define V_SUP_VR_OK    2.55f  /* VRELAY_REG x 10/44: 11.2 V (L41b2: hysteresis over the fail) */
#define V_SUP_VR_FAIL  2.50f  /* 11.0 V: the VRELAY supervisor (ADR-048) */
#define V_MD_ABSENT    2.50f  /* the mains detector: above = mains absent for ~15 ms */

/* ---- the pins with nothing on them (spec sec. 2) ----------------------- */
/* ADR-062 took the LDR drive off psu.py and left PA1, PA2, PA3, PA4 and PB4
 * open; PC3 was spare since L41b1. The user's choice (L47c2a): the adapter
 * writes ISC = INPUT_DISABLE in their PORTx.PINnCTRL and leaves them inputs
 * without pull-up. DS40002205A sec. 16.3.1 (p. 131): "For lowest power
 * consumption, disable the digital input buffer of unused pins"; after reset
 * the buffers are enabled, and a floating pin with its buffer on can draw
 * current as it drifts through the threshold. The core touches no register:
 * the list is here so that the host test can hold it against psu.net. */
#define TIMER_ISC_INPUT_DISABLE 0x4u  /* DS40002205A sec. 16.5.11, p. 145: ISC[2:0] */
typedef struct {
    char port;        /* 'A', 'B', 'C' */
    uint8_t bit;      /* n of Pxn */
    uint8_t pin;      /* the SOIC-20 pin, as psu.py wires it */
} timer_pin_t;
extern const timer_pin_t TIMER_PIN_LIBERI[];
extern const unsigned TIMER_N_PIN_LIBERI;
extern const uint8_t TIMER_PIN_LIBERI_ISC;

typedef enum {
    ST_STANDBY = 0, ST_ACCENSIONE, ST_MUTO, ST_RILASCIO, ST_MUSICA,
    ST_INSERZIONE, ST_SPEGNIMENTO, ST_BUCO_RETE, ST_GUASTO
} timer_stato_t;

/* What the pins read. The adapter converts ADC counts to volts. */
typedef struct {
    uint8_t front_in;    /* PC0 level: 0 = on (the switch pulls to RET) */
    uint8_t mute_sw_in;  /* PC1 level: 1 = mute (also a broken wire) */
    uint8_t mute_g_in;   /* PC2 level: 0 = the hardware imposes the mute */
    float v_sup_p, v_sup_m, v_sup_vr, v_md;   /* PA5, PA6, PA7, PB5 */
} timer_in_t;

typedef struct {
    uint8_t mains_req, vrelay_en, mute_req, permit_req;
    uint8_t stato;
    uint8_t power_down;      /* 1: the adapter may sleep until FRONT_IN moves */
} timer_out_t;

typedef struct {
    uint8_t level, cand;
    uint32_t t;
} timer_deb_t;

typedef struct {
    timer_stato_t stato;
    uint8_t fase;          /* the step inside the state */
    uint32_t t_fase;       /* us in this step, saturating */
    timer_deb_t front, sw; /* debounced: front.level 0 = on; sw.level 1 = mute */
    uint8_t mute_req, permit_req, mains_req, vrelay_en;
    uint32_t t_alim_ok;    /* us of rails and VRELAY_REG in regulation, mains present,
                              counted from the first good sample (L41b2: counting the
                              tick that found them good gave 99.7 ms on the circuit) */
    uint8_t alim_prev;     /* the last sample was good */
    uint32_t t_fault;      /* us of a rail out with the mains present */
    uint8_t rail_dipped;   /* BUCO_RETE: a rail went below |13.5 V| */
    uint8_t mains_absent;  /* BUCO_RETE: the detector saw the mains go */
    uint32_t t_permit_low; /* us since PERMIT_REQ went low, saturating */
} timer_state_t;

void timer_init(timer_state_t *st, const timer_in_t *in);
timer_out_t timer_step(timer_state_t *st, const timer_in_t *in, uint32_t dt_us);
const char *timer_stato_nome(uint8_t stato);

#endif
