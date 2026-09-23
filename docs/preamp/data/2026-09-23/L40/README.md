# L40 — V1 coi modelli del costruttore (2026-09-23)

Esplorazione della Fase A (punti 1–4 del prompt): **nessun valore del sorgente
cambiato**, nessun file di `models/` toccato. Tutti i deck sono copie dei deck di
`spice/preamp/tb/` con righe `alter` (o una riga di netlist in più) in testa al
`.control`, generate dagli script in `script/`; il resto del deck è identico. Ogni
famiglia ha una variante di controllo che ridà le cifre di L39/dopo.

| Percorso | Cosa | Script |
|---|---|---|
| `cause/` | una famiglia di modelli alla volta rimessa al segnaposto (stessi parametri, nome del costruttore), blocco B 0 dB | `separa_cause.py`, `riassumi_cause.py` → `cause/cause.csv` |
| `mje/` | dentro i MJE: CJE/CJC, TF, VAF uno alla volta (`altermod`, #29), poi R128 1,20–1,69 k | `separa_mje.py`, `riassumi.py` |
| `strada_a/` | Miller C124 470p–1,2n × R128 1,69k/1,33k sulle tre istanze (blocco B nei tre modi, blocco A, buffer) | `genera_a.sh`, `sintesi_v1.py` → `strada_a/sintesi_v1.csv` |
| `strada_b/` | guadagno minimo +0,5/+1,0/+1,5 dB (gamba fissa RG0L40 da FB a massa, R138 ricalcolata) × C124 × R128 | `genera_b.sh`, `sintesi_v1.py` |
| `strada_b_cf/` | strada (b) a +1,5 dB col C_f (C137) 100p–470p × C124 470p/560p × R128 | `genera_b_cf.sh`, `sintesi_v1.py` |
| `slew/` | slew rate a gradino e 20 kHz a fondo scala (+10 dB, 12 V di picco), metodo di L12 | `genera_slew.py` |
| `candidati/` | i costi dei candidati sui deck flat: risposta ed E2, V3, headroom, E5, PSRR/Zout, punto di lavoro | `genera_cand.sh`, `cand_ac.py`, `cand_costi.py` |

Runner: `script/esegui.sh <fase> <deck>...` (o `-f lista.txt`), 8 in parallelo.

**Fase B, dopo la decisione dell'utente (ADR-042: C124 1 nF, R128 invariato).**

| Percorso | Cosa | Script |
|---|---|---|
| `prima/` | i 21 deck veloci (`script/deck_veloci.txt`) e la cella V2 1 kHz/100 k sul `main` di L39 (C124 470 p), corsi in questa sessione prima di rigenerare; `gain_block_*_L39.*` è il blocco di prima | `esegui.sh`, `v2_cella.sh` |
| `dopo/` | gli stessi, sul blocco rigenerato (C124 1 nF) | idem |
| `prima_idss/`, `dopo_idss/` | ADR-031: V1 del blocco A e del buffer nel gruppo B di I_DSS (`altermod`, #29) | `idss_istanze.py` |
| `confronto_grezzo.csv`, `margini.csv` | ogni cifra prima/dopo; V1 per istanza | `confronta.py`, `margini.py`, `mosse.py` (cosa si muove oltre una soglia) |
| — | P7, classe A, V3, V2 | `p7.py`, `classe_a.py`, `v3.py`, `v2_riassunto.py` |
| — | i limiti per tono di ADR-020 dal PSRR vigente (riproduce L18 dai suoi CSV) | `limiti_psrr.py` |

Gli script di L39 (`confronta.py`, `margini.py`, `p7.py`, `classe_a.py`, `v3.py`, `cura.py`)
sono copiati senza modifiche al codice. **Tolto prima del commit** con `script/cura.py
--togli`: le forme d'onda di `prima/` e `dopo/` e i `.dat` di V2 (10 GB). Tutti i
riassunti sono stati rieseguiti dopo la pulizia, con le stesse cifre.

Due trappole trovate per strada, da riportare nel report:
- un corpo di `if` lasciato **vuoto** in `.control` (i `wrdata` commentati) fa
  uscire ngspice con **rc 139** a fine corsa, a tabelle complete: `varianti.py`
  mette un `let` innocuo al posto del `wrdata`;
- in `tb_ac.cir` le misure `fhi`/`flo` hanno i nomi **scambiati**: `flo` è l'angolo
  alto (2,45 MHz a 0 dB).
