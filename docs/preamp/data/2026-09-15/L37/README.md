# Dati di L37 — E4 nel dossier (2026-09-15)

Lotto **L37**, report `reports/2026-09-15-L37-e4-dossier.md`. Chiude **NC-033**.

**Nessun deck eseguito, nessun valore del circuito cambia.** L37 impagina i dati
di `data/2026-09-15/L13/dopo/`. Questa cartella contiene le prove che il
dossier rigenerato cambia solo dove tocca E4 e che i suoi controlli nuovi
cadono quando devono.

| File | Cosa |
|---|---|
| `script/confronto.py` | confronta il dossier di `main` prima di L37 con quello rigenerato: figure, sezioni di `index.html`, chiavi di `dossier.summary.json`, cifre vecchie e nuove. Esce 0 solo se cambia solo ciò che riguarda E4 |
| `confronto_esito.txt` | la sua uscita, rc 0 |
| `script/sabotaggi.py` | 10 casi: alberi di symlink ai dati veri con un file sostituito, e una copia del builder con `REPO` ricavato dall'albero; alcuni casi alterano la copia. Un caso passa solo se compaiono tutti i messaggi attesi e nessuno di quelli esclusi |
| `sabotaggi_esito.txt` | la sua uscita, rc 0: 10 casi come attesi, più il criterio ingenuo |

## Per rifarli

La baseline di `confronto.py` è l'output del builder **non modificato** sul
`main` di prima di L37 (`ffd7e02`), che L37 ha verificato identico byte per byte
ai file versionati. Per ricrearla:
1. `git worktree add <dir> ffd7e02`;
2. `/usr/bin/python3 <dir>/docs/preamp/dossier/build_dossier.py`;
3. copiare `index.html`, `fig_*.svg` e `dossier.summary.json` in una cartella.

Poi:
- `/usr/bin/python3 script/confronto.py <baseline> docs/preamp/dossier`;
- `/usr/bin/python3 script/sabotaggi.py <repo> <cartella di lavoro>`. Le
  cartelle dei casi non sono versionate.

## Il criterio ingenuo

In coda a `sabotaggi_esito.txt`: «il rapporto fra i modi della Zout al nodo
uguale al rapporto dei guadagni, entro l'1 %» scatta sulla Zout contaminata
(`prima/`, scarto 1,38·10⁻⁵) **e** su quella vera (`dopo/`, 3,74·10⁻⁴). Anche la
Zout vera scala col guadagno del modo, quindi quel criterio non distingue niente.
Il builder usa invece la grandezza, sotto 0,5 × G_lin Ω, più l'incrocio con
`tb_e4_uscite`. Vedi `docs/limitations.md` #28, «Correzione (L37)».
