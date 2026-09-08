# Analisi della catena esistente

Data: 2026-09-08 · Tipo: report (datato, non aggiornare — scriverne uno
nuovo se la catena cambia)

Questo documento è la **base di evidenza** su cui poggia tutto il
progetto. Non contiene decisioni: contiene i fatti da cui le decisioni
discendono. Se un domani cambiano diffusori o finale, questo documento
dice quali conclusioni cadono.

## Il sistema

| Ruolo | Apparecchio | Dato rilevante |
|---|---|---|
| Sorgente 1 | Phono MC a valvole, autocostruito ~2016 | Uscita a cathode follower su **ECC82** |
| Sorgente 2 | **FiiO K11 R2R** (+ Raspberry Pi / Volumio / Tidal) | Uscita di linea **2,7 V RMS** |
| Preamplificatore | **Technics SU-9070** (da sostituire) | **+16,5 dB** · Zout 600 Ω · max 20 V |
| Finale | **conrad-johnson Evolution 250 (EV250)** | 25 W/ch triodo · **sensibilità 670 mV** · **Zin 100 kΩ** · non invertente |
| Diffusori | **Klipsch Heresy I** | **96 dB / 1 W / 1 m** · 8 Ω nominali |
| Cuffie | Singxer SA-1 V2, Stax SRM-T1 | Entrambi con **proprio controllo di volume** |

## Il lamento soggettivo

L'utente giudica il Technics "poco lively, senza molta dinamica". Il
punto di partenza dell'analisi è stato cercare un meccanismo misurabile
dietro quel giudizio.

## Il conto

Guadagno di tensione del finale: 25 W su 8 Ω = 14,14 V, da 0,67 V
d'ingresso → **21,1×** (26,5 dB).

Per un ascolto normale (~85 dB in poltrona a ~3 m con diffusori da
96 dB/1W/1m) servono circa **0,5 W**, cioè 2,0 V ai morsetti, cioè
**95 mV** all'ingresso del finale.

Il Technics offre in uscita 2,7 × 6,67 = **18,0 V**.

Attenuazione richiesta: 20·log₁₀(18,0 / 0,095) = **45,6 dB**.

**La manopola del volume del Technics indicava 46 dB.**

Il modello della catena si chiude entro mezzo decibel. Non è una
coincidenza: conferma che il meccanismo è stato individuato
correttamente.

## Il meccanismo

Il K11 da solo ha già **12 dB più** di quanto il finale richieda per la
piena potenza. Il Technics ne aggiunge **altri 16,5**. Il potenziometro
deve buttarne via **46**, lavorando in fondo alla corsa — dove un
potenziometro logaritmico ha il tracking peggiore fra i canali (±2-3 dB
tipici) e la risoluzione più grossolana.

Si amplifica di 16,5 dB e se ne gettano 46. Ogni contributo di rumore e
distorsione dello stadio viene amplificato rispetto al segnale
effettivamente usato; l'immagine stereo vaga perché i due canali non
attenuano uguale; piccoli movimenti della manopola danno salti grossi.

**Non manca dinamica: se ne usa una fetta sottile, nel punto peggiore
della catena.**

## Verifica sperimentale

L'utente ha collegato il finale alla **REC OUT** del Technics — prelievo
**passivo**, come dimostra il fatto che **funziona a preamplificatore
spento** — pilotandolo con il volume interno del K11 in modalità PRE.

Configurazione risultante: K11 → selettore del Technics (solo contatto)
→ finale.

**Esito riportato**: scena più aperta, medio-alte più naturali e meno
chiuse, basso più profondo e più controllato, maggiore dinamica.

Livelli d'ascolto: **30-50 su 99** sulla scala del K11. Compatibile con
passi da ~0,5 dB:

| Volume K11 | Attenuazione | Potenza | SPL in poltrona |
|---|---|---|---|
| 30 | −34 dB | 0,16 W | ~81 dB |
| 40 | −29 dB | 0,5 W | ~85 dB |
| 50 | −24 dB | 1,6 W | ~91 dB |

