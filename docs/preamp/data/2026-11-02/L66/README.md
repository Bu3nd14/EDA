# L66 — il VAS a 126 °C e i modi fuori dai quindici (2026-11-02)

NC-076 (maggiore, prima di G1): col finale NPN Q132 in corto base-emettitore il VAS Q122 a 126 °C con
60 °C d'aria contro i 125 di P7, e l'uscita del blocco al rail. Decisione **ADR-111**; report
`../../../reports/2026-11-02-L66-vas-modi-fuori.md`. `<L>` = questa cartella; Python con
`/usr/bin/python3 -I`.

## I banchi e i casi noti

| Banco | Copiato da | Caso noto |
|---|---|---|
| `script/genera.py` (il calore dei guasti del blocco) | il banco di L45d2b3b2b2, caricato per percorso (come L58b) | `rif`, `Q132_ce`, `R126_cc`, `Q132_be` nelle cinque posizioni: 20 righe di `calore_sorg.csv` di L58b e 5 di `calore_fmje.csv` di L55, 775 celle, **0 diverse** (`script/confronta_noto.py`) |
| `script/genera_stax.py` (la Stax, P10) | `genera_stax_lunghi.py` di L45d2b3b2b2 | `G0_F2_Q132_ce`, `G0_F2_Q133_ce` (e `_k105`): 114,1 / 119,8 e 113,7 / 119,4 ms, come `p10_stax_lunghi.csv` di L45d2b3b2b2 |
| `script/v4caldo.py` e compagni (V4 a caldo, ogni giunzione alla sua Tj) | L45d2b3b2b2 | `sorg--sot223--diss`: margine 2,7 dB a 57 °C, THD 0,000726 %, IMD −131,7 dB, come `sintesi_caldo.csv` di L45d2b3b2b2 |
| `script/prepara_regressione.py`, `regressione.sh`, `confronta_regressione.py`, `op_caldo.py` | L45d2b3b2a (la regex del moltiplicatore di R123 generalizzata: il deck del sorgente ha 33, non 56) | `oggi` = il sorgente di prima, base del confronto |

Le varianti: `sorg` è il sorgente **com'era all'inizio di L66** (33 + 22 Ω, ADR-099). `lim34`
(34,0 + 21,0 Ω) e `lim365` (36,5 + 18,7 Ω) sono scritte da `script/varianti.py`, che rifiuta se cambiano
più delle due righe. `dopo` è il sorgente dopo ADR-111, uguale a `lim365` salvo la riga di commento.
Rigenerando `genera.py sorg` oggi si otterrebbe il sorgente nuovo: per questo, dopo ADR-111, si usa `dopo`.

## Le cifre

- **Il meccanismo** (`meccanismo.csv`, `script/meccanismo.py`: i deck del banco con le tensioni dei nodi
  e le correnti alla fine della corsa): sano NX +1,02 / NY −1,00 V, VAS 10,7 mA; con Q132 in corto
  base-emettitore OUT −13,6 V, VAS 19,8 mA, Q193 6,0 mA (il limitatore al limite), Q125 saturo (NY
  −14,75 V), Q133 25,5 mA, lo specchio spento.
- **I 91 modi fuori dai quindici** (`confronto.csv`, `script/confronto.py`): sul sorgente contro la riga
  della FMEA. Fuori da P7 solo **D158 in corto, 126 °C** (lo stesso guasto). I picchi al jack sono uguali
  entro 0,1 dB, salvo D158 in corto, che ora va al rail.
