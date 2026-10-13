# 2026-10-13 — L45a, i guasti del blocco di guadagno

Prima parte di **L45**, l'analisi dei guasti singoli (NC-042, maggiore, prima di G1). Dati, deck e
comandi in `docs/preamp/data/2026-10-13/L45a/` (README). Nessun cambiamento al circuito: si misura
e si classifica. La scelta del rimedio è di **L45d**.

## In breve

- **Un guasto singolo su due, in un blocco qualunque, supera il tetto di non-danno.** Su 112 modi di
  guasto (ogni transistor in corto C-E, in corto B-E e aperto; ogni JFET, diodo, resistenza e
  condensatore in corto e aperto), simulati uno per uno con il guasto che entra **durante
  l'ascolto**: oltre 0,87 V filtrati al jack **51** nel blocco A, **50** nel buffer del Singxer,
  **51** in quello della Stax, **53** nel blocco B (a 0 dB e a +10 dB). Il caso tipico è il blocco
  al rail: **~14,9 V** al jack, 136,9 dB SPL con la formula del PRB, che il finale da 30 W limita a
  **~114 dB SPL**. La stima di R1 di L52 (13,8 V, ~114 dB) è confermata dalla simulazione.
- **Il guasto del blocco A arriva su tutti e tre i jack**: in continua sulle due fisse, e al
  principale attraverso C_T e il blocco B, fino a **24,6 V** filtrati (il blocco B va al clip
  nell'altro verso mentre C_T si scarica).
- **Il sorvegliante non interviene.** Solo due guasti assorbono abbastanza da portare un
  regolatore in limitazione (il condensatore della cella RC in corto, la resistenza del
  riferimento in corto). Il peggiore degli altri, il finale NPN in corto, porta la scheda a
  0,90 A sul positivo, sotto il limite minimo del TPS7A4701 (1 A). Nessun altro organo vede il
  guasto.
- **Un rivelatore di continua che apra il mute non abbassa il picco.** Il gradino arriva al jack
  insieme al guasto (picco a 0 ms). Simulato con il mute inserito 0,1 / 1 / 3 / 10 ms dopo il
  guasto: il picco al jack principale resta **14,8–14,9 V** in tutti i casi (a 10 ms 16,6 V, perché
  il taglio aggiunge un suo gradino). Il rivelatore accorcia l'impulso da ~250 ms a pochi
  millisecondi, cioè toglie energia al woofer, ma la cifra che PR-23 misura non cambia. **È il
  numero che L45d deve mettere davanti all'utente.**
- **Il guasto avvenuto a mute inserito non arriva al rilascio** (R1, la geometria iii): al più
  **7,3 mV** al rilascio (70,7 dB SPL), oltre 40 dB sotto il tetto. Il lato del condensatore è a
  massa attraverso il contatto, e il condensatore si carica alla continua guasta in 0,2 ms.
- **Un guasto su quattro ne trascina un secondo.** In 26 modi su 112 una parte esce dai suoi
  limiti di calore: la 56 Ω del VAS (18), l'inseguitore di ADR-067 in SOT-23 (16, a centinaia di
  gradi di Tj calcolata), la 10 Ω della cella RC (12), le 22 Ω d'emettitore (8). Quattro guasti del
  moltiplicatore di Vbe lasciano il jack pulito ma portano i finali a 181–183 °C, o le 22 Ω a
  1,7–7,5 W: rompono P7 e poi diventano un altro guasto della tabella.

## Il banco

Il canale **di oggi**, letto da `preamp_audio.py` e `trim.py` (non il blocco CANALE dei deck di V2,
che è di prima di C_T):

