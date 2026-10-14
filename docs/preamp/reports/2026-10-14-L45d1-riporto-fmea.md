# 2026-10-14 — L45d1, le tabelle dei guasti di L45a, L45b e L45c1 nella forma di ADR-070

Prima metà di **L45d**, l'ultima parte dell'analisi dei guasti singoli (NC-042, maggiore, prima di
G1). ADR-070 ha dato alla FMEA la forma standard da L45c2 in poi, e ha rimandato a L45d il riporto
delle tre tabelle precedenti: **il blocco di guadagno (L45a), i controlli (L45b), i rail audio
(L45c1)**. Qui ogni riga riceve la gravità, il tasso con la fonte, la probabilità, la rilevabilità,
la priorità e i rimedi candidati, **dai dati già misurati**: nessuna corsa nuova, nessun cambiamento
al circuito. Le quattro tabelle sono poi messe in una sola, ordinata per priorità, che è l'ingresso
di **L45d2**, le scelte sui rimedi. Dati in `docs/preamp/data/2026-10-14/L45d1/` (README).

## Le scelte dell'utente, all'inizio del lotto

- **«Due parti»**: L45d1 il riporto e la sintesi, L45d2 la decisione sui rimedi, ognuna con la sua ADR.
- **«No, stima dichiarata»**: non sono arrivate né SN 29500 né FMD-2016. Vale la regola di L45c2. Gli
  integrati hanno il tasso di SN 29500-2 dal documento di sicurezza funzionale del costruttore. Le
  passive e le discrete hanno un ordine di grandezza dichiarato come stima. I modi vengono da
  MIL-HDBK-338B.

## In breve

- **469 modi classificati** nelle quattro tabelle: **96 ad alta priorità, 60 a media, 313 a bassa**;
  26 righe senza classe (i casi di riferimento, e in L45b i rimandi ad altri lotti).

  | Lotto | alta | media | bassa | senza classe |
  |---|---|---|---|---|
  | L45a, il blocco di guadagno | 57 | 34 | 21 | 0 |
  | L45b, i controlli | 3 | 8 | 53 | 14 |
  | L45c1, i rail audio | 16 | 7 | 55 | 4 |
  | L45c2, la linea dei relè e il comando | 20 | 11 | 184 | 8 |

- **Il blocco di guadagno fa più di metà delle righe alte** (57 su 96). Sono 31 modi fuori da P10, con
  un rivelatore di continua come rimedio candidato. Altri 21 sono fuori da P10 e trascinano anche un
  secondo guasto per calore. Restano 4 modi del moltiplicatore di Vbe (NC-062) e 1 col solo calore.
- **In cima alla lista**, per gravità e poi per tasso, c'è **C145 in corto**: l'elettrolitico da
  1000 µF della cella RC, gravità 5 (R144 a 22,5 W), ~42 FIT sulle otto celle. Poi i finali MJE in
  corto C-E e il JFET d'ingresso in corto D-S.
- **24 righe alte sono latenti** (rilevabilità 3):
  - il mute che non si inserisce: Q501 in corto e il NO di K2–K4 saldato (L45c1), Q501 gate-drain
    (L45c2);
  - i sorveglianti ciechi (L45c2);
  - il moltiplicatore di Vbe e R126 in corto, che scaldano i finali oltre i loro limiti senza che si
    senta niente (L45a, cinque modi);
  - F501 che non apre (L45c2).
- **28 righe medie del blocco hanno come rimedio «nessuno»**: stanno dentro P10. La matrice le mette
  in media solo perché sono latenti: il blocco lavora degradato, con un colpo sotto il tetto al
  guasto e nessun segno dopo. È il secondo caso di «Da riaprire se» per L45d2 (sotto).
