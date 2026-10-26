# L54a — il micro, lo standby e lo spegnimento morbido, riesaminati coi numeri (2026-10-25 / 26)

**Mandato**: NC-054 (maggiore, prima di G1; rilievi R3 e R4 dell'architetto in L52). Il progetto di oggi
contro un temporizzatore tutto analogico coi comparatori, con e senza lo standby: gli stati, PR-24 per
costruzione, PR-20 e PR-23 sui casi di L41c, il calore, NC-037; poi la scelta dell'utente. **L54
diviso dall'utente all'inizio, «Due parti»**: L54a i numeri, la scelta e l'ADR; L54b il sorgente.
Decisione **ADR-102**, **«Comparatori, con lo standby»**. Dati `data/2026-10-25/L54a/` (README).

**Non toccati**: `circuits/preamp/psu.py`, la scheda audio, il firmware. Il temporizzatore nuovo vive
solo sul banco (`psu/genera_tb_psu.py`, `TIMER_AN`).

## Sintesi

- **Tre opzioni sullo stesso banco**, quello dell'alimentatore di L45d2b3b1, provato sul suo caso noto
  (deck uguale salvo i percorsi, uscite del firmware byte-identiche). Il micro di oggi; dodici canali
  di comparatore con lo standby; lo stesso senza standby (con T2, o con `VRELAY` da T1).
- **La sicurezza è uguale in tutte**: i jack si staccano negli stessi istanti (17,4 ms alla perdita
  di rete, a ogni rete e all'angolo minimo), il guadagno dopo, il rail in regolazione fino allo
  stacco. I controfattuali senza Δ falliscono come devono.
- **Coi comparatori** la riserva del sorvegliante cieco diventa hardware e più veloce (< 0,5 ms dalla
  soglia, contro 2,2 ms); la ritenuta dopo un guasto e il timeout dei 2 s ci sono; lo standby sale di
  41–50 mW; il calore non cambia.
- **Senza standby niente stacca un guasto**: col corto davanti al regolatore + R550 resta a 83–102 W.
- **Scelta dell'utente**: «Comparatori, con lo standby». **NC-054 chiusa**; NC-037 avanza (T2 a vuoto
  ≤ 0,35 W).

## 1. Gli stati

I nove stati della specifica del firmware (`firmware/preamp_timer/spec/timer_spec.md` §3) e chi li fa
col temporizzatore a comparatori:

| Stato o sequenza (specifica) | Coi comparatori |
|---|---|
| STANDBY | frontale spento: il canale del frontale tiene giù il nodo «acceso»; `MUTE_REQ`, `PERMIT_REQ`, `MAINS_REQ` giù, `VRELAY_EN` giù |
| ACCENSIONE (4.1) | il nodo «acceso» chiude K501 (~3 ms) e dà `VRELAY_EN`; il rilascio dopo 0,57 s di alimentazione buona |
| il timeout dei 2 s (4.1) | l'armamento (2,7 MΩ · 1 µF) da ~1,9 s di «acceso con la rete»: senza rail la ritenuta scatta a 2,05 s |
| MUTO / RILASCIO / MUSICA (4.3) | SW3 sul nodo filtrato; `MUTE_REQ` e `PERMIT_REQ` insieme (il permissivo non dopo, D522) |
| INSERZIONE (4.2) | il nodo filtrato si svuota subito; `PERMIT_REQ` ~24 ms dopo; Δ e Δ₂ in hardware come oggi |
| SPEGNIMENTO (4.4) | `VRELAY` Δ₂ dopo il permissivo (U508, come oggi), K501 ~84 ms dopo il permissivo |
| BUCO_RETE (4.5) | il rivelatore di rete svuota l'alimentazione buona e l'armamento: al ritorno, 0,57 s e la musica; un buco lungo rifà l'accensione |
| GUASTO (4.6) | rail o `VRELAY_REG` fuori, rete presente, armato: la ritenuta tiene mute, `VRELAY`, K501 giù fino al frontale |
| debounce (4.7) | il nodo filtrato (200 kΩ · 100 nF): ogni ingresso buono per ~14 ms |
| watchdog (4.8) | non serve |

Il temporizzatore: dodici canali (tre TLV1704), 16 resistenze, 11 condensatori, 9 diodi, due
transistor, ~40 parti; ne escono U509, il suo condensatore, J515 e le cinque resistenze di lettura:
**~33 parti in più**.

## 2. Le correzioni del disegno

Sei, ognuna da una corsa (README della cartella): il nodo «acceso» a 10k; il canale di `PERMIT_REQ`
(senza, D522 teneva `MUTE_G` al permissivo e il permissivo non saliva mai); `PERMIT_REQ` ritardato
(Δ 15,4 ms senza, sotto 16,9); 1 nF sulla ritenuta (le corse si fermavano sul suo fronte); 820k
(dopo un buco di 20 ms la musica tornava 435 ms dopo la rete); il controfattuale analogico che toglie
anche il secondo Δ. Ogni CSV è letto dopo l'ultima correzione che lo tocca.

## 3. I casi di L41c e della FMEA

Istanti dall'evento; «jack» al più tardi, «guadagno» al più presto (le soglie del G6K di
`analizza_seq.py`).

