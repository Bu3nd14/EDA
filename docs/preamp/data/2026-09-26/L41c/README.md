# L41c — il banco di L30 col circuito vero (2026-09-26)

Dati del lotto L41c (NC-036). Report:
`docs/preamp/reports/2026-09-26-L41c-banco-l30-circuito-vero.md`. Sorgenti **non toccati**:
`circuits/preamp/psu.py`, `circuits/preamp/preamp_audio.py`, `firmware/preamp_timer/`.

Le forme d'onda (`seq/**/*_out.txt`, 15–45 MB l'una; `corse/*.dat`) sono in `.gitignore`: si
rifanno coi comandi sotto. Si versionano i deck, i log, le uscite del core di ogni giro, i JSON
del ponte, i manifesti e le analisi.

## La catena, in due tempi

Una scheda sola non sta in un deck. La catena va in due tempi, e in un senso solo:

1. **L'alimentatore** (`psu/`, copiato da `L41b2/deck/` ed esteso coi casi di L41c): il circuito
   di `psu.net` col firmware del temporizzatore come micro, iterato fino al punto fisso
   (`corri_seq.sh`), come in L41b2. La scheda audio qui è un carico: 56,6 Ω per rail, le bobine
   come resistenze, i LED delle LDR come diodi.
2. **Il ponte** (`ponte/estrai_ponte.py`): dal giro al punto fisso di ogni caso scrive un JSON con
   i due rail, le correnti delle due stringhe LED (i 10 Ω di sense), e gli istanti dei contatti
   all'angolo peggiore del G6K: il jack il più tardi possibile (bobina sotto 1,2 V, più 3 ms), il
   guadagno il più presto possibile (bobina sotto 9,6 V, più 0 ms).
3. **La scheda audio** (`deck/tb_v2_l41c.cir`): il banco di L30 generato da
   `genera_tb_v2_casopeggiore.py --matrice l41c --ponte ponte/`, sul sorgente (geometria iii,
   bleed dalla netlist, gemello di K1/K5), senza segnale, +10 dB, 100 kΩ, 0 pF di cavo. Rail,
   correnti LED e contatti vengono dal ponte. Ogni caso ha il **suo riferimento**: gli stessi
   punti fino a `t_ins`, poi fermi, e i contatti fermi.

Niente torna indietro: l'alimentatore non vede la corrente vera dei blocchi audio mentre il rail
scende.

## I casi

| Caso | Evento (a TE = 2 s) | In L30 |
|---|---|---|
| `spegnimento_l` | il frontale aperto in MUSICA; fino a TE + 7,6 s | N, spegnimento morbido |
| `perdita`, `perdita_min` | la rete assente per sempre (`_min`: i componenti di Δ all'angolo minimo) | F/s, entrambi i rail |
| `guasto_u501` | U501 (rail +) spento, rete presente | F/p |
| `guasto` | U502 (rail −) spento, rete presente (il caso di L41b2, rifatto) | F/m |
| `guasto_u503`, `guasto_u503_min` | U503 (`VRELAY_REG`) spento, rete presente | G, `VRELAY` persa |
| `cf_nodelta` | come `perdita`, con C528 = 10 pF: Δ a zero | il controfattuale senza Δ |
| `corto_u503` | l'uscita di U503 a massa (0,1 Ω) | la domanda all'utente |

## Come si rifà

Dalla radice del repo:

```sh
/bin/zsh docs/preamp/data/2026-09-26/L41c/psu/tutti_seq.sh                  # i nove casi, ~5 min
/usr/bin/python3 docs/preamp/data/2026-09-26/L41c/ponte/estrai_ponte.py \
    <abs>/seq <abs>/ponte spegnimento_l perdita perdita_min guasto guasto_u501 \
    guasto_u503 guasto_u503_min cf_nodelta corto_u503
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py \
    --matrice l41c --ponte <abs>/ponte --uscita <abs>/deck/tb_v2_l41c.cir
/usr/bin/python3 docs/preamp/data/2026-09-26/L41c/deck/controlla_deck.py <abs>/deck/tb_v2_l41c.cir
/bin/zsh docs/preamp/data/2026-09-23/L29c/script/corri.sh <abs>/corse <abs>/deck/tb_v2_l41c.cir '_l41c$' 9
grep -l -i 'too many args\|no such device\|timestep too small\|aborted' <abs>/corse/*.log   # vuoto
/usr/bin/python3 docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py <abs>/corse
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/script/analizza_par.py <abs>/corse/manifest_ok.csv <abs>/corse <abs>/corse/analisi.csv 8
/usr/bin/python3 docs/preamp/data/2026-09-26/L41c/script/tabella.py <abs>/corse/analisi.csv <abs>/corse/fallite.txt <abs>/tabella.csv
```

## Due guardie nuove

- **`alter: too many args.`** Un `alter @v[pwl] = [ … ]` con 1000 numeri o più viene ignorato:
  ngspice stampa solo quella riga ed esce 0, e la sorgente resta com'era (400 punti passano, 500
  no). Il ponte riduce ogni PWL a ≤ 350 punti, e `controlla_deck.py` rifiuta un deck con un
  `alter` oltre 800 numeri. Limitations **#36**.
- **Lo spegnimento lungo finisce a TE + 7,6 s.** Il primo giro fino a TE + 7,8 s si è fermato a
  TE + 7,641 s su «Timestep too small» in `xu511a.bout`, lo stesso nodo che aveva fermato L41b2.
  In quell'istante i rail erano a +0,73 / −0,70 V e le stringhe a 5 nA: dopo tutto quello che V2
  legge. Il ponte tiene i rail fermi a +0,83 / −0,81 V da TE + 7,6 s in poi.

## I file

| File | Cosa |
|---|---|
| `psu/` | il generatore, `corri_seq.sh`, `tutti_seq.sh`, `analizza_seq.py` (i criteri r, s nuovi, scritti prima) |
| `seq/<caso>/` | deck, log, `core_g<n>.csv`, `ponte_g<n>.txt` di ogni giro; `seq/analisi_seq.txt` |
| `ponte/` | `estrai_ponte.py`, un JSON per caso, `estrai.txt` |
| `deck/` | `tb_v2_l41c.cir` generato, `controlla_deck.py` |
| `corse/` | manifesti, log, `tempi.txt`, `analisi.csv` |
| `script/tabella.py`, `tabella.csv` | i criteri di L41c, scritti prima delle corse, e il verdetto |

## Le cifre

In `tabella.csv` e `seq/analisi_seq.txt`, e nel report:
- **Il lato alimentatore**: 9 casi su 9 al punto fisso, criteri r e s compresi. Nel controfattuale
  C3 e r falliscono, come devono.
- **La scheda audio**:
  - spegnimento morbido: 30 nV;
  - perdita di rete: 0,12 / 0,18 µV;
  - U501 / U502 spento: 1,03 / 1,37 mV;
  - U503 spento: 75 nV;
  - controfattuale senza Δ: ≥ 66,5 mV, fino all'aborto (`cf_nodelta_fino_all_aborto.txt`);
  - corto della linea a 12 V dei relè: 69,4 mV (~90 dB SPL di picco a 1 m), accettato
    dall'utente sotto il tetto (**ADR-051**).