**Limite del test**: sono cambiate **due cose insieme** — sono spariti
gli stadi attivi *e* si è spostato il controllo di volume fuori dalla
zona peggiore. Il risultato conferma l'ipotesi nel complesso ma non dice
quale delle due pesasse di più. Per il progetto non cambia nulla:
puntano nella stessa direzione.

## Verifiche collaterali

**La potenza non è il problema.** Era stato sollevato il dubbio che
25 W in triodo fossero pochi e che si stesse sentendo il clipping del
finale. Con le Heresy a 96 dB/1W/1m i 25 W darebbero **110 dB a un
metro**; l'utente ne usa meno di uno. Headroom abbondante.

**Ma le Heresy rendono udibile tutto ciò che sta a monte**, rumore
compreso. Sono diffusori che raccontano esattamente cosa fa il
preamplificatore — il motivo per cui un difetto che su diffusori da
87 dB passerebbe inosservato qui si sente bene.

**Impedenza d'uscita del phono**: un cathode follower su ECC82 ha
Zout ≈ r_p/(μ+1) ≈ 7,7 kΩ/18 ≈ **430 Ω**. Bassa. Ma il catodo sta a
tensione continua positiva, quindi **c'è quasi certamente un
condensatore di accoppiamento in uscita**: con 10 kΩ di carico e un cap
da 0,47 µF il taglio sarebbe a 34 Hz. Da qui il requisito **Zin ≥ 100 kΩ**
del nuovo preamplificatore. Inoltre un cathode follower eroga corrente
generosamente ma ne assorbe solo quanta gliene concede la resistenza di
catodo: su carico basso diventa asimmetrico.

## Ipotesi concorrente, non esclusa

Il SU-9070 ha 45+ anni. Nel 1978 misurava 0,003% di THD; oggi i suoi
elettrolitici hanno avuto una vita lunga. Parte del degrado potrebbe
essere invecchiamento e non progetto. **Il problema di struttura del
guadagno esiste comunque ed è indipendente dall'età dell'apparecchio.**

## Dati non verificati

- ~~Le specifiche del cj Evolution 250 (670 mV, 100 kΩ, 25 W) provengono
  da schede online e da annunci d'asta, non dal costruttore.~~
  **RISOLTO in giornata** — vedi `2026-09-08-identificazione-cj-ev250.md`.
  L'EV250 è un **MV50 in triodo**, dato per **30 W** dal costruttore;
  **Zin 100 kΩ confermata** dal manuale ufficiale MV50. La sensibilità
  resta non pubblicata ma delimitata fra 612 e 750 mV — intervallo
  troppo stretto per cambiare qualsiasi conclusione.
- L'impedenza d'**ingresso** del Singxer SA-1 V2 **non è pubblicata** —
  confermato leggendo il manuale ufficiale (Fase 1). Non è un limite
  della ricerca: il dato non esiste in forma pubblica.
- Il valore del condensatore d'uscita del phono dell'utente non è noto.

## Fonti

- conrad-johnson Evolution 250: [Catawiki](https://www.catawiki.com/en/l/103081732-conrad-johnson-evolution-250-tube-power-amplifier) · [Lot-Art](https://www.lot-art.com/auction-lots/Conrad-Johnson-EV250-Tube-power-amplifier/100909736-conrad_johnson-15.2.26-catawiki)
- FiiO K11 R2R: [parametri ufficiali](https://www.fiio.com/k11r2r_parameters) · [modalità PO/LO/PRE](https://www.fiio.com/newsinfo/934272.html)
- Technics SU-9070: [audio-database](https://audio-database.com/TechnicsPanasonic/amp/su-9070-e.html) · [Stereo Review 1978](https://www.worldradiohistory.com/hd2/IDX-Audio/Archive-Stereo-Review-IDX/IDX/70s/HiFi-Stereo-Review-1978-04-OCR-Page-0040.pdf)
- Klipsch Heresy: [Vintage Technology Archive](https://vintagetechnologyarchive.com/audio/klipsch/heresy/)
- Singxer SA-1 V2: [Audiophonics](https://www.audiophonics.fr/en/desktop-headphone-amplifiers/singxer-sa-1-v2-p-18558.html)
- Stax SRM-T1: [HiFi Engine](https://www.hifiengine.com/manual_library/stax/srm-t1.shtml)
