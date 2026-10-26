# L54a — il micro, lo standby e lo spegnimento morbido, riesaminati coi numeri (2026-10-25 / 26)

Prima parte di **L54** (diviso dall'utente all'inizio, «Due parti»: L54a i numeri, la scelta e l'ADR;
L54b il sorgente). Report `../../../reports/2026-10-26-L54a-micro-standby.md`. Decisione **ADR-102**
(«Comparatori, con lo standby»); **NC-054 chiusa**, NC-037 avanza. `<L>` = questa cartella. Python
con `/usr/bin/python3 -I`.

## Il banco, e il suo caso noto

`psu/` è il banco dell'alimentatore di L45d2b3b1 (`data/2026-10-22/L45d2b3b1/psu/`), copiato, con il
suo `carico.txt` (il carico di L45d2b3b1: senza il limitatore di L57b, ~1 mA per rail in meno,
dichiarato). **Il caso noto** `f_d530_corto_muss --n2n7002 ds`: deck uguale salvo i percorsi,
`core_g1.csv` byte-identico (`seq/controllo/`); col generatore esteso ancora uguale (`seq/controllo2/`,
cambia solo il nome della cartella nell'intestazione).

Le estensioni di `genera_tb_psu.py` (ognuna spenta per default, i deck del micro non cambiano):
- `--timer micro | comparatori | diretto`: chi pilota `MUTE_REQ`, `PERMIT_REQ`, `MAINS_REQ`,
  `VRELAY_EN`. `comparatori` = `TIMER_AN` (il temporizzatore di ADR-102, commentato riga per riga);
  `diretto` = lo stesso senza standby: il contatto di K501 sempre chiuso, la sua bobina non pilotata,
  il frontale chiuso;
- `--rete <fattore>` su qualunque caso, buchi compresi; `--tss` (3,0 per i temporizzatori analogici,
  che si accendono davvero da t = 0); `--sonda-t2` (le potenze dei secondari); `--vrelay-da t1`
  (senza T2: un raddrizzatore suo sui secondari di T1);
- i casi nuovi: `fredda` (la rete su tutto spento), `fredda_u501`, `accensione_u501` (il timeout dei
  2 s), `ritenuta_frontale` (la ritenuta azzerata dal frontale).

Gli script nuovi: `corri_an.sh` (un giro, le guardie e il ripiego di `corri_seq.sh`),
`corri_lista_an.sh` / `uno_an.sh`, `analizza_an.py` (i criteri di L41c dalle sole forme d'onda; legge
anche le cartelle del micro), `energia.py` (R550, R552), `potenza_t2.py`, `sonda.py`, `piedini.py`.

## Le correzioni del disegno, in ordine

1. `AT_ON` 47k → 10k: col pull-down di `VRELAY_EN` (R527) stava a 3,3 V.
2. `PERMIT_REQ` col suo canale: senza, D522 teneva `MUTE_G` al permissivo e `MUTE_REQ` a 2,5 V, e il
   permissivo non saliva mai (i jack mai collegati).
3. `PERMIT_REQ` ~24 ms dopo (4,7 MΩ · 10 nF): da `AT_MRQ` diretto Δ era 15,4 ms, sotto 16,9.
4. 1 nF base-emettitore sulla ritenuta: ogni caso di guasto si fermava sul suo fronte.
5. `AT_PGT` 680k → 820k: dopo un buco di 20 ms la musica tornava 435 ms dopo la rete (< 500).
6. Il controfattuale analogico toglie anche `CATprt` (il secondo Δ); senza standby la bobina di K501
   non si pilota.
Ogni corsa dei CSV è stata rifatta dopo l'ultima correzione che la tocca.

## Gli esiti

- `an_comparatori.csv`, `an_diretto.csv`, `an_micro.csv`, `an_fmea.csv`, `an_fmea_micro.csv`: tutti
  i casi dentro (C2, C3, jack prima del guadagno, jack prima di V+ < 10,6 V); i controfattuali
  falliscono come devono. Col micro i tre casi del sorvegliante cieco non hanno punto fisso (le
  sostituzioni di `MUTE_G_IN`): vale la cifra di L45c2.
- Energie (`energia.py`): corto di C509 R550 7,65 / 9,35 J coi comparatori, 7,21 / 8,80 col micro,
  **44,5 / 54,3 J nel primo secondo e senza fine** senza standby; bobina di K501 in corto R552
  0,47 / 0,54 J (micro 0,49 / 0,56).
- Potenze (`potenza_t2.py`): standby comparatori 116,7 / 130,1 / 145,1 mW (2,5–3,0 s); nella finestra
  1–2 s comparatori 193,4 / 217,1 / 241,2 e micro 152,6 / 171,8 / 191,3 mW (−10 / 0 / +10 %). In
  musica a +10 %: micro 18,03 W, comparatori 18,00, senza standby con T2 17,38, con `VRELAY` da T1
  17,63 W (più il ferro di T2, ~0,45 W, che se ne va).

## Rifare

```sh
/bin/zsh <L>/psu/corri_seq.sh --solo-compila
/usr/bin/env GIRI_MAX=20 /bin/zsh <L>/psu/corri_seq.sh f_d530_corto_muss controllo --n2n7002 ds
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_an.txt 5
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_an2.txt 5
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_an3.txt 5
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_diretto.txt 5
/usr/bin/env GIRI_MAX=20 /bin/zsh <L>/psu/corri_lista.sh <L>/lista_micro.txt micro --n2n7002 ds
/usr/bin/env GIRI_MAX=20 /bin/zsh <L>/psu/corri_lista.sh <L>/lista_micro_fmea.txt fmea_micro --n2n7002 ds
/usr/bin/env GIRI_MAX=20 /bin/zsh <L>/psu/corri_lista.sh <L>/lista_consumo_micro.txt consumo_micro --n2n7002 ds --sonda-t2
#   (e consumo_micro_m10 / _p10 con --rete 0.9 / 1.1)
/usr/bin/python3 -I <L>/psu/analizza_an.py --te=3.0 <L>/an_comparatori.csv <L>/seq/comparatori/<caso> ...
/usr/bin/python3 -I <L>/psu/analizza_an.py --te=2.0 <L>/an_micro.csv <L>/seq/micro/<caso> ...
/usr/bin/python3 -I <L>/psu/energia.py 3.0 <L>/seq/fmea_comparatori/f_c509_corto_mus/*_g1_out.txt
/usr/bin/python3 -I <L>/psu/potenza_t2.py <L>/seq/consumo_comparatori/accensione/*_g1_out.txt 2.5 3.0
```

Le forme d'onda (`*_out.txt`, ~34 MB l'una) non stanno nel repository (`.gitignore`): si rifanno.