| Tratto | Nel banco |
|---|---|
| Sorgente | K11, 1,5 Ω; C_IN 1 µF, R_SEL 470 kΩ, contatto del selettore 0,1 Ω (ADR-064) |
| Blocco A | `gain_block.subckt`, R_IN 1 MΩ |
| Buffer F1, F2 | accoppiati in continua all'uscita di A (ADR-023) |
| Ramo variabile | scala del trim 845 + 464 + 464 Ω sempre montata, trim a 0 dB, C_T 10 µF, volume 10 kΩ **al massimo** (il caso peggiore per il gradino di A verso B), bilanciamento al centro |
| Blocco B | 0 dB, e +10 dB in una seconda famiglia; R_G 1 MΩ |
| Uscite | 47 Ω, 4,7 µF, bleed sul lato condensatore e sul jack (220 / 470 kΩ), deviatore del mute della geometria iii (0,1 Ω), carichi: cj EV250 100 kΩ, Singxer 10 kΩ (come G0), Stax 50 kΩ |
| Rail | ideali, ±15 V; la corrente si legge e si confronta coi limiti dei regolatori a parte |

Il blocco guasto è una copia del sottocircuito con **una** riga cambiata e un interruttore:
10 mΩ per un corto, un terminale staccato (1e12) per un aperto. Il guasto entra a 0,3 s in 10 µs,
senza segnale; la corsa dura 2,3 s (V2 chiede almeno 2 s). Il metodo al jack è quello dei guasti
dell'alimentatore (L41c, L47c2b2, L56): `v2_metodo.py`, evento − riferimento, filtro
20 Hz–20 kHz, picco. In dB SPL di picco a 1 m con la formula del PRB
(96 + 20 log10(21,1 V / 2,83)); per la Stax con la catena di NC-046
(101 + 20 log10(1000 V / 100), la SRM-T1 al massimo).

**Controlli del banco.**

| Controllo | Atteso | Misurato |
|---|---|---|
| Continua d'uscita del blocco sano | −2,9 mV (L56) | −2,87 mV |
| Corrente per blocco | 37,97 / 38,99 mA (L56) | 38 mA (152 mA il canale) |
| Uscita del blocco B in corto col rail + (deve superare) | ~15 V al principale, niente altrove | 15,2 V grezzi, 16,0 V filtrati; 6 µV sulle fisse |
| Stesso, buffer della Stax | ~15 V sulla Stax, niente altrove | 16,0 V sulla Stax; 11 µV al principale |
| Stesso, blocco A | su tutti e tre | 14,0 V grezzi al principale (24,6 V filtrati), 12,4 / 12,6 V sulle fisse |