- **L'isolamento fra bobina e contatti dei relè di mute**, il titolo di L45b (12 V di continua
  permanenti sul jack, anche a mute inserito), esce **a priorità media**, non alta. Il modo è raro
  (~0,25–0,75 FIT con la ripartizione dichiarata), e la matrice di ADR-070 mette la gravità 4 a
  probabilità 1 in media. Lo stesso modo sui relè del selettore e del trim, più numerosi, esce alto.
  Si segnala perché L45d2 decida se tenerli insieme: è il primo dei casi di «Da riaprire se» di
  ADR-070 («la matrice mette nella stessa classe casi che l'utente vuole trattare in modo diverso»).
- **I corti dal lato grezzo del rail negativo hanno gravità 5** (L45c1): C502 in corto, i due diodi
  del ponte verso il negativo, C510 e l'ingresso di U502 a massa. Lasciano l'uscita di U502 da 0,78
  a 1,76 V sopra il suo ingresso, contro i −0,3 V del suo massimo assoluto. Il lato positivo resta a
  4, perché il datasheet di U501 non dà quel limite.

## Il metodo

### Il riporto legge le tabelle pubblicate, non rifà le misure

Il piano di partenza era di passare L45c1 dallo stesso script di L45c2. Leggendo `tabella_l45c1.py`,
però, L45c1 ha regole che `tabella_l45c2.py` non ha: i corti dei rail accettati da P9 (c), il NO
saldato col ponte del caso di base, le corse lette fino ai rimbalzi del contatto. Rifatta con lo
script di L45c2, la tabella di L45c1 avrebbe **cambiato verdetti già pubblicati**. Allora ogni riporto
**legge la tabella così come è stata pubblicata** e le aggiunge le colonne di ADR-070. Lo script di
L45c1 lo controlla: rifiuta se una colonna pubblicata cambia.

### Lo strumento, provato su un caso noto

Le regole di ADR-070 (la gravità dal verdetto e dal picco, la probabilità dal tasso e dalla
frazione, la matrice, i rimandi da una riga al suo caso) stanno in `tabella_l45c2.py`. Sono state
**tolte da lì senza cambiarle** e messe in `script/motore.py`. Prima di usarlo:

| Controllo | Atteso | Misurato |
|---|---|---|
| `verifica_l45c2.py`: le colonne di ADR-070 di L45c2 ricalcolate dalle sue stesse righe | tutte uguali | **215 righe su 215**, 11 colonne, tutte uguali |
| lo stesso con `--sabota` (l'obiettivo di 2 mV spostato a 10 mV) | diverse | **53 diverse**, tutte le righe da 6,44 mV di Δ perso |
| lo stesso dopo le tre estensioni del motore (sotto) | tutte uguali | tutte uguali |
| `riporto_l45b.py --prova`: il lettore dei numeri scritti come testo | 14 celle note | **14 su 14** |

Il primo sabotaggio provato, l'obiettivo a 1 mV, non cambiava niente: L45c2 non ha picchi fra 1 e
2 mV. Non provava nulla, ed è stato sostituito con quello a 10 mV.

Le tre estensioni, che L45c2 non usa:
- il regolatore da più di 1 W (U501, U502) segue le regole del regolatore;
- frazioni `a+b` e `a/N` generali (L45c2 aveva solo `off+gs` e `fuori/N`);
- le **istanze** (`MOLT`): una riga che vale per N parti uguali moltiplica il tasso per N. È la
  regola che L45c2 applicava a J514 e a R544–R547.

### L45a, il blocco di guadagno

Una riga per modo (112). Le colonne vengono così:
- **l'effetto**: il picco filtrato coi carichi di oggi, al jack peggiore, in ognuna delle cinque
  posizioni (`L45a/fmea_blocco.csv`);
- **il verdetto**: **P10**, il criterio di oggi per un guasto durante l'ascolto (ADR-069), grezzo e a
  vuoto, posizione per posizione (`L45b/p10_blocco.csv`);
- **la gravità**: 4 se P10 è fuori in una posizione, altrimenti dal picco. Un picco sopra il tetto
  per meno di 100 ms resta 3, come vuole ADR-070. **5** se la colonna del calore di L45a nomina una
  parte oltre i suoi limiti (`sintesi.py` di L45a ci scrive solo quelle);
- **la rilevabilità**: 2 se la musica si ferma o si rompe e resta così (l'uscita del blocco va al
  rail o oscilla), o se P10 è fuori (un colpo sopra il tetto per più di 100 ms, che nessuno perde);
  altrimenti 3, latente. Mai 1: il sorvegliante non interviene (0,90 A contro 1 A, L45a).

  **La prima regola era sbagliata, ed è stata corretta prima della sintesi.** Dava 2 a ogni picco
  sopra 2 mV e a ogni uscita spostata in continua: un colpo singolo al guasto contava come guasto
  visto. Così il moltiplicatore di Vbe usciva «udibile» per i 36 mV di un colpo al blocco B a +10 dB,
  mentre il suo effetto vero è scaldare i finali a 181–183 °C senza che si senta niente.

  La «continua» di L45a è uno spostamento di più di 50 mV all'uscita del blocco. I condensatori
  d'uscita la tengono lontana dal jack, e sotto ~9,7 V non taglia la musica. Per ADR-070, 2 è
  «lo vede subito chi ascolta (non suona …)» e 3 «non si vede finché non arriva un secondo evento».

  Con la regola corretta L45a passa da 57 / 12 / 43 righe alte / medie / basse a **57 / 34 / 21**. Le
  alte restano le stesse nel numero, ma 5 diventano latenti;
- **la probabilità**: il tasso del modo per le istanze del blocco. Sono 8 (blocco A, buffer F1 e F2,
  blocco B, per due canali); R113 ne ha 4, R138 e R143 2. Il blocco B a +10 dB è lo stesso blocco.

Lo script rifiuta se i conti non sono quelli pubblicati: 544 posizioni, 257 fuori, 58 modi (L45b);
112 modi, 26 col calore (L45a).

### L45b, i controlli

L45b aveva scritto i numeri come testo («7,1 µV (10 dB SPL)», «princ. 579 ms; Singxer 3082 ms»).
`riporto_l45b.py` li rilegge: il picco più grande fra le colonne del jack principale e delle fisse,
il tempo sopra 0,87 V più lungo; sopra 100 ms la riga è fuori da P10. Ogni riga ha in
`classi_l45b.py` le parti che rappresenta (tipo, modo, quante), la gravità minima, la rilevabilità e
il rimedio. Una riga senza numero e senza gravità dichiarata viene rifiutata: è successo una volta,
a R_SEL aperta, che ha ora una gravità 3 dichiarata (un gradino fino alla continua della sorgente).

**14 righe sono rimandi, senza classe qui**:
- il NO di mute saldato e Q501 in corto: misurati sul banco vero in L45c1;
- Q501 aperto, Q502, D522 e i pull-down dei comandi: classificati riga per riga in L45c2;
- il micro: è di L54, come in L45c2;
- le LDR: non ci sono più;
- «il LED rosso acceso con la musica»: è un effetto di tre righe, non un modo.

Così nessun modo è contato due volte nella sintesi.

### L45c1, i rail audio

La tabella pubblicata, con `classi_l45c1.py`. Sono **gravità 5** i corti del grezzo negativo (sopra).
Le **sovratensioni dei rail** (fino a ±20,3 V) tengono la gravità misurata, ≤ 0,4 mV al jack. Ma
L45c1 non ha letto le tensioni massime delle parti del blocco, e la dissipazione dei finali cresce
col rail: il rimedio candidato lo dice. **Il filo di massa fra le due schede aperto** non è
simulabile sul banco a due passi: ha una **gravità 4 prudente, dichiarata**, da verificare col
cablaggio di G2 (NC-044).

## I tassi nuovi

In `data/2026-10-14/L45d1/tassi/fonti.md`. Sono tutte stime dichiarate, con la ripartizione dei
modi da MIL-HDBK-338B:

| Parti | FIT della parte |
|---|---|
| bipolari di segnale | 2 |
| VAS e carico in SOT-223 | 5 |
| finali MJE | 10 |
| metà dell'LSK489 | 3 |
| condensatori a film | 1 |
| relè di segnale G6K | 10 |
| LED | 1 |
| commutatori | 10 |
| U501 / U502 | 100, il valore pieno di TI per un regolatore oltre 1 W, non dimezzato come U503 |

**Le ipotesi dichiarate**, dove la tabella non ha il modo:
- il corto di un bipolare diviso a metà fra collettore-emettitore e base-emettitore;
- l'isolamento fra bobina e contatti come 0,05 dello 0,19 di «corto» di un relè;
- un NO e un NC saldati che si dividono a metà il «polo saldato»;
- le istanze dei controlli: otto ingressi, sei uscite, sei LED a pannello.

## Che cosa dice la sintesi a L45d2

`fmea_sintesi.md` raggruppa le righe per rimedio candidato. In testa, per righe alte:

| Rimedio candidato | alta | media | Da dove |
|---|---|---|---|
| un rivelatore di continua sulle uscite dei blocchi che apra il mute (con o senza il calore) | 52 | 6 | L45a |
| un autotest dei sorveglianti all'accensione (oggi il firmware fa da riserva a 2,2 ms) | 10 | 0 | L45c2 |
| i corti del grezzo: accettarli (≤ 9,0 mV al jack) o rivedere D510 / D511 e la protezione di U502 | 9 | 1 | L45c1 |
| limitare la corrente sul comando (i clamp e i sink oltre i limiti) | 7 | 0 | L45c2 |
| il mute che non si inserisce: rivelarlo e staccare `VRELAY`, o due interruttori in serie (Q501 in corto, gate-drain) | 4 | 2 | L45c1, L45c2 |
| il NO di mute saldato: un contatto in serie, o leggere il jack | 4 | 0 | L45c1 |
| il moltiplicatore di Vbe (NC-062, il suo lotto) | 4 | 0 | L45a |
| l'isolamento dei relè: un relè con isolamento rinforzato, o togliere `VRELAY` | 3 | 4 | L45b |
| nessuno: dentro P10 (latenti, il blocco lavora degradato) | 0 | 28 | L45a |
| un controllo di Δ a ogni mute | 0 | 8 | L45c2 |
| il filo del rail fra le schede: far leggere al sorvegliante il lato della scheda audio | 0 | 2 | L45c1 |

**Due casi da portare a L45d2 col «Da riaprire se» di ADR-070** («la matrice mette nella stessa
classe casi che l'utente vuole trattare in modo diverso»):
1. l'isolamento dei relè di mute (12 V permanenti sul jack) esce in media per la sola rarità, mentre
   lo stesso modo sui relè del selettore e del trim esce in alta;
2. 28 guasti del blocco dentro P10 escono in media per la sola latenza, senza un rimedio candidato.

Le scelte della lista di NEXT-SESSION sono tutte nella tabella. Fra i numeri nuovi:
- **il rivelatore di continua copre 58 righe del blocco**, e potrebbe coprire anche il filo del rail
  e i due condensatori d'uscita in corto (rimedi candidati di L45c1 e L45b);
- **il tetto delle fisse** (NC-046) non ha righe proprie: nessun guasto sulle fisse ha un criterio
  diverso da quello del principale.

## Che cosa non è stato fatto

- Nessuna corsa nuova: nessuna colonna chiedeva una forma d'onda. Le forme d'onda di L45a e L45b non
  sono state cercate.
- Il tasso non è portato alla temperatura di ogni parte col modello di stress della norma, come in
  L45c2: le stime sono già pensate per il telaio caldo.
- Le tensioni massime delle parti del blocco col rail a 20 V restano da leggere. Sono un rimedio
  candidato, non un'analisi di questo lotto.

## Non conformità

**NC-042** avanza: le quattro tabelle sono nella forma di ADR-070 e in una sintesi. Resta aperta fino
alle scelte di L45d2. Nessuna NC aperta o chiusa. Le righe del moltiplicatore di Vbe rimandano a
**NC-062**.
