# ADR-088 — V2 con la media su ogni campione, corretta per l'attenuazione della media

Data: 2026-10-19 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Precisa ADR-087** sul metodo di V2: dopo la media su ogni campione, una correzione a tre
  coefficienti toglie l'attenuazione che la media stessa porta alle frequenze alte. ADR-087 diceva
  che «sui segnali lisci [la media] è uguale al metodo di oggi»: è vero a 1 kHz, non a 20 kHz.
- Il resto di ADR-087, ADR-032 e ADR-063 resta: il filtro 20 Hz – 20 kHz, le finestre, B1, B2g, i
  tetti a 100 µV.

## Contesto

Scrivendo la media in `scripts/v2_metodo.py` (L60d2): la media di un segnale su un intervallo lungo
un campione, 1/96 kHz = 10,4 µs, ha guadagno sin(x)/x con x = π f / 96 kHz:

| | 1 kHz | 10 kHz | 14 kHz | 20 kHz |
|---|---|---|---|---|
| Media pura | −0,002 dB | −0,156 dB | −0,31 dB | **−0,63 dB** |
| Media con la correzione | +0,0003 dB | +0,024 dB | +0,032 dB | **0,000 dB** |

La matrice di V2 ha 28 corse a 20 kHz (su 155). La media pura le leggerebbe 0,63 dB più basse del
metodo di prima: il verdetto sui 20 kHz diventerebbe più ottimista per una scelta di calcolo, non
per il circuito.

## Decisione

La domanda all'utente (2026-10-19), posta coi numeri qui sopra: «Con la media su ogni campione, la
musica a 20 kHz che passa a mute inserito risulta 0,62 dB più bassa di quanto il metodo di oggi la
leggeva (a 1 kHz la differenza è 0,016 dB). Come la tratto?». La risposta: **«Correggere»**.
(Nella domanda la cifra a 1 kHz era sbagliata di un fattore dieci: è 0,0016 dB, la tabella sopra.
La scelta non ne dipende: a 1 kHz la differenza è comunque trascurabile.)

- Dopo la media, ogni campione è `(1 + 2a) m[k] − a (m[k−1] + m[k+1])`; ai due estremi resta la
  media. Il guadagno del filtro, 1 + 2a (1 − cos 2πf/FS), moltiplicato per quello della media vale
  1 **esatto a 20 kHz**: a = (x / sin x − 1) / (2 (1 − cos 2x)), x = π · 20 kHz / FS, **a = 0,0507**.
  In banda l'errore resta entro +0,032 dB (a 14 kHz).
- La finestra della media è centrata sul campione, [k/FS − 1/(2 FS), k/FS + 1/(2 FS)]: nessun
  ritardo, gli istanti di A e C restano quelli di prima.
- Il metodo di prima resta come colonna di confronto (`picco_puntuale_V`), come ADR-087 chiede.

## Perché

- **Uguale ai segnali lisci, anche a 20 kHz**: col filtro la media dà su un tono le cifre del
  metodo di prima entro 0,03 dB in tutta la banda (autotest T17: −0,0016 dB a 1 kHz e −0,0019 dB a
  20 kHz sulla griglia di ngspice), quindi i tetti di V2 non cambiano significato.
- **Gli impulsi stretti restano ridotti alla loro area**: il filtro ha tre coefficienti e guadagno
  al più 1,2 (a 48 kHz); sul treno di impulsi da 134 ns di L60d1 l'autotest T16 legge 3,28 µV
  contro i 3,13 µV dell'area ideale (il metodo di prima: 2,7 V).

## Alternative scartate

- **La media pura**: i 20 kHz 0,63 dB più ottimisti.
- **Il coefficiente che rende minimo l'errore su tutta la banda** (a = 0,0489): ±0,021 dB ovunque,
  ma −0,021 dB a 20 kHz; quello scelto è esatto dove la media sbaglia di più, ed è ciò che è stato
  chiesto all'utente.
- **Media su un intervallo più fine e decimazione con un filtro anti-aliasing vero**: più fedele a
  un convertitore, ma è un metodo nuovo, non la media di ADR-087.

## Conseguenze

- `scripts/v2_metodo.py`: `media_campioni()` con la correzione, `campiona()` coi due metodi,
  autotest T16 e T17, sabotaggi `senza_media` e `senza_correzione`.
- La matrice di V2 di L60d2 si legge con questo metodo.

## Da riaprire se

- Una misura su un convertitore vero del prototipo legge i 20 kHz, o gli impulsi, in modo diverso
  da questo metodo.
