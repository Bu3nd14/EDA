# Prompt per la sessione successiva — L58b, l'autodiagnosi

Nome della sessione: **hi-fi preamp L58b** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L58a2 (2026-11-01). L58 è diviso dall'utente: L58a (test point, FMEA e
> distinta dell'alimentatore, **fatto**: L58a1 + L58a2) e L58b (l'autodiagnosi). L'ordine verso G1,
> confermato dall'utente: **L58b** → L66 → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L58b**, e si
ferma.

## Che cosa fare

L'autodiagnosi: che cosa il circuito vede da sé dei guasti latenti mandati a L58, e come lo dice. Il
micro è uscito (ADR-102): quello che ADR-076 / ADR-078 davano al firmware si fa **in hardware** (per
esempio un canale di comparatore) **o torna all'utente**.

1. **Leggi prima**: la riga di L58 nella tabella dei lotti di `STATE.md`; ADR-071, ADR-076, ADR-078,
   ADR-100 (il punto «alla diagnosi, L58»: 46 righe latenti), ADR-102, ADR-109; le righe latenti in
   `data/2026-10-24/L45d2b3b3/fmea_dopo.csv` (stato «alla diagnosi») e in
   `data/2026-10-29/L58a/fmea_alimentatore.csv` (L58a2: R585 in corto, accettata; D536 guasto; D534 /
   D541 aperti, latenti a priorità bassa).
2. **Il censimento**: per ogni gruppo di righe latenti (il mute che non si inserisce, ADR-076, 8 alte; il
   degrado silenzioso del blocco, ADR-071; lo standby col toroidale o la linea dei relè accesi per
   guasto, ADR-078) che cosa si potrebbe vedere, con quale nodo, quando (all'accensione, in musica) e
   con quale costo in parti. Il «Da riaprire se» di ADR-100: un latente che non si vede a costo
   ragionevole torna all'utente.
3. **Con l'utente, conversando** (non un questionario): che cosa vuole vedere e come gli si dice (un
   LED, il mute tenuto, niente). Se serve, una voce del PRB con la sua ADR.
4. Se il circuito cambia: sorgente (`circuits/preamp/psu.py`), netlist, disegno, i casi noti del banco
   di `data/2026-10-29/L58a/psu/` (copiarlo nella cartella del lotto; limitations #84: le parti nuove
   si mappano), `run_tests.sh`, la regressione dei sette eventi del temporizzatore.

## I vincoli

Quelli di L58a (comandi semplici, percorsi assoluti, script scritti con Write, `git add` un percorso
alla volta, le forme d'onda non si committano; commit e push prima di ogni lista lunga). Le domande per
nome, i colpi al jack in dB SPL, ogni opzione verificata sui limiti a rete ±10 %. `analizza_mc.py` ha
l'artefatto di limitations #85 sulle accensioni a freddo: l'armamento si legge con `psu/armo.py`.

## CHIUSURA

1. `STATE.md`: L58b **fatto**, il prossimo **L66**; In breve, diario (la più vecchia delle tre in
   `STATE-STORIA.md`).
2. Riscrivi questo file per L66 («Nome della sessione: hi-fi preamp L66»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L58b`; rimuovi il worktree; fermati.
