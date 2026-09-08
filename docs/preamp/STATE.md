# STATE — Preamplificatore di linea

**Leggi questo per primo** riprendendo il progetto.

**Documento vivo**: ogni sessione che tocca il preamp lo aggiorna prima
di chiudere, e lo committa insieme al lavoro. Se è disallineato dalla
realtà, il progetto non è ripartibile.

Ultimo aggiornamento: **2026-09-08**

---

## Dove siamo

**Fase 1 — verifica delle parti critiche.** In corso.

La Fase 0 (requisiti) è chiusa e i requisiti sono congelati. Dodici
decisioni sono registrate in `decisions/`. Nessun circuito è ancora
stato disegnato: `circuits/preamp/` non esiste.

## Il progetto in una frase

Preamplificatore di linea a **guadagno unitario**, Classe A pura a
componenti discreti senza operazionali, per sostituire un Technics
SU-9070 la cui struttura di guadagno sbagliata (46 dB di attenuazione
richiesta) è stata identificata come causa misurabile della mancanza di
dinamica lamentata.

## Il piano

| Fase | Cosa | Owner | Stato |
|---|---|---|---|
| 0 | Requisiti | orchestratore + utente | **fatto** |
| 1 | Verifica parti critiche (JFET, BJT, modelli SPICE vendor) | `bom-component-manager` | **in corso** |
| 2 | Bozza di topologia in `circuits/preamp/` | `analog-topology-designer` | da fare |
| 3 | Giro componenti completo | `bom-component-manager` | da fare |
| 4 | Revisione della topologia alla luce dei componenti | `analog-topology-designer` | da fare |
| 5 | Misure (stabilità per prima) | `measurement-analyst` | da fare |
| 6 | Alimentatore + **sicurezza rete** — parte in parallelo dalla Fase 2 | `psu-engineer` | da fare |
| **G1** | Congelamento topologia | `design-reviewer` | da fare |
| — | Layout → **G2** → fabbricazione → **G3** | | da fare |

**Perché la Fase 1 viene prima della bozza**: se i JFET complementari non
esistono, l'intero stadio d'ingresso cambia forma. Meglio saperlo prima
di disegnare tutto attorno a loro.

**Perché G1 viene dopo il giro componenti**: congela una topologia che
sappiamo costruibile con parti che esistono davvero, non una disegnata
sulla carta.

## Prossimo passo concreto

Attendere l'esito della Fase 1. Poi, a seconda del risultato:

- **Parti confermate** → Fase 2, `analog-topology-designer` scrive il
  blocco in `circuits/preamp/`.
- **Parti non disponibili** → nuova ADR che registra il ripiego, e
  revisione di ADR-005 / ADR-006 prima di disegnare.

## Domande aperte

| Cosa | Chi risponde | Blocca? |
|---|---|---|
| Impedenza d'**ingresso** del Singxer SA-1 V2 | Fase 1 | No — dimensiona un condensatore |
| Conferma delle specifiche cj EV250 dal manuale (670 mV / 100 kΩ / 25 W) | **utente** | No, ma **tutto il conto ci poggia sopra** |
| Valore del condensatore d'uscita del phono a valvole | **utente** | No — il requisito Zin ≥ 100 kΩ copre il caso peggiore ragionevole |

## Come è organizzata la documentazione

Tre cicli di vita, tenuti separati di proposito:

- **Vivi** — `STATE.md`, `REQUIREMENTS.md`. Riscritti, sempre veri al
  presente.
- **Immutabili** — `decisions/ADR-*.md`, i verdetti dei gate. Scritti una
  volta, mai corretti, solo superati da documenti nuovi.
- **Datati** — `reports/`. Output di un'esecuzione. Una misura è vera di
  una versione specifica del circuito: senza data è inutile.

I report di fase sono **cronaca**, non il posto dove si cerca il
"perché". Il perché sta nelle ADR.

## Da leggere per riprendere

1. Questo file.
2. `REQUIREMENTS.md` — cosa deve fare.
3. `reports/2026-09-08-analisi-catena.md` — la base di evidenza: i
   numeri della catena dell'utente e perché il progetto esiste.
4. `decisions/README.md` e le ADR — perché il circuito è così.
5. `../../CLAUDE.md` — l'ambiente EDA, se non lo conosci.
