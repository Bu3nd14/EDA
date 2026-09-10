# Prompt per la sessione successiva — L25

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L25** —
e si ferma. Non iniziarne un secondo.

## Cosa è cambiato, e perché il prossimo lotto è la promozione dei modelli

Il lotto precedente, **L22 + L23**, ha chiuso lo specchio d'ingresso. Tre
risultati cambiano il quadro:

- **il THAT320 è uscito dal progetto.** Al suo posto c'è un **Linear Systems
  LS352**, dual PNP monolitico in SOIC-8, congelato con provenienza,
  controllato contro il proprio datasheet e montato nella topologia. Deciso in
  **ADR-018**;
- **una bloccante in meno per la prima volta da G0.** NC-015 e NC-016 sono
  chiuse: **18 voci, 5 bloccanti**;
- **lo stadio d'ingresso è più silenzioso di prima** — caso peggiore da 5,697
  a **4,231 µV** — nonostante il dispositivo nuovo sia 2,2× più rumoroso di
  quello vecchio. La differenza l'ha fatta la degenerazione portata da 47 a
  **220 Ω**, spazzata e non argomentata.

Conseguenza: di **NC-017** (bloccante) resta solo la promozione in `models/`
dei cinque modelli che L24 ha congelato. È lavoro da **eseguire**, non da
scoprire — il controllo incrociato contro i datasheet è già fatto.

## Leggi PRIMA, in quest'ordine, e non saltare

1. `CLAUDE.md` — ambiente, percorsi assoluti, trappole che falliscono in
   silenzio, e la regola di fine sessione (push prima di tutto)
2. `docs/preamp/STATE.md` — la sezione «Come si lavora da qui», la tabella dei
   lotti, la sezione **L22 + L23**, e «Prossimo passo concreto», che contiene
   il mandato di questo lotto per esteso
3. `docs/preamp/decisions/ADR-016-modello-vendor-e-ciclo-di-vita.md` — le due
   regole T7 e T8, il perché coi numeri, e cosa costano
4. `docs/preamp/decisions/ADR-017-dispositivi-attivi-conformi-a-t7.md` — le
   cinque parti da promuovere, con i loro verdetti già misurati
5. `docs/preamp/reports/2026-09-10-L22-L23-specchio-ingresso.md` — non per la
   parte, che è chiusa, ma per il **metodo**: la ricetta di regressione, il
   difetto che ha trovato in sé stessa, e la trappola nuova
6. `docs/limitations.md` — prima di scrivere codice, in particolare **#17,
   #18, #19, #20 e #21**

## IL LOTTO: L25 — i cinque modelli entrano in `models/`

Chiude quel che resta di **NC-017** (bloccante).

MMBT5401, MMBT5551, MJE15032, MJE15033, 1N4148. Per ciascuno:

1. **il file `.lib` in `models/<classe>/`**, derivato dal file già congelato in
   `vendor/`, con l'intestazione che racconta provenienza, differenze dal testo
   vendor e verdetto — il modello è `models/bjt_pnp/ls350.lib` (L22) o
   `models/jfet/lsk489.lib` (L6);
2. **la sua `.provenance.json`**, con `origin: "vendor_derived"`,
   `vendor_source_path` e `vendor_source_sha256` che devono corrispondere
   all'hash congelato — `validate_models.py --check-provenance` li ri-hasha
   davvero;
3. **una ricetta in `scripts/validate_models.py`** che **blocca i numeri** già
   misurati in L24, così che una modifica silenziosa faccia diventare rossa la
   suite.

## Cosa L22 ti consegna — usalo invece di riscoprirlo

Sono fatti verificati, ognuno col comando che lo falsifica.

- **Il precedente da copiare è `tb_ls350()`**, in `scripts/validate_models.py`.
  È il più recente e copre due dei cinque per device class.
- **La ricetta deve interpolare come fa `meas`**, non prendere il campione che
  attraversa la soglia. In L22 la differenza valeva lo 0,7% sull'h_FE — cioè il
  passo dello sweep, non il modello — e avrebbe fatto fallire il controllo per
  la ragione sbagliata. È annotato nel codice.
- **Le condizioni sono quelle del datasheet, con `set temp = 25`.** ngspice
  gira a 27, e con `XTB` nel modello la differenza si vede su ogni h_FE.
- **Uno SKIP fa uscire `validate_models.py` con 1.** Un file in `models/`
  senza la sua ricetta rende rossa la suite: i cinque modelli e le cinque
  ricette vanno nello stesso lotto.
