# L45d2b2c — i massimi del blocco col rail alto (2026-10-21)

Ultima parte di **L45d2b2** (a la partenza morbida, b1 i diodi della tenuta, b2 il comando e i 5 V, c
questa). ADR-078 punto 1: le tensioni massime delle parti del blocco col rail alto e la dissipazione
dei finali; il sorvegliante della sovratensione solo se qualcosa esce. L'utente all'inizio: **«Una
sessione»**. Report `../../../reports/2026-10-21-L45d2b2c-massimi-blocco.md`, decisione **ADR-095**.

`<A>` = questa cartella. Python con `/usr/bin/python3 -I` salvo dove detto.

## 1. Il rail alto di oggi (`psu/`, `seq/oggi/`)

`psu/` è il banco dell'alimentatore di L45d2b2b2, **copiato**; `modi.py` aggiunge `RIGHE_078`: i modi di
L45c1 che alzano un rail (`data/2026-10-13/L45c1/psu/modi.py:73-91`), spariti dai banchi da L45c2, rifatti
sui nodi di oggi (il corto fra il piedino IN dietro R550 / R551 e il piedino OUT; SENSE aperto e R501
aperta come gemello a VSET 100; il pin ANY-OUT da 3,2 V a massa, 18,5 V) e `BASE_078` (senza guasto),
ciascuno alle tre reti, sulla netlist del sorgente, 2N7002 tarato (limitations #67). `carico.txt` è
quello di L45d2b2b2.

- **Il controllo** (`script/controllo_l45c1.sh`): i due deck dei corti di L45c1 (`seq/f_u50[12]_cortoio_mus`),
  copiati coi soli `.include` rimappati, rieseguiti oggi, letti da `script/rail_alto.py`:
  **+20,3253 / −20,2980 V**, cifra per cifra `vp_max` / `vm_min` di L45c1 (`controllo/l45c1.csv`).
- **Le 18 corse**: tutte al punto fisso al primo giro. `rail_alto.csv`:

| Modo | rete −10 % | nominale | +10 % |
|---|---|---|---|
| U501 ingresso-uscita in corto | +16,21 V | +18,13 V | **+20,05 V** |
| U501 SENSE aperto | +15,98 | +17,90 | +19,82 |
| U501 pin da 3,2 V a massa (18,5 V chiesti) | +15,98 | +17,90 | +18,17 |
| U502 ingresso-uscita in corto | −16,15 | −18,06 | **−19,97** |
| R501 aperta | −15,92 | −17,84 | −19,75 |
| sano | +14,98 / −14,97 | uguale | uguale |

  Il piedino a 20,38 V, il rail 0,34 V sotto (D515), il grezzo di picco 22,72 V; ripple ≤ 86 mV pp;
  il jack resta collegato (il sorvegliante vede solo il rail che scende).

## 2. Il blocco col rail alto (`script/genera_massimi.py`, `deck/`, `run/`)

Il banco di L62b (`genera_L62b.py`, importato; le copie guaste rifatte dal blocco di oggi, limitations
#62) con le cartelle spostate qui. I due rail ideali (`VPP` / `VMM`, una riga ciascuno, controllato)
sostituiti: `nom` ±15, `p` +20,3 / −15, `m` +15 / −20,3, `pm` ±20,3 (non un guasto singolo: il limite
superiore). Nella posizione B: il riferimento sano e i quattro modi di NC-062 (col rail alto un doppio
guasto, dichiarato). Ogni coppia di terminali di ogni parte del blocco, massimo e minimo su tutta la
corsa (`<modo>_tensioni.csv`). P7 (`tb_mute_corto` con le misure di L60d1) coi quattro rail e coi rail
misurati alle tre reti (`RAIL_P7`: +16,3 / +18,2 / +20,1, −16,2 / −18,1 / −20,0), più le giunzioni
base-emettitore dei finali in inversa (`tb_mute_corto_vbe.csv`, `vbe_p7()`).

- **I controlli**:
  - `nom` uguale a L62b: riposo dei finali 0,298 W, guasti del moltiplicatore 0,59–0,60 W, in P7 finali
    0,362 / 0,363 W, R134 0,2946 W, R135 0,3324 W, la 47 Ω 1,282 W;
  - lo strumento delle tensioni (`script/controllo_tensioni.py`): a blocco sano, V²/R di 15 resistenze su
    15 entro il 2 % del `[p]` di ngspice sui quattro rail; il sabotaggio (R +10 %) preso 15 volte su 15.
- **I limiti** (`limiti_blocco.csv`): dai datasheet, letti dall'agente bom-component-manager (solo web);
  ogni riga con la fonte e il tipo di lettura.
- **Gli esiti** (`script/analizza_massimi.py` → `tensioni.csv`, `massimi_blocco.csv`, `calore.csv`,
  `p7.csv`):
  - **tensioni: 272 massimi, 0 fuori**. LSK489 12,7 V fra drain e source, gate ≪ 60 V; C145 20,1 V
    contro 25; nessuna base-emettitore in inversa a blocco fermo; collettori ≤ 40 V contro 60–250;
  - **finali**: 85,5 °C a riposo col rail alto (60 °C d'aria), 112,9 °C sommando un guasto del
    moltiplicatore;
  - **P7, fuori**: col rail alto alle tre reti R135 0,358 / 0,391 / 0,401 W (≥ 0,34), R134 fino a
    0,360 W, la 47 Ω 1,35 / 1,44 / 1,47 W (≥ 1,3); e **già a ±15 V** la base di Q132 spento 5,18 V
    sopra l'emettitore (MJE15032: 5 V), nella cella più dura (principale, +10 dB, 20 kHz a fondo scala,
    mute o corto).

## 3. Il rimedio (`genera_massimi.py cbe`, `run/tb_cbe_*`, `p7_cbe.csv`)

D158 (NEN → NBN) e D159 (NBP → NEP), 1N4148, come variante del blocco (`varianti/cbe/`), P7 su tutti e
dieci i rail (`analizza_massimi.py cbe`): base-emettitore ≤ 0,77 / 0,84 V; 22 Ω ≤ 0,181 W, 47 Ω ≤ 0,78 W
anche col rail alto; Q133 92,7 °C a ±15 V, 109,8 °C col rail − alto a rete +10 %; i diodi ≤ 29 mA, ≤ 5
mW. Il meccanismo, cella per cella (`script/confronta_cbe.py`): il diodo fa da limite di corrente,
~0,11 A sul lato PNP.

## 4. Il sorgente e la regressione

L'utente: «Resistenze più robuste», «Rimedio in questo lotto», poi coi numeri del rimedio «Vincoli di
oggi» → **ADR-095**. `gain_block.py` sezione 12 (D158 / D159 in fondo, limitations #22); la scheda audio
554 → 570 parti (`script/conta_parti.py`: nessuna sigla doppia, 16 diodi sui finali nel verso giusto);
il disegno del blocco 61 dispositivi, e rifiuta il blocco di prima (`falsi/gain_block_flat_prima_di_adr095.inc`).
`script/rigenera.sh` rigenera netlist e sottocircuito con la cartella corrente in `circuits/preamp`.

- **La regressione dei 21 deck veloci** (`script/regressione.sh`, da L62b): `regressione/prima` col blocco
  di main 82a94e57, lanciata nel worktree prima del sorgente; `regressione/dopo` coi diodi.
  `misure_regressione.py`: 27 253 misure, 699 oltre 1e-3, di cui **695 in `tb_mute_corto`** (atteso), 2
  a zero (`tb_idss_op_noise @riso[i]` 0 contro −2,8e-15), 1 in `tb_blockA_carichi` (−3,03e-5 contro
  −3,04e-5), 1 il numero spezzato di `tb_trim` (noto da L62b). Margini di fase −0,004° al più.
  `p7_massimi.py`: Q133 0,363 → 0,523 W, R134 0,295 → 0,158, R135 0,332 → 0,129, 47 Ω 1,282 → 0,683 W:
  uguale alla variante.
- `run_tests.sh` **13 / 0** dal worktree.

## Che cosa sta nel repository

`run/` (le corse), le forme d'onda delle sequenze e del controllo (`*_out.txt`) e quelle grandi della
regressione non ci sono: si rifanno coi comandi sotto. Le tabelle di P7 di ogni rail, con e senza i
diodi, sono copiate in `p7/<gruppo>_regime.csv` e `p7/<gruppo>_vbe.csv` (`script/copia_p7.sh`).

```sh
/bin/zsh <A>/script/controllo_l45c1.sh
/bin/zsh <A>/psu/corri_078.sh
/usr/bin/python3 -I <A>/script/rail_alto.py <A>/seq/oggi <A>/rail_alto.csv @<A>/lista_078.txt
/usr/bin/python3 -I <A>/script/genera_massimi.py
/usr/bin/python3 -I <A>/script/genera_massimi.py cbe
/bin/zsh <A>/script/corri_massimi.sh
/bin/zsh <A>/script/corri.sh <A>/deck/lista_tb_reti.txt
/bin/zsh <A>/script/corri.sh <A>/deck/lista_tb_cbe.txt
/usr/bin/python3 -I <A>/script/controllo_tensioni.py
/usr/bin/python3 -I <A>/script/analizza_massimi.py
/usr/bin/python3 -I <A>/script/analizza_massimi.py cbe
/bin/zsh <A>/script/regressione.sh prima      # sul blocco senza D158 / D159
/bin/zsh <A>/script/regressione.sh dopo
/usr/bin/python3 -I <A>/script/misure_regressione.py
```

Il blocco senza i diodi (per `nom`/`p`/`m`/`pm` e la fase `prima`) è quello di main 82a94e57: dopo
ADR-095 `genera_massimi.py` legge il blocco del sorgente, che li ha.

## Limiti dichiarati

- Il calore è Tj = 60 °C + P · R_thJA con P a 27 °C (il metodo di L45a / L62a / P7).
- Le tensioni del blocco col rail alto sono a blocco fermo (nessun segnale) e nei guasti di NC-062; con
  il segnale le giunzioni dei finali sono lette in P7, le altre no. Ogni nodo del blocco sta fra i due
  rail: i limiti dei transistor e dei diodi fuori dalle base-emettitore (≥ 60 V) superano i 40,6 V fra
  i rail, e i condensatori verso massa vedono al più un rail (≤ 20,3 V).
- I condensatori elettrolitici del blocco non hanno una tensione scritta nel sorgente: le cifre (C141 /
  C142 20,3 V, C116 13,4 V, C104 1,4 V) dicono quella che serve.
- I modi dei diodi nuovi (D158 / D159 aperti e in corto) sono di L45d2b3.
