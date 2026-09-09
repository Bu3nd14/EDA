# Dati del dossier — versionati di proposito

Deciso il 2026-09-09, insieme allo spostamento del gate dai diff ai dati.

## Perché questa directory esiste

`design-reviewer` esegue i gate **offline, dopo il merge, su `main`**, e
deve poter **aprire i numeri**. `results/` non serve a questo: è scratch
e gitignorato, quindi su un checkout fresco è vuoto. Senza un posto
versionato, un gate su `main` non troverebbe nulla da giudicare e il
dossier non avrebbe grafici da impaginare.

## La convenzione

```
docs/preamp/data/<YYYY-MM-DD>/<nome>.csv
docs/preamp/data/<YYYY-MM-DD>/<nome>.json
docs/preamp/data/<YYYY-MM-DD>/<nome>.log     (l'evidenza, non solo il dato)
```

**La data è parte del percorso**, come per `reports/`: una misura è vera
di **una versione specifica del circuito**, e senza data è inutile.

**Curati, non grezzi.** Qui va ciò che il dossier impagina e ciò che una
non conformità cita — non l'output di ogni esecuzione. I run completi
restano in `results/`, che è scratch e va bene così: un deck si rilancia
in qualsiasi momento con

```sh
/bin/zsh scripts/run_simulation.sh spice/preamp/tb/<deck>.cir results/preamp/<nome>
```

La riproducibilità è garantita dai **deck**, che sono versionati; questi
file sono l'istantanea che rende il dossier guardabile e la non
conformità verificabile senza rieseguire nulla.

## Attenzione al `.gitignore`

`.gitignore` ha regole **globali** `*.log`, `*_out.txt` e `*.raw`. Senza
la negazione `!docs/preamp/data/**` in fondo al file, un log di ngspice
depositato qui come evidenza **sparirebbe in silenzio** — il tipo di
fallimento che questo repo documenta invece di subire. Se aggiungi
estensioni nuove, controlla che sopravvivano a `git status`.
