# Prompt per la sessione successiva — L46b (il PSRR del rail positivo: nel blocco o nell'alimentatore)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L46b**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'ordine dei rimedi scelto dall'utente il 2026-10-01 è **L46 → L44 → L47 → L48 → L49 → G1 → L45 →
L50**. L46 è stato diviso dall'utente all'inizio: **L46a** (fatto, 2026-10-01) ha rifatto la
compensazione del blocco di guadagno; **L46b** è la seconda metà, il PSRR del rail positivo.

- **NC-047 (bloccante per G1)** — il rilievo dell'utente: «Temo che l'alimentatore non riuscirà ad
  essere abbastanza silenzioso e quindi dovremo mettere mano al circuito audio per aumentare la
  PSRR.» Col blocco di **ADR-054** (VAS ~10,7 mA, C124 470 pF) il PSRR+ a +10 dB è **66,9 / 49,5
  / 29,5 / 23,5 dB** a 100 Hz / 1 / 10 / 20 kHz: +6,5 dB rispetto al blocco di prima, ma ancora
  ~50 dB sotto il rail − a 10 kHz. Dati: `data/2026-10-01/L46a/regressione/dopo/
  tb_zout_psrr_noise/`.
- **Quello che L46a ha imparato**: il PSRR+ **dipende solo dal Miller** (470 pF → 29,5 dB a 10 kHz
  in ogni topologia misurata; 330 pF → 32,6; 220 pF → 36,0). Il rail + entra nel blocco
  attraverso C124 e il VAS, che sta sul rail +. Un Miller più piccolo, coi dispositivi d'uscita
  ZXT, arrivava a 36 dB: l'utente l'ha scartato (ADR-054, «Da riaprire se» cita proprio L46b).
- **Il residuo dei rail non è mai stato simulato**: nel banco di `psu.py` i regolatori sono
  comportamentali, senza PSRR né rumore; il modello TI del TPS7A4701 dà un punto di lavoro
  sbagliato (~1 V). NC-011 resta la verifica sul prototipo.
- **NC-052** (minore): la «Nota su E5» di `REQUIREMENTS.md` cita
  `data/2026-09-23/L40/dopo/tb_zout_psrr_noise/*_psrr{p,m}_10db.csv`, che non esistono. Si
  ripunta ai CSV di L46a quando si ricalcolano i limiti.

## Il mandato

1. **All'inizio, con l'utente** (le domande **per nome**, mai per sigle: «non ricordo sigle a
   memoria»; i livelli di rumore in **dB SPL** contro una stanza silenziosa, non in µV): dove sta il
   rimedio. Le strade da mettere in tabella, ciascuna misurata prima di chiedere la scelta:
   - **nel blocco**: una cella RC (o RC + condensatore grande) che alimenti il VAS e/o lo stadio
     d'ingresso dal rail + filtrato, oppure un'alimentazione separata dello stadio d'ingresso; i
     costi in caduta di tensione (headroom, V3, clip), in rumore della resistenza, in parti;
   - **nell'alimentatore**: la quota di ADR-020 verificata su uno spettro simulato dei rail
     (serve un modello credibile del TPS7A4701 o un limite per eccesso dichiarato);
   - **entrambe**.
   La scelta è dell'utente, e diventa una **ADR**.
2. **Ogni variante del blocco** misurata col banco di L46a (`data/2026-10-01/L46a/script/`,
   README dentro): V1 su ogni istanza e nel gruppo B (≥ 60°, ADR-019), PSRR± a 100 Hz / 1 / 10 /
   20 kHz, rumore E5, i tetti di V4 di **ADR-055**, slew, punto di lavoro e clip. Il blocco di oggi
   (`cm1n` non è più il blocco di oggi: è `vas56_cm470p`) corre per primo come controllo.
3. **ADR-020 ricalcolato** sul circuito che ne esce con `data/2026-09-23/L40/script/limiti_psrr.py`,
   la tabella per tono in `REQUIREMENTS.md` aggiornata, la nota ripuntata a CSV che esistono
   (chiude **NC-052**). Il rail − ha perso 2,5 dB a 100 Hz con ADR-054 (73,3 → 70,7): entra nel
   ricalcolo.
4. **Tracciabilità**: ogni valore nuovo in `circuits/preamp/*.py` col commento che punta alla ADR.
   Netlist rigenerate; la regressione dei 21 deck veloci con `script/regressione.sh` di L46a (le
   cartelle `prima/` e `dopo/` si rifanno: copiale o cambia il nome delle fasi).

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (le trappole che falliscono in silenzio; la **#38** è nuova: il
  rimedio del «transient op» dipende dal circuito), e in `docs/preamp/STATE.md` «In breve» e le
  voci di diario di L46a e L40.
- `NONCOMPLIANCE.md`: NC-047, NC-011, NC-052.
- `decisions/ADR-020*`, `decisions/ADR-048*` (l'alimentatore), `decisions/ADR-054*`, e il report
  `reports/2026-10-01-L46a-compensazione.md`.

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `awk` con programmi, i cicli con variabili e i percorsi calcolati a runtime;
  - gli heredoc;
  - un titolo di PR con l'apostrofo (`gh pr create`): il corpo va su file (`--body-file`).

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi.
- Le cifre dai modelli sono cifre di modello: conta il trend, non il valore assoluto.
- Un deck con `tran` dopo un `alter` va guardato nel log: «Transient op started» invalida la corsa
  (#33, #38).

## NON fa parte di questo lotto

- il rumore 1/f (NC-004, è L44, subito dopo); la cella del mute (L47); il selettore d'ingresso e
  la continua del blocco A, salita a −26 mV con ADR-054 (L48); il placement e routing di prova
  (L49); la FMEA (L45); massa e terra (L50);
- la compensazione: è decisa (ADR-054), salvo che la strada del PSRR+ la rimetta in discussione
  come dice il suo «Da riaprire se»;
- rigenerare il dossier.

## CHIUSURA

1. `STATE.md` con L46b **fatto** e il prossimo lotto (L44) nella tabella.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L46b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
