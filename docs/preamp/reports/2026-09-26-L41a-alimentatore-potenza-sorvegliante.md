# L41a — l'alimentatore: le decisioni, la potenza, `VRELAY`, il relè di rete e il sorvegliante (2026-09-26)

**Mandato**: NC-036 (bloccante per G2), prima parte di L41. Decisione: **ADR-048**. Dati:
`data/2026-09-26/L41a/` (README). Sorgente nuovo: `circuits/preamp/psu.py` → `psu.net`.

**Sintesi.** L'utente ha deciso sei cose, conversando e con le cifre davanti. L'alimentatore
esiste ora come sorgente: due trasformatori standard, rail lineari, `VRELAY` a 12 V con un
avvolgimento proprio, standby con un interruttore posteriore, sorvegliante in hardware. Il
temporizzatore (L41b) e il banco di L30 col circuito vero (L41c) mancano ancora. **NC-036 resta
aperta.** Durante il lotto sono emersi quattro difetti, tutti trovati prima di dare un numero:
- nel sorgente, il pad del TPS7A3301 era su IN;
- nella stima, due trasformatori a 13 V che non reggono la rete bassa;
- nel banco, gli `alter` che sopravvivono a `destroy all`;
- nel progetto, `VRELAY` non sorvegliata.

Ne è emerso anche un quinto problema, **aperto**: il consumo in standby (NC-037).

## 1. Le decisioni dell'utente (ADR-048)

Una alla volta. Ogni risposta con le sue parole:

| # | Domanda | Risposta | Numeri portati |
|---|---|---|---|
| 1 | Struttura | il piano approvato: `psu.py`, secondo PCB, controllo del cablaggio | — |
| 2 | Trasformatore | «2×15 V 50 VA standard» | margine della valle con rete −10 %: 2×12 −1,3 V, 2×13 −0,1 V, 2×14 +1,0 V, 2×15 +2,5 V |
| 3 | `VRELAY` | «non accetto uno switching, siamo troppo deboli sulla PSRR»; «avere due trafo standard?»; «si confermo» | 5 V lineare 2,7 W; 12 V dal rail + mette le bobine sul grezzo del rail debole; 12 V con avvolgimento proprio |
| 4 | Interruttore morbido | «mi piace la 3, ma é possibile avere un secondo switch sul retro…?»; «si confermo la 3 con l'interruttore posteriore» | tre forme; la 3 contraddice ADR-046 su una frase |
| 5 | Sorvegliante | «accetto la tua raccomandazione» | comparatore ±0,15 V contro zener ±0,7 V; rivelatore di rete ~15–20 ms contro 66–133 ms |
| 6 | Temporizzatore | «accetto l'ibrido» | micro per la sequenza, ordine `MUTE_CMD` → Δ → `PERMIT_CMD` in hardware |
| — | P5 | «si lo accetto» | ~17 W nominali, ≤ 20 W al peggio, ≤ 58 °C nel vano stretto |

**Due mie affermazioni sbagliate, corrette davanti all'utente prima della decisione:**
- nel piano avevo stimato che 2×13 V reggesse la rete bassa. La simulazione dice di no (−0,1 V);
- alla scelta A avevo scritto «il calore torna dentro P5». Rifatto il conto, era falso (20,2 W),
  e l'ho detto prima di scrivere l'ADR. P5 è cambiato con una decisione, non per inerzia.

## 2. Il circuito (`circuits/preamp/psu.py`)

- **La rete**:
  - modulo IEC posteriore con fusibile e interruttore bipolare, fuori scheda (J510);
  - F501 per il primario di T2, sempre alimentato;
  - K501 G2RL-2A 12 VDC, bipolare, sul solo toroidale T1.
- **I rail**:
  - T1 2×15 V 50 VA, ponte, 4700 µF per rail;
  - U501 TPS7A4701 a +15 V: ANY-OUT coi pin 4, 5, 9 a massa, verificato su SBVS204G §6.5.1;
  - U502 TPS7A3301 a −15,04 V: V_REF −1,175 V, partitore 118 k / 10 k, SBVS169D;
  - **2200 µF di tenuta per rail dopo il regolatore** (P9);
  - i Schottky D510 / D511 di protezione: il 3301 ha il massimo assoluto OUT–IN ≥ −0,3 V; sulla
    corrente inversa del 4701 il datasheet tace.
- **`VRELAY`**:
  - T2 a 12 V AC, ponte, D504, **4700 µF** (C520);
  - U503 TPS7A4701 a 12 V (pin 4, 6, 9, 11);
  - **2200 µF di tenuta** dopo U503 (C523);
  - la logica V5 dall'MCP1703A-5002.
