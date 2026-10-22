# ADR-097 — I guasti rifatti: R153 sdoppiata, i corti dei 5 V affidati alla protezione del regolatore, l'impulso della cella alla scelta della parte, il calore del blocco in un lotto dedicato

Data: 2026-10-22 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Estende ADR-087**: la resistenza di collettore dell'inseguitore davanti al VAS resta il suo limite
  di corrente, ma in due metà in serie.
- **Precisa ADR-075 / ADR-094** sulle righe «i 5 V a massa» di L45c2: restano «i 5 V persi», con la
  potenza del regolatore scritta.
- **Precisa ADR-086** sulla cella RC: la cifra d'impulso delle due 20 Ω è quella dell'alimentatore di
  oggi; la parte resta da scegliere (NC-075).
- **Riapre il rimedio del calore della scelta 1**, che ADR-072 affidava al rivelatore (i rail spenti) e
  che con ADR-081 era sparito senza tornare all'utente: va a un lotto dedicato, prima della sintesi.

## Contesto

L45d2b3b1, le corse dei guasti singoli sul circuito di oggi (`data/2026-10-22/L45d2b3b1/`, README).
I banchi provati prima su casi noti: il calore ridà L62b cella per cella (897 celle), la Stax ridà
L60d2 (306 celle), l'alimentatore ridà L45d2b2b2 (punto fisso e firmware uguali), P7 ridà L45d2b2c
(29 400 celle) e la cifra di L60d2 su R153 (0,4112 / 2,006 W).

- **R153 in corto.** P7 sul blocco di oggi, col mute inserito o la principale in corto: Q146
  (MMBT5401, SOT-23) **0,39 W medi, 216 °C con 60 °C d'aria contro 150 °C**. Il mute inserito è una
  condizione d'uso: è un guasto singolo di gravità 5. I diodi di ADR-095 non lo toccano.
- **C536 in corto** (fra U504 e U512): l'uscita di U504 a massa, 0,25 A con 12 V ai capi, **2,99 W,
  ~246 °C a calcolo** in SOT-223 (62 °C/W). Il MCP1703A ha lo spegnimento termico a 150 °C
  (DS20005122B), che il modello comportamentale non ha. Lo stesso vale per i corti dei 5 V a massa di
  L45c2 (C517, C519, C525, C530, R517, R518), contati finora solo come «i 5 V persi».
- **La cella RC in corto** sull'alimentatore di oggi: ciascuna 20 Ω **11,1 W di picco, 1,09–1,28 J
  in ~0,25 s** (il sorgente diceva 0,69 J).
- **Il calore del blocco.** 16 modi portano una parte del blocco oltre i limiti con 60 °C d'aria e i
  rail ideali: l'aiuto dello specchio Q148 fino a 5123 °C (R149 in corto, ~12,6 W), lo specchio 574 °C,
  il VAS fino a 308 °C, i diodi del riferimento con R101 in corto. In L45a li fermava il rivelatore che
  spegneva i rail (ADR-072, «col calore»); ADR-081 ha tolto il rivelatore e rimesso davanti all'utente
  le scelte 6, 8, 9 e 10, non queste righe.

## Decisione

Parole dell'utente (2026-10-22), alle quattro domande:

1. **«Resistenza sdoppiata»**: R153 diventa due 2,4 kΩ in serie (R153 + R160 sul blocco del file),
   4,8 kΩ in tutto, nelle otto istanze. Con una metà in corto: **Q146 0,029 W, 72 °C** (simulato,
   P7 sul blocco di oggi con 2,4 kΩ). L'altra opzione era Q146 in SOT-223, ~108 °C a calcolo.
2. **«Accettare la protezione»**: i corti dei 5 V a massa restano «i 5 V persi» (il micro si spegne,
   i relè cadono, tutto in sicurezza); il regolatore che porta il corto si protegge con lo spegnimento
   termico dichiarato dal costruttore. La potenza (2,99 W) si scrive nella riga.
3. **«Alla scelta della parte»**: R144 / R152 con un impulso dichiarato ≥ 1,3 J in 0,25 s, 11,1 W di
   picco; NC-075, maggiore, si chiude alla scelta della parte come NC-073.
4. **«Lotto dedicato»**: i rimedi dei 16 modi del calore si studiano e si misurano in un lotto apposta,
   **L45d2b3b2**, prima della sintesi (che diventa L45d2b3b3). NC-042 resta aperta.

## Perché

- **R153 sdoppiata** tiene il limite di ADR-087 anche col guasto di una metà, con un margine di 78 °C,
  e non tocca l'impronta dell'inseguitore. Il SOT-223 avrebbe lasciato la dissipazione e affidato il
  margine a una Rth di piazzola non dichiarata dal costruttore.
- **Lo spegnimento termico** è il modo in cui un regolatore integrato è fatto per sopravvivere a un
  corto in uscita; un limite in più davanti avrebbe portato una parte e i suoi guasti per un caso che
  il circuito già mette in sicurezza.
- **L'impulso della cella** dipende da una curva che solo il datasheet della parte scelta dà.
- **Il calore** chiede un progetto (un limite di corrente per blocco, un fusibile ripristinabile, o
  altro, coi loro effetti su PSRR e rumore), non una correzione: un lotto suo.

## Alternative scartate

- **Q146 in SOT-223** (punto 1): sopra.
- **Una resistenza davanti a U504** (punto 2).
- **Una parte da impulsi scelta ora** (punto 3).
- **I rimedi del calore in questo lotto**, o **prima lo stato dopo la parte bruciata** (punto 4): la
  seconda resta una strada per il lotto dedicato.

## Da riaprire se

- La regressione o V1 col blocco sdoppiato si spostano oltre quanto 4,8 contro 4,7 kΩ spiega.
- Il datasheet del MCP1703A scelto non dichiara la protezione termica, o la dichiara solo come
  transitoria.
- Il lotto del calore sceglie un rimedio che cambia le correnti dei rail del blocco: allora la cella
  RC e R153 si rimisurano.
