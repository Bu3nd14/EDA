# ADR-058 — La cella del mute è la NSL-32SR3 di Advanced Photonix, modellata da dati pubblicati e da ipotesi dichiarate; il sorgente e le misure passano a L47b

Data: 2026-10-02 · Stato: accettata — supera in parte ADR-038 e ADR-039 sulla sola parte

## Contesto

Il mute graduale (ADR-038, ADR-039) usa per canale due VTL5C4 dell'Excelitas, una in serie e
una verso massa all'ingresso del blocco A. La serie VTL è fuori produzione dal 2015: NC-043,
**bloccante per G2**, perché il layout ha bisogno del pezzo vero. È la condizione «Da riaprire
se» di ADR-038: «la VTL5C4 non si trova, e nessuna parte con curva pubblicata la sostituisce».
L'utente ha diviso L47 in due il 2026-10-02: **L47a** la parte e il suo modello, **L47b** il
tempo del mute, il pilota e le misure. Il tempo massimo del mute lo fissa dopo la tabella.

## Decisione

**La cella del mute è la NSL-32SR3** (Advanced Photonix, già Silonex e Luna). Il suo modello è
`models/optocoupler/nsl32sr3_comportamentale.lib`, comportamentale, da dati pubblicati con
ipotesi dichiarate. L'utente non può misurare dei campioni.

Le parole dell'utente, alla domanda con la tabella: «la NSL-32SR3 può andare bene, ma non posso
misurare la curva, quindi dovremo cercare in rete o fare assunzioni oppure cercare un altro
modello». La ricerca in rete ha trovato abbastanza dati per un modello. Il sorgente non cambia
in L47a.

## Perché

**È l'unica sostituta acquistabile da un distributore.** DigiKey la dà a 7867 pezzi, $4,11,
Active, con 10 settimane di consegna (verificato il 2026-10-02).

**Al buio basta, con un calcolo.** Col mute inserito, prima che chiuda il relè al jack, la
musica che passa è il rapporto fra la cella in derivazione accesa e quella in serie al buio.
Col caso peggiore di +10 dB di guadagno e 2,7 V RMS alla sorgente:

| Cella | Accesa / al buio | Residuo al jack | dB SPL |
|---|---|---|---|
| VTL5C4 | ~110 Ω / 400 MΩ | ~3 µV | ~4 |
| **NSL-32SR3** | ~90 Ω / ≥ 25 MΩ | ~43 µV | **~26** |

Il limite di B è 100 µV, ~33 dB SPL, la stanza silenziosa. È un calcolo, non una misura: lo
misura L47b.

**È veloce.** Scende a 100 kΩ in 10 ms, contro 1,5 s della VTL5C4: non limita un mute più
corto (NC-045). La gradualità la dà tutta il pilota.

**I dati per il modello esistono, ma sono pochi.** Le fonti, in ordine di autorità:
- il **grafico tipico del costruttore** (Silonex 104058 Rev 07, cinque punti da 0,1 a 40 mA),
  letto a pixel;
- **una cella misurata** da JC Maillet (2008, dieci punti da 2 mA a 2,5 µA). È l'unico dato
  pubblico nella regione da kΩ a MΩ, dove sta la dissolvenza;
- la **dispersione di 61 pezzi** di Maillet (2014), misurata a due sole correnti: 103–289 Ω a
  2 mA, 16–89 kΩ a 10 µA, non correlate fra loro.

Il modello è verificato contro tutte e tre:
- **statica 84/84**: i nodi entro lo 0,05 %, il buio, i 60 Ω massimi a 20 mA, l'inviluppo dei
  61 pezzi;
- **dinamica 5/5** entro il 3 %: salita al 63 % in 5 ms, 100 kΩ a 10 ms, 25 MΩ a 10 s;
- **quattro sabotaggi**, tutti rilevati;
- **`validate_models.py`** 59/59.

Dettaglio in `reports/2026-10-02-L47a-cella-mute.md`.

## Alternative scartate

- **La riedizione Xvive della VTL5C4.**
  - Il suo datasheet vero (5C4-R) dà **2 MΩ tipici** al buio. Quello che i rivenditori
    ospitano è la pagina Excelitas col titolo cambiato.
  - Il residuo calcolato è ~1,3 mV, **~55 dB SPL**, oltre il limite di 33.
  - Si trova solo da rivenditori per hobbisti. Il LED è al limite a 60 °C.
