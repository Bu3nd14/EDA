# L34 — Le decisioni del 2026-09-15 diventano requisiti (2026-09-15)

Lotto **L34**, di sola documentazione. Nasce da una sessione di domande
dell'utente, in sola lettura. Apre **NC-032** e aggiorna **NC-028**. ADR nuove:
**ADR-028**, **ADR-029**, **ADR-030**.

**Nessun numero è stato simulato o rieseguito**, e nessun file di `circuits/`,
`spice/` o `scripts/` è cambiato. Le cifre marcate «calcolato» sono conti fatti
su valori già registrati nel repo (NC-028) e vanno lette come stime.

## 1. Le domande, e cosa diceva il repo

### N1 — «jack» vuol dire presa d'uscita

- **Domanda**: la documentazione dice spesso «jack», ma le uscite sono solo
  sbilanciate RCA.
- **Il repo**: circa 380 occorrenze, sempre col senso di **nodo al connettore
  d'uscita**, a valle di 47 Ω e 4,7 µF (ADR-024; `MAINJACK`, `FIXJACK1/2` in
  `preamp_audio.py`). Nessuna nomina 6,35 mm, 3,5 mm, TRS o cuffie.
- **Lacune**: F3 non diceva «RCA» (F1 sì, per gli ingressi); nel sorgente
  ingressi e uscite sono `Connector_Generic:Conn_01x02` con footprint
  segnaposto.

### N2 — Comandi rotativi sul frontale, e come funzionano i LED del trim

- **Il trim** ha SW1, rotativo a 4 poli × 3 posizioni «a pannello» (ADR-027):
  «frontale» non era scritto.
- **Il guadagno** non era progettato come comando: solo `GAIN_CMD` /
  `GAIN10_CMD`. **Il mute**, solo `MUTE_CMD`.
- **I LED del trim** (`trim.py`, ADR-027 §3):
  - tre, uno solo acceso;
  - pilotati dai relè spia K9/K10, bobine in parallelo a K7/K8;
  - la catena: `VRELAY` → 1,5 kΩ → K9 (reset: 0 dB; set: K10 → reset −6 dB,
    set −12 dB), catodi su `RLY_RET`;
  - accesi dentro e fuori mute. Fuori mute mostrano lo stato vero, che può non
    coincidere con la manopola.
- **Due osservazioni**:
  - i LED hanno footprint **sulla scheda**, non a pannello;
  - **il LED legge il relè gemello**, non quello che porta il segnale: un
    guasto meccanico di uno solo dei due li fa divergere. Non è in ADR-027.

### N3 — Cambiare il guadagno a caldo

- **Sicuro**: l'anello non si apre (ADR-004). V2 è verificata in L27 con
  contatti che rimbalzano, su `v(OUT)`.
- **Il bump c'è, solo sull'uscita principale.** Calcolato, non misurato:
  gradino al jack (G₂ − G₁)·Vos_in, cioè ~6–14 mV per 0↔+3, ~25–59 mV per
  +3↔+10, ~31–114 mV per 0↔+10; ~69–95 dB SPL di picco con la formula di
  NC-028. Tabella completa in ADR-030.
- **Nessuna misura esiste**: `tb_switch_v2` guarda `v(OUT)` per 70 ms, contro
  un τ di 0,32 s al jack.
- **Sotto mute l'offset non dà gradino**: il 4,7 µF segue l'uscita attraverso
  47 Ω. Resta il gradino della musica al rilascio (NC-028).

### N4 — Il mute come permissivo del guadagno

- **A**, bistabili: niente relè per il gate, +2 spia per i LED; ma contro F5
  sul guasto di bobina.
- **B**, monostabili con autoritenuta: +2 ausiliari, LED dai loro poli liberi,
  F5 conservato; da provare la corsa al rilascio del mute.
- **Correzione di quanto detto in sessione**: la caduta di `VRELAY` inserisce
  il mute (K2–K4 monostabili), quindi non distingue A da B.

### N5 — La strada B anche per il trim?

- **Possibile**, a parità di relè; commutatore a 2 poli; niente rischio termico
  dei bistabili.
- **Contro**: consumo fuori mute (circa 42 mA), la stessa corsa al rilascio,
  cablaggio «diseccitato = −12 dB», e il lavoro verificato di L16 da rifare.
