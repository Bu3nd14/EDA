# L47c2b2 — il mute coi soli relè: i guasti e la regressione (2026-10-06)

La seconda parte di L47c2b (scelta dell'utente: «Due parti»). Esegue ADR-062 (il mute che taglia)
con il banco di ADR-063 (il contatto in serie col fronte di 4,55 µs, che vale anche per
`--matrice l41c`). Nessuna ADR nuova. Report:
`docs/preamp/reports/2026-10-06-L47c2b2-guasti-regressione.md`. Sotto, `<L>` è questa cartella.

## All'inizio, con l'utente

Quanto dura lo spegnimento lungo (il frontale aperto mentre suona la musica). In L41c finiva a
TE + 7,6 s perché la sfumatura teneva il relè di rete chiuso fino a TE + 6,63 s; col mute che
taglia il relè di rete apre a TE + 0,13 s. **Scelta dell'utente: «1,1 s»** (TE + 1,1 s, lo stesso
secondo dopo il relè di rete). Misurato poi: a TE + 1,1 s i rail valgono **+0,83 / −0,81 V**, le
stesse cifre di L41c a TE + 7,6 s.

## La catena, in due tempi (come L41c, `data/2026-09-26/L41c/README.md`)

1. **L'alimentatore** (`psu/`): il generatore, `corri_seq.sh`, `tutti_seq.sh`, `sano.py`,
   `confronta.py` copiati da L47c2a, i nove casi di L41c iterati fino al punto fisso col firmware
   di L47c2a come micro.
2. **Il ponte** (`ponte/estrai_ponte.py`, da L41c): rail e istanti dei contatti all'angolo peggiore
   del G6K.
3. **La scheda audio** (`deck/tb_v2_l41c.cir`): `genera_tb_v2_casopeggiore.py --matrice l41c`, senza
   celle e col contatto `BSERx` (ADR-063), 18 corse (nove casi e nove riferimenti).

## Cosa è cambiato rispetto a L41c, e perché

