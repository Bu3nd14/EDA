# L55 — il dispositivo d'uscita del blocco di taglia driver (NC-056)

Data: 2026-10-29. Agente: approvvigionamento (modelli e parti). Nessun circuito è stato toccato: i
MJE15032/33 restano nel sorgente fino al banco del blocco con la coppia nuova e alla decisione
dell'utente.

## Esito in una riga

**Coppia scelta: onsemi MJE243G (NPN) / MJE253G (PNP), TO-225.** Passa T7 (modello servito da onsemi) e
T8 (Active sulla pagina di onsemi), ha scorte franchised per entrambe le polarità, i due modelli sono
dentro ogni finestra del datasheet, e a 20 mA la capacità di ingresso del modello scende da 8,1 nF a
1,7 / 2,2 nF. **Non è la coppia più veloce** (i ZXT25040DZ restano migliori sulla carta, ma l'utente li ha
scartati in ADR-054 per il PNP e il SOT-89): è la sola che regge T7 + T8 + disponibilità di entrambe le
polarità + un termico chiudibile con un dissipatore da catalogo. Un secondo candidato non c'è: tutti gli
altri cadono su un criterio duro (tabella).

## 1. I vagliati, criterio per criterio

T7 = modello SPICE servito dal costruttore. T8 = nessun fine vita / NRND / last shipments **sulla pagina del
costruttore**. «Mod. fisico» = il modello dà Vbe plausibile (≈0,6 V) a 20 mA. Cifre di modello da
`misure.txt` (stesso script per tutti: IC = 20 mA, VCE = 15 V, 25 °C).

