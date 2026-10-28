# ADR-104 — I diodi dei nodi da megaohm del temporizzatore a bassa perdita, e i cali lenti di rete lasciati alla ritenuta

Data: 2026-10-28 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Completa ADR-102** al punto 2 (il temporizzatore): D535, D541 (su AT_T2S, 2,7 MΩ) e D536 (su AT_PGT)
  non sono più BAT54 ma diodi al silicio a bassa perdita (BAS416); R571 da 820 kΩ a 1 MΩ. Le funzioni, gli
  altri RC, la ritenuta e R585 (ADR-103) restano.
- **Non cambia ADR-102** sul comportamento della ritenuta: un calo di rete che porta i regolatori fuori
  regolazione con la rete presente la fa scattare, come un guasto. Era implicito; da oggi è misurato e
  scelto.

## Contesto

L54b3a, la prima parte della robustezza al banco (`data/2026-10-28/L54b3a/`, README; report
`reports/2026-10-28-L54b3a-robustezza-rete-fronti-rimbalzi.md`). Due prove sono fallite contro i criteri
scritti prima delle corse:

1. **I cali lenti di rete.** Un calo che porta i regolatori fuori regolazione con la rete ancora presente
   (sotto ~77 % della nominale: −15 % partendo da −10 %, già per 0,1 s; −30 % a quasi ogni rete) fa
   scattare la ritenuta: l'apparecchio resta spento finché non lo si spegne e riaccende dal frontale. 14
   cali su 27 alle tre reti. Il criterio voleva la musica di nuovo ≥ 500 ms dopo la rete.
2. **I BAT54 del costruttore** (modello di Diodes Inc., perdita ~0,65 µA, dentro il massimo del datasheet
   DS11005: 2 µA a 25 V e 25 °C) su AT_T2S armano la ritenuta a 1,07 s invece che a ~1,9 s, prima che i
   rail siano su: **la ritenuta scatta a ogni accensione**. Il modello generico del banco (IS 20 nA)
   lo nascondeva. A 60 °C anche un BAT54 tipico perde ~1–2 µA.

## Decisione

Parole dell'utente (2026-10-28), alle due domande coi numeri:

1. **«Lasciare com'è»** per i cali lenti. Nessuna parte in più: dopo un calo profondo l'apparecchio resta
   spento in modo sicuro (il mute prima dei rail, K501 aperto) e si riaccende dal frontale. (La domanda
   diceva 16 cali e «14 su 16» col rimedio: ricontati su `an_rete.csv` sono 14 e 12 su 14. Detto
   all'utente nel resoconto del lotto.)
2. **«Diodi a bassa perdita, R571 1 MΩ»**: D535, D541, D536 diventano BAS416 (silicio a bassa perdita,
   SOD-323); R571 1 MΩ. Sul banco il BAS416 è il modello BAV199 di Diodes Inc. (`models/diodes/
   bav199.lib`, IS 59 pA), dichiarato: il modello proprio del BAS416 non è nel repository, e il pezzo si
   conferma alla distinta (L58).

## Perché

**I cali** (`an_rete.csv`, `an_qvrete.csv`, `confronta_q_*.txt`, `confronta_qv_*.txt`):

| | i cali che spengono l'apparecchio (su 27) | i 31 casi della sicurezza di L54b2 | parti |
|---|---|---|---|
| **com'è (scelto)** | 14 | uguali | — |
| soglia sul grezzo dei relè (12,7 V) | 2 (−30 % per 2 s, rete −10 % e 0 %: il timeout dell'accensione) | uguali | ~4 |
| soglia sui tre grezzi | 2 | **il corto davanti al regolatore + non fa più scattare la ritenuta**: K501 resta chiuso | ~8 |

- I regolatori escono quando la valle del grezzo + scende a 16,2 V; a rete −10 % stabile è 17,88 V.
  Quello dei relè esce per primo (12,37 V contro 13,07 V a −10 %): la soglia sul suo grezzo avrebbe
  avuto 0,37 V di margine.

**I diodi** (`an_lp.csv`, `an_bp_prova.csv`, coi transistor e i BAT54 del costruttore):

| | l'accensione | la musica dopo un buco di 20 ms (≥ 500 ms) | il timeout, la ritenuta nel guasto |
|---|---|---|---|
| BAT54 (com'era) | la ritenuta scatta | — | — |
| bassa perdita, R571 820 kΩ | musica a 1038,5 ms | **461 ms** | giusti |
| **bassa perdita, R571 1 MΩ (scelto)** | musica a 1149,7 ms | **559 ms** | giusti (K501 a 129,1 ms nel guasto) |

La VF più alta del diodo al silicio (~0,75 V contro ~0,3 V) fa ripartire AT_PGT più in alto: R571 lo
compensa. AT_T2S svuotato a ~0,75 V resta sotto VREF (2,5 V).

## Alternative scartate

- **La soglia sul grezzo dei relè**: ~4 parti per 12 cali su 14, e un margine di 0,37 V a rete −10 % da
  difendere con le tolleranze.
- **La soglia sui tre grezzi**: perde lo scatto nel corto davanti al regolatore + (l'energia in R550).
- **I diodi a bassa perdita con R571 com'è**: 461 ms dopo un buco di 20 ms.
- **I nodi a impedenza dieci volte più bassa** (270 kΩ / 10 µF): meno sensibili alla perdita, ma con
  condensatori X7R da 10 µF di tolleranza e calo in tensione larghi; non misurato.

## Da riaprire se

- L'apparecchio va usato dove i cali profondi sono frequenti, o il prototipo mostra spegnimenti a rete
  bassa: la soglia sul grezzo dei relè è misurata (`--qualifica v:12.7`).
- Le tolleranze o i 60 °C (L54b3b) portano la musica dopo un buco di 20 ms sotto i 500 ms, o la perdita
  dei diodi rimasti BAT54 (D533, D534, D537, su nodi da ≤ 200 kΩ) sposta un tempo oltre i suoi limiti.
- Il BAS416 non si trova alla distinta: un diodo con perdita ≤ 5 nA a 25 °C e VF ≤ 0,9 V a 1 mA.