- **NSL-37V5C4** (Advanced Photonix). Il nome promette una VTL5C4, ma le fonti del costruttore
  si contraddicono.
  - La tabella web dà 400 MΩ minimi al buio.
  - Il PDF dà **400 kΩ**, in intestazione e in tabella. È coerente con la sua dinamica di 75 dB
    dichiarata (buio sopra ~100 Ω a 20 mA).
  - Nessuno stock da DigiKey, nessun grafico. Si scarta per la disponibilità; la contraddizione
    la rende comunque inaffidabile.
- **CoolAudio VTL5C3.** È l'unica della serie che CoolAudio fa: 10 MΩ al buio e 30 kΩ a 1 mA.
- **NSL-32, NSL-32SR2.** Vanno al buio solo a 0,5 e 1 MΩ.
- **Chiedere una cella al costruttore** (il datasheet AP: «for Audio applications, contact
  techsupport»). Avrebbe fermato il lotto senza una data.

## Le ipotesi del modello

Tutte dichiarate nell'intestazione del `.lib`:
- **una sola cella misurata nella regione del mute**: la forma della curva fra 0,1 mA e 2,5 µA
  è di un esemplare. La dispersione è nota solo a due correnti;
- **sotto 2,5 µA** la pendenza dell'ultimo tratto fino a 25 MΩ, il minimo, poi costante;
- **lo spegnimento oltre 100 kΩ** al tasso più lento compatibile con 25 MΩ a 10 s
  (0,238 decadi/s). È pessimistico per il residuo, come nel modello della VTL5C4;
- **le capacità** della cella (5 pF) e ingresso-uscita (0,5 pF) sono quelle della VTL5C4:
  non sono pubblicate. La seconda conta per E3 ed E5;
- **il LED** è il diodo della VTL5C4 più 42,5 Ω in serie, per i 2,5 V massimi a 20 mA;
- **nessuna temperatura** (0,7 %/°C tipici, dichiarati), nessuna memoria della luce,
  distorsione o rumore.

## Cosa resta aperto per L47b

- **Il sorgente.** Parte, valore e footprint delle due celle per canale (`ls` e `lp` in
  `preamp_audio.py`): l'impronta è `OptoDevice:Luna_NSL-32`, presente in KiCad 10, al posto di
  `PerkinElmer_VTL5C`, col simbolo `Isolator:NSL-32` che la nomina.
  - Le piazzole hanno 3,81 mm fra i terminali del LED e 2,53 mm fra quelli della cella, a
    10,16 mm. Il disegno Silonex dà ~3,3 e 2,54 mm.
  - I terminali sono assiali, lunghi almeno 25 mm, e si piegano. Il passo e la piedinatura del
    simbolo vanno comunque confrontati col disegno prima di L49.
- **La cima della corrente del LED** (ADR-050, 12 mA).
  - Il datasheet non pubblica un declassamento della corrente del LED: la nota «derate
    linearly to 0 at 75 °C» è attaccata alla sola dissipazione della cella.
  - Se si legge per il LED, da 25 mA a 23 °C, a 60 °C restano **~7,2 mA**, sotto i 12.
  - Da decidere con l'utente: un'ipotesi dichiarata, oppure una domanda al costruttore.
  - Cambia la cella accesa, quindi il residuo.
- **La caduta dei LED.** Due LED in serie fra i canali (ADR-039) cadono fino a 2 × 2,5 V,
  contro 2 × 2,0 V della VTL5C4. Il commento di `psu.py` alla riga 182 cita la VTL5C4.
- **Il profilo del mute** (v4, ADR-039 e ADR-040) è tarato sulla curva della VTL5C4: va rifatto
  sull'inviluppo della NSL-32SR3, che nella regione del mute è largo ~5,5× fra gli estremi.
- **Le misure**: S su `tb_v2_casopeggiore.cir` sulle cinque curve, B del residuo, E3 ed E5
  (che dipendono dagli 0,5 pF ipotizzati).

## Da riaprire se

- L47b misura **B fuori** per la coda dello spegnimento ipotizzata, o per i soli 25 MΩ del buio.
- Advanced Photonix dichiara la NSL-32SR3 a fine vita, o il lead time diventa inaccettabile.
- Il prototipo misura celle **fuori dall'inviluppo** A–E, o una forma della curva diversa da
  quella della cella di Maillet nella regione del mute.
- Il costruttore pubblica una curva sotto 0,1 mA, il declassamento del LED o le capacità: il
  generatore si rigenera da lì.
