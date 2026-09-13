# Dati del 2026-09-13 — due deck riparati

Prodotti dal lotto **L10**. Report: `../../reports/2026-09-13-L10-simbolo-lsk489.md`.

**Cosa descrivono.** Due deck che lo scarto di −1 di L22 aveva rotto **in
silenzio** (ngspice esce 0 in entrambi i casi), rieseguiti prima e dopo la
correzione, sulla topologia di L10: LSK489 fuso in una Part, specchio LS352 a
220 Ω, ogni altro dispositivo ancora segnaposto
(`spice/preamp/placeholder_devices.lib`). La fusione non cambia la topologia:
`tb_op.cir` dà 81 valori su 81 identici prima e dopo.

I file `-BASELINE-` sono **la prova del guasto**, non dati da usare.

## I file

| File | Cosa |
|---|---|
| `tb_switch_v2_counterfactual-BASELINE-r138-assente.log` | prima della correzione: `Error: no such device or model name r138` due volte, e lo stato B identico allo stato A |
| `tb_switch_v2_counterfactual.log` | dopo: R_f è `r136` |
| `tb_switch_v2_counterfactual.csv` | stato A, contatto chiuso |
| `tb_switch_v2_counterfactual_open.csv` | stato B, R_f aperta: v(OUT) **−13,773 V** |
| `tb_switch_v2_counterfactual_reclosed.csv` | stato C, richiuso |
| `tb_bias_sweep-BASELINE-ramo-sbagliato.log` | prima: `r130` era il ramo NBB-NY da 1,00 k, I_q 5,207 mA a 1690 Ω |
| `tb_bias_sweep.log` | dopo: `r128`, il ramo NX-NBB da 1,69 k, I_q **14,714 mA** a 1690 Ω |

**Colonne dei CSV del controfattuale** (dal commento nel deck): i dati sono le
colonne dispari — col1 = v(OUT), col3 = v(FB), col5 = v(NX), col7 = v(NY).

**Nei log dello sweep dopo la correzione** l'`echo` dice `R128 = … ohm` e la
corrente è `@r134[i]`; nella baseline dice `R130` e `@r135[i]`, cioè i nomi di
allora.

I dati in `../2026-09-09/` (controfattuale: −13,677 V) descrivono la topologia
col THAT320, prima di L22, e restano validi come ciò che erano.
