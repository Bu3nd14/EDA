# Prompt per la sessione successiva — L68, la FMEA del temporizzatore a comparatori

Nome della sessione: **hi-fi preamp L68** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L64c (2026-11-03: il dossier completo). Rigenerando il dossier è
> venuto fuori che la FMEA non ha righe per 37 parti del temporizzatore a comparatori (NC-078); l'utente
> ha scelto «Non conformità, lotto apposta». L'ordine verso G1: **L68** → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L68**, e si
ferma.

## Che cosa fare

**Le righe della FMEA delle parti dell'alimentatore che non ne hanno** (NC-078), sul circuito di oggi
(il circuito non cambia), nella forma di ADR-070, e dentro la FMEA di oggi e il dossier.

1. **Leggi prima**:
   - NC-078 in `NONCOMPLIANCE.md`, la riga di L68 nella tabella dei lotti di `STATE.md`;
   - il report di L64c (`reports/2026-11-03-L64c-dossier-chiusura.md`) e il README di
     `data/2026-11-03/L64c/`: il banco (`psu/`, coi modi degli ingressi in `modi.py`), le corse, la
     catena al jack, `fmea_l64c.py`, `fmea_oggi.py`, `copertura.py`;
   - il report di L58a (`reports/2026-10-29-L58a-test-point-fmea-distinta.md`): com'erano fatte le righe
     di R585 e dei BAS416, gli stessi sette eventi.
2. **Le parti** (`data/2026-11-03/L64c/copertura.csv`): le 37 del temporizzatore — U513, U514, U515
   (TLV1704: l'uscita di un canale aperta, bloccata bassa, l'alimentazione persa), Q513 / Q514 (la
   ritenuta), D533, D537–D540, C545–C555, R569–R584 (aperto, in corto) —; i 5 connettori J4, J508,
   J510, J511, J512 (un pin aperto: quale conta); i 17 test point TP501–TP517 (un corto verso la massa
   vicina, o la ragione per cui non conta). Prima di correre, conta i casi e dillo all'utente coi numeri.
3. **Le corse**: i modi in `modi.py` (una lista nuova, come `RIGHE_L64C`), contro i sette eventi del
   temporizzatore (`EVENTI_TIMER`) e il mute dal frontale (`inss`); il calore dei regolatori dove i 5 V
   vanno a massa (`calore_5v.py`); il jack con la catena (`catena/`) dove i relè cadono insieme o il
   guadagno si muove prima del jack. Le corse sane di confronto sono in `data/2026-11-03/L64b/an_l64b.csv`.
4. **Le righe**: uno script come `fmea_l64c.py`; la gravità dal picco al jack con le soglie di ADR-070
   (o 5 se una parte esce dalla sua Tj max), la probabilità dai tassi (SN 29500 / IEC 61709, FMD-2016),
   la rilevabilità dal meccanismo, la priorità dalla matrice. Le righe in `fmea_oggi.csv` come sesta
   fonte (`fmea_oggi.py` e `FMEA_FONTI` in `build_dossier.py`); `copertura.py` deve dare 0 parti
   dell'alimentatore senza riga.
5. **Il dossier rigenerato** (`build_dossier.py` passa, i sabotaggi di `data/2026-11-03/L64c/script/
   sabotaggi.py` cadono tutti), e il PDF all'utente se lo vuole (in `/Users/roberto/Documents`, un PDF
   per documento).
6. **Le domande all'utente** coi numeri, per nome: una riga fuori dal criterio è sua (accettarla con una
   ADR, o una non conformità).

## I vincoli

- **Il circuito non cambia.** Un difetto trovato apre una non conformità e si porta all'utente.
- **La macchina è un MacBook Air senza ventole**: al più **3 simulazioni insieme**, con `nice -n 10`;
  prima di lanciare, `pgrep ngspice`. Se l'utente dice che girano altre sessioni, al più **2**.
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i
  comandi composti (cicli, variabili calcolate, `nice` in una catena, gli script in linea con `<<`):
  scriverli in uno script.
- Una lista che `xargs` sta leggendo non si riscrive.
- `git add` un percorso alla volta; commit e push prima di ogni lista lunga.
- Le forme d'onda e le corse grezze non si committano: `.gitignore` prima di ogni `git add` di una
  cartella dati. Le forme d'onda di un lotto chiuso non ci sono più: se servono, si ricorre.
- Le domande si fanno per nome; i colpi al jack in dB SPL.

## CHIUSURA

1. `STATE.md`: L68 **fatto**, NC-078 chiusa se le righe ci sono tutte, il prossimo **L65**; le celle di
   In breve; il diario (la voce più vecchia delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L65 («Nome della sessione: hi-fi preamp L65»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L68`; rimuovi il worktree; fermati.
