# ADR-112 — V4 sulla catena: ogni blocco si giudica al livello a cui lavora

Data: 2026-11-02 · Stato: accettata

## Contesto

V4 (ADR-055) fissa i tetti di THD a 20 kHz a un livello **in uscita**: 0,001 % a 0,2 V RMS, 0,01 % a
2 V. Il banco era il blocco da solo. NC-055 chiedeva la catena di un canale (selettore, blocco A,
trim, volume, blocco B; le due fisse dietro il blocco A). L67 l'ha misurata sul blocco di oggi
(ADR-111), a 27 °C e con ogni giunzione alla sua temperatura (`data/2026-11-02/L67/`). Con V4 letto
alla lettera:
- **la sorgente**, il blocco a guadagno unitario da 0 a 5,6 kΩ: 60 su 60 dentro, margine minimo 2,7 dB;
- **le fisse**: tutte dentro, margine ≥ 2,5 dB;
- **l'intermodulazione** CCIF sulla catena: 0 su 78 fuori, ≥ 10,8 dB sotto il tetto, ≤ −28 dB SPL a 1 m;
- **la principale col volume a metà**: 3 casi su 56 fuori a 20 kHz e 0,2 V, fino a 3,1 dB (0,001427 %,
  aria a 57 °C). Erano 2 in L56, e i cambi del blocco da allora non li spostano (0,001334 % identico);
- **la principale col volume a −10 / −20 dB**: fino a 14,2 dB sopra (0,005125 %).

Il meccanismo è quello di L53. La seconda armonica del blocco A cresce col suo livello, e il volume
la attenua insieme alla fondamentale: col volume a −20 dB la principale a 0,2 V porta la distorsione
del blocco A a 2 V. Ogni blocco, al livello a cui lavora, è dentro il tetto di quel livello.

## Decisione

**Sulla catena la THD a 20 kHz si giudica al livello a cui lavora ciascuna istanza**, con un tetto
che scala col livello fra 0,2 e 2 V RMS: **tetto(L) = 0,001 % × L / 0,2 V**. Ridà i due punti di
ADR-055. Alla principale la cifra della catena (A e B insieme) si confronta col tetto del livello più
alto lungo il percorso, max(livello del blocco A, livello alla principale). Il resto di V4 non cambia:
le armoniche dalla 5ª in su a −140 dB, l'intermodulazione a −110 dB, i livelli del banco del blocco.

Decisione dell'utente in L67: «Ogni blocco al suo livello». La formula del tetto e la verifica della
catena col livello più alto sono il modo di renderla decidibile.

## Perché

- **Con la regola, 0 casi fuori su 42 per blocco** a 20 kHz, in tutti e sette i blocchi corsi
  (`verifica_livello.csv`). Margine minimo 1,9 dB nella griglia di L56 (volume a metà, modo +3, aria a
  57 °C, 0,001132 % contro 0,00141 %) e 1,3 dB col volume basso (un caso a 2 V, già dentro con V4).
- **Il tetto proporzionale al livello è quello che ADR-055 aveva già scelto**: ×10 di livello e ×10 di
  tetto. Corrisponde alla seconda armonica, che domina qui (la THD della catena cresce col livello
  del blocco A, e dalla 5ª in su resta ≤ −149,7 dB).
- **Ciò che i casi fuori lasciavano è inudibile per livello e per frequenza**: seconda armonica di un
  tono a 20 kHz, quindi a 40 kHz, a ~2 dB SPL a 1 m col volume a metà e ~13 dB SPL nel peggiore. Il
  meccanismo, che in banda si vedrebbe come intermodulazione, sta ≥ 10,8 dB sotto il suo tetto ovunque.
- **Nessun costo sugli altri requisiti**: nessun componente cambia.

## Alternative scartate

- **Lasciare V4 com'è e accettare i casi per nome**: dava lo stesso circuito, ma una regola che nessun
  preamplificatore col volume dopo il primo stadio può rispettare. Col volume a −20 dB servirebbe un
  blocco A ~14 dB migliore di oggi a 2 V.
- **Il cascode pilotato sulle istanze a guadagno unitario** (la strada dell'architetto in L52): ~3 dB
  per il volume a metà e ~14 dB per il volume basso, con la topologia cambiata prima di G1. Il costo su
  margine di fase, rumore e calore non è stato misurato.
- **R_F adattata all'impedenza vista**: il meccanismo che l'avrebbe giustificata (un minimo della THD
  a R_S = R_F) non c'è. In L53, L56 e L67 la THD cresce in modo monotono con l'impedenza di sorgente.
- **Lasciare NC-055 aperta fino al prototipo**: bloccava G1 su una voce che il prototipo misurerebbe
  con lo stesso criterio ancora indeciso.

## Da riaprire se

- Sul prototipo la catena alla principale supera il tetto del livello più alto lungo il percorso:
  la somma di A e B non è quella del modello.
- Un'istanza lavora sopra 2 V RMS in un uso dichiarato (la regola si ferma lì, come ADR-055).
- Le prove d'ascolto (P6) trovano un'asprezza col volume basso: il criterio misura la cosa sbagliata.
- Il tetto complessivo di THD+N, da fissare sul prototipo (ADR-055), vuole un livello di catena
  invece che di istanza.
