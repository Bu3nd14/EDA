# Requisiti — Preamplificatore di linea

**Documento vivo.** Riscritto quando i requisiti cambiano. Ogni modifica
sostanziale deve avere una ADR corrispondente in `decisions/`.

Ultimo aggiornamento: 2026-09-08 · Stato: **congelati** (Fase 0 chiusa)

Le motivazioni non stanno qui: stanno nelle ADR referenziate e nel
report `reports/2026-09-08-analisi-catena.md`.

## Contesto d'uso

| Ruolo | Apparecchio |
|---|---|
| Sorgente | Phono MC a valvole autocostruito — uscita cathode follower ECC82, Zout ≈ 430 Ω, ~0,5 V |
| Sorgente | FiiO K11 R2R (Raspberry Pi / Volumio / Tidal) — 2,7 V RMS |
| Carico principale | conrad-johnson Evolution 250 (= **MV50 in triodo**, 30 W) — **Zin 100 kΩ confermata**, sensibilità 612–750 mV |
| Carico fisso | Singxer SA-1 V2 — volume proprio |
| Carico fisso | Stax SRM-T1 — Zin ~50 kΩ, volume proprio |
| Diffusori | Klipsch Heresy I — 96 dB/1W/1m |

## Requisiti funzionali

| # | Requisito | ADR |
|---|---|---|
| F1 | **4 ingressi** sbilanciati RCA, commutati a **relè** | ADR-009 |
| F2 | **Trim di livello per ingresso**: 0 / −6 / −12 dB a ponticello | ADR-011 |
| F3 | **3 uscite**: principale (attenuata) + 2 a livello fisso | ADR-008 |
| F4 | **Attenuatore a scatti**, commutatore rotativo, 10 kΩ, resistenze 0,1% | ADR-009 |
| F5 | **Guadagno commutabile 0 / +10 dB**, relè sulla rete di controreazione | ADR-004 |
| F6 | **Relè di mute** su tutte le uscite: accensione e commutazione guadagno | ADR-012 |
| F7 | **Nessun telecomando, nessun microcontrollore** | ADR-009 |

## Requisiti elettrici

| # | Parametro | Valore | Origine |
|---|---|---|---|
| E1 | Guadagno nominale | **0 dB** | ADR-001 |
| E2 | Guadagno alternativo | **+10 dB** commutabile | ADR-004 |
| E3 | Impedenza d'ingresso | **≥ 100 kΩ** | Cap di accoppiamento del phono — vedi report |
| E3b | Attenuazione tipica all'ascolto | ~29–31 dB con il nuovo preamp | Guadagno finale 20,7×–25,3× |
| E4 | Impedenza d'uscita | **< 100 Ω in banda passante** (misurata escludendo la reattanza del condensatore d'accoppiamento), costante con la posizione del volume | ADR-002 |
| E5 | Rumore in uscita | **< 10 µV RMS** (20 Hz–20 kHz, non pesato) | vedi nota sotto |
| E6 | Livello massimo d'ingresso | 2,7 V RMS | FiiO K11 R2R |
| E7 | Alimentazione | ±15 V regolati | ADR-003 |
| E8 | Accoppiamento d'uscita | Capacitivo: 4,7 µF principale, 2,2 µF uscite fisse | ADR-007 |

**Nota su E5.** Con il guadagno del finale (21,1×) e le Heresy a
96 dB/1W/1m, 10 µV in uscita dal preamplificatore producono circa
**+13 dB SPL a 1 m**, cioè ~+4 dB in poltrona a 3 m — ben sotto il
rumore di fondo di una stanza silenziosa (25-30 dB SPL). A 2 µV si
scende a −0,5 dB SPL a 1 m. Il margine è ampio ma **non illimitato**: le
trombe da 96 dB rendono il rumore più udibile che su diffusori normali,
quindi il target va rispettato, non trattato come formalità.

## Requisiti di topologia

