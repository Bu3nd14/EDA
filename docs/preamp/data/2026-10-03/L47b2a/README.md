# L47b2a — la NSL-32SR3 nel sorgente e nei banchi, la cima del LED a 7 mA (2026-10-03)

Report: `../../../reports/2026-10-03-L47b2a-cella-nel-sorgente.md`. Decisione: **ADR-060**.
**Cifre di modello** (`models/optocoupler/nsl32sr3_comportamentale.lib`: «modello comportamentale
da dati pubblicati, una sola cella misurata nella regione del mute»): conta il trend.

| Percorso | Cosa |
|---|---|
| `falsi/parte_vecchia_vtl5c.net` | la netlist di `main` prima del lotto (VTL5C), byte per byte (blob `836d4e79`) |
| `falsi/led_capovolti.net` | il sorgente con la sola `Part` cambiata e i LED ancora cablati per numero: i quattro LED rovesciati, connettività identica |
| `falsi/un_led_rovesciato.net` | la netlist buona con i piedini 1 e 2 di U301 scambiati (`script/rovescia_un_led.py`) |
| `script/piedini_celle.py` | stampa parte e rete di ogni piedino di U101/U301/U102/U302, con A/K secondo il simbolo |
| `cella/r_cella.cir` | R della cella per curva e corrente (7, 12, 20 mA; 4,5 µA; 10 nA), un op |
| `e3_e5/` | `tb_e3_e5_ldr.cir` sulla NSL-32SR3 a 7 mA, con `run_simulation.sh` |
| `script/e5_max.py` | E5 massimo per caso della cella, su uno o più CSV |
| `regressione/dopo/` | i 21 deck veloci (`script/regressione.sh`, copiato da L44); `regressione/confronto.csv` contro `../../2026-10-01/L44/regressione/dopo/` (`script/confronta_regressione.py`) |
| `v2_prova/` | `tb_v2_casopeggiore.cir` risolto (`script/risolvi_repo.py`) e diviso (`dividi.py` di L29b2); corse `g0sempre_1k_iii` e `mev_1k_iii` con log e `.dat`. **Prova di corsa, non verdetto**: profilo v4 e cima 20 mA della VTL5C4 |

I `corsa_*.cir` e i `.dat` di `v2_prova/` sono in `.gitignore` (~1,1 GB per corsa); si rigenerano.

## La matrice dei falsi

| Netlist | `check_relay_safe_state.py` (2e) | `check_psu_harness.py` (2j) |
|---|---|---|
| `circuits/preamp/preamp_audio.net` (buona) | OK | OK |
| `falsi/parte_vecchia_vtl5c.net` | FALLITO: nessuna LDR (Isolator:NSL-32) | FAIL ×4: `U101 is 'VTL5C'`… |
| `falsi/led_capovolti.net` | OK (la serie è coerente: la polarità a J3 è del 2j) | FAIL ×4: `J3 pin 1 does not reach the LED anode of U101`… |
| `falsi/un_led_rovesciato.net` | FALLITO ×2: `LDR_S_MID unisce K e K` | FAIL: `J3 pin 2 does not reach the LED cathode of U301` |

**Prima della correzione**, `check_psu_harness.py` su `led_capovolti.net` diceva «OK: … J3 LDR_CMD
… agree pin by pin»: il difetto era silenzioso (limitations #41). Il 2e col `KNOWN_LDR` vecchio
falliva «nessuna LDR del mute graduale (Isolator:VTL5C)»: chiuso, ma per la ragione sbagliata.

## Per rieseguire (dalla radice del repo; percorsi assoluti nel worktree)

```
/Users/roberto/EDA/env/venv/bin/python3 circuits/preamp/preamp_audio.py
/usr/bin/python3 docs/preamp/data/2026-10-03/L47b2a/script/piedini_celle.py circuits/preamp/preamp_audio.net docs/preamp/data/2026-10-03/L47b2a/falsi/*.net
/usr/bin/python3 scripts/check_relay_safe_state.py <netlist>
/usr/bin/python3 scripts/check_psu_harness.py <netlist> circuits/preamp/psu.net
/opt/homebrew/bin/ngspice -b docs/preamp/data/2026-10-03/L47b2a/cella/r_cella.cir
/bin/zsh scripts/run_simulation.sh spice/preamp/tb/tb_e3_e5_ldr.cir docs/preamp/data/2026-10-03/L47b2a/e3_e5
/usr/bin/python3 docs/preamp/data/2026-10-03/L47b2a/script/e5_max.py <e5.csv>...
/bin/zsh docs/preamp/data/2026-10-03/L47b2a/script/regressione.sh dopo
/usr/bin/python3 docs/preamp/data/2026-10-03/L47b2a/script/confronta_regressione.py
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py
/usr/bin/python3 docs/preamp/data/2026-09-22/L29b2/deck/genera_tb_v2_mute_ldr.py
/usr/bin/python3 docs/preamp/data/2026-10-03/L47b2a/script/risolvi_repo.py spice/preamp/tb/tb_v2_casopeggiore.cir docs/preamp/data/2026-10-03/L47b2a/v2_prova/v2.cir
/usr/bin/python3 docs/preamp/data/2026-09-22/L29b2/pavimento/dividi.py docs/preamp/data/2026-10-03/L47b2a/v2_prova/v2.cir
/opt/homebrew/bin/ngspice -b docs/preamp/data/2026-10-03/L47b2a/v2_prova/corsa_<nome>.cir -o docs/preamp/data/2026-10-03/L47b2a/v2_prova/corsa_<nome>.log
```

Le corse V2 scrivono i `.dat` nella cartella da cui si lanciano: vanno spostati in `v2_prova/`.
