# ADR-090 — Quattro diodi in serie di riserva al moltiplicatore di Vbe, nelle otto istanze del blocco

Data: 2026-10-19 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Risponde a NC-062** (PR-22, P7 di ADR-021): il rimedio scelto; si costruisce e si verifica in L62b.
- **Non tocca ADR-042 / ADR-054** (il riposo a ~20 mA, R128 1,58 kΩ): a blocco sano i diodi non conducono.
- **Non tocca ADR-082 punto 4** (Q127 in SOT-223, l'accoppiamento termico in rame col finale NPN).
- È la stessa logica di ADR-086 (la ridondanza nel blocco) applicata al moltiplicatore: un guasto
  singolo non deve lasciare una parte fuori dai suoi limiti.

## Contesto

Quattro guasti singoli del moltiplicatore di Vbe spengono Q127: emettitore aperto, base-emettitore
in corto, R129 in corto, R128 aperta. La corrente del VAS entra allora nelle basi dei finali, che ne
fanno 0,28–0,58 A. L62a li ha rifatti sul blocco di oggi (`data/2026-10-19/L62a/`, cinque posizioni
del canale): sono quelli di L45a.
- I finali vanno a **181–183 °C con 27 °C d'aria e 213–216 °C con 60 °C** (P7 vuole ≤ 125 °C).
- Le 22 Ω d'emettitore arrivano a 1,7–7,5 W (vincolo di BOM ≥ 0,34 W).
- Al jack non arriva niente (0,4 mV) e la scheda resta sotto 1 A: il sorvegliante non interviene.

## Decisione

In ognuna delle otto istanze di `gain_block()` vanno **quattro 1N4148 (DO-35, il modello D1N914 come
D102 / D103) in serie fra NX e NY**, anodo verso NX, in parallelo al moltiplicatore. L'utente, alla
domanda coi numeri del banco: **«Quattro diodi»**. Il sorgente, il sottocircuito, il disegno e la
verifica sono di **L62b**.

## Perché

Sul banco di L62a (`sintesi.csv`, `blocco_sano.csv`, `temperatura.csv`):
- **I quattro guasti dentro i limiti**: il riposo si ferma a 41,7–42,8 mA per finale (spread ~3,0 V).
  I finali stanno a 64–65 °C con 27 °C d'aria e a **97–98 °C con 60 °C**; le 22 Ω a 0,039–0,041 W.
  Nessuna parte del blocco supera i suoi limiti in nessuna delle cinque posizioni. Ogni diodo dissipa
  ~8 mW (a calcolo).
- **I guasti dei diodi non peggiorano niente**: un diodo aperto toglie la riserva e non cambia il
  blocco. Un diodo in corto lascia tre diodi che a 2,0 V conducono poco: il riposo resta a
  19,7 / 20,9 / 22,1 mA a 27 / 60 / 90 °C, contro i 20,5 / 21,9 / 23,1 del blocco di oggi.
- **A blocco sano i diodi non si vedono**:
  - il riposo cambia di −0,05 mA (−0,09 / −0,13 a 60 / 90 °C);
  - il margine di fase di V1 cambia al più di 0,05° (tb_loop, tb_loop_blockA, tb_loop_bufferfissa,
    tb_idss_loop);
  - in P7 le cifre sono uguali (finale 0,362 W, 83 °C con 60 °C d'aria).
- **La letteratura**: Elliott (ESP, Project 03) lascia i diodi nel circuito «as a fail-safe» contro il
  servo di bias che si apre. Self (Trimodal, *EW+WW* luglio 1995) usa lo stesso principio con un
  moltiplicatore («the lowest voltage wins»).
- **Il costo**: 32 parti sulla scheda audio (522 → 554).

## Alternative scartate

- **Il secondo moltiplicatore di guardia** (Self; Q160 + 2,7 kΩ / 1 kΩ). Tiene i quattro guasti a
  94–95 °C e costa 24 parti, ma tre suoi guasti singoli fanno crollare il riposo a 0–7,6 mA: il suo
  transistor in corto collettore-emettitore, la resistenza alta in corto, la bassa aperta. Il blocco
  lavora allora in classe B, con la distorsione d'incrocio. I diodi non hanno guasti così.
- **Il limitatore di corrente sulle 22 Ω** (un transistor per finale, ~72 mA, 48 parti). Tiene i
  guasti a 121–123 °C, al bordo dei 125. Con il mute e col corto all'uscita (P7) taglia la corrente dei
  finali da 214 a 118 mA e porta il PNP a 0,52 W: riaprirebbe il funzionamento in mute che ha dato
  NC-070. Un suo guasto porta il VAS a 135 °C. Non c'è una finestra fra la corrente che il mute chiede
  e quella che P7 permette.
- **Un dissipatore sui finali**: per 2,48 W con 60 °C d'aria servono ≤ 26 °C/W giunzione-aria
  (≤ ~24 °C/W di dissipatore) su 16 finali. In più le 22 Ω da 7,5 W andrebbero cambiate con resistenze
  da 10 W o più. Va contro i vincoli meccanici dell'assieme (L49b) e non salva le resistenze.
- **Una resistenza fissa sul moltiplicatore**, **un fusibile o una PTC per stadio**, **meno corrente
  nel VAS**, valutati solo a calcolo dalla ricerca di L62a:
  - la resistenza (~220 Ω) ruberebbe ~9 dei 10,7 mA al moltiplicatore;
  - la PTC peggiora il disaccoppiamento dei rail e non protegge le 22 Ω nel tempo d'intervento;
  - per scendere sotto ~0,1 A il VAS andrebbe a 1–2 mA.
- **Uno stato riconoscibile dal sorvegliante**: non serve. Coi diodi ogni parte resta nei suoi limiti,
  la prima delle due strade che NC-062 ammette.

## Da riaprire se

- In L62b, col blocco nel sorgente, i diodi conducono a blocco sano più di qualche µA a 60 °C d'aria
  (il riposo si sposta di più di 0,5 mA), o V4 a caldo esce.
- Il riposo del blocco cambia (R128, la corrente del VAS, i finali): lo spread nominale si avvicina
  ai ~2,6 V a cui quattro diodi conducono, o se ne allontana tanto che un guasto supera ~0,6 W per finale.
- Il prototipo mostra il moltiplicatore e i diodi a temperature diverse da quelle del banco (i diodi
  vicino ai finali, per esempio), o diodi con una Vf diversa dal modello D1N914.
