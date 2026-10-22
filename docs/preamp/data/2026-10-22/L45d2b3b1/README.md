# L45d2b3b1 — i guasti singoli rifatti sul circuito di oggi (2026-10-22)

Prima parte di **L45d2b3b** (diviso dall'utente all'inizio, «Due parti»: b1 le corse, b2 la sintesi;
poi, coi numeri, un lotto in mezzo per il calore, ADR-097). Report
`../../../reports/2026-10-22-L45d2b3b1-guasti-rifatti.md`. Decisione **ADR-097**; **NC-075** aperta;
NC-042 avanza. `<L>` = questa cartella, `<R>` = la radice del repo. Python con `/usr/bin/python3 -I`,
i disegni col venv.

## I banchi, e il caso noto di ciascuno

Ogni banco è quello di un lotto precedente, importato o copiato, provato su un suo caso noto **prima**
di guardare un numero nuovo.

| Banco | Da | Che cosa | Caso noto | Esito |
|---|---|---|---|---|
| calore (`script/genera_calore.py`) | L62b (canale di L45a) | ogni modo del blocco (132), cinque posizioni, rail ideali, potenze a fine corsa, Tj a 27 / 60 °C; in più la potenza dei diodi | il blocco di L62b sui modi di L62b in A (`varianti/l62b`) | `confronta_l62b.py`: **897 celle, 0 diverse** |
| Stax (`script/genera_stax.py`) | L60d2 (L60c2, L60c1, L45a) | P10 sulla fissa 2 col carico e 1 µF prima di K3: 107 + 20 modi, più D154–D159 | il blocco di L60d2 (commit 4fde9e40, `varianti/l60d2`) su sei casi | `confronta_l60d2.py`: **306 celle, 0 diverse** |
| relè (`script/genera_rele.py`) | L60a | scelte 6, 8, 9, 10 col blocco di oggi | i tre riferimenti di L60a | uguali, salvo R126 in corto a vuoto (44 → 60 ms, il blocco nuovo) |
| alimentatore (`psu/`, copiato) | L45d2b2b2 | i modi delle parti di ADR-093 / ADR-094 (`RIGHE_NUOVE`), tre reti, 2N7002 tarato; la cella RC in corto (`carico`) | `f_u512_cortoio_muss`, `f_d530_corto_muss` sul sorgente | punto fisso e CSV del firmware **uguali**, deck uguali salvo i percorsi |
| P7 (`script/genera_p7.py`) | L45d2b2c / L60d1 | `tb_mute_corto` con Q146 / Q148, le giunzioni dei finali e i diodi | 1: il blocco di oggi contro `tb_cbe_nom_*` di L45d2b2c; 2: il blocco di L60d2 con R153 a 1 Ω contro L60d2 | 1: **29 400 celle**, 0 oltre 1e-3; 2: **0,4112 / 2,006 W**, uguale |

## Gli esiti

- **Il calore** (`sintesi_calore.csv`, `calore_oggi.csv`, `analisi_jack_oggi.csv`): 132 modi, **16 con
  una parte oltre i limiti a 60 °C** — l'aiuto dello specchio Q148 fino a 5123 °C (R149 in corto),
  lo specchio 574 °C, il VAS fino a 308 °C, i diodi del riferimento con R101 in corto. In L45a li
  fermava il rivelatore (ADR-072, «col calore»); ADR-081 l'ha tolto. → un lotto dedicato (ADR-097, 4).
- **La Stax** (`p10_stax.csv`, sul blocco prima di ADR-097): nessun guasto oltre 150 ms; il peggiore
  D102 / D103 aperti in A, **141,3 / 145,5 ms** (C nominale / +5 %; erano 125,1 / 128,5 in L60d2).
  Q132 / Q133 in corto collettore-emettitore da ~20 a 107–124 ms (il limite di corrente di ADR-095).
  Tre corse fermate subito dopo il guasto rifatte in gear (`p10_stax_gear.csv`): 118,3 / 124,1 ms,
  come L60d2. I modi di D154–D159: 0 ms.
- **I relè** (`analisi_rele.csv`): K13 116 / 95 ms, K7 118 ms (era 70), R126 in corto 71 ms (era 37)
  sulla Stax; K3 12 V per sempre (escluso da ADR-085), K2 / K4 su fissa 1 / principale senza durata
  (ADR-081).
