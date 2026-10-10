# L51b — il dossier rigenerato, l'alimentatore e il firmware: i dati

Sotto, `<L>` è questa cartella, `<P>` la sorella `../L51b-prima/` e `<R>` la radice del repo.
L'alimentatore è quello di L47c2a (`psu.py` non è cambiato dopo); la scheda audio è quella di L48b.
Nessun sorgente, deck versionato o firmware è stato toccato.

## Le scelte dell'utente (2026-10-09)

- **«Tutto col selettore»**: tutte le catene dell'alimentatore ricorse oggi col carico di oggi, e
  come seconda strada lo stesso col carico di prima.
- **«Sì, i rail di oggi»**: il carico dei rail non è più quello di L41a (265 mA per rail), ma
  quello di `tb_op` di oggi.
- **«Rifare e mostrarmela»**, poi **«Sì, così»**: la stima del calore con le potenze dal banco di
  oggi, il ferro dei trasformatori come ipotesi dichiarata.

## Due cartelle, gli stessi script

| Cartella | `carico.txt` | Cosa deve ridare |
|---|---|---|
| `<L>` | rail 293,62 / 301,7864 mA (8 × `tb_op` di L51a), resto di `VRELAY` 51,5 mA (L48a, il selettore), U503 col metodo gear | la prima strada del dossier |
| `<P>` | rail 265 / 265 mA, resto 42,4 mA, U503 col trapezoidale | L47c2a e L47c2b2 byte per byte |

Gli script di `psu/`, `ponte/`, `deck/` e `script/catena_audio.sh` sono **identici** nelle due
cartelle; il generatore legge il carico da `carico.txt` nella radice del lotto, e senza quel file
rifiuta. Il controfattuale col carico di L41a corre solo in `<P>`: su un altro carico non sarebbe
né quello di L41a né quello di oggi, e il generatore lo rifiuta.

