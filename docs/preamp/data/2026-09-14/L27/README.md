# Dati di L27 — il terzo livello di guadagno (2026-09-14)

Lotto **L27**, report `reports/2026-09-14-L27-terzo-livello-di-guadagno.md`.
Decisione **ADR-026**: due rami di R_g in parallelo, 3,57 kΩ su K1 e 866 Ω su K5.

Tutti i deck girano con `scripts/run_simulation.sh`, ngspice rc 0. Modelli:
segnaposto più LS352 e LSK489 vendor, come i deck di L12. Nei log non ci sono
righe `Error`, tranne `tb_noise_vectors` (vedi sotto e NC-030).

Come L12, si versionano i `.csv` e i `.log`. I `.txt` grezzi di `wrdata`, i
`.json` e i deck risolti no. La forma d'onda di `tb_switch_v2` (22 MB) non è
versionata: le finestre stanno in `tb_switch_v2_finestre.csv` e gli estremi nel
log.

## `prima/` — il circuito di L12 (R_g 698 Ω, un relè)

- `tb_loop/`: `tb_loop.cir` di `main` rieseguito prima di toccare il circuito. La
  tabella è **byte-identica** a `L12/dopo/tb_loop/tb_loop_margini.csv`: 61,2055° a
  0 dB e 102,959° a +10 dB.

## `dopo/` — il circuito di L27

| Directory | Per cosa |
|---|---|
| `tb_loop/` | **V1**, blocco B a 0 / +3 / +10 dB, carico 100 k e 10 k, sorgente 1 mΩ / 1 k / 2,5 k, sonda al jack e sul nodo. Tabella `tb_loop_margini.csv`, 396 righe; la colonna `rload` sta in coda |
| `tb_ac/`, `tb_zout_psrr_noise/`, `tb_noise_breakdown/`, `tb_dc_headroom/` | risposta, E4, PSRR, E5 e dinamica nei tre modi |
| `tb_switch_v2/` | **V2** con due relè che rimbalzano: `tb_switch_v2_finestre.csv` e il log |
| `tb_switch_v2_counterfactual/` | il controfattuale di ADR-004, rieseguito: anello aperto a −13,773 V |
| `tb_mute_corto/` | **P7** e classe A anche a +3 dB (sweep 1c e transitorio a tre modi). 600 righe |
| `tb_op/`, `tb_v3_overload/`, `tb_blockA_carichi/`, `tb_loop_blockA/`, `tb_loop_bufferfissa/`, `tb_uscite_fisse/`, `tb_bias_sweep/` | non regressione: le istanze senza relè hanno ora due nodi di contatto aperti invece di uno |
| `tb_noise_vectors/` | **solo il log.** Il deck cita vettori di rumore di dispositivi che non esistono più (`onoise_q123`, `onoise_r121`, `onoise_jq110`, `onoise_jq111`), il `wrdata` si ferma e nessun dato viene scritto. È preesistente a L27 → **NC-030** |

## `esplorazione/` — deck di scratch e script d'analisi

Non sono deck versionati sotto `spice/preamp/tb/`.

| File | Cosa |
|---|---|
| `deck/tb_loop_fine.cir`, `fine_margini.csv` | griglia fitta da 1,8 a 4,2 nF, passo 0,1 nF, a 0 e +3 dB, sorgente 2,5 k. Minimi: 61,8289° (0 dB, 3,3 nF) e **69,7905°** (+3 dB, 2,8 nF) |
| `deck/toll_L27.cir`, `toll_L27_tab.csv` | spigoli di L12 (C124 e C137 ±5 %, R_iso ±1 %) a 0 e +3 dB. Minimi: **61,449°** e **68,671°** |
| `script/netcmp.py` | confronto semantico di due netlist KiCad: componenti per riferimento e connettività come **partizione** di nodi, mai per nome di net (#23) |
| `script/v1.py` | minimi di `tb_loop_margini.csv` per modo, carico e posizione della sonda |
| `script/cmp.py` | ogni `.csv` di L27 contro quello omonimo di L12: scarto relativo massimo |
| `script/mute.py` | classe A riga per riga contro L12, P7 per blocco e modo, percorsi ascoltabili |
| `script/toll.py`, `script/v3.py` | minimo agli spigoli; forme d'onda di V3 contro L12 |

## Nota di L33 (2026-09-15) — la provenienza dell'LSK489

Il testo sopra resta com'era: è l'output di un'esecuzione datata. **Una sua frase non è vera**: «Modelli: segnaposto più LS352 e LSK489 vendor».

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
