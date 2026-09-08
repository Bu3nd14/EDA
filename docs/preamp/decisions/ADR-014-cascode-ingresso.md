# ADR-014 — Cascode sulla coppia d'ingresso

Data: 2026-09-08 · Stato: accettata

## Contesto

Domanda dell'utente: la capacità d'ingresso del JFET gioca un ruolo?

Sì, e in modo che sarebbe passato inosservato fino alle misure.

## Decisione

**La coppia differenziale d'ingresso è cascodata**, in entrambi i blocchi.

## Perché

**Al gate non si vede C_iss, si vede C_gs + C_rss × (1 + A_v)** — la
capacità Miller moltiplicata dal guadagno fino al drain. Con la coppia
caricata da uno specchio di corrente quel guadagno è alto.

Con LSK170 (esempio) e A_v ≈ 200: C_eff ≈ **1 nF**.

**Dove morde**: non all'ingresso del preamplificatore, dove la sorgente è
un cathode follower da 430 Ω. Morde sul **BLOCCO B, pilotato
dall'attenuatore**. Un attenuatore a scatti da 10 kΩ ha impedenza
d'uscita che **culmina a R/4 = 2,5 kΩ** a metà corsa:

> f₋₃dB = 62 kHz → **−0,42 dB a 20 kHz**

E il vero problema non è quel mezzo decibel: **l'impedenza
dell'attenuatore varia con la posizione della manopola**, quindi la
risposta in alta frequenza cambierebbe alzando il volume.

**È esattamente il difetto per cui abbiamo scartato il preamplificatore
passivo in ADR-002.** Lasciarlo passare significherebbe farlo rientrare
dalla porta di servizio.

**Il cascode tiene il drain a tensione costante**: se il drain non si
muove, l'effetto Miller sparisce e al gate resta C_iss. Con LSK489
(4 pF) e 2,5 kΩ di sorgente: **oltre 15 MHz**. Il problema cessa di
esistere.

## Tre vantaggi collaterali che servivano comunque

- **PSRR migliore** — era il punto debole dichiarato del discreto
  (ADR-003).
- **Più linearità** — V_ds costante significa parametri del dispositivo
  che non ondeggiano col segnale.
- **Meno dipendenza dal modello SPICE.** Con V_ds fisso, i parametri
  legati alla tensione drain-source pesano molto meno. Dato che la
  qualità dei modelli è il nostro punto debole (Fase 1, ADR-013), vale
  doppio.

## Nota di metodo

Senza cascode, la risposta alla domanda dell'utente sarebbe *«dipende da
quanto guadagno mettiamo sul drain»* — cioè da una scelta non ancora
fatta. **Il cascode elimina la dipendenza invece di gestirla.** È il
motivo per cui è la scelta giusta anche prima di conoscere i numeri
definitivi.

## Alternative scartate

- **Nessun cascode + dispositivo a bassa capacità**: funzionerebbe con i
  4 pF dell'LSK489, ma legherebbe la risposta in frequenza a una scelta
  di guadagno non ancora fatta, e la renderebbe fragile a ogni revisione
  della topologia.
- **Abbassare l'impedenza dell'attenuatore**: carica di più il buffer e
  non risolve il principio — l'impedenza continuerebbe a variare con la
  posizione.

## Da riaprire se

Le misure mostrano che il cascode costa margine di tensione in un punto
dove serve. Con rail ±15 V e segnali piccoli sulla coppia d'ingresso non
è previsto, ma va verificato.
