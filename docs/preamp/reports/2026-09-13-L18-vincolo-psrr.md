# L18 — il vincolo PSRR scritto dove verrà letto

Data: 2026-09-13 · Lotto: **L18** (XS/S) · Tocca: **NC-011** (maggiore), metà
scritta. Il rimedio e la verifica restano al lotto dell'alimentatore.

**Il difetto.** Il PSRR del rail + era pubblicato, ma non vincolava nessuno:
nessun documento diceva all'alimentatore quanto ripple può lasciare sui rail.
In questo lotto **nessun valore del circuito è cambiato**. Un commento di
`gain_block.py` è stato aggiornato, con AST identico (§6).

## 1. Qualcuno aveva già deciso? Sì, a mezza voce

```sh
grep -rn -i "ripple\|ronzio\|psrr" docs circuits/preamp/*.py AGENTS.md .claude/agents
```

Stessa quota in due posti, dallo stesso commit `d9ca07f` del 2026-09-08:
- `circuits/preamp/gain_block.py:571-572`: «V+ ripple at 100 Hz must be
  <= 1 mV pk for the rail contribution to stay under **1 uV at the output**
  in +10 dB mode»;
- `reports/2026-09-08-fase2-bozza-topologia.md:170-174`: «≤ 1 mV picco di
  ripple a 100 Hz su V+ e ≤ 30 µV di rumore a banda larga sopra 10 kHz».

È una ripartizione di **1 µV** del budget di E5, ma non era un requisito. Ha
tre limiti: sta in un commento e in un report datato, usa cifre del THAT320,
e mescola picco e RMS su due sole bande. ADR-010 e ADR-015 parlano
dell'alimentatore (telaio unico, ronzio come rischio numero uno, ±15 V e
calore) ma non del ripple. **L18 rende vincolo quella quota e non ne inventa
un'altra.** Nessuna voce nuova aperta.

## 2. Le cifre, rilette dalla topologia di oggi

```sh
/bin/zsh scripts/run_simulation.sh spice/preamp/tb/tb_zout_psrr_noise.cir $CLAUDE_JOB_DIR/tmp/l18/tb_zout_psrr_noise
```

**Il deck ha letto il circuito del worktree, e ci sono due prove.**
- `run_simulation.sh` stampa «resolved against …/worktrees/L18-vincolo-psrr»,
  e le tre `.include` risolte puntano lì.
- La riga WORST CASE del rumore dà **4,230582 µV**, cioè la cifra LS352 di
  `data/2026-09-10/`, non 5,697 µV (THAT320). Questo è un controllo che poteva
  fallire, ed è indipendente dal PSRR.

**Lo scarto rispetto a `data/2026-09-09/`.** Confronto in python su 16 `meas`
e su 81 punti × 4 CSV, a griglia identica:

| Curva | max \|Δ\| sugli 81 punti | dove | Δ medio |
|---|---|---|---|
| PSRR+ 0 dB | 0,105 dB | 25,2 Hz | +0,071 |
| PSRR+ +10 dB | 0,107 dB | 25,2 Hz | +0,070 |
| PSRR− 0 dB | **4,739 dB** | 20 Hz | −2,258 |
| PSRR− +10 dB | **4,739 dB** | 20 Hz | −2,260 |

- **Rail + praticamente fermo**: a 10 kHz, +10 dB, 29,76 → **29,82 dB**.
- **Rail − peggiorato** in bassa frequenza: a 100 Hz, +10 dB, 79,02 →
  **74,37 dB**. È coerente con uno specchio diverso sul lato che non è il
  rail +, ma la causa **non è stata inseguita**: non serve al vincolo, che
  include comunque il rail −.
- **Zout** cambia di meno dello 0,6% (za100k a +10 dB: 4,9945 → 4,97282).

La tabella completa è in `data/2026-09-13/README.md`, dove sono versionati il
log e i 4 CSV PSRR. **Il vincolo è scritto sulle cifre nuove.**

## 3. Dove, col criterio di L15: ADR più nota

Il criterio: una modifica ai requisiti è sostanziale se **cambia l'insieme
dei progetti conformi**. Una quota fissa per il ripple lo cambia. Un progetto
con 5 µV di rumore e 5 µV di ripple somma 7,07 µV e passa E5; con la quota a
1 µV non passa. **Sostanziale, quindi ADR-020**, scritta secondo TEMPLATE e
con la sola riga 020 aggiunta all'indice.

La conseguenza operativa va però letta da chi progetta l'alimentatore, cioè
accanto a E5 ed E7. Da qui la **«Nota su E5 — la quota del ripple
d'alimentazione»** in `REQUIREMENTS.md` e il rimando nelle due righe. Nessuna
aggiunta in coda ad ADR-010 o ADR-015 (§2 di L15).

Una quota fissa, e non «quel che avanza», perché il rumore del circuito non è
noto: 4,231 µV è un pavimento senza 1/f (NC-004).

## 4. Il verbo, e il controllo fatto fallire

√( Σ_rail Σ_k [V_rail,k · 10^(−PSRR_rail(f_k)/20)]² ) ≤ 1 µV, con k in
20 Hz–20 kHz e PSRR minimo fra le modalità.

Script in `$CLAUDE_JOB_DIR/tmp/l18/budget.py`, non versionato: è aritmetica
sui CSV versionati, e la verifica vera spetta al lotto dell'alimentatore. Il
PSRR è interpolato in log f.

