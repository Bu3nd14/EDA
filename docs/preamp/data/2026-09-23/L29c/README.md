# L29c — il caso peggiore di V2 col mute reale (2026-09-23)

Dati del lotto L29c (NC-028). Report: `docs/preamp/reports/2026-09-23-L29c-v2-caso-peggiore.md`.
Le forme d'onda (`*.dat`, ~400 MB l'una) **non si committano**: si rifanno correndo. Si tengono
manifesti, analisi, verdetti, tempi e log.

## Il banco

`deck/genera_tb_v2_casopeggiore.py` genera:
- `spice/preamp/tb/tb_v2_casopeggiore.cir`, il deck **versionato** (matrice `l29c`, 246 corse);
- `controfattuale/cf.cir` (matrice `controfattuale`): la cella di L40 con le aggiunte neutre;
- `curve/tb_v2_curve_{AA,AD,DA,DD}.cir` (matrice `curve`): il punto 6;
- `caldo/tb_v2_caldo.cir` (matrice `caldo`): il cambio di guadagno a caldo, criterio 3 di ADR-030.

L'intestazione del generatore dice cosa c'è dentro e le ipotesi di accensione e spegnimento.

## Gli script (`script/`)

| Script | Cosa fa |
|---|---|
| `v2_cella.sh <fase>` | la cella di L40 (1 kHz, 100 k) dal deck di `main`, come in L40 |
| `corri.sh DIR DECK REGEX NPAR` | divide il deck, seleziona le corse per il nome del file, le corre a NPAR per volta; rc=OPT se il log ha il «Transient op» (limitations #33) |
| `seleziona.py` | filtra il manifesto per la colonna file e rifiuta una selezione senza i suoi riferimenti |
| `controlla_op.py DIR` | per ogni corsa, da dove parte la `tran` (1 ms): OUTA all'offset, jack a 0, niente transient op |
| `analizza_par.py` | `v2_metodo.py analizza` in parallelo, su gruppi autosufficienti del manifesto |
| `verdetto.py` | A, B2, S di verdetto per riga (colonna `conta`), il peggiore sulle tre uscite, contro le soglie |
| `confronta_analisi.py` | due `analisi.csv` cella per cella |
| `scarta.py` | toglie da una directory le corse da rifare |
| `coda.sh` | dispersione e curve dopo le veloci |

## Le cartelle

| Cartella | Cosa |
|---|---|
| `riferimento/` | la cella di L40 rifatta: **identica** a L40 (132 grandezze, scarto 0) |
| `controfattuale/` | il banco nuovo in posizione neutra contro `riferimento/`: A, B2, C entro 0,09 %, S identico |
| `sonde/` | la PWL su una sorgente DC (`rampa_alter*.cir`); `op/`: la convergenza (limitations #33), le varianti di solutore |
| `matrice/k20/` | le tre corse a 20 kHz |
| `matrice/veloci/` | punti 1, 2, 4, 5 |
| `matrice/disp/` | punto 3 |
| `curve/` | punto 6 |
| `caldo/` | il cambio a caldo, contatto morbido; `analisi_netto.csv`: le tre corse a caldo riuscite con l'interruttore netto, entro 0,4 % |