| File | Cambio |
|---|---|
| `psu/analizza_seq.py` | Quello di L47c2a, coi criteri di L41c **riportati** prima delle corse: `L41C`, `L41C_M`, `INFO`; **r41** (jack il più tardi ≤ guadagno il più presto) ed **s41** (jack prima che V+ scenda a 10,6 V) su ogni caso di L41c. In L41c si chiamavano r ed s: rinominati, perché il rilascio di L47c2a ha già una r. m esteso (40 ms per U503), p e q anche per U501, i, j, k, l per `spegnimento_l` (quelli di L47c2a: 20–25 ms dopo il pin); in `cf_nodelta` C3 e r41 **devono fallire** |
| `psu/corri_seq.sh` | **Il `--angolo min` ripristinato** per i casi `_min`: la copia di L47c2a l'aveva perso, e il generatore li rifiuta senza |
| `psu/tutti_seq.sh` | i nove casi di L41c |
| `psu/genera_tb_psu.py` | Il commento della fine di `spegnimento_l` (TE + 1,1 s, confermato). **I due casi di U503 col metodo trapezoidale e `gmin=1e-9`**: vedi «U503 e il metodo» |
| `ponte/estrai_ponte.py` | Via le correnti delle stringhe LED (`is`, `ip`); **via la finestra propria dello spegnimento** (T0 = TE + 5,4 s, t_ins = TE + 6,4 s era la sfumatura: con la fine a TE + 1,1 s sarebbe partita dopo i dati). Lo spegnimento prende la finestra dei guasti, t_ins 10 ms prima che il frontale si apra |
| `deck/controlla_deck.py` | Senza il controllo BILS/BILP (rifiutava il deck di oggi, provato in L47c2b1); tiene quello degli `alter` oltre 800 numeri (#36), e **rifiuta il ritorno** delle sorgenti delle stringhe LED. Provato sul deck di L46b, che le ha: rifiutato |
| `script/verifica_eventi.py` | Le colonne degli stati senza celle (`ina vplus vminus main_a mainc fixc1 fixc2`). Quello di L41c **salterebbe ogni riga** dei file di oggi (il controllo della larghezza) e stamperebbe 0 per ogni caso: una cifra piccola senza evento, in silenzio. Questa copia rifiuta un file senza righe della larghezza attesa |
| `script/verifica_partenza.py` | Quello di L47c2b1 chiede V+ = 15 V tondi a t = 0 (il rail disegnato a mano della matrice): qui i rail vengono dal ponte (+14,999735 / −15,052534 V) e **rifiutava tutte le 18 corse per questo solo motivo** (`corse/partenza_l47c2b1.txt`). Questa copia confronta il rail di partenza col primo punto del ponte del suo caso, entro 1 µV; il resto è uguale |
| `script/tabella.py` | Quella di L41c, criteri invariati |

## U503 e il metodo (`sonda_u503/`)

I due casi di U503 spento (`guasto_u503`, `guasto_u503_min`) **non finivano** il primo giro col
metodo gear degli altri deck delle sequenze: oltre 45 minuti al 100 % contro i ~2 minuti degli
altri casi. La sonda:

- il deck fermato a TE − 10 ms corre in 12,1 s, a TE + 20 ms in 12,5 s, a TE + 0,5 s in 17,1 s;
  fermato a TE + 0,55 s **non finisce**;
- a TE + 0,5 s la linea a 5 V del micro è a ~0,9 V e il suo dominio galleggia: le uscite del micro
  a ~1 V, `MUTE_G_IN` a 0,92 V, `ADC_MD` che oscilla (`tutte.py`). In L41c su quella linea c'erano
  i carichi del pilota delle LDR (U510, U511), tolti da ADR-062;
- tutto quello che i criteri e il ponte leggono succede prima: il jack a +15,7 / +18,7 ms, il
  guadagno a +35,9 ms, V+ sotto 10,6 V a +253 ms;
- varianti numeriche sul caso intero (fino a TE + 1 s): nominale, il trapezoidale corre in 24 s;
  all'angolo minimo il trapezoidale **non** finisce, il trapezoidale con `gmin=1e-9` sì (17 s), e
  anche con `reltol=1e-3` (15 s); gear con `rshunt=1e12` e gear col passo massimo di 5 µs non
  finiscono in 3 minuti;
- **la verifica** (`gear_contro_trap.txt` e le righe sotto): fino a TE + 0,5 s il trapezoidale
  dà le forme d'onda del gear. Gli istanti del jack, del guadagno e di V+ < 10,6 V sono gli stessi
  al passo di 0,1 ms, nominale e angolo minimo; i rail entro 0,54 mV.

**Scelto: trapezoidale con `gmin=1e-9` per i due casi di U503**, e per nessun altro. `gmin` è
1 nS attraverso ogni giunzione: 0,5 nA a 0,5 V, e da quando le stringhe LED non ci sono più
nessuna corrente della scheda è così piccola (in L41b2 il gear era servito per il DAC, tolto).
Il commento accanto ai due casi in `genera_tb_psu.py` lo dice.

## Come si rifà

Dalla radice del repo, coi percorsi assoluti:

```sh
/bin/zsh <L>/psu/tutti_seq.sh                       # i nove casi, ~5 min
/usr/bin/python3 <L>/ponte/estrai_ponte.py <L>/seq <L>/ponte spegnimento_l perdita perdita_min \
    guasto guasto_u501 guasto_u503 guasto_u503_min cf_nodelta corto_u503
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py \
    --matrice l41c --ponte <L>/ponte --uscita <L>/deck/tb_v2_l41c.cir
/usr/bin/python3 <L>/deck/controlla_deck.py <L>/deck/tb_v2_l41c.cir
/bin/zsh docs/preamp/data/2026-09-23/L29c/script/corri.sh <L>/corse <L>/deck/tb_v2_l41c.cir '_l41c$' 9
/usr/bin/python3 docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py <L>/corse
/usr/bin/python3 <L>/script/verifica_partenza.py <L>/corse <L>/ponte
/usr/bin/python3 docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py <L>/corse
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/script/analizza_par.py <L>/corse/manifest_ok.csv <L>/corse <L>/corse/analisi.csv 8
/usr/bin/python3 <L>/script/verifica_eventi.py <L>/corse <L>/ponte <casi>
/usr/bin/python3 <L>/script/tabella.py <L>/corse/analisi.csv <L>/corse/fallite.txt <L>/tabella.csv
/usr/bin/python3 <L>/script/confronta_tabelle.py
/bin/zsh <L>/script/regressione.sh dopo ; /usr/bin/python3 <L>/script/confronta_regressione.py
/bin/zsh firmware/preamp_timer/test/run_host_tests.sh --falsi <L>/falsi/esito.txt
```

Le forme d'onda (`seq/**/*_out.txt`, `corse/*.dat`) e i deck espansi sono in `.gitignore`.

## Le cifre

**L'alimentatore** (`seq/analisi_seq.txt`): **9 casi su 9** al punto fisso al giro 2, 0
sostituzioni; **VERDETTO: PASSA**.

| Caso | MUTE_CMD dopo l'evento | jack (tardi) | guadagno (presto) | V+ < 10,6 V |
|---|---|---|---|---|
| `spegnimento_l` | 21,2 ms dopo il pin | +31,3 ms | +68,1 ms | +313 ms |
| `perdita`, `_min` | 14,4 ms | +17,4 ms | +34,7 / +33,4 ms | +183 ms |
| `guasto` (U502) | 10,7 ms | — | — | — |
| `guasto_u501` | 10,1 ms | +13,1 ms | +30,4 ms | +34,8 ms |
| `guasto_u503`, `_min` | 15,7 / 15,3 ms | +18,7 / +18,3 ms | +35,9 / +34,3 ms | +253 ms |
| `cf_nodelta` | 14,4 ms | +17,4 ms | **+14,4 ms**: C3 e r41 falliscono, come devono | +183 ms |
| `corto_u503` (senza verdetto) | 0,1 ms | +3,1 ms | +0,1 ms | +183 ms |

(`guasto` è il caso di L41b2: L41c non gli dava r ed s, e così qui.)

**La scheda audio** (`tabella.csv`, `confronto.csv`): 18 corse su 18 passano la guardia, partono
dal punto giusto, e hanno il loro evento (`corse/eventi.txt`: MAIN_A si sposta di ≥ 0,09 V dopo il
cambio di guadagno in ogni caso). Picco al jack, dB SPL di picco a 1 m:

| Caso | L41c | L46b | **L47c2b2** | criterio |
|---|---|---|---|---|
| spegnimento morbido | 30,1 nV | 12,8 nV | **15,0 nV** (−43,0) | ≤ 100 µV |
| perdita di rete / angolo min | 0,12 / 0,18 µV | 0,08 / 0,09 µV | **0,05 / 0,09 µV** | ≤ 2 mV |
| U502 spento | 1,37 mV | 0,90 mV | **0,89 mV** (52,5) | ≤ 2 mV |
| U501 spento | 1,03 mV | 0,56 mV | **0,55 mV** (48,3) | ≤ 2 mV |
| U503 spento / angolo min | 75 / 75 nV | 75 / 75 nV | **52 / 15 nV** | ≤ 2 mV |
| controfattuale senza Δ | ≥ 66,5 mV (aborto) | 29,7 mV | **29,7 mV** (82,9) | deve superare 2 mV |
| corto della linea a 12 V | 69,4 mV | 29,7 mV | **29,7 mV** (82,9) | sotto il tetto 0,87 V (ADR-051) |

Tre cause di differenza da L46b, insieme: l'alimentatore senza il pilota e col firmware di L47c2a;
la scheda senza celle; il contatto in serie `BSERx` col fronte di 4,55 µs (ADR-063). I guasti che
contano (U502 e U501) restano entro l'1,5 % di L46b; gli altri sono ai nanovolt.

**La regressione**: i 21 deck veloci con rc 0; **248 file su 248 uguali** a
`L47c1/regressione/dopo` (`regressione/confronto.csv`), come atteso: da L47c1 il circuito audio e
i deck sono cambiati solo nei commenti. **Il firmware sull'host**: 76 controlli, 0 falliti;
**19 falsi su 19** (`falsi/esito.txt`).
