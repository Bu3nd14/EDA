# Prompt per la sessione successiva — L45d2b2b, i diodi della tenuta, il regolatore negativo, il comando e i 5 V

Nome della sessione: **hi-fi preamp L45d2b2b** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura della prima parte di L45d2b2 (2026-10-20), dal prompt di L45d2b2 di
> L62b. L45d2b2 è stato diviso dall'utente in tre («Tre parti»): la partenza morbida (fatta, ADR-091,
> NC-063 chiusa), **questa**, e i massimi del blocco (L45d2b2c, prompt in
> `data/2026-10-20/L45d2b2a/NEXT-SESSION-L45d2b2c.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b2b**, e si ferma. Non iniziarne un secondo, salvo che
l'utente lo chieda esplicitamente nella sessione. Se L45d2b2b si rivela più grande di una sessione,
**dividilo con l'utente all'inizio**.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. L45d2a ha deciso i rimedi
(ADR-071…078); L45d2b li costruisce:
- L45d2b1 (il rivelatore, poi tolto da ADR-081);
- **L45d2b2** in tre parti: a) la partenza morbida (fatta), **b) questa**, c) i massimi;
- L45d2b3, i guasti rifatti nella forma di ADR-070 e la sintesi.

**Che cosa è cambiato con la prima parte (2026-10-20)**:
- **C507 4,7 µF e C508 470 nF** (ADR-091): i rail salgono insieme in ~0,6 s, MUSICA a 0,72 s;
- **R550 / R551, 4,7 Ω** fra il serbatoio e l'ingresso di U501 / U502 (ADR-092, per il calore a
  regime, **NC-072**). Sul lato del piedino, `RAW_PR` / `RAW_MR`, stanno l'ingresso, l'abilitazione,
  C509 / C510 e **D510 / D511**. È il lato grezzo che ADR-074 tratta: in un corto del serbatoio la
  tenuta si scarica nel corto **attraverso 4,7 Ω**, non più direttamente. ADR-092 lo dice nel suo
  «Da riaprire se»;
- **un banco dell'alimentatore nuovo**: `data/2026-10-20/L45d2b2a/psu/` (README). Senza il
  rivelatore, con K3 IM06TS, la partenza morbida, i condensatori della scheda audio sui rail
  (`--cap-audio`), il carico di oggi e le misure a regime; `modi.py` senza i casi del rivelatore.
  `corri_seq.sh <caso> <etichetta> [opzioni]`. Si parte da lì;
- la lettura dei diodi di ADR-090 è fatta («Conta il limite in mA»): non si riapre.

## Che cosa costruire

Il punto di partenza è `docs/preamp/data/2026-10-14/L45d2a/decisioni.csv`. Ogni ADR, commit e report
cita la scelta per numero di `data/2026-10-14/L45d1/scelte_L45d2.pdf`, che non si riscrive.

1. **D510 / D511 rivisti e U502 protetto** dall'uscita sopra l'ingresso (ADR-074; scelta 3).
   - Senza R551, U502 arrivava fino a 1,76 V sopra l'ingresso, contro un massimo di −0,3 V
     (SBVS169D). **Prima di tutto si rifà quella misura sul circuito di oggi**: con R550 / R551 e
     D510 / D511 sul lato del piedino il quadro può essere diverso. I casi sono quelli di L45c1 per
     le righe di ADR-074 (C501, C502, C509, C510, D501 in corto, l'ingresso di un regolatore a
     massa), sul banco nuovo.
   - Va verificato che i colpi al jack non crescano, e che la tenuta di P9 (b) regga ancora (i ≥ 25 ms
     di `VRELAY` e i ≥ 1500 µF effettivi). Se non regge: «Da riaprire se» di ADR-074, si torna
     all'utente coi due numeri.
2. **Il limite di corrente sul comando** (oggi ~1 A in un 2N7002 col corto di un clamp) e **il
   limitatore sulla linea a 5 V**, uno zener o un TVS con fusibile ripristinabile (ADR-075; scelta 4).
   - Il limite non deve rallentare lo stacco del jack né Δ.

**Ogni opzione portata all'utente** arriva già con la sua cifra contro il limite della parte (Tj a
60 °C d'aria, corrente, tensione), alle tre reti.

Ogni cambio al circuito porta con sé sorgente, netlist, disegno, `run_tests.sh` e regressione. Ogni
valore nuovo in `circuits/preamp/*.py` ha un commento che punta alla sua ADR. Uno strumento di
misura nuovo si controlla su un caso noto prima di usarlo.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#65** e **#66**, nuove), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L45d2b2a, L62b, L60d2, L60c2, L60b, L45d2b1.
- `NONCOMPLIANCE.md`: NC-042 (l'avanzamento di L45d2b2a), **NC-072**.
- ADR-074, ADR-075, ADR-091, ADR-092, ADR-046, ADR-048, ADR-070.
- `reports/2026-10-20-L45d2b2a-partenza-morbida.md`; `data/2026-10-20/L45d2b2a/README.md`.
- I casi di L45c1 e L45c2 (`data/2026-10-13/L45c1/`, `data/2026-10-14/L45c2/`) per le righe di
  ADR-074 e ADR-075.
- `circuits/preamp/psu.py` (U501, U502, R550, R551, D510 / D511, U503, U504, Q501–Q503 coi clamp) e
  `firmware/preamp_timer/spec/timer_spec.md`.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script);
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, gli script lunghi passati sulla riga di comando (scriverli
    su file e lanciarli);
  - `sed` con un valore calcolato al momento (si scrive uno script);
  - un comando che nomina la storia del repository in forma che il guardiano non sa verificare;
  - `pkill -f` col percorso relativo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi.
- **Non modificare uno script mentre zsh lo sta eseguendo** (zsh lo legge a pezzi).
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito.
- Le domande all'utente si fanno per nome, senza sigle; i colpi al jack in dB SPL.
- Il banco della rete con la partenza morbida usa il gear (il trapezio si ferma a 0,900 s). Un PWL in
  un `alter` sta sotto ~100 numeri (limitations #66).
- Piste larghe al layout: un rimedio che aggiunge parti di potenza lo ricordi.

## NON fa parte di questo lotto

- **I massimi del blocco** (ADR-078): sono di **L45d2b2c**.
- **I guasti rifatti nella forma di ADR-070** e la sintesi: sono di **L45d2b3** (con loro R144 contro
  la sua parte, R153 in corto, le durate di P10 sulla Stax).
- **Il rame sotto i regolatori** (NC-072): al layout dell'alimentatore, G2.
- La diagnosi (L58), l'ingresso protetto (L57), il riesame del micro e dello standby (L54), il
  dispositivo d'uscita (L55), il tetto delle fisse (NC-046), G1.
- Le decisioni prese in L45d2a, L60a…L60d, L62 e L45d2b2a non si riaprono, salvo che un «Da riaprire
  se» della loro ADR scatti. In quel caso si torna all'utente con i numeri.

## CHIUSURA

1. `STATE.md` con L45d2b2b **fatto** nella tabella dei lotti, e il prossimo (L45d2b2c).
2. Riscrivi QUESTO file per il lotto successivo (dal prompt messo da parte di L45d2b2c), con la riga
   «Nome della sessione: hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45d2b2b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
