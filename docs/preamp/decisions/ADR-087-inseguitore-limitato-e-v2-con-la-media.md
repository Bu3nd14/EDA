# ADR-087 — L'inseguitore davanti al VAS con la resistenza di collettore, e V2 misurato con la media su ogni campione

Data: 2026-10-18 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Precisa ADR-067** (l'inseguitore davanti al VAS e l'aiuto sullo specchio, L56): il collettore
  dell'inseguitore va al rail negativo attraverso 4,7 kΩ, non diretto. Il resto di ADR-067 resta.
- **Precisa ADR-032 e ADR-063** (il metodo di V2): il ricampionamento a 96 kHz diventa la media del
  segnale sull'intervallo di ogni campione. Il filtro, le finestre, B1, B2g e i tetti restano.
- **Precisa ADR-086** sul valore: la resistenza in parallelo alla resistenza di gate del lato di
  retroazione è **4,7 kΩ**, non ~10 kΩ (sotto, «Il valore della ridondanza»).
- **NC-070** resta **maggiore, prima di G1**: la severità proposta in L60c2, confermata dall'utente.

## Contesto

L60d1 ha cercato la causa di NC-070 (la principale fuori in 16 verdetti di V2 col blocco di L56,
`data/2026-10-18/L60d1/`):

- La stessa corsa «sempre in mute» col sottocircuito di prima di L56 riporta il jack principale da
  0,58 mV a **1,34 µV**: la causa è il blocco di L56.
- La musica a 1 kHz non passa: la sua componente sul jack è 0,7 µV col blocco di oggi e 0,8 µV con
  quello di prima. I 0,58 mV sono **due impulsi per periodo, larghi 134 ns, a fase fissa**.
- Gli impulsi vengono dall'**inseguitore davanti al VAS** (Q146 sul blocco del file). Col mute
  inserito il blocco B vede 47 Ω e un condensatore chiuso a massa, e a +10 dB con l'ingresso massimo
  non riesce a pilotarli. Niente limita l'inseguitore: conduce fino a **82 mA** e porta il VAS in
  saturazione profonda; quando la richiesta si inverte, il VAS ne esce di colpo in ~1 µs, e il
  fronte di corrente passa per gli 0,1 pF del contatto aperto verso il jack.
- Lo stesso difetto ha una conseguenza vera: **P7 non aveva mai misurato Q146 e Q148**. Q146 dissipa
  **0,41 W medi e 2,0 W di picco** col mute inserito o col corto sulla principale (blocco B, +10 dB,
  ingresso massimo), contro i 0,31 W di un SOT-23. È NC-071.
- Il metodo di V2 trasforma gli impulsi in 132 µV: dirada i punti più vicini di 2 µs, ricampiona a
  96 kHz senza anti-aliasing con un'interpolazione cubica e filtra. Con la media del segnale vero su
  ogni intervallo di 10,4 µs (ciò che vedrebbe un convertitore col suo filtro) la stessa corsa dà
  **B1 3,3 µV e B2g 5,9 µV**. Sul blocco di prima di L56, dove il segnale è liscio, i due metodi danno
  la stessa cifra, 0,93 µV, cioè quella di L48b.

## Decisione

Le parole dell'utente (2026-10-18), alle domande poste per nome coi numeri qui sopra:
1. Sulla severità di NC-070: **«Maggiore, prima del congelamento»**; sul dove: **«In questo lotto»**.
2. Sul rimedio all'inseguitore: **«4,7 kΩ sul collettore»**.
3. Sul metodo di V2: **«Media su ogni campione»**.
4. Sul quando: **«Rimedio qui, metodo dopo»**: il rimedio in L60d1, il metodo e la matrice dei mute
   rifatta in L60d2.

- **R153 (sul blocco del file) da 4,7 kΩ fra il collettore dell'inseguitore e il rail negativo**,
  nelle otto istanze, aggiunta in fondo a `gain_block()`. A riposo ~5 V ai suoi capi (1,1 mA);
  sotto sovraccarico limita l'inseguitore a ~10 mA.
- **V2 con la media su ogni campione**: in `scripts/v2_metodo.py` (L60d2) ogni campione a 96 kHz è
  la media del segnale di ngspice, lineare a tratti e senza diradamento, sul suo intervallo. La
  lettura di oggi resta come colonna di confronto.

## Il valore della ridondanza

