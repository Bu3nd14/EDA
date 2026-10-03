# L47b2a — la NSL-32SR3 nel sorgente e nei banchi, la cima del LED a 7 mA (2026-10-03)

Decisione: **ADR-060**. Dati e come rifarli: `data/2026-10-03/L47b2a/README.md`. Cifre di
modello: «modello comportamentale da dati pubblicati, una sola cella misurata nella regione del
mute» (`models/optocoupler/nsl32sr3_comportamentale.lib`, ADR-058). La distorsione della
NSL-32SR3 **non è modellata**, né il suo rumore in eccesso.

## 1. Il mandato e la divisione

`NEXT-SESSION.md` chiedeva L47b2: la NSL-32SR3 nel sorgente, il profilo a 3 s, il pilota, il
firmware, le misure sul preamp intero. All'inizio, alle due domande per nome:

- **la divisione**: «Due parti». **L47b2a** (questo lotto): il sorgente, l'impronta confrontata
  col disegno, i controlli dei relè e del cablaggio, tutti i banchi canonici sulla NSL-32SR3, la
  cima del LED. **L47b2b**: il profilo a 3 s ricalibrato, il pilota in `psu.py` (con NC-050 e
  NC-051), il firmware, S/B/E3/E5 sul preamp intero, le catene a valle;
- **la cima del LED**: «Solo ipotesi a 7 mA» (ADR-060). Nessuna domanda al costruttore.

## 2. Il difetto silenzioso della piedinatura

Il primo passo è stato cambiare **solo** la `Part` nel sorgente e generare la netlist, per vedere
cosa succede. `Isolator:NSL-32` ha **1 = anodo, 2 = catodo**; `Isolator:VTL5C` il contrario (letti
da `Isolator.kicad_sym` di KiCad 10). Il sorgente collegava i LED a J3 per numero.

- La netlist generata ha la **connettività identica** a quella di `main` (cambiano solo valore,
  impronta, descrizione, foglio dati e parte), SKiDL dà 0 errori.
- Su quella netlist i quattro LED sono **tutti rovesciati** (`script/piedini_celle.py`).
- `check_psu_harness.py` (blocco 2j) diceva **OK**: confrontava J3 coi piedini 2 e 1 per numero.
- `check_relay_safe_state.py` (2e) falliva, ma per la ragione sbagliata: «nessuna LDR
  (Isolator:VTL5C)».

Nel prototipo il mute non si sarebbe mai inserito. Registrato in `docs/limitations.md` come #41.

**Il rimedio.**
- Nel sorgente i LED si collegano **per nome** (`left["A"]`, `left["K"]`, …), col commento che
  spiega perché.
- `check_psu_harness.py`: `LDR_AUDIO` dice la **funzione** (anodo o catodo), che si risolve
  attraverso la parte (`LED_PINS`); una parte che non conosce è un rilievo, non un'ipotesi.
- `check_relay_safe_state.py`: `KNOWN_LDR` accetta la sola `Isolator:NSL-32` con anodo e catodo
  per nome; nuova regola: la rete fra i due LED di una stringa unisce un catodo a un anodo
  (ADR-039, serie fra i canali).
- `preamp_blocks_draw.py` (2f) asserisce la parte `NSL-32SR3`; l'etichetta di `psu_blocks_draw.py`
  pure. I due SVG rigenerati.

**I falsi** (`data/2026-10-03/L47b2a/falsi/`), ciascuno fatto fallire prima di fidarsi:

| Netlist | Relè (2e) | Cablaggio (2j) |
|---|---|---|
| sorgente nuovo (buona) | OK | OK |
| `main`, VTL5C | FALLITO (nessuna NSL-32) | FAIL ×4 (parte sconosciuta) |
| LED tutti capovolti | OK — la serie è coerente | **FAIL ×4** (anodo/catodo a J3) |
| un LED rovesciato (U301) | **FALLITO ×2** (`K e K`) | FAIL ×1 |

I due controlli girano entrambi in `run_tests.sh`: insieme coprono tutti e tre i casi.

## 3. L'impronta

