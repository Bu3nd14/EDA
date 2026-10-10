# L51b — il dossier rigenerato, l'alimentatore e il firmware

Data: 2026-10-09/10 · Lotto: L51b (la seconda delle tre parti di L51) · Decisioni: nessuna ADR,
nessuna NC aperta o chiusa. Dati: `data/2026-10-09/L51b/` e la sorella `L51b-prima/` (README).

## In breve

- **Le scelte dell'utente**, chieste coi numeri:
  - **«Tutto col selettore»**: ogni catena dell'alimentatore ricorsa oggi col carico di oggi, e
    come seconda strada lo stesso col carico di prima. I guasti al jack di L47c2b2 erano corsi
    senza la bobina del selettore sulla linea a 12 V.
  - **«Sì, i rail di oggi»**: trovato preparando le corse, il banco caricava ancora ogni rail con
    265 mA, la cifra di L41a. `tb_op` di oggi dà 293,6 / 301,8 mA (ADR-054), +11–14 %.
  - **«Rifare e mostrarmela»**, poi, coi numeri, **«Sì, così»**: la stima del calore con le
    potenze misurate sul banco, il ferro dei trasformatori come ipotesi dichiarata.
- **Due cartelle, gli stessi script.** Il carico (i due rail, il resto di `VRELAY`, il metodo
  dei casi di U503) è un dato della cartella (`carico.txt`), non del generatore.
  - **Col carico di prima**, `L51b-prima/` ridà L47c2a e L47c2b2 **byte per byte**: 109 file su
    109, cioè banchi, temporizzatore, controfattuale col carico di L41a, 15 sequenze e ponte.
  - **Col carico di oggi**, `L51b/` è la prima strada del dossier.
- **Col carico di oggi nessun verdetto cambia**:
  - la tenuta di `VRELAY_REG` a rete −10 % scende da 61,1 a **48,3 ms** (P9 ≥ 25 ms);
  - il rivelatore guasto fa scattare il mute 0,4 ms prima della soglia invece di 1,2;
  - Δ e lo standby non si muovono: 16,91 ms all'angolo minimo, 80,5 mW da T2;
  - il firmware passa **15 sequenze su 15**; sull'host 76 controlli e **19 falsi su 19**.
- **I due casi di U503 spento col metodo gear.** Col carico di oggi il trapezoidale di L47c2b2
  non finisce più. Gear, il metodo di tutte le altre sequenze, li finisce in 12 s. La sonda
  (`sonda_u503/`) dà gli stessi istanti con un terzo metodo e i rail entro 0,5 mV.
- **I guasti al jack**: U502 spento **0,815 mV** (51,7 dB SPL; L47c2b2 0,893), U501 0,517 mV, il
  controfattuale senza Δ 14,8 mV (cade, come deve). La scomposizione separa le cause: il
  controfattuale e il corto si dimezzano per la **scheda audio di oggi** (C_T di L48b, −6,0 dB),
  non per il carico (0,00 dB).
- **Il calore**: 17,3 / 15,1 / 19,5 W (rete nom / −10 % / +10 %), caso peggiore a 3 cm **57,2 °C**,
  gioco minimo **1,5 cm** (era 2,0). La mia proiezione a mano di inizio lotto (~59 °C) era
  sbagliata: la regolazione di `VRELAY` ipotizzata in L41a (1,34 W al peggio) sul banco vale 0,63.
- **Tolti**:
  - la sezione del pilota delle LDR e la sua figura (ADR-062);
  - la riga di ADR-050;
  - la tabella del raddrizzatore di L41a, sostituita dalla valle del grezzo misurata oggi;
  - la tabella di L30 coi rail disegnati a mano, corsa sulla scheda del 26 settembre.
- **Trovato, non corretto** (il sorgente non si tocca in questo lotto): in `psu.py` il commento
  di `C_VRELAY` cita 61,1 ms (oggi 48,3) e quello di `C_RAW` la valle di L41a, 18,1 V (oggi 17,9).
- **Il generatore**: `PARTI = ("audio", "alimentatore")`; scrive ancora solo con `--standalone`
  fuori dal repo, e il primo `index.html` nuovo lo scrive L51c. Sabotaggi: vedi sotto.

## Le corse

| Catena | Col carico di oggi | Col carico di prima | Contro |
|---|---|---|---|
| banchi rete e guasti, 4 deck | log puliti, deck rigenerati uguali | uguali | L47c2a, byte per byte |
| controfattuale col carico di L41a | — (il generatore lo rifiuta) | uguale | L47c2a |
| temporizzatore | Δ, standby uguali | `analisi_timer.txt` uguale | L47c2a |
| 15 sequenze del firmware | PASSA, 15 su 15 | PASSA | L47c2a, L47c2b2: testo, punto fisso, deck, core |
| ponte, 9 JSON | — | uguali | L47c2b2 |
| scheda audio, 18 corse | rc 0, 0 fallite | rc 0 | la tabella: scomposizione |
| firmware sull'host | 19 su 19 | — | L47c2a e L47c2b2, byte per byte |

