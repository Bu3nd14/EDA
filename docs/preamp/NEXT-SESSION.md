# Prompt per la sessione successiva — L54b3b, le tolleranze e la temperatura del temporizzatore

Nome della sessione: **hi-fi preamp L54b3b** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura della prima parte di L54b3 (2026-10-28). L54b3 è stato diviso
> dall'utente all'inizio, «Due parti»: la prima (i modelli del costruttore, la rete sporca, i fronti
> veloci, i rimbalzi, a 25 °C) è fatta; questa è la seconda. L'ordine deciso con l'utente: L54b3b → L55 →
> L58 → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L54b3b**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Dove siamo

Il temporizzatore di ADR-102 è nel sorgente (`circuits/preamp/psu.py`, U513–U515, la ritenuta Q513 /
Q514, R585 di ADR-103) con **ADR-104**: D535 / D541 (su AT_T2S, 2,7 MΩ) e D536 (su AT_PGT) sono BAS416 a
bassa perdita, R571 1 MΩ; i cali lenti di rete che portano i regolatori fuori regolazione lasciano
scattare la ritenuta (scelta dell'utente, «Lasciare com'è»). Il banco è
`data/2026-10-28/L54b3a/psu/genera_tb_psu.py` (README della cartella): `--timer sorgente --comparatore
tarato`, e coi modelli del costruttore **`--ritenuta costruttore --bat54 costruttore`** (BC847B / BC857B /
BAT54 di Diodes Inc., `models/`); il BAS416 è sul banco il modello BAV199 di Diodes Inc. (dichiarato). Le
opzioni di quel banco: `--rete-forma`, `--disturbo nodo:…`, `--rimbalzo`, `--durata`, `--passo-max`,
`--sonde-piu` (la base della ritenuta e tre `.meas`), `--valore`, `--qualifica`, `--bassa-perdita`;
l'analisi `psu/analizza_rob.py`; il confronto con la lista della sicurezza `psu/confronta_serie.sh`. Le
serie `n_` (la lista della sicurezza di L54b2 sul sorgente di oggi, coi modelli del costruttore:
`an_n_seq.csv`, `an_n_fmea.csv`) sono **il caso nominale** da cui partire: non si rifanno.

## Che cosa fare

Il punto 7 del prompt di L54b (richiesta dell'utente dopo L54a, 2026-10-26), parola per parola; la prima
parte ha fatto la rete, i fronti veloci e i rimbalzi, questa fa **le tolleranze e la temperatura**:

> 7. **La robustezza del temporizzatore, al banco e non al prototipo** (richiesta dell'utente dopo L54a,
>    2026-10-26: «il prototipo è molto costoso, dobbiamo cercare di accorgerci al banco delle simulazioni
>    dei problemi, il primo prototipo deve essere usabile»; ADR-102 lasciava al prototipo l'immunità ai
>    disturbi). I criteri si scrivono prima delle corse; per ognuno: niente scatto a vuoto
>    dell'accensione, del mute o della ritenuta, e lo scatto quando deve:
>    - **la rete**: cali lenti (brown-out) a −15 / −20 / −30 % per 0,1–2 s; buchi di ½, 1, 3, 10 periodi;
>      una sovratensione +15 %; la rete che torna mentre i rail scendono; tutto alle tre reti;
>    - **i disturbi veloci**: fronti ripidi su `VRELAY_REG` e su V5 (K501 che chiude, i relè della scheda
>      audio che commutano, il carico di `VRELAY` a gradino): la ritenuta a due transistor non si innesca
>      da sola; il suo 1 nF base-emettitore dimensionato coi numeri, non a sentimento;
>    - **i rimbalzi** del frontale e di SW3 con forme di rimbalzo vere (treni di 1–5 ms);
>    - **le tolleranze**: un Monte Carlo sugli RC dei ritardi (resistenze ±1 %, condensatori secondo il
>      dielettrico, ±5 % C0G / ±20 % X7R con la tensione) e sulle soglie e gli offset dei comparatori:
>      ogni tempo nei suoi limiti (il permissivo ≥ 16,9 ms dopo il mute, la musica ≥ 500 ms dopo la
>      rete, K501 ≥ 50 ms dopo il permissivo, il timeout ~2 s, la ritenuta armata), col caso peggiore
>      dichiarato;
>    - **la temperatura** a 0 e 60 °C, coi transistor della ritenuta e i comparatori del costruttore;
>    - al prototipo resta solo ciò che non si simula (i disturbi irradiati, il layout), detto per nome.
>    Se una prova fallisce, il rimedio si porta all'utente coi numeri prima di cambiare il circuito.

«I comparatori del costruttore» sono, per ADR-103, il tarato `CMPTA` (non ha temperatura: lo scostamento
e la sua deriva si prendono dal datasheet SBOS589D e si mettono come parametri per canale). Il banco ha
`temp=25` fisso: serve un'opzione `--temp`, e va detto che cosa segue la temperatura (i modelli di Diodes
Inc. sì: XTB, EG, XTI; i regolatori e il riferimento comportamentali no). In più, dalla prima parte:

