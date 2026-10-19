# L62a — il moltiplicatore di Vbe: i guasti rifatti, i rimedi sul banco, la scelta

Data: 2026-10-19 · Lotto: L62a · Non conformità: **NC-062** (avanza), NC-042 · Decisione: **ADR-090**
· Dati: `docs/preamp/data/2026-10-19/L62a/` · Il circuito non cambia.

## Prima di tutto: che cosa è cambiato rispetto a L45a

- **Il calore no.** I quattro guasti sul blocco di oggi (R150–R153, R112 / R144 sdoppiate, Q127 in
  SOT-223) danno le cifre di L45a alla terza cifra:

  | Guasto | Ogni finale | Tj a 27 / 60 °C d'aria | Ogni 22 Ω |
  |---|---|---|---|
  | Q127 emettitore aperto | 2,48 W | 183 / 216 °C | 3,28 W |
  | Q127 base-emettitore in corto | 2,45 W | 181 / 214 °C | 1,72 W |
  | R129 in corto | 2,45 W | 181 / 214 °C | 1,72 W |
  | R128 aperta | 1,23 W | 104 / 137 °C | 7,54 W |

  Q127 non scalda: è spento. La sua R_thJA è ora di 125 °C/W (ADR-082), non più i 417 di `analizza_tr.py`.
- **Il gradino al jack sì, ma per il metodo.** Nell'istante del guasto la principale dà **74 mV «A»,
  91 dB SPL** (B; 227 mV e 101 dB SPL a +10 dB; R128 aperta 159 mV, 97,5 dB SPL). In L45a: 0,42 mV.
  - Non è il blocco: nel banco di oggi la copia guasta di L45a dà gli stessi 74 mV; R150, R151 / R152
    tolte e R153 a 1 Ω non cambiano niente (`diagnosi_scatto.csv`).
  - È un solo punto a −1,35 V, largo ~2 µs, all'apertura dell'interruttore ideale del banco. Dopo, il
    jack si ferma a −0,39 mV.
  - Il metodo con la media (ADR-087 / ADR-088, da L60d2) lo conta per la sua area; il puntuale di L45a
    lo scartava. Sulle stesse corse il metodo puntuale dà **0,43 mV** (`metodo_scatto.py`).
  - Sotto il tetto di non-danno (0,87 V). L'utente: **«Solo nel report»**, e la trappola è la
    **limitations #64**.

## Il banco

Il canale di L45a (`genera_canale.py`), con le copie guaste riscritte dal subckt di ogni variante
(limitations #62), nelle posizioni A, F1, F2, B e B a +10 dB: 246 corse di guasto, più 24 deck a
blocco sano (tb_op, quattro deck d'anello, tb_mute_corto) e 8 di temperatura.

Controlli:
- il riferimento sano dà −2,9 mV e 151,9 mA dal rail + del canale (38 mA per blocco);
- `CTRL_OUT_VP` dà 16,0 V alla principale, oltre il tetto;
- tutte le corse sono finite con uscita 0;
- la variante base è il blocco di oggi byte per byte.

## La letteratura

Cercata con un agente prima del worktree.
- **Self**, *Trimodal audio power, part 2*, Electronics World + Wireless World, luglio 1995. Due
  regolatori in parallelo fra i due nodi, «the lowest voltage wins». Un moltiplicatore di riserva
  limita la polarizzazione al doppio del normale, «a survivable experience».
- **Elliott**, ESP, *Audio Power Amplifier Design Guidelines* §3.2: il cursore del trimmer aperto
  mette «entrambi i finali in piena conduzione», più in fretta di qualunque fusibile.
- **Elliott**, ESP, *Project 03*: «I left the diodes in circuit as a fail-safe».
- **Russell**, hifisonix: il partitore orientato in modo che un'apertura tolga la polarizzazione.
- **Cordell**, *BC-1*, 2025: la corrente del VAS limitata e i «catch diodes»; a giudizio dell'agente,
  non coprono questo guasto.
- Il libro di Self (6ª ed.) e quello di Cordell (2ª ed.) non sono stati letti, solo cercati.

## I rimedi sul banco

| | Quattro diodi | Moltiplicatore di guardia | Limitatore sulle 22 Ω |
|---|---|---|---|
| Parti per blocco (scheda) | 4 (32) | 3 (24) | 6 (48) |
| Finali coi quattro guasti, 60 °C d'aria | **97–98 °C** | 94–95 °C | 121–123 °C |
| 22 Ω coi quattro guasti | 0,041 W | 0,036 W | 0,124 W |
| Parti oltre i limiti, cinque posizioni | nessuna | nessuna | nessuna |
| Riposo a blocco sano, scarto (27 / 60 / 90 °C) | −0,05 / −0,09 / −0,13 mA | −0,27 / −0,36 / −0,39 mA | +0,19 / +0,20 / +0,21 mA |
| V1, scarto massimo | 0,05° | 0,03° | 0,13° |
| P7, finale peggiore | 0,362 W, 83 °C (uguale) | uguale | **0,521 W, 93 °C**; i finali a **118 mA** di picco invece di 214 |
| I suoi guasti | il riposo 19,7–22,1 mA (un diodo in corto) | **0–7,6 mA**: Q160 in corto C-E, R161 in corto, R162 aperta → classe B | Q160 in corto: **VAS 135 °C** |
| Gradino nell'istante del guasto (B, media) | 4,3 mV, 66 dB SPL | 3,7 mV, 65 dB SPL | 8,5 mV, 72 dB SPL |

Il dissipatore, solo a calcolo:
- per 2,48 W con 60 °C d'aria servono ≤ 26 °C/W giunzione-aria su 16 finali;
- le 22 Ω da 7,5 W andrebbero cambiate con resistenze da 10 W;
- va contro l'assieme di L49b.

## La scelta

L'utente, coi numeri qui sopra: **«Quattro diodi»** → **ADR-090**. Quattro 1N4148 in serie fra NX e NY
in tutte le otto istanze, anodo verso NX. Il sorgente e la verifica sono di **L62b**.

## Limiti dichiarati

- **Il calore** si calcola dalle potenze a 27 °C, come in L45a: Tj = Ta + P · R_thJA. Le parti nuove
  in SOT-23 sono a 417 °C/W.
- **La temperatura uniforme** di `temperatura_op.py` è un limite grossolano: i diodi e la guardia non
  sono accoppiati ai finali.
- **V4 a caldo non è rifatta.** Il riposo a blocco sano cambia di −0,05 mA coi diodi, contro gli
  0,8 mA che il sorgente dà per 50 Ω di R128. Si rifà in L62b.
- **La potenza dei diodi** si ricava a calcolo, ~8 mW: il deck non la misura.
- **Il secondo guasto non è simulato** (come in L45a).

## Che cosa resta, e a chi

- **L62b**:
  - i diodi in `gain_block()`, il sottocircuito, il disegno;
  - i quattro modi e i guasti dei diodi sul banco di L62a col blocco del sorgente;
  - la regressione dei deck veloci, V4 a caldo e P7;
  - la chiusura di NC-062.
- **Dopo L62b**: L45d2b2 legge i massimi e la dissipazione col blocco a diodi.
