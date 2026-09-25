# L29d2 — la matrice del contatto in serie sulla geometria iii (2026-09-25)

Dati del lotto L29d2 (NC-028). Report: `docs/preamp/reports/2026-09-25-L29d2-matrice-contatto-serie.md`.
Le forme d'onda (`*.dat`) **non si committano**: si rifanno correndo. Si tengono manifesti,
analisi, verdetti, tempi e log.

## Le decisioni dell'utente (2026-09-25), prima di correre

| Domanda | Risposta, con le sue parole |
|---|---|
| Quale geometria | «iii»: serie più derivazione dal lato del condensatore |
| Lo stato sicuro | «Il bleed basta» |
| I valori | «C dal datasheet + cavo realistico» |

- **C del contatto aperto**: 0,075–0,080 pF, dalla curva d'isolamento del G6K
  (`script/c_contatto.py`, `script/c_contatto.txt`). Nel banco va **0,1 pF**, arrotondata per eccesso.
- **Cavo al jack**: 0 pF, il caso peggiore; 100 pF nella variante `c100`.
- **Bleed lato condensatore** (220 k / 470 k) e **trasferimento** (1 ms): invariati.

## Il banco

`deck/tb_v2_l29d2.cir`, **generato** dal generatore di L29c, esteso con `--matrice l29d2`:

```sh
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py \
    --matrice l29d2 --uscita docs/preamp/data/2026-09-25/L29d2/deck/tb_v2_l29d2.cir
```

Il deck ha 548 corse: 4 varianti per 135 corse, più le 8 del controfattuale N. Le varianti sono
`""` (0 pF e 100 k), `c100`, `r10k` e `k5` (il contatto a 5 pF, il ponte con la sonda L29d).
Si corre soltanto ciò che il regex seleziona.

`script/identici.sh <tmp>` rigenera col generatore esteso gli 8 deck versionati di L29c e L29d, e li
confronta con `cmp`: sono **byte-identici**.

## Come si è corso

Con gli script di L29c, per percorso assoluto:

```sh
corri.sh <abs>/cf      <abs>/deck/tb_v2_l29d2.cir '_N$' 8
corri.sh <abs>/matrice <abs>/deck/tb_v2_l29d2.cir '^(?!off_).*(?<!_c100)(?<!_r10k)(?<!_k5)_iii$' 8
analizza_par.py <dir>/manifest_sel.csv <dir> <dir>/analisi.csv 8
verdetto.py     <dir>/manifest_sel.csv <dir>/analisi.csv <dir>/verdetto.csv
```

Script propri:
- `script/tabella.py`: la tabella di iii contro L29c;
- il controfattuale riusa `L29d/script/controfattuale_N.py`.

## Le cartelle

| Cartella | Cosa |
|---|---|
| `deck/` | il deck generato |
| `cf/` | il controfattuale N: 8 corse, `controfattuale_N.csv` |
| `matrice/` | la matrice di L29c su iii: 111 corse |
| `script/` | gli script propri di L29d2 |
