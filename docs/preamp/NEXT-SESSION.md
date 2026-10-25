# Prompt per la sessione successiva — L57b, il limitatore d'ingresso nel sorgente

Nome della sessione: **hi-fi preamp L57b** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di **L57a** (2026-10-25): l'RCA a caldo, il banco provato, i numeri, le
> strade, la scelta. L57 è stato diviso dall'utente all'inizio («Due parti»). **ADR-101**: «Limitatore
> ±5,6 V» e «Sì, mute prima». NC-059 avanza e si chiude qui.
> L'ordine deciso con l'utente dopo L45d2b3b2a: L57 (b) → L54 → L55 → L58 → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L57b**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se si rivela più grande di una sessione, **dividilo con l'utente
all'inizio**.

## Perché questo lotto

**NC-059** (maggiore, prima di G1). In L57a (`data/2026-10-25/L57a/`, `sintesi.csv`): senza rimedio,
inserendo un RCA a caldo da una sorgente in classe II, il gate-gate dell'LSK489 del blocco A arriva a
**32,2 V a rete +10 %**, oltre i 30 V di rottura minima. L'utente ha scelto il **limitatore a ±5,6 V**:
per canale, fra il contatto del relè del selettore e l'ingresso del blocco A, **1 kΩ** in serie e due
diodi verso due riferimenti a **±5 V**, comuni ai due canali. Sul banco (diodi 1N4148, riferimenti
ideali): gate-gate 4,3 V, il jack alla posizione d'ascolto 99,8 / 109,8 dB SPL (0 / +10 dB) sotto i
112,2, le fisse +3,4 dB sul K11, THD a 20 kHz 0,000764 % a 0,2 V e 0,00765 % a 2 V, E5 stimato 4,92 µV.

## Che cosa fare

1. **Le parti**, coi numeri contro i loro limiti: i due diodi per canale (bassa dispersione e bassa
   capacità; il 1N4148 era uno stand-in), i due riferimenti a ±5 V **a shunt** (devono assorbire la
   corrente dei diodi: ~1,1 mA per canale a rete +10 %, due canali), la resistenza da 1 kΩ (il picco al
   contatto della massa). Modelli del costruttore in `models/` con la provenienza, se servono.
2. **Il sorgente**: la protezione è del canale, non del blocco (ADR-006): in `preamp_audio.py`, accanto
   al selettore (R_SEL), con sigle esplicite (limitations #22); i riferimenti dove stanno meglio (il
   canale o la scheda). Netlist, i disegni (schematico completo, schema a blocchi), `run_tests.sh`.
   Commento con ADR-101 su ogni valore non ovvio.
3. **Il banco di L57a sul circuito generato**: `data/2026-10-25/L57a/script/genera.py` e `dist.py` hanno
   la protezione scritta a mano (`--prot R=1k,D=5`); il banco nuovo prende la protezione dalla netlist (o
   ne prova l'uguaglianza riga per riga) e ridà le cifre di ADR-101 entro i suoi «Da riaprire se» — prima
   provato su un caso noto di L57a.
4. **Il costo con le parti vere**, col banco del costo di L57a (il punto di lavoro vivo come nodeset, il
   rifiuto di un blocco spento), e **la regressione**: V1, E5, V4 dove il rimedio tocca l'ingresso; E3 non
   dovrebbe cambiare (la protezione è in serie dopo R_SEL): dirlo coi numeri.
5. **NC-059 si chiude** se i numeri tengono; l'avviso nel manuale è in ADR-101 (non c'è ancora un manuale).

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#22**, **#62**, **#75**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di L57a.
- **ADR-101**; il report `reports/2026-10-25-L57a-rca-a-caldo.md` (§4: le due trappole del banco del
  costo); il README di `data/2026-10-25/L57a/`.
- **NC-059** in `NONCOMPLIANCE.md`; ADR-064 (il selettore), ADR-006 (una sola topologia del blocco), V4 e
  E5 in `REQUIREMENTS.md`.

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti, le pipe o i `;` attorno a comandi che eseguono
  script; `cd … && script`; le variabili di shell nei percorsi e nei cicli; `xargs` sulla riga di
  comando; `awk` con programmi, heredoc, `python3 -c`, script lunghi sulla riga di comando (scriverli su
  file); `sed` con valori calcolati; un titolo di PR con l'apostrofo (il corpo su file,
  `--body-file`). Comandi semplici, **percorsi assoluti**, script scritti con Write, Edit per i testi.
- Le corse: la memoria (limitations #75) decide il parallelo (i banchi di L57a stanno a ~65 MB l'uno);
  commit e push prima di una lista lunga; le forme d'onda grandi non si committano.
- Le domande all'utente si fanno per nome, senza sigle (al più fra parentesi); i colpi al jack in dB
  SPL; ogni opzione con la sua cifra contro il limite della parte, alle tre reti dove la rete conta.

## NON fa parte di questo lotto

- Il micro e lo standby (L54), il dispositivo d'uscita (L55), la diagnosi (L58), il dossier (L64), la
  revisione (L65), G1.
- Un mute automatico all'inserimento (non proposto in ADR-101); un manuale d'uso.
- Le decisioni prese non si riaprono, salvo che un «Da riaprire se» della loro ADR scatti. In quel caso
  si torna all'utente coi numeri.

## CHIUSURA

1. `STATE.md` con L57b **fatto** nella tabella dei lotti, e il prossimo (L54, dall'ordine deciso con
   l'utente).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L57b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
