# Prompt per la sessione successiva — L29d2 (la matrice del contatto in serie)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L29d2** e si ferma. Non iniziarne un secondo.

## PRIMA DI TUTTO: le decisioni dell'utente

La sonda di L29d (`reports/2026-09-25-L29d-sonda-contatto-serie.md`) ha lasciato **tre decisioni
all'utente**. Nessuna corsa della matrice parte prima di averle, e ogni decisione va registrata con
le sue parole.

1. **Quale geometria** va nella matrice:
   - la **iii**: serie più derivazione dal lato del condensatore. È l'unica che ha retto quasi tutto;
   - la **iB**: serie più derivazione al jack, la serie che si chiude per prima, con un
     trasferimento più lungo di 1 ms. Oggi dà 0,3–5,6 mV;
   - la **ii**, serie sola, è da scartare: nessuna cella la salva.
2. **Lo stato sicuro (ADR-012)**: «a macchina spenta le uscite sono a massa». Nella iii, a riposo, il
   jack va a massa solo attraverso il bleed (220 k / 470 k), non attraverso un contatto. Le strade:
   - il bleed basta;
   - un secondo polo che mette a massa anche il jack: la iii più la derivazione al jack, da
     misurare. Conta anche quanti poli ha il relè: oggi un relè serve L e R con due poli.
   - La scelta tocca il failsafe di ADR-043.
3. **I valori**, che oggi sono ipotesi del banco:
   - il bleed dal lato condensatore;
   - la capacità del contatto aperto, dal datasheet del relè: 5 pF ipotizzati;
   - la capacità del cavo al jack da considerare: zero nella sonda;
   - il tempo di trasferimento: 1 ms.

   **Il residuo della iii** (205 µV all'accensione da 300 ms) è passaggio capacitivo di quei 5 pF:
   dipende proprio da questi numeri.

**Nessun cambio di topologia né di valore in `circuits/` senza l'utente.**

## Da dove si parte

- **Il generatore**: `data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py`, esteso in L29d:
  - `--matrice sonda_l29d`, con le geometrie N, iA, iB, ii e iii;
  - `sonda_aggiunte()`, i contatti KS (serie) e KC (derivazione lato condensatore);
  - `geo_alter()`, gli istanti e il bleed.

  Si estende di nuovo per la matrice di L29d2. I deck di L29c devono restare byte-identici
  rigenerandoli.
- **I dati di L29d**: `data/2026-09-25/L29d/` (README). Contiene:
  - `sonda/verdetto.csv` e `sonda/tabella.csv`;
  - `script/controfattuale_N.py`, `tabella.py`, `sbircia.py` e `forma.py`.
- **Gli strumenti di L29c** (`data/2026-09-23/L29c/script/`): `corri.sh`, `verifica_partenza.py`,
  `analizza_par.py`, `verdetto.py`, `confronta_analisi.py`.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`**, in particolare #29–#33.
2. **`docs/preamp/STATE.md`**: le voci L29d e L29c del diario, le righe L29d2, L36 e L30.
3. **`reports/2026-09-25-L29d-sonda-contatto-serie.md`** per intero, poi il report di L29c.
4. **ADR-012**, **ADR-038/039/040/041**, **ADR-043**.
5. **`NONCOMPLIANCE.md`**: NC-028, gli aggiornamenti di L29c e L29d.

## IL LAVORO, dopo le decisioni

1. **La geometria scelta nel generatore**, coi valori dell'utente, più il controfattuale: N deve
   ridare L29c.
2. **La matrice di L29c** sulla geometria scelta:
   - il cambio di guadagno e di trim a relè chiuso (punti 1 e 2);
   - la dispersione peggiore (`dp…max`, punto 3);
   - l'accensione (punto 5);
   - la musica (S, B2) a 1 kHz e 20 Hz;
   - **B col contatto aperto**.
3. **Il carico da 10 kΩ** sulla cella peggiore di ogni punto: mai fatto, né in L29c né in L29d.
4. **20 kHz** solo se serve, pianificato prima: in L29c ci sono volute 6–11 ore.

**Esito**: la tabella della geometria scelta contro L29c. La scelta diventa **una ADR** (tocca
ADR-012 e ADR-043). Se tutte le celle stanno sotto 100 µV (lo spegnimento escluso, che è di L30),
**NC-028 si può chiudere per la parte del mute**. Scrivilo con l'utente, non da solo.

## I vincoli

- `set numdgt=15` prima di ogni `wrdata` (#30); `pwl()` estrapola (#31); nessun corpo di `if`
  vuoto (#32); una corsa col transient op non vale (#33).
- **Il manifesto non è l'elenco delle corse**: una cella si estrae dalla colonna `file`.
- Nel worktree `git`, i comandi composti, `awk -v` e i percorsi calcolati a runtime vengono
  rifiutati: comandi semplici, **percorsi assoluti**, script su file.
- Le forme d'onda non si committano: c'è un `.gitignore` in ogni cartella dati.
- I tempi di L29d: con i rail in rampa o senza segnale, una corsa dura 2–4 minuti, 8 in
  parallelo; `analizza_par.py` con 8 processi fa 32 corse in 4 minuti.

## NON fa parte di questo lotto

- **L36** (viene dopo), L30 e il failsafe (ADR-043), L35, L28, il dossier.

## CHIUSURA

1. `STATE.md` con L29d2 **fatto** e il prossimo lotto.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L29d2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
