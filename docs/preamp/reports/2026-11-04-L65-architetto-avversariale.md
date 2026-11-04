# 2026-11-04 — L65, revisione dell'architetto avversariale

**Suona bene: regge con riserve.** La struttura di guadagno, il rumore (5,43 µV, circa 8 dB SPL a 1 m), la stabilità (minimo 64,11°) e il carattere della distorsione di modello sono solidi. Restano aperte tre cose: il ronzio d'anello (NC-044), il dielettrico e le impronte dei condensatori di segnale (R2), l'equilibrio dei canali con le resistenze all'1 % (R6).

**Nessun bump fastidioso: regge.** V2 dà 250 verdetti su 250, il peggiore a 82,3 µV (31,8 dB SPL). Il cambio d'ingresso fa 19,8 µV (19,4 dB SPL). Lo spegnimento dal frontale fa 3,7 nV, la perdita di rete al più 3,5 µV (4,3 dB SPL). Fuori dal contratto restano il cavo collegato a caldo e i colpi delle sorgenti sulle fisse (vedi le omissioni).

**Fallisce senza danneggiare: regge con riserve.** Sulla Stax la soglia di 0,87 V viene dalla catena delle Heresy, non dalla Stax (R5). La protezione della principale è motivata con un meccanismo sbagliato, anche se la conclusione probabilmente tiene (R7).

---

## Che cosa ho letto, che cosa ho rieseguito

**Fase 1, cieca:**
- `PRB.md`, `REQUIREMENTS.md`, l'indice delle ADR e per intero ADR-007, ADR-103, i «Da riaprire se» di ADR-023, 034, 065 e 102;
- il dossier `docs/preamp/dossier/index.html`, convertito in testo e letto per intero;
- `circuits/preamp/gain_block.py` e `preamp_audio.py` per intero, `psu.py` in parte (testata, regolatore +, fusibili, terra);
- la netlist `preamp_audio.net`, per le impronte;
- il datasheet Omron G6K in `vendor/`.

**Fase 2, a rilievi scritti:** `NONCOMPLIANCE.md`, cioè le voci aperte, gli stati, NC-044, NC-046, NC-048 e il contesto di NC-042; poi le righe di `STATE.md` su G1 e sui lotti. Non ho letto `STATE-STORIA.md`, `NEXT-SESSION.md` né i report. Nessun rilievo della fase 1 è stato tolto o ammorbidito: ho solo aggiunto le note di fase 2.

**Bash era consentito.** Ho scritto solo in `/Users/roberto/.claude/jobs/9cc1317d/tmp/l65/`.

**Rieseguito con ngspice** (`nice -n 10`, tre corse insieme). Il banco della THD a 20 kHz è quello del dossier (`data/2026-11-02/L64a/distorsione/deck/oggi/thd_20k.cir`), modo 0 dB, blocco di oggi:
- così com'è: **0,000446 %** a 0,2 V e **0,00449 %** a 2 V. Il dossier dice 0,000447 / 0,00449 %: coincide;
- con **100 nF** fra NX e NY: 0,000446 / 0,00448 %;
- con **100 µF** fra NX e NY: 0,000448 / 0,00450 %.

**Calcolato** (Python, solo stdlib):
- i tempi e la risposta a 20 Hz della Stax al variare del condensatore;
- lo squilibrio dei canali nel caso peggiore con resistenze all'1 %;
- le conversioni in dB SPL (finale ×21,1, 96 dB con 2,83 V).

**Calcolato a mano:** C_T contro E9, e la stabilità termica del moltiplicatore.

**Letto dal dossier, non rieseguito:** tutte le altre cifre.

---

## Il prototipo: le tre domande dell'utente

### 1. Che cosa è ancora affidato di fatto al prototipo, oltre al suono

