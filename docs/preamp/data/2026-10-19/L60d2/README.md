# L60d2 — i guasti sulla Stax e V2 con la media (2026-10-19)

Report `../../../reports/2026-10-19-L60d2-guasti-stax-e-v2-media.md`. Decisioni ADR-088 (la correzione
dopo la media) e ADR-089 (i guasti più lunghi accettati sotto il tetto). `<L>` = questa cartella,
`<R>` = la radice del repo.

## I file

| Percorso | Che cosa |
|---|---|
| `sabotaggi_v2.txt` | `scripts/v2_metodo.py sabotaggi`: 27 controlli, 15 sabotaggi su 15 presi (T16 impulsi stretti, T17 toni a 1 e 20 kHz) |
| `script/prova_metodo.py`, `prova_metodo.txt` | il metodo nuovo su due riferimenti veri della matrice, accanto a `b1_confronto.py` di L60d1: sui segnali lisci le cifre coincidono |
| `script/genera_L60d2.py`, `deck/`, `inc/` | il banco dei guasti sulla Stax: quello di L60c2 importato, 107 modi + 20 delle parti nuove, A e F2, C nominale e +5 %; **le copie guaste del blocco riscritte dal blocco di oggi** in `inc/` (limitations #62) |
| `script/uno.sh`, `script/corri.sh` | le corse, 3 alla volta (la matrice di V2 ne teneva 7), esiti in `run/esiti.tsv` |
| `p10.csv`, `script/sintesi_p10.py`, `p10_stax.csv` | `analizza_p10.py` di L45b; la Stax contro 150 ms, con la stessa corsa di L60c2 accanto (`L60c2_sopra_ms`, `peggio_di_L60c2`) |
| `script/diagnosi_peggio.py`, `script/varianti_jq110b.py`, `p10_diagnosi.csv` | perché 17 guasti durano di più (blocco di L45a, di oggi, di oggi con R153 a 1 Ω); JQ110B aperta in A col C nominale che si ferma (gear, rshunt, fronte lento: si fermano; `reltol=3e-4`: 118,5 ms) |
| `p7/` | P7 con R123 / R126 a 56 Ω (`tb_mute_corto.cir` corretto): `prima/` = L60d1 (91 Ω), `dopo/` = oggi, `p7.txt` |
| `script/p7_r153cc.py`, `script/corri_p7_r153cc.sh`, `script/sintesi_p7_r153cc.py`, `p7_r153cc.txt` | P7 con R153 in corto: Q146 0,41 W. Con 1 mΩ dieci celle finiscono in un punto di lavoro sbagliato (rail a 48 W, limitations #59); la cifra è quella con 1 Ω |
| `v2/` | la matrice di V2: `manifest_sel.csv`, `manifest_finale.csv` (senza `off_r10m_d20_iii`), `analisi.csv` (con `picco_puntuale_V`), `verdetto.csv`, `verdetto_per_uscita.txt` (contro L48b), `contro_L60c2/`, `tempi.txt`, `peggiore_per_uscita.txt` (e `_L60c2`) |
| `script/peggiore_per_uscita.py` | il peggiore di ogni uscita da `analisi.csv`, con le regole del verdetto (limitations #63) |
| `script/gear_v2.py`, `script/corri_gear_v2.sh` | `off_r10m_d20_iii` e il suo riferimento col gear: si ferma ancora (è escluso dal verdetto da L29d2) |

Le corse (`run/`) non stanno nel repository (`.gitignore`): si rifanno.

## Rifare

```sh
/usr/bin/python3 -I <R>/scripts/v2_metodo.py sabotaggi
/usr/bin/python3 <R>/docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py      # uguale al versionato
/bin/zsh <R>/docs/preamp/data/2026-09-23/L29c/script/corri.sh <L>/run/v2 <R>/spice/preamp/tb/tb_v2_casopeggiore.cir '.*' 7   # ~6 h
/usr/bin/python3 -I <L>/script/genera_L60d2.py
/bin/zsh <L>/script/corri.sh <L>/deck/lista.txt                                                # ~1 h a 3 alla volta (R120 in corto, 1 h)
/usr/bin/python3 -I <R>/docs/preamp/data/2026-10-13/L45b/script/analizza_p10.py <L>/p10.csv <L>/run/g0/G0_CTRL_*/ <L>/run/g0/G0_pin_*/ <L>/run/guasti/*/
/usr/bin/python3 -I <L>/script/sintesi_p10.py
/usr/bin/python3 -I <L>/script/diagnosi_peggio.py ; /usr/bin/python3 -I <L>/script/varianti_jq110b.py
/bin/zsh <L>/script/corri.sh <L>/deck/lista_diagnosi.txt ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_jq110b.txt
/usr/bin/python3 -I <R>/docs/preamp/data/2026-10-13/L45b/script/analizza_p10.py <L>/p10_diagnosi.csv <L>/run/diagnosi/*/
/bin/zsh <R>/scripts/run_simulation.sh <R>/spice/preamp/tb/tb_mute_corto.cir <L>/p7/dopo/tb_mute_corto
/usr/bin/python3 -I <L>/p7/script/p7.py
/bin/zsh <L>/script/corri_p7_r153cc.sh 1 ; /usr/bin/python3 -I <L>/script/sintesi_p7_r153cc.py
/usr/bin/python3 <R>/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py <L>/run/v2
/usr/bin/python3 <R>/docs/preamp/data/2026-10-07/L48b/v2/filtra_manifesto.py <L>/run/v2/manifest_sel.csv <L>/run/v2/manifest_finale.csv off_r10m_d20_iii
/usr/bin/python3 <R>/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py <L>/run/v2/manifest_finale.csv <L>/run/v2 <L>/run/v2/analisi.csv 8
/usr/bin/python3 <R>/docs/preamp/data/2026-10-05/L47c2b1/script/verdetto.py <L>/run/v2/manifest_finale.csv <L>/run/v2/analisi.csv <L>/run/v2/verdetto.csv
/usr/bin/python3 -I <R>/docs/preamp/data/2026-10-15/L60c2/script/verdetto_per_uscita.py <L>/v2/verdetto.csv <R>/docs/preamp/data/2026-10-07/L48b/v2/matrice/verdetto.csv
/usr/bin/python3 -I <L>/script/peggiore_per_uscita.py <L>/v2/analisi.csv <L>/v2/manifest_finale.csv
```

`b1_confronto.py` di L60d1 importa `v2_metodo.py`: da L60d2 la sua riga «v2» legge la media corretta.
