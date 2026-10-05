# L47c2b1 — il mute coi soli relè: V2 senza celle, la matrice e il clic del taglio (2026-10-05)

Report: `../../../reports/2026-10-05-L47c2b1-v2-senza-celle.md`. Esegue ADR-062; **ADR-063**
nata qui (il residuo con la musica e il contatto in serie del banco: vedi «La sonda»).

L47c2b è stato diviso dall'utente all'inizio: **«Due parti»**. **L47c2b1** (questo) i deck V2
senza fotoresistenze e senza S, la matrice e il clic del taglio; **L47c2b2** la catena dei guasti
di L41c sull'alimentatore di L47c2a, i 21 deck veloci e il firmware sull'host.

## Cosa è cambiato nel banco

| File | Cambio |
|---|---|
| `data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py` | via le due celle, il loro comando, `VPWL`, `alter rsrc` (la sorgente torna sulla `RSRC` del blocco, come L40); i tempi del firmware di L47c2a (contatto 24 ms dopo il tasto); `conta` da `S_*` a `C2_*` dichiarati; via `mnorele`/`rele_contro_norele`; via le matrici `l29c` e `curve` (rifiutano, col commit `dffa7148`); `clic()`: i 20 kHz a 100 k e i tre toni a 10 k; `l41c` senza le correnti dei LED |
| `spice/preamp/tb/tb_v2_casopeggiore.cir` | rigenerato: **145 corse** (135 di L47b2b1 − 2 `mnorele` + 12 del clic) |
| `data/2026-09-22/L29b2/deck/genera_tb_v2_mute_taglio.py` | era `genera_tb_v2_mute_ldr.py` (`git mv`): senza celle, `norele`, inversioni; 30 corse |
| `spice/preamp/tb/tb_v2_mute_taglio.cir` | era `tb_v2_mute_ldr.cir` (`git mv`) |
| `scripts/v2_metodo.py` | S tolto (costanti, `ampiezza`, `salto_db`, T15–T19, due sabotaggi); C2 è il clic del taglio, dichiarato. `autotest` **23 controlli, 0 caduti** (erano 30); `sabotaggi` **12 su 12** |

**I tempi** (`analisi_seq.txt` di L47c2a): il tasto a t_ins; `MUTE_CMD` 21 ms dopo (21,10 misurati
al rilascio); il contatto in serie 3 ms dopo (rilascio/intervento massimo del G6K); la derivazione
lato condensatore 1 ms dopo ancora (geometria iii). `t_ins`/`t_rel` del manifesto sono il tasto,
`t_grad` = 24 ms. Il cambio di guadagno e di trim sotto mute a contatto + 0,5 s, oltre Δ.

## La prima matrice e la sonda (`matrice_interruttore/`, `sonda/`)

La prima matrice (`matrice_interruttore/`, contatto in serie = interruttore nativo ideale) ha dato
**34 corse fermate su 145** su «Timestep too small»: tutte quelle con la musica dove il contatto
in serie si muove (più 4 `off_`, escluse comunque). Il log accusa il JFET d'ingresso del blocco A;
le forme d'onda dicono altro. La sonda (`sonda/`, README nei docstring degli script):

| Variante | Cosa | `mev_20_iii` | `mev_1k_iii` |
|---|---|---|---|
| `t1`, `t1r`, `gear` | `trtol=1`; `+ rshunt=1e12`; `method=gear` | ferma a 1,0244 s | ferma a 1,0244 s |
| `c100` | cavo al jack 100 pF | ferma a 1,0244 s | ferma a 1,0244 s |
| `nb` | l'apertura della serie senza rimbalzo | **corre** | ferma a 2,025 s |
| `bser` | la serie = `BSERx` del blocco, fronte ~4,55 µs | **corre** | **corre** |

1,0244 s è il rimbalzo che **richiude** la serie 400 µs dopo l'apertura: il lato condensatore a
−12,02 V, il jack a −3 µV. 2,025 s è la chiusura del rilascio. L'interruttore ideale si ferma ogni
volta che chiude su volt di musica. `bser` contro `nb` su `mev_20_iii`: C2 all'inserimento 9,015 /
8,939 V, al rilascio 0,4723 / 0,4728 V, B2 0,732 / 0,700 V; senza segnale (`mev_lz_iii`) tutto al
pavimento (~10⁻¹¹ V) contro la matrice.

**Trovato con la sonda**: con la musica B2 misura il taglio. `sonda/b2_ideale.py` su `bser`
`mev_20_iii`: sulla principale B2 0,732 V, lo stesso metodo sul taglio ideale 0,698 V, il jack
grezzo nella finestra **4,3 µV**, il riferimento sempre in mute 0,45 nV.

**Scelte dell'utente** (per nome, in dB SPL): **«Musica che passa davvero»** (con la musica il
verdetto è sul jack grezzo, `B2g`, e sul riferimento sempre in mute, B1; B2 filtrato va col clic) e
**«Tutta la matrice»** (il contatto in serie `BSERx` in tutte le 145 corse). **ADR-063**.
`v2_metodo.py`: `b_grezzo`, `B2g` in `analizza`, T15 e il sabotaggio `b_grezzo_filtrato` (24
controlli, 13 sabotaggi su 13).

