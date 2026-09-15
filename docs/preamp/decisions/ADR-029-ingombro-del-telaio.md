# ADR-029 — Ingombro del telaio: l'impronta del Technics SU-9070, alto 3U

Data: 2026-09-15 · Stato: accettata

## Contesto

Nessun requisito limitava le dimensioni. P1–P5 (ADR-010) dicono telaio unico,
alimentatore a bordo, toroidale, due PCB e ventilazione, ma senza un limite non
si può dire se i PCB ci stanno. L'apparecchio prende il posto di un Technics
SU-9070 (ADR-001), nella stessa libreria.

## Decisione

Parole dell'utente, 2026-09-15: altezza «3U», profondità «come il technics»,
«metti i limite di ingombro e un paio di modelli come esempio».

**Ingombro massimo: L ≤ 450 mm · A ≤ 130 mm · P ≤ 367 mm.**

- **Larghezza e profondità** sono quelle del SU-9070, **450 × 92 × 367 mm**,
  misurate con la stessa convenzione: manopole davanti e cavi dietro non
  sporgono più di oggi. È un'interpretazione dell'orchestratore, dichiarata
  all'utente.
- **L'altezza** è quella di un 3U con frontale da 10 mm, piedini esclusi.
- **Il requisito è un ingombro, non un modello.** Due esempi che ci stanno:

  | Modello | Esterni L × P × A (mm) | Interni utili (mm) |
  |---|---|---|
  | Modushop Pesante 03PN, 3U | 435 × 305 × 122; frontale da 10 mm, 450 × 130 | 415 fra i fianchi; profondità e altezza interne non lette |
  | Audiophonics, alluminio con dissipatori | 430 × 315 × 120, dissipatori compresi | **330 × 300 × 112** |

- **I PCB si verificano sulle misure interne** del contenitore scelto, e il
  contenitore si sceglie **entro G2**.

## Perché

- **La libreria ospita oggi il SU-9070**: la sua impronta è lo spazio che c'è.
  Una seconda fonte dà 369 mm di profondità; si prende il valore minore.
- **3U è una scelta dell'utente.** Va nella direzione di ADR-010, che vuole la
  ventilazione «prevista, non sperata»: la scheda audio dissipa **6,45 W** a
  riposo (L17, NC-029) contro i 3-4 W di P5, e il SU-9070 è alto solo 92 mm.
- **L'ingombro da solo non basta ai PCB**, e i due esempi lo mostrano: quasi la
  stessa impronta, 415 contro 330 mm di larghezza interna.

Le misure sono lette il 2026-09-15:
- SU-9070: <https://audio-database.com/TechnicsPanasonic/amp/su-9070-e.html>;
- Pesante 03PN: <https://modushop.biz/site/index.php?route=product/product&product_id=162>
  e <https://hifi2000.shop/site/en/catalog/pesante> (415 mm interni, frontale
  da 10 mm alto 130);
- Audiophonics:
  <https://www.audiophonics.fr/en/aluminium-boxes-cases/100-aluminium-diy-chassis-with-heatsink-for-audio-amplifier-430x315x120mm-p-10523.html>
  (179 € IVA inclusa).

## Alternative scartate

- **2U come il Technics**, fino a 92 mm: scartato dall'utente.
- **Altezza doppia**, fino a 184 mm (per esempio Pesante 4U, 167 mm): l'utente
  l'aveva ammessa, ha scelto 3U.
- **Profondità 400** (Pesante 03P400, 405 mm): oltre il SU-9070.
- **Un modello fissato**: l'utente vuole un ingombro con esempi.

## Da riaprire se

- **L30** mostra che un 3U non smaltisce la dissipazione dentro i 60 °C
  d'ambiente di ADR-021.
- **Nessun contenitore** entro l'ingombro contiene i due PCB (P4) con le
  distanze della sezione rete (P2).
- **Cambia lo scaffale**, o una misura dal vero del SU-9070 smentisce i dati
  pubblicati.