| # | Requisito | ADR |
|---|---|---|
| T1 | **Classe A pura, tutto a discreti.** Nessun operazionale nel percorso del segnale | ADR-003 |
| T2 | **Nessun servo di continua** (sarebbe un operazionale mascherato) | ADR-007 |
| T3 | **Un solo blocco di guadagno**, progettato una volta, usato due volte per canale | ADR-006 |
| T4 | Coppia JFET d'ingresso: **LSK489 duale monolitico** — appaiamento intrinseco, supera il "stesso lotto" di ADR-005 | ADR-013 |
| T5 | Buffer d'ingresso **unico**, uscite fisse via resistenze di isolamento ~100 Ω | ADR-008 |
| T6 | **Coppia d'ingresso cascodata** in entrambi i blocchi | ADR-014 |

## Requisiti fisici e di sicurezza

| # | Requisito | ADR |
|---|---|---|
| P1 | **Telaio unico**, alimentatore a bordo | ADR-010 |
| P2 | **Analisi di sicurezza rete obbligatoria** — assente = BLOCK automatico a G3 | ADR-010 |
| P3 | Trasformatore toroidale, massima distanza e orientamento ottimale rispetto agli ingressi | ADR-010 |
| P4 | Due circuiti stampati (alimentazione / audio), massa a stella | ADR-010 |
| P5 | Ventilazione prevista: ~3-4 W in mobile chiuso | ADR-010 |
| P6 | **Condensatori di segnale e resistenze critiche facilmente sostituibili** — passi multipli, per permettere all'utente di provare per ascolto | vedi nota |

**Nota su P6.** Nessun agente di questo progetto giudica come suona un
circuito: è una regola di `AGENTS.md`. La valutazione soggettiva spetta
all'utente, sull'hardware reale. Il progetto la serve rendendo lo scambio
dei componenti **banale invece che richiedere un dissaldatore**.

## Requisiti di verifica

Nascono da una conseguenza scoperta tardi: il relè di ADR-004 **commuta
la rete di controreazione**, e la capacità d'ingresso (ADR-014) forma un
polo con quella rete. Impedenza diversa significa **polo in posizione
diversa**, quindi **margine di fase diverso nelle due modalità di
guadagno**.

Non c'è un caso di stabilità da verificare: ce ne sono molti. Se non
sono enumerati qui, verrà verificata solo la configurazione in cui il
circuito passa il test.

### V1 — Stabilità in tutte le configurazioni statiche

Il margine di fase va misurato per **ogni combinazione** di:

| Variabile | Valori da coprire |
|---|---|
| Blocco | A (buffer, guadagno 1) · B a 0 dB · B a **+10 dB** |
| Posizione dell'attenuatore | minimo · **metà corsa (Zout massima, 2,5 kΩ)** · massimo |
| Carico d'uscita | cj 100 kΩ · Stax ~50 kΩ · Singxer (Zin ignota) · **carico capacitivo** (cavo, spazzata di lunghezza) |
| Sorgente a monte | phono 430 Ω · K11 <1,5 Ω · le tre posizioni del trim |

La posizione dell'attenuatore **non è un dettaglio**: la sua impedenza
d'uscita varia da ~0 a 2,5 kΩ e ritorno, quindi **il margine di fase
varia con la manopola del volume**.

### V2 — Stabilità ai transienti di commutazione

Comportamento dinamico durante e dopo ogni commutazione:

- **Relè del guadagno (0 ↔ +10 dB).** Vincolo di progetto: la rete va
  disposta in modo che **l'anello di controreazione non si apra mai**
  durante la transizione. Concretamente: il relè commuta la resistenza
  verso massa (R_g), mentre R_g mai in serie all'anello — così a
  contatti aperti il guadagno è 1 e l'anello resta chiuso. Se si
  commutasse R_f, l'anello si aprirebbe e lo stadio sbatterebbe contro
  un rail. **Da verificare sul circuito, non da assumere.**
- **Relè del selettore d'ingresso**: commutazione a caldo fra sorgenti,
  con l'eventuale carica residua sui condensatori di accoppiamento a
  monte.
- **Relè di mute** (ADR-012): il transitorio all'inserzione e al
  rilascio.
- **Accensione e spegnimento**: salita e discesa asimmetrica dei rail.

### V3 — Recupero dalla saturazione

