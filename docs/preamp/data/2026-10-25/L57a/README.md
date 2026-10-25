# L57a — l'RCA a caldo: il banco provato, i numeri di oggi, le strade, la scelta (2026-10-25)

Report: `docs/preamp/reports/2026-10-25-L57a-rca-a-caldo.md`. Decisione: **ADR-101**. Non conformità:
**NC-059** avanza (si chiude in L57b). Il circuito non cambia in questo lotto.

## Che cosa c'è

| Percorso | Che cosa |
|---|---|
| `script/genera.py` | Il banco dell'RCA a caldo. Modo `l53`/`l53gate`: il testo di L53 riga per riga col blocco scelto (caso noto). Modo `oggi`: la catena di oggi (+ R_G 1 M, le scarica lato condensatore), `--prot` (resistenza, diodi ai rail o a ±V), `--rete`, `--mute`, `--forma` |
| `script/verifica_noto.py` | Il caso noto: le corse col blocco di L53 contro i CSV di L53 (0,5 % o 1 mV / 0,01 mA) |
| `script/spl.py` | I picchi in dB SPL a 1 m (convenzione di L53 / NC-028) e contro i limiti dell'LSK489 → `rca_spl.csv` |
| `script/forma.py` | La corrente di gate sulla forma d'onda → `rca/forma/forma.txt` |
| `script/dist.py`, `nodeset.py`, `leggi_costo.py` | Il costo al segnale: THD (metodo di L46a) e rumore → `costo/costo.csv` |
| `script/esegui.py <gruppo>` | Genera e corre un gruppo: `oggi`, `forma`, `strade`, `reti`, `mute`, `an015`, `costo`, `costo_an015` (tre corse alla volta, ~65 MB l'una) |
| `script/sintesi.py` | Per variante e rete il caso peggiore in classe II → `sintesi.csv` |
| `rca/noto/` | Il caso noto: `gain_block_L53.subckt` (dal commit 96bacb07, stesso hash del blob) e le corse |
| `rca/oggi/`, `rca/strade/`, `rca/reti/`, `rca/mute/`, `rca/an015/` | Le corse (deck, deck risolto, log, `rca.csv`, `rca_spl.csv`) |
| `costo/` | I deck e le corse del costo, `nodeset.inc` (il punto di lavoro vivo), `costo.csv` |

Nomi delle varianti: `r<R>_rail` (diodi ai rail), `r<R>_lim5` (diodi verso ±5 V, il limitatore a
~±5,6 V scelto), `r<R>_z12` (AN-015: diodi e zener da 12 V, sorgente ideale), `r2k2` (sola resistenza);
`_rete09` / `_rete11` la rete a −10 / +10 %; `mute_` il mute inserito (contatti aperti, 1 pF).

## Rifare

```sh
P=/Users/roberto/EDA/docs/preamp/data/2026-10-25/L57a/script
/usr/bin/python3 $P/genera.py l53 <deck> --blocco docs/preamp/data/2026-10-25/L57a/rca/noto/gain_block_L53.subckt
/usr/bin/python3 $P/verifica_noto.py             # dopo le due corse del caso noto
/usr/bin/python3 $P/esegui.py oggi               # e strade, reti, mute, an015, forma
/usr/bin/python3 $P/nodeset.py                   # prima del costo
/usr/bin/python3 $P/esegui.py costo              # e costo_an015
/usr/bin/python3 $P/leggi_costo.py
/usr/bin/python3 $P/sintesi.py
```

Le forme d'onda di `--forma` (~3,5 MB a caso) non sono versionate (`.gitignore`).

## Ipotesi dichiarate

- Quelle di L53 (`data/2026-10-12/L53/rca/genera.py`): il polo caldo 10 ms prima della massa; la
  sorgente a terra con 10 mV e 0,65 V; in classe II la massa a metà rete attraverso 1 nF e 3,46 nF
  (0,25 mA a 230 V); il contatto 0,1 Ω.
- I diodi di protezione sono il modello del 1N4148 (D1N914, l'unico diodo del repo); i riferimenti a
  ±5 V e gli zener da 12 V sono sorgenti ideali. Le parti vere si scelgono in L57b.
- Il mute inserito: il contatto aperto del relè fra il condensatore e il jack, 1 pF (limitations #63).
- Il costo: la THD si legge sul nodo dopo i 47 Ω, prima del 4,7 µF, con la sorgente oltre C_IN (i due
  condensatori partivano con un transitorio a rampa che metteva un pavimento di −101 / −103 dB a 1 kHz,
  uguale in tutte le varianti); il rumore con la sorgente da 2,5 kΩ e il punto di lavoro vivo
  (`nodeset.inc`): coi diodi alcuni punti di lavoro ripiegavano su un blocco **spento** (guadagno 0,0008),
  con una cifra di rumore plausibile e falsa; `leggi_costo.py` rifiuta un guadagno lontano da 1.
- E5 è una stima per eccesso: il rumore aggiunto, portato al jack col guadagno peggiore (×3,152), in
  quadratura con la cifra peggiore di E5 (4,577 µV).
