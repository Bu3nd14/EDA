# Prompt per la sessione successiva — L4

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L4,
e si ferma. Non iniziarne un secondo.

Leggi PRIMA, in quest'ordine, e non saltare:
  1. CLAUDE.md — ambiente, percorsi assoluti, trappole che falliscono in
     silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. docs/preamp/STATE.md — la sezione "Come si lavora da qui", la
     tabella dei lotti, e il paragrafo "L2-L5 — i testbench diventano
     artefatti". Contiene la convenzione già decisa e misurata, la
     tabella che dice quale deck muto è L4 e quale è L5, e il riquadro su
     `gain_block.py` (L3b) che NON è di questa sessione
  3. spice/preamp/tb/tb_op.cir — il commento in testa al file È la
     convenzione. Non va riprogettata: va replicata
  4. docs/limitations.md — #10 (trappole di ngspice batch) e #13
     (i suffissi di valore che falliscono in silenzio)

Non serve rileggere le ADR: L4 non tocca il circuito.

Contesto in due righe: preamplificatore di linea a guadagno unitario,
Classe A pura a discreti senza operazionali, per sostituire un Technics
SU-9070 la cui struttura di guadagno sbagliata (46 dB di attenuazione
richiesta) è la causa misurabile della mancanza di dinamica lamentata.
La topologia canonica è in circuits/preamp/, i banchi di prova in
spice/preamp/tb/ (12 deck).

IL RAMO NON È PIÙ UN PROBLEMA. Da L3c ogni lotto si chiude mergiando e
riallineando il checkout principale, quindi **`main` è corrente e si
riparte sempre da lì**. Se `git -C /Users/roberto/EDA log --oneline -1`
non mostra l'ultimo lotto, qualcosa è andato storto nella chiusura
precedente: risolvi quello prima di iniziare L4.

------------------------------------------------------------------
IL LOTTO: L4 — `wrdata` sui deck muti SENZA cicli
------------------------------------------------------------------

L'infrastruttura c'è tutta e non va ridiscussa:

  lettura   `.include @REPO@/<percorso-dalla-radice-del-repo>`
  scrittura `wrdata <nome-nudo>`, cioè `<basename>_wrdata.txt`

`run_simulation.sh` sostituisce `@REPO@`, fa `cd "$OUTDIR"`, e da L3
converte in CSV/JSON **ogni** file wrdata prodotto da una run, non solo
il primo. Quindi un deck può scriverne più di uno senza perderne nessuno.

STATO DI PARTENZA: scrivono dati **4 deck su 12** (`tb_op`,
`tb_dc_headroom` con due file, `tb_switch_v2`, `tb_v3_overload`).
Restano **8 deck muti**, e solo i primi sono L4:

| Deck muto | `foreach`? | `destroy all`? | Lotto |
|---|---|---|---|
| `tb_noise_vectors` | no | no | **L4** |
| `tb_switch_v2_counterfactual` | no (tre `op` in sequenza) | no | **L4** |
| `tb_bias_sweep` | sì (un ciclo con `op`) | **no** | **da decidere aprendolo** |
| `tb_noise_breakdown` | sì | sì | L5 |
| `tb_ac` | sì, doppio | sì | L5 |
| `tb_loop` | sì, doppio | sì | L5 |
| `tb_loop_blockA` | sì | sì | L5 |
| `tb_zout_psrr_noise` | sì, quattro sezioni | sì | L5 |

LA REGOLA CHE SEPARA I DUE LOTTI: dove c'è `destroy all` dentro il ciclo,
il `wrdata` va **dentro il ciclo, prima del `destroy all`**, con il nome
parametrizzato — e quello è L5, perché non è meccanico.

`tb_bias_sweep` è il caso di confine e la prima decisione della sessione:
ha un `foreach` su 7 valori di R130 con un `op` per iterazione, ma
**nessun `destroy all`**. Aprilo, guarda se un `wrdata` fuori dal ciclo
cattura qualcosa di utile o se serve un file per iterazione, e decidi in
quale lotto cade. Se cade in L5, L4 sono due deck e finisce presto: va
benissimo, un lotto piccolo che chiude è meglio di uno grande che no.

COSA SCRIVERE, DECK PER DECK

