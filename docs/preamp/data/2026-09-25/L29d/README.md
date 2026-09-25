# L29d — la sonda del contatto in serie al jack (2026-09-25)

Dati del lotto L29d (NC-028). Report: `docs/preamp/reports/2026-09-25-L29d-sonda-contatto-serie.md`.
Le forme d'onda (`*.dat`) **non si committano**: si rifanno correndo. Si tengono manifesti,
analisi, verdetti, tempi e log.

**È una sonda, non la matrice.** Decisione dell'utente del 2026-09-25: si corrono le celle peggiori
di L29c su tutte le geometrie, e ci si ferma. La matrice completa sulle geometrie scelte è L29d2.

## Il banco

`deck/tb_v2_sonda_serie.cir`, **generato** dal generatore di L29c esteso:

```sh
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py \
    --matrice sonda_l29d --uscita docs/preamp/data/2026-09-25/L29d/deck/tb_v2_sonda_serie.cir
```

L'intestazione del generatore (sezione «SONDA L29D») descrive le cinque geometrie (N, iA, iB, ii,
iii) e le ipotesi. Il blocco CANALE è identico (`v2_metodo.py canale`). Rigenerati col generatore
esteso, il deck versionato, il controfattuale, `caldo` e le curve di L29c risultano **byte-identici**.

## Come si è corso

Con gli script di L29c, per percorso:

```sh
/bin/zsh docs/preamp/data/2026-09-23/L29c/script/corri.sh <abs>/sonda <abs>/deck/tb_v2_sonda_serie.cir '.' 8
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/script/verifica_partenza.py sonda
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/script/analizza_par.py sonda/manifest.csv sonda sonda/analisi.csv 4
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/script/verdetto.py sonda/manifest.csv sonda/analisi.csv sonda/verdetto.csv
```

`script/controfattuale_N.py` confronta la geometria N con le stesse celle di L29c.

## Le cartelle

| Cartella | Cosa |
|---|---|
| `deck/` | il deck generato della sonda |
| `sonda/` | le 32 corse: manifesto, `tempi.txt`, analisi, verdetto |
| `script/` | gli script propri di L29d |
