# 2026-09-09 — controfattuale del relè di guadagno (ADR-004)

Prodotto in **L4**. Deck: `spice/preamp/tb/tb_switch_v2_counterfactual.cir`,
rieseguibile in qualsiasi momento con

```sh
/bin/zsh scripts/run_simulation.sh spice/preamp/tb/tb_switch_v2_counterfactual.cir \
         results/preamp/tb_switch_v2_counterfactual
```

## Perché questi numeri sono nel dossier

ADR-004 ha **scartato** l'idea di mettere il contatto del relè in serie a
R_f (il ramo dell'anello). Una decisione di progetto porta informazione
solo se la disposizione scartata è mostrata **fallire**: questo è il
mezzo falsificabile della verifica V2, e il transitorio del relè nel
dossier va affiancato proprio a questo controfattuale.

Con R_f aperto l'anello è rotto, la coppia d'ingresso vede solo il
proprio offset moltiplicato per tutto il guadagno ad anello aperto, e
l'uscita si appoggia al rail: **−13,68 V**.

## I tre file

| File | Stato | `v(OUT)` |
|---|---|---|
| `tb_switch_v2_counterfactual.csv` | A — contatto **chiuso**, R_f = 1,50 kΩ | −0,0372229 V |
| `tb_switch_v2_counterfactual_open.csv` | B — contatto **aperto**, R_f = 1e12 Ω | **−13,676851 V** |
| `tb_switch_v2_counterfactual_reclosed.csv` | C — richiuso, controprova di B | −0,0372229 V |

C esiste per escludere che B sia un artefatto del solutore: A e C
coincidono a tutte le cifre.

## Legenda delle colonne

`run_simulation.sh` intesta i CSV `col0…colN`, quindi l'identità delle
colonne vive solo qui e nel commento dentro il deck.

Un `wrdata` preso da un `.op` scrive **una riga** e, per ogni vettore
richiesto, una **coppia** di colonne `(scale, valore)`. Lo *scale* di un
plot `op` è un vettore arbitrario del plot e **non significa niente**. I
dati sono quindi le colonne **dispari**:

| Colonna | Vettore |
|---|---|
| col1 | `v(OUT)` |
| col3 | `v(FB)` |
| col5 | `v(NX)` |
| col7 | `v(NY)` |

Le colonne pari (col0, col2, col4, col6) sono lo scale ripetuto: si
ignorano.

## Provenienza e limite

Modelli **segnaposto** (`spice/preamp/placeholder_devices.lib`), non
vendor. Questo dato è un risultato **in continua**, cioè la parte che il
progetto dichiara credibile anche con i segnaposto: nessuna cifra di
distorsione o di rumore va ricavata da qui.

`tb_switch_v2_counterfactual.log` è l'evidenza: contiene gli stessi
`v(out)` stampati da ngspice, con cui i CSV sono stati confrontati.