- **Verdetto proposto**: tenere i bistabili, riconsiderare dopo aver chiuso la
  corsa sul guadagno.

### N6 — Il limite di dimensioni del telaio

- **Il repo**: nessun vincolo dimensionale.
- **Technics SU-9070**: 450 × 92 × 367 mm (una seconda fonte: 369).
- **Contenitori trovati** (misure lette sulle pagine prodotto il 2026-09-15):

  | Modello | Esterni L × A × P (mm) | Note |
  |---|---|---|
  | Modushop Pesante 2U / 3U / 4U / 5U | 435 × 80 / 122 / 167 / 210 × 305 o 405 | 415 fra i fianchi; frontale da 10 mm alto 90 / 130 / 180 / 220 |
  | Modushop Galaxy GX283 / GX288 / GX388 | 230 × 80 × 230 / 230 × 80 × 280 / 330 × 80 × 280 | terza larghezza della serie non verificata |
  | BRZ 4308P | 430 × 80 × 308 o 358 | interni 410 × 74 × 297 o 347; circa 67 USD |
  | Audiophonics, con dissipatori | 430 × 120 × 315 | interni 330 × 112 × 300; 179 € |

## 2. Le decisioni dell'utente

| # | Parole dell'utente | Dove va |
|---|---|---|
| — | nessun jack, uscite sbilanciate RCA | F3, nota di terminologia |
| D1 | «si il guadagno é rotativo a 3 posizioni sul frontale» | ADR-028, F10 |
| D2 | «si il mute ha un comando sul pannello (switch)» | ADR-028, F10 |
| D3 | «non servono led per il guadagno, ne metterei uno rosso per il mute» | ADR-028, F11; la prima metà è superata da D7 |
| D4 | «i LED li colleghiamo con fili» | ADR-028 |
| D5 | «vorrei evitare bump sulle casse, mettiamo il cambio gudagno condizionato al mute, prendiamo la strada B» | ADR-030 |
| D6 | «seguo il tuo consiglio» (il trim resta bistabile) | ADR-030 |
| D7 | «ovviamente servono i LED anche per il guadagno ora»; «anche i led guadagno sono a pannello» | ADR-030 |
| D8 | «si serve una misura perchè altrimenti rischiamo di aggiungere relè e LED senza motivo, introducendo un bump per togliere un bump» | ADR-030 §3, L29 |
| D9 | «1. 3U 2. come il technics 3. metti i limite di ingombro e un paio di modelli come esempio» | ADR-029, P8 |

## 3. Cosa è stato scritto

- **ADR-028**: comandi sul frontale, LED a pannello cablati, mute = interruttore
  oppure temporizzatore.
- **ADR-029**: ingombro L ≤ 450 · A ≤ 130 · P ≤ 367 mm, con due esempi.
- **ADR-030**: interblocco del guadagno dal mute con la strada B, e i suoi LED,
  subordinati alla misura di L29.
- **`REQUIREMENTS.md`**: F3 con «RCA», **F10**, **F11**, **P8**, nota su F5,
  nota di terminologia su «jack», una riga in V2.
- **`NONCOMPLIANCE.md`**: **NC-032** aperta, maggiore; NC-028 aggiornata.
- **`STATE.md`**: lotti **L35** e **L36** nuovi, **L29** esteso, ordine rivisto.

## 4. Lotti e ordine

- **L13** resta il prossimo: nessuna decisione di oggi tocca E4. Poi **L20** e
  **L28**, invariati.
- **L29** passa sul cammino critico ed è esteso: per ogni variante di mute,
  cambio a caldo contro cambio sotto mute seguito dal rilascio, sul jack. Resta
  prima la soglia dell'utente su V2.
- **L36**, l'interblocco del guadagno, si fa solo se L29 lo giustifica; poi
  **L35**, comandi e LED a pannello nel sorgente.
- **L30 e l'alimentatore** vanno **dopo** L35/L36: ereditano il budget delle
  bobine, la tensione di `VRELAY` e il temporizzatore di mute combinato con
  l'interruttore.
- **Entro G2**: la scelta del contenitore (ADR-029) e le prese RCA vere nel
  sorgente.
