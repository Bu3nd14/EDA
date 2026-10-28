# L54b2 — il temporizzatore sul sorgente: i comparatori, lo standby, la catena al jack (2026-10-28)

Seconda parte di **L54b** (diviso dall'utente all'inizio, «Tre parti»: L54b1 il sorgente, i
guardiani, i disegni e il banco col suo caso noto; **L54b2** il modello del costruttore dei
comparatori, lo standby e la catena al jack; L54b3 la robustezza al banco). Decisione di riferimento
**ADR-102**. `<L>` = questa cartella. Python di analisi con `/usr/bin/python3 -I`.

`psu/` è il banco di L54b1, copiato, con `carico.txt`. Le forme d'onda (`*_out.txt`, le CSV a passo
fine) non stanno nel repository: si rifanno.

## 1. Il TLV1701 del costruttore

`models/comparator/genera_tlv1701.py` scrive `models/comparator/tlv1701_ngspice.lib` dal file di TI
in `vendor/comparator/ti/TLV1702/` (sola lettura); ogni ritocco contato contro il file del
costruttore. Due sottocircuiti: **`TLV1701`**, il modello di TI tradotto per ngspice e niente altro, e
**`TLV1701_OC`**, una variante nominata coi ritocchi numerici (provenance, limitations #77). La
ricetta: `validate_models.py`, `tb_tlv1701`.

Le prove (`prova/`):

- `tb_sw.cir`: il senso degli interruttori SW di ngspice coi parametri di un VSWITCH. La traduzione
  di L41a dà un'isteresi larga quanto l'escursione e **non inverte** i quattro interruttori con
  Von < Voff: la causa del «DO NOT USE» di L41a.
- `tb_tlv1701_solo.cir` (+ `leggi_solo.py`) e `psa/`: il derivato da solo, nel circuito (V5 dietro
  1 Ω, 10 k di pull-up, il riferimento a 1,25 V), contro il file di TI non toccato col modo di
  compatibilità `psa`: le stesse soglie e gli stessi ritardi.
- `tb_ritardi.cir` (+ `leggi_ritardi.py`, passo 5 ns): TI **tpLH 574 ns, tpHL 460 ns** (SBOS589D
  560 / 460); soglia allo scostamento del modello, −0,4 mV; uscita bassa 75 mV a 0,5 mA; 55 µA.
- `tb_tlv1701_rampa.cir`: col modello di TI, V5 che sale non passa **2,19 V** (ngspice fermo,
  1,4 GB e in crescita); `tb_tlv1701_rampa_oc.cir`: la variante sì.
- Sul banco (`seq/costruttore/perdita/`), anche la variante si ferma: a 42,8 ms (la decisione con V5
  a ~1 mV), poi a 0,21 s (lo stadio d'uscita), dopo sette ritocchi.

**La scelta dell'utente** (2026-10-28), alla domanda coi numeri: **«Comportamentale tarato»**: il
comparatore comportamentale del banco coi numeri misurati sul modello di TI, dichiarato come
taratura. `psu/cmpta.lib` (`CMPTA`): soglia a −0,4 mV, la decisione larga 0,1 mV, un polo di 745 ns
(tpLH 581 / tpHL 457 ns contro i 574 / 460 di TI sullo stesso passo), l'uscita a 150 Ω, 55 µA, la
soglia d'alimentazione di `CMPOD` a 2 V.

## 2. I casi della sicurezza col comparatore tarato

`genera_tb_psu.py --comparatore {comportamentale,costruttore,costruttore18,tarato,tarato18}`:
predefinito `comportamentale`, che lascia il deck **byte per byte** quello di L54b1 (provato su
`perdita`); `tarato` = i dodici canali di U513–U515 con `CMPTA`, `tarato18` anche i sei di U505 /
U506 / U508. Solo con `--timer sorgente`. I nomi delle istanze e i piedini restano quelli di `CMPOD`
(i tre sorveglianti ciechi di `modi.py` spostano il gettone dell'uscita).

### I criteri, scritti prima delle corse

Le 31 corse di `../../2026-10-26/L54b1/lista_noto.txt` senza le tre del consumo (`lista_tarato.txt`,
`lista_tarato18.txt`: gli stessi argomenti più `--comparatore`), contro `an_sorgente.csv` (24 casi di
sequenza) e le 7 righe di `an_fmea_sorgente.csv` di L54b1, con `confronta_noto.py` di L54b1:

- gli stessi verdetti: `C2`, `C3`, `r41`, `s41`, `musica_TE`, `mus_end`, `k501_end`, `esito`;
- ogni istante entro **max(0,1 ms; 0,5 %)** (0,1 ms è un campione della griglia del banco: il limite
  di 0,05 ms di L54b1 era sotto la sua risoluzione); `vplus_end` entro 0,01 V;
- il controfattuale senza Δ (`cf_nodelta`) fallisce come in L54b1.

Che cosa ci si aspetta, e perché: i ritardi del comparatore (~0,5 µs) sono 200 volte sotto il
campione; lo scostamento di 0,4 mV sposta un istante di 0,4 mV / (pendenza all'incrocio), sotto il
campione per ogni RC del temporizzatore salvo uno che incroci il riferimento a meno di 4 V/s. Una
differenza oltre i limiti si spiega coi numeri (quale canale, quale pendenza), non si accetta.

## 3. Lo standby

(in corso)

## 4. La catena al jack

(in corso)
