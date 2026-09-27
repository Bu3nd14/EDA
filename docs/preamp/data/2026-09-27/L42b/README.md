# L42b — il dossier rigenerato, l'alimentatore (2026-09-27)

Dati del lotto L42b. Il dossier è `docs/preamp/dossier/index.html`, generato da
`docs/preamp/dossier/build_dossier.py`: le cartelle dei lotti dell'alimentatore (L41a, L41b1,
L41b2, L41c, L30) sono la prima strada, queste ricorse la seconda. Nessuna modifica al
circuito, al firmware o ai deck versionati.

## Le decisioni dell'utente (2026-09-27), prima di scrivere codice

Approvate col piano del lotto:

| Domanda | Risposta |
|---|---|
| La scaletta | sette sezioni: schema e decisioni; potenza, rail e `VRELAY`; sorvegliante e guasti; temporizzatore; firmware; pilota delle LDR (col grafico); spegnimento e failsafe al jack, in dB SPL |
| I banchi di L41a, corsi su un `psu.py` che non c'è più | **ricorsi sul `psu.net` di oggi**, con L41a come seconda strada |

## Le cartelle

Tre cartelle sorelle, perché gli script dei lotti ricavano la radice del repo dalla loro
profondità e scrivono in `../seq`: copiati identici alla stessa profondità, non si toccano.

