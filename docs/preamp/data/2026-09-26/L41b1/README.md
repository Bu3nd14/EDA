# L41b1 — il temporizzatore dell'alimentatore, l'hardware (2026-09-26)

Dati del lotto L41b1 (NC-036, NC-037). Decisione: **ADR-049**. Report:
`docs/preamp/reports/2026-09-26-L41b1-temporizzatore-hardware.md`. Sorgente:
`circuits/preamp/psu.py` → `circuits/preamp/psu.net`. Specifica del firmware:
`firmware/preamp_timer/spec/timer_spec.md`.

Qui niente forme d'onda: i deck scrivono solo misure (`meas`, `print`), e i log pesano decine di
kB. Si versionano tutti.

## Le cartelle

| Cartella | Cosa |
|---|---|
| `scelte/` | `dimensiona.py` → `dimensiona.txt`: Δ, Δ₂, la rete del DAC, il minimo col DAC in reset, la tensione di conformità, la VTL5C4 contro la temperatura del telaio. **Fatto prima** di mettere i valori nel sorgente |
| `deck/` | `genera_tb_psu.py` (il generatore di L41a copiato ed esteso: rifiuta le parti che non conosce, modelli dichiarati nell'intestazione), `analizza_timer.py`, `analizza_ldr.py` |
| `timer/` | i transitori con tutto l'alimentatore: il micro in reset, a zero, bloccato alto; la perdita di rete; il guasto di U503; il rilascio; lo standby; il controfattuale senza C528. `nom` e `min` (C_T, C_T2 −5 %, R_T, R_T2 −1 %, V5 4,90 V, VREF 2,505 V) |
| `ldr/` | i punti di lavoro del pilota delle LDR contro la tabella v4, a 15/25/35/45/60 °C: senza compensazione, compensato, calibrato (`cal.json`), col DAC in reset; il caso peggiore di conformità (`ledmax_v5_4.9`); il rumore all'anodo della derivazione |
| `falsi/` | `falsi.py` → `esito.txt`: il 2j esteso e il 2e `--timer` fatti fallire, 15 falsi su 15, più la netlist di `main` |

## Come si rifà

Dalla radice del repo, e poi dentro ogni cartella per ngspice (i deck scrivono accanto a sé):

```sh
env/venv/bin/python3 circuits/preamp/psu.py
/usr/bin/python3 docs/preamp/data/2026-09-26/L41b1/scelte/dimensiona.py
G=docs/preamp/data/2026-09-26/L41b1/deck/genera_tb_psu.py
D=$PWD/docs/preamp/data/2026-09-26/L41b1
/usr/bin/python3 $G --uscita $D/timer --nome timer
/usr/bin/python3 $G --uscita $D/timer --nome timer --angolo min --v5 4.9
/usr/bin/python3 $G --uscita $D/ldr --nome ldr
/usr/bin/python3 $G --uscita $D/ldr --nome ldr --led max --v5 4.9
/usr/bin/python3 $G --uscita $D/ldr --nome rumore
cd $D/timer ; /opt/homebrew/bin/ngspice -b tb_psu_timer_nom.cir -o tb_psu_timer_nom.log   # idem _min
cd $D/ldr   ; /opt/homebrew/bin/ngspice -b tb_psu_ldr.cir -o tb_psu_ldr.log               # idem gli altri
/usr/bin/python3 $D/deck/analizza_timer.py tb_psu_timer_nom.log tb_psu_timer_min.log
/usr/bin/python3 $D/deck/analizza_ldr.py tb_psu_ldr.log --scrivi-cal cal.json
/usr/bin/python3 $G --uscita $D/ldr --nome ldr --cal $D/ldr/cal.json    # poi ngspice e analizza
/usr/bin/python3 $D/falsi/falsi.py circuits/preamp/preamp_audio.net circuits/preamp/psu.net
```

La calibrazione ha due passi, come la farà il firmware: il deck senza calibrazione dà le correnti
a 20 mA e a 2 mA; `--scrivi-cal` ne ricava `off` e `r_ohm` per stringa e per temperatura; il deck
`--cal` le applica. Il caso `ledmax_v5_4.9` ha la sua calibrazione (`cal_ledmax_v5_4.9.json`).

**Le guardie**:
- `analizza_timer.py`: 0 righe con `Error`, `singular`, `no such`, `non-increasing`, `Transient
  op`, `Timestep too small`. Fanno eccezione i messaggi delle `meas` che non trovano l'evento:
  sono misure, lette come tali;
- `analizza_ldr.py`: un punto risolto dal ripiego in transitorio invalida il deck
  (limitations #33). Nei deck versionati non ce n'è nessuno;
- ogni caso del deck `timer` rimette a valore ogni sorgente e ogni parte che un caso altera
  (limitations #34), e stampa `@cc528[capacitance]`: 1e-7 (nom) o 9,5e-8 (min), 1e-11 solo nel
  controfattuale.

## I modelli

Quelli di L41a (vedi il suo README), più quelli dichiarati nell'intestazione di
`genera_tb_psu.py`:
- ATtiny3216, MCP4822, MCP6004 comportamentali;
- BJT generici (niente calo del β a bassa corrente, niente perdite, niente autoriscaldamento);
- AO3401A come MPGEN;
- il LED della VTL5C4 dal modello di L29b.

Per i punti di lavoro e il rumore, l'MCP6004 è una **variante liscia**: guadagno 1e3 negli anelli
di riferimento, inseguitore ideale nel buffer. Con quella a gradino e guadagno 1e5 Newton falliva
in 7 punti su 85 (limitations #33). **Del datasheet non sono modellati**:
- gli offset (±4,5 mV): li toglie la calibrazione;
- il rumore degli op-amp e del DAC: aggiunto a mano nel report.

## Le cifre

**Il temporizzatore** (`timer/analisi_timer.txt`), nominale / angolo minimo:

| Caso | Δ (`PERMIT_CMD` − `MUTE_CMD`) | `VRELAY` a J1 < 9,6 V dopo `PERMIT_CMD` |
|---|---|---|
| micro in reset (uscite in alta impedenza) | 18,84 / 16,91 ms | 60,4 / 56,5 ms |
| micro portato a zero | 20,07 / 18,12 ms | 60,4 / 56,5 ms |
| perdita di rete + micro in reset | 18,84 / 16,91 ms | 60,4 / 56,5 ms |
| U503 cede + micro in reset | 18,84 / 16,91 ms | 24,7 / 26,9 ms |
| **controfattuale senza C528** | **0,00 ms: fallisce come deve** | — |
| perdita di rete, micro bloccato alto | `MUTE_CMD` a +14,3 ms, `PERMIT_CMD` mai nei 400 ms | — |
| il firmware abbassa solo `PERMIT_REQ` | nessun rilascio (drain ≤ 0,02 V) | — |
| rilascio con solo `MUTE_REQ` | `PERMIT_CMD` 0,04 ms prima di `MUTE_CMD` | — |
| standby | `VRELAY` a J1: 0,000 V; dal secondario di T2 **92,5 / 90,8 mW** | — |

**Le LDR** (`ldr/analisi_ldr_cal*.txt`), errore contro la tabella v4, da 15 a 60 °C:

| Modo | Peggiore |
|---|---|
| legge a 25 °C, senza compensazione | +8,7 dB (riposo a 60 °C), −6,6 dB (20 mA a 60 °C) |
| compensata col sensore del micro | −3,1 dB alla cima (parte ohmica), ≤ ±0,3 dB altrove |
| **compensata e calibrata** | **−0,92 dB alla cima, ≤ +0,41 dB altrove: PASSA** (criterio ±1 dB, riposo 5–20 nA) |
| LED al massimo (2,0 V) e V5 4,90 V, calibrata | −0,92 dB; lo specchio ha ancora 0,34–0,59 V ai capi: PASSA |
| DAC in reset | 2,1–8,9 nA (mai 0, sotto il ginocchio di 190 nA) |

**Il rumore all'anodo della derivazione** (`ldr/tb_psu_rumore.log`, 25 °C):
- dal simulatore, 1,05 µV/√Hz a 10 nA e 20 nV/√Hz a 20 mA;
- aggiungendo a mano DAC (1,2 µV/√Hz × 0,181) e op-amp (2 × 28 nV/√Hz) senza il filtro di C_X,
  ~1,4 µV/√Hz;
- limite 690 µV/√Hz (ADR-039).