| Candidato | T7 modello del costruttore | T8 stato (fonte) | Scorte, entrambe le polarità | V_CEO / I_C | Cpi a 20 mA, Cmu | fT a 20 mA (incrocio) | Esito |
|---|---|---|---|---|---|---|---|
| **MJE243G / MJE253G** onsemi TO-225 | **sì**, `/download/models/lib/mje243.lib`, `mje253.lib` (MODPEX 2003) | **Active** (JSON-LD e badge di onsemi, 2026-10-29) | **sì**: MJE243G Farnell 4908, TME 823; MJE253G Farnell 709, TME 292, RS 520 (findchips, 2026-10-29) | 100 V / 4 A, V_EBO 7 V | 1,70 / 2,19 nF; 21 / 15 pF | 88 / 61 MHz | **SCELTI** |
| MJE182G / MJE172G onsemi TO-126 | sì (MODPEX 2004) | Active (onsemi, 2026-10-29) | non verificate | 80 V / 3 A | 1,15 / 1,01 nF; 9 / 18 pF | 103 / 88 MHz | **scartati: il modello non è fisico** — Vbe = 0,92 / 0,90 V a 20 mA (IS = 1e-17); il datasheet è di Fairchild 2001 (Rev. A2) |
| MJD243 onsemi DPAK (NPN) | sì | non letto | — | 100 V / 4 A | 3,73 nF; 22 pF | 49 MHz | scartato: Cpi doppia dei MJE243, e **il modello del PNP MJD253 non esiste** (`/download/models/lib/mjd253.lib` risponde 302) |
| MJE340 / MJE350 onsemi TO-225 | sì | non letto | — | 300 V / 0,5 A | 0,82 / 0,93 nF; 3,3 pF | 117 / 122 MHz | scartati: il modello ha CJE = CJC = 10 pF, TF = 1 ns, **numeri tondi**, e il datasheet (Fairchild 2001) non pubblica né fT né C_ob: niente contro cui controllare; I_C ai limiti (0,5 A) |
| D44H11 / D45H11 onsemi TO-220 | sì | non letto | — | 80 V / 10 A | 4,0 / 5,0 nF; 92 / 169 pF | 29 / 28 MHz | scartati: più capacità del MJE15032 in Cmu; il D45H11 ha Vbe = 0,41 V a 20 mA |
| MJD44H11 / MJD45H11 onsemi DPAK | sì | non letto | — | 80 V / 8 A | 7,8 / 8,8 nF; 64 pF | 19 / 16 MHz | scartati: come il MJE15032 (CJE 3 nF) |
| ZXTN19060CG / ZXTP19060CG Diodes SOT-223 | sì (Zetex/Diodes 2011, `spice/download/2669`, `2748`) | **non verificabile**: diodes.com risponde 403 (datasheet Rev. 2-2 senza testo NRND) | **no**: ZXTP19060CGTA Farnell 0, solo broker (Chip Stock 42000, Win Source 16580, New Advantage 1000), findchips 2026-10-29 | 60 V / 4,5 A | 1,37 / 1,00 nF; 17 / 26 pF | 88 / 118 MHz | **scartata**: stesso difetto per cui ADR-054 scartò i ZXT25040DZ (PNP senza scorta franchised); termico R_thJA 42 °C/W su 50 × 50 mm di rame 2 oz, oltre i 40 richiesti |
| FZT651 / FZT751 Diodes SOT-223 | sì, ma **Zetex del 1991** | non verificabile (403) | non cercate | 60 V / 3 A | 1,09 / 1,28 nF; 13 / 22 pF | 112 / 94 MHz | non approfonditi: modelli di 35 anni; stesso SOT-223 e stessa soglia termica |
| Toshiba TTC004B / TTA004B | sì (PSpice, LTspice) | **«Not Recommended for New Design»** (pagina Toshiba, letta con curl su TTC004B; TTA004B letta con lo stesso script) | — | 160 V / 1,5 A | non misurati | — | **scartati da T8** |
| Toshiba TTC015B / TTA008B | sì | **«Not Recommended for New Design»** (entrambe le pagine) | — | 80 V / 2 A | non misurati | — | **scartati da T8** |
| ZXTN25040DZ / ZXTP25040DZ Diodes SOT-89 (già in `models/`) | sì | non verificabile (403) | PNP debole (L46a) | 40 V / 5 A | 0,79 / 0,60 nF; 11 / 16 pF | 150 / 196 MHz | già valutati e scartati dall'utente in ADR-054; **V_CEO 40 V** appena sopra i ±20 V del regolatore in corto |
| STMicroelectronics | — | — | — | — | — | — | **non esaminato**: non ho cercato modelli SPICE di BJT ST; non è un esito |
| KSC3503 / KSA1381, BD139 / BD140, MJE15034/35, 2SC4793 / 2SA1837 | | | | | | | già scartati in L46a, non riproposti |

