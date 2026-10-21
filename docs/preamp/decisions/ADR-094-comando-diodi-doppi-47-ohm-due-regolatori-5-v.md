# ADR-094 — Il comando dei relè e la logica: diodi di bloccaggio doppi, 47 Ω davanti a Q503, resistenze sdoppiate, due regolatori a 5 V in serie

Data: 2026-10-21 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- Realizza **ADR-075** (scelta 4 di `data/2026-10-14/L45d1/scelte_L45d2.pdf`), di cui era la parte
  rimasta a L45d2b.
- **Supera la lettera di ADR-075 su due punti**, entrambi per decisione dell'utente coi numeri:
  - il limite di corrente non è «una resistenza o un fusibile nel ramo dei clamp, o un MOSFET che
    regga il limite di U503», ma due diodi in serie più una resistenza davanti a Q503;
  - il limitatore sui 5 V non è «uno zener o un TVS con un fusibile ripristinabile», ma un secondo
    regolatore in serie.
- Lo schema delle resistenze sdoppiate è quello di **ADR-087** (R112 / R144 nel blocco).
- Conserva Δ (**ADR-045**), P9 (b) (**ADR-046**) e il bilancio dello standby di **NC-037**.

## Contesto

Dal banco dell'alimentatore di L45d2b2b2 (`data/2026-10-20/L45d2b2b2/`, README). Le righe di ADR-075
(D505, D506, D508 in corto, la bobina di K501 in corto, R503, R510, R512 in corto, U504 in corto fra
ingresso e uscita) sono state corse per la prima volta, ciascuna alle tre reti, con una sonda di
corrente sui pin delle parti, controllata su un caso noto.

- **Il ~1 A di L45c2 non era la cifra giusta.**
  - Col 2N7002 del banco i MOSFET del comando prendono 2,9–3,1 A di picco, 22–36 W, perché la tenuta
    da 2200 µF su VRELAY_REG si scarica nel corto.
  - Col 2N7002 tarato sul datasheet (Nexperia Rev. 7, fig. 5: ~0,7 A con 4,5 V sul gate) la corrente
    si ferma a 0,87–0,89 A, ma con ~11 V sul MOSFET: ~9–11 W.
  - Il 2N7002 ammette 1,2 A per 10 µs e 0,26 W continui con 60 °C d'aria.
- **A rete +10 % D506 in corto resta acceso per sempre**: VRELAY_REG non scende sotto gli 11,0 V del
  sorvegliante, e nessuno se ne accorge. Q501 a 6,4 W, lo zener D507 in diretta a ~1 W.
- **Il firmware riparte**: legge la caduta come un buco di rete (§ 4.5) e rifà l'accensione, e il
  corto si ripresenta a ogni ripartenza.
- **D508, D505 e la bobina di K501 in corto perdono Δ**: il guadagno si muove 1,8–3,8 ms prima che il
  jack si apra, **6,56 mV, ~70 dB SPL** al jack principale.
- **Le resistenze in corto portano le parti oltre i loro limiti**:
  - R503 in corto: LM4040 a 0,62 W, contro 20 mA e 0,22 W ammessi; U504 al limite a 2,4 W; la
    logica a ~2,5 V;
  - R510 in corto: Q504 a 4,8–7,6 W, contro 0,18 W;
  - R512 in corto: Q504 a 133–149 °C col β = 100 del modello generico; un BC847B tira di più.
- **U504 in corto fra ingresso e uscita**: V5 = 12,0 V contro i 6,0 V di massimo assoluto
  dell'ATtiny3216.

## Decisione

Parole dell'utente (2026-10-21): «Diodi doppi + 47 Ω», «Due regolatori in serie». Le resistenze
sdoppiate erano nella domanda come parte comune.

1. **Ogni diodo di bloccaggio dei comandi è due 1N4148 in serie**: D506 + D530 (MUTE_CMD), D508 + D531
   (PERMIT_CMD), D505 + D532 (la bobina di K501). Con un diodo in corto l'altro blocca.
2. **R552, 47 Ω (2 W assiale), fra la bobina di K501 e il drain di Q503**, fuori dall'anello del
   flyback. Limita la bobina in corto a VRELAY_REG / 47 Ω.
3. **R503, R510, R512 sdoppiate in serie**: 2 × 1 kΩ (R503 + R553), 2 × 11 kΩ (R510 + R554),
   2 × 110 kΩ (R512 + R555). I valori totali e le soglie non cambiano.
4. **Due MCP1703A-5002 in serie**: U504 su V5_PRE, U512 da V5_PRE a V5, con C536 da 1 µF in mezzo.
   Uno in corto fra ingresso e uscita lascia l'altro a regolare.

Il guardiano dello stato di riposo (`check_relay_safe_state.py --timer`) riconosce ora un drain che
raggiunge il comando attraverso una resistenza. Si rifiuta inoltre di lasciar fuori in silenzio un
2N7002 che non riconosce: il falso `falsi/psu_q503_non_riconosciuto.net` lo prova.

