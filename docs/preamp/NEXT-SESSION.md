# Prompt per la sessione successiva — L5

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L5,
e si ferma. Non iniziarne un secondo.

Leggi PRIMA, in quest'ordine, e non saltare:
  1. CLAUDE.md — ambiente, percorsi assoluti, trappole che falliscono in
     silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. docs/preamp/STATE.md — la sezione "Come si lavora da qui", la
     tabella dei lotti, il paragrafo "L2-L5 — i testbench diventano
     artefatti" **compreso il riquadro L4**, e soprattutto il riquadro
     "⚠ WARNING PER L5", che è il cuore di questo lotto
  3. spice/preamp/tb/tb_op.cir — il commento in testa È la convenzione di
     percorso. Non va riprogettata: va replicata
  4. spice/preamp/tb/tb_switch_v2_counterfactual.cir — il commento dentro
     il `.control` è il modello di come si documenta un `wrdata`:
     mappatura file→stato e **ordine delle colonne**
  5. docs/limitations.md — #10 (trappole di ngspice batch, incluso il
     plot vecchio letto in silenzio) e #13 (suffissi di valore)

Non serve rileggere le ADR: L5 non tocca il circuito.

Contesto in due righe: preamplificatore di linea a guadagno unitario,
Classe A pura a discreti senza operazionali, per sostituire un Technics
SU-9070 la cui struttura di guadagno sbagliata (46 dB di attenuazione
richiesta) è la causa misurabile della mancanza di dinamica lamentata.
La topologia canonica è in circuits/preamp/, i banchi di prova in
spice/preamp/tb/ (12 deck).

IL RAMO NON È PIÙ UN PROBLEMA. Da L3c ogni lotto si chiude mergiando e
riallineando il checkout principale, quindi **`main` è corrente e si
riparte sempre da lì**. Se `git -C /Users/roberto/EDA log --oneline -1`
non mostra L4, qualcosa è andato storto nella chiusura precedente:
risolvi quello prima di iniziare L5.

------------------------------------------------------------------
IL LOTTO: L5 — `wrdata` dentro i cicli, e un numero sbagliato da correggere
------------------------------------------------------------------

L'infrastruttura c'è tutta e non va ridiscussa:

  lettura   `.include @REPO@/<percorso-dalla-radice-del-repo>`
  scrittura `wrdata <nome-nudo>`, cioè un file dentro la directory dei
            risultati, senza percorso

`run_simulation.sh` sostituisce `@REPO@`, fa `cd "$OUTDIR"`, e da L3
converte in CSV/JSON **ogni** file wrdata prodotto da una run. Quel
secondo passaggio guarda i file **prodotti** e non il testo del deck,
proprio perché un nome dentro un `foreach` è parametrizzato e nessun grep
può ricavarlo: è la parte costruita apposta per questo lotto.

STATO DI PARTENZA: dopo L4 scrivono dati **6 deck su 12**. Restano **6
deck muti, tutti con `foreach`**, e sono tutti L5:

| Deck | Forma | Nota |
|---|---|---|
| `tb_bias_sweep` | `foreach` (7 × `op`), **nessun** `destroy all` | assegnato a L5 in L4, vedi sotto |
| `tb_noise_breakdown` | `foreach` + `destroy all` | |
| `tb_ac` | `foreach` doppio + `destroy all` | 2 modalità × 4 Z sorgente = 8 curve |
| `tb_loop` | `foreach` doppio + `destroy all` | |
| `tb_loop_blockA` | `foreach` + `destroy all` | |
| `tb_zout_psrr_noise` | quattro sezioni + `destroy all` | **porta anche la correzione qui sotto** |

LA REGOLA: dove c'è `destroy all` dentro il ciclo, il `wrdata` va
**dentro il ciclo, prima del `destroy all`**, con il nome parametrizzato.

