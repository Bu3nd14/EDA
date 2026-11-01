# 2026-11-01 — L58b, l'autodiagnosi

**Documento datato: non si riscrive.** Dati e comandi in `../data/2026-11-01/L58b/` (README). Decisione
**ADR-110**. Procedura `../DIAGNOSI.md`. Cifre di modello: ngspice 47; il banco dell'alimentatore di
L58a (regolatori comportamentali, limitations #80, comparatori e diodi del costruttore); il banco del
calore di L45d2b3b2b2 sul blocco del sorgente; V2 di L29c con le rampe vere. Il MOSFET del banco è
generico, senza capacità.

## Perché

Il micro è uscito (ADR-102): ciò che ADR-076 e ADR-078 davano al firmware si fa in hardware o torna
all'utente. ADR-100 mandava a L58 46 righe latenti; ADR-071 e ADR-100 chiedevano di tornare
all'utente con ogni guasto che non si vede a un costo ragionevole. Il lotto ha misurato **che cosa
mostra** ogni riga, e poi ha portato le scelte all'utente, conversando.

## 1. Il censimento

**I casi noti.** Il banco dell'alimentatore ridà `l58a_base` riga per riga (accensione, musica a
1209,3 ms; spegnimento). Il banco del blocco ridà 15 righe di L45d2b3b2b2 (rif, Q132_ce, R126_cc
nelle cinque posizioni). V2 ridà la base di L58a2.

**Lo standby (ADR-078, 8 righe).**

| Guasto | A frontale spento | Al frontale acceso |
|---|---|---|
| Q505 / Q506 in corto, R540 aperta | VRELAY 12,0 V alla scheda audio: **i LED restano accesi** | come oggi |
| R536 aperta | dal primo spegnimento: VRELAY 12 V e toroidale acceso | come oggi |
| R537 in corto, U508 B cieco | VRELAY 12 V e toroidale acceso | la musica a 17,4 ms |
| Q503 in corto, K501 saldato | toroidale acceso, VRELAY 0: **LED spenti** | la musica a 17,4 ms |

**Il mute (ADR-076, 10 righe).**
- Con Q501 in corto D-S o G-D le bobine si eccitano 2,5 ms dopo il frontale, coi rail a 0,012 V. A
  ogni accensione il jack prende la salita dei rail:
  - principale **70,1 mV, ~90 dB SPL**;
  - fisse **0,642 / 0,657 V, ~110 dB SPL**;
  - uguale a rete −10 / +10 %; il banco ha 100 kΩ su ogni jack.
- All'inserimento del mute dal frontale le bobine restano eccitate.
- Il contatto saldato di K2–K4 fa lo stesso su quell'uscita.
- Il colpo del primo spegnimento dopo il guasto resta quello di ADR-076: ~102 dB SPL, fino a ~125.

**Il blocco (ADR-071, 28 righe)**, sul blocco del sorgente di oggi:
- **Q132 in corto B-E porta l'uscita al rail** (−13,6 V). Non è un degrado silenzioso; la cifra di L45
  (0,053 V) era del blocco di prima. La riga è di L66 (NC-076).
- **6 guasti spostano la continua** al test point d'uscita di 15–226 mV.
- **15 cambiano il riposo dei finali** (20,2 mA): 0, 9,5, 0 / 39 mA. Si legge sulle due 22 Ω.
- **3 tolgono il +10 dB** (C137, R136, R143, blocco B).
- **3 non si vedono**: R123, R144 in corto, R147 aperta.

Il calore sposta la continua di ~0,6 mV e il riposo da 21,1 a 22,5 mA fra 27 e 57 °C d'aria (L45d2b3b2b2).

**R585** (ADR-109). In funzionamento AT_F sta a 0,007 V, sia in standby sia in musica: il tester non
vede la ritenuta cieca. In sessione l'avevo detto all'utente in modo sbagliato («~1,2 V invece di 0») e
l'ho corretto. Resta l'ohmmetro a scheda spenta, da verificare sul prototipo.

## 2. Le scelte dell'utente

Sulle tre domande coi numeri:

1. **Lo standby**: «si». Bastano i LED e la musica che arriva subito; niente LED nuovo, PR-19 resta.
2. **Il mute**:
   - prima: «accetterei il bump all'accensione, ma mi devi ricordare i dB prima di avere conferma»;
   - poi, coi dB, l'utente ha pensato alle quattro resistenze di R585. Era un altro guasto, e gliel'ho
     detto. L'equivalente per Q501 è un secondo transistor in serie;
   - «si, misura il transistor in serie; R585 resta com'era»;
   - sulla coppia misurata: «si, metti la coppia nel sorgente»; sul contatto saldato coi suoi dB: «si».