**Verifiche rinviate per scritto:**
- E10 col volume: l'RK27 «si verifica al prototipo sul potenziometro montato».
- E11, la diafonia: «al layout e sul prototipo».
- P5: 57,7 °C contro 60 °C, con 1,95 W di ferro ipotizzati. Il margine è 2,3 °C, circa 2 W.
- NC-037: le perdite a vuoto di T2 «si leggono sul pezzo».
- NC-011: il rumore e il ripple dei rail.
- V4: il tetto di THD+N «da fissare sulle prime misure».
- La lettura di R585 in circuito (DIAGNOSI).

**Cifre solo di modello che decidono il funzionamento:**
- Nell'alimentatore, i regolatori e i comparatori sono comportamentali. Il comparatore è tarato sul modello di TI, che sul banco non passa l'accensione (ADR-103).
- I 2N7002 del comando del mute e i MOSFET hanno un modello generico scritto a mano.
- T1 e T2 sono generatori ideali con R e L in serie.
- La dinamica delle bobine dei relè è dichiarata, non del costruttore.
- V1 è misurato ai valori nominali, non agli spigoli di tolleranza: lo dice il dossier, sezione 30.

**Tarature:** R128/R129 del moltiplicatore sono «SELECT-ON-TEST on the bench», e il sorgente aggiunge: «if the bench disagrees, the classic remedy is a capacitor across NX-NY» (`gain_block.py`, sezione 4).

**Scelte di parti non chiuse:**
- la lista ammessa dei condensatori di P6/E12, che non esiste;
- le resistenze del guadagno e del trim (tolleranza non scritta);
- le parti di R550/R551 e della cella RC (NC-073, NC-075);
- T1 e T2;
- il rame dei regolatori (NC-072).

**Il fisico:**
- Le schede non sono sbrogliate sul circuito di oggi: 653 parti contro le 458 dell'ultima prova (dossier, sezione 30).
- La massa audio verso la terra non è decisa (NC-044).

### 2. I difetti che solo il prototipo rivelerebbe, e che non si correggono cambiando un condensatore d'accoppiamento

| Difetto | Probabilità | Che cosa lo toglie prima | Costo |
|---|---|---|---|
| La scheda audio non entra nel contenitore di P8, oppure ci entra solo togliendo blocchi (R1) | media | il piazzamento di prova sul circuito di oggi, come L49a | un lotto |
| I condensatori di segnale in polipropilene (ADR-007) non entrano nelle impronte, che sono quelle del poliestere; senza zoccoli si cambiano solo dissaldando (R2) | alta, se si monta il polipropilene | scegliere ora i pezzi della lista ammessa; impronte sul pezzo più grande, a passi multipli o con zoccoli a tulipano | un giro di distinta, ore |
| Ronzio d'anello sulle trombe: si rifà il cablaggio di terra, o si aggiunge una rete di separazione sulla scheda (NC-044) | media-alta | la decisione di NC-044 e l'impronta della rete 10 Ω ∥ C ∥ ponte di diodi | una decisione e 4 parti |
| Canali oltre 0,2 dB con le resistenze all'1 % (R6) | media | lo 0,1 % su 6 posizioni per canale, nella distinta | nullo |
| Standby oltre 0,5 W: secondo ADR-103 servono 4 parti in più | bassa-media | scegliere T2 e leggerne le perdite a vuoto, oppure rilassare PR-25 | un datasheet |
| Corrente di riposo o quasi-saturazione del moltiplicatore: R o C da aggiungere | bassa | un'impronta vuota per un C fra NX e NY. Rieseguito: è neutro sulla distorsione di modello | nullo |
| Temporizzatore all'accensione coi pezzi veri (comparatori sotto 2,2 V, 2N7002) | bassa (700 corse di Monte Carlo, angoli a 0 / 25 / 60 °C) | il modello del costruttore del 2N7002 nei banchi delle sequenze, come già fatto per BC847 e BAT54 | ore |
| Calore del telaio oltre 60 °C | bassa | non serve cambiare la scheda: feritoie | — |
| Tracciamento dell'RK27 oltre 3 dB | media | non serve cambiare la scheda: il potenziometro è un pezzo di pannello | — |

