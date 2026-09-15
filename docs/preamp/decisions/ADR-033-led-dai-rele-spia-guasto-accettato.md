# ADR-033 — I LED del trim restano sui relè spia K9 e K10: il guasto di un solo relè è un caso noto e accettato

Data: 2026-09-15 · Stato: accettata

## Contesto

ADR-027 §3 legge lo stato vero del trim da due relè spia, **K9 e K10**, con le
bobine in parallelo a quelle dei relè di segnale K7 e K8. Un guasto che separa un
relè dal suo gemello fa mostrare al LED uno stato che il segnale non ha: una
bobina interrotta, oppure un contatto che non commuta. Dopo L20 all'utente è stata
proposta l'altra strada: leggere i LED dai relè che portano il segnale.

## Decisione

**Si tiene ADR-027 §3 com'è.** Il guasto di un solo relè resta un **caso noto e
accettato**. Vale anche per i tre LED del guadagno di ADR-030, letti dai poli
liberi dei relè ausiliari, se L36 li realizza.

## Perché

- **È una preferenza dell'utente, e va registrata come tale.** Voce «Dopo L20» di
  `STATE.md`: l'utente voleva lo stato vero. Sentite le conseguenze, **tiene la
  soluzione attuale**, «anche per i LED di ADR-030».
- **Le conseguenze che l'utente ha pesato:**
  - relè a 3-4 poli non verificati;
  - LED e audio nello stesso relè;
  - L16 in parte da rifare.
- **I G6KU-2F-Y di segnale non hanno poli liberi.** Hanno due poli, uno per
  canale (ADR-027 §2).
- **Il lavoro verificato resta valido**:
  - il 2e prova l'interblocco sulla netlist;
  - il budget delle bobine resta **126,6 mA** a 5 V (ADR-027).

## Alternative scartate

- **LED letti dai relè di segnale**: servono relè a più poli non verificati (T8),
  LED e audio sullo stesso relè, e L16 da rifare in parte.
- **Nessuna spia, LED dalla posizione del comando**: fuori mute può mentire, ed è
  già scartata da ADR-027.

## Da riaprire se

- **Il prototipo, o un'analisi dei guasti**, mostra che il disaccordo fra un relè
  e il suo gemello è frequente, o che porta a regolare male il trim.
- **Un relè a 3-4 poli** passa T8 e rende a costo zero leggere lo stato dal relè
  di segnale.
- **L36 cambia gli ausiliari** del guadagno, o non si fa.

Precisa **ADR-027** §3 e **ADR-030** §2. Non ne supera nessuna.
