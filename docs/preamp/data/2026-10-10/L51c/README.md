# L51c — il dossier rigenerato: le schede di prova e la chiusura (2026-10-10)

Report: `../../../reports/2026-10-10-L51c-dossier-schede.md`. La terza delle tre parti di L51
(«Tre parti»). Il generatore è `docs/preamp/dossier/build_dossier.py`. Con `PARTI` completa
scrive accanto a sé `index.html`, le figure, gli schemi, le cinque immagini delle schede e
`dossier.summary.json`.

```sh
/usr/bin/python3 docs/preamp/dossier/build_dossier.py                         # la pagina nel repo
/usr/bin/python3 docs/preamp/dossier/build_dossier.py --standalone <fuori dal repo>.html
/usr/bin/python3 docs/preamp/dossier/stampa_a4.py <fuori dal repo>.pdf
/usr/bin/python3 docs/preamp/data/2026-10-10/L51c/script/sabotaggi.py         # 71 su 71
```

| Percorso | Cosa |
|---|---|
| `script/stati.py` | le quindici righe `Stato:` scelte dall'utente, scritte uguali nel file della decisione e nell'indice. Dieci erano nella lista di `NEXT-SESSION.md` (009, 027, 032, 038, 039, 040, 049, 050, 061, 062). Cinque le ho trovate rigenerando: accettate che rimandavano al mute graduale (012, 021, 030, 035, 036). Le frasi riscritte su richiesta dell'utente sono annotate nello script |
| `distorsione/script/` | `genera.py`, `esegui.sh`, `leggi_four.py` copiati da `../../2026-10-01/L46b/script/`; cambia solo la profondità della radice (un livello più giù). `oggi.py` scrive `inc/oggi.inc` |
| `distorsione/inc/oggi.inc` | `spice/preamp/gain_block_flat.inc` del 2026-10-10, nessuna modifica, una riga d'origine in testa. Il blocco è stato rigenerato da `circuits/preamp/gain_block.py` ed è uguale byte per byte a quello versionato (`gain_block.py` da L46b ha cambiato solo commenti) |
| `distorsione/deck/oggi/` | `thd_1k`, `thd_10k`, `thd_20k`, `imd`: i deck di L46b a meno del titolo e del blocco incluso |
| `distorsione/run/` | le corse (`esiti.tsv`, rc 0 su 4) e `oggi/distorsione.csv` (24 casi) |
| `drc/` | la DRC rifatta oggi con `scripts/run_drc.sh` sulle due schede copiate nei dati di L49a e L49b (kicad-cli 10.0.6): 0 violazioni, 0 aperte, come il 9 ottobre |
| `script/sabotaggi.py`, `sabotaggi.txt` | i 15 sabotaggi nuovi, più i 26 di L51a e i 29 di L51b importati dai loro script, più la pagina autoconsistente nel repo: **71 su 71**. La cartella del dossier si fotografa e si ripristina a ogni caso, perché con la pagina completa il generatore scrive nel repo |

**Per rieseguire la distorsione** (dalla radice del repo):

```sh
/usr/bin/python3 docs/preamp/data/2026-10-10/L51c/distorsione/script/oggi.py
/usr/bin/python3 docs/preamp/data/2026-10-10/L51c/distorsione/script/genera.py thd,imd oggi
/bin/zsh docs/preamp/data/2026-10-10/L51c/distorsione/script/esegui.sh <assoluto>/docs/preamp/data/2026-10-10/L51c/distorsione/deck/lista_thdimd.txt
/usr/bin/python3 docs/preamp/data/2026-10-10/L51c/distorsione/script/leggi_four.py oggi
```

**Il confronto con L46b** (`../../2026-10-01/L46b/run/sv_r10_esr0_r120_226/distorsione.csv`) sulle
24 righe: ampiezza, THD, h2, h3 e i due prodotti d'intermodulazione sono **uguali alla cifra**.
Cambiano solo il pavimento numerico (~−260 dB) e le armoniche sotto ~−195 dB, cioè il fondo del
metodo. I numeri: THD a 20 kHz a 0,2 V **0,000596 %** (tetto 0,001), dalla 5ª in su −192,6 dB
(tetto −140), intermodulazione **−125,6 dB** (tetto −110), a 2 V **0,0068 %** (tetto 0,01). Sono
cifre di modello, sul blocco da solo.
