# ADR-113 — PR-24 riscritta: la sicurezza non dipende da un programma, perché un microcontrollore non c'è

Data: 2026-11-03 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Cambia la voce PR-24** del PRB (ADR-053): il titolo, il corpo e la riga «Dettagli».
- **Porta nel contratto ADR-102** (il temporizzatore a comparatori: il micro e il firmware escono),
  che supera ADR-049; ADR-049 resta nei «Dettagli» accanto a chi la supera.

## Contesto

PR-24, firmata il 2026-09-27, diceva: «La sicurezza non dipende dal firmware. Senza firmware, con il
micro bloccato o in reset, l'apparecchio resta muto e il guadagno non può cambiare con le uscite
collegate», con i «Dettagli» F7 · ADR-022, ADR-045, ADR-049. Da ADR-102 (L54b1, 2026-10-26) il
temporizzatore è fatto a comparatori: nel preamplificatore non c'è più un microcontrollore, né
firmware. La promessa resta vera, e a maggior ragione; ma il suo testo parla di un micro che non c'è,
e i «Dettagli» citano ADR-049, che da L64a ha lo stato «superata da ADR-102».

Rigenerando il dossier (L64a, 2026-11-03) il controllo del contratto ha rifiutato: «PR-24 cita
ADR-049, superata da ADR-102, senza citare ADR-102: il contratto non è univoco». Il PRB sta sopra
`REQUIREMENTS.md` e cambiarlo vuole una ADR (ADR-053).

## Decisione

La scelta dell'utente (2026-11-03, L64a), fra il testo proposto, il cambio della sola riga
«Dettagli» e una frase sua: **«Rewrite the promise»**, col testo proposto. La voce diventa:

> **PR-24 · La sicurezza non dipende da un programma.** Non c'è un microcontrollore: accensione,
> ritardi e mute sono fatti da comparatori e relè, e il guadagno non può cambiare con le uscite
> collegate.
> *Dettagli: F7 · ADR-022, ADR-045, ADR-049, ADR-102, ADR-113.*

## Perché

- Una voce che parla del «micro bloccato o in reset» contraddice l'alimentatore che il dossier
  pubblica (ADR-102): il contratto non sarebbe univoco.
- La promessa che l'utente aveva firmato (la sicurezza non si affida a un programma) è conservata;
  cambia la ragione per cui vale: non c'è niente da bloccare.
- Il guadagno che non cambia con le uscite collegate non dipendeva dal micro neanche prima: è
  l'interblocco a relè col mute (ADR-041, ADR-045), e resta nella voce.

## Alternative scartate

- **Cambiare la sola riga «Dettagli»** (come ADR-066 per PR-14): il controllo passa, ma la voce
  continua a promettere qualcosa su un micro che non c'è.
- **Una frase dell'utente**: offerta, non scelta.

## Da riaprire se

- Un microcontrollore o un programma rientra nel progetto (un telecomando, un DAC, un display): la
  voce va riscritta perché dica di nuovo che cosa succede col programma fermo.
- F7 in `REQUIREMENTS.md` si misura ancora «senza firmware»: va allineato al lotto che la tocca.
