# Dati del 2026-09-14, lotto L17 — un buffer per ogni uscita fissa

Decisione: **ADR-023**. Report: `../../../reports/2026-09-14-L17-buffer-uscite-fisse.md`.

**Topologia.** Quella di L17: il blocco A pilota l'attenuatore e due buffer
`GAINBLOCK`, uno per fissa. Ogni dispositivo è un segnaposto
(`spice/preamp/placeholder_devices.lib`, NC-017), tranne LS352 e LSK489.
Nessuna protezione dal corto.

**Sottocartella, non la cartella del giorno.** L11 ha versionato lo stesso
giorno file con gli stessi nomi (`tb_blockA_carichi_*.csv`,
`tb_mute_corto_*.csv`), sulla topologia senza buffer. Stanno un livello sopra
e non sono stati toccati.

## I file

| File | Deck | Cosa |
|---|---|---|
| `tb_blockA_carichi.csv` | `tb_blockA_carichi.cir` | 108 righe: 2 cablaggi × 2 frequenze × 9 impedenze a valle × 3 blocchi |
| `tb_blockA_carichi_<rj>.csv` | idem | forme d'onda, cablaggio nuovo, 1 kHz: col1 I_C XA.Q132, col3 XA.Q133, col5 XF1.Q132, col7 XF2.Q132, col9 v(OUTA) |
| `tb_blockA_carichi_ac_<rj>.csv` | idem | col1 vdb(OUTA), col3 vdb(J2) |
| `tb_mute_corto_regime.csv` | `tb_mute_corto.cir` | 440 righe: 110 corse × 4 blocchi (A, F1, F2, B) |
| `tb_mute_corto_transitorio.csv`, `_trans_{0,10}.csv` | idem | inserzione e rilascio del mute; forma d'onda con col17 = p(XF1.Q132) |
| `tb_loop_blockA.csv`, `tb_loop_blockA_<C>.csv` | `tb_loop_blockA.cir` | margine del blocco A: carico 1 = nuovo, 2 = canonico di ADR-008 (controllo); curve del carico 1 |
| `tb_loop_bufferfissa.csv`, `_p<pos>_<C>.csv` | `tb_loop_bufferfissa.cir` | margine del buffer: pos 1 = sonda al jack, 2 = sul nodo d'uscita; RLD 10 k / 50 k |
| `tb_uscite_fisse_e4.csv`, `_zout.csv` | `tb_uscite_fisse.cir` | E4 al jack della fissa 1: \|Z\|, Re(Z), \|Z\| al nodo del buffer |
| `tb_uscite_fisse_rumore.csv`, `_rumore_<Rs>.csv` | idem | E5: rumore integrato e spettri, catena A → F1 → J1 |
| `*.log` | ciascun deck | log completo di ngspice |

## Colonne principali

**`tb_blockA_carichi.csv`**
- `cablaggio`: 1 nuovo (buffer), 2 vecchio (ADR-008, il controllo che il deck
  sappia fallire).
- `rj1`: impedenza a valle della fissa 1.
- `blk`: `a`, `f1`, `f2`. ngspice scrive minuscolo.
- `classe_a` = 1 ⇔ `icmin_q132 > 0` e `icmax_q133 < 0`, calcolato da
  ngspice. Il ricalcolo dai due valori coincide in 108 righe su 108.

**`tb_mute_corto_regime.csv`**: le colonne di L11 (vedi `../README.md`), più
due cose.
- `blk` vale A, F1, F2 o B. `p_rsep` è la 47 Ω del blocco: F1 RSEP1, F2 RSEP2,
  B RISOM, e 0 per il blocco A.
- `caso` 5 e 6: apparecchio spento sulla fissa 1, a 10 Ω e a 100 Ω.
- `p_rail`: potenza media erogata dai rail al **canale** intero.

**Percorsi ascoltabili per caso** (ADR-023):

| Caso | Stadi che devono restare in classe A |
|---|---|
| 0 | A, F1, F2, B |
| 1 | nessuno |
| 2, 5, 6 | A, F2, B |
| 3 | A, F1, B |
| 4 | A, F1, F2 |

## Numeri chiave

Verificati rileggendo questi CSV.

**ADR-023, classe A sui percorsi ascoltabili.**
- `tb_mute_corto`: 294 righe controllate, **0 violazioni**. Il blocco A non
  scende mai sotto 14,354 mA.
- `tb_blockA_carichi`, cablaggio nuovo: blocco A a **14,356 mA** e buffer F2 a
  **14,509 mA** in tutte le 18 righe.
- Il buffer F1 va in classe B a ≤ 22 Ω (1 kHz) e a ≤ 47 Ω (20 kHz).
- **Controllo**: col cablaggio vecchio il blocco A va in classe B alle stesse
  soglie. A 10 Ω e 1 kHz: min −0,0002 mA, max 57,33 mA (L11: −0,23 µA e
  57,258 mA).

**P7.** Nessun dispositivo supera 125 °C. Il più caldo resta Q125, a
**96,4 °C**. Le MJE per blocco:

| Blocco | MJE peggiore | Tj | Condizione |
|---|---|---|---|
| A | 214,0 mW | 73,4 °C | riposo, in ogni caso |
| F1 / F2 | 298,1 mW | 78,6 °C | corto sulla propria fissa, o mute |
| B | 348,2 mW | 81,8 °C | corto MAIN, +10 dB, 20 kHz |

- Apparecchio spento su F1: **261,3 mW** a 10 Ω, 214,2 mW a 100 Ω, contro
  298,1 mW del corto.
- Resistenze e contatti:
  - 47 Ω principale 1,097 W;
  - 47 Ω delle fisse 0,154 W;
  - 22 Ω del blocco B 0,271 W, dei buffer 0,037 W;
  - contatti ≤ 152,7 mA RMS.
- **Controprova indipendente** della potenza, corto FIX1 a 20 kHz: XF1.Q132
  297,94 mW da `@q[p]` contro 297,83 da tensioni e correnti; RSEP1 154,42 mW
  per entrambe le strade.
- Stazionarietà: scarto massimo **0,74 %**.

**Calore.** A riposo **3,225 W** per canale, **6,45 W** per i due, 0,806 W per
blocco (NC-029).

**Margine di fase** (nessun rimedio: è L12):

| | bare | 1 nF | 2,2 nF | 4,7 nF |
|---|---|---|---|---|
| Blocco A, carico nuovo, sonda sul nodo | 69,30° | 63,45° | 55,87° | **40,96°** |
| Blocco A, carico canonico di ADR-008 (controllo) | 69,31° | 63,47° | 55,91° | 41,02° |
| NC-002, THAT320, 2026-09-09 | 69,83° | 64,08° | 56,65° | 41,98° |
| Buffer, sonda al jack, 10 k | 69,31° | 64,34° | 61,78° | 62,27° |
| Buffer, sonda sul nodo, 10 k | 69,31° | 63,46° | 55,88° | **40,98°** |

Al jack, il minimo su entrambi i carichi è **61,74°** (50 k, 2,2 nF).

**E4 ed E5** sulla fissa 1:
- Re(Z) al jack al massimo **53,13 Ω** (a 20 Hz); \|Z\| 57,95 Ω a 1 kHz;
- rumore **1,624 / 1,667 / 1,859 µV** con sorgente 1 / 430 / 2500 Ω;
- il solo blocco A a 430 Ω dà 1,211 µV.
