# ADR-009 — Niente telecomando: attenuatore a scatti, nessun microcontrollore

Data: 2026-09-08 · Stato: accettata

## Contesto

Il controllo di volume è il componente più importante del progetto,
perché **il tracking fra i canali è il difetto che stiamo eliminando**
(vedi ADR-001). La scelta dell'architettura dipendeva da una sola
domanda: serve il telecomando?

L'utente ha risposto di no.

## Decisione

**Attenuatore a scatti su commutatore rotativo**, resistenze allo 0,1%,
10 kΩ. Nessun telecomando, e di conseguenza **nessun microcontrollore in
tutto il progetto**.

Gli ingressi restano commutati **a relè**, pilotati direttamente da un
commutatore rotativo.

## Perché

- Un attenuatore a scatti ha **tracking perfetto per costruzione**: i due
  canali usano resistenze della stessa tolleranza, non due piste di
  carbone che devono somigliarsi. È la risposta diretta al difetto
  diagnosticato.
- Zero elettronica di controllo, e invecchia meglio di qualsiasi
  soluzione con firmware.
- **I relè sugli ingressi restano anche senza telecomando**, e il motivo
  è indipendente: servono a tenere il **segnale lontano dal pannello
  frontale**. Sul commutatore passa solo corrente continua per le
  bobine, e il percorso audio resta corto, vicino ai connettori
  posteriori. È la ragione vera per cui si usano i relè — il telecomando
  è solo un bonus.
- Niente firmware, niente clock, niente digitale in un telaio analogico:
  coerente con ADR-003.

## Alternative scartate

- **Attenuatore a relè con microcontrollore**: tracking eccellente e
  telecomando possibile, ma ~20 relè e del firmware.
- **Integrato di volume (MUSES72320, PGA2311)**: tracking eccellente e
  controllo semplice, ma un integrato nel percorso del segnale —
  incompatibile con ADR-003.
- **Potenziometro ALPS RK27**: un solo componente, ma tracking ±2 dB
  tipico ai bassi livelli, cioè il difetto da cui veniamo.

## Da riaprire se

L'utente cambia idea sul telecomando. Nota che questo comporterebbe
reintrodurre un microcontrollore, cioè riaprire anche la coerenza con
ADR-003.

## Costo noto

Un commutatore rotativo di qualità adeguata è costoso. È un costo
accettato consapevolmente.
