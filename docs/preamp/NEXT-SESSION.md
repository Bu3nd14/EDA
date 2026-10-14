# Prompt per la sessione successiva — L45d2, la decisione sui rimedi dei guasti

Nome della sessione: **hi-fi preamp L45d2** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. L45a il blocco di guadagno, L45b
i controlli, L45c1 i rail audio, L45c2 la linea dei relè e il comando. **L45d1 (fatto, 2026-10-14)**
ha riportato le prime tre tabelle alla forma di ADR-070 e le ha messe tutte e quattro in una sintesi.
L45d era stato diviso dall'utente all'inizio («Due parti»). **L45d2** è la seconda metà, e NC-042 si
chiude con lei.

## Il punto di partenza: il PDF delle scelte

**`docs/preamp/data/2026-10-14/L45d1/scelte_L45d2.pdf`** è il passo intermedio, versionato dopo L45d1
su richiesta dell'utente («teniamolo come step intermedio, così possiamo referenziarlo nelle
modifiche che applicheremo»). Le 156 righe ad alta e media priorità diventano **10 scelte
numerate** (118 righe); altre 38 non chiedono una scelta adesso. **Ogni ADR, commit e report di
questo lotto cita la scelta per numero** («scelta 5 di `scelte_L45d2.pdf`»), e il PDF non si
riscrive: se la numerazione deve cambiare, se ne fa uno nuovo accanto e lo si dice.

Il dettaglio sta nella sintesi: `docs/preamp/data/2026-10-14/L45d1/fmea_sintesi.md` (e `.csv`; il report è
`reports/2026-10-14-L45d1-riporto-fmea.md`). **469 modi: 96 a priorità alta, 60 media, 313 bassa.**
Le righe sono raggruppate per rimedio candidato. In testa:
- **un rivelatore di continua sulle uscite dei blocchi** che apra il mute: 52 righe alte e 6 medie
  del blocco. Oggi il blocco al rail porta 14,9 V al jack, sopra il tetto per 0,56–3,1 s. Col
  rivelatore ideale si scende a 0,2–10,1 ms, dentro P10 (ADR-069); il picco non cambia. In 21 di
  quelle righe c'è anche un secondo guasto per calore (in cima C145 in corto, R144 a 22,5 W);
- **l'autotest dei sorveglianti** (L45c2, 10 alte): oggi il firmware muta a 2,2 ms, fuori dalla sola
  clausola di 1 ms di P9 (b) quando a mutare è il firmware;
- **i corti del grezzo** (L45c1, 9 alte, gravità 5 sul rail negativo: U502 con l'uscita fino a
  1,76 V sopra l'ingresso, contro −0,3 V): accettarli (≤ 9,0 mV al jack) o rivedere D510 / D511;
- **i sovraccarichi del comando** (L45c2, 7 alte: i clamp D506 / D508 in corto, D505 o la bobina di
  K501 in corto) e **la sovratensione su V5** (U504 in corto ingresso-uscita);
- **il mute che non si inserisce**: Q501 in corto (L45c1), Q501 con gate e drain in corto (L45c2,
  0,27 V alla perdita di rete, il jack a 685 ms), **il NO di mute saldato** (L45c1, 4 alte; il LED
  rosso non lo vede);
- **l'isolamento fra bobina e contatti dei relè** (L45b: sul mute 12 V permanenti sul jack, anche a
  mute inserito);
- **il ritardo Δ perso** (L45c2, 45 modi, 6,44 mV): accettarlo come il corto della linea a 12 V
  (ADR-051) o un permesso indipendente da VRELAY e da `MUTE_G`; e i due latenti **a ogni mute**
  (D520 in corto, R524 aperta);
- **il filo del rail + fra le due schede** (L45c1: 13,3 V al jack, nessun mute);
- **le sovratensioni dei rail** che nessuno vede (L45c1, fino a ±20,3 V; le tensioni massime delle
  parti del blocco non sono mai state lette) e la presa centrale aperta;
- lo standby con VRELAY o il toroidale accesi (L45c2);
- **il tetto delle fisse** (con NC-046): nella sintesi non ha righe proprie.

**Due casi del «Da riaprire se» di ADR-070** da portare all'utente prima delle scelte:
1. l'isolamento dei relè di mute esce in **media** per la sola rarità (~0,25–0,75 FIT), mentre lo
   stesso modo sui relè del selettore e del trim esce in alta;
2. 28 guasti del blocco **dentro P10** escono in **media** per la sola latenza, senza rimedio candidato.

Ogni scelta prende la sua ADR. Dopo il rimedio si aggiungono la gravità, la probabilità e la priorità
(ADR-070). Se una scelta cambia il circuito: sorgente, netlist, disegno, `run_tests.sh`, regressione,
e i guasti toccati rifatti. **È ancora un lotto grande: all'inizio chiedi all'utente se dividerlo**
(per esempio prima le scelte che cambiano il circuito, poi le accettazioni dichiarate), per nome e
senza sigle.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (**58** voci), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di **L45d1**, L45c2, L45c1, L45b, L45a.
- `NONCOMPLIANCE.md`: NC-042, NC-046, NC-062.
- `scelte_L45d2.pdf`, il report di L45d1 e la sintesi; i quattro report di L45 per il dettaglio di
  una riga.
- `STATE.md`, la riga di **L58** nella tabella dei lotti.
- ADR-045, ADR-046, ADR-051, ADR-062, ADR-069, **ADR-070**.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script: `psu/corri_lista.sh`);
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che contiene la parola «git» anche solo
    in un testo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi.
- **Non modificare uno script mentre zsh lo sta eseguendo** (zsh lo legge a pezzi).
- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB SPL.
- Uno strumento di misura nuovo si controlla su un caso noto prima di usarlo.
- Per rifare la sintesi dopo un rimedio: `data/2026-10-14/L45d1/README.md` («Rifare»).

## NON fa parte di questo lotto

- L'ingresso protetto (L57), il riesame del micro e dello standby (L54: `MUTE_REQ` bloccata alta,
  Q502 in corto all'accensione, D522), il dispositivo d'uscita (L55), il moltiplicatore di Vbe
  (NC-062), G1. Se una scelta tocca uno di questi, si dice e si lascia al suo lotto.
- **La diagnosi, L58** (lotto nuovo, richiesta dell'utente dopo L45d1): i test point e l'autodiagnosi
  dei guasti latenti. Quando un rimedio è una diagnosi (l'autotest dei sorveglianti, il firmware che
  legge `MUTE_CMD` o il jack, il controllo di Δ a ogni mute), l'utente può sceglierlo qui e
  **mandarne la realizzazione a L58**; lo si scrive nella ADR.

## CHIUSURA

1. `STATE.md` con L45d2 (o le sue parti) **fatto** nella tabella dei lotti, e il prossimo.
2. Riscrivi QUESTO file per il lotto successivo, con la riga «Nome della sessione: hi-fi preamp
   <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh <lotto>`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