| Caso | V_out | Esito | Atteso |
|---|---|---|---|
| (a) precedente Fase 2: 1 mV pk a 100 Hz, rail + | 0,551 µV | passa | — |
| (a2) precedente Fase 2: 30 µV come tono a 10 kHz, rail + | 0,968 µV | passa | — |
| (b) 1 mV RMS a 10 kHz, rail + | 32,278 µV | **fallisce** | fallisce |
| (c) 1 mV RMS a 10 kHz, rail − | 0,049 µV | passa | passa |
| (d0) 0,5 mV RMS a 1 kHz, rail +, PSRR minimo | 1,653 µV | **fallisce** | fallisce |
| (d1) stesso tono, PSRR della sola modalità 0 dB | 0,525 µV | passa | passa |
| (f) 100 mV RMS a 100 kHz, rail + | 0 (fuori banda) | passa | passa |

- **(d0)/(d1)** prova che la clausola «minimo fra le modalità» serve: senza,
  il tono passerebbe a torto.
- **(f)** prova che il verbo è cieco sopra 20 kHz, e l'ADR lo dichiara.
- **Con l'aspettativa invertita su (b)** lo script segnala l'errore ed esce 1.

**Il controllo ha fermato anche un errore di chi lo scriveva.** La prima
versione di (d) usava 1,2 mV pk a 100 Hz più 20 µV a 10 kHz. Quello spettro
dà 0,924 µV e **passa anche a +10 dB**, quindi non poteva provare niente. Lo
script l'ha segnalato («ATTESA DISATTESA») ed è stato sostituito dal tono a
1 kHz.

**Tabella derivata.** Ripple massimo se tutta la quota cade su un tono, a
+10 dB, la modalità peggiore su tutti gli 81 punti di entrambi i rail:

| f | PSRR+ | V+ max | PSRR− | V− max |
|---|---|---|---|---|
| 50 Hz | 62,76 | 1,3748 mV RMS | 69,51 | 2,990 mV |
| 100 Hz | 62,17 | 1,2832 mV RMS | 74,37 | 5,231 mV |
| 1 kHz | 49,62 | 0,3025 mV | 87,75 | 24,412 mV |
| 10 kHz | 29,82 | 0,0310 mV | 86,23 | 20,498 mV |
| 20 kHz | 23,81 | 0,0155 mV | 81,91 | 12,461 mV |

Densità bianca massima su 20 Hz–20 kHz: **189,9 nV/√Hz** sul rail + e
119,9 µV/√Hz sul rail −.

## 5. La metà che non è di L18

NC-011 chiede anche la **scelta del rimedio**: regolatore a bassissimo rumore,
oppure moltiplicatore di capacità per gli stadi d'ingresso. Non è di L18. La
scelta vuole i numeri di un alimentatore che non esiste: dropout disponibile
sotto ±15 V (ADR-015), dissipazione in un telaio chiuso (ADR-010), spettro di
rumore del regolatore. Il mandato esclude di progettarlo.

Lo stesso vale per il **limite sopra 20 kHz**: a 100 kHz il PSRR+ vale
10,20 dB, e E5 non può dare un numero lì. **NC-011 resta aperta**, come NC-005
dopo L15. Conteggi invariati: **19 voci aperte, 6 bloccanti.**

## 6. Cosa è cambiato

| File | Modifica |
|---|---|
| `decisions/ADR-020-quota-ripple-alimentazione.md` | nuova |
| `decisions/README.md` | solo la riga 020 |
| `REQUIREMENTS.md` | righe E5 ed E7, Nota su E5 — la quota del ripple, data |
| `NONCOMPLIANCE.md` | NC-011: stato, evidenza rimisurata, chiusura parziale; intestazione |
| `data/2026-09-13/` | log + 4 CSV PSRR, sezione L18 del README |
| `circuits/preamp/gain_block.py` 563-572 | commento: cifre PSRR LS352, rimando ad ADR-020 |
| `STATE.md`, `NEXT-SESSION.md` | L18 fatto, prossimo L11 |

**`gain_block.py` non cambia codice**, verificato con il metodo di L14.
- `ast.dump` identico fra HEAD e il file nuovo, 648 righe contro 648, quindi i
  `SKiDL Line` delle netlist restano veri.
- Il controllo è stato fatto fallire: una copia con `6.81k` → `6.82k` risulta
  diversa.

## 7. Visto e non corretto

- **Il dossier** ha `DATA_DATE = "2026-09-09"` cablato
  (`dossier/build_dossier.py:32`), quindi pubblica ancora il PSRR col THAT320.
  Va con la rigenerazione del dossier.
- **`docs/preamp/schematic/gain_block_draw.py:468`** scrive «V+ e' il rail
  debole per il PSRR (59,5 dB a 1 kHz)»: oggi è 59,57. Lo scarto è di un
  decimo e il disegno non è stato rigenerato.
- **La causa del peggioramento del PSRR− in bassa frequenza** dopo L22 non è
  stata cercata.
- **Il limite di Fase 2 «30 µV sopra 10 kHz»** è a banda larga, e solo come
  tono a 10 kHz sta sotto quota (0,968 µV). Su una banda 10–20 kHz, dove il
  PSRR+ scende a 23,81 dB, andrebbe integrato: ADR-020 lo sostituisce, e il
  numero non è più il riferimento.