### 3. I condensatori d'accoppiamento: sono gli unici punti di regolazione, e si cambiano davvero?

**I condensatori di oggi** (netlist `preamp_audio.net`):

| Riferimenti | Ruolo | Valore e tipo | Impronta oggi | ADR | Finestra ammessa (calcolo mio, salvo nota) |
|---|---|---|---|---|---|
| C171–C174, C371–C374 | ingresso, uno per ingresso | 1 µF PP | `C_Rect_L16.5mm_W7.0mm_P15.00mm_MKT` | ADR-064 | E9 non vincola. La perdita del condensatore fissa il limite di PR-14 (~0,67 V col poliestere peggiore), e il limite scende in proporzione a C |
| C265, C465 | C_T, fra trim e volume | 10 µF PP | `…L31.5mm_W17.0mm_P27.50mm_MKS4` | ADR-065 | **non sotto ~10 µF**: a 4,7 µF su ~8 kΩ fa 0,19 dB a 20 Hz da solo, ed E9 è ±0,2 dB |
| C262, C462 | uscita principale | 4,7 µF PP | `…L26.5mm_W10.5mm_P22.50mm_MKS4` | ADR-007 | libero verso l'alto; verso il basso fino a ~2,2 µF col cj da 100 kΩ |
| C162, C362 | fissa 1, Singxer | 4,7 µF PP | `…P15.00mm_MKT` | ADR-007 | ≥ 4,7 µF: l'impedenza d'ingresso del Singxer è ignota |
| C165, C365 | fissa 2, Stax | 1 µF PP ±5 % | **la stessa impronta di C162** | ADR-081, 084, 086 | **bloccato a ~0,97–1,2 µF**: sotto cade E9, sopra cade PR-30 (R3) |

**Che cosa sposta il cambio:**
- I colpi di V2 non si spostano. Con la geometria iii il lato del condensatore è a massa in mute: il valore non cambia i gradini A, B e B1.
- Si spostano invece il clic al rilascio a 20 Hz (dichiarato), le durate di P10 sulla principale (dichiarate) e quelle sulla Stax.
- Si sposta la continua al jack (PR-11): la perdita del dielettrico per lo scarico.

**Si possono sostituire senza rifare la scheda? Oggi no:**
- nessuna impronta ha uno zoccolo, e PR-12 dice «senza dissaldare»;
- un unico passo per posizione, e P6 dice «passi multipli»;
- le impronte sono quelle del poliestere (R2).

**Non sono gli unici punti dove il suono si regola:**
- **Il volume e il bilanciamento** sono pezzi di pannello, sostituibili senza toccare la scheda. Sono probabilmente il punto più sensibile all'ascolto.
- **Il limitatore d'ingresso** (BAV199 con 1 kΩ, ADR-101) costa 0,9 dB di THD a 20 kHz.
- **C124 (470 pF) e C_f (330 pF)** non vanno toccati: reggono V1.

---

## I rilievi, dal più grave

### R1 — La fattibilità fisica non è verificata sul circuito di oggi

- **Voce:** PR-27, P8; NC-048.
- **Il rilievo:** la chiusura di NC-048 non vale più. Fu fatta su 458 parti della scheda audio, e oggi sono 653: 195 aggiunte e 67 valori cambiati.
- **Evidenza:** il dossier stesso, sezione 30, dice che le prove di L49a/L49b «non sono più il progetto». Da allora sono entrati:
  - sedici dissipatori WA-T220-101E al potenziale di collettore, che non devono toccarsi;
  - le parti di ridondanza e di limitazione in otto blocchi;
  - il limitatore d'ingresso;
  - i test point;
  - e, se R2 si risolve col polipropilene, condensatori di segnale molto più grandi (un 4,7 µF / 250 V misura 31,5 × 15 × 26 mm).