`OptoDevice:Luna_NSL-32` contro i disegni in `vendor/optocoupler/` (Silonex 104058 Rev 07,
Advanced Photonix; quello di Luna non ha quote):

| | Impronta KiCad | Silonex | Advanced Photonix |
|---|---|---|---|
| Passo dei terminali della cella | 2,53 mm | 2,54 ± 0,13 | 2,5 |
| Passo dei terminali del LED | **3,81 mm** | **3,30 ± 0,13** | **3,3** |
| Fra la coppia LED e la cella | 10,16 mm (corpo 5,72–6,22) | — | — |
| Foro | 0,81 mm | cella Ø 0,4 ± 0,05; LED 0,25 × 0,64 | cella Ø 0,45–0,56; LED 0,20 × 0,40/0,50 |
| Piedino 1 | anodo (piazzola rettangolare) | — | — |

- La cella coincide. I fori accolgono i terminali (il LED Silonex, 0,25 × 0,64, ha diagonale
  ~0,69 mm: 0,12 mm di gioco).
- **Il LED no**: 0,51 mm di differenza, quattro volte la tolleranza. I terminali sono lunghi
  almeno 25 mm e si piegano, ma Advanced Photonix avverte che divaricarli male danneggia il
  passante in vetro («Lead Splaying»), e chiede la saldatura a 1/16" (Silonex 2 mm) dal corpo.
  Coi 10,16 mm fra le coppie restano ~2 mm per lato.
- **Non creata un'impronta nuova**: è una decisione per L49 (placement di prova), con l'utente.

## 4. La cella e la cima

| Curva | 7 mA | 12 mA | 20 mA |
|---|---|---|---|
| A, D | 51,2 Ω | — | — |
| **B (tipica)** | **99,9 Ω** | 76,4 Ω | 62,4 Ω |
| C, E | **115,5 Ω** | 80,3 Ω (C) | — |

B a 4,5 µA 248 kΩ, a 10 nA 25,0 MΩ (il buio dichiarato). LED a 1,89 V a 7 mA (2,13 V a 12 mA).
(`cella/r_cella.cir`.)

## 5. I banchi canonici

**Nessuno resta sulla VTL5C4** (`grep` sui 26 deck di `spice/preamp/tb/`: vuoto).

- **`tb_e3_e5_ldr.cir`** (a mano, non è generato): il modello, `NSL32SR3_B`, la cella accesa a
  7 mA; per E5 la serie come resistore da 99,9 Ω (B) e 115,5 Ω (C/E, «curvaCE», le più resistive);
  la derivazione spenta a 25 MΩ invece di 400 MΩ. I commenti con le cifre nuove.
- **`tb_v2_casopeggiore.cir`** e **`tb_v2_mute_ldr.cir`**, rigenerati dai loro generatori
  (`data/2026-09-23/L29c/deck/`, `data/2026-09-22/L29b2/deck/`, modificati sul posto come in L30 e
  L41c): il modello e i sottocircuiti. **Il profilo v4 a 6 s e la cima di 20 mA restano**, e
  l'intestazione lo dice: profilo e cima nuovi vanno insieme in L47b2b, e fino ad allora le cifre
  di S e B di questi deck non sono verdetti del mute nuovo.
- **Una deriva trovata**: L44 aveva corretto a mano la riga del KF in `tb_v2_mute_ldr.cir` («da
  L44 tutti hanno KF»), ma non il generatore; rigenerando la riga tornava indietro. Corretto il
  generatore.

## 6. Le misure preliminari

**E3 ed E5** (`e3_e5/`, cella in serie a 7 mA; verdetto in L47b2b sul preamp intero col profilo
nuovo):

| | NSL-32SR3, 7 mA | VTL5C4, 20 mA (L44) | Requisito |
|---|---|---|---|
| \|Zin\| minima, in gioco | **110,7 kΩ** | 110,7 kΩ | ≥ 100 kΩ |
| \|Zin\| minima, in mute | 113,6 kΩ | 113,6 kΩ | |
| \|Zin\| minima, a metà | 114,4 kΩ | 116,4 kΩ | |
| E5, caso della cella più resistiva | **5,53 µV** | 5,53 µV | ≤ 9,90 µV |
| E5 senza cella | 5,496 µV | 5,496 µV | |