## I criteri, scritti prima delle corse della matrice

- **A senza segnale ≤ 100 µV** di picco su ogni uscita (ADR-032): cambi di guadagno e di trim
  sotto mute (gruppi 1, 2), dispersione (3), mute senza segnale (4), accensione (5). Una A con
  finestra corta non accetta.
- **B2 ≤ 100 µV** senza segnale. **Con la musica** (ADR-063, criterio rivisto dopo la prima
  matrice e prima della seconda): **B2g** (il jack grezzo) **e B1** del riferimento sempre in mute
  ≤ 100 µV, ai tre toni dove ci sono; B2 filtrato dichiarato col clic. È **NC-053** (con la
  NSL-32SR3 B2 a 20 Hz valeva 100,5–241,2 µV, la musica lasciata dalla cella prima del relè): si
  chiude se regge su tutte le uscite.
- **Il clic del taglio (C2)**: nessuna soglia (ADR-062). Tabella intera, 18 valori, in picco e in
  dB SPL a 1 m, il peggiore in cima, **accanto al taglio ideale** allo stesso istante.
- Escluse dal verdetto le 24 corse `off_` (lo spegnimento brusco di L29c), come in L29d2 e
  L47b2b1: lo spegnimento vero è quello morbido dell'alimentatore (L30, L41c, L47c2b2).
- **Il controfattuale prima di tutto**: `--matrice controfattuale` (tutte le aggiunte del banco
  in posizione neutra, geometria N) contro la stessa cella di `tb_v2_mute_taglio.cir` (1 kHz,
  100 k). Le grandezze devono coincidere entro lo 0,09 % di L29c (o entro il pavimento numerico
  dove la cifra è al pavimento); se non coincidono, la matrice non vale.
- Ogni corsa passa `guardia_v2.py` di L47b2b1 (#35, #36, #42) e `corri.sh` (#33).

## Le cartelle

| Cartella | Cosa |
|---|---|
| `controfattuale/` | `cf.cir` (generato), `corse/` le 7 corse, `analisi.csv` |
| `taglio/v2_1k_100k/` | la cella a 1 kHz e 100 k di `tb_v2_mute_taglio.cir` (7 corse), `analisi.csv` |
| `matrice_interruttore/` | la prima matrice, superata: `tempi.txt` e i log dicono le 34 fermate |
| `sonda/` | le varianti di convergenza e di contatto, `b2_ideale.py` |
| `matrice/` | le 145 corse del deck versionato col contatto `BSERx` (ADR-063); `analisi.csv`, `verdetto.csv`, `clic.csv` |
| `script/` | `verdetto.py` (da L29c, senza S, C2 dichiarato), `tabella_clic.py`, `verifica_partenza.py` (da L29c, con le colonne degli stati senza le celle: quello di L29c le leggerebbe per posizione, sbagliate, senza errore) |

Le forme d'onda (`*.dat`) e i deck espansi (`corsa_*.cir`, `deck.cir`) sono in `.gitignore`: si
rifanno correndo.

## Per rieseguire (percorsi assoluti; `<L>` = `docs/preamp/data/2026-10-05/L47c2b1`, `<C>` = `docs/preamp/data/2026-09-23/L29c`)

```
/usr/bin/python3 scripts/v2_metodo.py sabotaggi
/usr/bin/python3 <C>/deck/genera_tb_v2_casopeggiore.py
/usr/bin/python3 <C>/deck/genera_tb_v2_casopeggiore.py --matrice controfattuale --uscita <L>/controfattuale/cf.cir
/usr/bin/python3 docs/preamp/data/2026-09-22/L29b2/deck/genera_tb_v2_mute_taglio.py
/bin/zsh <C>/script/corri.sh <L>/controfattuale/corse <L>/controfattuale/cf.cir '.*' 5
/bin/zsh <C>/script/corri.sh <L>/taglio/v2_1k_100k spice/preamp/tb/tb_v2_mute_taglio.cir '^([a-z]+_1k_100k|lz[a-z]+_100k)$' 5
/bin/zsh <C>/script/corri.sh <L>/matrice spice/preamp/tb/tb_v2_casopeggiore.cir '.*' 8
/usr/bin/python3 docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py <cartella>
/usr/bin/python3 <L>/script/verifica_partenza.py <cartella>      # colonne nuove degli stati
/usr/bin/python3 <C>/script/analizza_par.py <cartella>/manifest_sel.csv <cartella> <cartella>/analisi.csv 8
/usr/bin/python3 <C>/script/confronta_analisi.py <L>/taglio/v2_1k_100k/analisi.csv <L>/controfattuale/corse/analisi.csv
/usr/bin/python3 <L>/script/verdetto.py <L>/matrice/manifest_sel.csv <L>/matrice/analisi.csv <L>/matrice/verdetto.csv
/usr/bin/python3 <L>/script/tabella_clic.py <L>/matrice/manifest_sel.csv <L>/matrice <L>/matrice/analisi.csv <L>/matrice/clic.csv
```