| Percorso | Cosa |
|---|---|
| `L42b/deck/` | `genera_tb_psu.py`: il generatore di L41c con `--nome rete` e `--nome guasti` (i casi e le sonde di L41a sul circuito di oggi) e `--carico l41a` (il controfattuale del carico); `analizza.py`: quello di L41a con la sonda `VRELAY_REG`. Le differenze sono dichiarate nelle intestazioni |
| `L42b/rete/`, `L42b/guasti/` | i due banchi di L41a ricorsi: deck, log, `analisi.csv` |
| `L42b/carico_l41a/` | gli stessi banchi senza ciò che il banco di L41a non aveva (le bistabili del trim, le stringhe delle LDR e la serie al riposo, il micro): **ridanno L41a su ogni colonna** |
| `L42b/timer/` | i deck del temporizzatore rigenerati col generatore di L41b1 (uguali a quelli di L41b1 a meno dei percorsi) e corsi |
| `L42b/ldr/` | i quattro deck delle LDR a 12 mA rigenerati col generatore di L41b2, corsi e analizzati; calibrazioni e CSV uguali byte per byte a L41b2 |
| `L42b/falsi/esito.txt` | `run_host_tests.sh --falsi` rieseguito: uguale a quello di L41b2 |
| `L42b/scelte/` | `raddrizzatore.py` di L41a, copiato e rieseguito: `raddrizzatore.csv` uguale |
| `L42b/l30/` | il deck di L30 rigenerato (uguale) e le sue 29 corse rifatte: `analisi.csv` e `tabella.csv` uguali |
| `L42b-L41c/` | `psu/` di L41c copiato identico; `seq/` (i nove casi al punto fisso), `ponte/`, `deck/`, `corse/`, `tabella.csv` ricorsi: tutto uguale a L41c |
| `L42b-L41b2/` | `deck/` di L41b2 copiato identico; `seq/` (le sette sequenze): uguale a L41b2 |
| `L42b/script/sabotaggi.py`, `sabotaggi.txt` | i 15 sabotaggi di L42a più 32 di L42b (29 del generatore, 3 del disegnatore dell'alimentatore): **47 su 47 caduti**, e poi generatore e disegnatore escono 0 sui file veri |

Le forme d'onda (`*.txt` di wrdata, `*_out.txt`, `*.dat`: ~11 GB) non si committano
(`.gitignore` di radice).

## Come si rifà

Dalla radice del repo, percorsi assoluti:

```sh
G=docs/preamp/data/2026-09-27/L42b/deck/genera_tb_psu.py
/usr/bin/python3 $G --nome rete   --cima 12e-3 --uscita <abs>/L42b/rete
/usr/bin/python3 $G --nome guasti --cima 12e-3 --uscita <abs>/L42b/guasti
/usr/bin/python3 $G --nome rete   --cima 12e-3 --carico l41a --uscita <abs>/L42b/carico_l41a/rete
/usr/bin/python3 $G --nome guasti --cima 12e-3 --carico l41a --uscita <abs>/L42b/carico_l41a/guasti
/opt/homebrew/bin/ngspice -b <deck>.cir -o <deck>.log          # ognuno, pochi minuti
/usr/bin/python3 docs/preamp/data/2026-09-27/L42b/deck/analizza.py <abs>/L42b/rete   # idem gli altri tre
/bin/zsh docs/preamp/data/2026-09-27/L42b-L41c/psu/tutti_seq.sh      # ~5 min, poi ponte, deck, corse: README di L41c
/bin/zsh docs/preamp/data/2026-09-27/L42b-L41b2/deck/tutti_seq.sh    # ~10 min
/usr/bin/python3 docs/preamp/dossier/build_dossier.py
/usr/bin/python3 docs/preamp/data/2026-09-27/L42b/script/sabotaggi.py
```

Il temporizzatore, le LDR, il raddrizzatore e L30: i comandi dei README dei loro lotti, con
`--uscita` (o la cartella delle corse) qui dentro.

## Cosa si è trovato

- **I banchi della potenza di L41a erano su un circuito che non c'è più.** L41b1 ha riscritto
  `psu.py` (+331/−40 righe), e il generatore di oggi non faceva più `rete` e `guasti`. Il
  dossier li mostra ricorsi; `build_dossier.py` rifiuta `L41a/rete`, `guasti`, `varianti` come
  prima strada (`FORBIDDEN`) e li legge solo come seconda (`vecchio()`).
- **La tenuta di `VRELAY` è scesa**: a rete −10 / nom / +10 %, `VRELAY_REG` ≥ 11,4 V per
  **36,1 / 102,1 / 168,5 ms** dopo il rilascio del mute, contro 62,8 / 144,9 / 227,3 di L41a.
  P9 (≥ 25 ms) regge ancora, con 11 ms di margine invece di 38. La causa è il carico che
  L41b1 e L41b2 hanno aggiunto su `VRELAY_REG`: il controfattuale col carico di L41a ridà
  62,68 / 144,68 / 227,00 ms. Soprattutto il ramo d'ingresso dello specchio delle LDR alla cima:
  tolte le sole stringhe, la tenuta tornava solo a 49,1 ms. Lo stesso carico anticipa il
  rilascio nel guasto di U503 (13,3 ms contro 15,8) e, col rivelatore guasto a rete −10 %, fa
  scattare per primo il sorvegliante di `VRELAY_REG` (59,9 ms contro 72,5).
- **Il commento di `C_VRELAY` in `psu.py`** cita ancora la tenuta di L41a («51 / 134 / 216 ms»,
  dalle varianti). Il sorgente non si tocca in questo lotto: è materia per L43.
- **Tutto il resto si riproduce byte per byte**: le catene di L41c e L41b2 (verdetti, punti
  fissi, deck, uscite del core, ponte, corse audio, tabelle), il temporizzatore di L41b1, le
  LDR di L41b2, i falsi sull'host, L30, il raddrizzatore.
- **Un difetto del banco, non del circuito**: con la serie alla cima da t = 0 il caso a rete
  −10 % si fermava a 4,6 ms su «Timestep too small» in `exp_e_s`; il rimedio è quello di L41c
  (`uscite_core`): il DAC al codice di riposo fino a 0,5 s. Dichiarato nel generatore.
- **I due falsi sul circuito** (6 e 9 di L41b2) non sono stati ricorsi: richiedono di
  ricompilare il ponte col falso dentro. Il dossier lo dice.
