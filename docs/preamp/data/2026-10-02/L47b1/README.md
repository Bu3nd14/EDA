# L47b1 — la prova del mute: JFET contro fotoresistenza NSL-32SR3

Dati della prova di L47b1 (2026-10-02). Report: `docs/preamp/reports/2026-10-02-L47b1-prova-mute.md`.
Decisione: `docs/preamp/decisions/ADR-059-*.md`.

## Il banco, e cosa NON vede

Banco **ridotto**: sorgente (1,5 Ω) → cella del mute → ingresso del blocco A (R_IN 1 MΩ verso
massa, `gain_block.py`). Si misura `v(AIN)`. Gli stadi a valle sono lineari rispetto al mute: il
salto di livello e la distorsione della cella si vedono già lì. Il livello al jack si ricava col
guadagno massimo (×3,15, +10 dB); dB SPL di picco a 1 m con 100 µV = 33 dB SPL (NC-028, ADR-032).
La corsa sul preamp intero, col relè al jack e il caso peggiore di V2, è di **L47b2**.

Non vede, e il report lo dice accanto a ogni cifra:
- **la distorsione della NSL-32SR3**: il modello di L47a è un resistore lineare (`BCELL`), THD zero
  per costruzione. La tabella dice «non modellata»;
- **il rumore termico del canale del JFET in zona lineare**: il modello JFET di ngspice non lo ha
  (a Vds = 0 gm = 0). Né quello della LDR (`BCELL` è una sorgente B). Calcolato a mano: ~60–100 Ω
  ≈ 1–1,3 nV/√Hz, ~0,4 µV al jack;
- **il JFET sotto il pinch-off**: corrente zero nel modello (il datasheet: ID(off) ≤ 1 nA);
- la temperatura, la memoria della luce, la dispersione oltre le curve A–E.

## Come si rifà

Tutto con `/usr/bin/python3` (stdlib), dalla cartella `banco/`. ngspice `/opt/homebrew/bin/ngspice`.

| Script | Cosa fa | Esito di oggi |
|---|---|---|
| `modelli.py` | scrive `inc/jfet_angoli.lib` (copie RINOMINATE della scheda onsemi, VTO −1 / −1,68 / −5 V, rDS(on) 59,5 Ω tenuto) e la sonda: IDSS, rDS(on), spegnimento, TIP = originale | 22/22 controlli |
| `statico.py jfet` | 5 combinazioni d'angoli × 3 correttivi × 41 profondità: livello e THD a 1 e 20 kHz, \|H\| in mute, \|Zin\| minimo, comando → AIN | 615 righe, 0 rifiuti |
| `statico.py ldr` | NSL-32SR3, curve A–E e due incroci, correnti del profilo v4 per profondità: op + ac | 287 righe, 0 rifiuti |
| `riassunto_statico.py` | le due celle affiancate | — |
| `limite_jfet.py` | il limite fisico: partitore a L (1 k, 10 k, 33 k) e JFET verso massa col correttivo **ideale** (sorgente B, Vg = Vd/2 + Vc) | THD 6–30 % fra −1 e −20 dB |
| `rumore.py` | E5 della cella in gioco e il rumore del comando ammesso nella quota di 1 µV | trascurabile per entrambe |
| `sfumatura.py` | la sfumatura nel tempo, S col metodo di `scripts/v2_metodo.py` importato | JFET 24–46 dB; NSL-32SR3 7–10 dB a 6 s |
| `sfumatura.py --tempo`, `--tre` | la NSL-32SR3 a 2 e 3 s, cima del LED a 20 mA | S 13,1–17,4 dB a 3 s |
| `sfumatura.py --cima12`, `statico.py ldr --cima12` | la NSL-32SR3 con la cima a 12 mA di ADR-050 | S 12,7–16,9 dB a 3 s |

`run/controprova/piccolo_TIP_1k.*`: la controprova del banco. Lo stesso deck di `limite_jfet.py`
con 50 mV di picco invece di 3,818 V: THD 0,0002–0,0009 % da −1,6 a −25 dB. Il banco vede anche
la distorsione bassa; quella alta viene dal livello del segnale.

Le forme d'onda (`run/**/*.dat`, ~1,3 GB) non sono versionate (`.gitignore`): si rigenerano.

## Le guardie

`comune.guardia()` rifiuta un log con «Transient op started» (#33 #38), «Timestep too small» e
«aborted» (#35), «too many args» (#36), «no such device», «could not find» (#29), «is not
available» (un `print` di un vettore che non c'è: trovato qui, alla prima stesura di `modelli.py`),
«Error». **«failed» da solo non è un rifiuto** (#40). Le Note dentro una riga si ricuciono (#37).

Due rifiuti veri durante il lotto, entrambi presi dalla guardia e non dai numeri:
- `statico.py ldr` con la `tran` a stato fermo: «Timestep too small … trouble with B-instance
  b.xlp.bdx» su tutte e 7 le combinazioni, rc 0. Il ramo `?:` dello stato a regime fa collassare
  il passo. Rimedio: solo op + ac per la LDR statica (è lineare); la sfumatura nel tempo corre;
- la prima misura di |Zin| staccava la sorgente (RSRC 1 TΩ + iniezione, come `tb_e3_e5_ldr`):
  col JFET il connettore restava **senza percorso in continua**, il gate polarizzava il source e
  l'op era un altro circuito (6 kΩ in mute che non esistono). Rimedio: v(srcx) / corrente di ramo
  della sorgente, a 1,5 Ω. Non è un errore di `tb_e3_e5_ldr` (la LDR non ha giunzioni), ma lo
  diventa per qualunque cella con un gate: da ricordare in L47b2 se il banco E3 cambia cella.
