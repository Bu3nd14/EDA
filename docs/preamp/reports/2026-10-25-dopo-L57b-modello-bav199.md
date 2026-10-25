# Dopo L57b — il modello del costruttore del BAV199 nel limitatore

Data: 2026-10-25 · Sessione «hi-fi preamp dopo L57b» · Dati: `data/2026-10-25/dopo-L57b/` (README)
· Decisione: ADR-101 (invariata) · Non conformità: NC-059 resta chiusa, con le cifre del modello vero.

Alla chiusura di L57b il limitatore d'ingresso era simulato con una **stima** del BAV199 (Nexperia non
lasciava scaricare il suo modello). L'utente ha incollato il modello SPICE del BAV199 di **Diodes
Incorporated** (`DI_BAV199`): qui sostituisce la stima e i conti si rifanno.

## 1. Il modello

`vendor/diodes/diodes_inc/BAV199/BAV199.spice.txt`, verbatim, con hash e provenienza (l'origine è
l'incolla dell'utente: l'identità byte per byte col file di diodes.com non è verificata, i parametri
sì); la copia invariata in `models/diodes/bav199.lib`, e il sorgente (`input_limiter.py`) chiama
`DI_BAV199`. È il modello del **secondo costruttore** dello stesso tipo: la sua riga dei limiti (85 V,
160 mA, 3 µs) coincide col datasheet di Nexperia su cui la parte è stata scelta.

Contro quel datasheet (ricetta `tb_bav199`, `validate_models.py` **67 / 67**, provenienza **31 / 31**):

| | modello Diodes Inc. | stima di L57b | datasheet Nexperia |
|---|---|---|---|
| C a 0 V, 1 MHz | 2,003 pF | 1,848 pF | 2 pF tip. |
| C a 5 V inversi | 1,101 pF | 1,095 pF | ~1,1 pF (fig. 5, a occhio) |
| VF a 1 mA | 0,769 V | 0,635 V | ≤ 0,9 V |
| corrente inversa a 5 V | **0,055 nA** | 3,91 nA (il tetto del 1N4148) | 5 nA max a 75 V |
| tempo di transito | 4,32 µs | 10 ns | trr ≤ 3 µs |

La stima aveva preso bene la capacità. Le differenze che contano sono tre: la VF più alta, che
alza un poco la soglia; la dispersione 70 volte più bassa; la carica immagazzinata.

## 2. I due casi noti

- Il caso di L57a (la topologia generata col 1N4148 e i riferimenti ideali): **256 celle su 256**.
- La stima di L57b rinominata `DI_BAV199`: ridà le cifre di L57b, **256 celle su 256** sull'RCA a caldo, e
  il costo uguale alla quarta cifra. Il cambio del nome del modello non ha cambiato nient'altro.

## 3. L'RCA a caldo, col modello del costruttore

Classe II, caso peggiore, alle tre reti (`sintesi.csv`):

| | L57b (stima) | **ora** | limite |
|---|---|---|---|
| gate-gate LSK489 | 4,33 V | **4,42 V** | 30 V |
| gate-drain | −14,7 V | −14,9 V | 60 V |
| il jack alla posizione d'ascolto, 0 / +10 dB | 99,8 / 109,8 dB SPL | **100,1 / 110,0 dB SPL** | 112,2 dB SPL |
| le fisse sul picco del K11 | +3,4 dB | +3,6 dB | — |
| col mute: 0 / +10 dB / cima | 77,0 / 82,5 / 105,3 | 77,0 / 82,7 / 105,3 dB SPL | 112,2 |
| picco nel diodo | 1,15 mA | **5,63 mA** | 160 mA |

La soglia sale di ~0,13 V con la VF del diodo vero: +0,3 / +0,2 dB SPL al jack, 2,2 dB sotto il tetto
a +10 dB. Con la capacità raddoppiata le stesse cifre.

**Il picco di 5,6 mA nel diodo** è la carica immagazzinata del modello vero (4,32 µs di tempo di
transito: mentre conduce il diodo si comporta come ~90 nF), che al contatto della massa porta il fronte
verso il riferimento. Il diodo regge 160 mA. Quanto ne arriva all'LM4040 l'ho misurato a parte
(`rca/rif/`, rete +10 %, i due casi in classe II): il picco nella sua impedenza è **2,79 mA** (1,0 mA di
bias e 1,8 di impulso; il resto lo prende il 100 nF), la media sull'evento è il solo bias (1,0007 mA).
Con i due canali insieme e il rail a ~20 V di un regolatore in corto si arriva a circa 5 mA: dentro i
15 mA raccomandati.

## 4. Il costo al segnale (V4, E5)

`costo/costo.csv`, sorgente 2,5 kΩ, a 0,2 V RMS dove non è detto:

| | L57b (stima) | **ora** | capacità doppia | tetto di V4 |
|---|---|---|---|---|
| THD 20 kHz | 0,000764 % | **0,000764 %** | 0,000764 % | 0,001 % (riaprire a 0,0009) |
| h5+ a 1 / 10 / 20 kHz | −148,9 / −188,6 / −200,2 | **−148,9 / −188,7 / −200,1 dB** | −148,9 / −188,7 / −198,2 | ≤ −140 dB |
| h3 a 20 kHz | −140,7 dB | −138,6 dB | −132,6 dB | (lo spettro cala in ordine) |
| CCIF 19 + 20 kHz | −133,6 dB | **−133,6 dB** | −133,6 dB | ≤ −110 dB |
| THD 20 kHz, 2 V | 0,00772 % | **0,00776 %** | 0,00808 % | 0,01 % |
| E5 stimato | 4,922 µV | **4,921 µV** | 4,921 µV | 9,95 µV |

## 5. Regressione dei deck canonici

`regressione/verdetti.csv`: col modello del costruttore V1 **67,81°**, E3 **105,3 kΩ**, E5 **5,413 µV**,
F1 139,8 µV. Sono le cifre della stima, entro lo 0,03 % (`regressione/confronto.csv`), e nessun
ripiego in più nei log.

## 6. Conclusione

Le cifre di L57b tengono col modello del costruttore. Nessun «Da riaprire se» di ADR-101 scatta e
NC-059 resta chiusa. Cambia una sola cosa: l'impulso del fronte di massa passa dal diodo al
riferimento. L'LM4040 lo regge (2,8 mA di picco).

## Limiti dichiarati

- Il modello è di Diodes Inc., la parte scelta è il tipo BAV199 sul datasheet di Nexperia: un
  esemplare tipico, nessuna dispersione fra pezzi, nessuna temperatura oltre i parametri predefiniti
  (la dispersione a caldo non è descritta). Il datasheet di Diodes Inc. non è nel repo.
- I riferimenti nei banchi restano la cifra di datasheet (`INREF_EQ`, limitations #76).
- La stima `bav199_fit.lib` resta in `models/` con la sua ricetta: i dati di L57b la usano.
