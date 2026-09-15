# Dati di L31 — i vettori di rumore di `tb_noise_vectors.cir` (2026-09-15)

Lotto **L31**, report `reports/2026-09-15-L31-vettori-di-rumore.md`. Chiude
**NC-030**. Nessun valore del circuito è cambiato: cambiano solo la riga
`wrdata` e i commenti del deck, e il guardiano del blocco 2g.

**Ogni cifra qui è un pavimento senza rumore 1/f.**
- **Provenienza dei modelli**, letta dagli `.include` del deck:
  `spice/preamp/placeholder_devices.lib`, cioè segnaposto scritti a mano con
  `KF = 0` (LSK489X compreso), più `models/bjt_pnp/ls350.lib`, il modello LS352
  del costruttore, che però non ha 1/f.
- Nessun dispositivo simulato ha rumore 1/f (NC-004, NC-031).
- Il commento del deck che chiama vendor anche l'LSK489 è sbagliato: lo
  corregge **L33**.

Si versionano `.log` e `.csv`, come in L12 e L27. I `.txt` grezzi di `wrdata`,
i `.json` e il deck risolto no.

## `prima/` — il deck di `main`, rieseguito prima di toccarlo

- `tb_noise_vectors/tb_noise_vectors.log`: **una** riga `Error:` (riga 485,
  `Error: no such vector onoise_q123`), ngspice rc 0.
- Nessun file dati: `run_simulation.sh` avvisa `no wrdata output found` e scrive
  un JSON a **0 righe**.

## `dopo/` — il deck coi vettori rinominati

- `tb_noise_vectors/tb_noise_vectors.log`: **0** righe `Error`, ngspice rc 0.
- `tb_noise_vectors/tb_noise_vectors.csv`: **2 righe** (1000 e 1001 Hz), 20
  colonne, in V/√Hz. Le colonne pari sono la frequenza ripetuta, i dati sono
  nelle dispari.

  | Colonna | Vettore | Cosa è | 1000 Hz |
  |---|---|---|---|
  | col1 | `onoise_spectrum` | rumore totale al jack | 8,6053e-09 |
  | col3 | `inoise_spectrum` | riportato all'ingresso | 8,6174e-09 |
  | col5 | `onoise_q121b` | LS352, uscita dello specchio | 2,4335e-09 |
  | col7 | `onoise_q121a` | LS352, diodo dello specchio | 2,1173e-09 |
  | col9 | `onoise_r136` | R_f | 4,9818e-09 |
  | col11 | `onoise_r120` | degenerazione dello specchio, lato uscita | 2,7743e-09 |
  | col13 | `onoise_r119` | degenerazione dello specchio, lato diodo | 2,7712e-09 |
  | col15 | `onoise_rsrc` | sorgente, 430 Ω | 2,6660e-09 |
  | col17 | `onoise_jq110a` | LSK489, lato non invertente | 1,6377e-09 |
  | col19 | `onoise_jq110b` | LSK489, lato di retroazione | 1,6464e-09 |

  Circuito: blocco a 0 dB (contatti RG e RG10 aperti), sorgente 430 Ω,
  R_iso 47 Ω, 4,7 µF, carico 100 kΩ.

## `esplorazione/` — la mappa, il guardiano, il riscontro

| File | Cosa |
|---|---|
| `script/map_noise_names.py`, `mappa.txt` | Dai **nodi**, non dai nomi (#22): ogni dispositivo della riga `wrdata` di L4 (`dd6fd14`, include e deck esportati con `git show`) confrontato con l'elemento di oggi dello stesso tipo e con gli stessi nodi. Rifiuta su zero o più corrispondenze. Esito: **4 nomi morti** (q123, r121, jq110, jq111) e **3 vivi sbagliati** (q122 oggi è il VAS, r120 l'altra degenerazione, r138 R_g) |
| `guardiano_sul_deck_di_main.txt` | `check_deck_refs.py` esteso, sui 17 deck **prima** della correzione: rc 1, esattamente 4 MISSING, tutti in `tb_noise_vectors.cir:55` |
| `guardiano_sui_deck_pre_L27.txt` | Lo stesso sui 16 deck di `6748fbc`, con l'include di allora: l'unico rifiuto sono gli stessi 4 nomi, nessun falso allarme |
| `script/sabotaggi_guardiano.py`, `sabotaggi_guardiano.txt` | 13 mini-deck: passano sotto-sorgenti vere (`_rb`, `_1overf`, `_idsw`, `_thermal`), elementi del deck, `let`, stringhe fra virgolette, commenti, `onoise_total`; cadono suffisso falso, `inoise` morto, nome morto in `wrdata`, `onoise_uv` senza `let`, `onoise_thermal`. **13/13** |
| `guardiano_dopo_la_correzione.txt` | I 17 deck dopo la correzione: rc 0 |
| `script/riscontro.py`, `riscontro.txt` | Il riscontro dei dati: vedi sotto |
| `riscontro_sabotato.txt` | Il riscontro sul deck di `main`: deve cadere |

## Il riscontro

Tutto a 1000 Hz, da `riscontro.txt`, sempre come pavimento senza 1/f.

- I 10 valori del CSV coincidono con `print all` del log, alle 7 cifre che il
  log stampa.
- Il log ha **42 totali per dispositivo**, esattamente i 42 R/D/Q/J dell'include
  e del deck.
- **Quadratura**: √(Σ dei quadrati dei 42 totali) = **8,605323e-09** contro
  `onoise_spectrum` **8,605323e-09**, scarto relativo +5,6e-08.
- Gli **8 dispositivi scritti sono i primi 8** della classifica e portano
  l'**85,21 %** della potenza di rumore. R136 (R_f) da solo il 33,51 %; il nono
  è il VAS Q122, al 2,94 %.
- **Contro `tb_noise_breakdown`**, configurazione B di L27 (stesso circuito:
  0 dB, Rsrc 430):
  - `onoise_spectrum` scarto 0;
  - `inoise_spectrum` scarto −1,4e-08.

  Il punto più vicino di quella spazzata a 100 punti per decade è
  **1002,37 Hz**, non 1000: lo spettro lì è piatto alla settima cifra.

**Una premessa del mandato non era vera.** `tb_noise_breakdown.cir` **non**
stampa la ripartizione per dispositivo a 1 kHz. Il suo log dice solo
`No. of Data Rows : 2`, e il deck distrugge il plot con `destroy all`. Il
riscontro per dispositivo è quindi la quadratura sui totali di questo deck; il
confronto con `tb_noise_breakdown` resta sullo spettro.