- **R120 in corto** (limitations #75): nella lista lunga a 2,3 s le cinque corse si sono fermate oltre
  un'ora di CPU ciascuna. Le ho fermate a mano (rc 143 in `run/esiti.tsv`): **errore mio**, perché la #75
  dice di correrle da sole e corte. Rifatte a 0,6 s (`genera.py corta`, `dopo` per il sorgente nuovo),
  in serie, ~25 min l'una, sotto 1 GB.
- **La Stax** (`p10_stax.csv`): Q132_be e D158_cc 114,3 ms, 120,0 col condensatore a +5 % (P10: 150).
- **Le varianti** (`calore_lim34.csv`, `calore_lim365.csv`, `*t60.csv` coi dispositivi a 60 °C):

  | VAS, 60 °C d'aria, 125 °C/W | sorg | lim34 | lim365 |
  |---|---|---|---|
  | Q132_be | 126 | 124 | 120 |
  | D158_cc | 126 | 125 | 121 |
  | i quattro di ADR-099 | 123–124 | 118–123 | 118–119 |
  | Q132_be, dispositivi a 60 °C | 121 | 119 | 115 |

  Le colonne dei finali in `calore_*.csv` sono **senza dissipatore** (62,5 °C/W), come nei casi noti.
  `calore_dopo.csv` (`script/analizza_diss.py`) li dà col WA-T220-101E, a 24,5 °C/W.
- **Il blocco sano** (`sintesi_regressione.csv`, `regressione/misure_*.csv`): margine di fase minimo
  43,33 → 43,34 / 43,26°.
  **A riposo a caldo** (`op_caldo.csv`): il limitatore 0,06 / 0,9 / 7,5 µA (sorg), 0,09 / 1,3 / 10,4
  (lim34), 0,25 / 3,3 / 23 (lim365) a 27 / 60 / 90 °C.
  **V4 a caldo** (`sintesi_caldo.csv`): 0 su 12 fuori in tutte e tre; IMD a 57 °C −131,7 / −131,6 /
  −131,0 dB.
- **Il sorgente** (ADR-111): R123 36,5, R192 18,7 nelle otto istanze. `spice/preamp/gain_block*` uguali a
  `varianti/lim365/`. Netlist: 396 / 44 reti con gli stessi piedini; una rinominata, AL_OUT → F2L_IN
  (limitations #74; il sinonimo è aggiunto in `audio_draw.py`). `prima/` tiene i file di prima.
  `run_tests.sh` 14 / 0.
- **Tutti i modi sul sorgente nuovo** (`calore_dopo.csv`, `analisi_jack_dopo.csv`) e **la FMEA**
  (`fmea_l66.csv`, `script/fmea_l66.py`): vedi il report.

## Rifare

```sh
/usr/bin/python3 -I <L>/script/genera.py noto ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_noto.txt 6
/usr/bin/python3 -I <L>/script/genera.py fuori ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_fuori.txt 6
/usr/bin/python3 -I <L>/script/genera.py corta ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_corta.txt 1
/usr/bin/python3 -I <L>/script/analizza.py sorg ; /usr/bin/python3 -I <L>/script/confronta_noto.py
/usr/bin/python3 -I <L>/script/confronto.py
/usr/bin/python3 -I <L>/script/meccanismo.py A rif Q132_be      # poi uno.sh su ciascuno
/usr/bin/python3 -I <L>/script/leggi_meccanismo.py <L>/meccanismo.csv A_rif A_Q132_be
/usr/bin/python3 -I <L>/script/genera_stax.py stax G0_F2_Q132_ce G0_F2_Q132_ce_k105 G0_F2_Q133_ce G0_F2_Q133_ce_k105 G0_F2_Q132_be G0_F2_Q132_be_k105 G0_F2_D158_cc G0_F2_D158_cc_k105
/bin/zsh <L>/script/corri.sh <L>/deck/lista_stax.txt 3
/usr/bin/python3 -I docs/preamp/data/2026-10-13/L45b/script/analizza_p10.py <L>/p10_stax.csv <L>/run/stax/*/
/usr/bin/python3 -I <L>/script/varianti.py lim34 Q132_be Q133_ce Q125_ce R126_cc D102_ap D103_ap D158_cc   # e lim365
/usr/bin/python3 -I <L>/script/caldo.py sorg 60 Q132_be D102_ap D103_ap Q125_ce R126_cc Q133_ce            # e lim34, lim365
/bin/zsh <L>/script/corri.sh <L>/deck/lista_rimedi.txt 4
/usr/bin/python3 -I <L>/script/analizza.py lim34 lim365 sorgt60 lim34t60 lim365t60
/usr/bin/python3 -I <L>/script/prepara_regressione.py oggi lim34 lim365
/bin/zsh <L>/script/regressione.sh oggi        # e lim34, lim365
/usr/bin/python3 -I <L>/script/confronta_regressione.py lim34 lim365 ; /usr/bin/python3 -I <L>/script/sintesi_regressione.py lim34 lim365
/usr/bin/python3 -I <L>/script/op_caldo.py ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_op_caldo.txt 3 ; /usr/bin/python3 -I <L>/script/op_caldo.py leggi
/usr/bin/python3 -I <L>/script/v4caldo.py op sorg--sot223--diss lim34--sot223--diss lim365--sot223--diss
/bin/zsh <L>/script/esegui.sh <L>/deck/lista_op.txt      # poi p2, p3, p4 allo stesso modo, poi deck4
/usr/bin/python3 -I <L>/script/sintesi_caldo.py sorg--sot223--diss lim34--sot223--diss lim365--sot223--diss
/bin/zsh <L>/script/rigenera.sh                 # dopo la modifica di circuits/preamp/gain_block.py
/usr/bin/python3 -I docs/preamp/data/2026-10-22/L45d2b3b1/script/nomi_reti.py <L>/prima/preamp_audio.net circuits/preamp/preamp_audio.net
/usr/bin/python3 -I <L>/script/genera.py dopo ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_dopo.txt 5 ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_dopo_corta.txt 1
/usr/bin/python3 -I <L>/script/analizza_diss.py dopo ; /usr/bin/python3 -I <L>/script/fmea_l66.py
```

`run/` (le corse, ~30 GB con R120 in corto) e `regressione/<v>/` non stanno nel repository: si rifanno.
