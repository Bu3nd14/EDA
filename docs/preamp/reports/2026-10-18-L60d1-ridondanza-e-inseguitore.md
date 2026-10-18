# L60d1 — la ridondanza nel blocco, e la causa della musica a mute inserito (2026-10-18)

Prima parte di L60d, divisa dall'utente all'inizio («Due parti»). Decisioni: **ADR-086** (costruita
qui) e **ADR-087** (nuova). Dati: `data/2026-10-18/L60d1/` (README lì). Cifre di modello, ngspice 47,
i modelli di `models/`.

## Le decisioni dell'utente

All'inizio, su NC-070 (la principale fuori in 16 verdetti di V2 col blocco di L56):
**«Maggiore, prima del congelamento»**, **«In questo lotto»**, e sul lotto **«Due parti»**.
Dopo la diagnosi: **«4,7 kΩ sul collettore»**, **«Media su ogni campione»**, **«Rimedio qui, metodo
dopo»** → ADR-087.

## 1. La causa di NC-070

**La corsa di riferimento «sempre in mute»** (`g10sempre_1k_iii`, dal deck versionato, fermata a
2 s), identica salvo il sottocircuito del blocco:

| | Jack principale, picco | 1 kHz sul jack | Uscita del blocco B: media / 1 kHz |
|---|---|---|---|
| Blocco di oggi (L56) | **0,58 mV** (come L60c2) | 0,71 µV | −1,06 V / 5,5 V |
| Blocco di prima di L56 (L46b) | **1,34 µV** | 0,83 µV | −0,07 V / 6,5 V |

La causa è il blocco di L56. La musica non passa: i 0,58 mV sono **due impulsi per periodo, larghi
134 ns, a fase fissa** (50° e 320° del ciclo).

**Da dove vengono** (`script/sonda_blocco.py`, i nodi interni del blocco B). Col mute inserito il
blocco B vede 47 Ω e il condensatore d'uscita chiuso a massa con 0,1 Ω; a +10 dB con l'ingresso
massimo non riesce a pilotarli. L'inseguitore davanti al VAS (Q146, ADR-067) conduce **73–84 mA**
(1,1 mA a riposo) e porta il VAS in saturazione profonda. Quando la richiesta si inverte, in ~1 µs
l'inseguitore si spegne, il VAS esce di colpo dalla saturazione e il finale salta da 75 a 127 mA. Il
nodo dopo il condensatore si muove a ~8·10⁴ V/s; per gli 0,1 pF del contatto aperto verso il jack
(69 kΩ, 1e-18 F) fanno 0,1 pF × 8·10⁴ V/s × 69 kΩ ≈ 0,55 mV, il picco misurato. Prima di L56 la base
del VAS la pilotava lo specchio, che non dà più della corrente della coda (4 mA).

