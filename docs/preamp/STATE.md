# STATE — Preamplificatore di linea

**Leggi questo per primo** riprendendo il progetto.

**Documento vivo**: ogni sessione che tocca il preamp lo aggiorna prima
di chiudere, e lo committa insieme al lavoro. Se è disallineato dalla
realtà, il progetto non è ripartibile.

Ultimo aggiornamento: **2026-09-08** (dopo la Fase 1)

---

## Dove siamo

**Fase 1 chiusa. In attesa di una decisione dell'utente prima della
Fase 2.**

Le Fasi 0 e 1 sono chiuse. Dodici decisioni sono in `decisions/`.
Nessun circuito è ancora stato disegnato: `circuits/preamp/` non esiste.

**Esito Fase 1: la topologia regge — le parti esistono.** Il punto debole
non è l'approvvigionamento ma la **provenienza dei modelli SPICE**, cioè
l'opposto di quanto temuto. Vedi
`reports/2026-09-08-fase1-parti-critiche.md`.

**Il finale è stato identificato**: il cj Evolution 250 è un **MV50
riconfigurato in triodo**, 30 W, Zin 100 kΩ confermata dal manuale
ufficiale. La diagnosi di ADR-001 regge su tutto l'intervallo plausibile
di sensibilità. Vedi `reports/2026-09-08-identificazione-cj-ev250.md`.

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
| 1 | Verifica parti critiche (JFET, BJT, modelli SPICE vendor) | `bom-component-manager` | **fatto** |
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

**Serve una decisione dell'utente: quale JFET d'ingresso.** È un
compromesso fra genealogia e verificabilità della simulazione, e va
registrato in una ADR nuova (sarà la 013) prima di disegnare.

| Candidato | Pro | Contro |
|---|---|---|
| **LSK170 + LSJ74** | La genealogia 2SK170/2SJ74; complementari veri; in stock | Modello SPICE è un **PDF da trascrivere a mano**; **il modello LSJ74 non è confermato** |
| **LSK489** (duale monolitico N) | Appaiamento e tracking termico **intrinseci**: elimina il problema del lotto | Stesso problema del modello PDF; niente complementare P |
| **TI JFE2140** (duale monolitico N) | **Modelli SPICE nativi TI, verificati**; il più economico | Nessuna genealogia audio; polarizzazioni da ricalcolare; niente complementare P |

Chiuso questo, si passa alla **Fase 2**: `analog-topology-designer`
scrive il blocco in `circuits/preamp/`.

Da decidere in parallelo, minore: portare a **4,7 µF** anche il
condensatore verso il Singxer, visto che la sua impedenza d'ingresso non
è pubblicata. Costa ingombro, elimina il rischio, aggiorna ADR-007.

## Domande aperte

| Cosa | Chi risponde | Blocca? |
|---|---|---|
| **Quale JFET d'ingresso** | **utente** | **Sì — blocca la Fase 2** |
| Condensatore verso il Singxer: 2,2 o 4,7 µF | utente | No |
| Modello SPICE LSJ74 (link non risolto) | Fase 2/3 | Solo se si sceglie LSJ74 |
| Impedenza d'ingresso Singxer SA-1 V2 | — | **Non pubblicata**, verificato sul manuale. Chiedere a Singxer o misurare |
| Conferma specifiche cj EV250 | — | **CHIUSA**: email costruttore + manuale MV50 |
| Valore del cap d'uscita del phono a valvole | utente | **Rinviata** — non ha accesso agli schematici né può aprire agevolmente il telaio. Non blocca |

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
   Poi `2026-09-08-identificazione-cj-ev250.md` (il finale è un MV50 in
   triodo) e `2026-09-08-fase1-parti-critiche.md` (cosa esiste davvero).
4. `decisions/README.md` e le ADR — perché il circuito è così.
5. `../../CLAUDE.md` — l'ambiente EDA, se non lo conosci.
