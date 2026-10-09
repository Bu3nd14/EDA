# ADR-066 — La riga «Dettagli» di PR-14: il selettore è progettato (ADR-064), e regge con sorgenti fino a ~0,65 V di continua

Data: 2026-10-09 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Cambia la sola riga «Dettagli» di PR-14** del PRB (ADR-053). Il titolo e le tre righe di corpo
  della voce restano parola per parola.
- **Rimanda ad ADR-064**, il selettore, e ne porta nel contratto il limite dichiarato.

## Contesto

La riga «Dettagli» di PR-14 diceva «il selettore è ancora da progettare». Era vero quando il PRB è
stato firmato (L42c, 2026-09-27); da L48a (2026-10-06, ADR-064) il selettore è nel sorgente: un
condensatore per ingresso col lato del preamp a 0 V e un relè monostabile per ingresso dalla
manopola. Il PRB sta sopra `REQUIREMENTS.md` e cambiarlo vuole una ADR (ADR-053), quindi L48a aveva
lasciato la riga com'era e l'aveva scritta fra le cose da allineare. La porta all'utente L51a, che
rigenera il dossier col PRB in testa.

La misura di L48a (`spice/preamp/tb/tb_f1_selettore.cir`, `data/2026-10-06/L48a/`): fino a 100 mV
di continua della sorgente il gradino al cambio è **19,8 µV** al principale a +10 dB (~19 dB SPL),
lo stesso di due sorgenti a 0 V; con 1 V sale a 140 µV. Col poliestere peggiore (costante
d'isolamento 10 000 s) **F1 regge fino a ~0,65 V di continua della sorgente**: oltre, i 100 µV
della voce non sono garantiti. ADR-064 lo dichiara come limite, non come difetto.

## Decisione

Le risposte dell'utente (2026-10-09, all'inizio di L51): «Aggiornare la riga Dettagli», e fra il
solo rimando e il rimando col limite, **«Rimando e limite»**. La riga diventa:

> *Dettagli: F1, V2 · ADR-053, ADR-064, ADR-066 · regge con sorgenti fino a ~0,65 V di continua.*

## Perché

- Una riga falsa in testa al dossier («ancora da progettare») contraddice la sezione del selettore
  che il dossier stesso pubblica: il contratto non sarebbe univoco.
- Il limite di ~0,65 V è l'unica condizione sotto cui la voce regge che il corpo non dice. Scritto
  nei «Dettagli», chi legge il contratto lo vede senza aprire ADR-064.

## Alternative scartate

- **Il solo rimando ad ADR-064**: corretto, ma lascia il limite fuori dal contratto.
- **Lasciare la riga com'era** fino a una richiesta dell'utente: scelta che l'utente non ha fatto.

## Da riaprire se

- il limite di continua cambia (un condensatore in distinta con costante d'isolamento diversa, o
  una misura al prototipo, come in «Da riaprire se» di ADR-064);
- il corpo di PR-14 cambia: allora la voce intera va ridiscussa e rifirmata.
