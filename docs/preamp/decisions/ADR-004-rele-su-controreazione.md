# ADR-004 — Guadagno commutabile via relè sulla controreazione

Data: 2026-09-08 · Stato: accettata

## Contesto

Il guadagno unitario (ADR-001) è corretto per la catena **attuale**.
L'utente ha chiesto di non dover rifare il preamplificatore se un giorno
la catena cambia — richiesta sensata.

La sua proposta iniziale era uno stadio di guadagno **scavalcato dai
relè**.

## Decisione

**Un solo stadio d'uscita, con la rete di controreazione commutata dal
relè**: 0 dB / +10 dB. Non uno stadio separato che i relè scavalcano.

## Perché

- Con lo stadio scavalcato, i contatti del relè stanno nel percorso del
  segnale in **entrambe** le modalità, e con il guadagno inserito ci si
  ritrova due stadi attivi in cascata.
- Con la controreazione commutata, il relè **non tocca il segnale**:
  chiude a massa il partitore di feedback e basta.
- Il vantaggio non è cosmetico. Un contatto nel percorso del segnale
  mette in serie la propria resistenza e la propria non-linearità, e
  nessuno le corregge. Lo stesso contatto **dentro l'anello di
  controreazione** viene diviso dal guadagno d'anello: l'amplificatore lo
  corregge attivamente. Stesso componente, punto in cui i suoi difetti
  non contano.
- In modalità unitaria si ottiene un buffer a guadagno 1 vero, con tutta
  la riserva di controreazione disponibile — la configurazione più
  lineare che quello stadio possa assumere.

**+10 dB** perché copre il caso realistico: un finale a stato solido che
vuole 1,5-2 V invece dei 0,67 V del cj Evolution 250.

## Alternative scartate

- **Stadio di guadagno separato scavalcato dai relè** (proposta
  iniziale): relè nel percorso del segnale, due stadi in cascata.
- **Guadagno fisso unitario senza opzione**: costringerebbe a rifare il
  preamplificatore al cambio di catena.

## Da riaprire se

Serve più di +10 dB, o servono più di due posizioni di guadagno.

## Nota collegata

Senza servo di continua (ADR-007), commutando il guadagno l'offset
residuo salta da ×1 a ×3,16 e il condensatore d'uscita trasmette il
gradino come un botto. Vedi ADR-012 (relè di mute).
