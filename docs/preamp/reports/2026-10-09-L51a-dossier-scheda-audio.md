# L51a — il dossier rigenerato, la scheda audio

Data: 2026-10-09 · Lotto: L51a (la prima delle tre parti di L51) · Decisioni: **ADR-066** (la
riga «Dettagli» di PR-14). Dati: `data/2026-10-09/L51a/` (README).

## In breve

- **Le scelte dell'utente all'inizio**, chieste coi numeri: **«Tre parti»** (L51a la scheda
  audio, L51b l'alimentatore e il firmware, L51c le schede di prova, «Cosa non dice», le righe di
  stato restanti); la riga «Dettagli» di PR-14 **«Aggiornare la riga Dettagli»**, poi **«Rimando
  e limite»**; le righe `Stato:` **«Una per una, con la mia frase»**. Le cinque che bloccavano il
  generatore sono state portate una per una (sotto); alla frase per il contratto (ADR-053):
  «non é comprensibile, rendiamola umanamente chiara», poi «Sì, così».
- **Il generatore non girava su `main` da L47c1**, per tre ragioni indipendenti: il controllo
  del contratto rifiutava (ADR-065 non era nell'indice; ADR-042, 053, 058, 059, 060 col file
  diverso dall'indice o con uno stato che nominava decisioni più vecchie); il convertitore
  markdown non sapeva leggere le «Voci cambiate dopo la firma» in testa al PRB; un deck che
  leggeva non esiste più (`tb_e3_e5_ldr.cir`). E i dati che leggeva erano del circuito di L28.
- **La ricorsa**: i 21 deck veloci, il selettore e le due copie col bilanciamento, il 2026-10-09
  sul circuito di oggi (fermo da L48b): **252 file su 252 uguali** alla corsa di L48b (L48a per il
  selettore), 24 deck, nessun rc ≠ 0. Il deck V2 rigenerato dal sorgente è uguale byte per byte a
  quello versionato. Le celle peggiori del mute rifatte: 21 corse, tutte finite con rc 0 e sotto la guardia di L47b2b1; le 198 righe dell'analisi uguali a quelle di L48b per le stesse celle.
- **Due difetti del generatore, trovati rigenerando e corretti** (codice del dossier, non del
  circuito):
  1. **la provenienza leggeva KF = 0 su MMBT5401, MMBT5551 e sui due MJE**, che da L44 portano il
     tetto di ADR-057: chiudeva la `.model` alla prima riga di commento (ngspice no, e L44 ha messo
     la riga `+ KF=1e-13` dopo il proprio commento), e prendeva il primo KF invece dell'ultimo (i
     MJE hanno `KF=0` nel blocco del costruttore). Il dossier avrebbe detto «1/f solo sull'LS352»;
  2. **la pagina autoconsistente** (`--standalone`, quella che `stampa_a4.py` stampa) incorporava
     le figure lette dai file su disco **prima** che il generatore li riscrivesse: le figure della
     corsa precedente.
- **La pagina di L51a ha solo la scheda audio**: le sezioni dell'alimentatore, il calore e «Cosa
  non dice» escono finché L51b e L51c non le rigenerano (`PARTI`), e il generatore non scrive
  niente accanto a sé: `index.html` resta quello di L42 fino a L51c. **Il calore va a L51b**: la
  stima di L30 somma l'alimentatore, e ha quattro voci superate.
- **Le cifre di oggi**, tutte lette dai dati: V1 ≥ **64,42°** (il blocco B con la sorgente del
  bilanciamento); E3 **108,2 kΩ**; E5 ≤ **5,60 µV** col bilanciamento girato di 3 dB, col rumore
  1/f al tetto di ADR-057 (un limite per eccesso); F1 **19,8 µV** con sorgenti fino a 100 mV di
  continua, il limite a **~0,67 V**; V2 del mute **250 verdetti su 250**, il clic al più **+5,19 dB**
  sopra il taglio ideale; il passo del volume ≤ **48 nV**; PSRR peggiore 78,5 dB a 10 kHz; E4
  60,08 Ω; P7 Tj ≤ 82,7 °C.
- **Sabotaggi**: **27 su 27** (`L51a/sabotaggi.txt`); il primo giro ne ha fatti passare uno, e ha trovato un buco: la corsa di L36 si leggeva con `src()` e non passava dalla guardia del giorno. Corretto, poi 27 su 27.

## Il contratto, prima di tutto

Il controllo del punto 14 rifiutava sei volte. Le righe `Stato:`, portate all'utente una per una,
scritte uguali nel file e nella cella dell'indice (`decisions/README.md`, regola 2):

