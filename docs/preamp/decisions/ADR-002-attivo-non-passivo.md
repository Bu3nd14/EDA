# ADR-002 — Preamplificatore attivo, non passivo puro

Data: 2026-09-08 · Stato: accettata

## Contesto

Stabilito che serve guadagno unitario (ADR-001), la domanda diventa
legittima: serve uno stadio attivo, o basta un attenuatore passivo con
la commutazione degli ingressi?

La domanda si è posta con forza perché l'utente, collegando il finale
alla REC OUT del Technics — un prelievo **passivo**, come dimostra il
fatto che funziona a preamplificatore spento — ha giudicato il suono
**migliore**: scena più aperta, medio-alte più naturali, basso più
profondo e controllato, maggiore dinamica.

## Decisione

Preamplificatore **attivo**: attenuatore seguito da stadio a guadagno
unitario. Non un passivo puro.

## Perché

- L'impedenza d'uscita di un attenuatore passivo **varia con la
  posizione della manopola**, con massimo R/4 a metà corsa. Il carico
  che vedono cavo e finale cambia mentre si ascolta.
- Con un passivo il valore dell'attenuatore è un compromesso che non si
  vince: **basso (10 kΩ)** carica il cathode follower a ECC82 del phono
  e ne peggiora l'asimmetria; **alto (100 kΩ)** è gentile con la valvola
  ma porta la Zout fino a 25 kΩ a metà corsa, dove la capacità del cavo
  comincia a contare.
- Con un buffer a monte dell'attenuatore quel compromesso sparisce:
  l'attenuatore si sceglie per le prestazioni (10 kΩ, rumore basso) e il
  phono vede solo l'ingresso ad alta impedenza del buffer.
- Le uscite fisse verso gli amplificatori per cuffia richiedono comunque
  un buffer (vedi ADR-008), quindi lo stadio attivo c'è a prescindere.

Nota: il miglioramento sentito con il prelievo passivo **non è un
argomento contro lo stadio attivo**. Cambiavano due cose insieme —
sparivano 16,5 dB di guadagno inutile *e* si spostava il controllo di
volume fuori dalla zona peggiore. Entrambe sono risolte dal progetto
attivo a guadagno unitario.

## Alternative scartate

- **Passivo puro**: impedenza d'uscita variabile, compromesso sul valore
  dell'attenuatore, sensibilità a cavi e carico.
- **Ponticello di bypass del buffer** per provare il passivo: resta
  possibile prevederlo sul circuito stampato, costa due piste.

## Da riaprire se

Si rinuncia alle uscite fisse per gli amplificatori per cuffia e si
accetta un attenuatore dimensionato sul solo phono.
