# L60a — le scelte che il rivelatore copriva, senza rivelatore e con 1 µF sulla Stax (2026-10-15)

Prima parte di **L60**, divisa dall'utente all'inizio («Tre parti»): le scelte 6, 8, 9 e 10 di
`../../2026-10-14/L45d1/scelte_L45d2.pdf`, che ADR-072 affidava al rivelatore di continua e che
ADR-081 ha lasciato scoperte togliendolo. Report `../../../reports/2026-10-15-L60a-scelte-scoperte.md`,
decisione **ADR-082**. **Il circuito non cambia**: il condensatore da 1 µF e i carichi sono solo nel
banco.

`<A>` = questa cartella. Gli script ricavano la radice del repo dalla propria posizione.

## Il banco

Il canale di L45a (`2026-10-13/L45a/script/genera_canale.py`) e i guasti dei controlli di L45b
(`2026-10-13/L45b/script/genera_controlli.py`), importati e non copiati, con due differenze:
- `CFIX2` (il condensatore d'uscita della Stax) a **1 µF** (ADR-081);
- **i carichi montati** (cj 100k, Singxer 10k, Stax 50k): P10 sulla fissa 2 col carico della Stax
  (ADR-081 punto 3). L45b e L45d2b1 lavoravano a vuoto.

Nessun rivelatore, nessun mute dopo il guasto; rail ideali a ±15 V (il sorvegliante non c'è). Il
guasto a 0,3 s, 2,3 s di corsa. L'analisi è `2026-10-13/L45b/script/analizza_p10.py`, com'è.

## I file

| File | Cosa |
|---|---|
| `script/genera_L60a.py` | i 30 deck in `deck/<gruppo>/` e `deck/lista.txt` |
| `script/uno.sh`, `script/corri.sh` | le corse con `run_simulation.sh`, 8 alla volta; esiti in `run/esiti.tsv` |
| `analisi.csv` | per ogni corsa e ogni jack: picco, tempo sopra 0,87 V, continua finale; il calore del blocco |

## I risultati (`analisi.csv`)

**Il riferimento**, prima dei numeri nuovi:

| Corsa | Atteso | Misurato |
|---|---|---|
| R126 in corto in F2, 4,7 µF, a vuoto | 44,2 ms (L45d2b1 `riv_F2`, senza scatto) | 44,2 ms |
| F2 al rail, 4,7 µF, carico della Stax | ~0,56 s (L61) | 552 ms |
| isolamento di K3 sul jack, 4,7 µF, a vuoto | 12 V fino alla fine (L45b) | 12 V fino alla fine |
| F2 al rail, **1 µF**, carico della Stax | 117 ms (ADR-081, a calcolo) | 117,5 ms |

**Le scelte**, tempo sopra 0,87 V (picco):

| Gruppo | Corsa | Stax | Principale | Fissa 1 |
|---|---|---|---|---|
| 1 | blocco A al rail | 118 ms (13,8 V) | 296 ms | 129 ms |
| 6 | K3 sul NO / sul comune, 10 Ω | **12 V per sempre** | — | — |
| 6 | K3 sul NO, 1 kΩ | **11,7 V per sempre** | — | — |
| 6 | K13 (selettore), 10 Ω / 1 kΩ | 116 / 95 ms | 510 / 258 ms | 127 / 105 ms |
| 6 | K7 (cima di C_T), 10 Ω / 1 kΩ | 70 ms / niente | 95 ms / niente | 77 ms / niente |
| 6 | K2 sul NO | — | — | 12 V per sempre |
| 6 | K4 sul NO / sul comune | — | 12 V per sempre | — |
| 6 | K1 (ramo +3 di B) | — | 432 ms (5,7 V) | — |
| 8 | filo + aperto, 0 / +10 dB | **388 / 421 ms** (1,35 / 1,27 V) | 932 / 957 ms | 410 / 433 ms |
| 8 | filo − aperto, 0 / +10 dB | 3,7 mV | ≤ 12 mV | 3,7 mV |
| 9 | condensatore della Stax in corto | 6,3 mV | — | — |
| 9 | lo stesso, poi A / F2 al rail | **14,4 / 15,0 V per sempre** | 296 ms / — | 129 ms / — |
| 10 | R126 in corto in A / F2 / F1 / B / B +10 dB | 37 / 38 / — / — / — ms | 32 / — / — / 41 / 47 ms | 29 / — / 30 / — / — ms |

Con R126 in corto, in ogni posizione, Q127 (il moltiplicatore di Vbe) dissipa 0,49 W: ~231 °C in
SOT-23 (417 °C/W), ~88 °C in SOT-223 (125 °C/W). L'uscita del blocco torna a −0,22 V.

## Rifare

```sh
/usr/bin/python3 -I <A>/script/genera_L60a.py
/bin/zsh <A>/script/corri.sh <A>/deck/lista.txt          # ~20 s, 30 corse
/usr/bin/python3 -I docs/preamp/data/2026-10-13/L45b/script/analizza_p10.py <A>/analisi.csv <A>/run/<gruppo>/<corsa> ...
```

Le forme d'onda (`run/**/*.dat`, ~1 GB) non stanno nel repository: si rifanno.