| ADR | Prima (file) | Dopo | Risposta |
|---|---|---|---|
| 058, la cella NSL-32SR3 | «supera in parte ADR-038 e ADR-039 sulla sola parte» (indice: «accettata») | superata da ADR-062 (il mute taglia coi soli relè: la cella è tolta) | «Sì, questa frase» |
| 059, il JFET scartato e i 3 s | «conferma ADR-058; precisa ADR-039 e ADR-040 …» | superata da ADR-062 (niente sfumatura; la prova del JFET resta come esito) | «Sì, questa frase» |
| 060, la cima a 7 mA | «supera il punto 1 di ADR-050 …; precisa ADR-058 …» | superata da ADR-062 (niente celle, niente LED da pilotare) | «Sì, questa frase» |
| 042, il Miller da 1 nF | «accettata» (l'indice era già aggiornato) | il testo dell'indice: il Miller e R128 superati da ADR-054; la corrente d'uscita ~20 mA resta | «Sì, il testo dell'indice» |
| 053, il PRB | «accettata» | dopo la firma alcune voci sono cambiate, ognuna con la sua decisione: V4 (ADR-055), il mute (ADR-062), il volume e i canali (ADR-065), il selettore (ADR-066) | «Sì, così», dopo «rendiamola umanamente chiara» |

Una ADR non può nominare nel suo stato decisioni più vecchie (punto 14, d): per questo le tre del
mute con le celle passano a «superata da ADR-062», e quello che dicevano delle decisioni prima di
loro resta nel loro testo. ADR-065 non era nell'indice: aggiunta, con lo stato del file
(«accettata») e un titolo dalle cifre di L48b. **ADR-066** cambia la sola riga «Dettagli» di PR-14:

> *Dettagli: F1, V2 · ADR-053, ADR-064, ADR-066 · regge con sorgenti fino a ~0,65 V di continua.*

La «~0,65 V» è quella di ADR-064, arrotondata per difetto; il dossier la ricalcola dalla tabella
del selettore (gradino di fondo più ~120 µV per volt di continua al principale a +10 dB) e ottiene
~0,67 V. Una correzione mia, detta all'utente durante la sessione: nella domanda avevo scritto che
la prova del selettore dava «≤ 100 µV»; è vero fino a ~0,65 V di continua della sorgente, non oltre.

Restano per L51c: ADR-009 (il volume a scatti superato da ADR-065), 027 (precisata da ADR-065),
032 e 062 (precisate da ADR-063), 038, 039, 040, 061 (superate da ADR-062), 049 e 050 (il pilota
delle LDR superato da ADR-062).

## La ricorsa e la seconda strada

`script/ricorsa.sh dopo`: i 21 deck della regressione di L48b, `tb_f1_selettore.cir` e le due copie
di L48b col bilanciamento, con `run_simulation.sh`. `script/confronta.py`: ogni CSV contro la sua
seconda strada, **252 su 252 uguali byte per byte**. Il generatore rifà lo stesso confronto, e in
più ogni riga di risultato dei log (13 064) contro la corsa di L48b.

Il mute: la matrice di L48b (155 corse, 250 verdetti, 108 grandezze dichiarate) si ricalcola con la
regola di `verdetto.py` di L47c2b1 scritta di nuovo nel generatore, e coincide con `verdetto.csv`
riga per riga. La seconda strada sono **21 corse** rifatte oggi sul deck versionato (`script/mute.sh`):
le celle peggiori dei gruppi 1, 2, 3, 5, 6 e il clic a 1 kHz, coi loro riferimenti.
21 corse, tutte finite con rc 0 e sotto la guardia di L47b2b1; le 198 righe dell'analisi uguali a quelle di L48b per le stesse celle. **Non rifatte**: B2g e B1 del gruppo 4 a 20 kHz (`mev_20k_iii`,
`g10sempre_20k_iii`), che in L48b hanno richiesto da sette a oltre quaranta ore di corsa; la
pagina lo dice per nome, e restano a una sola strada.

## Le sezioni

Nuove: **il selettore** (F1 sul banco, la rete di ogni ingresso letta dal 2e sulla netlist) e
**il volume col bilanciamento** (gli scatti del banco di L48b, `analizza.py` rieseguito uguale
byte per byte; V1 con le sorgenti del bilanciamento; E5 girato di 3 dB; C_T e R_G dal 2e).
Riscritte: il mute (soli relè, la matrice senza S, la tabella del clic, il gruppo 6 col difetto
noto del banco tolto: 9,2 nV); i punti di lavoro (la frase di NC-041 «il trim sta dopo il
condensatore d'uscita del blocco A» è sostituita da quella vera: la continua del blocco A,
−6,62 mV, attraversa il trim e C_T la ferma prima del volume); il trim con E3 al jack; i falsi del
2e (L48a e L48b, il 2e di oggi, al posto di quelli di L35 e L36); il rumore (il tetto di ADR-057,
non più «pavimento, NC-004»); il riquadro iniziale. La figura del profilo del mute è tolta: il mute
taglia, non c'è un profilo. I dati più vecchi del circuito di oggi sono rifiutati, tranne tre
eccezioni stampate nella pagina con la loro ragione (la corsa di L36, il selettore e i falsi di
L48a).

## Trovato, per gli altri lotti

- **Il calore** (L51b): `stima_telaio.py` di L30 scrive 7,94 W per gli otto blocchi da
  15 V × (32,6 + 33,6) mA; `tb_op` di oggi dà 36,70 + 37,72 mA (il VAS di ADR-054), cioè ~8,9 W;
  e le voci delle LDR, delle bobine a 5 V e del regolatore di `VRELAY` sono di prima di L41a,
  L47c1 e L48a. Rifarla è una misura nuova: all'utente in L51b.
- **La distorsione** (L51c): il dossier dice «nessuna cifra di distorsione misurata in questa
  pagina». Le cifre di L46a/L46b sono sul banco del blocco, e i modelli sono cambiati dopo (il KF
  di L44, che non tocca la distorsione): da verificare prima di citarle.

## Verifica

- `build_dossier.py --standalone <fuori dal repo>`: esce 0, «tutti i controlli incrociati sono passati», nessun file scritto nel repo (la pagina ha la sola parte audio).
- `run_tests.sh`: **13 passed / 0 failed**.
- `script/sabotaggi.py`: **27 su 27** (`L51a/sabotaggi.txt`); il primo giro ne ha fatti passare uno, e ha trovato un buco: la corsa di L36 si leggeva con `src()` e non passava dalla guardia del giorno. Corretto, poi 27 su 27.
