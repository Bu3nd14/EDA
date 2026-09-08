# Prompt per la sessione successiva

Copia il blocco qui sotto in una sessione nuova aperta su
`/Users/roberto/EDA`. È scritto per essere autosufficiente: non presuppone
nulla della conversazione precedente.

Riscrivilo — non aggiungerci in coda — quando il lotto che descrive è
chiuso. Deve descrivere **un lotto solo**, quello prossimo.

---

```
Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L2,
e si ferma. Non iniziarne un secondo.

Leggi PRIMA, in quest'ordine, e non saltare:
  1. CLAUDE.md — ambiente, percorsi assoluti, trappole che falliscono in
     silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. docs/preamp/STATE.md — in particolare la sezione "Come si lavora da
     qui: a lotti piccoli e pushati", la tabella dei lotti, e il
     paragrafo "L2-L5 — i testbench diventano artefatti", che contiene
     l'analisi già fatta e i vincoli già scoperti
  3. docs/limitations.md — obbligatorio prima di scrivere codice; in
     particolare la #10 (trappole di ngspice batch) e la #13 (i suffissi
     di valore che falliscono in silenzio)

Non serve rileggere le ADR per questo lotto: L2 non tocca il circuito.

Contesto in due righe: preamplificatore di linea a guadagno unitario,
Classe A pura a discreti senza operazionali, per sostituire un Technics
SU-9070 la cui struttura di guadagno sbagliata (46 dB di attenuazione
richiesta) è la causa misurabile della mancanza di dinamica lamentata.
La topologia canonica è in circuits/preamp/, i banchi di prova in
spice/preamp/tb/ (12 deck).

------------------------------------------------------------------
IL LOTTO: L2 — collaudare la convenzione di percorso su UN deck solo
------------------------------------------------------------------

IL PROBLEMA, già analizzato e verificato — non ricominciare da capo

Tutti e 12 i deck in spice/preamp/tb/ contengono percorsi assoluti
cablati dentro un worktree: .claude/worktrees/preamp-fase1/. In tutto
28 righe, e 24 di queste sono .include, cioè la METÀ CHE LEGGE:

  .include /Users/roberto/EDA/.claude/worktrees/preamp-fase1/spice/preamp/gain_block_flat.inc

Il pericolo è la lettura, non la scrittura. Una modifica al circuito su
main NON raggiungerebbe le simulazioni: continuerebbero a includere la
copia di settembre, senza errore da nessuna delle due parti. Oggi le due
copie sono identiche (verificato con diff su gain_block_flat.inc e
placeholder_devices.lib), quindi nessun risultato prodotto finora è
sbagliato — ma il meccanismo è armato, e cancellare quel worktree rompe
di colpo tutti e 12 i deck.

Le altre 4 righe sono wrdata, e scrivono i risultati nell'albero vecchio.

È la stessa classe di difetto già corretta una volta in run_tests.sh
(ROOT cablato, che faceva testare in silenzio un altro albero).

DUE VINCOLI GIÀ SCOPERTI leggendo scripts/run_simulation.sh. Verificali,
ma non riscoprirli:

  1. Lo script fa  cd "$OUTDIR"  prima di lanciare ngspice (riga 73).
     Quindi un .include RELATIVO non funziona: si risolverebbe contro la
     directory dei risultati, non contro quella del deck. "Basta usare
     percorsi relativi" è la risposta sbagliata.

  2. Lo stesso cd risolve però la metà wrdata quasi da sé: lo script CERCA
     GIÀ il file che il deck ha scritto dentro $OUTDIR (righe 80-90).
     Un  wrdata <nomefile>  SENZA percorso dovrebbe atterrare nel posto
     giusto da solo.

  3. run_simulation.sh ha lo stesso difetto dei deck: ROOT=/Users/roberto/EDA
     cablato alla riga 26. run_tests.sh è stato corretto a suo tempo
     (ROOT=${0:A:h:h}); export_fab.sh e setup.sh no.

CANDIDATO PRINCIPALE PER GLI .include, da provare e non da dare per
buono: far sostituire a run_simulation.sh un segnaposto @REPO@ nel deck,
producendo un deck derivato — cosa che lo script già fa quando serve
(riga 61, "autowrap"). Se trovi una via migliore, prendila e scrivi
perché.

COSA DEVE FARE QUESTO LOTTO, e nient'altro

  - Scegliere e collaudare la convenzione su UN SOLO deck: tb_op.cir.
    È il più semplice (un .op e una lista di print, nessun ciclo) ed è
    già usato dalla suite.
  - Correggere ROOT in run_simulation.sh, se serve alla convenzione.
  - Lasciare gli altri 11 deck INTATTI. Toccarli è L3.
  - Scrivere la convenzione in un commento dentro tb_op.cir, così L3 la
    replica senza riprogettarla.

FATTO QUANDO

  - tb_op.cir non contiene più la stringa .claude/worktrees
  - eseguito dal checkout corrente, include i file DI QUEL checkout e
    scrive il suo file DENTRO quel checkout — verificato con ls, non
    dedotto
  - la prova che conta: il deck deve funzionare anche se il worktree
    .claude/worktrees/preamp-fase1 non esiste. Non cancellarlo per
    provarlo — basta verificare che nessun percorso lo nomini più
  - /bin/zsh scripts/run_tests.sh resta 5 passed, 0 failed

COME LAVORIAMO

  - Verifica invece di fidarti. Se un subagente riporta dei numeri,
    rieseguili tu prima di riferirmeli. È già servito.
  - Niente cifre non eseguite. Una simulazione descritta e non lanciata
    non è evidenza.
  - Un lotto per volta, mai due agenti in parallelo: il vincolo è il cap
    di token del piano, e i resoconti che tornano insieme sono la parte
    che consuma.
  - Lavora in un worktree. I commit non pushati dentro
    .claude/worktrees/ spariscono col worktree, ed è già successo.
  - CHIUSURA, nell'ordine: git push PRIMO (verifica con
    git log --oneline origin/<branch>..HEAD, che deve essere VUOTO),
    poi aggiorna docs/preamp/STATE.md segnando L2 fatto e L3 prossimo,
    poi riscrivi questo file per L3, poi fermati.

STATO DEL REPO A QUESTO PUNTO

Il lavoro sta sul branch worktree-preamp-lotti, pushato su origin, due
commit avanti a origin/main (L0: il piano dentro STATE.md; L1: il
diagramma a blocchi del preamp intero). Se preferisco averlo su main te
lo dico io: non aprire una PR di tua iniziativa.

Comincia dicendomi cosa hai trovato aprendo tb_op.cir e
run_simulation.sh, e quale convenzione proponi. Poi falla.
```