`tb_bias_sweep` è finito qui, e non per prudenza: ogni `op` crea un plot
nuovo (`op1…op7`), quindi un `wrdata` **fuori** dal ciclo scriverebbe solo
la settima iterazione e la curva Iq(R130) — il senso del deck — andrebbe
persa. Serve un file per iterazione, più uno snapshot `let iq = @r136[i]`
perché un parametro di dispositivo non è un vettore del plot.

LA PRIMA DECISIONE DELLA SESSIONE: **la convenzione di nome per gli
output parametrizzati**, presa una volta sola per tutti e sei i deck. È
stata rimandata a qui apposta, per non deciderla su un deck solo.

------------------------------------------------------------------
⚠ WARNING PER L5 — un numero già stampato oggi è sbagliato
------------------------------------------------------------------

Copiato da STATE.md, dove sta per esteso. **`tb_zout_psrr_noise.cir`
riporta un rumore di caso peggiore sbagliato di un fattore 3,4, e lo fa
in silenzio.** Trovato il 2026-09-09 rispondendo a una domanda sullo
stato delle misure, non cercandolo.

La riga finale del deck, `RRG=0.1 RSRC=2500 ... WORST CASE`, stampa
**1,676 µV** — che è *identico* al valore "intrinsic" della riga
precedente — invece di **5,697 µV**.

**Causa**: in coda a quel deck mancano i `destroy all` che invece ci sono
dentro i `foreach`. Ogni analisi crea plot numerati, quindi la seconda
`noise` produce `noise3`/`noise4` e il `setplot noise2` continua a
selezionare il plot della **prima**. Vedi `docs/limitations.md` #10.

**Provato su tre gambe, non dedotto:**

1. `alter` funziona in quel deck — il `foreach` sopra dà 1,718 µV e
   5,070 µV per le due modalità, quindi non è `alter` a non avere effetto;
2. `tb_noise_breakdown.cir` misura la **stessa** configurazione con
   `destroy all` e dà **5,696897e-06**;
3. aggiungendo `destroy all` a una copia di scratch dello stesso deck la
   riga diventa **5,696896e-06** — coincide a sette cifre. Il rimedio è
   verificato.

**Cosa deve fare L5**: oltre ad aggiungere i `wrdata`, **correggere quella
coda** e ricontrollare che le due righe finali tornino diverse. E stare
attento al caso generale: ogni `wrdata` piazzato dopo un'analisi ripetuta
senza `destroy all` scriverà i dati del plot **sbagliato** — lo stesso
guasto, ma dentro un file che poi finisce nel dossier.

------------------------------------------------------------------
DUE REGOLE EREDITATE DA L4, non da riscoprire
------------------------------------------------------------------

1. **L'identità delle colonne esiste solo nel deck.**
   `run_simulation.sh` intesta i CSV `col0…colN`, punto. Quindi ogni riga
   `wrdata` non banale vuole sopra di sé un commento con l'ordine delle
   colonne. Il modello è dentro `tb_switch_v2_counterfactual.cir`.
2. **Si scrivono i vettori scelti, non `all`.** In `tb_noise_vectors`
   `print all` elencava **172** vettori: scriverli tutti dà 344 colonne
   intestate `colN`, cioè un file che nessuno può più interpretare. Si
   scrivono i totali più i contributori dominanti, e **solo i totali per
   dispositivo** — `onoise_q123_rb` accanto a `onoise_q123` conta due
   volte.

E una forma da conoscere: un `wrdata` da un `.op` scrive **una riga** e,
per ogni vettore, una **coppia** di colonne `(scale, valore)`. Lo *scale*
di un plot `op` è un vettore arbitrario e **non significa niente**: i dati
sono le colonne **dispari**. Per un `ac`/`noise`/`tran` la colonna pari è
invece l'asse vero (frequenza o tempo) ripetuto.

DOVE FINISCONO I DATI (deciso in L3c)

