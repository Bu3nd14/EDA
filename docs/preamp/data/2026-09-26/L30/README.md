# L30 — spegnimento, failsafe dell'alimentatore, calore del telaio (2026-09-26)

Dati del lotto L30 (NC-028 per lo spegnimento, NC-029). Report:
`docs/preamp/reports/2026-09-26-L30-spegnimento-failsafe-calore.md`. Decisioni: **ADR-046**,
**ADR-047**. Le forme d'onda (`*.dat`) **non si committano**: si rifanno correndo.

## Le decisioni dell'utente (2026-09-26), prima di correre

| Domanda | Risposta, con le sue parole |
|---|---|
| La soglia in caso di guasto | «in caso di guasto una soglia di non-danno basta» |
| Il tetto, e la forma del failsafe | «le soglie vanno bene come tetto, non come target, dobbiamo stare più bassi, il resto OK» |
| Lo spegnimento normale | «sì, interruttore morbido va bene» |

## Il banco

`deck/tb_v2_l30.cir`, **generato** dal generatore di L29c, esteso con `--matrice l30`:

```sh
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py \
    --matrice l30 --uscita docs/preamp/data/2026-09-26/L30/deck/tb_v2_l30.cir
```

- **Sul sorgente**: la geometria iii e i bleed si leggono da `circuits/preamp/preamp_audio.net`,
  col controllo del 2e, come `--matrice sorgente`.
- **Il guadagno**: K1/K5 hanno il **gemello comportamentale** (fronte di 4,55 µs) al posto
  dell'interruttore netto, come `--matrice caldo`. Con l'interruttore netto, 5 corse su 6 che
  commutano il guadagno col blocco fuori regolazione si fermavano su «Timestep too small».
- **Il deck versionato** `spice/preamp/tb/tb_v2_casopeggiore.cir` si rigenera col generatore
  esteso **byte-identico** (`cmp`).

29 corse, senza segnale, +10 dB, 100 kΩ, 0 pF di cavo:

| Corse | Cosa |
|---|---|
| `g10mai_lz_l30`, `g10sempre_lz_l30` | i riferimenti |
| `n_r{10,300}{s,p,m}_{gi,gm}_l30` | **spegnimento morbido**: jack isolati da prima; rampe dei rail di L29c; guadagno a 0 dB all'inizio (gi) o a metà della discesa (gm) |
| `f_c{470,1000,2200}{s,p,m}_l30` | **guasto**: un rail (p, m) o entrambi (s) con la pendenza di 265 mA / C; il relè al jack si apre 3 ms dopo lo scatto a 13,5 V; il guadagno resta a +10 dB |
| `g_c{470,1000,2200}s_l30` | come f, con `VRELAY` persa: il guadagno a 0 dB Δmin = 10 ms dopo |
| `cf_nodelta_l30` | controfattuale senza Δ: il guadagno a 0 dB col comando |
| `cf_tardi_l30`, `cf_corto_p_l30` | controfattuali: relè solo a 10 V; corto del rail + in 100 µs. **Non corsi**: «Timestep too small» nel JFET, come le 7 corse di L29d2 |

## Come si è corso

```sh
/bin/zsh docs/preamp/data/2026-09-23/L29c/script/corri.sh <abs>/corse <abs>/deck/tb_v2_l30.cir '_l30$' 8
/usr/bin/python3 docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py <abs>/corse
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/script/analizza_par.py <abs>/corse/manifest_ok.csv <abs>/corse <abs>/corse/analisi.csv 8
/usr/bin/python3 docs/preamp/data/2026-09-26/L30/script/tabella.py <abs>/corse/analisi.csv <abs>/corse/fallite.txt <abs>/tabella.csv
/usr/bin/python3 docs/preamp/data/2026-09-26/L30/script/soglia_regolazione.py <abs>/corse f_c2200s_l30 f_c2200p_l30 f_c2200m_l30 f_c1000s_l30 f_c470s_l30
/usr/bin/python3 docs/preamp/data/2026-09-26/L30/termica/stima_telaio.py
```

**La guardia che manca a `corri.sh`**: una `alter` su un dispositivo che non esiste dà
«no such device» e ngspice esce 0. Il primo giro di L30 è girato **senza i contatti del jack**:
il generatore li aggiungeva solo per `l29d2` e `sorgente`. Prima di fidarsi di un giro:
`grep -l 'no such device' corse/*.log` deve essere vuoto. Per questo giro lo è.

## I file

| File | Cosa |
|---|---|
| `tabella.csv` | picco peggiore per corsa, dB SPL di picco a 1 m, soglia della classe, esito |
| `soglia_regolazione.csv` | il rail a cui MAIN_A si scosta di 1 / 10 / 100 mV |
| `termica/stima_telaio.py`, `.txt` | la stima termica (CALCOLATA) |
| `corse/` | manifesti, `analisi.csv`, log, `tempi.txt`, `fallite.txt` |
| `script/` | `tabella.py`, `soglia_regolazione.py` |