Un amplificatore discreto retroazionato può impiegare molto tempo a
riprendersi da un sovraccarico, o restare agganciato. Da verificare
esplicitamente. Nota di margine: a +10 dB con il K11 a fondo scala
l'uscita sarebbe 2,7 × 3,16 = **8,5 V**, contro rail a ±15 V — margine
adeguato ma non enorme, e quella combinazione è raggiungibile per errore.

### V4 — Le misure audio

THD/THD+N, risposta, rumore in banda (target E5), PSRR, Zout in
funzione della frequenza. Ognuna con la **provenienza del modello**
dichiarata accanto: una cifra di distorsione ottenuta da un modello
trascritto a mano da PDF (ADR-013) va riportata con quel caveat.

### V5 — Equivalenza fra netlist SPICE e netlist KiCad

La Fase 2 **non** ha usato il percorso documentato
`generate_schematic()` → `kicad-cli sch export netlist --format spice`:
per ~40 componenti finisce dritto nelle limitazioni #3 e #5. Al suo
posto `circuits/preamp/spice_export.py` percorre gli stessi oggetti
`Part`/`Net` di SKiDL, quindi **la definizione della topologia resta
una sola**.

Ma il rischio si sposta sull'esportatore: un suo difetto farebbe
divergere ciò che si simula da ciò che si manda in produzione, **senza
errori da nessuna delle due parti**. Non è teorico — è già successo una
volta in Fase 2 con i suffissi dei valori (vedi `docs/limitations.md`
#13), ed è rimasto invisibile per diverse analisi.

Prima di G2, le due netlist vanno **confrontate per equivalenza
topologica**, non lette a occhio: stessi nodi, stessi collegamenti,
stessi valori tradotti correttamente. È un controllo automatizzabile e
va automatizzato.

## Architettura

```
 phono ECC82 ──┐
 K11 R2R    ───┤  selettore    trim      BLOCCO A          ┌─100Ω─C 2,2µ─[mute]──► Singxer SA-1
 (spare)    ───┤   a relè    0/-6/-12   guadagno 1         ├─100Ω─C 2,2µ─[mute]──► Stax SRM-T1
 (spare)    ───┘             per ingr.  Zin ≥ 100k         │
                                                            └── ATTENUATORE ── BLOCCO B ── C 4,7µ ─[mute]──► cj EV250
                                                                 10k, a scatti   0/+10 dB
                                                                                 relè su feedback
```

Due blocchi identici per canale, quattro in totale.

## Requisiti espliciti di NON-obiettivo

- Nessun ingresso o uscita bilanciata.
- Nessuno stadio phono integrato (l'utente ne ha già uno).
- Nessun controllo di tono, filtro o loudness.
- Nessun telecomando, nessuna interfaccia digitale.

## Aperti

| Cosa | Impatto | Assegnato a | Stato |
|---|---|---|---|
| ~~Conferma specifiche cj EV250~~ | Struttura di guadagno | utente | **CHIUSO** — email costruttore + manuale MV50, vedi report 2026-09-08 |
| Impedenza d'**ingresso** Singxer SA-1 V2 | Dimensionamento C uscita fissa | Fase 1 | **NON PUBBLICATA.** Verificato sul manuale ufficiale. Vie residue: chiedere a Singxer, misurare, o adottare 4,7 µF e chiudere la questione |
| ~~Scelta del JFET d'ingresso~~ | Topologia dello stadio d'ingresso | utente | **CHIUSO** — **LSK489**, vedi ADR-013 |
| Valore del cap d'uscita del phono a valvole | Verifica del margine su E3 | utente | **RINVIATO** — non ha accesso agli schematici né può aprire agevolmente il telaio. Non blocca: E3 ≥ 100 kΩ copre il caso peggiore ragionevole |
| ~~Modello SPICE LSJ74~~ | — | — | **DECADUTO** — LSJ74 non è più in progetto (ADR-013) |
| Trascrizione del modello LSK489 da PDF | Credibilità della simulazione di distorsione | Fase 2 | **APERTO** — procedura obbligatoria in ADR-013, con controllo incrociato su datasheet |
