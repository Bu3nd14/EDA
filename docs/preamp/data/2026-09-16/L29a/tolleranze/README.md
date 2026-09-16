# Le tolleranze del solutore — perché sono cambiate, e la prova che non cambiano la misura

Dati del 2026-09-16, L29a (ripresa). **SIMULATI.**

## Il difetto

I tre deck `tb_v2_mute_*.cir` portavano `.options reltol=1e-6 vntol=1e-9
abstol=1e-15`. Con quei valori **il deck delle varianti e quello del graduale
non sono eseguibili**, e non per lentezza generica: dove il jack sta vicino a
zero — cioè in ogni cella **senza segnale** a mute inserito — un `vntol` da 1 nV
domina il controllo del passo del transitorio, il passo collassa e non risale.

Misurato il 2026-09-16 sulla cella `var0_100k_lz` (mute lungo senza segnale,
inserzione a 1,0 s):

| | |
|---|---|
| Avanzamento | **2,71 ms di transitorio ogni 100 s di calcolo** |
| Estrapolato alla cella intera (5 s) | **~41 ore**, per **una** cella su 87 |
| La stessa cella con `vntol=1e-6 abstol=1e-12` | **5,5 s** |

Non ci sono errori di convergenza nel log: sono passi minuscoli, non tentativi
falliti. Le celle **con** segnale non ne soffrono, perché lì `reltol × |v|`
(1e-6 × 12 V = 12 µV) domina su `vntol`.

Spiega perché il deck del pavimento girava ieri — non ha celle in mute — e
perché varianti e graduale erano rimasti «fermati».

## La prova che la misura non cambia

Stessa cella con segnale (`var0_100k_bm` e il suo riferimento
`var0_100k_bmmai`), fatta girare due volte cambiando **solo** le tolleranze, e
analizzata con `v2_metodo.py analizza`. Manifesto in `manif_ctrl.csv`, tabelle
in `ctrl_vntol_1e-9.csv` e `ctrl_vntol_1e-6.csv`.

| Grandezza | Uscita | `vntol=1e-9` | `vntol=1e-6` | scarto |
|---|---|---|---|---|
| A_rel | MAINJACK | 12,16 V | 12,11 V | 0,4 % |
| A_rel | FIXJACK1/2 | 3,891 V | 3,876 V | 0,4 % |
| B2 | MAINJACK | 33,23 mV | 33,03 mV | 0,6 % |
| B2 | FIXJACK1/2 | 11,02 mV | 10,96 mV | 0,5 % |
| C2_rel | MAINJACK | 8,875 V | 8,871 V | 0,05 % |
| C2_rel | FIXJACK1/2 | 3,057 V | 3,056 V | 0,03 % |
| **C_pav** (pavimento) | MAINJACK | 1,256 / 1,260 mV | 1,270 / 1,214 mV | ~1 % |
| **C_pav** (pavimento) | FIXJACK1/2 | 184,7 / 186,3 µV | 187,8 / 182,8 µV | ~2 % |

**Il pavimento è la cifra che conta**, perché è quella che decide se un valore di
C è una misura o rumore, ed è **invariata**. Resta anche coerente con quella di
ieri misurata a tolleranza stretta (1,23 mV sulla principale, 188 µV sulle
fisse, `data/2026-09-15/L29a/esplorazione/pav4_out.csv`).

`vntol=1e-6` resta **100 volte** sotto la soglia di A e B (100 µV) e **1000
volte** sotto quella di C (1 mV, ADR-035).

## Il limite, dichiarato

Il confronto è possibile **solo sulle celle con segnale**, perché sulle celle
senza segnale la tolleranza stretta non termina: lì l'uguaglianza delle due
tolleranze è **argomentata, non misurata**. L'argomento è che il meccanismo del
collasso (il `vntol` che domina quando `|v|` è piccolo) riguarda la *dimensione
del passo*, non l'accuratezza della soluzione, e che sulle celle dove entrambe
girano le cifre coincidono entro l'1 %.

## Come rifarlo

I due deck di prova si ottengono dal deck risolto che `run_simulation.sh`
scrive, restringendo i cicli a una variante, un carico e una cella, e cambiando
la sola riga `.options`.
