# Prompt per la sessione successiva — L69b, l'evidenza dell'alimentatore e il dossier sul sorgente nuovo

Nome della sessione: **hi-fi preamp L69b** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L69 (2026-11-04: i pull-up di AT_MRQ e di AT_ON in due metà in serie,
> R588 / R589, ADR-116, NC-079 chiusa). **Il circuito è cambiato**, e `build_dossier.py` rifiuta:
> l'evidenza dell'alimentatore del dossier (L64b) è corsa sul circuito di prima. L'utente: «Lotto a parte».
> L'ordine verso G1: **L69b** → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L69b**, e si
ferma.

## Che cosa fare

**Il dossier rigenerato sul sorgente di ADR-116.** Il dossier rigenera dal `psu.net` di oggi i deck
dell'alimentatore di `data/2026-11-03/L64b/` e li confronta con quelli corsi: oggi non coincidono più
(R572 + R588, R576 + R589). Va rifatta l'evidenza di L64b sul sorgente nuovo, in una cartella nuova
(`data/<oggi>/L69b/`), e il dossier ripuntato lì.

1. **Leggi prima**: il README e il report di L64b (`reports/2026-11-03-L64b-dossier-alimentatore.md`: che
   cosa c'è e come si rifà, `script/coda.sh`), il report di L69 (`reports/2026-11-04-L69-ritenuta.md`) e
   ADR-116, e in `docs/preamp/dossier/build_dossier.py` tutto ciò che legge `L64B` (≈ righe 192, 2501–3175:
   il calore, i banchi della rete e dei guasti, le sequenze, la seconda strada, il censimento, lo standby,
   il ponte e la catena al jack) e `PARTI_SCHEDE` (L64c).
2. **Il primo giro**: `build_dossier.py` sul `main` di oggi, i rifiuti salvati (in L69: 125, tutti dei deck
   di L64b più `parti_schede.csv`).
3. **Le corse**, sul banco di L64b copiato (i modi della coppia già coi nomi del sorgente; i corti di R572 /
   R576 sulle loro metà come in `L69/psu/modi.py`): le 117 sequenze, i banchi `rete` e `guasti`, il calore
   del telaio, lo standby, il ponte e la catena al jack alle tre reti. **I conti e il tempo stimato detti
   all'utente prima di lanciare** (L69: una sequenza ~26 s; la catena ~1 GB a corsa).
4. **La seconda strada** contro L64b: il circuito cambia solo nei due pull-up, quindi ci si aspetta lo stesso
   risultato cella per cella salvo i tempi che toccano AT_MRQ / AT_ON (L69: le corse sane uguali). Ogni cella
   diversa si spiega, o va all'utente.
5. **`parti_schede.csv`** rifatto (`L64c/script/parti_schede.py`: 2 parti aggiunte in più, R588 / R589).
6. **Il dossier**: `build_dossier.py` ripuntato (`L64B` → la cartella nuova; la FMEA e la copertura già da
   L69), «OK»; i sabotaggi di L64b, L64c, L68 riportati sui file nuovi cadono tutti (e uno nuovo sulla fonte
   L69). Il PDF all'utente se lo vuole (in `/Users/roberto/Documents`, un PDF per documento).

## I vincoli

- **La macchina è un MacBook Air senza ventole**: al più **3 simulazioni insieme**, con `nice -n 10`;
  prima di lanciare, `pgrep ngspice`. Se l'utente dice che girano altre sessioni, al più **2**. La catena al
  jack: 2 insieme (~1 GB l'una).
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i
  comandi composti (cicli, variabili calcolate, `nice` in una catena, gli script in linea con `<<`, le
  pipe dentro `$(...)`, `git` in un comando con altro, `sed` con programmi): scriverli in uno script.
- Uno script di un lotto vecchio scrive nella **sua** cartella: non rieseguirlo per confronto (L69 ha
  riscritto `L68/copertura.csv` così, ripristinato da git).
- Una lista che `xargs` sta leggendo non si riscrive; i sabotaggi toccano i file per un istante: niente
  commit mentre girano.
- `git add` un percorso alla volta; commit e push prima di ogni lista lunga.
- Le forme d'onda e le corse grezze non si committano: `.gitignore` prima di ogni `git add` di una
  cartella dati (L69: ~44 GB di forme d'onda fuori).
- Le domande si fanno per nome; i colpi al jack in dB SPL; ogni opzione con la sua temperatura contro il
  limite.

## CHIUSURA

1. `STATE.md`: L69b **fatto**, il prossimo **L65**; le celle di In breve (la Suite col dossier «OK»); il
   diario (la voce più vecchia delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L65 («Nome della sessione: hi-fi preamp L65»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L69b`; rimuovi il worktree; fermati.
