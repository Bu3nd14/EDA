# L39 — i modelli del costruttore nel progetto (2026-09-22)

Report: `docs/preamp/reports/2026-09-22-L39-modelli-costruttore.md`.

| Percorso | Cosa |
|---|---|
| `prima/` | i 21 deck veloci e una cella di V2 sul `main` di L29b2, **sui segnaposto**, eseguiti in questa sessione prima di toccare il sorgente |
| `prima/gain_block_flat_L29b2.inc`, `prima/gain_block_L29b2.subckt` | il blocco generato di prima: il confronto con quello di oggi cambia solo i nomi dei modelli |
| `prima/tb_v2_mute_ldr_L29b2.cir` | il deck V2 di L29b2, con l'include del blocco puntato alla copia qui sopra (le due corse di pavimento `evp`/`invp` sono state corse dopo la rigenerazione del blocco) |
| `dopo/` | gli stessi deck e la stessa cella **sui modelli del costruttore** |
| `*/esiti.tsv` | rc e durata di ogni deck; `*/v2_1k_100k/tempi.txt` lo stesso per le corse V2 |
| `confronto_grezzo.csv` | ogni cifra `nome = valore` dei log e ogni cella delle tabelle echo, prima e dopo (`script/confronta.py`) |
| `margini.csv` | V1: il minimo per istanza e modo, prima e dopo (`script/margini.py`) |
| `esplorazione/` | C_f e Miller spazzati sul blocco B coi modelli veri, **nessun valore del sorgente cambiato** (`script/esplora_compensazione.py`, `script/riassumi_comp.py`) |
| `sabotaggi/` | il 2i nuovo fatto cadere: 8 casi su 8 come attesi (`script/sabotaggi_2i.sh`) |
| `bozza_prompt_L29c.md` | il mandato di L29c aggiornato ai modelli del costruttore; L29c viene dopo L40 |

Gli script in `script/`: `esegui_deck.sh <fase> -f deck_veloci.txt` corre i deck;
`v2_cella.sh <fase> [deck]` corre la cella V2 (1 kHz, 100 k); `porta_deck.py` ha fatto le
sostituzioni meccaniche nei deck; `forme_commento.py` elenca cosa dicono le intestazioni;
`p7.py`, `classe_a.py`, `v3.py` riassumono P7, la classe A e V3.

**Tolto prima del commit** (`script/cura.py`): le forme d'onda rigenerabili, cioè i `.txt`
di `wrdata` con le loro conversioni `.csv`/`.json`, i `.dat` delle corse V2 (~400 MB
l'una) e i deck divisi `corsa_*.cir`. In tutto 9,3 GB. Resta la forma d'onda di
`tb_v3_overload`, che `v3.py` rilegge. Tutti i riassunti sono stati rieseguiti dopo la
pulizia, e danno le stesse cifre.
