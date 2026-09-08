# STATE — Preamplificatore di linea

**Leggi questo per primo** riprendendo il progetto.

**Documento vivo**: ogni sessione che tocca il preamp lo aggiorna prima
di chiudere, e lo committa insieme al lavoro. Se è disallineato dalla
realtà, il progetto non è ripartibile.

Ultimo aggiornamento: **2026-09-08** (bozza di topologia consegnata)

---

## Dove siamo

**Fase 2: bozza di topologia consegnata. In attesa della Fase 3.**

Le Fasi 0 e 1 sono chiuse. **Quattordici** decisioni sono in
`decisions/`.

`circuits/preamp/` **esiste ed è la fonte di verità**:

| File | Cosa |
|---|---|
| `gain_block.py` | il blocco di guadagno (ADR-006), 44 componenti |
| `preamp_audio.py` | due canali, quattro blocchi, relè condivisi (205 comp.) |
| `spice_export.py` | esportatore SKiDL -> ngspice |

I banchi di prova stanno in `spice/preamp/tb/` (11 deck) e i modelli
segnaposto in `spice/preamp/placeholder_devices.lib` — **deliberatamente
fuori da `models/`**, che resta a 24/24.

**Tutte le cifre prodotte in Fase 2 sono PREVISIONI da modelli
segnaposto scritti a mano.** Nessuna cifra di distorsione esiste: il
`.four` gira ma il suo risultato è privo di significato. La verifica
indipendente è la Fase 5.

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
| 2 | Bozza di topologia in `circuits/preamp/` | `analog-topology-designer` | **fatto** |
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

**Fase 3, giro componenti.** La bozza chiede a
`bom-component-manager` cose che la Fase 1 non copriva:

- **2N5401** (VAS) e **2N5551** (cascode, generatori, moltiplicatore di
  Vbe): parti nuove, non verificate in Fase 1.
- **Modello SPICE LSK489**, procedura obbligatoria di ADR-013.
- **THAT320**: stock non ancora fissato, e va confermata la BVceo.
- **Omron G6K-2F-Y**: confermare quale contatto è NO e quale NC. Il
  progetto fallisce in sicurezza solo se sono quelli giusti.
- **Simbolo KiCad dell'LSK489**: non esiste. Oggi il duale è disegnato
  come due JFET separati. Va creato un simbolo a 2 unità con il pinout
  letto dal datasheet **prima del G2**, o il PCB piazzerà due package.

Due tensioni fra requisiti sono state **segnalate, non aggirate**:

1. **E6 x E2 contro E7.** 2,7 V RMS a +10 dB vogliono 8,54 V RMS in
   uscita; con rail a ±15 V il blocco clippa a 9,31 V RMS simulati.
   Margine 0,75 dB. Il rimedio previsto è il trim di ADR-011 (-6 dB
   sull'ingresso del K11). Decisione dell'utente.
2. **E4 contro E8 a 20 Hz.** Con accoppiamento capacitivo la |Zout| al
   jack a 20 Hz è ~1,7 kΩ (è la reattanza del 4,7 µF). A 1 kHz è
   58,8 Ω. E4 letta alla lettera non è soddisfacibile a 20 Hz da nessun
   circuito con condensatore d'uscita.

Decisione minore ancora aperta: portare a **4,7 µF** anche il
condensatore verso il Singxer, visto che la sua impedenza d'ingresso non
è pubblicata.

## Domande aperte

| Cosa | Chi risponde | Blocca? |
|---|---|---|
| Condensatore verso il Singxer: 2,2 o 4,7 µF | utente | No |
| Trascrizione del modello LSK489 da PDF | Fase 2 | No, ma **la credibilità della distorsione ci poggia sopra** |
| Impedenza d'ingresso Singxer SA-1 V2 | — | **Non pubblicata**, verificato sul manuale ufficiale |
| Valore del cap d'uscita del phono a valvole | utente | **Rinviata** — non ha accesso agli schematici né può aprire agevolmente il telaio |
| ~~Quale JFET d'ingresso~~ | — | **CHIUSA**: LSK489 (ADR-013) |
| ~~Conferma specifiche cj EV250~~ | — | **CHIUSA**: email costruttore + manuale MV50 |

## Decisioni che aspettano l'utente

| Cosa | Perché |
|---|---|
| **Rail ±15 V o ±18 V** | A +10 dB con il K11 a fondo scala restano **0,75 dB** di margine prima del clipping. Mitigato dal trim di ADR-011 a −6 dB, che da comodità è diventato **portante**. ±18 V darebbero ~11,4 V RMS ma contraddicono E7 e vogliono una ADR |
| Condensatore verso il Singxer: 2,2 o 4,7 µF | La sua impedenza d'ingresso non è pubblicata |

## Attenzione per chi riprende

`REQUIREMENTS.md` contiene ora una sezione **Requisiti di verifica**
(V1–V4). Non è burocrazia: il relè del guadagno commuta la rete di
controreazione, quindi **il margine di fase è diverso nelle due
modalità**, e l'impedenza dell'attenuatore varia con la manopola, quindi
**varia anche con la posizione del volume**. Se non si verifica tutta la
matrice, si verifica solo il caso in cui il circuito passa.

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
