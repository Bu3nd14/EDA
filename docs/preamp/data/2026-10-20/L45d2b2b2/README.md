# L45d2b2b2 — il comando dei relè e i 5 V della logica (2026-10-20)

Seconda parte di **L45d2b2b** (b1 i diodi della tenuta, ADR-093; b2 questa, ADR-075). L'utente
all'inizio: **«Una sessione»**, nessuna divisione. Report `../../../reports/2026-10-21-L45d2b2b2-comando-5v.md`.

`<A>` = questa cartella, `<R>` = la radice del repo.

## Il banco

`psu/` è il banco di L45d2b2b1, **copiato**; le intestazioni di `genera_tb_psu.py` e `modi.py`
dichiarano ogni cambio:

| Cambio | Perché |
|---|---|
| `SONDE_I`: una sorgente da 0 V in serie a un **pin** (drain di Q501, Q502, Q503, Q505; anodo di D507 / D509; LM4040; collettore e base di Q504; uscite di U503 e U504), solo nei casi di guasto; `--sonde` | le parti del comando contro i loro limiti: la corrente non era mai stata misurata |
| `i(vfc)`: la corrente del corto stesso | il bilancio di Kirchhoff del controllo |
| `modi.py`: `RIGHE_075` (D506, D508, D505, K501 bobina, R503, R510, R512 in corto, U504 IN-OUT) a rete −10 / 0 / +10 % | le righe di ADR-075; D508, K501, R503, R510, R512 e U504 erano `uguale` / `calcolo` in L45c2 |
| `corri_seq.sh`: `GIRI_MAX` dall'ambiente (8 di default, 20 qui) | il comando che riparte (sotto) |
| `--n2n7002 ds` | il 2N7002 tarato sul datasheet (sotto) |
| `--serie2`, `--rk`, `--mos`, `--u504doppio` | le opzioni senza toccare il sorgente |

Senza opzioni, fuori dai casi di guasto, il deck è quello di L45d2b2b1 riga per riga.

### Il controllo della sonda (`controllo_sonda.txt`)

`f_d506_corto_mus` sul banco di L45d2b2b1 (`psu_vecchio/`, una copia con il solo `GIRI_MAX`; non nel
repository) e su questo:
1. il core al punto fisso è uguale entro 0,2 ms (la regola di `confronta.py`): un evento si sposta
   di 1 µs. Ogni colonna in comune sta entro 10 mV, salvo al più 20 campioni su 30 001; il peggiore è
   MUTE_CMD, con 5 campioni sui fronti. **La soglia di 10 mV è fissata dopo la prima corsa**: con
   «byte per byte» e poi con 1 mV cadeva su un evento spostato di 1 µs e su ADC_MD (3 mV);
2. Kirchhoff: il drain di Q501 è uguale alle bobine meno il corto, e l'anodo di D507 è uguale a
   meno il corto, entro 1 mA + 1 %;
3. sabotaggio: le bobine G6K di prima (438,33 Ω) nel bilancio → preso. **Il margine è sottile**
   (1,3 mA oltre la tolleranza).

### Il comando che riparte

Con D506 in corto il firmware legge la caduta come un buco di rete e non come un guasto (§ 4.5:
«rete assente», `ADC_MD`). Al ritorno rifà l'accensione, il corto si ripresenta, e così via: tre
impulsi nel primo secondo, poi altri. Ogni giro del punto fisso porta l'accordo un ciclo più in là
(L45c2 ci arrivò al giro 9). Con R503 in corto la logica scende a ~2,5 V e il firmware batte ogni
20–40 ms con centinaia di sostituzioni di MUTE_G_IN: **non c'è un punto fisso**. Le tre corse sono
lette all'ultimo giro (`giro` = «g20 SENZA punto fisso»), e le colonne del jack restano vuote; il
calore del LM4040 non dipende dal firmware.

### Il 2N7002 del banco

`MNGEN` a W 2000u (L41a) satura a ~2,5 A con 4,5 V sul gate. Il 2N7002 di Nexperia (Rev. 7, fig. 5,
letto a occhio) satura a ~0,55–0,7 A. Con `--n2n7002 ds` (W 571u, 0,70 A a 4,5 V, 0,91 A a 5 V) il
guasto cambia forma: meno corrente, più tensione sul MOSFET. **A rete +10 % D506 in corto resta
acceso**: VRELAY_REG non scende sotto gli 11,0 V del sorvegliante, e Q501 resta a 6,4 W per sempre.

## I limiti delle parti

`limiti_parti.csv`: dai datasheet, letti dall'agente bom-component-manager (solo web) e dai PDF in
`vendor/`; ogni riga ha la fonte e il tipo di lettura (DS, curva, secondaria). Le Tj sono a 60 °C
d'aria. Il tetto `tj100_C` di `riassunto_075.py` applica la Rth di regime alla media dei 100 ms
peggiori: **per eccesso** (lo Zth a 100 ms è più basso).

## Le corse