- **La stella**: `RLY_RET` e la massa audio si toccano in un solo punto, NT501, accanto alla
  presa centrale di T1.
- **Il sorvegliante**: tutte le uscite open-drain spengono in hardware il gate di Q501 (il sink
  di `MUTE_CMD`), e un pull-down mette in mute se nessuno pilota.
  - U505 TLV1702 sui due rail, con l'LM4040 da 2,5 V: soglie 13,55 V e −13,50 V; il partitore
    del rail − guarda VREF/2, così gli ingressi non scendono mai sotto massa;
  - U506 canale A, rivelatore di rete sul secondario di T2: scatta ~15 ms dopo l'ultima
    semionda;
  - U506 canale B, **`VRELAY` sotto 11,0 V**.
- **J4**: Q501 e Q502 (2N7002), ciascuno con diodo + zener da 24 V verso `VRELAY`, e non un diodo
  di ricircolo semplice, che allungherebbe il rilascio su cui poggiano ADR-045 e L30.
- **Il segnaposto di L41b**: J509 `TIMER_IO` porta `MUTE_REQ`, `PERMIT_REQ`, `MAINS_REQ`,
  `MUTE_G`, `FRONT_SW`, `MUTE_SW` e le quattro linee delle LDR.
- **ERC**: 16 avvisi e 2 «errori», tutti spiegati nel sorgente:
  - i due errori sono i pin OUT doppi del simbolo TPS7A, entrambi dichiarati uscita di potenza;
  - gli avvisi: i pin ANY-OUT aperti apposta (SKiDL 2.3 non ha `NC`), e le uscite dei ponti
    viste come «drive insufficiente».

**Sulla scheda audio** cambiano solo valori fuori dal segnale: le resistenze dei LED da 1,5 k a
**4,99 k** (R1, R2, R3) e i commenti delle bobine a 12 VDC. Il suffisso bobina va solo nella
BOM, perché il 2e legge il ruolo dal campo value. **ERC 47 avvisi come prima; il deck V2
rigenerato è byte-identico** (`cmp`); il 2e passa.

## 3. Il banco (modelli dichiarati)

`genera_tb_psu.py` genera il deck **da `psu.net`**, e rifiuta una parte che non sa tradurre. I
modelli:
- regolatori comportamentali: transconduttanza, limite di corrente, dropout, nessuna corrente
  inversa, e **niente PSRR né rumore**;
- comparatore open-drain comportamentale, in alta impedenza senza alimentazione (il caso
  peggiore per un mute che deve fallire sicuro);
- trasformatori Thevenin, con la regolazione ipotizzata;
- il carico della scheda audio: 265 mA per rail, e le bobine come resistenze.

Il resto in `data/…/L41a/README.md`.

**Dai modelli del costruttore** (`bom-component-manager`, in `vendor/`):
- il TPS7A3301 (SBVM665) funziona in ngspice;
- il TPS7A4701 (SBVM364) carica, ma dà un punto di lavoro sbagliato (~1 V);
- il TLV1701 (SBOM859C) non commuta.

Nessuno di questi è in `models/`. Il modello dell'LM4040 da 4,096 V, portato dall'agente, è
stato tolto da `models/`, perché il progetto usa il 2,5 V e il banco uno shunt comportamentale.
Restano datasheet e originale in `vendor/`.

**Trappola nuova, limitations #34**: un `alter` sopravvive a `destroy all`. Nel primo deck dei
guasti il guasto di U501 è rimasto nel caso di U502, e poi in quello di U503. L'hanno tradito i
numeri: il rail + scendeva nel guasto del regolatore −. Ora ogni caso rimette tutto a valore di
netlist, e il log stampa il valore di R512 per provarlo.

## 4. Le cifre

Rete −10 / nominale / +10 %, 265 mA per rail, 0 righe `Error` nei log:

