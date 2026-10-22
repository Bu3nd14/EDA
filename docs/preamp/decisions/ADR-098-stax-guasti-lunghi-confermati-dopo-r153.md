# ADR-098 — I guasti più lunghi sulla Stax restano accettati dopo il cambio di R153; D102 / D103 aperti al lotto del calore

Data: 2026-10-22 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Risponde al «Da riaprire se» di ADR-089** («R153 cambia valore»), scattato con ADR-097 (R153 da
  4,7 kΩ a due 2,4 kΩ in serie). **Conferma ADR-089**: il tetto della Stax resta 150 ms (ADR-086).
- **Aggiunge al lotto del calore** (ADR-097, punto 4) i due diodi del riferimento dello stadio
  d'ingresso aperti.

## Contesto

L45d2b3b1 (`data/2026-10-22/L45d2b3b1/`, `stax_lunghi.csv`, `script/confronta_lunghi.py`): i 121 casi
che sul blocco di prima tenevano la Stax sopra 0,87 V per più di 100 ms, rifatti sul blocco di ADR-097
col banco di L60d2 (provato su sei casi di L60d2, 306 celle uguali):

- **si spostano al più di 0,4 ms**; nessuno oltre 150 ms (una corsa fermata subito dopo il guasto,
  Q122 in corto, rifatta in gear: 118,1 ms come prima);
- il peggiore, **D102 o D103 aperti nel blocco A: 141,7 ms, 145,8 col condensatore a +5 %**. In L60d2
  erano 125,1 / 128,5 ms: li hanno allungati i diodi aggiunti dopo (ADR-090, ADR-095), non R153. Il
  margine sul tetto scende da 21,5 a **4,2 ms**;
- gli stessi due guasti sono fra i sedici del calore (l'aiuto dello specchio Q148 a 416 °C con 60 °C
  d'aria).

## Decisione

Parole dell'utente (2026-10-22): **«Confermare, D102/D103 al calore»**.

1. ADR-089 resta: i guasti più lunghi sulla Stax sono accettati, tutti entro 150 ms.
2. D102 / D103 aperti vanno nel lotto dedicato al calore: un rimedio per il loro calore può accorciare
   anche la Stax, e si misura lì.

## Perché

- Il cambio di R153 non sposta la Stax (≤ 0,4 ms): la clausola chiedeva di guardare, e i numeri non
  cambiano la decisione.
- Il margine più stretto viene da due guasti che hanno già un lavoro aperto: si studiano una volta sola.

## Alternative scartate

- **Confermare senza altro**: il margine di 4,2 ms resterebbe senza nessuno che lo guardi.
- **Un rimedio sulla Stax ora**: prima di sapere che cosa il lotto del calore cambia nel blocco.

## Da riaprire se

- Un guasto del blocco sulla Stax supera i 150 ms, in simulazione o sul prototipo.
- Il rimedio del lotto del calore cambia la corrente o il punto di lavoro dello stadio d'ingresso: si
  rifanno i casi oltre 100 ms (`script/genera_stax_lunghi.py`).
