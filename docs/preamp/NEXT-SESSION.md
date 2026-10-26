# Prompt per la sessione successiva — L54b, il temporizzatore a comparatori nel sorgente

Nome della sessione: **hi-fi preamp L54b** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di **L54a** (2026-10-26): il riesame coi numeri, la scelta dell'utente
> «Comparatori, con lo standby», ADR-102, NC-054 chiusa. L'ordine deciso con l'utente: L54 (L54a fatto)
> → **L54b** → L55 → L58 → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L54b**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se si rivela più grande di una sessione, **dividilo con l'utente
all'inizio** (è probabile: il sorgente e i controlli, poi le corse sul sorgente).

## Perché questo lotto

ADR-102: il micro U509 e il firmware escono dall'alimentatore; al loro posto un temporizzatore di
dodici canali di comparatore (tre TLV1704), RC, diodi e una ritenuta a due transistor, provato solo sul
banco di L54a (`data/2026-10-25/L54a/psu/genera_tb_psu.py`, la lista `TIMER_AN`, commentata riga per
riga coi valori e le loro ragioni). Lo standby, K501, l'interruttore frontale, il sorvegliante su
`MUTE_G`, Δ e Δ₂ (U508) e Q505 restano.

## Che cosa fare

1. **Il sorgente** (`circuits/preamp/psu.py`): il temporizzatore coi valori di `TIMER_AN`, ogni valore
   col commento che punta ad ADR-102; fuori U509, C534, J515, R543–R547. Le reti per piedini prima e
   dopo (limitations #74). Simboli: TLV1704 (verificare la libreria KiCad; altrimenti il quadruplo
   più vicino, dichiarato), BC847 / BC857.
2. **`firmware/preamp_timer/` fuori**, e con lui il 2k di `run_tests.sh`; il 2e (`check_relay_safe_state.py
   --timer`, le regole T1–T5 che cercano il micro: limitations #68) riscritto per il temporizzatore
   nuovo, con i suoi falsi; il controllo meccanico di J1–J4 invariato.
3. **I disegni** dell'alimentatore e i loro controlli.
4. **Il banco sul sorgente**: `genera_tb_psu.py` che legge il temporizzatore dalla netlist (non più da
   `TIMER_AN`), il caso noto (le corse di L54a con `--timer comparatori` devono tornare), poi i casi di
   L54a sul sorgente; i comparatori col **modello del costruttore** (`vendor/comparator/ti/TLV1702/
   tlv1701.lib`) almeno sui casi della sicurezza, contro il comportamentale.
5. **Lo standby** (NC-037): i pull-up delle uscite tenute basse in standby alimentati solo da acceso;
   la cifra dal secondario di T2 alle tre reti, contro 130 mW di L54a.
6. **La catena al jack** dello spegnimento dal frontale e della perdita di rete (il ponte di L41c),
   contro 33,9 / 39,2 nV del dossier.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#67**, **#68**, **#73–#76**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di L54a.
- **ADR-102**; il report `reports/2026-10-26-L54a-micro-standby.md` (§1 gli stati, §8 per L54b); il
  README di `data/2026-10-25/L54a/`.

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti, le pipe o i `;` attorno a comandi che eseguono
  script; `cd … && script`; le variabili di shell nei percorsi e nei cicli; `xargs` sulla riga di
  comando; `awk` con programmi, heredoc, `python3 -c`, script lunghi sulla riga di comando (scriverli su
  file); `sed` con valori calcolati; un titolo di PR con l'apostrofo (il corpo su file,
  `--body-file`); un `git` con `-C` dentro un comando composto. Comandi semplici, **percorsi
  assoluti**, script scritti con Write, Edit per i testi.
- Le corse: la memoria (limitations #75) decide il parallelo; commit e push prima di una lista lunga;
  le forme d'onda grandi non si committano. Un deck che cambia si confronta coi numeri di prima, non
  col suo codice d'uscita (#76).
- Le domande all'utente si fanno per nome, senza sigle (al più fra parentesi); i colpi al jack in dB
  SPL; ogni opzione con la sua cifra contro il limite della parte, alle tre reti dove la rete conta.

## NON fa parte di questo lotto

- Le righe della FMEA delle parti nuove del temporizzatore e la diagnosi in hardware (ADR-076,
  ADR-078): L58.
- Il dispositivo d'uscita (L55), il dossier (L64), la revisione (L65), G1.
- Le decisioni prese non si riaprono, salvo che un «Da riaprire se» della loro ADR scatti. In quel caso
  si torna all'utente coi numeri.

## CHIUSURA

1. `STATE.md` con L54b **fatto** nella tabella dei lotti (o le sue parti), e il prossimo (L55,
   dall'ordine deciso con l'utente).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L54b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
