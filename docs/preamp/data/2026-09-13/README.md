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

---

# L18 — il PSRR sulla topologia LS352

Prodotti dal lotto **L18**. Decisione: **ADR-020**. Report:
`../../reports/2026-09-13-L18-vincolo-psrr.md`.

**Cosa descrivono.** `spice/preamp/tb/tb_zout_psrr_noise.cir` rieseguito sul
codice del 2026-09-13:
- LSK489 fuso in una Part;
- specchio LS352 a 220 Ω;
- ogni altro dispositivo ancora segnaposto (**NC-017**).

Che il deck abbia letto **questa** topologia lo prova la riga WORST CASE del
log: **4,230582 µV**, cioè la cifra LS352 di `../2026-09-10/`, non i 5,697 µV
del THAT320.

| File | Cosa |
|---|---|
| `tb_zout_psrr_noise-LS352.log` | log completo: Zout, PSRR, rumore |
| `tb_zout_psrr_noise_psrrp_0db.csv`, `_psrrp_10db.csv` | PSRR dal rail + |
| `tb_zout_psrr_noise_psrrm_0db.csv`, `_psrrm_10db.csv` | PSRR dal rail − |

**Colonne.** `col0` = f [Hz], `col1` = PSRR [dB] (più grande è meglio).
81 righe, 20 Hz–200 kHz, 20 punti per decade. Misura: 1 V AC in serie al
rail, sorgente d'ingresso silenziata, 100 kΩ al jack. Gli spettri di Zout e di
rumore non sono versionati qui: le loro cifre stanno nel log.

**Scarto rispetto a `../2026-09-09/`** (THAT320, fra parentesi), dalle `meas`
dei due log, in dB:

| Configurazione | 100 Hz | 1 kHz | 10 kHz | 100 kHz |
|---|---|---|---|---|
| rail +, +10 dB | 62,17 (62,07) | 49,62 (49,56) | **29,82** (29,76) | 10,20 (10,15) |
| rail +, 0 dB | 72,12 (72,02) | 59,57 (59,51) | 39,78 (39,72) | 19,78 (19,72) |
| rail −, +10 dB | **74,37** (79,02) | 87,75 (90,54) | 86,23 (86,93) | 61,56 (61,44) |
| rail −, 0 dB | 84,33 (88,97) | 97,71 (100,50) | 96,21 (96,91) | 71,15 (71,02) |

**Sugli 81 punti:**
- **rail +**: si muove al più di **0,107 dB**, in meglio;
- **rail −**: perde fino a **4,74 dB** a 20 Hz (media −2,26 dB);
- **Zout**: si muove di meno dello 0,6%.

La modalità +10 dB è la peggiore su tutti gli 81 punti di entrambi i rail.

## Nota di L33 (2026-09-15) — la provenienza dell'LSK489

Il testo sopra resta com'era: è l'output di un'esecuzione datata. **Una sua frase non è vera**: «LSK489 fuso in una Part, specchio LS352 a 220 Ω, ogni altro dispositivo ancora segnaposto», che si legge come se l'LSK489 non fosse un segnaposto. Lo è.

- L'LSK489 simulato è **`LSK489X`**, il segnaposto scritto a mano di
  `spice/preamp/placeholder_devices.lib`, con `KF = 0`. Il modello del
  costruttore, `models/jfet/lsk489.lib` (`LSK489A`), non l'ha mai incluso
  nessun deck, né oggi né alla data di questi dati:
  `git log -S "jfet/lsk489.lib" -- spice circuits` è vuoto.
- L'unico modello del costruttore simulato è l'**LS352**
  (`models/bjt_pnp/ls350.lib`), che non ha `KF`. Quindi **nessun dispositivo
  simulato ha rumore 1/f**.
- **Nessun numero cambia**, cambia cosa se ne crede: ogni cifra di rumore qui è
  un pavimento senza flicker, JFET compresi (NC-004, NC-031).
