# Prompt per la sessione successiva — L54b3, la robustezza del temporizzatore al banco

Nome della sessione: **hi-fi preamp L54b3** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura della seconda parte di L54b (2026-10-28). L54b è stato diviso
> dall'utente all'inizio, «Tre parti»: la prima (il sorgente, i guardiani, i disegni, il banco sul
> sorgente) e la seconda (i comparatori, l'innesco della ritenuta, lo standby, la catena al jack) sono
> fatte; questa è la terza. L'ordine deciso con l'utente: L54b3 → L55 → L58 → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L54b3**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Dove siamo

Il temporizzatore di ADR-102 è nel sorgente (`circuits/preamp/psu.py`, U513–U515, la ritenuta Q513 /
Q514), con **R585** di ADR-103 (33 kΩ dall'innesco della ritenuta, AT_F, al ritorno: all'accensione
a freddo col frontale acceso le uscite dei comparatori sotto 2,2 V possono essere aperte, e senza
R585 la ritenuta scattava). Il banco è `data/2026-10-28/L54b2/psu/genera_tb_psu.py` (README della
cartella): `--timer sorgente`, e per ADR-103 i comparatori **tarati** sul modello di TI
(`--comparatore tarato`, `CMPTA` in `psu/cmpta.lib`; `tarato18` anche U505–U508; `tarato22` con le
uscite vive solo a 2,2 V, il caso peggiore dell'accensione). Il modello di TI stesso
(`models/comparator/tlv1701_ngspice.lib`) torna col datasheet da solo ma non passa l'accensione del
banco (limitations #77): non si riprova. I casi di L54b2 sul sorgente — `an_fin_*` (comportamentale),
`an_fint_*` (tarato) — sono il punto di partenza: **non vanno rifatti qui**.

## Che cosa fare

Il punto 7 del prompt di L54b (richiesta dell'utente dopo L54a, 2026-10-26), parola per parola:

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

Nel sorgente i due 1 nF base-emettitore della ritenuta sono C554 (Q513) e C555 (Q514). «I comparatori
del costruttore» sono, per ADR-103, il tarato `CMPTA`. In più, da L54b2:

- **l'accensione a freddo col frontale acceso** fra i casi, col tarato a 2,2 V: la base di Q513 deve
  restare ≤ 0,45 V anche a 60 °C e col Monte Carlo (oggi 0,30 V a 25 °C; il «Da riaprire se» di
  ADR-103);
- **la perdita di rete a −10 %**: i regolatori escono di regolazione 2,4 ms prima dello stacco del jack
  (+4,4 dB SPL, sotto la soglia di V2): le tolleranze non devono farlo crescere oltre il criterio.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#72**, **#75**, **#76**, **#77**, **#78**),
  `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di L54b2.
- **ADR-102**, **ADR-103**; il report `reports/2026-10-28-L54b2-temporizzatore-sul-sorgente.md`; i
  README di `data/2026-10-28/L54b2/` e `data/2026-10-26/L54b1/`.

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti, le pipe o i `;` attorno a comandi che eseguono
  script; `cd … && script`; le variabili di shell nei percorsi e nei cicli; `xargs` sulla riga di
  comando; `awk` con programmi, heredoc, `python3 -c`, script lunghi sulla riga di comando (scriverli
  su file); `sed` con valori calcolati; un titolo di PR con l'apostrofo (il corpo su file,
  `--body-file`); un `git` con `-C` dentro un comando composto. Comandi semplici, **percorsi
  assoluti**, script scritti con Write, Edit per i testi.
- Il banco di L54b2 col comparatore comportamentale e senza opzioni è il deck di L54b1 più R585; per
  rifare L54b1 serve `--net data/2026-10-28/L54b2/psu_prima.net`.
- Le corse: la memoria (limitations #75) decide il parallelo (una corsa di sequenza col tarato è
  ~0,45 GB e ~15 s); commit e push prima di una lista lunga; le forme d'onda grandi non si committano.
- Le domande all'utente si fanno per nome, senza sigle (al più fra parentesi); i colpi al jack in dB
  SPL; ogni opzione con la sua cifra contro il limite della parte, alle tre reti dove la rete conta.

## NON fa parte di questo lotto

- Le righe della FMEA delle parti nuove (R585 compresa) e la diagnosi in hardware (ADR-076, ADR-078):
  L58.
- Il dispositivo d'uscita (L55), il dossier (L64), la revisione (L65), G1.
- Lo standby: la scelta di ADR-103 («Lasciare com'è») non si riapre, salvo che il suo «Da riaprire se»
  scatti.
- Le decisioni prese non si riaprono, salvo che un «Da riaprire se» della loro ADR scatti.

## CHIUSURA

1. `STATE.md` con L54b3 **fatto** nella tabella dei lotti, e il prossimo (L55); le celle di «In
   breve» sostituite, la voce di diario, la più vecchia delle tre in cima al diario di
   `STATE-STORIA.md` (la regola 7 di «Le regole»).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L54b3`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
