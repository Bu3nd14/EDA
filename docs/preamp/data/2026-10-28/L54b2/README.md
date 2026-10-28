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

### Gli esiti

`lista_finale.txt` (100 corse, `corri_lista_an.sh … 5`, tutte pulite, nessun ripiego): `fin_*` il
comportamentale sul sorgente di L54b2 (con R585, sotto), `fint_*` il tarato sui dodici canali,
`fint18_*` sui diciotto. `dirs_noto.py` dà le cartelle nell'ordine di L54b1; `confronta_noto.py` è
quello di L54b1 coi limiti di sopra.

- **Il tarato contro il comportamentale sullo stesso sorgente** (`confronta_fint_*_vs_fin.txt`,
  `confronta_fint18_*_vs_fin.txt`): **tutti i verdetti uguali**, `cf_nodelta` fallisce come deve. Gli
  istanti escono dal limite che avevo scritto: il guadagno +0,3 ms alla perdita di rete e nei buchi,
  il jack +0,2–0,4 ms nei sorveglianti ciechi (+0,2–0,8 ms coi diciotto canali), la musica dopo il
  buco di 20 ms 4,1 ms prima (537,2 invece di 541,3 ms, sempre ≥ 500). **La spiegazione, coi
  numeri**: le uscite del temporizzatore scaricano condensatori, e il tarato assorbe a 150 Ω invece
  dei 50 Ω di `CMPOD` (AT_PGT, 1 µF dietro un BAT54: τ 150 µs invece di 50). Provato su `perdita`
  con `CMPTA` a 50 Ω: il guadagno torna da 55,7 a 55,6 ms (comportamentale 55,5): metà dello scarto è
  la resistenza d'uscita, il resto è entro un campione della griglia. Lo scostamento di 0,4 mV e il
  ritardo di ~0,5 µs non si vedono.
- **R585 contro L54b1, col comportamentale** (`confronta_fin_*.txt`): cambiano solo i casi in cui la
  ritenuta scatta: K501 +2,7 ms (129,1 → 131,8; 161,6 → 164,3), il guadagno +0,4 ms. Le energie (R550
  7,795 / 9,523 J, R552 0,479 / 0,546 J) sono quelle del rimedio sul banco.

## 2b. L'accensione a freddo col frontale acceso (ADR-103)

