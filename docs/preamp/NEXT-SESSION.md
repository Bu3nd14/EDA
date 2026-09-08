# Prompt per la sessione successiva — L3

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L3,
e si ferma. Non iniziarne un secondo.

Leggi PRIMA, in quest'ordine, e non saltare:
  1. CLAUDE.md — ambiente, percorsi assoluti, trappole che falliscono in
     silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. docs/preamp/STATE.md — la sezione "Come si lavora da qui", la
     tabella dei lotti, e il paragrafo "L2-L5 — i testbench diventano
     artefatti", che contiene la convenzione già decisa e misurata
  3. spice/preamp/tb/tb_op.cir — il commento in testa al file È la
     convenzione. Non va riprogettata: va replicata
  4. docs/limitations.md — #10 (trappole di ngspice batch) e #13
     (i suffissi di valore che falliscono in silenzio)

Non serve rileggere le ADR: L3 non tocca il circuito.

Contesto in due righe: preamplificatore di linea a guadagno unitario,
Classe A pura a discreti senza operazionali, per sostituire un Technics
SU-9070 la cui struttura di guadagno sbagliata (46 dB di attenuazione
richiesta) è la causa misurabile della mancanza di dinamica lamentata.
La topologia canonica è in circuits/preamp/, i banchi di prova in
spice/preamp/tb/ (12 deck).

ATTENZIONE AL RAMO. Il lavoro sta su `worktree-preamp-lotti`, pushato su
origin. Se la PR verso `main` è già stata mergiata, riparti da `main`
aggiornato; altrimenti riusa quel worktree. `main` da solo NON contiene
L0/L1/L2.

------------------------------------------------------------------
IL LOTTO: L3 — applicare la convenzione agli altri 11 deck
------------------------------------------------------------------

LA CONVENZIONE È GIÀ DECISA E MISURATA. Non riaprirla.

  lettura   .include @REPO@/<percorso-dalla-radice-del-repo>
            run_simulation.sh sostituisce @REPO@ con la radice del
            checkout di cui lo script stesso fa parte
  scrittura wrdata <nome-nudo>, senza percorso
            il `cd "$OUTDIR"` dello script lo porta nel posto giusto

Perché non un percorso relativo, misurato in L2 e non da rifare: ngspice
risolve un `.include` relativo contro la DIRECTORY DI LAVORO, non contro
la directory del deck. Due file omonimi, uno da 1 kΩ raggiungibile dal
deck e uno da 9 kΩ dal cwd: ngspice ha letto quello del cwd
(i(V1) = -1.111e-04). Il vincolo è reale.

COSA RESTA DA FARE

Restano 26 righe cablate su `.claude/worktrees/preamp-fase1/` negli 11
deck diversi da tb_op.cir: 22 `.include` e 4 `wrdata`. L'elenco esatto:

  grep -rn '\.claude/worktrees' spice/preamp/tb/

DUE TRAPPOLE, già viste aprendo i deck — non riscoprirle

  1. `tb_dc_headroom.cir` ha DUE `wrdata` (dc_0db, dc_10db).
     `run_simulation.sh` cerca per primo `<basename>_wrdata.txt` e, se
     non lo trova, ripiega su `grep ... | head -1`, che vede UN SOLO
     wrdata. Con due file per deck il secondo non viene convertito in
     CSV/JSON. Va gestito consapevolmente: o si accetta (i .txt ci sono
     comunque) e lo si scrive in STATE.md, o si migliora lo script.
     Decidere, non subire.
  2. `tb_ac.cir` ha un doppio ciclo `foreach` che chiude ogni iterazione
     con `destroy all`. NON è un deck da L3: aggiungere lì un wrdata è
     L5. In L3 gli si cambiano solo i due `.include`.

FATTO QUANDO

  - `grep -rc '\.claude/worktrees' spice/preamp/tb/*.cir` dà 0 ovunque
  - OGNI deck toccato è stato ESEGUITO davvero con
    `/bin/zsh scripts/run_simulation.sh <deck> results/preamp/<nome>`,
    con exit code 0 e nessun "Could not find include file" nel log —
    verificato con ls e grep, non dedotto
  - i numeri non cambiano: per almeno i deck che stampano un .op, il
    confronto con la versione committata deve dare risultati identici
    (le due copie incluse sono identiche, quindi uno scostamento
    significa che si include il file sbagliato)
  - /bin/zsh scripts/run_tests.sh resta 5 passed, 0 failed

NON FA PARTE DI L3: aggiungere `wrdata` ai 9 deck muti (è L4/L5), e
toccare il circuito.

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
    poi aggiorna docs/preamp/STATE.md segnando L3 fatto e L4 prossimo,
    poi riscrivi questo file per L4, poi fermati.
