# 2026-10-29 — L58a, i test point, la FMEA delle parti nuove del temporizzatore, la distinta

**Documento datato: non si riscrive.** Due sessioni: **L58a1** (2026-10-29, i test point e la distinta)
e **L58a2** (2026-11-01, le righe della FMEA). Le voci vivono in `../NONCOMPLIANCE.md`. Dati e comandi
in `../data/2026-10-29/L58a/` (`distinta/README.md`; il banco in `psu/`, V2 in `v2/`). Decisioni:
**ADR-107**, **ADR-108**, **ADR-109**. Cifre di modello: ngspice 47, il banco dell'alimentatore di
L54b3b (regolatori comportamentali, limitations #80), i modelli del costruttore dei comparatori, della
ritenuta e dei diodi (ADR-104).

## Perché

L58 nasce da una richiesta dell'utente dopo L45d1 («test point per diagnosi») e dai rinvii di ADR-102 /
ADR-104 / ADR-105: le righe della FMEA delle parti che il temporizzatore a comparatori ha aggiunto, e le
conferme alla distinta del BAS416 e dei condensatori dei ritardi. L'utente ha diviso L58 in **L58a**
(test point, FMEA, distinta) e **L58b** (l'autodiagnosi), e L58a in due sessioni per il budget.

## 1. I test point (L58a1, ADR-107)

`Connector:TestPoint` con l'anello Keystone 5000 / 5001 (`TestPoint_Keystone_5000-5004_Miniature`), mai
`Conn_01x01` (`check_relay_safe_state.py` lo leggerebbe come un jack), valore `TP_<rete>`.

- **Scheda audio** (`preamp_audio.py`): TP1–TP9 al cablaggio (rail, `VRELAY`, `RLY_RET`, `MUTE_CMD`,
  `PERMIT_CMD`, `MUTE_SW`), e una coppia uscita / massa per blocco, TP101…TP802.
- **Alimentatore** (`psu.py`): TP501–TP517 — rail, `VRELAY` dai due lati di Q505, V5, `MUTE_G` /
  `PERMIT_G` / `PERMIT_T`, i comandi dei relè, `RLY_RET`. Niente sul lato di rete.
- Il vincolo per G2: ogni test point accanto al suo riferimento. Non entrano nei deck SPICE. ERC come
  prima; i disegni (`sheet_kit.testpoint()`) verificati nei due sensi.
- **Cinque reti della scheda audio cambiano nome a ogni rigenerazione**, coi piedini uguali. Lo fa anche
  il sorgente di prima dei test point (limitations #74: SKiDL tiene uno dei nomi di due reti unite, e
  quale dipende dalle parti); i sinonimi del disegno lo coprono.

## 2. La distinta (L58a1, ADR-108)

`distinta/README.md` (`bom-component-manager`, codici letti su DigiKey e LCSC il 2026-10-29).

- **BAS416** (D534 / D535 / D536 / D541): Nexperia BAS416,115, in produzione, LCSC 14 080 pz, perdita
  max 5 nA a 25 °C. VF a 1 mA 0,9 V, sul limite di ADR-104, letta solo su riassunti del datasheet.
- **Nessun C0G da 1 µF a montaggio superficiale** (1206 / 1210 / 1812 / 2220): il «Da riaprire se» di
  ADR-105. La scelta dell'utente: **C548 / C552 in film di polipropilene a foro** (TDK B32672L2105J003),
  **C553 in C0G 2220**, **C518 in C0G 1206**. Valori invariati: gli angoli di L54b3b restano.

## 3. Il banco della FMEA

La copia del banco di L54b3b in `psu/`, sulla netlist coi test point: `TestPoint` mappato a niente
(limitations #84). In `modi.py` i sette eventi del temporizzatore (`EVENTI_TIMER`: accensione dallo
standby, accensione a freddo, guasto del rail − in musica, buco di rete di 20 ms, perdita di rete,
spegnimento dal frontale, accensione con un rail morto), presi interi dai casi di sequenza, e i dieci
modi aperto / in corto di R585 e dei quattro BAS416 (`RIGHE_TIMER`), **latenti dall'istante zero**.
`lista_l58a.py` aggiunge la **perdita** di ciascun BAS416 (1 µA in più del modello, **un'ipotesi**: una
giunzione danneggiata, ~12 × gli 80 nA del datasheet a 150 °C; nessuna tabella dà un modo «perdita»,
ADR-070) e la **deriva** di R585 al doppio (66 kΩ).

**I casi noti** (`lista_prova.txt`, `an_prova.csv`; le forme d'onda di L58a1 erano perse col suo
worktree, rifatte): la base ridà `v_sorgente` di L54b3b (la musica a **1209,3** ms dallo standby e
**2045,6** ms da freddo); **R585 aperta** porta la base di Q513 a **0,898 V** all'accensione (ADR-103:
0,89 V).

**La lista**: 112 corse (7 basi, 70 guasti, 28 perdite, 7 derive), **112 con `ok.txt`, nessun ripiego
numerico** (limitations #81), nessuna rifiutata. `analizza_mc.py` → `an_l58a.csv`; `confronta_l58a.py`
applica i criteri scritti di L54b3b (ogni verdetto come la base del suo evento; permesso ≥ 16,9 ms
dopo il mute; musica ≥ 500 ms dopo un buco; K501 ≥ 50 ms dopo il permesso; ritenuta armata dopo
l'alimentazione buona; base di Q513 ≤ 0,45 V dove la base non scatta) → `confronto_l58a.csv`.

**Un artefatto, non un guasto** (limitations #85): in otto accensioni a freddo `arm_pg_ms` esce
−1383,5 ms, «la ritenuta armata prima dell'alimentazione buona». I deck coi guasti sondano anche VREF,
la base no, e all'istante zero AT_T2S sta sopra VREF di qualche nanovolt. La salita vera (`psu/armo.py`)
è quella della base, 2431 ms. Restano veri i −70,7 / −69,4 ms delle perdite su D535 / D541.

## 4. Le righe della FMEA

`fmea_alimentatore.csv` (`psu/fmea_l58a.py`), con le colonne di `L45d2b3b3/fmea_dopo.csv`. La
probabilità dai tassi di `classi_l45c2.py`: R 0,5 FIT (aperta 0,59, deriva 0,36, corta 0,05), diodo di
segnale 1,0 FIT (deriva 0,58, aperto 0,24, corto 0,18); la perdita prende la quota della deriva
(dichiarato). **Ogni modo sta sotto 1 FIT: probabilità 1.**

| Parte | Modo | Effetto misurato | G | R | Priorità |
|---|---|---|---|---|---|
| R585 | aperta | dalla rete col frontale acceso la ritenuta scatta (0,898 V): non si accende; dallo standby sì | 2 | 2 | bassa |
| R585 | **in corto** | **la ritenuta cieca**: col rail − che cade o un rail morto all'accensione il mute si inserisce come oggi, ma K501 resta chiuso | **4** | 3 | **alta** → accettata (ADR-109) |
| R585 | deriva a 66 kΩ | nei sette eventi niente; a 60 °C col comparatore a 2,2 V la ritenuta scatta da freddo (1,06 V) | 2 | 2 | bassa |
| D534 | aperto / perdita | niente | 1 | 3 | bassa |
| D534 | in corto | non suona mai dallo standby, la ritenuta scatta da freddo | 2 | 2 | bassa |
| D535 | aperto | niente | 1 | 3 | bassa |
| D535 | in corto | la ritenuta scatta a ogni accensione | 2 | 2 | bassa |
| D535 | perdita | la ritenuta si arma 70,7 ms prima dell'alimentazione buona: non si accende da freddo | 2 | 2 | bassa |
| D536 | aperto | la musica all'alimentazione buona (537 ms dalle rampe, non 1198); dopo un buco 21,2 ms (criterio ≥ 500); al jack **2,63 µV, ~2 dB SPL** | 2 | 3 | bassa |
| D536 | in corto | la musica a 616 ms dalle rampe; dopo un buco 78,5 ms; al jack **2,75 µV, ~2 dB SPL** | 2 | 3 | bassa |
| D536 | perdita | dopo un buco 462,2 ms (criterio ≥ 500), su rail fermi | 2 | 3 | bassa |
| D541 | aperto | solo margine: base di Q513 0,540 V allo spegnimento dal frontale (0,471 a 60 °C), non scatta | 1 | 3 | bassa |
| D541 | in corto | la ritenuta scatta a ogni accensione | 2 | 2 | bassa |
| D541 | perdita | come D535 (−69,4 ms) | 2 | 2 | bassa |

**«Non si accende»** vuol dire mute inserito, rail spenti o musica che non parte: nessun colpo.

**D536 al jack, misurato.** Il criterio dei 500 ms dopo un buco (ADR-104) cade, e all'accensione il
mute si sblocca coi rail ancora in salita (il + a 13,57 V su 14,98). `v2/genera_v2_l58a.py` è la copia
del banco di V2 all'accensione di L45d2b2a, con le rampe e l'istante di sblocco presi dalle corse di
L58a: **8 corse su 8 passano la guardia**; il picco allo sblocco **2,63 / 2,75 µV** al jack principale
(la base, che sblocca su rail fermi, 7,7 nV), ~2 dB SPL a 1 m con l'ancora di L54b2 (3,52 µV = +4,4),
30 dB sotto la soglia di V2. Dopo un buco di 20 ms i rail non si muovono affatto (14,980 / −14,967 V,
`psu/rail_rilascio.py`): lo sblocco anticipato è quello normale. Solo rampe nominali: la tolleranza delle
rampe sposterebbe anche l'alimentazione buona, e chiederebbe il temporizzatore di nuovo.

## 5. R585 in corto, all'utente

Il «Da riaprire se» di ADR-102: un guasto singolo del temporizzatore che toglie la ritenuta, e che il
firmware (che leggeva i rail) copriva. P9 (b) non è rispettato dopo un secondo evento. Con VRELAY_REG
perso K501 si apre comunque a 50 ms.

**I rimedi provati prima della domanda** (spezzare R585 in serie: il corto di un pezzo ne lascia una
parte). La ritenuta scatta solo con ≥ ~30 kΩ rimasti, e il nominale non regge sopra ~40 kΩ:

| R585 | nominale: a freddo, 60 °C, comparatore 2,2 V (≤ 0,45 V) | un pezzo in corto: guasto del rail −, K501 |
|---|---|---|
| 33 kΩ (oggi) | 0,300 V | chiuso |
| 2 × 16,5 kΩ | — | 16,5 kΩ: chiuso |
| 3 × 11 kΩ | — | 22 kΩ: chiuso |
| 3 × 12 kΩ | 0,316 V | 24 kΩ: aperto a 133,3 ms a 25 °C, **chiuso a 0 °C** |
| 2 × 33 kΩ | **1,06 V, scatta a vuoto** | 33 kΩ: aperto |
| **4 × 10 kΩ** | **0,336 V** (rete ±10 % uguale) | 30 kΩ: aperto a 129,4 ms (rete ±10 %), 126,8 a 0 °C |

Le corse a 0 °C del guasto sono col ripiego numerico (limitations #81), 33 / 30 / 24 kΩ tutte sullo
stesso metodo.

**La scelta dell'utente** (2026-11-01): **«Accettarlo, dichiarato»**, e la voce **«Minore»**. ADR-109:
il circuito non cambia; **P9 (e)**, caso accettato; **NC-077** aperta, minore, si chiude alla scelta
delle parti o al layout.

## Che cosa non so

- Lo spegnimento dal frontale **col rail già caduto** e R585 in corto: non corso (ADR-109 lo dichiara).
- Il calore di un guasto di rail col toroidale acceso a tempo indefinito: è il primo «Da riaprire se»
  di ADR-109.
- La perdita da 1 µA è un'ipotesi, non un dato: nessuna tabella dà il modo.
- V2 di D536 con le rampe a ±20 %: non corso.
- La VF del BAS416 a 1 mA, e la deriva del film scelto: solo riassunti (ADR-108).

## Le voci

- **Aperta NC-077** (minore): R585 in corto, la ritenuta cieca; accettata in P9 (e), ADR-109.
- Nessuna voce chiusa. **18 voci aperte, 1 bloccante** (NC-044, per G2).

## Rifare

`<L>` = `docs/preamp/data/2026-10-29/L58a`, dalla radice del repository:

```sh
/usr/bin/python3 -I <L>/psu/lista_l58a.py > <L>/lista_l58a.txt
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_l58a.txt 6        # ~25 min
/usr/bin/python3 -I <L>/psu/analizza_mc.py --te=3.0 <L>/an_l58a.csv <L>/seq/l58a_base/* <L>/seq/l58a/* <L>/seq/l58a_perdita_*/* <L>/seq/l58a_r585x2/*
/usr/bin/python3 -I <L>/psu/confronta_l58a.py <L>/an_l58a.csv <L>/confronto_l58a.csv
/usr/bin/python3 -I <L>/psu/fmea_l58a.py <L>/fmea_alimentatore.csv
# le prove di R585 e di D541: lista_r585_serie.txt, lista_r585_66k.txt, lista_r585_serie2.txt,
# lista_r585_t0.txt, lista_r585_rete.txt, lista_t60_d541.txt, con corri_lista_an.sh e analizza_mc.py
/usr/bin/python3 -I <L>/v2/genera_v2_l58a.py
/bin/zsh docs/preamp/data/2026-09-23/L29c/script/corri.sh <L>/v2/run <L>/v2/tb_v2_l58a.cir '^(l58_.*|g10sempre_lz_iii|g10mai_lz_iii)$' 8
/usr/bin/python3 docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py <L>/v2/run
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/script/analizza_par.py <L>/v2/run/manifest_sel.csv <L>/v2/run <L>/v2/run/analisi.csv 6
/usr/bin/python3 docs/preamp/data/2026-10-05/L47c2b1/script/verdetto.py <L>/v2/run/manifest_sel.csv <L>/v2/run/analisi.csv <L>/v2/run/verdetto.csv
```

Le forme d'onda (`*_out.txt`) e `v2/run/` non stanno nel repository: si rifanno.

## Il lotto dopo

**L58b**, l'autodiagnosi (ADR-076: la diagnosi del mute che non si inserisce, in hardware o all'utente).
Poi L66 (NC-076), L64, L65, G1.