- **L'alimentatore** (`analisi_nuove.csv`, `riassunto_nuove.csv`): 54 casi, tutte le parti dentro
  salvo **C536 in corto, U504 2,99 W** (lo spegnimento termico del regolatore: ADR-097, 2). Otto casi
  senza punto fisso (C536 in corto, U512 spento, R503 aperta: i 5 V o il riferimento persi; e V5 a
  −20 V, un artefatto del banco, limitations #73).
- **La cella RC in corto** (`seq/cella/`, `script/energia_cella.py`): ciascuna 20 Ω 11,1 W di picco,
  1,09 / 1,24 / 1,28 J a rete −10 / 0 / +10 % → NC-075.
- **R153 in corto** (`p7_r153cc.txt`, `p7/`): Q146 0,39 W, 216 °C con 60 °C d'aria → R153 + R160,
  due 2,4 kΩ (ADR-097, 1); con una metà in corto 0,029 W, 72 °C.

## Il sorgente (ADR-097)

`gain_block.py`: R153 2,4 kΩ da NFC a NFCR, R160 2,4 kΩ da NFCR al rail negativo (sezione 13, in
fondo: limitations #22); il commento della cella RC con la cifra di oggi. Scheda audio 570 → 578
parti (`script/conta_parti.py`: nessuna sigla doppia, 8 nodi NFCR con due resistenze). Le reti
confrontate per piedini (`script/nomi_reti.py`): cambia solo VMINUS, e tre nomi (limitations #74). I
disegni: `gain_block_draw.py` 62 dispositivi, `audio_draw.py` 578 su 578 coi sinonimi dei nomi.
`script/rigenera.sh` rigenera netlist e sottocircuito con la cartella corrente in `circuits/preamp`.

- **La regressione dei 21 deck veloci** (`script/regressione.sh`): `regressione/prima` sul blocco
  generato prima del cambio, `regressione/dopo` col blocco nuovo; 21 + 21 con esito 0.
  `misure_regressione.py` e `riassunto_regressione.py`: fuori da `tb_mute_corto` 0,4 % al più (un
  guadagno a 100 kHz di `tb_ac`); `p7_massimi.py`: i massimi di P7 entro lo 0,2 %.
- `run_tests.sh` **15 / 0**.

## Le corse sul blocco dopo ADR-097

`script/genera_dopo097.py` (cartelle `*dopo097*`): i modi di R153 / R160 al calore e sulla Stax, e R120
in corto **a 0,6 s, una corsa alla volta** (limitations #75). `script/genera_stax_lunghi.py`
(`deck/stax_lunghi/`): i guasti oltre 100 ms sulla Stax rifatti sul blocco nuovo, per il «Da riaprire
se» di ADR-089 («R153 cambia valore»).

- **Il calore** (`sintesi_calore_dopo097.csv`): il riferimento sano uguale (−2,9 mV, 151,7 mA); R153 /
  R160 aperte o in corto e R120 in corto (0,6 s) **senza parti oltre i limiti**, Tj massima 86–87 °C.
  R153 o R160 aperta: la principale a 1,36 V (116 dB SPL), senza durata (ADR-081); sulla Stax 0 ms.
- **La Stax** (`stax_lunghi.csv`, `script/confronta_lunghi.py`): 121 casi, scarto ≤ 0,4 ms, nessuno
  oltre 150 ms (Q122 in corto, fermata subito dopo il guasto, rifatta in gear con `rifai_gear.py
  --da stax_lunghi`: 118,1 ms) → ADR-098.
- **Le righe** (`righe_b1.csv`, `script/righe_b1.py`): 97 = 80 entro, 15 al calore (L45d2b3b2), C145 in
  corto all'impulso della cella (NC-075), K3 escluso (ADR-085). Ingresso della sintesi (L45d2b3b3).

## Rifare

```sh
/usr/bin/python3 -I <L>/script/genera_calore.py
/bin/zsh <L>/script/corri.sh <L>/deck/lista_controllo.txt 8      # il caso noto
/usr/bin/python3 -I <L>/script/analizza_calore.py l62b ; /usr/bin/python3 -I <L>/script/confronta_l62b.py
/bin/zsh <L>/script/corri.sh <L>/deck/lista_calore.txt 6         # NON R120 in corto su 2,3 s insieme (#75)
/usr/bin/python3 -I <L>/script/analizza_calore.py oggi ; /usr/bin/python3 -I <L>/script/sintesi_calore.py
/usr/bin/python3 -I <L>/script/genera_stax.py
/bin/zsh <L>/script/corri.sh <L>/deck/lista_stax_controllo.txt 3
/usr/bin/python3 -I <R>/docs/preamp/data/2026-10-13/L45b/script/analizza_p10.py <L>/p10_controllo.csv <L>/run/stax_l60d2/*/
/usr/bin/python3 -I <L>/script/confronta_l60d2.py
/bin/zsh <L>/script/corri.sh <L>/deck/lista_stax.txt 3
/usr/bin/python3 -I <R>/docs/preamp/data/2026-10-13/L45b/script/analizza_p10.py <L>/p10_stax_grezzo.csv <L>/run/stax_g0/G0_CTRL_*/ <L>/run/stax_g0/G0_pin_*/ <L>/run/stax_guasti/*/
/usr/bin/python3 -I <L>/script/sintesi_stax.py
/usr/bin/python3 -I <L>/script/rifai_gear.py G0_A_R107_cc G0_A_R107_cc_k105 G0_A_Q106_ce   # poi corri.sh e analizza_p10 -> p10_stax_gear.csv
/usr/bin/python3 -I <L>/script/genera_rele.py ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_rele.txt 4
/usr/bin/python3 -I <L>/script/genera_p7.py ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_p7.txt 3
/usr/bin/python3 -I <L>/script/sintesi_p7.py
/bin/zsh <L>/psu/corri_seq.sh --solo-compila
/usr/bin/env GIRI_MAX=20 /bin/zsh <L>/psu/corri_lista.sh <L>/lista_controllo_psu.txt controllo --n2n7002 ds
/usr/bin/env GIRI_MAX=20 /bin/zsh <L>/psu/corri_lista.sh <L>/lista_nuove.txt nuove --n2n7002 ds
/usr/bin/python3 -I <L>/script/analizza_075.py <L>/seq/nuove <L>/analisi_nuove.csv @<L>/lista_nuove.txt
/usr/bin/python3 -I <L>/script/riassunto_075.py <L>/analisi_nuove.csv <L>/riassunto_nuove.csv
/usr/bin/env GIRI_MAX=20 /bin/zsh <L>/psu/corri_lista.sh <L>/lista_cella.txt cella --n2n7002 ds
/usr/bin/python3 -I <L>/script/energia_cella.py <L>/seq/cella f_c145_corto_musm10s f_c145_corto_muss f_c145_corto_musp10s
/bin/zsh <L>/script/regressione.sh prima                          # sul blocco generato PRIMA del sorgente
/bin/zsh <L>/script/rigenera.sh
/bin/zsh <L>/script/regressione.sh dopo
/usr/bin/python3 -I <L>/script/misure_regressione.py ; /usr/bin/python3 -I <L>/script/riassunto_regressione.py ; /usr/bin/python3 -I <L>/script/p7_massimi.py
/usr/bin/python3 -I <L>/script/genera_dopo097.py
/bin/zsh <L>/script/corri.sh <L>/deck/lista_dopo097.txt 3
/bin/zsh <L>/script/corri.sh <L>/deck/lista_dopo097_r120.txt 2   # ~1 GB l'una, ~30 min
/usr/bin/python3 -I <L>/script/analizza_calore.py dopo097 ; /usr/bin/python3 -I <L>/script/sintesi_calore.py dopo097
/usr/bin/python3 -I <L>/script/genera_stax_lunghi.py ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_stax_lunghi.txt 3
/usr/bin/python3 -I <R>/docs/preamp/data/2026-10-13/L45b/script/analizza_p10.py <L>/p10_stax_lunghi.csv <L>/run/stax_lunghi/*/
/usr/bin/python3 -I <L>/script/confronta_lunghi.py
/usr/bin/python3 -I <L>/script/righe_b1.py
```

## Il crash

Alle 12:48 il Mac si è bloccato: le cinque corse di R120 in corto del calore, su 2,3 s, stavano a
~9 GB ciascuna (limitations #75). Il lavoro era su disco e si è salvato; quelle corse sono rifatte
corte.

## Che cosa sta nel repository

`run/` (le corse, ~77 GB) e le forme d'onda delle sequenze (`*_out.txt`) no: si rifanno. Le tabelle di
P7 sono copiate in `p7/<variante>_<tabella>.csv`.