Col tarato `perdita` non arrivava alla musica: con le uscite aperte sotto 2 V, AT_F (100 kΩ da V5)
seguiva V5 e la ritenuta scattava prima che i comparatori si svegliassero (a 0,16 s, V5 1,81 V, la
base di Q513 a 0,62 V). Col comportamentale la stessa base arriva a 0,50 V: passava per 0,1 V
(limitations #78). `--rfpd <ohm>` (una resistenza da AT_F al ritorno), `--valore C554=…`,
`--comparatore tarato22` (le uscite vive al minimo del datasheet, 2,2 V); `lista_rimedi.txt`,
`lista_rimedi2.txt`.

| la base di Q513 al massimo con V5 < 2,3 V | |
|---|---|
| comportamentale | 0,50 V |
| tarato a 2,2 V | la ritenuta scatta |
| tarato a 2,2 V, C554 470 nF | 0,61 V |
| tarato a 2,2 V, 33 kΩ | **0,30 V** |

Coi due rimedi la ritenuta scatta e tiene in `guasto`, `guasto_u503`, `ritenuta_frontale`, nel
sorvegliante cieco (VRELAY_EN a ~0,79 V fino alla fine; `ritenuta_frontale` la rilascia col
frontale). La scelta dell'utente: **«Resistenza verso il ritorno»**, R585 33 kΩ (ADR-103).

## 3. Lo standby

`--standby {oggi,v5on,alti,v5on_alti,v5on_mr}` (`lista_standby.txt`, `lista_standby_mr.txt`); lo
standby dal secondario di T2, 2,5–3,0 s, a rete −10 / 0 / +10 %:

| | standby | la sequenza |
|---|---|---|
| oggi | 116,1 / 130,1 / 144,2 mW | — |
| `v5on`: 5 V dal solo frontale | 67,5 / 76,0 / 84,7 | lo spegnimento dal frontale perde l'ordine: il guadagno a 16,0 invece di 47,6 ms, K501 a 19,4 invece di 123,1 |
| `alti`: i pull-up ×10 (non R576) | 80,3 / 90,3 / 100,4 | l'apparecchio non si accende in nessun caso |
| `v5on_mr`: 5 V finché il frontale è chiuso o K501 è chiuso | 71,5 / 80,5 / 89,7 | ogni sequenza uguale (K501 a un campione) |

La scelta dell'utente: **«Lasciare com'è»** (ADR-103). Sul sorgente di L54b2 lo standby è
**116,14 / 130,08 / 144,21 mW**, lo stesso di L54b1.

## 4. La catena al jack

Il ponte di L41c (`ponte/estrai_ponte.py`, copia di quello di L51b) con `--passata-unica --te 3.0`:
col temporizzatore a comparatori non c'è firmware né punto fisso; rifiuta una corsa senza `ok.txt` o
non del sorgente a comparatori (provato su una corsa del micro di L56). `ponte/nom/` i nove casi del
sorgente; `ponte/m10/`, `ponte/p10/` i tre casi dalle loro corse e gli altri sei copiati da `nom/`
(LEGGIMI). `script/catena_audio.sh <rete>`: il deck di V2 `--matrice l41c`, 18 corse, la guardia, la
partenza, l'analisi, gli eventi, la tabella (`tabella_<rete>.csv`). Ogni rete: 18 corse su 18
passano la guardia, 0 non partono dal punto giusto; `cf_nodelta` 69,7 dB SPL, fallisce come deve.

Il jack principale, picco a 1 m (formula di NC-028; la soglia di V2, 100 µV, è ~33 dB SPL; una stanza
silenziosa è 25–35 dB(A): un picco contro un livello pesato A):

| | rete −10 % | 0 % | +10 % | L56 (0 %) | il dossier (L51b) |
|---|---|---|---|---|---|
| spegnimento dal frontale | −55,2 dB SPL (3,70 nV) | −55,2 (3,70 nV) | −55,2 (3,70 nV) | −58,5 (2,52 nV) | −35,9 (33,9 nV) |
| perdita di rete | **+4,4 (3,52 µV)** | −55,3 (3,63 nV) | −55,2 (3,69 nV) | −46,7 (9,79 nV) | −34,7 (39,2 nV) |
| perdita, Δ all'angolo minimo | +4,4 (3,52 µV) | −55,4 (3,63 nV) | −55,2 (3,70 nV) | −43,0 (15,0 nV) | −35,0 (38,0 nV) |

- **A rete −10 %** il grezzo è a 16,8 V allo stacco e i regolatori escono di regolazione ~2,4 ms prima
  del jack (17,4 ms): il rail + −21 mV, il rail − −49 mV allo stacco. Il colpo è +4,4 dB SPL, 29 dB
  sotto la soglia di V2 e sotto una stanza silenziosa; ma la frase di ADR-102 «il rail resta in
  regolazione fino allo stacco in ogni caso» a −10 % non vale, di qualche decina di mV.
- **Le cifre del dossier** (33,9 / 39,2 nV, L51b) erano già superate da L56 (2026-10-12) e il dossier
  non è stato rigenerato: lo rigenera L64.

## Rifare

```sh
/usr/bin/python3 -I models/comparator/genera_tlv1701.py vendor/comparator/ti/TLV1702/tlv1701.lib models/comparator/tlv1701_ngspice.lib
/usr/bin/python3 scripts/validate_models.py
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_finale.txt 5
/bin/zsh <L>/psu/corri_an.sh corto_u503 fin_sorgente sorgente --n2n7002 ds --tss 3.0
/usr/bin/python3 -I <L>/psu/analizza_an.py --te=3.0 <L>/an_fin_seq.csv $(/usr/bin/python3 -I <L>/dirs_noto.py <L> fin_ seq)
/usr/bin/python3 -I <L>/confronta_noto.py <L>/an_fin_seq.csv <L>/an_fint_seq.csv
/usr/bin/python3 -I <L>/confronta_timer.py docs/preamp/data/2026-10-25/L54a/psu/genera_tb_psu.py circuits/preamp/psu.net
/usr/bin/python3 -I <L>/ponte/estrai_ponte.py --passata-unica --te 3.0 <L>/seq/fin_sorgente <L>/ponte/nom spegnimento_l perdita perdita_min guasto guasto_u501 guasto_u503 guasto_u503_min cf_nodelta corto_u503
/bin/zsh <L>/script/catena_audio.sh nom
/usr/bin/python3 -I <L>/psu/potenza_t2.py <L>/seq/fin_consumo_sorgente/accensione/*_g1_out.txt 2.5 3.0
```

Il sorgente: `nomi_reti.txt` (prima `psu_prima.net`, dopo, R585: 0 reti coi piedini o il nome
cambiati); `confronta_timer.txt` 48 / 48 (la netlist di prima fallisce: manca R585).
