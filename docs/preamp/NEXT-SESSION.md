# Prompt per la sessione successiva — L58a2, le righe della FMEA delle parti nuove del temporizzatore

Nome della sessione: **hi-fi preamp L58a2** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L58a1 (2026-10-29), chiusa a metà su richiesta dell'utente (il budget
> settimanale). L58 è diviso dall'utente: L58a (test point, FMEA e distinta dell'alimentatore) e L58b
> (l'autodiagnosi). L58a1 ha fatto i test point (ADR-107) e la distinta (ADR-108: C548 / C552 in film di
> polipropilene). L'ordine verso G1, confermato dall'utente: **L58a2** → L58b → L66 → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L58a2**, e si
ferma.

## Che cosa fare

Le righe della FMEA di **R585** e dei **BAS416** (D534 / D535 / D536 / D541), nella forma di ADR-070. Il
banco è pronto in `docs/preamp/data/2026-10-29/L58a/psu/` (la copia di L54b3b): `modi.py` ha i sette
eventi del temporizzatore come guasti latenti (`EVENTI_TIMER`) e le righe aperto / in corto
(`RIGHE_TIMER`); `lista_l58a.py` scrive la lista con la base, i guasti, la perdita (1 µA su ogni BAS416:
l'ipotesi della riga, dichiarata) e la deriva di R585 (66k).

1. **Leggi le quattro prove sul caso noto** già corse (`lista_prova.txt`; le forme d'onda in
   `data/2026-10-29/L58a/seq/` se il worktree c'è ancora, altrimenti si rifanno con
   `/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_prova.txt 4`):
   `/usr/bin/python3 -I <L>/psu/analizza_mc.py --te=3.0 <L>/an_prova.csv <L>/seq/l58a_base/* <L>/seq/l58a/*`.
   Atteso: la base come `v_sorgente` di L54b3b; **R585 aperta** all'accensione con la base di Q513
   vicina a 0,89 V (ADR-103).
2. La lista intera (`lista_l58a.py > <L>/lista_l58a.txt`, 112 corse), `corri_lista_an.sh … 6`; conta i
   `ripiego.txt` (limitations #81). Commit e push prima.
3. Le righe in `<L>/fmea_alimentatore.csv` con le colonne di
   `data/2026-10-24/L45d2b3b3/fmea_dopo.csv`: G dall'effetto misurato, P da
   `data/2026-10-14/L45c2/script/classi_l45c2.py` (R 0,5 FIT, D_seg 1,0 FIT), R dal meccanismo. **R585 in
   corto** probabilmente acceca la ritenuta: se un guasto singolo toglie il mute o la ritenuta è il «Da
   riaprire se» di ADR-102 — non conformità nuova e domanda all'utente, per nome, coi numeri ricontati.
4. Il report `reports/2026-10-29-L58a-test-point-fmea-distinta.md` (anche la parte di L58a1: i test
   point, la distinta, le 5 reti audio che cambiano nome a ogni rigenerazione anche col sorgente di
   prima, limitations #74), e una voce di `docs/limitations.md`: i generatori di banco sulle netlist
   intere devono mappare `TestPoint` (fatto nella copia di L58a).

## I vincoli

Quelli del prompt di L58 (comandi semplici, percorsi assoluti, script scritti con Write, `git add` un
percorso alla volta, le forme d'onda non si committano). Le domande per nome, i colpi al jack in dB SPL.

## CHIUSURA

1. `STATE.md`: L58a2 **fatto**, il prossimo **L58b**; In breve, diario (la più vecchia delle tre in
   `STATE-STORIA.md`).
2. Riscrivi questo file per L58b («Nome della sessione: hi-fi preamp L58b»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L58a2`; rimuovi il worktree; fermati.