- **la perdita dei diodi a 60 °C** sui nodi ad alta impedenza: AT_PRT (4,7 MΩ / 10 nF, **D538 1N4148**:
  la sua perdita a 60 °C accorcia il ritardo del permissivo, C3), AT_T2S e AT_PGT coi BAS416, e i BAT54
  rimasti (D533, D534, D537, su nodi da ≤ 200 kΩ); la perdita del BAT54 del modello è ~3,4 volte la
  tipica e cresce ~9,5 volte da 25 a 60 °C (`data/2026-10-28/L54b3a/modelli.md`): con la perdita
  **massima** del datasheet, non la tipica (limitations #79);
- **la musica dopo un buco di 20 ms**: 559 ms a 25 °C, il margine di ADR-104 (≥ 500) sotto le tolleranze
  e la temperatura (il «Da riaprire se» di ADR-104);
- **i gruppi di hFE** (BC847A/C, BC857A/C sono in `models/`) e la VBE del BC847B del modello (708 mV a
  2 mA, oltre il massimo di 700 del datasheet);
- **l'accensione a freddo col frontale acceso** col tarato a 2,2 V (`--comparatore tarato22`): la base
  di Q513 ≤ 0,45 V anche a 60 °C e col Monte Carlo (il «Da riaprire se» di ADR-103);
- **la perdita di rete a −10 %**: i regolatori escono di regolazione 2,4 ms prima dello stacco del jack
  (+4,4 dB SPL, L54b2): le tolleranze non devono farlo crescere oltre il criterio.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#75**, **#77**, **#78**, **#79**, **#80**),
  `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce della prima parte di L54b3.
- **ADR-102**, **ADR-103**, **ADR-104**; il report `reports/2026-10-28-L54b3a-robustezza-rete-fronti-
  rimbalzi.md`; i README di `data/2026-10-28/L54b3a/` e `data/2026-10-28/L54b2/`.

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti, le pipe o i `;` attorno a comandi che eseguono
  script; `cd … && script`; le variabili di shell nei percorsi e nei cicli; `xargs` sulla riga di
  comando; `awk` con programmi, heredoc, `python3 -c`, script lunghi sulla riga di comando (scriverli
  su file); `sed` con valori calcolati; un titolo di PR con l'apostrofo (il corpo su file,
  `--body-file`); un `git` con `-C` dentro un comando composto. Comandi semplici, **percorsi
  assoluti**, script scritti con Write, Edit per i testi.
- Le corse: la memoria (limitations #75) decide il parallelo (una corsa coi modelli del costruttore è
  ~0,45 GB e 15–40 s; sei in parallelo hanno retto); commit e push prima di una lista lunga. **Le forme
  d'onda non si committano e `.gitignore` non le esclude**: `git add … ":(exclude)*_out.txt"`. Un Monte
  Carlo di centinaia di corse cancella le forme d'onda dopo l'analisi.
- Un disturbo o un parametro nuovo si prova prima su un caso di cui si sa la risposta, e ogni corsa
  deve poter mostrare che il disturbo è arrivato (la lezione dei fronti, limitations #80).
- Le domande all'utente si fanno per nome, senza sigle (al più fra parentesi); i colpi al jack in dB
  SPL; ogni opzione con la sua cifra contro il limite della parte, alle tre reti dove la rete conta.
  **Le cifre di una domanda si ricontano dai CSV prima di farla** (nella prima parte una domanda ha
  portato 16 invece di 14).

## NON fa parte di questo lotto

- Le righe della FMEA delle parti nuove (R585, i BAS416) e la diagnosi in hardware (ADR-076, ADR-078):
  L58. La conferma del BAS416 alla distinta: L58.
- Il dispositivo d'uscita (L55), il dossier (L64), la revisione (L65), G1.
- I cali lenti di rete (ADR-104, «Lasciare com'è») e lo standby (ADR-103) non si riaprono, salvo che un
  loro «Da riaprire se» scatti.

## CHIUSURA

1. `STATE.md` con L54b3b **fatto** nella tabella dei lotti, e il prossimo (L55); le celle di «In
   breve» sostituite, la voce di diario, la più vecchia delle tre in cima al diario di
   `STATE-STORIA.md` (la regola 7 di «Le regole»).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L54b3b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