## Perché

| Riga (alle tre reti) | Oggi | **Questa** (il banco sul sorgente, `seq/sorgente/`, 45 corse) |
|---|---|---|
| D506 / D508 / D505 in corto (ciascuna metà) | 0,87–3,1 A, 9–36 W nel 2N7002; a +10 % acceso per sempre (6,4 W); Δ perso, ~70 dB SPL | **0 mA in più** (la corrente normale delle bobine) |
| bobina di K501 in corto | 0,89–3,1 A in Q503, 10,6–36 W; Δ perso, ~70 dB SPL | **0,24 A**, Q503 0,156 W (≤ 114 °C); R552 2,7 W per ~0,2 s (≤ 0,56 J); il sorvegliante entro 1 ms, il jack prima dei 10,6 V, Δ 17,1 ms; ~16 dB SPL (catena sull'opzione) |
| R503 / R510 / R512, ciascuna metà in corto | LM4040 0,62 W; Q504 4,8–7,6 W / fino a 149 °C | LM4040 2,2 mA; Q504 < 1,1 mW |
| U504 o U512 in corto fra IN e OUT | V5 12,0 V | **V5 5,000 V** |
| il rilascio del jack, Δ (perdita di rete) | 17,4 ms, Δ 17,3 ms | 17,5 ms, Δ 17,1 ms |
| MUSICA all'accensione | 747 ms dall'interruttore | uguale |
| la tenuta di VRELAY a rete −10 % (≥ 25 ms) | 46,4 ms | **51,2 ms** (la bobina di K501 assorbe meno) |
| V5 a regime / standby dal secondario di T2 | 5,00 V / 96,17 mW | 4,98 V / 96,04 mW |
| le righe di ADR-074, i regolatori dei rail a regime | — | uguali a L45d2b2b1 (entro 1e-5) |

- **Le alternative portate all'utente erano fuori.** Coi tre MOSFET robusti (DMN6075S, 60 V, 2 A) lo
  zener di bloccaggio in diretta prende 8,3 A di picco. Col solo Q503 robusto la bobina in corto
  scarica C523 a 14,7 A, 137 W, oltre i 12 A del MOSFET. Un MOSFET forte sposta il problema, non lo
  limita.
- **La lettera di ADR-075 sui 5 V non regge** (dai datasheet, `limiti_parti.csv`). Uno zener da
  5,6 V con un fusibile ripristinabile da 0,12 A prenderebbe ~6 W per fino a 0,2 s, contro 0,38 W.
  A 1 A V5 non è garantita sotto i 6,0 V. Nessun TVS trovato ha insieme ≤ 1 µA a 5 V e un
  bloccaggio sotto i 6,0 V.
- **Il bloccaggio sale di un diodo**: al peggio 12 + 25,6 + 1,7 ≈ 39,3 V contro i 60 V del 2N7002.
  È un calcolo: il banco ha bobine resistive. Il rilascio dei relè si accorcia, non si allunga, e Δ
  perde 0,1–0,2 ms.
- **La bobina di K501 a 10,6 V (88 %)** invece di 12: sopra il 70 % che il banco suppone (il datasheet
  della G2RL non è in `vendor/`), e 41 mW in meno alla bobina.

## Alternative scartate

- **I MOSFET robusti** (la seconda via di ADR-075): fuori, sopra.
- **Diodi doppi + MOSFET robusto su Q503**: fuori sulla bobina in corto, 14,7 A.
- **Una resistenza nel ramo dei clamp**: limita, ma dissipa a guasto latente (≥ 0,3 W continui per
  tenere il bloccaggio sotto i 60 V) e lascia scoperta la bobina di K501. Ragionata, non corsa.
- **Zener + fusibile sui 5 V** (la lettera di ADR-075): fuori, sopra.
- **Lasciare i 5 V alla revisione del micro (L54)**: il micro oggi si guasta con quel corto.

## Da riaprire se

- Il datasheet della resistenza scelta per R552 non regge 2,7 W per 0,2 s (0,56 J) ripetuti alle
  ripartenze del firmware: si sceglie una parte più robusta, non un altro valore senza rifare la
  bobina in corto.
- Il datasheet della G2RL-2A dà una tensione d'eccitazione sopra 10,4 V (11,76 × 360 / 407: con R552
  e VRELAY_REG al −2 %).
- Il riesame del micro (L54) cambia il micro con uno che regge 12 V sull'alimentazione (la clausola
  di ADR-075): U512 si può togliere.
- Il datasheet dell'MCP1703A, o la misura, dà in caduta (V5_PRE ≈ V5) una corrente di riposo che
  rompe il bilancio dello standby di NC-037.
- Le bobine vere misurano un rilascio dei relè del jack che, col bloccaggio più alto di un diodo,
  cambia Δ oltre quanto chiede P9 (b).
