# L64a — il dossier rigenerato, la scheda audio: i dati

La prima delle tre parti di L64 (l'utente, 2026-11-02: «Three parts, like last time»: L64a la scheda
audio, L64b l'alimentatore e il temporizzatore, L64c gli schemi, la FMEA, le schede di prova, «Cosa
non dice», la consegna). Il circuito è quello di `main` dopo L67 (4d7be348c): **non cambia** in
questo lotto. Sotto, `<L>` è questa cartella e `<R>` la radice del repo.

## Che cosa c'è

| Percorso | Che cosa |
|---|---|
| `script/stati.py` | Le righe `Stato:` scelte dall'utente («Yes, use these sentences»): 15 file di ADR e l'indice; ADR-087, 088, 089 aggiunte all'indice |
| `script/genera_bilanciamento.py`, `bilanciamento/` | Le due copie col bilanciamento di L48b rigenerate dai deck canonici di **oggi** (quelle di L48b non hanno il limitatore d'ingresso) |
| `script/ricorsa.sh`, `dopo/` | I 21 deck veloci, il selettore e le due copie, corsi il 2026-11-02: 24 su 24 con rc 0 |
| `script/confronta.py`, `script/confronta_mute.py`, `confronto.txt`, `misure_confronto.csv` | La seconda strada: le **10 503 misure** dei 20 deck uguali alla sesta cifra a quelle della regressione di L66 sulla variante lim365 (il sorgente di oggi); il deck del mute di L66 ricorso (`l66_mute/`) ridà le sue **32 200 misure** e i CSV di oggi |
| `script/genera_seconda.py`, `script/seconda.sh`, `seconda/`, `l66_mute/` | Selettore e copie col blocco preso dai file della variante di L66: byte per byte uguali |
| `script/v2_da_l60d2.py`, `v2_da_l60d2.csv` | Il criterio di L62b dal blocco di L60d2 a oggi: il banco di V2 cambia al più di 6,0e-4 |
| `scatti/` | Gli scatti di L48b (`genera_scatti.py` col limitatore d'ingresso di ADR-101) sul circuito di oggi, varianti 0 e 4; la continua propria del blocco A **−2,888 mV** (L48b −6,623) |
| `falsi_l48a/`, `falsi_l48b/` | Gli script dei falsi del 2e ricorsi sulla netlist di oggi: 10 su 10; 7 su 7 (il caso «main» di L48b esce: la netlist di prima di L48b non ha il limitatore) |
| `distorsione/` | Il banco di L46b sul blocco di oggi (come L51c), 2 deck alla volta |
| `script/nodeset_v2.py`, `prova_nodeset_v2.sh`, `scarto_nodeset_v2.py`, `analisi_nodeset_v2.py`, `prova_nodeset/` | I `.nodeset` del blocco da solo per le 22 celle della dispersione che sul blocco di oggi non trovano il punto di lavoro (limitations #86); la prova su tre celle che convergono anche senza: le grandezze di V2 si spostano al più di 0,64 µV |
| `script/resto_v2.py`, `corri_resto_v2.sh`, `finalizza_v2.sh`, `v2/` | La matrice di V2 intera sul circuito di oggi (155 corse, 3 alla volta a priorità bassa), la guardia, l'analisi, il verdetto, il clic, la sonda di VOSB = 0 |
| `mute/tb_v2_casopeggiore_generato.cir` | Il deck V2 rigenerato oggi dal sorgente: uguale byte per byte a quello versionato |
| `script/sabotaggi.py`, `sabotaggi.txt` | Ogni controllo nuovo di `build_dossier.py` fatto fallire |

Le onde (`run/`, i `.dat`), i `.txt` e `.json` grezzi di `run_simulation.sh` e le cache di Python
non stanno nel repository (`.gitignore`).

## Come si rifà

```sh
/usr/bin/python3 -I <L>/script/genera_bilanciamento.py
/bin/zsh <L>/script/ricorsa.sh dopo
/bin/zsh <L>/script/seconda.sh
/usr/bin/python3 -I <L>/script/confronta.py ; /usr/bin/python3 -I <L>/script/confronta_mute.py
/usr/bin/python3 -I <L>/script/v2_da_l60d2.py
cd <L>/scatti && /usr/bin/python3 -I genera_scatti.py --va0=0 --op && /opt/homebrew/bin/ngspice -b deck/tb_l48b_op.cir -o deck/tb_l48b_op.log
/usr/bin/python3 -I <L>/scatti/genera_scatti.py --va0=-2.88797e-3   # poi solo v0 e v4
/bin/zsh <L>/scatti/corri.sh <L>/scatti/deck ; /usr/bin/python3 -I <L>/scatti/analizza.py
/usr/bin/python3 <L>/falsi_l48a/falsi.py ; /usr/bin/python3 <L>/falsi_l48b/falsi.py
/bin/zsh <L>/distorsione/script/tutto.sh
/bin/zsh <R>/docs/preamp/data/2026-09-23/L29c/script/corri.sh <L>/run/v2 <R>/spice/preamp/tb/tb_v2_casopeggiore.cir '.*' 3
/bin/zsh <L>/script/corri_resto_v2.sh 3      # le celle rimaste e le 22 coi nodeset del blocco
/bin/zsh <L>/script/finalizza_v2.sh
/usr/bin/python3 <R>/docs/preamp/dossier/build_dossier.py --standalone <fuori dal repo>/dossier.html
/usr/bin/python3 <L>/script/sabotaggi.py
```

La matrice di V2 è lunga: le celle a 20 kHz chiedono da due a tre ore l'una.