| Caso | micro | comparatori | senza standby |
|---|---|---|---|
| perdita di rete (−10 / 0 / +10 %) | 17,4 / 34,6 ms | 17,4 / 55,5 ms (uguale alle tre reti) | 17,4 / 55,5 ms |
| perdita, Δ all'angolo minimo | 17,5 / 33,4 | 17,5 / 54,5 | 17,5 / 54,5 |
| spegnimento dal frontale | 31,3 / 67,9, K501 131,5 | 10,3 / 47,6, K501 123,1 | (= perdita di rete) |
| buco di 20 ms: la musica torna | 521 ms | 541 ms (521 dopo la rete) | 541 ms |
| U502 spento (rail −) | 15,6 / 32,7, K501 115,5 | 15,6 / 53,3, K501 129,1 | 15,6 / 53,3, **toroidale acceso** |
| U501 spento (rail +) | 48,1 / 65,2 | 48,1 / 86,0 | 48,1 / 86,0 |
| U503 spento | 17,7 / 34,9 | 17,9 / 45,0 | 22,5 / 60,3 |
| controfattuale senza Δ | — | guadagno 14,5 < jack 17,4: **fallisce** | fallisce |
| accensione: dal frontale alla musica | 0,74 s | 1,11 s | 1,61 s da freddo |

In ogni caso C2 e C3 (il permissivo eccitato col mute, rilasciato ≥ 16,9 ms dopo), il jack prima del
guadagno e prima di V+ < 10,6 V. **PR-20 e PR-23**: i jack e i rail sono gli stessi, quindi le cifre al
jack del dossier (39,2 nV alla perdita di rete, §24) valgono; lo spegnimento coi comparatori muta col
rail a 14,98 V. La catena verso la scheda audio si rifà sul sorgente in L54b.