**Perché V2 li conta** (`script/b1_confronto.py`, limitations #60). `v2_metodo.py` dirada i punti a
2 µs, ricampiona a 96 kHz con un'interpolazione cubica senza anti-aliasing e filtra:

| Riferimento «sempre in mute», da 0,5 s | B1 filtrato | B2g grezzo |
|---|---|---|
| Blocco di oggi, metodo di V2 | **132,2 µV** (la cifra di L60c2) | 263,7 µV |
| Blocco di oggi, media su ogni campione | **3,3 µV** | 5,9 µV |
| Blocco di prima di L56, i due metodi | 0,93 µV | 0,93 µV |

Il verdetto dipendeva da dove cadeva il campione. Misurata come la vedrebbe un convertitore, la
musica a mute inserito è ~30 dB sotto il tetto di 100 µV. NC-070 resta aperta fino alla matrice
rifatta col metodo nuovo (L60d2).

## 2. NC-071: l'inseguitore senza limite, e P7 che non lo guardava

`tb_mute_corto.cir` (P7) salva e misura Q122, Q125, Q127 e il resto del blocco, ma **non i due
transistor di L56**. Con le loro misure aggiunte (`script/p7_l56.py`): Q146 nel blocco B a +10 dB,
ingresso massimo, col mute inserito o col corto sulla principale, **0,41 W medi, 2,0 W di picco,
82 mA** contro i 0,31 W di un SOT-23; in ogni altro caso 0,033 W. È un uso normale (il mute con la
musica). Aperta e chiusa qui.

**I rimedi provati** (`script/varianti_follower.py`, `follower/riassunto.csv`):

| | Oggi | **4,7 kΩ sul collettore** | 10 kΩ sul collettore | 1 kΩ in base al VAS | 2,2 kΩ in base |
|---|---|---|---|---|---|
| Q146 in P7, media / picco | 0,41 / 2,0 W | **0,027 / 0,075 W** | 0,010 / 0,014 W | 0,060 / 0,19 W | 0,053 / 0,14 W |
| Margine minimo B / A / buffer | 65,2 / 68,4 / 65,3° | **64,8 / 68,0 / 64,9°** | non converge | 61,8 / 64,4 / 61,6° | 57,5 / 58,9 / 56,6° |
| B1 con la media, 0,3 s | 2,7 µV | **1,1 µV** | — | 1,1 µV | — |

Clip, recupero (0,65 µs) e THD di modello uguali ovunque. Con 10 kΩ il punto di lavoro non converge
in parti della matrice d'anello (#57). L'utente: **«4,7 kΩ sul collettore»** → R153.

## 3. La ridondanza (ADR-086) nel sorgente

Nelle otto istanze, aggiunte in fondo a `gain_block()` (i designatori di prima non cambiano, #22):
R150 in parallelo a R109; R112 a 200 Ω con R151 da 200 Ω; R144 a 20 Ω con R152 da 20 Ω; e R153 di
ADR-087. R111 resta 100 Ω da sola: i due lati della coppia sono uguali al nominale, e la continua
d'uscita e la distorsione non cambiano (sotto).

**Il valore in parallelo a R109** (`script/prepara_shunt.py`, `shunt/margini_shunt.csv`). I deck
d'anello aprono R109 per rompere l'anello (limitations #61): il guasto si prova con l'iniezione dal
lato di FB, controllata a 100 Ω (i margini dei deck entro 0,07°).

| Col guasto (R109 aperta), posizioni che contano | 4,7 kΩ | 10 kΩ | 22 kΩ |
|---|---|---|---|
| Blocco B, 0 dB, cavo al jack | **62,7°** | 59,9° | 54,1° |
| Blocco A, cavo ≤ 1 nF | **65,4°** | 62,2° | 55,6° |
| Buffer fisso, cavo al jack | **62,6°** | 59,7° | 53,5° |

A blocco sano i tre valori danno margini identici. **4,7 kΩ** (ADR-087 precisa ADR-086).

**Il calore di R144 e R152** col 1000 µF in corto: metà ciascuna del picco di 22,5 W e degli 1,37 J
di L45d2b1, **11,3 W e 0,69 J**. Che la parte lo regga resta una domanda per la distinta (G2).

## 4. La regressione del blocco

I 21 deck veloci (`regressione/`, `prima` = il blocco di `main`, `dopo` = il blocco finale), tutti
con esito 0.

| | Prima | Dopo |
|---|---|---|
| V1, margine minimo sulle posizioni che contano (B / A ≤ 1 nF / buffer) | 65,16 / 68,38 / 65,31° | 64,76 / 67,97 / 64,88° |
| E5 | 5,103 µV | 5,102 µV |
| E3, E4 principale / fisse | 108,2 kΩ, 60,02 / 53,10 Ω | uguali |
| Continua all'uscita del blocco | −2,87 mV | −2,92 mV |
| V3: clip, recupero, continua al jack | +13,34 / −13,85 V, 0,65 µs, +19,3 mV | +13,29 / −13,85 V, 0,65 µs, +4,6 mV |
| Classe A | invariata | invariata |

**V4 a caldo** (`script/caldo.py` di L56, VAS e carico in SOT-223, aria 27 / 57 °C, rame e piazzola
minima): **0 casi fuori su 48**, margine ≥ 2,7 dB, IMD −131,8 dB, gradino della coda oltre +23,6 %:
uguale al blocco di L56 alla cifra.

**P7 sul blocco finale**: Q146 0,027 W, Q148 0,024 W, R153 0,043 W (0,17 W di picco). Il blocco non
satura più il VAS, e col corto sulla principale spinge più corrente: **la 47 Ω della principale
1,28 W** (0,99 prima; il commento del sorgente diceva ancora 1,13 W, la cifra di L46a) e **le 22 Ω
d'emettitore 0,333 W** (0,298). I vincoli per la distinta salgono a ≥ 1,3 W e ≥ 0,34 W a 60 °C.
Q132 e Q125 scendono (0,362 e 0,142 W).

**Una cella di E4 falsa** (limitations #59): con il blocco a ridondanza, `tb_e4_uscite` aveva una
cella (trim 0, attenuatore al 25 %, +3 dB) col canale spento, 5,57 A dal rail positivo. L'accensione
in transitorio nella stessa cella arriva allo stato vivo; con un `.nodeset` sui VPF le 135 righe
tornano a quelle di prima alla sesta cifra.

## 5. Netlist, disegno, suite

- La scheda audio da **490 a 522 parti** (+4 per blocco); `confronta_netlist.py` di L60c2: cambiano
  solo R112 / R144 di ogni istanza e le quattro parti nuove sui loro nodi. ERC di SKiDL 0 errori.
- Il disegno del blocco con R150–R153 e il collettore di Q146 su NFC: 55 dispositivi su 55.
- `run_tests.sh`: vedi `STATE.md`.

## Cose trovate per strada

- **P7 calcola la potenza di R123 con 91 Ω**, il valore di prima di ADR-054 (oggi 56 Ω):
  `tb_mute_corto.cir`, `x123`. La cifra è a favore di sicurezza (×91/56), ma è sbagliata. Per L60d2.
- `esegui.sh` e `regressione.sh` copiati contano i figli con `${#jobstates}` (limitations #58).

## Che cosa resta a L60d2

NC-069: i guasti di L45a sulle parti nuove (aperta e corto di R150–R153, R151, R152) e P10 sulla
Stax sulla tabella di ADR-086, R109 aperta sotto 150 ms. NC-070: `v2_metodo.py` con la media
(ADR-087), autotest e sabotaggi, la matrice di V2 rifatta.
