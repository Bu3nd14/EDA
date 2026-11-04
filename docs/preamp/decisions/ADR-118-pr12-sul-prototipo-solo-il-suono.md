# ADR-118 — PR-12 riscritta: sul prototipo si giudica solo il suono, e dopo si dissalda

Data: 2026-11-04 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Modifica PR-12** del PRB (ADR-053). Da «Condensatori di segnale e resistenze critiche si cambiano senza
  dissaldare, per provarli all'ascolto» al testo qui sotto.
- **P6** resta (passi multipli, la lista ammessa); quello che cade è il «senza dissaldare»: niente zoccoli.
- Collegata a **NC-082** (la lista ammessa dei condensatori di segnale, aperta in L65).

## Contesto

All'apertura di L65 l'utente ha scritto: «il prototipo sarà molto costoso e quindi dobbiamo essere certi
che funzioni perfettamente, l'unica cosa che vogliamo valutare sul proto è la qualità audio percepita. Le
modifiche post prototipo devono limitarsi a cambio condensatori di accoppiamento». L'architetto avversariale
(rilievo **R2**) ha notato che nessuna impronta ha uno zoccolo, contro il «senza dissaldare» di PR-12.
L'utente: la lista ammessa sì, lo zoccolo no, «dissalderemo».

## Decisione

**PR-12 · Il giudizio del suono è dell'utente, sull'hardware.** Sul prototipo si giudica solo il suono:
tutto il resto si verifica prima, in simulazione. Dopo il prototipo si cambiano solo i condensatori di
accoppiamento e le resistenze critiche, dissaldandoli, coi tipi della lista ammessa. Nessun agente dichiara
come suona il circuito.

Scelta dell'utente, 2026-11-04, sul testo proposto: **«Tenere le resistenze»** (le resistenze critiche
restano fra le parti che si cambiano).

## Perché

- La regola del prototipo è dell'utente, e il contratto deve dirla: un difetto che si vedrebbe solo sul
  prototipo e chiederebbe un altro componente, un taglio di pista o una scheda nuova diventa una non
  conformità da chiudere prima.
- Gli zoccoli a tulipano su condensatori di segnale grandi (un polipropilene da 4,7 µF / 250 V misura
  31,5 × 15 × 26 mm) aggiungono resistenza di contatto e altezza; l'utente preferisce dissaldare.

## Alternative scartate

- **Il testo senza le resistenze critiche**: l'utente le ha volute tenere.
- **Gli zoccoli** (la lettera del vecchio PR-12): scartati dall'utente.

## Da riaprire se

- Sul prototipo serve cambiare qualcosa che non è un condensatore di accoppiamento né una resistenza
  critica: è un difetto del processo di verifica, da registrare, non un'eccezione alla voce.
- Il numero di prove d'ascolto previste rende la dissaldatura un rischio per le piazzole.
