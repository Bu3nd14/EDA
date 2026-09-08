# ADR-005 — Appaiamento JFET rilassato a "stessa gradazione"

Data: 2026-09-08 · Stato: accettata

## Contesto

La topologia prevede una coppia differenziale a JFET all'ingresso.
L'assunto iniziale era che servissero **coppie appaiate di precisione**,
che sono la parte scarsa e cara del progetto (LSK170/LSJ74 e simili) — e
quindi il principale rischio di approvvigionamento.

L'utente ha chiesto perché.

## Decisione

Non servono coppie appaiate di precisione. Basta **stessa gradazione,
stesso lotto**, eventualmente con una selezione fatta in casa misurando
I_DSS su una ventina di pezzi.

## Perché

Scomponendo cosa compra realmente l'appaiamento in **questo** circuito:

- **Offset in continua** — è il motivo principale per cui si appaiano.
  Ma l'accoppiamento capacitivo in uscita (ADR-007) impedisce alla
  continua di arrivare a valle: il requisito cade.
- **Distorsione di ordine pari** — è il motivo che si cita di solito, ed
  è qui il meno rilevante. In un amplificatore retroazionato la coppia
  d'ingresso non vede il segnale, vede l'**errore**: con 60 dB di
  guadagno d'anello e 2 V in uscita, ai capi della coppia ci sono
  **2 mV**. Su dispositivi che lavorano linearmente su centinaia di
  millivolt di escursione gate-source, in quel regime la coppia è lineare
  comunque, appaiata o no.
- **PSRR e bilanciamento delle correnti** — questo resta reale, ed è
  l'unica ragione superstite. Ma è uno squilibrio **grossolano** (2:1 di
  I_DSS) a dare fastidio, non qualche millivolt.

Rovescio di un'intuizione diffusa: l'appaiamento è critico in uno
**stadio phono** — segnale minuscolo, guadagno alto, nessun servo — ed è
molto meno critico in uno **stadio di linea a guadagno unitario con
retroazione globale**.

## Alternative scartate

- **Coppie appaiate di precisione acquistate**: costo e disponibilità
  ingiustificati per il beneficio reale in questa topologia.
- **Ingresso a BJT**: rumore più basso, ma corrente di base e Zin più
  difficile da portare a 100 kΩ senza acrobazie.

## Da riaprire se

Si rimuove il condensatore d'uscita a favore di un accoppiamento diretto
(l'offset tornerebbe critico), oppure la stessa topologia viene riusata
per lo stadio phono del progetto successivo — dove le conclusioni sopra
**non valgono**.
