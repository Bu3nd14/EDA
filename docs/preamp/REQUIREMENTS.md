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
| E4 | Impedenza d'uscita | **< 100 Ω**, costante con la posizione del volume | ADR-002 |
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
| T4 | Coppia JFET d'ingresso: **stessa gradazione**, non appaiamento di precisione | ADR-005 |
| T5 | Buffer d'ingresso **unico**, uscite fisse via resistenze di isolamento ~100 Ω | ADR-008 |

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
| Scelta del JFET d'ingresso | Topologia dello stadio d'ingresso | **utente** | **APERTO** — LSK170/LSJ74 vs LSK489 vs JFE2140, vedi report Fase 1. Richiede una ADR |
| Valore del cap d'uscita del phono a valvole | Verifica del margine su E3 | utente | **RINVIATO** — non ha accesso agli schematici né può aprire agevolmente il telaio. Non blocca: E3 ≥ 100 kΩ copre il caso peggiore ragionevole |
| Modello SPICE LSJ74 | Credibilità della simulazione di distorsione | Fase 2/3 | **APERTO** — link non risolto in Fase 1 |
