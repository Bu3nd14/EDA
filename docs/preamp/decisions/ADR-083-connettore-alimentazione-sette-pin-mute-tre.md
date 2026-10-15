# ADR-083 — Il connettore dell'alimentazione a sette pin con due masse, quello del mute di nuovo a tre

Data: 2026-10-15 · Stato: accettata

**Rapporti con le decisioni precedenti.** Precisa **ADR-082 punto 2** («Due pin per il rail») sul
numero dei pin di massa e sul loro ordine; è una conseguenza di **ADR-081** (il rivelatore di continua
esce) sul connettore del mute, che **ADR-079** aveva portato a quattro pin. ADR-048 resta il contratto
dei connettori fra le schede.

## Contesto

L60b toglie il rivelatore e costruisce i due pin per rail di ADR-082. Restavano aperte due domande
che il prompt del lotto lasciava all'utente: quanti pin per la massa sul connettore dell'alimentazione
J1 (oggi quattro: +15 V, massa, −15 V, 12 V dei relè), e se il connettore del mute J4 resta a quattro
pin col quarto libero, dopo che `DC_FLT` se ne va, o torna a tre.

## Decisione

Parole dell'utente (2026-10-15, alle domande poste per nome):

1. **«Due pin di massa»** — **J1 a sette pin**, sulle due schede: 1 e 2 `VPLUS`, 3 e 4 `GND`,
   5 e 6 `VMINUS`, 7 `VRELAY`. Ogni rail e la massa passano su due pin e due fili in parallelo;
   `VRELAY` resta su un pin.
2. **«Torna a tre pin»** — **J4 di nuovo a tre pin**, come prima di L45d2b1: 1 `MUTE_CMD`,
   2 `PERMIT_CMD`, 3 `MUTE_SW`.

## Perché

- **La massa come i rail.** Un filo di massa aperto toglie alla scheda audio il riferimento dei due
  rail insieme: è lo stesso guasto singolo di un filo di rail aperto (scelta 8, 388–421 ms sulla
  Stax per il + in L60a), e due pin lo tolgono allo stesso costo — un pin in più sul connettore,
  nessuna parte attiva. Il guasto che resta è doppio.
- **L'ordine.** Le coppie stanno adiacenti, la massa in mezzo fra i due rail come prima; `VRELAY` in
  fondo, al posto del 4 di prima. Il controllo del cablaggio (`scripts/check_psu_harness.py`, 2j)
  legge tutti e sette i pin sulle due schede; nove sabotaggi (un pin per coppia aperto sulle due
  schede, le coppie incrociate, `VRELAY` persa) lo fanno fallire tutti
  (`data/2026-10-15/L60b/falsi/verdetti.txt`).
- **J4 a tre.** Un pin libero non serve a niente di deciso oggi; la diagnosi (L58), se ne vorrà uno,
  lo aggiungerà con la sua decisione. Tre pin sono il connettore di prima, già provato dal 2e e
  dal 2j.

## Alternative scartate

- **Un pin di massa** (sei pin): la decisione alla lettera, ma lascia la massa aperta come guasto
  singolo non coperto.
- **Tre pin di massa** (otto pin), uno anche fra il −15 V e i 12 V dei relè: separazione che oggi
  nessun numero chiede.
- **J4 a quattro col quarto libero**: un pin scollegato nel contratto, da dichiarare nel controllo
  del cablaggio, per un uso non deciso.

## Da riaprire se

- Il connettore scelto al layout (G2) non regge la corrente di un rail su un pin solo, quando l'altro
  della coppia è aperto (~0,3 A per rail oggi): allora la coppia è necessaria e non solo ridondante,
  e il guasto di un pin va rivisto.
- La diagnosi (L58) chiede un filo fra le schede.