Non copiare vettori a caso: il `wrdata` serve al dossier, quindi deve
contenere ciò che il grafico dovrà mostrare. Guarda cosa il deck già
`print`a — è la lista di ciò che l'autore considerava interessante.

  - `tb_noise_vectors` fa un `noise` a 1 kHz e stampa il plot `noise1`
    per intero. Il candidato è la densità spettrale, cioè le colonne che
    servono a disegnare un grafico rumore-vs-frequenza. Attenzione: un
    `noise` produce DUE plot (`noise1` spettrale, `noise2` integrato) e
    il `setplot` conta.
  - `tb_switch_v2_counterfactual` fa tre `op` in sequenza alterando
    `r138` fra l'uno e l'altro. Un `.op` non ha un asse: un `wrdata` di
    un punto operativo è una riga. Verifica cosa ne esce davvero prima di
    dichiararlo utile — se non è utile, dillo e non aggiungerlo: è un
    esito legittimo di L4, non un fallimento.

DOVE FINISCONO I DATI (deciso in L3c)

`results/` resta scratch e gitignorato: è dove atterrano tutte le run.
Ma **i dati del dossier sono versionati**, perché il gate gira offline su
`main` e deve poter aprire i numeri. Se un CSV prodotto in L4 è materiale
da dossier — cioè qualcosa che verrà impaginato o citato da una non
conformità — copialo in

```
docs/preamp/data/<YYYY-MM-DD>/<nome>.csv   (+ .json, + il .log come evidenza)
```

Curati, non grezzi: ciò che serve, non l'output di ogni esecuzione. La
convenzione per esteso è in `docs/preamp/data/README.md`. Attenzione: il
`.gitignore` ha regole globali `*.log`/`*_out.txt`/`*.raw` neutralizzate
lì dentro da una negazione — se aggiungi estensioni nuove, controlla con
`git status` che sopravvivano.

Se in L4 non esce niente di degno del dossier, va benissimo non copiare
nulla: dirlo è un esito, riempire la directory per abitudine no.

DUE TRAPPOLE

  1. Un `wrdata` di un `.op` può produrre un file con una riga sola o
    nessuna. Non dare per scontato che il CSV sia sensato: aprilo.
  2. `run_simulation.sh` avvisa su un `.include` relativo. Se vedi
    quell'avviso hai sbagliato la metà lettura della convenzione.

FATTO QUANDO

  - ogni deck toccato è stato ESEGUITO davvero con
    `/bin/zsh scripts/run_simulation.sh <deck> results/preamp/<nome>`,
    exit code 0, nessun "could not find include" nel log — verificato con
    ls e grep, non dedotto
  - il CSV e il JSON esistono, NON sono vuoti, e il numero di righe è
    quello che ti aspetti dal tipo di analisi. Se non lo è, capisci
    perché prima di andare avanti
  - i numeri dei deck già esistenti non cambiano: `wrdata` è additivo,
    quindi qualunque scostamento è un errore tuo. Il modo di controllarlo
    è quello di L3: eseguire prima della modifica e confrontare i log
  - `/bin/zsh scripts/run_tests.sh` resta 5 passed, 0 failed

NON FA PARTE DI L4: i 5-6 deck con `destroy all` (è L5), il `REPO`
cablato in `circuits/preamp/gain_block.py` (è L3b, e va fatto prima della
Fase 4, non ora), e toccare il circuito.

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
  - CHIUSURA. Non è più una lista da ricordare, è uno script che
    rifiuta. Nell'ordine:
      1. aggiorna `docs/preamp/STATE.md` segnando **L4 fatto** e L5
         prossimo (la tabella dei lotti deve dire `**fatto**`)
      2. riscrivi QUESTO file per **L5** — se il titolo nomina ancora L4,
         lo script rifiuta, ed è il controllo che esiste apposta
      3. committa, pusha, apri la PR
      4. `/bin/zsh scripts/chunk_close.sh L4`
         Verifica tutto, merghia, riallinea il checkout dell'utente e
         **rilegge da lì** per provare il riallineo. Se rifiuta, ha
         ragione: sistema e rilancia.
      5. rimuovi il worktree con i due comandi che lo script stampa
      6. fermati. Non iniziare L5.