ADR-086 chiedeva ~10 kΩ in parallelo a R109. I deck d'anello rompono l'anello proprio al posto di
R109, quindi il guasto «R109 aperta» non lo provano; L60d1 l'ha provato spostando l'iniezione dal
lato di FB (`data/2026-10-18/L60d1/shunt/`, controllo del metodo con 100 Ω: i margini dei deck entro
0,07°). Con R109 aperta la resistenza in parallelo e la capacità della JFET mettono un polo nell'anello:

| Margine col guasto, posizioni che contano | 4,7 kΩ | 10 kΩ | 22 kΩ |
|---|---|---|---|
| Blocco B, cavo al jack | 62,7° | 59,9° | 54,1° |
| Blocco A, cavo ≤ 1 nF | 65,4° | 62,2° | 55,6° |
| Buffer fisso, cavo al jack | 62,6° | 59,7° | 53,5° |

A blocco sano i margini sono gli stessi per i tre valori. **4,7 kΩ**: anche col guasto il blocco tiene
i 60° di V1; in parallelo ai 100 Ω fa 97,9 Ω.

## Perché

- **4,7 kΩ sul collettore** (`data/2026-10-18/L60d1/follower/riassunto.csv`, blocco B):

  | | Oggi | 4,7 kΩ sul collettore | 1 kΩ in base al VAS | 2,2 kΩ in base |
  |---|---|---|---|---|
  | Q146 in P7, media / picco | 0,41 / 2,0 W | **0,027 / 0,075 W** | 0,060 / 0,19 W | 0,053 / 0,14 W |
  | Margine minimo (B / A / buffer) | 65,2 / 68,4 / 65,3° | **64,8 / 68,0 / 64,9°** | 61,8 / 64,4 / 61,6° | sotto 60° |
  | Jack in mute, B1 con la media | 2,7 µV | **1,1 µV** | 1,1 µV | — |

  Clip, recupero e THD di modello uguali. 10 kΩ scartata: il punto di lavoro smette di convergere in
  parti della matrice d'anello (limitations #57).
- **La media su ogni campione** misura quello che V2 chiede, la musica che arriva al jack, e non
  dove un campione cade su un impulso di 134 ns. Sui segnali lisci è uguale al metodo di oggi.
- **Rimedio qui, metodo dopo**: il rimedio cambia il blocco, e la regressione del blocco è di questo
  lotto; la matrice dei mute dura ~8 ore e va corsa una volta, col metodo nuovo, insieme ai guasti
  della Stax di L60d2.

## Alternative scartate

- **1 kΩ o 2,2 kΩ in serie alla base del VAS**: limitano anche loro, ma costano 3,4° di margine e
  più (61,6° sul buffer; sotto 60° con 2,2 kΩ).
- **Tornare al blocco senza inseguitore**: riapre ADR-067, che aveva tolto 12 casi su 12 di
  distorsione a caldo fuori.
- **Tenere il metodo di V2 com'è**: il verdetto dipende da dove cade il campionamento (col rimedio
  20–40 µV su 0,3 s, 132 µV senza), non da quanta musica passa.

## Conseguenze

- **Sorgente** (L60d1): R153 e il nodo del collettore; il disegno del blocco; le netlist (la scheda
  audio da 490 a 522 parti, con le tre resistenze di ADR-086).
- **P7** col rimedio: Q146 0,027 W, Q148 0,024 W, R153 0,043 W medi e 0,17 W di picco. Il blocco non
  satura più il VAS, quindi col corto sulla principale spinge più corrente: la 47 Ω della
  principale **1,28 W** (era 0,99) e le due 22 Ω d'emettitore **0,333 W** (era 0,298). I vincoli per
  la distinta (ADR-021) salgono a ≥ 1,3 W e ≥ 0,34 W a 60 °C.
- **NC-071** aperta e chiusa in L60d1. **NC-070** resta aperta fino alla matrice di V2 rifatta col
  metodo nuovo (L60d2).
- **L60d2**: `v2_metodo.py` con la media (ADR-032 / ADR-063 precisati qui), i suoi autotest e i
  sabotaggi; la matrice di V2 rifatta; i guasti di L45a sulle parti nuove e sulla Stax.

## Da riaprire se

- Sul prototipo l'inseguitore non tiene la distorsione a caldo misurata (il «Da riaprire se» di
  ADR-067), o la misura del jack col mute inserito mostra il fronte del VAS.
- La matrice di V2 col metodo nuovo trova la principale fuori: la causa non sarebbe più il metodo.
- Un controllo di P7 sui dispositivi di L56 trova un'altra parte del blocco non misurata.