| Percorso | Cosa |
|---|---|
| `psu/genera_tb_psu.py` | quello di L47c2b2 col carico da `carico.txt` (le differenze nell'intestazione) |
| `psu/genera_tutti.sh`, `corri_tutti.sh` | i quattro banchi (temporizzatore nominale e all'angolo minimo, rete, guasti) |
| `psu/corri_controfattuale.sh` | il controfattuale col carico di L41a (solo in `<P>`) |
| `psu/tutti_seq.sh`, `corri_seq.sh`, `analizza_seq.py`, `sano.py`, `confronta.py` | le 15 sequenze: le sei di L47c2a e le nove di L47c2b2 (U502 spento è in tutte e due) |
| `script/analizza_timer_in.py` | `analizza_timer.py` lanciato da dentro `timer/`, come L47c2a, senza `cd` nella shell |
| `script/catena_audio.sh` | il ponte, il deck di V2 dal sorgente di oggi, le 18 corse, le guardie, la tabella (la catena di L47c2b2) |
| `script/confronta_prima.py`, `confronto_prima_*.txt` | `<P>` contro L47c2a e L47c2b2: **109 file su 109 uguali** |
| `script/scomposizione.py`, `scomposizione.csv` | i picchi al jack di L47c2b2, di `<P>` e di oggi, coi due scarti in dB |
| `sonda_u503/` | le varianti numeriche dei due casi di U503 spento col carico di oggi (`prepara.py`, `corri.sh`, `esiti.tsv`) |
| `termica/genera_calore.py`, `tb_calore.cir`, `tb_calore.log` | il banco della rete di oggi a regime, con le medie delle potenze su 1,5–2,0 s |
| `termica/stima_telaio_l51b.py`, `.txt` | il modello del telaio di L30/L41a con le potenze dal banco |
| `falsi/esito.txt` | `run_host_tests.sh --falsi`: 19 su 19, uguale a L47c2a e L47c2b2 |
| `script/sabotaggi.py`, `sabotaggi.txt` | ogni controllo nuovo di `build_dossier.py` fatto fallire |

Le forme d'onda (`rete/*.txt`, `guasti/*.txt`, `seq/**/*_out.txt`, `corse/*.dat`, la sonda) sono
in `.gitignore`: ~8 GB.

## Come si rifà

Per ciascuna cartella (`<X>` = `<L>` o `<P>`), coi percorsi assoluti:

```sh
/bin/zsh <X>/psu/genera_tutti.sh
/bin/zsh <X>/psu/corri_tutti.sh            # due «errori» attesi: t_permit out of interval (L47c2a)
/usr/bin/python3 <X>/psu/analizza.py <X>/rete
/usr/bin/python3 <X>/psu/analizza.py <X>/guasti
/usr/bin/python3 <L>/script/analizza_timer_in.py <X>
/bin/zsh <P>/psu/corri_controfattuale.sh   # solo <P>
/bin/zsh <X>/psu/tutti_seq.sh              # ~5-8 min
/bin/zsh <X>/script/catena_audio.sh        # ~2 min
```

Poi:

```sh
/bin/zsh <R>/firmware/preamp_timer/test/run_host_tests.sh --falsi <L>/falsi/esito.txt
/usr/bin/python3 <L>/script/confronta_prima.py --fase tutto
/usr/bin/python3 <L>/script/scomposizione.py
/usr/bin/python3 <L>/termica/genera_calore.py
/opt/homebrew/bin/ngspice -b <L>/termica/tb_calore.cir -o <L>/termica/tb_calore.log
/usr/bin/python3 <L>/termica/stima_telaio_l51b.py > <L>/termica/stima_telaio_l51b.txt
/usr/bin/python3 <R>/docs/preamp/dossier/build_dossier.py --standalone <fuori dal repo>/dossier.html
/usr/bin/python3 <L>/script/sabotaggi.py
```

## Le cifre

**Col carico di prima** tutto è L47c2a e L47c2b2 byte per byte: deck, analisi, temporizzatore,
controfattuale, le 15 sequenze (testo, punto fisso, deck, uscite del core; i fatti di L47c2a a
quattro decimali, l'`analizza_seq.py` di L47c2b2 ne stampa sei) e il ponte. Il deck di V2 no: si
genera dalla scheda audio di oggi (il selettore, C_T), che il generatore del deck esige.

**Col carico di oggi** nessun verdetto cambia:

| | carico di prima | oggi |
|---|---|---|
| tenuta di `VRELAY_REG` ≥ 11,4 V, rete −10 % | 61,1 ms | **48,3 ms** (P9 ≥ 25) |
| rail + a 13,5 V dopo la perdita, −10 % | 73,9 ms | 65,5 ms |
| rivelatore guasto, −10 %: il mute prima della soglia | 1,2 ms | 0,4 ms |
| valle del grezzo −, rete −10 % | 18,05 V | 17,89 V |
| `VRELAY` a J1 < 9,6 V dopo `PERMIT`, U503 spento | 42,0 ms | 35,9 ms |
| Δ all'angolo minimo; standby da T2 | 16,91 ms; 80,5 mW | uguali |
| sequenze | 15 su 15 | **15 su 15** (U503 col metodo gear) |

**I guasti al jack** (`tabella.csv`, `scomposizione.csv`): U502 spento **0,815 mV** (51,7 dB SPL;
L47c2b2 0,893), U501 0,517 mV, il controfattuale senza Δ 14,8 mV (cade, come deve; L47c2b2 29,7),
il corto della linea a 12 V 14,9 mV sotto il tetto. Il dimezzamento del controfattuale e del corto
è la scheda audio di oggi (−6,0 dB col carico di prima), non il carico (0,00 dB).

**U503 e il metodo** (`sonda_u503/esiti.tsv`): col carico di oggi il trapezoidale con `gmin` 1e-9
di L47c2b2 non finisce `guasto_u503` (> 300 s, anche fermato a TE + 0,5 s) e ferma
`guasto_u503_min` a TE + 0,968 s; gear li finisce in ~12 s. Gear contro trapezoidale con `gmin`
1e-8 sul caso nominale: jack, guadagno e V+ < 10,6 V agli stessi istanti, i rail entro 0,5 mV.

**Il calore** (`termica/stima_telaio_l51b.txt`): 17,27 / 15,05 / 19,54 W (rete nom / −10 % /
+10 %), contro 17,04 / 14,05 / 20,18 di L41a; caso peggiore a 3 cm **57,2 °C**, gioco minimo
1,5 cm (era 2,0). La regolazione di `VRELAY` vale 0,63 W al peggio contro 1,34 ipotizzati (il
grezzo è ~15 V, non 20–23), e compensa il watt in più della scheda audio. Il ferro dei due
trasformatori, 1,95 W al peggio, è l'unica ipotesi.

**Trovato, non corretto** (il sorgente non si tocca in questo lotto): in `psu.py` il commento di
`C_VRELAY` cita 61,1 ms (oggi 48,3) e quello di `C_RAW` la valle di L41a, 18,1 V (oggi 17,9).