- **Il conteggio dei check è ora 28**, non 26 (L22 ha aggiunto provenienza +
  elettrico dell'LS350). Cinque modelli ne aggiungono dieci, e la
  documentazione che cita «26/26» va aggiornata dove compare.

## I verdetti già misurati che vanno bloccati, non ri-derivati

Da ADR-017 e dal report di L24, alle condizioni dei rispettivi datasheet,
25 °C:

| Parte | Misure |
|---|---|
| MMBT5401 | hFE 124,9 @ 10 mA · f_T 169,5 MHz · C_obo 3,706 pF — **sei su sei dentro** con l'altro |
| MMBT5551 | hFE 107,2 @ 10 mA · f_T 173,1 MHz · C_obo 2,221 pF |
| MJE15032 | hFE **66,4** a I_C = 0,5 A contro un **minimo di 70** — **fuori del 5,1%**, direzione pessimistica |
| MJE15033 | dentro a tutti e tre i punti |
| 1N4148 | V_F 0,766 V @ 10 mA (max 1,0) · C_T 0,869 pF (max 4,0) |

**Il MJE15032 fuori finestra va bloccato come tale**, non pareggiato: è la
stessa forma di NC-013 sull'LSK489 e di NC-020 sull'LS352. Una ricetta che
dichiarasse conformità dove non c'è sarebbe peggio di nessuna ricetta.

## Cosa NON accettare

- **un mirror di terze parti non conta.** ADR-016 lo scarta esplicitamente:
  si congela e si deriva da ciò che il **costruttore** ha servito;
- **il nome di un file non è la sua parte** (#20): onsemi serve `1n4148.lib`
  contenente `.SUBCKT 1N4148WT`, un'altra variante in un altro package. Il
  modello giusto è in `1n914.lib`. È già congelato correttamente — non
  "correggerlo";
- **`mfg=` è fatale in ngspice** e va tolto, ma **solo quello**: nessun valore
  va arrotondato, riordinato o "corretto";
- **una cifra non eseguita non è evidenza.** Se una ricetta dichiara un
  numero, quel numero deve uscire da una run.

## NON fa parte di questo lotto

- **Sostituire le parti nella topologia.** MMBT5401/MMBT5551 in
  `circuits/preamp/` è **Fase 4**. Questo lotto tocca `models/` e
  `scripts/validate_models.py`, non `circuits/`.
- **Rifare le misure del blocco.** PSRR, Z_out e risposta restano da rifare in
  Fase 4; i dati in `data/2026-09-09/` descrivono la topologia col THAT320,
  quelli in `data/2026-09-10/` lo stadio d'ingresso con l'LS352.
- **Le altre non conformità.** Hanno i loro lotti. Le cinque bloccanti:
  NC-001 (L11), NC-004, NC-010 (L17), NC-014 (**L21**, quasi gratis), NC-017
  (questo lotto + Fase 4).
- **Non toccare i file già in `vendor/`**: sono la traccia di controllo. Una
  correzione si aggiunge accanto come addendum — è quello che ha fatto L7 —
  non si riscrive l'originale.

## Come lavoriamo

- Verifica invece di fidarti. Se un subagente riporta dei numeri, rieseguili
  tu prima di riferirmeli.
- **Verifica alla fonte anche ciò che il lotto precedente ti ha scritto.** Un
  compito ereditato è un'ipotesi, non un dato — L24 lo ha dimostrato sulla
  conclusione di L8 riguardo a Diodes, e L22 lo ha rifatto su `mfg=`.
- Cerca se qualcuno ha già deciso, prima di aprire una voce.
- Niente cifre non eseguite.
- Diffida degli script che dichiarano di aver verificato qualcosa.
  `export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora `ROOT` cablato
  su `/Users/roberto/EDA`: eseguiti da un worktree leggono e scrivono nel
  checkout principale, in silenzio. Se il tuo lotto ne tocca uno, correggilo lì.
- Un lotto per volta, mai due agenti in parallelo: il vincolo è il cap di
  token del piano.
- **Lavora in un worktree.** I commit non pushati dentro `.claude/worktrees/`
  spariscono col worktree, ed è già successo.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto fatto e il successivo
   come prossimo (la tabella deve dire **fatto**)
2. riscrivi QUESTO file per il lotto successivo — se il titolo nomina ancora
   L25, lo script rifiuta, ed è il controllo che esiste apposta
3. committa, pusha, apri la PR
4. `/bin/zsh scripts/chunk_close.sh L25` — verifica tutto, merghia, riallinea
   il checkout dell'utente e **rilegge da lì** per provare il riallineo. Se
   rifiuta, ha ragione: sistema e rilancia
5. rimuovi il worktree con i due comandi che lo script stampa
6. **fermati.** Non iniziare il lotto dopo.
