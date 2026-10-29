# L55 — il dispositivo d'uscita del blocco (2026-10-29)

NC-056: un driver di taglia intermedia col modello del costruttore contro il MJE15032 / MJE15033 sul banco
del blocco. Report `../../../reports/2026-10-29-L55-dispositivo-uscita.md`; decisione **ADR-106** («MJE as
it is»). **Il circuito non cambia**: le varianti stanno in `inc/` e `varianti/`. `<L>` = questa cartella;
Python con `/usr/bin/python3 -I`. Le corse (`run/`, ~5,4 GB) non stanno nel repository (`.gitignore`).

I criteri sono in `CRITERI.md`, scritti prima delle corse dei candidati (con la correzione delle cifre
attese di V1 del controllo, dichiarata lì). Ogni banco ha il suo caso noto sul MJE di oggi.

## Il candidato e il modello (`modelli/`)

`modelli/README.md`: la tabella dei vagliati (T7, T8, disponibilità, capacità, termico), la scelta
**onsemi MJE243G / MJE253G** (TO-225), le misure a 20 mA (`misura_modelli.py`, `misure.txt`) e il termico
(Boyd TV4, 21 °C/W **dall'elenco del distributore**, la curva del costruttore non trovata). I modelli in
`models/bjt_npn/mje243.lib`, `models/bjt_pnp/mje253.lib` col congelamento in `vendor/`; la ricetta
`_tb_mje24x` in `scripts/validate_models.py` (89 / 89).

## Il banco freddo (`sintesi.csv`, `idss.csv`)

Copia di L46a (`script/genera.py`, `esegui.sh`, `leggi_four.py`, `sintesi.py`, `idss.py`,
`riassumi_*.py`); `script/varianti.py` scrive `inc/<v>.inc` dal `gain_block_flat.inc` di oggi.

| variante | cosa |
|---|---|
| `mje` | il blocco di oggi (il **caso noto**: V1 64,92°, la storia del banco — ADR-054 64,94°; PSRR+ e riposo di L56 alla cifra) |
| `mje_senza_d158d159` | senza i diodi di ADR-095: cifre identiche (spiega che i diodi non muovono V1) |
| `mje24x_r<R>` | il candidato, R128 spazzata: 1,78k dà 20,75 / 20,70 mA (scelta), 1,74k 20,08 / 20,03 |
| `mje24x`, `mje24x_cm330p`, `mje24x_cm220p` | il candidato con R128 1,78k e il Miller a 470 / 330 / 220 pF (220 pF: blocco A 59,54°, fuori) |
| `*_fz` | le stesse con le capacità dei finali ferme a TNOM (`modelli_banco/`): a 27 °C cifre identiche |

## Il banco a caldo (`sintesi_caldo.csv`, `riposo.csv`, `tj/`)

`script/v4caldo.py` (copia di L45d2b3b2b2, con la tabella `FINALI` delle Rth per modello: il MJE nudo
62,5 / col WA-T220-101E 24,5 °C/W; il TO-225 nudo 83,4 / col TV4 31,34 °C/W), `genera_imd.py`,
`sintesi_caldo.py`, `riposo.py`. Spec `--sot223--diss` e `--sot223--diss--molt`.

**Il modello del MJE253 a caldo** (limitations #82): VJC 0,033 V, sotto zero sopra ~35 °C
(`script/vj_temperatura.py`); i deck del candidato con la temperatura di istanza si fermano al primo
punto della `tran` (`script/prova_tran.py`: senza `temp=` sui finali passa, con `dtemp=` o `gear` no). Le
cifre a caldo del candidato vengono dalle copie di banco `modelli_banco/*_fermo.lib`
(`script/modelli_banco.py`: `TLEVC=1`, coefficienti zero). **Caso noto del congelamento**: `mje_fz` ridà
`mje` all'ultima cifra (margine 2,7 / 3,0 dB, THD 0,000726 %, IMD −131,7 dB). Le corse del candidato senza
congelamento (`mje24x--*`, `mje24x_cm330p--*`) sono fallite tutte e restano solo come prova.

## I guasti dei finali e P7 (`calore_<v>.csv`, `dissipatore.csv`)

`script/guasti_finali.py`: il banco del calore di L45d2b3b2a / L45d2b3b2b2 (le cinque posizioni, rail
ideali, il guasto a 0,3 s) con rif e i sei modi di Q132 / Q133, per `fmje` (il sorgente byte per byte),
`c243` e `c243m`; e `tb_mute_corto.cir` (P7) col subckt della variante in `deck/p7/`. **Caso noto**:
`script/confronta_noto.py`, `calore_fmje.csv` contro `calore_sorg.csv` di L45d2b3b2b2, 465 celle, 0
diverse; `dissipatore_l55.py` ridà i 99 / 95 / 67 / 69 / 70 °C di ADR-099. `oltre_limiti.py`: le parti
oltre i limiti (la colonna giudica i finali col MJE nudo; per i finali vale `dissipatore.csv`).
`fmea_correzione.csv`: la riga di Q132 in corto base-emettitore, 126 °C (NC-076).

## Le cifre della domanda

`script/tabella_opzioni.py` le riconta dai CSV. La quota del rifiuto delle alimentazioni:
`data/2026-09-23/L40/script/limiti_psrr.py run/<v>/tb_zout_psrr_noise tb_zout_psrr_noise 0db 3db 10db`.

## Rifare

```sh
/usr/bin/python3 -I <L>/script/varianti.py mje mje24x mje24x_cm330p mje24x_cm220p mje_fz mje24x_fz mje24x_cm330p_fz
/usr/bin/python3 -I <L>/script/genera.py op,v1,psrr,thd,imd,slew mje mje24x mje24x_cm330p mje24x_cm220p
/bin/zsh <L>/script/esegui.sh <L>/deck/lista_opv1psrrthdimdslew.txt
/usr/bin/python3 -I <L>/script/idss.py mje mje24x mje24x_cm330p mje24x_cm220p
/bin/zsh <L>/script/esegui.sh <L>/deck/lista_idss.txt
/usr/bin/python3 -I <L>/script/riassumi_op.py mje mje24x mje24x_cm330p mje24x_cm220p
/usr/bin/python3 -I <L>/script/leggi_four.py mje mje24x mje24x_cm330p mje24x_cm220p
/usr/bin/python3 -I <L>/script/sintesi.py mje mje24x mje24x_cm330p mje24x_cm220p
/usr/bin/python3 -I <L>/script/riassumi_idss.py mje mje24x mje24x_cm330p mje24x_cm220p
/usr/bin/python3 -I <L>/script/modelli_banco.py
/usr/bin/python3 -I <L>/script/v4caldo.py op mje--sot223--diss mje_fz--sot223--diss mje24x_fz--sot223--diss mje24x_cm330p_fz--sot223--diss
/bin/zsh <L>/script/esegui.sh <L>/deck/lista_op.txt      # poi p2, p3, p4 allo stesso modo, poi deck4
/usr/bin/python3 -I <L>/script/leggi_four.py <spec...>
/usr/bin/python3 -I <L>/script/sintesi_caldo.py <spec...>
/usr/bin/python3 -I <L>/script/riposo.py <spec...>
/usr/bin/python3 -I <L>/script/guasti_finali.py
/bin/zsh <L>/script/corri.sh <L>/deck/lista_finali.txt 6
/bin/zsh <L>/script/esegui.sh <L>/deck/lista_p7.txt
/usr/bin/python3 -I <L>/script/analizza.py fmje c243 c243m
/usr/bin/python3 -I <L>/script/confronta_noto.py
/usr/bin/python3 -I <L>/script/dissipatore_l55.py fmje c243 c243m
/usr/bin/python3 -I <L>/script/tabella_opzioni.py
```

`deck/lista_*.txt` è l'ultima lista scritta per quella fase: una corsa successiva la sovrascrive.