Ogni corsa è letta rifiutando «timestep too small», «aborted», «source stepping failed» e «transient
op» (limitations #33, #35, #57), e controllando che arrivi a 2,3 s.

## I risultati

La tabella completa, un modo per riga e una colonna per posizione, è in
`data/2026-10-13/L45a/fmea_blocco.md` (e `.csv`). In **grassetto** i casi oltre 0,87 V. Sulle fisse
0,87 V è il tetto del jack principale preso come riferimento: **sulle fisse un tetto non c'è**
(lo fissa L45d, con NC-046).

### Per classe

| Che cosa fa il blocco | Guasti tipici | Al jack (filtrato) |
|---|---|---|
| **Va al rail e ci resta** | JFET aperto o in corto D-S, cascode aperti, specchio d'uscita in corto, VAS aperto o in corto, inseguitore aperto o in corto, riferimento dei cascode in corto, condensatore di Miller in corto, cella RC in corto, resistenze d'emettitore del VAS e della coda aperte | **12–15 V** (136–137 dB SPL col PRB; ~114 col finale) |
| **Va al rail e ritorna** in 20–30 ms (la coda ritrova corrente dalla giunzione base-collettore) | coda in corto B-E | **12,7 V** |
| **Si sposta in continua** di 1–10 V | specchio e aiuto (±2 V), coda e JFET in corto (≈ 7 V, 10 V al jack), carico del VAS in corto (−4,7 V), finali in corto (+1,3 / −7,2 V) | **1–10 V** |
| **Oscilla** | finale PNP staccato (0,7 V picco-picco attorno a zero), emettitore dello specchio d'uscita in corto (1,3 V picco-picco attorno a −1,45 V) | 0,3 V; **≥ 1,5 V** |
| **Niente al jack, ma calore** | moltiplicatore di Vbe aperto o in corto B-E, sua resistenza alta aperta | < 1 mV; finali 181–183 °C, 22 Ω a 1,7–7,5 W |
| **Niente** | disaccoppiamenti aperti, condensatori del riferimento aperti, stopper e degenerazioni in corto, rami di guadagno a 0 dB | < 2 mV |

**A +10 dB** i rami di guadagno cambiano classe: un loro corto, o la resistenza di retroazione aperta,
mette la retroazione a massa e il blocco B al rail (**11–12 V**). Gli spostamenti in continua escono
amplificati (lo specchio da 2,1 a 6,6 V).

### Il blocco A

Sulle fisse il guasto arriva in continua, attraverso i buffer: lo stesso gradino del blocco al rail
(12–15 V). Al jack principale arriva attraverso C_T (10 µF su 10 kΩ, τ ≈ 0,1 s) e il blocco B, che
va al clip mentre C_T si carica e poi nell'altro verso mentre si scarica: col filtro di PR-23
**fino a 24,6 V** (specchio a diodo aperto, diodo del riferimento aperto), più del rail, perché il
passa-banda sovraelonga una salita seguita da una discesa. Il grezzo resta sotto i 15 V.

### Le fisse

Il buffer della Stax e quello del Singxer si comportano come il blocco B sul loro jack. Con la
catena di NC-046 (la SRM-T1 al massimo) il blocco al rail darebbe **144 dB SPL** all'orecchio: la
SRM-T1 esce al più con 300 V RMS, cioè ~110 dB in questa convenzione, e ci va al clip. Il Singxer
(+11 dB) non ha una sensibilità di cuffia dichiarata: si danno i volt (fino a 15 V al jack).

### Con la musica

Il K11 a fondo scala (2,7 V RMS, 1 kHz), contro la corsa di riferimento con la stessa musica:
blocco B al rail 15,4–17,1 V (137–138 dB col PRB), finale NPN in corto 4,9 V, finale PNP in corto
7,7 V; blocco A al rail 16,8 V su tutti e tre i jack. La musica non cambia nessun verdetto. Il VAS
in corto del blocco A con la musica si ferma a 0,306 s: 15,7 V è un limite inferiore.

### Il rivelatore di continua, simulato prima di sceglierlo

Un rivelatore ideale che inserisca il mute in un tempo dato dopo il guasto (il G6K si rilascia in
3 ms al massimo, datasheet in `vendor/`):

| Mute dopo il guasto | Blocco B al rail + | Blocco B al rail − | Blocco A al rail −, tutti e tre i jack |
|---|---|---|---|
| 0,1 ms | 14,82 V | 14,91 V | — |
| 1 ms | 14,82 V | 14,91 V | — |
| 3 ms | 14,82 V | 14,91 V | 14,6 V |
| 10 ms | 14,82 V | 16,59 V | — |
| nessuno | 14,8 V | 14,9 V | 14,6 V |

Il picco cade **a 0 ms** dal guasto. Quello che il rivelatore cambia è la durata: senza, il gradino
decade col condensatore d'uscita e i bleed (~0,25 s); con, il jack si stacca dopo il tempo del
relè. Per PR-23 così com'è scritto (picco filtrato) non basta nessun relè, per quanto veloce.

### Il sorvegliante e la corrente

La scheda (8 blocchi, 0,30 A a riposo per rail) con un guasto in un blocco: il peggiore è il
finale NPN in corto, 0,90 A sul positivo; il moltiplicatore di Vbe aperto 0,67 A. Il TPS7A4701
limita fra 1 e 1,26 A (minimo / tipico), il TPS7A3301 a 1,9 A: **nessun guasto del blocco porta
i rail sotto 13,5 V**, salvo due:

- **la cella RC in corto**: 1,6 A sul positivo nel canale, il regolatore in limitazione, il
  sorvegliante muta; la 10 Ω dissipa 22,5 W e si apre (e la cella aperta è un altro modo della
  tabella: il blocco va al rail lentamente, 1,5–6 V al jack);
- **la resistenza del riferimento in corto**: i due 1N4148 diretti fra massa e il rail negativo,
  14 A col rail ideale; in realtà il regolatore negativo limita a 1,9 A, il sorvegliante muta e i
  diodi si aprono (il caso «diodo del riferimento aperto»).

Il corto di un disaccoppiamento dei rail è un sovraccarico del regolatore: è **L45c**.

## Quello che il banco non dice

- **Due guasti derivano lentamente, e la velocità della deriva il banco non la sa**: lo stopper di
  gate del lato segnale aperto e la resistenza di retroazione aperta (a 0 dB) lasciano un gate senza
  ritorno in continua. Nel banco il primo porta l'uscita del blocco a +4,5 V in 2 s, il secondo a
  −0,09 V; al jack arrivano 35 mV e 0,2 mV, perché una salita lenta il passa-alto di 20 Hz la toglie.
  La corrente che muove il gate la inventa `gmin` (limitations #49): nel prototipo la fissa la
  perdita del JFET, e la deriva arriva comunque al rail. Vanno letti come «al rail, lentamente»: un
  danno in continua più che un gradino.
- **Tre corse non arrivano in fondo**: lo stopper di gate di retroazione aperto (si ferma a 0,61 s
  anche col metodo gear, ma ha già dato 23–27 V); il corto dell'emettitore dello specchio d'uscita
  (oscilla, 20 ms costano 87 s: misurato fino a 0,32 s sul blocco B, 1,9 V; nelle altre posizioni
  il punto di lavoro, −1,47 V); il finale PNP staccato del blocco A, fino a 0,6 s.
- **Il secondo guasto non è simulato.** Quando una parte esce dai suoi limiti di calore si dice
  quale e quanto, e lo stato che segue è un'altra riga della tabella (quasi sempre il rail).
- **Sotto i ~10 mV il verdetto contro i 2 mV dipende dal diradamento.** Con 0,1 µs l'interpolazione
  cubica aveva dato 47,8 V su un jack fra −6 e +4,4 V; con un quinto del passo (la regola di
  `v2_metodo analizza`) i numeri sono sani, ma cinque guasti dello stadio d'uscita passano da
  0,04–0,4 mV a 2–6 mV. Nessun verdetto contro il tetto cambia.
- Temperatura dell'aria 27 °C, rail ideali, modelli del costruttore (gli stessi di L56).
- **Il calore** è Tj = 27 °C + P · R_thJA con le R_thJA di `caldo.py` di L56: le Tj di centinaia di
  gradi dicono «si rompe», non una temperatura.

## Che cosa resta, e a chi

- **L45b** — i controlli: i relè (contatti saldati e aperti, bobine), i condensatori d'uscita e C_T,
  i comandi dal micro, il firmware.
- **L45c** — l'alimentatore componente per componente, coi corti dei disaccoppiamenti dei rail.
- **L45d** — la decisione, con i numeri di sopra davanti: il rivelatore di continua (che accorcia,
  ma non abbassa il picco), un tetto sulle fisse (NC-046), e se PR-23 debba coprire i guasti della
  scheda audio con lo stesso tetto o con un criterio di durata.

## Requisiti

- **NC-042**: avanza; si chiude con L45d.
- **PR-22 / P7**: quattro guasti del moltiplicatore di Vbe portano i finali o le 22 Ω oltre i loro
  limiti a riposo, senza nessun segno al jack. È nella FMEA, non è una voce nuova: P7 è scritto per
  il corto all'uscita, non per i guasti interni.
- **Limitations #58** (nuova): `esegui.sh` lanciato in background fa partire tutta la lista insieme.