- **Severità proposta: bloccante per G1.** È la regola che l'utente stesso diede a NC-048 il 2026-10-01: «un problema di spazio scoperto al layout rimanda al progetto, quindi va scoperto prima di congelare la topologia».
- **Fase 2:** già noto (NC-048), chiusa il 2026-10-09 su un circuito che non c'è più. Va riaperta.

### R2 — I condensatori di segnale: impronte del poliestere, nessuno zoccolo, nessuna lista ammessa

- **Voce:** PR-12, PR-11, PR-8; P6, E12; ADR-007.
- **Il rilievo:** la promessa «dopo il prototipo si cambiano solo i condensatori d'accoppiamento» oggi non è costruibile. Ci sono tre ragioni:
  1. le impronte portano il nome e le misure delle serie in poliestere (MKT, MKS4), mentre ADR-007 e i commenti del sorgente chiedono il polipropilene;
  2. nessun zoccolo e un passo solo per posizione, contro il «senza dissaldare» di PR-12 e i «passi multipli» di P6;
  3. la lista ammessa, che P6 dice «il giro della distinta scrive qui accanto», non esiste.
- **Evidenza:**
  - la netlist mostra le impronte nella tabella qui sopra;
  - un polipropilene WIMA MKP4 da 4,7 µF / 250 V misura 31,5 × 15 × 26 mm a passo 27,5 (dato del distributore), contro l'impronta da 16,5 × 7 mm a passo 15 di C162/C362;
  - `gain_block.py` riga 101: «swap … with an iron, not a desoldering station», che non è «senza dissaldare»;
  - un `grep` di «zoccol», «socket», «lista ammessa» in sorgente e ADR non trova niente;
  - il dielettrico non è neutro: Self (AES) misura distorsione nei poliesteri quando sul condensatore cade una tensione di segnale significativa. Sulla Stax, 1 µF su 41,2 kΩ lascia a 20 Hz il 19 % del segnale ai capi del condensatore: lì serve il polipropilene, e V4 non lo vede perché il suo banco usa 4,7 µF ideali su 10 kΩ.
- **Severità proposta: maggiore.** Le finestre di valore della lista vanno scritte prima di G1, perché sono requisiti; le impronte e gli zoccoli prima di G2.
- **Fase 2:** nuovo.

### R3 — Il condensatore della Stax non è una variabile d'ascolto, e i requisiti dicono un altro valore

- **Voce:** PR-30, PR-9; E8, T5, P10; ADR-081, ADR-084.
- **Il rilievo:**
  - C165/C365 sono bloccati a ~0,97–1,2 µF;
  - hanno la stessa impronta del 4,7 µF del Singxer, quindi si possono montare scambiati senza che niente lo segnali;
  - E8 («4,7 µF su tutte e tre le uscite») e T5 («dopo ciascuno … 4,7 µF») contraddicono ancora ADR-081. Chi li segue rompe PR-30.
- **Evidenza (calcolo):** carico 50 kΩ ∥ 470 kΩ ∥ 470 kΩ = 41,2 kΩ, gradino da 14 V.

  | C | a 20 Hz | sopra 0,87 V |
  |---|---|---|
  | 0,90 µF | 0,195 dB | — |
  | 0,95 µF | 0,176 dB | — |
  | 1,00 µF | 0,159 dB | 115 ms (il dossier dà 111–123 ms) |
  | 1,50 µF | — | 172 ms |
  | 2,2 µF | — | 252 ms |
  | 4,7 µF | — | 538 ms |

  - Il guasto interno peggiore oggi è 124,5 ms al +5 % (dossier, sezione 20); scalato, un condensatore oltre ~1,26 µF supera i 150 ms.
  - Anche il dossier, sezione 6, attribuisce il polo col carico Stax-like al «condensatore d'uscita da 4,7 µF (E8)».
- **Severità proposta: maggiore.** Il testo di E8/T5 va corretto prima di G1; l'impronta va resa distinta (o la serigrafia marcata) prima di G2.
- **Fase 2:** nuovo. Il sorgente stesso avverte del montaggio scambiato («the assembly drawing must»), ma nessuna voce lo registra.