Il minimo di E3 lo fissa la capacità del selettore (68 pF), non la cella.

**L'accoppiamento LED-cella sul nodo d'ingresso** (0,5 pF, ipotesi del modello presa dalla
VTL5C4): la trasferenza dall'anodo al jack sale del 13 % (la derivazione spenta ora vale 25 MΩ,
non 400), e il rumore ammesso sul comando dei LED scende da 692 a **613 nV/√Hz** (modo +10 dB).
È un requisito sul pilota: L47b2b.

**La prova di corsa V2** (`v2_prova/`, profilo e cima della VTL5C4):
- `g0sempre_1k_iii` (mute fermo a d = 1 per 19 s): corre fino in fondo, 1 900 008 righe,
  l'ultima a t = 19 s; serie a 7,398 decadi (25 MΩ), derivazione a 62,4 Ω, rail a ±15 V. Nessun
  «Transient op», nessun passo collassato: nel banco V2 la cella ferma corre, a differenza del
  banco statico di L47b1 (limitations #42).
- `mev_1k_iii` (un evento di mute col relè, inserimento e rilascio): corre fino a t = 17,5 s, il
  tempo chiesto, senza errori. A fine corsa il mute è rilasciato (d = 0), la serie riaccesa a
  62,4 Ω, la derivazione che torna al buio (6,77 decadi), il segnale al nodo d'ingresso di nuovo
  a 3,81 V di picco. Non analizzata per S e B: il profilo non è ancora quello della NSL-32SR3.

## 7. Le catene a valle

- **I 21 deck veloci** (`regressione/`): 21 su 21 con uscita 0; contro L44, su 249 CSV
  **cambiano solo i 3 di `tb_e3_e5_ldr`**, nelle colonne delle celle. Il resto è identico.
- **`validate_models.py --check-provenance`**: 27 su 27.
- **`run_tests.sh`**: **13 passati, 0 falliti** (compresi 2e, 2j, 2f e il firmware sull'host:
  i test passano, i 21 falsi falliscono).
- **La catena dei guasti di L41c non è ricorsa.** Il suo deck della scheda audio **include** le
  celle, e il generatore (`--matrice l41c`) ora le scrive NSL-32SR3. Ma le correnti dei LED, lì,
  arrivano dalle forme d'onda del pilota vero (i JSON del ponte di L41c), tarato sulla VTL5C4 e da
  rifare in L47b2b: ricorrerla ora misurerebbe la cella nuova col pilota vecchio. Si ricorre in
  L47b2b, dopo il pilota.
- **Il firmware** non è toccato: `LDR_I_TOP` resta 12 mA fino a L47b2b (ADR-060, punto 3).

## 8. Le non conformità

- **NC-043** (bloccante per G2): avanzata. Sorgente e banchi fatti; restano profilo, pilota e
  misure (L47b2b).
- **NC-049** (maggiore): avanzata. La cima che la chiude è ora 7 mA.
- **NC-045, NC-050, NC-051**: invariate, sono di L47b2b.

## 9. Per L47b2b

- Il profilo a 3 s ricalibrato sull'inviluppo A–E **con la cima di 7 mA**: il banco di L47b1
  (`sfumatura.py`) aveva 12 mA; a 7 mA la serie accesa è più resistiva e la derivazione meno
  profonda (~2,3 dB a pari serie).
- Il pilota in `psu.py`: la cima, la caduta di due LED NSL in serie, il rumore ammesso sul
  comando (613 nV/√Hz), la tenuta di `VRELAY` (NC-050) e il commento di `C_VRELAY` (NC-051).
- Il firmware: `LDR_I_TOP`, la tabella, il punto alto della calibrazione (ADR-050 punto 2 dice
  12 mA), `timer_spec.md`, i test sull'host e i falsi per il tempo di 3 s.
- S, B (20 kHz prima del relè), E3, E5 sul preamp intero, curva D compresa.
- L'impronta del LED (3,81 contro 3,30 mm) va decisa con l'utente prima di L49.
