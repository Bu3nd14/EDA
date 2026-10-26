# ADR-073 — Il sorvegliante di un rail diventato cieco: accettata la riserva del firmware, che muta in 2,2 ms invece di 1 ms

Data: 2026-10-14 · Stato: superata da ADR-102 — il firmware esce; la riserva del sorvegliante cieco la fanno i comparatori del temporizzatore, in < 0,5 ms

**Rapporti con le decisioni precedenti.**
- È la **scelta 2** di `data/2026-10-14/L45d1/scelte_L45d2.pdf` (10 righe alte, L45c2).
- È una **deroga dichiarata** alla sola clausola di 1 ms di P9 (b), e la si scrive lì come caso
  accettato. **Il PRB non cambia**: PR-23 resta rispettato (vedi sotto).

## Contesto

Il sorvegliante dei rail (U505, due comparatori) rilascia `MUTE_CMD` entro 1 ms quando un rail scende
sotto |13,5 V| (P9 (b)). Se un comparatore diventa cieco (l'uscita aperta, l'alimentazione persa,
un partitore aperto o in corto) il guasto è **latente**: non si vede finché un rail non cade.
Quando cade, il firmware fa da riserva leggendo i rail dall'ADC e muta in **2,2 ms**. Al jack
restano **0,17 mV** (~38 dB SPL a 1 m) nel caso peggiore, sotto l'obiettivo di 2 mV (~60 dB). Le 10
righe sono a gravità 4 solo perché la clausola di 1 ms non è rispettata.

## Decisione

Parole dell'utente (2026-10-14): «Accettare la riserva del firmware».

Con un sorvegliante cieco, alla caduta di un rail **muta il firmware, in ~2,2 ms**. È un caso
accettato di P9 (b). Il circuito non cambia, e non si aggiunge un autotest.

## Perché

- **Il colpo resta sotto l'obiettivo, non solo sotto il tetto**: 0,17 mV contro 2 mV, cioè ~22 dB
  di margine. La clausola di 1 ms è un mezzo per arrivare a quel numero, e il numero regge.
- **Serve un doppio evento**: il comparatore cieco e poi la caduta di un rail. Il tasso della prima
  metà è 0,03–2,4 FIT per riga.
- **PR-24 regge**: la sicurezza contro il guasto singolo resta in hardware. Il firmware interviene
  solo quando l'hardware ha già un guasto latente.

## Alternative scartate

- **Un autotest all'accensione** (il firmware forza e legge il sorvegliante): sarebbe andato al
  lotto della diagnosi. L'utente non lo ha scelto. Resta disponibile se L58 lo trova a costo zero.

## Da riaprire se

- Una misura sul banco vero mostra la riserva del firmware più lenta di 2,2 ms, o un colpo al
  jack sopra 2 mV.
- Il firmware cambia in modo da non leggere più i rail dall'ADC (riesame del micro, L54).
