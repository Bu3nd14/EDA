# L63a — i dati dello schematico completo dell'alimentatore (2026-10-21)

Il lotto ha prodotto un disegno, non misure: i file che contano stanno in
`docs/preamp/schematic/` (`sheet_kit.py`, `psu_draw.py`, `psu.svg`, `psu.pdf`,
`psu.manifest.json`). Qui c'è la prova che i suoi controlli rifiutano.

| File | Che cosa |
|---|---|
| `script/sabotaggi.py` | 14 manomissioni, ciascuna deve essere rifiutata per il suo motivo: 6 sul manifesto (`check_schematic.py` contro `psu.net`), 8 su disegni sbagliati apposta (`sheet_kit.py`) |

Si esegue col Python del venv (il kit usa schemdraw):

```sh
/Users/roberto/EDA/env/venv/bin/python3 docs/preamp/data/2026-10-21/L63a/script/sabotaggi.py
```

Esce 0 se tutte e 14 sono prese. Esito a fine L63a: **14 / 14**.

Le manomissioni:

- **sul controllo**:
  - il manifesto vero passa;
  - un piedino spostato su un'altra rete (R506.2 → VREF);
  - una parte tolta (D522);
  - una parte inventata (R999);
  - un piedino libero disegnato collegato (U509.2, PA4);
  - un piedino collegato non disegnato (U501.13, EN).
- **sul kit**:
  - un filo fra due reti;
  - due reti sullo stesso punto;
  - una rete in due pezzi senza nome (SUP_P);
  - un filo sopra una resistenza;
  - un'etichetta col nome di un'altra rete;
  - un testo sopra un altro;
  - una parte non disegnata;
  - un piedino libero usato come terminale.
