# L45a — i guasti del blocco di guadagno (2026-10-13)

Dati del report `docs/preamp/reports/2026-10-13-L45a-fmea-blocco.md` (NC-042). Prima parte di L45
(«Quattro parti», scelta dell'utente all'apertura): qui solo il blocco di guadagno, nelle quattro
posizioni del canale. Il circuito non cambia.

## Il banco

`script/genera_canale.py` scrive un canale intero di oggi (sorgente K11, C_IN 1 µF e R_SEL 470 kΩ,
blocco A, buffer F1 e F2, scala del trim sempre montata, C_T 10 µF, volume al massimo, blocco B,
le tre uscite con la geometria iii e i carichi) e mette nella posizione scelta `GAINBLOCKG`: il
`gain_block.subckt` di oggi con **una** riga cambiata e un interruttore comandato da `CTL`.

- un corto: `SFLT` fra due terminali, 10 mΩ quando CTL = 1;
- un aperto: il terminale spostato su `FLTX`, e `SFLT` fra i due, 10 mΩ quando CTL = 0 e 1e12 dopo;
- il guasto entra a **0,3 s**, con una rampa di 10 µs, durante l'ascolto (mute rilasciato), senza
  segnale; la corsa finisce a 2,3 s. Lo stato finale e il calore sono medie degli ultimi 10 ms.

Modi (`modi.csv`, 116): BJT corto C-E (`ce`), corto B-E (`be`), emettitore aperto (`ae`); JFET
corto D-S, G-S, source aperto; diodi, resistenze, condensatori corto (`cc`) e aperto (`ap`). Esclusi
dal banco: i corti dei disaccoppiamenti dei rail (C139–C142 `cc`), che coi rail ideali sarebbero
migliaia di ampere (un sovraccarico del regolatore: L45c), e le parti che in una posizione non ci
sono (R113 sui buffer, R138/R143 fuori dal blocco B).

## Le famiglie di corse (`deck/`, `run/`)

| Variante | Cosa |
|---|---|
| `op_A`, `op_F2`, `op_B`, `op_B_g10` | punto di lavoro col guasto inserito; solo controllo incrociato (circa 70 su 442 non convergono, limitations #57) |
| `tr_A`, `tr_F1`, `tr_F2`, `tr_B`, `tr_B_g10` | il transitorio di ogni modo, e `rif` senza guasto |
| `tr_ctrl_A/F2/B` | il controllo che DEVE superare il tetto: l'uscita del blocco in corto col rail + |
| `tr_corta_*` | i casi bloccati (30 min senza finire) rifatti fino a 0,6 s; `tr_r120_B` il corto di R120 fino a 0,32 s |
| `tr_gear_*` | i casi interrotti («timestep too small») rifatti col metodo gear |
| `tr_musica_A/B` | i casi peggiori col K11 a fondo scala (2,7 V RMS a 1 kHz), contro `rif` con la stessa musica |
| `tr_mute_A/B` | il guasto a mute inserito (0,3 s) e il rilascio a 1,0 s: l'argomento della geometria iii (R1 di L52) |
| `tr_taglio*_A/B` | il mute inserito 0,1 / 1 / 3 / 10 ms dopo il guasto: un rivelatore ideale col relè (G6K, rilascio 3 ms max) |

## Le analisi

- `script/analizza_tr.py` — per ogni corsa e ogni jack il gradino grezzo e il metodo di PR-23
  (`scripts/v2_metodo.py`: evento − riferimento, filtro 20 Hz–20 kHz, picco), in volt e in dB SPL
  di picco a 1 m (PRB: 96 + 20 log10(21,1 V / 2,83)); la Stax con la catena di NC-046
  (101 + 20 log10(1000 V / 100)); lo stato finale, la corrente dei rail, le potenze e le Tj
  (R_thJA di `caldo.py` di L56, VAS e carico in SOT-223). Diradamento come `v2_metodo analizza`:
  un quinto del passo massimo del deck (con 0,1 µs l'interpolazione cubica dava 47,8 V su un jack
  fra −6 e +4,4 V).
- `script/sintesi.py` — classe dell'uscita del blocco, verdetto contro il tetto (0,87 V) e
  l'obiettivo (2 mV) di PR-23, calore oltre i limiti.
- `script/forma.py`, `script/picchi.py` — diagnostica di una corsa.

File: `analisi_<famiglia>.csv`, `sintesi_<famiglia>.csv`, `analisi_taglio.csv`.

## Rifare

```sh
/usr/bin/python3 <L45a>/script/genera_canale.py modi
/usr/bin/python3 <L45a>/script/genera_canale.py tr A TUTTI        # e F1, F2, B; B con --gain 10 --nome B_g10
/bin/zsh <L45a>/script/corri.sh <L45a>/deck/lista_tr_A.txt        # 8 alla volta (xargs -P 8)
/bin/zsh <L45a>/script/analizza_tutto.sh
```

Gli elenchi `deck/lista_*.txt` portano i percorsi assoluti del worktree di L45a, che non esiste
più: **si rigenerano** con `genera_canale.py` (che li riscrive) prima di `corri.sh`.

**Non** `esegui.sh` di L56 in background: parte tutta la lista insieme (limitations #58).
