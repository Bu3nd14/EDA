/* mondo.c - see mondo.h (L41b2). */
#include "mondo.h"

#include <math.h>
#include <string.h>

int n_fail, n_check;
const char *test_corrente = "";

void rete_sana(timer_in_t *in)
{
    in->v_sup_p = 15.0f * 10.0f / 54.2f;   /* 2.77 V */
    in->v_sup_m = 1.13f;                   /* -15 V (spec sec. 2) */
    in->v_sup_vr = 12.0f * 10.0f / 44.0f;  /* 2.73 V */
    in->v_md = 0.5f;
    in->mute_g_in = 1;
}

void rete_assente(timer_in_t *in)
{
    in->v_md = 3.5f;
}

void rail_giu(timer_in_t *in)
{
    in->v_sup_p = 12.0f * 10.0f / 54.2f;   /* 12 V: below 13.5 */
    in->v_sup_m = 1.40f;
}

/* The string's true current for a DAC code: the network inverted to V_X,
 * then I = I_ref exp((V_X - VREF - off - r I) / Vt), solved by Newton in
 * ln I. With the DAC shut down the hardware gives 2-9 nA (L41b1): 5 nA. */
float corrente_vera(const mondo_t *m, uint16_t code, uint8_t on, float off, float r)
{
    if (!on)
        return 5e-9f;
    const double ga = 1.0 / LAW_R_A, gc = 1.0 / LAW_R_C;
    double vdac = code * (double)LAW_DAC_FS / 4096.0;
    double vx = (vdac * ga + LAW_VREF * gc) / (ga + gc);
    double vt = 1.380649e-23 * (m->t_true + 273.15) / 1.602176634e-19;
    double iref = (LAW_V5 - LAW_VREF) / LAW_R_REF;
    double y = log(1e-3);                  /* ln I */
    for (int k = 0; k < 60; k++) {
        double i = exp(y);
        double f = vt * (y - log(iref)) + off + r * i - (vx - LAW_VREF);
        double fp = vt + r * i;
        y -= f / fp;
    }
    return (float)exp(y);
}

static void registra(mondo_t *m)
{
    if (m->n >= MAX_TICK)
        return;
    int k = m->n++;
    m->t[k] = m->t_us * 1e-6f;
    m->d[k] = m->st.d;
    m->mains[k] = m->out.mains_req;
    m->vrel[k] = m->out.vrelay_en;
    m->mute[k] = m->out.mute_req;
    m->perm[k] = m->out.permit_req;
    m->dac[k] = m->out.dac_on;
    m->stato[k] = m->out.stato;
    m->cs[k] = m->out.code_s;
    m->cp[k] = m->out.code_p;
    m->is[k] = corrente_vera(m, m->out.code_s, m->out.dac_on, m->off_s, m->r_s);
    m->ip[k] = corrente_vera(m, m->out.code_p, m->out.dac_on, m->off_p, m->r_p);
    if (m->csv && (k == 0 || m->mains[k] != m->mains[k - 1] || m->vrel[k] != m->vrel[k - 1] ||
                   m->mute[k] != m->mute[k - 1] || m->perm[k] != m->perm[k - 1] ||
                   m->dac[k] != m->dac[k - 1] || m->cs[k] != m->cs[k - 1] ||
                   m->cp[k] != m->cp[k - 1] || m->stato[k] != m->stato[k - 1]))
        fprintf(m->csv, "%.6f,%d,%d,%d,%d,%d,%d,%d,%s,%.6f\n", m->t_us * 1e-6, m->out.mains_req,
                m->out.vrelay_en, m->out.mute_req, m->out.permit_req, m->out.dac_on,
                m->out.code_s, m->out.code_p, timer_stato_nome(m->out.stato), m->st.d);
}

static void passo(mondo_t *m, uint32_t dt)
{
    /* the ADC reads the currents the last command produced, 10 ohm sense */
    float is = corrente_vera(m, m->out.code_s, m->out.dac_on, m->off_s, m->r_s);
    float ip = corrente_vera(m, m->out.code_p, m->out.dac_on, m->off_p, m->r_p);
    m->in.i_s = ((is * 10.0f) * (1.0f + m->adc_gain) + m->adc_off_v) / 10.0f;
    m->in.i_p = ((ip * 10.0f) * (1.0f + m->adc_gain) + m->adc_off_v) / 10.0f;
    if (!m->mute_g_manuale)
        m->in.mute_g_in = (uint8_t)(m->out.mute_req && !m->sup_trip);
    m->out = timer_step(&m->st, &m->in, dt);
}

void mondo_init(mondo_t *m, const char *csv_path)
{
    memset(m, 0, sizeof *m);
    m->tick_us = 1000;
    m->off_s = m->off_p = 4.5e-3f;     /* the op-amp's max offset (MCP6004) */
    m->r_s = m->r_p = 0.43f;           /* L41b1's bench */
    m->t_true = 25.0f;
    m->in.t_c = 25.0f;
    m->in.front_in = 0;                /* on */
    m->in.mute_sw_in = 0;              /* music */
    rete_sana(&m->in);
    timer_init(&m->st, &m->in);
    m->out = timer_step(&m->st, &m->in, 0);
    if (csv_path) {
        m->csv = fopen(csv_path, "w");
        if (m->csv)
            fprintf(m->csv, "t,mains_req,vrelay_en,mute_req,permit_req,dac_on,code_s,code_p,stato,d\n");
    }
    registra(m);
}

void mondo_corri(mondo_t *m, uint32_t ms)
{
    for (uint32_t k = 0; k < ms * 1000u / m->tick_us; k++) {
        m->t_us += m->tick_us;
        passo(m, m->tick_us);
        registra(m);
    }
}

void mondo_isr(mondo_t *m)
{
    passo(m, 0);
    registra(m);
}

void mondo_chiudi(mondo_t *m)
{
    if (m->csv)
        fclose(m->csv);
    m->csv = NULL;
}

float porta_a(mondo_t *m, timer_stato_t s)
{
    for (int k = 0; k < 20000; k++) {
        if (m->out.stato == (uint8_t)s)
            return m->t_us * 1e-6f;
        mondo_corri(m, 1);
    }
    return -1.0f;
}

float primo_fronte(const mondo_t *m, const uint8_t *sig, uint8_t v, float dopo)
{
    for (int k = 1; k < m->n; k++)
        if (m->t[k] >= dopo && sig[k] == v && sig[k - 1] != v)
            return m->t[k];
    return -1.0f;
}

float primo_stato(const mondo_t *m, timer_stato_t s, float dopo)
{
    for (int k = 0; k < m->n; k++)
        if (m->t[k] >= dopo && m->stato[k] == (uint8_t)s)
            return m->t[k];
    return -1.0f;
}

int idx_a(const mondo_t *m, float t)
{
    for (int k = 0; k < m->n; k++)
        if (m->t[k] >= t - 1e-7f)
            return k;
    return m->n - 1;
}