Fonti dei modelli scartati: `scartati/` in questa cartella, byte per byte, con `SHA256SUMS`; gli URL sono
quelli del criterio (`/download/models/lib/<parte>.lib` per onsemi, `/spice/download/<id>/<PARTE>.spice.txt`
per Diodes, ids 2669, 2748, 2647, 2723 — con il nome letto nel Content-Type, limitations #21).

**Le pagine onsemi dei candidati** (JSON-LD letto con curl, 2026-10-29): MJE243G, MJE253G, MJE172G,
MJE182G «Active, available»; le sigle nude MJE243, MJE253, MJE172, MJE182 «Obsolete». Si ordina con la **G**.

## 2. La scelta e perché

- **T7**: i due file sono serviti da onsemi, byte per byte in `vendor/bjt_npn/onsemi/MJE243/` e
  `vendor/bjt_pnp/onsemi/MJE253/` (sha256 e URL in `PROVENANCE.json`). Intestazione letta prima del
  congelamento (limitations #20): `.MODEL Qmje243 npn`, `.MODEL Qmje253 pnp`. Content-Type
  `application/octet-stream`, 994 e 996 byte (non i 303722 byte della pagina HTML di limitations #18).
  Autore dichiarato nel file: MODPEX / Symmetry Design Systems, 22 gen 2003 (lo stesso appaltatore del
  MJE15032).
- **T8**: Active sulla pagina del costruttore per la G; il datasheet (Rev. 17, dicembre 2024) elenca solo le
  due G e non ha banner «DISCONTINUED».
- **Datasheet**: `mje243-d.pdf`, un documento per la coppia. Le righe di condizione le ho lette sul render
  delle pagine 2 e 4 (limitations #19), non solo su `pdftotext`.
- **Perché non uno più veloce**: nessuno dei più veloci ha insieme modello fisico, stato Active verificato e
  PNP con scorte. Il MJE243/253 toglie il 79 % / 72 % della Cpi del MJE15032/33 a 20 mA, e il 67 % / 77 % della
  Cmu; il fT unitario sale da 12 a 88 / 61 MHz.

### Il prezzo di questa scelta (cose che il banco del blocco dovrà riprendere)

1. **Vbe più alta di 55 mV (NPN) e 83 mV (PNP)** a 20 mA: 0,626 V contro 0,571 / 0,543 V. Il moltiplicatore di
   Vbe e la corrente di riposo vanno rimessi a punto.
2. **hFE a 20 mA 377 / 209** contro 103 / 237: il rapporto NPN/PNP passa da 0,44 a 1,8 (invertito).
3. **Il PNP ha il hFE più basso del catalogo**: il modello dà 45,1 a 200 mA con un minimo di 40.
4. **Pin-out e footprint cambiano**: TO-225, piedino 1 emettitore, 2 e linguetta collettore, 3 base (il
   MJE15032 TO-220 ha base-collettore-emettitore); in KiCad `Package_TO_SOT_THT:TO-126-3_Vertical` esiste, il
   foro è 2,9–3,3 mm. La linguetta è il collettore e **non è isolata**, come per il TO-220 di oggi.
5. Il datasheet non specifica nulla a 20 mA (10× sotto il punto più basso, 200 mA per hFE, 100 mA per fT).

## 3. Le misure del punto 4 (`misure.txt`, `misure.json`, `misura_modelli.py`)

ngspice 47, `set temp = 25` (TNOM resta 27 °C come in ogni ricetta del repo), IC = 20,0000 mA e
VCE = 15 V trovati per bisezione sull'`op`. Cpi / Cmu sono le capacità di piccolo segnale che ngspice calcola
all'op (Cpi comprende la diffusione TF·gm). fT = frequenza a cui |ic/ib| = 1, collettore in corto in AC.
C_obo a VCB = 10 V, IE = 0, 0,1 MHz (la condizione del datasheet onsemi).

| Dispositivo | CJE (zero) | CJC (zero) | hFE | Vbe | gm | Cpi | Cmu | fT (incrocio) | C_obo |
|---|---|---|---|---|---|---|---|---|---|
| MJE15032 NPN (caso noto) | **3059,7 pF** | 300,1 pF | 103,1 | 0,571 V | 618 mS | **8093 pF** | 64,1 pF | 12,2 MHz | 92,4 pF |
| MJE15033 PNP (caso noto) | **3060,1 pF** | 300,1 pF | 236,6 | 0,543 V | 607 mS | **7808 pF** | 64,05 pF | 12,3 MHz | 92,4 pF |
| **MJE243 NPN** | **219,5 pF** | 74,4 pF | 377,0 | 0,626 V | 721 mS | **1700 pF** | 21,1 pF | 87,7 MHz | 29,15 pF |
| **MJE253 PNP** | **157,8 pF** | 65,5 pF | 209,3 | 0,626 V | 761 mS | **2190 pF** | 14,6 pF | 61,2 MHz | 19,70 pF |
| ZXTN25040DZ (riferimento) | 192,0 pF | 35,0 pF | 509,6 | 0,632 V | 773 mS | 793 pF | 10,8 pF | 150,1 MHz | 12,18 pF |
| ZXTP25040DZ (riferimento) | 183,0 pF | 58,0 pF | 661,0 | 0,631 V | 772 mS | 602 pF | 15,7 pF | 195,7 MHz | 18,09 pF |

Lettura: **CJE scende di 14× (NPN) e 19× (PNP)**, ma la Cpi di piccolo segnale solo di 4,8× e 3,6×: a 20 mA
la diffusione (TF·gm, 1,1 nF NPN e 2,0 nF PNP) pesa più della giunzione. Il MJE253 ha TF = 2,6 ns, quasi il
doppio del MJE243: la coppia è asimmetrica in velocità (88 contro 61 MHz). GBW a 10 MHz: 66,6 / 55,0 MHz.

**Un risultato di metodo**: la prima lettura della C_obo del MJE243 con l'emettitore su 1 TΩ (come i ricette
dei ZXT) dava 24,7 pF; era sbagliata. ngspice 47 non trova l'op di quel deck con quel modello (gmin e source
stepping falliscono, ripiega su un'analisi transitoria) e restituiva anche IC = 123 mA dove la polarizzazione
è per 100 mA. Con 1 GΩ converge direttamente e dà 29,15 pF, che è il valore teorico (74,4 pF·(1+10/0,4)^−0,287
= 29,2 pF) e che sta sulla curva del datasheet (~30 pF). La ricetta del validatore usa 1 GΩ, e il controllo di
IC è quello che l'ha scoperto. Il PNP e i ZXT non ne soffrono.

## 4. Il termico

Il peggiore dei due corti dei finali: il superstite dissipa 1,4–1,6 W; aria a 60 °C; Tj ≤ 125 °C, quindi
**R_thJA totale ≤ 40,6 °C/W** a 1,6 W. In funzionamento normale la dissipazione è ~0,36 W (NC-056): senza
dissipatore Tj = 60 + 0,36 · 83,4 = 90 °C, quindi il dissipatore serve **per i corti**, non per il riposo.

| Voce | Valore | Fonte |
|---|---|---|
| Contenitore | **TO-225** (CASE 77-09, uguale a TO-126 / SOT-32), linguetta = collettore, non isolata | datasheet MJE243/D p. 6 |
| R_thJC | **8,34 °C/W** max | datasheet p. 1 |
| R_thJA senza dissipatore | 83,4 °C/W max → a 1,6 W: Tj = 193 °C, **non regge** | datasheet p. 1 |
| Tj max | **150 °C** (−65…+150) | datasheet p. 1 |
| P_D | 15 W a TC = 25 °C; 1,5 W a TA = 25 °C | datasheet p. 1 |

**Dissipatore concreto: Boyd (Aavid Thermalloy) TV4**, a pannello di scheda per TO-126 / SOT-32,
**21 °C/W** in convezione naturale, 22 × 19,05 × 19 mm. Farnell codice **170075**: 4470 pezzi a magazzino
(Farnell Giappone, vista web 2026-10-29), kr 105,40 + IVA al pezzo (Farnell Norvegia), 9,70 € + IVA
(Comet/Farnell, Bulgaria); Newark 10WX1055 lo elenca.

| | °C/W | |
|---|---|---|
| R_thJC (max) | 8,34 | datasheet |
| R_thCS (contatto, **assunto**) | 2 | non pubblicato; ipotesi dichiarata |
| R_thSA (TV4, convezione naturale) | 21 | distributori, **non la curva** |
| Totale | **31,3** | |
| Tj a 1,6 W, 60 °C d'aria | **110 °C** | 60 + 1,6 · 31,3 |
| Tj a 1,4 W | 104 °C | |
| R_thSA massima ammessa a 1,6 W | **30,3** | (125−60)/1,6 − 8,34 − 2 |

Margine: la R_thSA reale può essere 1,44× quella di targa prima di toccare 125 °C. **Il limite: non ho letto
la curva del costruttore.** Il catalogo Boyd (Mouser) non si è scaricato e il datasheet di Boyd non l'ho
trovato; il 21 °C/W viene dal titolo dell'elenco Farnell («Heat Sink, PCB, Board Level, 21 °C/W, TO-126»). A
bassa potenza la R_thSA in convezione naturale è peggiore di quella a ΔT alto, quindi **il margine di 1,44×
potrebbe non esserci**: va confermata sul catalogo Boyd o sul banco prima di congelare. L'adattamento
meccanico del TV4 al TO-225 (stesso ingombro del TO-126) non è verificato su un disegno del costruttore.

Scartati come dissipatore: Wakefield-Vette 692-25/-50 (TO-126, clip e piedino, disponibili) — il datasheet
(`690 updated.pdf`) non riporta R_th; Assmann V5236BP-T (18 °C/W, SOT-32, **non tenuto a magazzino** da
DigiKey, 15 settimane); Ohmite C126-025-1AE obsoleto.

## 5. Disponibilità e prezzo

Fonte: **findchips.com, 2026-10-29** (aggregatore; Mouser e DigiKey non sono stati letti) e il JSON-LD di
onsemi. Gli intervalli di prezzo di findchips sono «minimo–massimo» fra le fasce di quantità, in dollari, senza
fasce esplicite.

| Parte | Distributore | Scorta | Prezzo (findchips) |
|---|---|---|---|
| MJE243G | Farnell | 4908 | $0,3770–1,1936 |
| MJE243G | Avnet Americas | 992 | $0,2537–0,2700 |
| MJE243G | RS (box / bag) | 1100 / 1100 | $0,3135–0,3581 / $0,5511–0,6369 |
| MJE243G | TME | 823 | $0,3530–1,0800 |
| MJE253G | Farnell | 709 | $0,3715–1,1936 |
| MJE253G | RS (box) | 520 | $0,3581–0,4116 |
| MJE253G | TME | 292 | $0,3880–1,1300 |
| MJE253G | Avnet Americas | **0** | $0,2537–0,2700 |
| MJE243G / MJE253G | onsemi (JSON-LD) | «available» | $0,2808 (fascia non indicata) |
| TV4 | Farnell | 4470 | ¥537,92 (1 pz, Giappone) |

La coppia ha scorte franchised su tre distributori **per entrambe** le polarità; il PNP è la metà più sottile
(709 + 520 + 292).

## 6. Cosa non ho verificato

- Scorte e prezzi a Mouser e DigiKey (bot-wall / non raggiunti).
- La **curva** R_th del TV4 e la compatibilità meccanica TO-225 / TV4 (§4).
- Lo stato Active di MJE182G/172G è da pagina onsemi ma non ne ho cercato le scorte.
- Lo stato dei Diodes (ZXT19060, FZT) sulla pagina del costruttore (diodes.com risponde 403).
- STMicroelectronics: non esaminato.
- Il comportamento del blocco con la coppia nuova (V1, V4, PSRR, slew, calore): è il banco che NC-056 chiede
  dopo questo lotto, non qui.
- Una circostanza a margine: il campo `Sim.Library` / `Sim.Name` e il footprint TO-225 nel sorgente non sono
  stati toccati.

## 7. File di questo lotto

Creati:
- `vendor/bjt_npn/onsemi/MJE243/{mje243.lib, mje243-d.pdf, *.sha256, PROVENANCE.json}`
- `vendor/bjt_pnp/onsemi/MJE253/{mje253.lib, mje253.lib.sha256, PROVENANCE.json}`
- `models/bjt_npn/mje243.lib` + `.provenance.json`; `models/bjt_pnp/mje253.lib` + `.provenance.json`
- `docs/preamp/data/2026-10-29/L55/modelli/`: `README.md`, `misura_modelli.py`, `misure.txt`, `misure.json`,
  `costruisci_modelli.py`, `scartati/` (i 13 file dei vagliati + `SHA256SUMS`), `ngspice/` (i deck e i CSV di lavoro)

Modificati: `scripts/validate_models.py` (ricetta `_tb_mje24x`, `tb_mje243`, `tb_mje253`, registro, `FLICKER`).

Riprodurre: `/usr/bin/python3 -I misura_modelli.py` in questa cartella; `/usr/bin/python3
scripts/validate_models.py` (89/89) e `--check-provenance` (41/41).