3. **Il blocco**: «si». La procedura col tester, e i tre invisibili accettati.

## 3. La coppia in serie (ADR-110)

Q501 sopra (drain su MUTE_CMD) e Q509 sotto (source su RLY_RET), ciascun gate da MUTE_G con la sua
resistenza. Sul banco, con l'opzione `--q501serie` del sorgente di prima:

| | 10 kΩ / 10 kΩ | **1 MΩ / 10 kΩ** |
|---|---|---|
| coppia sana, 8 eventi | uguale alla base (≤ 0,2 ms) | uguale alla base (≤ 0,2 ms), anche a rete −10 / +10 % |
| Q501 corto D-S, Q509 corto D-S | come la coppia sana | come la coppia sana |
| Q501 corto G-D | **il jack a 50 ms invece di 10, dopo il guadagno** (C3, r41) | **come la coppia sana** (K501 +2,5 ms alla perdita di rete) |
| Q509 corto G-D | muto, nessun colpo | muto, nessun colpo |
| R586 / R587 aperte | — | come la coppia sana |

Con 10 kΩ, il corto gate-drain di Q501 rimanda la corrente delle bobine in MUTE_G (~5,6 V) e tiene
acceso Q509. Con 1 MΩ la corrente scende a ~12 µA.

Il modello del 2N7002 sul banco non ha capacità (LEVEL 1). Il ritardo attraverso 1 MΩ è calcolato dal
datasheet, ≤ ~0,2 ms, e conta solo quando Q501 spegne da solo con Q509 già in corto. **Da confermare
sul prototipo** (il «Da riaprire se» di ADR-110).

**Nel sorgente** (`psu.py`, `sink(..., serie=("Q509", "R586", "R587"))`):
- la netlist ha tre parti nuove e tre reti nuove; il resto è invariato;
- il deck del sorgente nuovo è il deck della variante, salvo il titolo (`psu/sorgente_uguale.py`);
- gli otto eventi sul sorgente nuovo danno la variante entro 0,1 ms / 0,1 mV;
- l'ERC di SKiDL dà gli stessi 19 avvisi e 2 errori di prima (i due OUT dei TPS7A, noti);
- lo schematico A3 ha 187 parti su 187; il diagramma a blocchi asserisce la coppia e i due valori;
- **i guardiani**: `check_relay_safe_state.py --timer` riconosce la coppia (il suo gate è il nodo di
  pilotaggio comune, MUTE_G) e chiede ≥ 1 MΩ sopra; `check_psu_harness.py` accetta il sink attraverso
  un secondo N-MOSFET. Rifatti fallire: i 24 falsi di L54b1 e 5 della coppia, **29 su 29**;
- `run_tests.sh` **14 / 0**, `validate_models.py` 89 / 89.

## 4. La FMEA e la procedura

`data/2026-11-01/L58b/fmea_l58b.csv`: 60 righe (le 46, cinque di L58a2, nove della coppia), con la
matrice di ADR-070.

| | prima | dopo |
|---|---|---|
| mute (ADR-076) | 8 alte, 2 medie | 4 alte (K2–K4, accettate coi dB), 6 basse (Q501, rimediata) |
| blocco (ADR-071) | 28 medie | 25 medie (21 con la procedura, 3 accettate invisibili, Q132 B-E a L66), 3 basse (si sentono) |
| standby (ADR-078) | 8 basse | 8 basse (6 si vedono dai LED) |
| R585 | alta | alta, accettata (ADR-109, invariata) |

`DIAGNOSI.md`: i segni (LED in standby, il mute su ogni uscita, il colpo all'accensione, la musica
subito, il +10 dB), la procedura col tester per gli otto blocchi (le sigle lette dalla netlist: test
point d'uscita e le due 22 Ω), R585 all'ohmmetro.

## 5. Che cosa resta

- **NC**: nessuna voce aperta o chiusa. NC-077 resta (R585). NC-076 (L66) prende anche la riga di
  Q132 B-E, che sul blocco di oggi porta l'uscita al rail.
- **Sul prototipo**:
  - il ritardo della coppia e il gate di Q501 su 1 MΩ (disturbi);
  - la lettura di R585 in circuito;
  - la stabilità nel tempo della continua e del riposo dei blocchi (le soglie di `DIAGNOSI.md`).
- **L64**: il dossier mostra la coppia.
