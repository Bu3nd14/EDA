# ADR-006 — Un solo blocco discreto, usato due volte

Data: 2026-09-08 · Stato: accettata

## Contesto

Servono due funzioni per canale: un buffer d'ingresso a guadagno
unitario e uno stadio d'uscita con guadagno commutabile. Il buffer, che
è sempre a guadagno unitario, potrebbe essere un semplice inseguitore —
molto più economico in parti di un blocco retroazionato completo.

## Decisione

**Lo stesso blocco discreto**, progettato una volta, usato due volte per
canale: cablato a guadagno unitario come buffer d'ingresso, e con la
controreazione commutata come stadio d'uscita.

## Perché

- Una sola topologia da progettare, simulare, validare e tenere a
  magazzino. In SKiDL è la stessa funzione richiamata due volte, che è
  esattamente il modo in cui `circuits/` è pensato per funzionare.
- **La decisione sull'appaiamento (ADR-005) ha ribaltato il calcolo.**
  Quando appaiare significava comprare coppie di precisione, risparmiare
  un blocco era un risparmio vero. Ora un blocco in più costa **due JFET
  presi dalla stessa bustina**.
- Un inseguitore semplice avrebbe un offset **sistematico e grande**
  (l'uscita sta a V_in + |V_GS|, cioè 300-700 mV per costruzione, non per
  tolleranza), contro le decine di millivolt di sbilanciamento del blocco
  retroazionato.
- Tenere l'inseguitore semplice avrebbe significato **due topologie
  diverse da validare** per risparmiare due transistor.

## Alternative scartate

- **Inseguitore semplice per il buffer d'ingresso** (JFET source
  follower + inseguitore complementare): meno parti, ma seconda
  topologia da validare, offset sistematico grande, e prestazioni
  disomogenee tra le uscite.

## Da riaprire se

Il giro componenti (Fase 3) rivela che i JFET sono scarsi o cari al
punto da rendere significativo il risparmio di due esemplari per canale.
