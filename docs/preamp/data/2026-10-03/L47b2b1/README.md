# L47b2b1 — il profilo del mute a 3 s con la cima di 7 mA, la scelta del pilota, l'impronta (2026-10-03)

Report: `../../../reports/2026-10-03-L47b2b1-profilo-v5.md`. Decisione: **ADR-061**.
**Cifre di modello** (`models/optocoupler/nsl32sr3_comportamentale.lib`: «modello comportamentale
da dati pubblicati, una sola cella misurata nella regione del mute»): conta il trend. La
distorsione della NSL-32SR3 **non è modellata**.

L47b2b è stato diviso dall'utente all'inizio: **L47b2b1** (questo) il profilo, le misure sul
preamp intero con un pilota ideale, la scelta del pilota, l'impronta; **L47b2b2** il pilota vero
in `psu.py`, il firmware, `VRELAY`, le catene a valle.

| Percorso | Cosa |
|---|---|
| `banco/rapido.py` | il banco ridotto di L47b1 in Python (modello della cella letto dal `.lib`, S come `v2_metodo`, E3 stimata a 20 Hz e 20 kHz, il carico della cella di L29b). Verificato contro ngspice: S entro 0,03 dB (L47b1 a 12 mA e v4 a 7 mA), E3 entro 0,1 kΩ |
| `banco/sfumatura.py` | la `tran` vera sul banco ridotto (comune.py e la guardia di L47b1 importati), per `v4`, `v5` e profili per verso (`asim:`) |
| `banco/ottimizza.py`, `banco/famiglia.py`, `banco/fronte.py`, `banco/asimmetrico.py`, `banco/componi.py`, `banco/durata_e3.py`, `banco/traccia.py` | la ricerca del profilo: discesa per coordinate (abbandonata: E3 vuole mosse coordinate), la famiglia a quattro parametri sulla griglia (3, 4, 5 s), il compromesso S–E3, l'accoppiata per verso |
| `banco/pilota_semplice.py`, `banco/cerca_pilota.py`, `banco/prova_p2.py` | NC-045: i due piloti semplificati (P1 RC + generatore lineare; P2 RC + un NPN con RE), ricerca dei parametri e angoli |
| `banco/tabelle/` | i risultati: `famiglia*.csv`, `asimmetrico*.json`, `candidati.json`, `pilota_p*.json`, `sfumatura_*.csv` |
| `e3/` | E3 lungo la sfumatura: `genera_e3_sequenza.py` (gli istanti peggiori della `tran` del v5 nell'AC del deck E3), `riassunto_e3.py`, `e3_sequenza.csv` |
| `impronta/genera_impronta.py` | l'impronta `library/preamp.pretty/NSL-32SR3_LED3.30.kicad_mod`, da `OptoDevice:Luna_NSL-32` |
| `banco/b2_rele.py` | NC-053: il residuo a 20 Hz all'istante del relè, il rapporto con B2 (0,070–0,072) e B2 previsto per ritardi del relè da 0,5 a 3 s |
| `v2/sorgente/` | la matrice del deck versionato `tb_v2_casopeggiore.cir` (135 corse, curve B/B), col banco di prima; `manifest_v.csv` senza le 24 `off_` (come L29d2), `analisi.csv`, `verdetto.csv` |
| `v2/deck/`, `v2/curve_XX/`, `v2/corri_curve.sh` | la matrice «curve» per A, C, D, E (18 corse ciascuna), `verdetto.csv` per curva |
| `v2/sonda_20hz/` | il collasso del passo a 20 Hz con le curve C ed E: `varianti.py`, `corri_sonda.sh`, `esito.txt` (e `rele/`, `rele2/`); `confronta.py` (#38); `aggiungi_trtol.py`, `aggiungi_rshunt.py`, `rifai_20hz.sh`, `rifai_20hz_e.sh` |
| `v2/cf_offset/` | il controfattuale del click con la dispersione (`genera_cf.py`: IOSA = VOSA / 1 MΩ), 11 corse `dpamax`, `verdetto.csv` (0 su 23) |
| `v2/sorgente_iosa/` | le altre 22 corse di dispersione sul deck versionato corretto (`iosa()` nel generatore), `verdetto.csv` (0 su 46) |
| `script/guardia_v2.py` | le guardie che `corri.sh` non ha (#35, #36, #42) |
| `script/regressione.sh`, `script/confronta_regressione.py`, `regressione/` | i 21 deck veloci contro L47b2a |

Le forme d'onda (`*.dat`) e i deck espansi (`corsa_*.cir`, `deck.cir`, `*_resolved.cir`) sono in
`.gitignore`: si rifanno correndo. Le `corsa_*_20.cir` di `curve_CC` ed `curve_EE` portano le
opzioni di `sonda_20hz/aggiungi_*.py`: dopo `corri.sh`, si rimettono con quegli script.

## Il verdetto V2 (pilota ideale, banco corretto)

| | Peggiore | Dove |
|---|---|---|
| S inserimento | 9,36 dB (B), 10,21 dB (D) | `sorgente/`, `curve_DD/` |
| S rilascio | 13,52 dB (B), 12,29 dB (A, E) | `sorgente/`, `curve_*/` |
| A senza segnale | 5,4 µV (accensione); con la dispersione 0,56 µV | `sorgente/`, `cf_offset/`, `sorgente_iosa/` |
| B senza segnale | 0,004 µV | `curve_*/` |
| **B con musica a 20 Hz** | **100,5–241,2 µV, non regge** (NC-053) | `sorgente/`, `curve_*/` |

Escluse: le 24 corse di spegnimento (`off_`), come in L29d2; 3 abortite con rc 0. `cinv25_lz`, A
all'inserimento d'un'inversione a d = 0,25: finestra corta, «non accetta» (3–11 nV).

## Per rieseguire (percorsi assoluti nel worktree; `<L>` = `docs/preamp/data/2026-10-03/L47b2b1`)

```
/usr/bin/python3 <L>/banco/rapido.py 7e-3 [v5]           # v4 (o v5) a 7 mA, curve A-E, in secondi
/usr/bin/python3 <L>/banco/sfumatura.py v4               # la tran vera: v4 compresso
/usr/bin/python3 <L>/banco/sfumatura.py v5 v5            # la tran vera: v5
/usr/bin/python3 <L>/banco/famiglia.py <L>/banco/tabelle/famiglia_versi.csv [td_s]
/usr/bin/python3 <L>/banco/asimmetrico.py <famiglia_versi.csv> <uscita.json> [td_s]
/usr/bin/python3 <L>/banco/cerca_pilota.py p1|p2 200 <seme> <uscita.json> --carico
/usr/bin/python3 <L>/e3/genera_e3_sequenza.py <L>/e3/tb_e3_seq.cir
/bin/zsh scripts/run_simulation.sh <L>/e3/tb_e3_seq_<curva>.cir <L>/e3/out
/usr/bin/python3 <L>/e3/riassunto_e3.py <L>/e3/out <L>/e3/e3_sequenza.csv
/usr/bin/python3 <L>/impronta/genera_impronta.py library/preamp.pretty/NSL-32SR3_LED3.30.kicad_mod
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py
/usr/bin/python3 docs/preamp/data/2026-09-22/L29b2/deck/genera_tb_v2_mute_ldr.py
/bin/zsh docs/preamp/data/2026-09-23/L29c/script/corri.sh <L>/v2/sorgente spice/preamp/tb/tb_v2_casopeggiore.cir '.*' 8
/bin/zsh <L>/v2/corri_curve.sh 8
/usr/bin/python3 <L>/script/guardia_v2.py <L>/v2/sorgente <L>/v2/curve_AA ...
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/script/verifica_partenza.py <cartella>
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/script/analizza_par.py <cartella>/manifest_sel.csv <cartella> <cartella>/analisi.csv 8
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/script/verdetto.py <cartella>/manifest_sel.csv <cartella>/analisi.csv <cartella>/verdetto.csv
/bin/zsh <L>/script/regressione.sh dopo
/usr/bin/python3 <L>/script/confronta_regressione.py
```
