# Prompt per la sessione successiva — L72, i testi e le parti

Nome della sessione: **hi-fi preamp L72** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L71 (2026-11-04, report `reports/2026-11-04-L71-frontale-mosso.md`). Il
> frontale mosso durante una sequenza è simulato e dentro (NC-083 chiusa); il criterio del ritardo del
> permissivo è la regola fisica, **«Sì, regola fisica»** (ADR-120); il circuito non è cambiato. L'ordine verso
> G1: **L72** → L73 → L74 → G1 (la tabella dei lotti di `STATE.md`; concordato dall'utente il 2026-11-04).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L72**, e si ferma.

## La regola dell'utente sul prototipo (PR-12, ADR-118)

«Il prototipo sarà molto costoso e quindi dobbiamo essere certi che funzioni perfettamente, l'unica cosa che
vogliamo valutare sul proto è la qualità audio percepita.» **Ciò che si può simulare si simula qui.** Dopo il
prototipo si cambiano solo i condensatori di accoppiamento e le resistenze critiche, dissaldandoli.

## Che cosa fare

1. **Leggi prima**: `STATE.md`, `PRB.md` (PR-12, PR-30), `NONCOMPLIANCE.md` (**NC-080, NC-081, NC-082,
   NC-084**: per ciascuna «Cosa serve per chiuderla»), in `REQUIREMENTS.md` E8, E9, E10, E12, T5, P6, ADR-081,
   ADR-117, ADR-118, e i rilievi R2, R3, R6, R7 di `reports/2026-11-04-L65-architetto-avversariale.md`.
2. **Il condensatore della Stax (NC-080)**: E8 e T5 riscritti sul valore di ADR-081 (C165 / C365 da 1 µF ±5 %)
   con la finestra ammessa (~0,97–1,2 µF: ricavala, non copiarla — il limite basso da E9 a 20 Hz sul carico
   peggiore, quello alto dalla durata sopra 0,87 V di ADR-117), e la sezione 6 del dossier corretta. Un
   requisito cambia: ADR.
3. **La lista ammessa dei condensatori di segnale (NC-082)**: accanto a P6, per ogni posizione (C162 / C362,
   C171–C174 / C371–C374, C165 / C365, C262 / C462, C265 / C465) la finestra di valore e i tipi in
   polipropilene, ognuno conforme a E12, con le dimensioni del pezzo più grande (servono alle impronte e alla
   prova di spazio di L73). **Niente zoccoli** («dissalderemo»). Parti vere, verificate sul sito del
   costruttore o del distributore, mai un codice plausibile non controllato.
4. **Le resistenze del guadagno e del trim allo 0,1 % (NC-081)**: le 6 posizioni per canale nel sorgente
   (`circuits/preamp/`, con il commento che punta alla ADR) e nella distinta; E10 ricalcolato nel caso
   peggiore. Cambia il sorgente: netlist, disegni, `run_tests.sh`.
5. **La motivazione di PR-30 sulla principale (NC-084)**: riscritta sulla potenza del finale (il clipping a
   ~114 dB SPL di picco), col dato di potenza delle Heresy **verificato** da una fonte del costruttore; le righe
   della FMEA (Q132, C145) col tetto. È una riga del PRB: ADR e **firma dell'utente** sul testo proposto.
6. **Le domande all'utente** si fanno per nome, coi numeri; ogni opzione con la sua temperatura / potenza
   contro il limite, a rete ±10 %.

## I vincoli

- **La macchina è un MacBook Air senza ventole**: al più **3 simulazioni insieme**, con `nice -n 10`;
  prima di lanciare, `pgrep ngspice`. Se l'utente dice che girano altre sessioni, al più **2**.
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i comandi
  composti (`git` con altro, `cd` + `git`, `nice` dentro un `;` o un `&&`, i cicli con le variabili): `git -C
  <worktree>` un comando alla volta, il resto in uno script.
- Uno script di un lotto vecchio scrive nella **sua** cartella: non rieseguirlo per confronto; copiarlo.
- **Prima di iniziare e di nuovo prima di fare la domanda all'utente**: `git -C <worktree> fetch origin main`
  e `git -C <worktree> log --oneline HEAD..origin/main`. Se `main` ha già chiuso L72, fermarsi e dirlo (L70 è
  stato fatto due volte da due sessioni in parallelo: L70bis).
- `git add` un percorso alla volta; **`.gitignore` prima** di ogni `git add` di una cartella dati.
- Prima di una domanda che fa aspettare l'utente, un commit di lavoro pushato (L71 l'ha fatto: il lavoro è
  al sicuro anche se la sessione si chiude).
- Le domande si fanno per nome; i colpi al jack in dB SPL.

## CHIUSURA

1. `STATE.md`: L72 **fatto**, il prossimo **L73**; le celle di In breve; il diario (la voce più vecchia
   delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L73 («Nome della sessione: hi-fi preamp L73»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L72`; rimuovi il worktree; fermati.