### R4 — Il ronzio d'anello e la messa a terra non sono decisi

- **Voce:** PR-5, PR-2; P4.
- **Il rilievo:** nessun requisito e nessuna decisione dicono come la massa audio incontra la terra di protezione. La catena ha cinque apparecchi a rete sbilanciati, fra cui una sorgente in classe II con alimentatore switching (il motivo stesso di ADR-101), e diffusori da 96 dB.
- **Evidenza:**
  - `psu.py` riga 334: «Protective earth goes from the IEC module to the chassis directly, not through this board», e nient'altro;
  - ESP «Earthing your hi-fi» raccomanda ~10 Ω ∥ C ∥ un ponte di diodi fra lo zero volt e il telaio;
  - E5 copre solo il rumore proprio e il ripple.
- **Severità proposta:** maggiore. Non serve prima di G1, ma va deciso prima della scheda del prototipo.
- **Fase 2:** già noto (**NC-044**, bloccante per G2, aperta dal 2026-09-27). La severità mi convince; il punto è che il prototipo non si fa senza.

### R5 — Il tetto di non-danno della Stax è quello delle Heresy

- **Voce:** PR-30; P10; ADR-081, ADR-086.
- **Il rilievo:** 0,87 V è il punto in cui il finale da 30 W arriva al clipping (~112 dB SPL). Non dice niente della Stax. L'SRM-T1 è riportato con 60 dB di guadagno (100 mV in ingresso per 100 V in uscita) e risposta da DC: è accoppiato in continua. A volume massimo l'energizzatore satura già con ~0,1–0,3 V in ingresso, e gli statori ricevono la saturazione in continua per tutto quel tempo.
- **Evidenza (calcolo, 1 µF):** sopra 0,87 V 115 ms; sopra 0,3 V 158 ms; sopra 0,1 V 204 ms. Al +5 %: 120 / 166 / 214 ms.
  - Se 150–210 ms di saturazione danneggino un'elettrostatica non lo sa nessuno: Stax non pubblica un limite.
  - Col volume dell'energizzatore a −20 dB la soglia equivalente sale a ~3 V e il tempo scende a ~63 ms.
- **Severità proposta: maggiore, prima di G1.** È una domanda all'utente: tenere 0,87 V e 150 ms dichiarando l'ipotesi, oppure riformulare PR-30 sulla Stax come «tempo in saturazione dell'energizzatore».
- **Fase 2:** già noto in parte (**NC-046**, minore, aperta). NC-042 è stata chiusa senza un tetto proprio delle fisse. La severità minore di NC-046 è bassa: oggi la metrica non governa più solo il fastidio, governa il criterio di danno di PR-30.

### R6 — L'equilibrio dei canali dipende da una tolleranza che nessuno ha scritto