L'`analizza_seq.py` di L47c2b2, che contiene i criteri di tutti e due i lotti, stampa i dati
di contorno a sei decimali; quello di L47c2a a quattro. Il confronto tiene esatte le righe dei
criteri e legge i fatti alla precisione del lotto d'origine (0,010647 è 0,0106).

## Cosa cambia col carico di oggi

| | carico di prima | oggi | requisito |
|---|---|---|---|
| tenuta di `VRELAY_REG` ≥ 11,4 V, rete −10 / nom / +10 % | 61,1 / 142,2 / 223,6 ms | **48,3** / 121,7 / 195,4 ms | P9 ≥ 25 ms |
| rail + a 13,5 V dopo la perdita, −10 % | 73,9 ms | 65,5 ms | |
| rivelatore guasto: il mute prima della soglia | 1,2 ms | 0,4 ms | P9: entro 1 ms dopo |
| U501 spento: jack / V+ < 10,6 V | 13,1 / 34,8 ms | 12,1 / 31,4 ms | r41, s41 |
| U503 spento: `VRELAY` a J1 < 9,6 V dopo `PERMIT` | 42,0 ms | 35,9 ms | |
| valle del grezzo −, rete −10 % | 18,05 V | 17,89 V (2,6 V sopra 15,3) | |

## I guasti al jack, scomposti

| Caso | L47c2b2 | la scheda di oggi, il carico di prima | oggi | la scheda | il carico |
|---|---|---|---|---|---|
| U502 spento | 0,893 mV | 0,869 mV | **0,815 mV** | −0,24 dB | −0,55 dB |
| U501 spento | 0,552 mV | 0,537 mV | **0,517 mV** | −0,24 dB | −0,32 dB |
| controfattuale senza Δ | 29,7 mV | 14,8 mV | **14,8 mV** | −6,02 dB | 0,00 dB |
| corto della linea a 12 V | 29,7 mV | 14,9 mV | **14,9 mV** | −6,01 dB | 0,00 dB |
| spegnimento morbido | 15 nV | 6 nV | 34 nV | −7,6 dB | +14,7 dB |

I casi ai nanovolt si muovono di molti dB nei due sensi: sono il fondo del metodo, migliaia di
volte sotto V2 (100 µV).

## Il calore

Il modello del telaio e del vano è quello di L30/L41a, senza cambi. Il banco della rete di oggi, a
regime con la musica e le bobine accese, dà la potenza che esce dai secondari e dove va. Il
bilancio torna entro 0,07 W; la scheda audio è 8,931 W da `tb_op` e 8,947 W sul banco.

| W (nom / −10 % / +10 %) | L41a | oggi |
|---|---|---|
| scheda audio | 7,94 | 8,93 |
| regolatori ±15 V | 2,95 / 1,76 / 4,14 | 3,24 / 1,90 / 4,58 |
| linea a 12 V (bobine, selettore, relè di rete, micro) | 0,95 + 0,40 | 1,50 |
| regolatore di `VRELAY` | 0,98 / 0,73 / 1,34 | 0,39 / 0,14 / 0,63 |
| trasformatori e ponti | 3,10 (ipotesi) | rame e ponti 1,84 misurati + ferro 1,30 / 0,70 / 1,95 (ipotesi) |
| LDR | 0,25 | — |
| **totale** | 17,04 / 14,05 / 20,18 | **17,27 / 15,05 / 19,54** |

Caso peggiore: 3 cm 57,2 °C (L41a 57,9), gioco minimo 1,5 cm per lato. Ogni watt di ferro in più
vale ~1,1 °C.

## Il generatore del dossier

- La prima strada dell'alimentatore passa da `ps()`: niente da prima del 2026-10-09. I lotti di
  prima si rileggono solo da `vecchio()`, come seconda strada.
- Ogni deck si rigenera da `psu.net` col `carico.txt` del lotto:
  - i quattro banchi, nelle due cartelle;
  - il controfattuale;
  - il deck al punto fisso di **ogni** sequenza, dalle uscite del core del giro prima;
  - il deck di V2, dal sorgente e dal ponte;
  - il deck del calore, dal deck della rete.
- Tre difetti miei, trovati facendo girare il generatore e corretti:
  - la guardia `sp()` copriva il modulo dei grafici (`svgplot as sp`): ora si chiama `ps()`;
  - una variabile locale `num` copriva una funzione;
  - un deck non rigenerato faceva cadere il generatore con un'eccezione invece che con un
    rifiuto. L'ha trovato il primo giro dei sabotaggi (29 su 30); ora `stesso_deck` rifiuta per
    nome.
- **Sabotaggi**: vedi `L51b/sabotaggi.txt`.

## Non fatto, e di chi è

- **L51c**: le schede di prova e l'assieme di L49, «Cosa questo dossier non dice» (la sezione
  `s14` usa nomi che non esistono più, `all_kf0`, `kf_parts`, `mu["cima_deck"]`, e cadrà alla
  prima corsa con `"schede"`), le righe `Stato:` restanti, il primo `index.html` nuovo.
- **Il sorgente**: i commenti di `C_VRELAY` e `C_RAW` in `psu.py` (sopra), per l'utente.
- **I falsi sul circuito**: nessuno dopo L41b2; i due di allora erano sul firmware con la legge
  delle LDR, che L47c2a ha tolto.
