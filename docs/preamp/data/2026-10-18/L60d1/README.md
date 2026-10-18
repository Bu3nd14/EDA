# L60d1 — la ridondanza nel blocco, e la causa della musica a mute inserito (2026-10-18)

Report `../../../reports/2026-10-18-L60d1-ridondanza-e-inseguitore.md`. Decisioni ADR-086 (la
ridondanza, costruita qui) e ADR-087 (l'inseguitore limitato, V2 con la media). `<L>` = questa
cartella, `<R>` = la radice del repo.

## I file

| Percorso | Che cosa |
|---|---|
| `base/gain_block_L46b.subckt` | il sottocircuito di prima di L56 (5dc5c8b1), per la diagnosi |
| `script/prepara_diagnosi.py`, `corri_diagnosi.sh` | il riferimento «sempre in mute» di V2 (`g10sempre_1k_iii`) a 2 s, col blocco di oggi e con quello di L46b, in `run/diagnosi/` |
| `script/forma_jack.py`, `picchi_jack.py` | media, 1 kHz e RMS del jack e dei nodi; gli impulsi (numero, fase, durata, forma attorno al massimo) |
| `script/sonda_blocco.py`, `corri_sonda.sh`, `analizza_sonda.py` | la stessa corsa a 0,3 s coi nodi interni e le correnti del blocco B: chi fa il fronte |
| `script/b1_confronto.py` | B1 e B2g col metodo di V2 e con la media su ogni campione (limitations #60) |
| `script/p7_l56.py`, `corri_p7_l56.sh`, `sintesi_p7_l56.py` | P7 (`tb_mute_corto`) con le misure di Q146, Q148 e (`r153`) di R153 |
| `script/varianti_follower.py`, `corri_follower.sh`, `riassumi_follower.py`, `follower/` | i rimedi all'inseguitore (base, 4,7 / 10 kΩ sul collettore, 1 / 2,2 kΩ in base al VAS): P7, sonda, V1, V3; `follower/riassunto.csv` |
| `script/prepara_shunt.py`, `corri_shunt.sh`, `riassumi_shunt.py`, `shunt/` | il valore in parallelo a R109, a blocco sano e col guasto (iniezione dal lato di FB, limitations #61); `shunt/margini_shunt.csv` |
| `script/regressione.sh`, `confronta_regressione.py`, `regressione/` | i 21 deck veloci (copia di L56, `${#jobstates}`): `prima` = `main`, `dopo` = il blocco finale; `regressione/script/` gli analizzatori di L56, `cifre.csv`, `margini.csv` |
| `script/prova_e4.py`, `e4_nodeset.py`, `corri_e4_nodeset.sh` | la cella di E4 col canale spento (limitations #59): punto di lavoro da zero, accensione, `.nodeset` |
| `script/caldo.py`, `genera.py`, `esegui.sh`, `leggi_four.py`, `sintesi_caldo.py`, `inc/`, `deck/`, `tj/`, `sintesi_caldo.csv` | V4 a caldo di L56 (copiati): `adr067` il blocco di L56, `l60d1` il blocco finale, entrambi `--sot223` |

Le corse (`run/`, ~3 GB), le varianti corse e le forme d'onda grandi della regressione non stanno
nel repository (`.gitignore`): si rifanno.

## Rifare

```sh
/usr/bin/python3 -I <L>/script/prepara_diagnosi.py ; /bin/zsh <L>/script/corri_diagnosi.sh   # ~7 min
/usr/bin/python3 -I <L>/script/forma_jack.py <L>/run/diagnosi/oggi        # e l46b
/usr/bin/python3 -I <L>/script/picchi_jack.py <L>/run/diagnosi/oggi
/usr/bin/python3 -I <L>/script/b1_confronto.py <L>/run/diagnosi/oggi/g10sempre_1k_iii.dat
/usr/bin/python3 -I <L>/script/sonda_blocco.py oggi 300m ; /bin/zsh <L>/script/corri_sonda.sh oggi ; /usr/bin/python3 -I <L>/script/analizza_sonda.py oggi 0.28
/bin/zsh <L>/script/regressione.sh prima        # sul blocco di main, PRIMA di rigenerare il sorgente
/Users/roberto/EDA/env/venv/bin/python3 <R>/circuits/preamp/gain_block.py
/bin/zsh <L>/script/regressione.sh dopo
/usr/bin/python3 <L>/regressione/script/margini.py           # e cifre.py, p7.py, classe_a.py; v3_con_continua.py col venv
/bin/zsh <L>/script/corri_e4_nodeset.sh dopo
/bin/zsh <L>/script/corri_p7_l56.sh dopo r153 ; /usr/bin/python3 -I <L>/script/sintesi_p7_l56.py dopo
/usr/bin/python3 -I <L>/script/prepara_shunt.py ; /bin/zsh <L>/script/corri_shunt.sh ; /usr/bin/python3 -I <L>/script/riassumi_shunt.py
/usr/bin/python3 -I <L>/script/varianti_follower.py ; /bin/zsh <L>/script/corri_follower.sh ; /Users/roberto/EDA/env/venv/bin/python3 <L>/script/riassumi_follower.py
/usr/bin/python3 <L>/script/caldo.py op adr067--sot223 l60d1--sot223 ; /bin/zsh <L>/script/esegui.sh <L>/deck/lista_op.txt   # poi p2, p3, p4, deck4 allo stesso modo
/usr/bin/python3 <L>/script/leggi_four.py adr067--sot223 l60d1--sot223 ; /usr/bin/python3 <L>/script/sintesi_caldo.py adr067--sot223 l60d1--sot223
```

`prepara_shunt.py` e `varianti_follower.py` partono dal sottocircuito generato: rieseguiti sul blocco
finale (R150 a 4,7 kΩ, R153 già presente) le varianti cambiano significato; le cifre del report sono
quelle corse sul blocco del momento (R150 a 10 kΩ per la scansione, senza R153 per i rimedi).