- **Voce:** PR-10; E10.
- **Il rilievo:** E10 si «garantisce con la tolleranza delle parti», ma la tolleranza di R_F, R_G3, R_G10 e della scala del trim (845 / 464 / 464 Ω) non è fissata da nessuna parte.
- **Evidenza (calcolo, caso peggiore all'1 %):**
  - +10 dB: ±0,118 dB per canale, cioè **0,24 dB** fra i canali;
  - trim −12 dB: **0,26 dB** fra i canali;
  - insieme: **0,49 dB**, contro 0,2 dB;
  - lo 0,1 % lo toglie. Correggerlo dopo il prototipo vuol dire cambiare resistenze, non condensatori.
- **Severità proposta: maggiore** (costo nullo), prima di G2.
- **Fase 2:** nuovo.

### R7 — La principale «conta sul trasformatore del finale»: il meccanismo è sbagliato

- **Voce:** PR-30; P10; ADR-081.
- **Il rilievo:**
  - Un trasformatore d'uscita non blocca un gradino di 14–21 V con una costante di ~0,3 s: lo passa come transitorio di bassa frequenza.
  - Quello che limita davvero è la potenza: il finale da 30 W va in clipping a ~114 dB di picco, mentre la FMEA calcola 137–140 dB SPL «lineari» (righe Q132 e C145).
  - La conclusione regge se la potenza ammessa dalle Heresy supera 30 W. Non ho verificato il dato delle Heresy I.
- **Severità proposta:** minore, prima di G1. Va riscritta la motivazione, non il circuito.
- **Fase 2:** già deciso (ADR-081). La decisione mi convince, la motivazione no.

### R8 — Il moltiplicatore di Vbe: lavoro da banco che si può togliere ora

- **Voce:** PR-7, PR-8; ADR-034, ADR-042, ADR-054.
- **Il rilievo:**
  - Il «select-on-test» e il «condensatore su NX–NY se il banco non torna» sono modifiche post-prototipo che non sono condensatori d'accoppiamento.
  - Per calcolo nessuna delle due serve: con 22 Ω d'emettitore, 50 mV di dispersione di Vbe spostano la corrente di riposo di ±1,1 mA su 20 mA, mentre la classe A ne chiede 3,9 mA di picco.
  - Il condensatore è neutro (rieseguito, sopra). Un'impronta vuota lo trasforma da modifica a opzione di montaggio.
- **Severità proposta:** minore, prima di G2.
- **Fase 2:** il «select-on-test» è già noto (NC-035); l'impronta vuota è nuova.

### R9 — Il volume: l'RK27 dichiara 3 dB fra le sezioni, non 2

- **Voce:** PR-10, PR-1; E10; ADR-065.
- **Il rilievo:** E10 cita «≤ 2 dB». Alps dichiara 3 dB da 0 a −60 dB (2 dB solo in un riassunto di distributore). Il punto di lavoro di PR-1 è a −30 dB, e il bilanciamento corregge una sola posizione.
- **Severità proposta:** minore. Il potenziometro è un pezzo di pannello, sostituibile senza cambiare la scheda.
- **Fase 2:** nuovo. Il «Da riaprire se» di ADR-065 (~3 dB) è la soglia giusta.

### R10 — Relè monostabili eccitati per ore con la musica sui contatti

- **Voce:** PR-8, PR-29.
- **Il rilievo:** il contatto NO in serie dei relè di mute K2–K4, i relè del selettore K13–K16 e K1/K5 a +3 / +10 dB restano eccitati per tutto l'ascolto. Omron avverte che la bobina sempre eccitata scalda e fa crescere un film sui contatti, e raccomanda il bistabile o un progetto a prova di guasto. Il progetto è a prova di guasto (mute a riposo = muto). È affidabilità nel tempo, non del primo prototipo.
- **Evidenza:** `vendor/relays/omron/G6K/en-g6k.pdf`, «Long-term Continuously ON Contacts».
- **Severità proposta:** minore, prima di G2.
- **Fase 2:** nuovo.

### R11 — E3 misura la cosa sbagliata

- **Voce:** PR-6; E3.
- **Il rilievo:** il verdetto (105,3 kΩ, margine del 5 %) lo decide la capacità del selettore a 20 kHz, mentre il motivo di E3 è il condensatore d'uscita del phono, che conta in bassa frequenza.
- **Severità proposta:** minore.
- **Fase 2:** già noto (**NC-057**, minore). D'accordo.

### R12 — Un buco di rete di 20 ms toglie la musica per ~0,6 s

- **Voce:** PR-20, PR-23; P9 (b).
- **Il rilievo:** il rivelatore di rete scatta a ~14,4 ms. Un buco di uno o due cicli, che i rail reggono, inserisce il mute e la musica torna dopo 613 ms (dossier, sezione 25). Non è un colpo, ma all'ascolto è un difetto.
- **Severità proposta:** minore (uso).
- **Fase 2:** nuovo. Vedi la semplificazione S2.

### R13 — Il +10 dB serve una catena che il PRB dice di non servire

- **Voce:** PR-2 contro PR-3; ADR-004, ADR-015.
- **Il rilievo:** con la catena di PR-2 basta al più +3,5 dB (il phono a 0,5 V contro il finale a 0,612–0,75 V). Il +10 dB è per «una catena futura» e porta con sé K5, K12, R_G10, un LED e la tensione di headroom (+0,51 dB a trim 0).
- **Severità proposta:** minore. È una domanda all'utente.
- **Fase 2:** collegato a NC-009 (aperta). La semplificazione è nuova.

---

## Le ADR che riaprirei

- **ADR-102, punto 2 (la ritenuta).** Il suo «Da riaprire se» («un guasto singolo del temporizzatore che toglie … la ritenuta») si è avverato: L68 ha trovato 31 guasti singoli che la rendono cieca, accettati in P9 (e). Vedi S1.
- **ADR-034 (l'accoppiamento termico col rame), insieme a NC-019.** Il calcolo dice che non serve: il guadagno d'anello termico è ~0,035 (0,095 mA/°C per 0,37 °C/mA), quindi il circuito è stabile anche non accoppiato. Dopo il dissipatore (ADR-099) il finale è «un dispositivo più freddo e lento».
- **ADR-023 (un buffer per uscita fissa).** Solo se R1 trova che lo spazio manca. Il «Da riaprire se» sul calore del telaio è vicino: 57,7 °C contro 60.
- **ADR-081, la motivazione sulla principale** (R7), e, con l'utente, il criterio sulla Stax (R5).

## Le semplificazioni proposte

| Sottosistema | Che cosa si toglie | Che cosa si perde | Quale voce regge comunque, e con quale evidenza |
|---|---|---|---|
| **S1. La ritenuta dopo un guasto di rail** (Q513/Q514, R581–R585, C552–C555, parte di U515) | la ritenuta; al suo posto un fusibile per rail sul secondario di T1 e R550/R551 a film antifiamma | il toroidale che si spegne da solo dopo un guasto: resta acceso fino al frontale | PR-23: il sorvegliante muta comunque. Lo stato «jack muto, K501 chiuso» è già accettato per 31 guasti latenti (P9 (e), ADR-109, ADR-115). Spariscono circa 25 delle 47 righe ad alta priorità. Da fare: l'I²t del fusibile contro l'impulso di R550, che NC-073 chiede comunque |
| **S2. Il rivelatore di rete** | il rivelatore; resta il sorvegliante dei rail a 13,5 V | il mute anticipato | PR-23: con il rivelatore guasto le righe sono conformi (MUTE_CMD a 50–104 ms); U501 spento al jack fa 87 µV. In più R12 sparisce: un buco di 20 ms non toglie più la musica. P9 (b) va riscritto, il PRB no |
| **S3. I quattro buffer delle fisse** (4 blocchi su 8) | i buffer; il blocco A pilota le fisse attraverso le loro 47 Ω | la classe A degli altri percorsi con una fissa in corto; l'isolamento fra Singxer e Stax | PR-22: L11 misurava 484 mW sul blocco A con le fisse in corto, contro 1,04 W, su un blocco di allora: da rimisurare. PR-15 regge. Si risparmiano ~4,6 W (P5 da 2,3 a ~7 °C di margine), 8 TO-220 coi dissipatori e circa 300 parti: aiuta R1 |
| **S4. Il terzo livello, +10 dB** | K5, K12, R_G10 ×2, un LED | una sorgente futura molto debole | PR-2. Con 0 / +3 dB il margine su E6 a trim 0 è di +7,4 dB, e NC-009 decade |
| **S5. Il rame fra moltiplicatore e finale** (ADR-034) | il vincolo di layout | ~+0,7 mA di deriva di I_q a caldo | PR-4 e PR-7: classe A con 20 mA contro 3,9 mA di picco |
| **S6. Il select-on-test di R128** | la taratura al banco | niente di misurabile | ±1,1 mA a calcolo; un'impronta vuota su NX–NY come assicurazione (rieseguito: neutra) |

Due cose non le semplificherei: i relè al jack in geometria iii e C_T con R_G. Risolvono gradini reali e misurati, e la pratica commerciale fa lo stesso.

## Le omissioni cercate

- **Il frontale mosso durante una sequenza.** Spento prima che la musica arrivi a 1209 ms, o riacceso nei ~120 ms dello spegnimento; e SW3 mosso dentro Δ. Fra gli eventi di `data/2026-11-04/L69b/seq/oggi/` non li trovo. **Nuovo.**
- **I colpi d'accensione e spegnimento delle sorgenti.** Le fisse sono «copia fedele» e non sono mutate fuori dal mute: passano il colpo della sorgente intero a Singxer e Stax. PR-20 copre solo le commutazioni del preamp. **Nuovo**, minore: una regola d'uso o una voce del PRB.
- **Il cavo collegato a caldo all'ingresso:** 100 / 110 dB SPL alla principale, 77 / 83 dB SPL col mute inserito, affidato al manuale. Già noto (NC-059, ADR-101).

Niente di più grave di R1–R3 è emerso. Non ho trovato un difetto che faccia mancare il funzionamento elettrico del circuito simulato. I rischi veri del primo prototipo stanno nel fisico (spazio, impronte, massa) e nelle scelte di parti ancora aperte, non nella topologia del segnale.

---

## Fonti

- [WIMA MKP4F044706F00KSSD, 4,7 µF / 250 V PP, P27,5 — Bürklin](https://www.buerklin.com/en/p/wima/film-capacitors/mkp4f044706f00kssd/43D5893); [Octopart](https://octopart.com/part/wima/MKP4F044706F00JSSD); [ManoMano, 31,5 × 15 × 26 mm](https://www.manomano.fr/p/condensateur-film-mkp-wima-mkp4f044706f00kssd-47-f-250-v-dc-10-pas-275-mm-l-x-l-x-h-315-x-15-x-26-mm-1-pcs-7021795)
- [WIMA MKP1F041006B00KSSD, 1 µF / 250 V, 27,5 mm — Future Electronics](https://www.futureelectronics.com/p/3126187)
- [Stax SRM-T1, 60 dB, 100 mV / 50 kΩ — audio-markt.de](https://www.audio-markt.de/en/market/stax-srm-t1-3077950257); [Ken Rockwell, SRM-T1 (DC–20 kHz)](https://kenrockwell.com/audio/stax/srm-t1.htm), letto dall'estratto della ricerca: la pagina risponde 403
- [ESP, Earthing your hi-fi](https://sound-au.com/earthing.htm)
- [D. Self, distorsione dei condensatori, AES](https://aes2.org/publications/elibrary-page/?id=19535); [Silicon Chip, Audio Out](https://siliconchip.com.au/Issue/PE/2025/March/Audio+Out)
- [ALPS RK27, gang error — RS](https://za.rs-online.com/web/p/potentiometers/1727722); [scheda RK27111 — Meditronik](https://www.meditronik.com.pl/doc/plus/rk27111250k.pdf)
- [Ground lift: resistenza, diodi, condensatore — diyAudio](https://www.diyaudio.com/community/posts/1143863), opinione diffusa, non letteratura
- Omron G6K, «Long-term Continuously ON Contacts» e «Minimum set/reset signal width 10 ms»: `vendor/relays/omron/G6K/en-g6k.pdf` (nel repo); [copia G6K](https://www.100y.com.tw/pdf_file/G6K.pdf)
- [Talema, trasformatori toroidali 10 VA — RS](https://no.rs-online.com/web/p/toroidal-transformers/2239288): nessuna perdita a vuoto pubblicata, quindi NC-037 resta da leggere sul pezzo

I file delle riesecuzioni sono in `/Users/roberto/.claude/jobs/9cc1317d/tmp/l65/`: `thd_base.log`, `thd_cnxny.log`, `thd_cnxny100n.log` e `gen_thd.py`.
