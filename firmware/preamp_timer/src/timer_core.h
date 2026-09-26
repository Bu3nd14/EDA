/*
 * timer_core.h - the supply board's timer, the pure logic (L41b2).
 *
 * Contract: firmware/preamp_timer/spec/timer_spec.md. Decisions: ADR-048
 * point 6, ADR-049, ADR-050 (the LDR top at 12 mA). No registers, no globals:
 * timer_step() takes what the pins read and returns what the pins must do.
 * The adapter (main_attiny.c) calls it every millisecond, and once more with
 * dt = 0 from the pin-change interrupt on MUTE_G_IN (spec 4.5: within 1 ms).
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
#define T_CAL_SETTLE_US   200000u    /* L41b2: 11 x C_X's 18 ms, the step settled to < 10 uV */
#define T_VRELAY_US        50000u    /* spec 4.1 step 6: >= 13 ms of ADR-027 plus Q505 */
#define T_RELAY_OP_US      10000u    /* spec 4.3 step 2: the G6K's operate time */
#define T_FADE_US         6000000u   /* ADR-039: Td = 6 s from d = 0 to d = 1 */
#define T_MUTE_HOLD_US    500000u    /* ADR-039 (J3 contract): MUTE_REQ low 0.5 s after d = 1 */
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
#define T_CAL_MUSIC_US    1000000u   /* L41b2: the series is calibrated 1 s after it reaches d = 0 */

/* ---- ADC thresholds, volts at the pin (psu.py dividers, spec sec. 2) --- */
#define V_SUP_P_OK     2.55f  /* VPLUS x 10/54.2: 13.8 V, in regulation (spec 4.1) */
#define V_SUP_P_FAIL   2.49f  /* 13.5 V: the supervisor's threshold (ADR-046) */
#define V_SUP_M_OK     1.20f  /* the - rail's node: below 1.20 V = in regulation (spec 4.1) */
#define V_SUP_M_FAIL   1.25f  /* 1.25 V at -13.5 V (spec sec. 2) */
#define V_SUP_VR_OK    2.55f  /* VRELAY_REG x 10/44: 11.2 V (L41b2: hysteresis over the fail) */
#define V_SUP_VR_FAIL  2.50f  /* 11.0 V: the VRELAY supervisor (ADR-048) */
#define V_MD_ABSENT    2.50f  /* the mains detector: above = mains absent for ~15 ms */

/* ---- the LDR law (spec sec. 5; psu.py's network) ------------------------ */
#define LDR_I_TOP      12e-3f   /* ADR-050 (NC-038): the VTL5C4 LED holds 13 mA at 60 C */
#define LDR_I_IDLE     10e-9f   /* ADR-039: 10 nA of idle, never 0 */
#define LDR_I_CAL_LO    2e-3f   /* ADR-049: the calibration's second point, 20 mV on 10 ohm */
#define LAW_VREF        2.5f    /* LM4040-2.5 */
#define LAW_V5          5.0f
#define LAW_R_REF       24.9e3f /* I_ref = (V5 - VREF) / R_REF = 100 uA */
#define LAW_R_A         100e3f
#define LAW_R_C         22.1e3f
#define LAW_DAC_FS      4.096f  /* MCP4822, G = 2x */
#define CAL_E_MAX       0.030f  /* L41b2: a fit needing > 30 mV is a broken string, not a correction */

typedef enum {
    ST_STANDBY = 0, ST_ACCENSIONE, ST_MUTO, ST_RILASCIO, ST_MUSICA,
    ST_INSERZIONE, ST_SPEGNIMENTO, ST_BUCO_RETE, ST_GUASTO
} timer_stato_t;

/* What the pins read. The adapter converts ADC counts to volts / amperes
 * and the temperature sensor to degrees C. */
