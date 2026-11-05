# ADR-124 — La principale è protetta dalla potenza del finale, non dal suo trasformatore

Data: 2026-11-05 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Precisa ADR-081** (la principale «conta sul trasformatore del finale a valvole»): la decisione resta —
  sulla principale nessuna soglia di durata —, cambia la ragione. Riscrive la seconda frase di **PR-30** e
  la parentesi di **P10**. Chiude **NC-084**.
- Accanto ad **ADR-117**: anche qui un dato del costruttore che manca diventa un'ipotesi dichiarata.

## Contesto

La revisione dell'architetto avversariale di L65 (rilievo **R7**): un trasformatore d'uscita non blocca un
gradino di 14–21 V con costante ~0,3 s, lo passa come transitorio di bassa frequenza. Ciò che limita è la
potenza del finale; la FMEA scriveva 137–140 dB SPL «lineari» alla principale (Q132, C145), che il finale
non può dare. La conclusione regge se le Heresy reggono più di quanto il finale dà: il dato non era letto.

## Decisione

1. **PR-30**, scelta dell'utente sul testo proposto, **«Firmo così»**: «L'uscita principale conta sulla
   potenza del finale: 30 W, che vanno in clipping a ~114 dB SPL di picco, meno di quanto le Heresy
   reggono; la fissa 1 sulla protezione dichiarata del Singxer.»
2. **La potenza delle Heresy I: 100 W continui, ipotesi dichiarata.** Scelta dell'utente: **«100 W, ipotesi
   dichiarata»**.
3. **La FMEA col tetto**: nel dossier le cifre al jack sopra **113,8 dB SPL** si scrivono «il finale in
   clipping», con la cifra lineare accanto (`dossier/build_dossier.py`, `TETTO_FINALE_DB`).

## Perché

`data/2026-11-05/L72/script/principale_potenza.py`, con la convenzione di NC-028 (96 dB / 1 W / 1 m,
finale ×21,1), che ridà le cifre della FMEA (Q132 corto B-E 136,6 dB SPL, corto C-E 140,1):

- il cj Evolution 250 (30 W su 8 Ω) satura a **21,9 V di picco: 113,8 dB SPL di picco a 1 m**; al suo
  ingresso servono 1,04 V, e il gradino del guasto è 13–20 volte tanto: il finale è in clipping per tutta la
  durata del colpo;
- al diffusore al più **30 W** col seno, **60 W** in onda quadra; contro 100 W il margine è 5,2 / 2,2 dB.
- **Il dato delle Heresy**: Klipsch pubblica **100 W continui / 400 W di picco** per Heresy III e IV (le sue
  schede, `assets.klipsch.com`); per la Heresy I nessun documento Klipsch raggiungibile il 2026-11-05 (le
  copie del manuale su hifiengine e hifi-wiki rispondono 403); le fonti secondarie dicono 100–105 W, un
  proprietario 25 W per una coppia del 1966.

## Alternative scartate

- **Lasciare NC-084 aperta** finché il dato della Heresy I non è letto: l'utente ha scelto l'ipotesi.
- **Una soglia di durata anche sulla principale**: ADR-081 l'ha già scartata; il finale satura comunque.

## Da riaprire se

- La potenza stampata sulle Heresy dell'utente, o un documento Klipsch della Heresy I, è sotto **60 W**
  continui.
- Cambia il finale (più di 50 W su 8 Ω porta il caso quadro oltre i 100 W) o i diffusori (PR-30: «un
  apparecchio nuovo a valle fa rivedere il preamp»).
