# L45d2b3b2a — il calore dei guasti del blocco: lo stato dopo, i rimedi, la scelta (2026-10-22)

Lotto di **NC-042** (prima di G1). Prima parte di L45d2b3b2, divisa dall'utente all'inizio: **«Due
parti»** (qui lo stato dopo, i rimedi misurati e la scelta; il sorgente e le verifiche in L45d2b3b2b).
Decisione **ADR-099**. Dati: `data/2026-10-22/L45d2b3b2a/` (README). **Il circuito non cambia.**

## Il problema

Quindici guasti singoli del blocco di guadagno portano una parte oltre i limiti, con 60 °C d'aria e i
rail regolati (ADR-097 punto 4). Li fermava il rivelatore di continua spegnendo i rail (ADR-072); dal
giorno in cui il rivelatore è uscito (ADR-081) non avevano rimedio.

## Il banco

Il banco del calore di L45d2b3b1, importato e puntato qui, **provato prima sul suo caso noto**: il
blocco su cui b1 aveva corso i quindici ridà le sue tabelle, **5920 celle su 5920**. Sul blocco di oggi
(R153 sdoppiata) i quindici sono ancora tutti fuori, con le stesse cifre.

## Che cosa resta quando la parte brucia

Simulato in due giri, la parte bruciata aperta o in corto:

- **aperta**, ferma il danno in circa metà dei casi: l'aiuto dello specchio aperto chiude i quattro
  guasti dello specchio, ma coi diodi del riferimento aperti il danno passa al carico del VAS (211 °C);
- **in corto**, lo propaga quasi sempre: l'aiuto in corto porta lo specchio a 493–577 °C, e con R149
  anch'essa in corto le due 20 Ω della cella RC a **45 W** ciascuna; il VAS in corto porta il finale
  NPN a 309 °C.

Lasciare bruciare non è un rimedio.

## I rimedi misurati

Ogni guasto ha un meccanismo, e quasi tutti hanno lo stesso: una parte prende base o corrente da un
nodo che niente limita. Sei varianti del blocco, ciascuna sui quindici guasti, sul riferimento sano e sui
guasti delle sue parti nuove, nelle cinque posizioni; poi la regressione dei 21 deck veloci, P7, il
punto di lavoro a caldo.

| Variante | Oltre i limiti | Il blocco sano |
|---|---|---|
| 10 kΩ sul collettore dell'aiuto | 9 su 15 | margine −0,2°, rifiuto delle alimentazioni −0,4 dB |
| resistenze sdoppiate e diodi del riferimento doppi | 10 | sposta il punto di lavoro (finali −3 %, lo specchio verso il ginocchio di ADR-067) |
| limite di corrente del VAS | 11 | margine +0,3…+0,8° |
| le tre insieme | 3 | come la seconda |
| 1 kΩ sul collettore della sorgente di coda | 13 | — |
| **aiuto + VAS + coda + R101 in due** | **2** | margine 43,1 → 43,6°, ±0,34 dB, rumore invariato, P7 non peggiora |

Con la quarta combinazione il più caldo è il VAS, **123 °C contro 125** (119 °C coi dispositivi del
banco a 60 °C: a caldo il limite scende). A riposo il limitatore del VAS conduce al più 7,5 µA a 90 °C,
e il blocco resta quello di oggi entro 3 µA e 0,04 mV.

**Restano i corti dei finali**: l'altro finale porta 1,4–1,6 W, e in TO-220 senza dissipatore va a 149 /
160 °C (il massimo assoluto è 150 °C). Col dissipatore Ohmite WA-T220-101E — in produzione, ~20 °C/W a
1 W — **99 / 95 °C** a calcolo, con 2 °C/W d'interfaccia come ipotesi.

La letteratura trovata è poca e di seconda mano sul limite del VAS; nessuna fonte sulla protezione di
uno stadio di piccolo segnale da un guasto singolo. I rimedi vengono dal meccanismo, giudicati sui numeri.

## La scelta

L'utente, alle due domande coi numeri: **«Quattro rimedi»** e **«Dissipatore scelto ora»** (ADR-099).
Restano per la seconda parte: R169 da almeno 0,5 W (0,236 W con R107 in corto), i dissipatori al
potenziale del collettore, l'accoppiamento termico del moltiplicatore col finale da rifare, la Stax dei
casi oltre 100 ms (ADR-098), V4 a caldo.

## Non conformità

**NC-042 avanza**: i quindici guasti del calore hanno un rimedio scelto, simulato su varianti; si chiude
sul sorgente (L45d2b3b2b) e nella sintesi (L45d2b3b3). Nessuna voce aperta o chiusa.
