# Dati di L12 — margine di fase (2026-09-14)

Lotto **L12**, report `reports/2026-09-14-L12-margine-di-fase.md`. Decisioni
**ADR-024** (dove si applica la sonda) e **ADR-025** (C_f da 22 a 330 pF).

Tutti i deck girano con `scripts/run_simulation.sh`, ngspice rc 0, nessuna riga
`Error:` nei log. Modelli: segnaposto più LS352 e LSK489 vendor, come i deck
di L17.

## `prima/` — il circuito di L17 (C137 = 22 pF)

- `tb_loop/`: `tb_loop.cir` esteso con la sonda sul nodo (commit intermedio di
  L12). Sorgente nulla, griglia a 8 punti. È il deck fatto fallire: con la sonda
  sul nodo mai applicata le righe `pos 2` restavano al valore a 1 fF.

## `esplorazione/` — la scelta del rimedio

Tabelle scritte da deck di **scratch**, copiati in `deck/`. Non sono deck
versionati sotto `spice/preamp/tb/`: agiscono con `alter` su C124, C137 e sulla
resistenza d'uscita.

| File | Cosa |
|---|---|
| `esplora_B_tab.csv`, `fine_B_tab.csv` | blocco B: Miller × C_f × R_iso, poi griglia fitta sui candidati |
| `esplora_B2_tab.csv`, `esplora_B3_tab.csv` | blocco B: Miller basso con C_f da 47 a 330 pF e R_iso da 47 a 82 Ω |
| `esplora_A_tab.csv`, `esplora_A3_tab.csv` | blocco A, cablaggio sul nodo |
| `esplora_F_tab.csv`, `esplora_F3_tab.csv` | buffer delle fisse, cavo al jack |
| `toll_B_tab.csv`, `toll_F_tab.csv`, `toll_A_tab.csv` | spigoli di tolleranza: C ±5 %, R ±1 % |
| `slew2_*.csv`, `slew3_*.csv` | slew rate e 20 kHz a fondo scala, +10 dB |

`genera.zsh` e `genera2.zsh` producono le copie dei deck versionati con i
candidati applicati via `alter`, usate per i costi (PSRR, rumore, V2, V3,
risposta).

## `dopo/` — il circuito di L12 (C137 = 330 pF)

Deck versionati, sul netlist rigenerato:

| Directory | Per cosa |
|---|---|
| `tb_loop/` | V1, blocco B: 0 e +10 dB, sorgente 1 mΩ / 1 k / 2,5 k, sonda al jack e sul nodo. Tabella `tb_loop_margini.csv` |
| `tb_loop_blockA/` | V1, blocco A: sorgente 1 mΩ e 430 Ω, cablaggio sul nodo |
| `tb_loop_bufferfissa/` | V1, buffer delle fisse: Singxer e Stax, sonda al jack e sul nodo, griglia fitta |
| `tb_op/` | punto di lavoro: 79 valori identici a `data/2026-09-10/tb_op-LS352.log` |
| `tb_ac/`, `tb_zout_psrr_noise/`, `tb_noise_breakdown/` | risposta, Zout, PSRR, rumore |
| `tb_v3_overload/` | V3: recupero calcolato dal CSV |
| `tb_switch_v2/` | V2: solo il log. La forma d'onda (2,9 MB) non è versionata; i picchi stanno nel log |
| `tb_blockA_carichi/`, `tb_uscite_fisse/`, `tb_mute_corto/` | non regressione di L17: classe A sui percorsi ascoltabili, P7, E4, E5 |

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