`results/` resta scratch e gitignorato. Ma **i dati del dossier sono
versionati**, perché il gate gira offline su `main` e deve poter aprire i
numeri. Se un CSV prodotto in L5 è materiale da dossier — e in L5 lo sarà,
perché qui escono risposta in frequenza, guadagno d'anello, PSRR e Z_out,
cioè i grafici che il dossier deve impaginare — copialo in

```
docs/preamp/data/<YYYY-MM-DD>/<nome>.csv   (+ .json, + il .log come evidenza)
```

con un `README.md` accanto che porti **la legenda delle colonne**: senza,
un CSV intestato `colN` non è interpretabile da chi apre il dossier. Il
modello è `docs/preamp/data/2026-09-09/README.md`, scritto in L4. La
convenzione per esteso è in `docs/preamp/data/README.md`.

Attenzione: il `.gitignore` ha regole globali `*.log`/`*_out.txt`/`*.raw`
neutralizzate lì dentro da una negazione — dopo la copia metti i file in
staging e guarda lo stato del repo per **vedere** che siano sopravvissuti.

Cautela di merito, non di forma: i modelli sono **segnaposto**. Il rumore
e la distorsione che escono da questi deck non sono cifre credibili e non
vanno presentate come tali; lo diventeranno dopo L6-L7. I risultati in
continua e la **forma** delle risposte in frequenza sì.

FATTO QUANDO

  - ogni deck toccato è stato ESEGUITO davvero con
    `/bin/zsh scripts/run_simulation.sh <deck> results/preamp/<nome>`,
    exit code 0, nessun "could not find include" nel log — verificato con
    ls e grep, non dedotto
  - il numero di file prodotti è quello che il ciclo promette (8 curve da
    `tb_ac`, 7 punti da `tb_bias_sweep`, …), i CSV non sono vuoti e il
    numero di righe è quello atteso dal tipo di analisi
  - la riga WORST CASE di `tb_zout_psrr_noise.cir` stampa **5,697 µV** e
    non più 1,676 µV, e le due righe finali sono diverse fra loro
  - i numeri dei deck già esistenti non cambiano: `wrdata` è additivo,
    quindi qualunque scostamento è un errore tuo. Il modo di controllarlo
    è quello di L3/L4: eseguire PRIMA della modifica, conservare i log,
    e confrontarli dopo ignorando i timestamp
  - `/bin/zsh scripts/run_tests.sh` resta 5 passed, 0 failed

NON FA PARTE DI L5: toccare il circuito. La topologia sta solo in
`circuits/preamp/*.py` e L5 non la sfiora.

(Il `REPO` cablato in `gain_block.py` non è più un problema: quella era
L3b, chiusa il 2026-09-09 subito prima di L5. Il circuito ora si rigenera
nel checkout corrente, verificato rieseguendo davvero i due generatori.
Una cosa da sapere se ti capita di guardare quegli artefatti: **un `.net`
di SKiDL non è riproducibile byte a byte** — data, tag casuali e UUID
cambiano a ogni esecuzione — quindi un diff grezzo su un `.net`
rigenerato non dice se la topologia è cambiata. Il dettaglio è nella
sezione L3b di `STATE.md`.)

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
  - CHIUSURA. Non è una lista da ricordare, è uno script che rifiuta.
    Nell'ordine:
      1. aggiorna `docs/preamp/STATE.md` segnando **L5 fatto** e il lotto
         successivo come prossimo (la tabella deve dire `**fatto**`)
      2. riscrivi QUESTO file per il lotto successivo — se il titolo
         nomina ancora L5, lo script rifiuta, ed è il controllo che
         esiste apposta
      3. committa, pusha, apri la PR
      4. `/bin/zsh scripts/chunk_close.sh L5`
         Verifica tutto, merghia, riallinea il checkout dell'utente e
         **rilegge da lì** per provare il riallineo. Se rifiuta, ha
         ragione: sistema e rilancia.
      5. rimuovi il worktree con i due comandi che lo script stampa
      6. fermati. Non iniziare il lotto dopo.