| Caso | `MUTE_CMD` rilasciato | Rail al rilascio | Tenuta rail 13,5 → 10,6 V (P9: ≥ 16 ms) | `VRELAY` dopo lo scatto |
|---|---|---|---|---|
| Regime | — | +15,00 / −15,05 V; valle del grezzo 18,0 / 20,3 / 22,5 V | — | 12,00 V; grezzo 13,2 / 15,1 / 17,1 V |
| Perdita di rete | **14,2 / 14,3 / 14,4 ms** | **+15,00 / −15,05 V** | 60,3 ms | ≥ 11,4 V per **62,8** / 144,9 / 227,3 ms (≥ 25 ✓) |
| U501 cede | 9,56 ms | scatto a **13,56 V**, 0,41 ms prima dei 13,5 V | **19,35 ms** ✓ | rete presente |
| U502 cede | 10,14 ms | scatto a **−13,52 V** | **19,36 ms** ✓ | rete presente |
| U503 cede aperto | 15,83 ms | scatto a `VRELAY` 11,0 V | — | ≥ 9,6 V (80 %) per **32,9 ms**: K6 e K1/K5 su per Δ |
| Rivelatore guasto + perdita di rete | 72,5–136 ms | 13,56 V | 60 ms | con rete −10 %: **0 ms** (doppio guasto) |

- **P9 (b), «entro 1 ms dai 13,5 V»**: il sorvegliante scatta *prima* della soglia (13,56 V), in
  ogni caso.
- **La tenuta dei rail** con la sola capacità dopo il regolatore (1760 µF effettivi) dura
  19,4 ms, contro i 16 ms richiesti.
- **La tenuta di `VRELAY`**: con 2200 µF di serbatoio e la rete a −10 % durava 14,2 ms, fuori
  (`varianti/t2_12vac_c2200`). È il «Da riaprire se» di ADR-048. Con **4700 µF** dura 51 ms
  prima di C523, e 62,8 ms dopo. 15 V AC con 2200 µF avrebbe fatto 81 ms, ma scalda ~0,4 W in
  più.
- **La perdita di rete stacca il jack coi rail a 15 V**, cioè prima di qualunque discesa. In L30
  il residuo del guasto (0,5–1,8 mV, ~58 dB SPL di picco a 1 m) veniva in parte proprio dalla
  discesa col jack collegato. Quanto scenda lo misura **L41c**; qui non lo prometto.

## 5. Quello che resta aperto, in dB dove si può

- **NC-036** resta aperta e bloccante per G2:
  - il temporizzatore, il ritardo Δ in hardware e il pilota delle LDR sono di **L41b**;
  - il banco di L30 col circuito vero è di **L41c**.
- **Il cortocircuito dell'uscita di U503** scarica anche C523: tutte le bobine cadono insieme. È
  il controfattuale «senza Δ» di L30, **69 mV, ~90 dB SPL di picco a 1 m**, sotto il tetto di
  ~112 dB ma sopra l'obiettivo di ~60 dB. È una decisione dell'utente, in L41c: accettarlo come
  il corto istantaneo di un rail, oppure una tenuta locale delle bobine sulla scheda audio, che
  ADR-046 aveva scartato.
- **NC-037, lo standby oltre 0,5 W**: in mute le bobine del trim sono pilotate di continuo, circa
  0,44 W a 12 V. Rimedio per L41b: togliere `VRELAY` alla scheda audio in standby, e i LED del
  pannello si spengono.
- **NC-011, la quota di ADR-020**: rimedio scelto, lineari e nessuno switching. La densità di
  rumore del TPS7A4701 letta dal grafico (~0,1–0,15 µV/√Hz a 1 kHz) sembra sopra gli 87 nV/√Hz;
  non verificato.
- **Il limite europeo dello standby**: dalla Commissione e da fonti terze, Reg. (UE) 2023/826,
  0,5 W. EUR-Lex non era raggiungibile: la fonte primaria resta da leggere (`SAFETY.md`).
- **P2**: aperto il registro `docs/preamp/SAFETY.md`. Non è l'analisi, e la norma di riferimento
  non è ancora scritta.

## 6. Cosa cambia nel repo

- Nuovi:
  - `circuits/preamp/psu.py` e `psu.net`;
  - `scripts/check_psu_harness.py` e il blocco **2j** di `run_tests.sh`;
  - `docs/preamp/SAFETY.md`;
  - ADR-048;
  - `data/2026-09-26/L41a/`;
  - `vendor/ldo_regulator/`, `vendor/comparator/`, `vendor/voltage_reference/` (datasheet e
    modelli TI, congelati).
- Modificati:
  - `trim.py`, `gain_interlock.py` e `preamp_audio.py` (valori dei LED, commenti a 12 V);
  - `preamp_audio.net`;
  - `REQUIREMENTS.md` (P3, P5, P9);
  - l'indice delle ADR (con le note su ADR-046 e ADR-047);
  - `NONCOMPLIANCE.md` (NC-011, NC-036, NC-037);
  - `limitations.md` (#34);
  - `CLAUDE.md` (34 limitazioni).
- Suite: `run_tests.sh` **11 passed / 0 failed**; `validate_models.py` 48/48.
