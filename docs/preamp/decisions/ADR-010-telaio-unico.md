# ADR-010 — Telaio unico con alimentatore a bordo

Data: 2026-09-08 · Stato: accettata

## Contesto

Con quattro stadi in Classe A e un phono a valvole già presente nella
stessa libreria, tenere il trasformatore lontano dai segnali avrebbe un
valore reale. L'alternativa era un alimentatore in cassa separata con
cordone ombelicale.

## Decisione

**Telaio unico**, con trasformatore e alimentazione a bordo.

## Perché

Scelta dell'utente: non vuole due telai. Il sistema è chiuso in una
libreria, e un apparecchio in più è ingombro e calore in più.

## Conseguenze accettate

Queste **non** sono obiezioni: sono il prezzo della decisione, messo per
iscritto perché non arrivi come sorpresa.

**1. La rete elettrica entra nel telaio.** Al gate **G3 l'assenza di
un'analisi di sicurezza è un BLOCK automatico** (regola di `AGENTS.md`).
Non è una formalità finale: riguarda fusibili, messa a terra, distanze di
isolamento e separazione fisica della sezione rete. Per questo l'analisi
di sicurezza parte in **Fase 6, in parallelo alla progettazione**, non in
coda.

**2. Il trasformatore finisce vicino a un nodo da 100 kΩ**, che è il
punto più sensibile del circuito, in un mobile chiuso. **Il ronzio è il
rischio numero uno del progetto.** Mitigazioni previste: toroidale (campo
disperso basso), orientamento e distanza massima dai connettori
d'ingresso, eventuale schermatura, due circuiti stampati separati
(alimentazione e audio) con massa a stella.

**3. Calore in un mobile chiuso.** ~3-4 W di Classe A più le perdite dei
regolatori. Non è drammatico, ma la ventilazione va prevista nel telaio,
non sperata.

## Alternative scartate

- **Alimentatore in cassa separata**: il meglio per il ronzio, ma due
  telai da progettare e costruire.
- **Alimentatore esterno DC certificato**: elimina il rischio sicurezza e
  semplifica il layout, ma prestazioni inferiori e un oggetto in più.

## Da riaprire se

Le misure di ronzio sul prototipo non rientrano nonostante le
mitigazioni. In quel caso l'alimentatore separato torna sul tavolo.