| Etichetta | Cosa | Analisi |
|---|---|---|
| `seq/oggi/` | le 24 righe sul circuito di oggi, banco di L41a | `analisi_oggi.csv`, `riassunto_oggi.*` |
| `seq/oggi_ds/` | le 12 righe del comando col 2N7002 tarato | `*_oggi_ds.*` |
| `seq/opz_a/` | A: diodi sdoppiati, Q503 DMN6075S | `*_opz_a.*` |
| `seq/opz_b/` | B: Q501–Q503 DMN6075S | `*_opz_b.*` |
| `seq/opz_a2/` | **A2: diodi sdoppiati, 47 Ω nel drain di Q503** | `*_opz_a2.*` |
| `seq/opz_r/` | R503, R510, R512 sdoppiate | `*_opz_r.*` |
| `seq/opz_5v/` | due MCP1703A in serie (rifatta: la prima corsa metteva il corto a valle di tutti e due, perché la sonda aveva rinominato il pin) | `*_opz_5v.*` |
| `seq/norm_base/`, `seq/norm_opz/`, `seq/norm_a2/` | perdita, mute dal tasto, accensione, spegnimento, rilascio, senza e con le opzioni | `norm_opz_primo.csv`, `norm_a2.csv`, `picchi_drain.txt` |
| `corse/oggi_100k/`, `corse/opz_a2_100k/` | la catena audio: D508 e K501 oggi, K501 con A2 | `analisi.csv` |

Le forme d'onda (`*_out.txt`) non stanno nel repository: si rifanno.

## La scelta e il sorgente

L'utente (2026-10-21): **«Diodi doppi + 47 Ω»**, **«Due regolatori in serie»**, con le resistenze
sdoppiate → **ADR-094**. Il sorgente: D530 / D531 / D532, R552, R553–R555, U512, C536; `psu.py`
133 parti. Il banco sul sorgente (`psu/corri_sorgente_075.sh`):

| Etichetta | Cosa | Esito |
|---|---|---|
| `seq/sorgente/` | `RIGHE_SORGENTE` di `modi.py`: ogni metà di ogni parte sdoppiata in corto, U504 e U512, la bobina di K501, alle tre reti (eventi `musm10s` / `muss` / `musp10s`), 2N7002 tarato | `analisi_sorgente.csv`, `riassunto_sorgente.*`: 171 righe dentro; «fuori» solo R552 nel tetto dei 100 ms (Rth di regime su ~0,2 s, per eccesso) |
| `seq/norm_sorgente/` | le sequenze normali | `norm_sorgente.csv`: jack 17,5 ms, Δ 17,1 ms (17,4 / 17,3 prima), MUSICA uguale |
| `seq/s074/` | le righe di ADR-074 a rete nominale | `analisi_s074.csv`: uguali a `../L45d2b2b1/analisi_sorgente.csv` entro 1e-5 |
| `rete/prima/`, `rete/sorgente/` | regime e perdita di rete alle tre reti | `rete_sorgente.csv`: regolatori uguali, tenuta di VRELAY a −10 % 46,4 → 51,2 ms |
| `timer/prima/`, `timer/sorgente/` | lo standby | dal secondario di T2 96,17 → 96,04 mW |

Il guardiano dello stato di riposo e il disegno dell'alimentatore:
- `falsi/psu_prima_di_adr094.net` è rifiutata dal disegno, che chiede U512;
- `falsi/psu_q503_non_riconosciuto.net` (il drain di Q503 senza R552 verso la bobina) è rifiutata da
  `check_relay_safe_state.py --timer`, invece di lasciar fuori Q503 in silenzio.

```sh
/bin/zsh <A>/psu/corri_sorgente_075.sh
/usr/bin/python3 -I <A>/script/analizza_075.py <A>/seq/sorgente <A>/analisi_sorgente.csv @<A>/lista_sorgente.txt
/usr/bin/python3 -I <A>/script/riassunto_075.py <A>/analisi_sorgente.csv <A>/riassunto_sorgente.csv
/usr/bin/python3 -I <A>/script/confronta_norm.py <A>/seq/norm_base <A>/seq/norm_sorgente <A>/norm_sorgente.csv
/usr/bin/python3 -I <A>/psu/riassunto_rete_074.py <A>/rete_sorgente.csv <A>/rete/prima <A>/rete/sorgente
```

## Rifare

```sh
/bin/zsh <A>/psu/corri_seq.sh --solo-compila
/usr/bin/python3 -I <A>/psu/lista_075.py > <A>/lista_075.txt
/usr/bin/env GIRI_MAX=20 /bin/zsh <A>/psu/corri_lista.sh <A>/lista_075.txt oggi
/bin/zsh <A>/psu/corri_opzioni_075.sh
/bin/zsh <A>/psu/corri_opzioni_075b.sh
/bin/zsh <A>/script/analizza_tutto.sh
/usr/bin/python3 -I <A>/script/confronta_norm.py <A>/seq/norm_base <A>/seq/norm_a2 <A>/norm_a2.csv
/bin/zsh <A>/script/corri_catene.sh
```