typedef struct {
    uint8_t front_in;    /* PC0 level: 0 = on (the switch pulls to RET) */
    uint8_t mute_sw_in;  /* PC1 level: 1 = mute (also a broken wire) */
    uint8_t mute_g_in;   /* PC2 level: 0 = the hardware imposes the mute */
    float v_sup_p, v_sup_m, v_sup_vr, v_md;   /* PA5, PA6, PA7, PB5 */
    float i_s, i_p;      /* string currents: ADC_I_S / 10 ohm, ADC_I_P / 10 ohm */
    float t_c;           /* the micro's temperature sensor */
} timer_in_t;

typedef struct {
    uint8_t mains_req, vrelay_en, mute_req, permit_req;
    uint8_t dac_on;          /* 0: the MCP4822 shut down (both channels) */
    uint16_t code_s, code_p; /* VA = series, VB = shunt */
    uint8_t stato;
    uint8_t power_down;      /* 1: the adapter may sleep until FRONT_IN moves */
} timer_out_t;

typedef struct { float off, r_ohm; } timer_cal_t;

typedef struct {
    uint8_t level, cand;
    uint32_t t;
} timer_deb_t;

typedef struct {
    timer_stato_t stato;
    uint8_t fase;          /* the step inside the state */
    uint32_t t_fase;       /* us in this step, saturating */
    float d;               /* the mute depth, 0 = music, 1 = full mute */
    timer_deb_t front, sw; /* debounced: front.level 0 = on; sw.level 1 = mute */
    uint8_t front_seen_off;/* GUASTO: the front has gone off since */
    uint8_t mute_req, permit_req, mains_req, vrelay_en, dac_on;
    uint32_t t_alim_ok;    /* us of rails and VRELAY_REG in regulation, mains present,
                              counted from the first good sample (L41b2: counting the
                              tick that found them good gave 99.7 ms on the circuit) */
    uint8_t alim_prev;     /* the last sample was good */
    uint32_t t_fault;      /* us of a rail out with the mains present */
    uint8_t rail_dipped;   /* BUCO_RETE: a rail went below |13.5 V| */
    uint8_t mains_absent;  /* BUCO_RETE: the detector saw the mains go */
    timer_cal_t cal_s, cal_p;
    uint8_t cal_active;    /* 0 none, 1 series, 2 shunt */
    float cal_i;           /* the current the calibration commands */
    float cal_top_read;
    uint8_t cal_ok_s, cal_ok_p;
    uint32_t n_cal_reject; /* calibrations refused (CAL_E_MAX) */
    uint32_t t_permit_low; /* us since PERMIT_REQ went low, saturating */
    /* the sense pins' zero, read while their string idles at 10 nA (0.1 uV on
     * 10 ohm): the ADC's offset and the pin's leakage through 47k, which
     * otherwise cost up to 2 dB of the profile (L41b2, test_legge bilancio) */
    float zero_s, zero_p;
    uint8_t cal_done_here; /* the string at its top calibrated in this stay */
} timer_state_t;

void timer_init(timer_state_t *st, const timer_in_t *in);
timer_out_t timer_step(timer_state_t *st, const timer_in_t *in, uint32_t dt_us);

/* The pieces, exposed for the host tests. */
float timer_law_vx(float i, float t_c, const timer_cal_t *cal);
uint16_t timer_law_code(float i, float t_c, const timer_cal_t *cal);
float timer_profile_series(float d);
float timer_profile_shunt(float d);
/* Two-point fit (ADR-049): e_k = Vt ln(I_want_k / I_read_k) = off + r_ohm x_k,
 * added to cal. The core passes x_k = I_read_k: the ohmic drop happens at the
 * current that flows (L41b2). L41b1's analizza_ldr.py used x_k = I_want_k,
 * which a linear plant shows biased (-0.38 dB at the top, test_sequenze).
 * Returns 0 and leaves cal alone if a point needs > CAL_E_MAX. */
int timer_cal_fit_x(timer_cal_t *cal, float t_c,
                    float want1, float read1, float x1,
                    float want2, float read2, float x2);
int timer_cal_fit(timer_cal_t *cal, float t_c, float i_top_want, float i_top_read,
                  float i_lo_want, float i_lo_read);
const char *timer_stato_nome(uint8_t stato);

#endif