**La FMEA che contava sul firmware** (lista dell'agente di ricognizione, §5):
- **sorvegliante cieco** (U505 A, U505 B, U506 B, poi il regolatore spento): coi comparatori il mute
  arriva < 0,5 ms dopo che il rail passa la soglia (il caso del rail +: 13,55 V a TE + 45,5 ms, `MUTE_G`
  giù nello stesso campione). Col micro questi tre casi non trovano un punto fisso sul banco (le
  sostituzioni di `MUTE_G_IN`): vale la cifra di L45c2, 2,2 / 2,1 ms. Un partitore guasto acceca anche i
  canali nuovi, come accecava il firmware, che leggeva gli stessi nodi;
- **corto di C509** (davanti a U501): R550 **7,65 / 9,35 J** coi comparatori (oltre 1 W per 194 ms),
  7,21 / 8,80 J col micro (184 ms); **senza standby 44,5 / 54,3 J nel primo secondo, 83–102 W senza
  fine**: R550 è da 2 W;
- **bobina di K501 in corto**: R552 0,47 / 0,54 J coi comparatori, 0,49 / 0,56 J col micro;
- **il timeout** (U501 morto all'accensione) e **la ritenuta azzerata dal frontale**: K501 aperto a
  2,05 s; spento e riacceso, K501 si richiude e la ritenuta riscatta ~2,1 s dopo.

## 4. Standby e calore

| | rete −10 % | nominale | +10 % |
|---|---|---|---|
| standby da T2, comparatori (a regime) | 116,7 mW | 130,1 mW | 145,1 mW |
| differenza dal micro (stessa finestra, 1–2 s) | +40,8 | +45,3 | +49,9 |
| micro (stimato a regime) | ~76 | ~85 | ~95 |
| in musica, dai secondari: micro / comparatori | | 16,36 / 16,34 W | 18,03 / 18,00 W |
| senza standby, con T2 / con `VRELAY` da T1 | | 15,77 / 16,01 W | 17,38 / 17,63 W |

- **NC-037**: coi comparatori il margine per la perdita a vuoto di T2 è **0,35 W** a +10 % (era 0,40).
  La causa principale sono i pull-up delle uscite tenute basse in standby (`MUTE_REQ`, `PERMIT_REQ`,
  `MAINS_REQ`, il nodo «acceso»): L54b può alimentarli solo da acceso.
- **Il calore** (P5): coi comparatori −25 mW in musica, il telaio resta **57,2 °C** contro 60 °C nel
  caso peggiore. Senza standby −0,65 W (56,5 °C), o ~−0,8 W col ferro di T2 tolto (56,2 °C), con
  1,13 °C/W dal bilancio del dossier.

## 5. Cosa la sicurezza chiedeva al firmware

Un agente di sola lettura ha raccolto ogni punto in cui le ADR, il registro e i report della FMEA danno
credito al firmware. Coi comparatori:

| Credito | Coi comparatori |
|---|---|
| staccare K501 dopo un guasto con la rete (NC-073, ADR-094, ADR-048 p. 5) | sì, ~0,13 s; energie del 6 % più alte |
| la ritenuta fino al frontale | sì (la coppia a tiristore) |
| buco di rete contro guasto, rilascio dopo ≥ 500 ms | sì (il rivelatore svuota l'armamento) |
| il timeout dei 2 s (ADR-091) | sì, 2,05 s |
| la riserva del sorvegliante cieco (ADR-073) | sì, in hardware, < 0,5 ms: ADR-073 superata |
| la diagnosi di L58 (ADR-076, ADR-078, ADR-071) | **da rifare in hardware in L58**, o tornare all'utente |

## 6. La scelta

Portata all'utente il 2026-10-26, quattro opzioni per nome con le loro cifre contro i limiti:
«Comparatori, con lo standby» (raccomandata), «Il micro, come oggi», «Comparatori, senza standby»,
«Senza standby, senza T2». **Risposta: «Comparatori, con lo standby».** ADR-102.

## 7. Cosa la simulazione non vede

- Le corse sono a 25 °C; i comparatori sono il modello comportamentale del banco (`CMPOD`, 55 µA,
  1 µs), non quello del costruttore (`vendor/comparator/ti/TLV1702/tlv1701.lib` c'è: L54b può usarlo).
- I transistor della ritenuta sono generici; l'immunità ai disturbi (dv/dt, rete sporca) si vede solo
  sul prototipo (un «Da riaprire se» di ADR-102).
- Il ferro dei trasformatori non è nel modello (le cifre del dossier sono ipotesi).
- La catena verso la scheda audio non è rifatta: le cifre al jack valgono per gli istanti uguali.

## 8. Per L54b

Il temporizzatore in `psu.py` coi valori di `TIMER_AN` e le loro ragioni; U509, J515, R543–R547 e
`firmware/preamp_timer/` fuori (`run_tests.sh` compila il firmware: va aggiornato); il controllo dei
relè `--timer` (le regole T1–T5 trovano il micro); i disegni; i casi di questo lotto rifatti sul
sorgente, col modello del costruttore dei comparatori; i pull-up dello standby; la catena al jack per
lo spegnimento. Le righe della FMEA delle parti nuove: L58.
