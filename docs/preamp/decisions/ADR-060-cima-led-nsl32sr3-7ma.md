# ADR-060 — La cima del LED della NSL-32SR3 a 7 mA, a ogni temperatura: un'ipotesi dichiarata

Data: 2026-10-03 · Stato: superata da ADR-062 (niente celle, niente LED da pilotare)

## Contesto

ADR-050 aveva portato la cima della tabella delle LDR a 12 mA perché il LED della VTL5C4 regge
13 mA a 60 °C. La VTL5C4 è uscita (NC-043); al suo posto c'è la NSL-32SR3 di Advanced Photonix
(ADR-058, confermata da ADR-059).

Il datasheet della NSL-32SR3 (Silonex 104058 Rev 07, Luna, Advanced Photonix, in
`vendor/optocoupler/`) dà al LED 25 mA a 23 °C, e un'unica nota di declassamento, «derate
linearly to 0 at 75 °C», attaccata alla **dissipazione della cella**, non al LED. Il declassamento
del LED **non è pubblicato**.

- Letta alla lettera, la nota non tocca il LED, e 12 mA restano possibili.
- Letta in modo prudente, vale anche per il LED: 25 mA · (75 − 60) / (75 − 23) = **~7,2 mA a
  60 °C** (il limite di ADR-021), sotto i 12 mA.

All'inizio di L47b2 l'utente ha diviso il lotto (**L47b2a**: la cella nel sorgente, nei banchi e
nei controlli, e questa decisione; **L47b2b**: il profilo a 3 s, il pilota, il firmware, le misure
sul preamp intero), e ha scelto fra quattro strade: un'ipotesi a 7 mA o a 12 mA, con o senza una
domanda scritta al costruttore.

## Decisione

**Dell'utente**, il 2026-10-03: **«Solo ipotesi a 7 mA»**.

1. **La cima del LED della NSL-32SR3 è 7 mA a ogni temperatura, su tutte e due le stringhe** (la
   serie a d = 0 e la derivazione a d = 1). È un'**ipotesi dichiarata**: la nota di declassamento
   del datasheet si legge come se valesse anche per il LED. Il margine a 60 °C è del 3 %.
2. **Nessuna domanda al costruttore.** La cifra si verifica sul prototipo, o si rivede se il
   costruttore pubblica il declassamento (sotto, «Da riaprire se»).
3. **Dove entra subito (L47b2a)**: nel banco E3/E5 (`tb_e3_e5_ldr.cir`, la cella accesa a 7 mA).
   **Dove entra in L47b2b, tutto insieme**: il profilo a 3 s ricalibrato sulla NSL-32SR3 (che
   ha già sotto gli occhi la cima nuova), il pilota in `psu.py`, la tabella del firmware
   (`LDR_I_TOP`, oggi 12 mA) e il punto alto della calibrazione di ADR-050 (punto 2: oggi
   12 mA). I banchi V2 restano intanto col profilo v4 della VTL5C4 e la sua cima, e lo dicono
   nell'intestazione: le loro cifre di S e B non sono verdetti del mute nuovo.

## Cosa costa

Modello comportamentale da dati pubblicati, una sola cella misurata nella regione del mute
(`models/optocoupler/nsl32sr3_comportamentale.lib`, ADR-058). Cifre di modello: conta il trend.

| | 7 mA | 12 mA | 20 mA |
|---|---|---|---|
| Cella accesa, curva B (tipica) | **99,9 Ω** | 76,4 Ω | 62,4 Ω |
| Cella accesa, curve C ed E (le più resistive) | **115,5 Ω** | 80,3 Ω (C) | — |
| Cella accesa, curve A e D | 51,2 Ω | — | — |

(`data/2026-10-03/L47b2a/cella/r_cella.cir`, un punto di lavoro per caso.)

- **In ascolto**: 99,9–115,5 Ω in serie contro 1 MΩ di R_IN: una perdita di −0,001 dB.
- **E5** (preliminare, il banco di L47b2a): **5,53 µV** contro ≤ 9,90 µV, sul caso più resistivo;
  la catena senza cella 5,50 µV, identica a L44.
- **E3** (preliminare): |Zin| minima **110,7 kΩ** contro ≥ 100 kΩ (CSEL 68 pF, in gioco),
  identica alla VTL5C4: la fissa la capacità del selettore, non la cella.
- **La profondità del mute a LDR** nell'istante in cui d arriva a 1, prima del relè al jack: la
  derivazione accesa vale ~100 Ω invece di ~76 Ω a 12 mA, ~2,3 dB meno profonda a pari serie.
  Si misura in L47b2b col profilo nuovo (B, NC-049).
- **La caduta dei LED**: a 7 mA il LED del modello cade 1,89 V (2,13 V a 12 mA). Due in serie
  per stringa (ADR-039) stanno sotto i 2 × 2,5 V del massimo a 20 mA. Il conto della tensione
  disponibile al pilota è di L47b2b (`psu.py`, commento alla riga 182).
- **Il riscaldamento del LED**: ~13 mW per LED, meno dei ~19 mW di ADR-050.

## Alternative scartate

- **12 mA, la nota letta alla lettera**: mute più profondo e la tabella di oggi, ma se la nota
  vale anche per il LED, a 60 °C la cima starebbe sopra il massimo del 66 %.
- **Una domanda al costruttore** (techsupport@advancedphotonix.com), con l'una o l'altra ipotesi
  in attesa della risposta: l'utente ha preferito non scrivere.
- **Una cima che scende con la temperatura**: già scartata in ADR-050 (il sensore sta sul micro,
  non sulla cella), e qui la cima a freddo non è nota con certezza più di quella a caldo.

## Da riaprire se

- Advanced Photonix pubblica il declassamento del LED, o lo dichiara su richiesta di qualcuno.
- Il prototipo misura il LED più caldo del telaio: il declassamento vale per la temperatura
  della cella.
- In L47b2b il mute a LDR con 7 mA risulta non abbastanza profondo nei 0,5 s prima del relè
  (B), o S sfora 20 dB per la cima più bassa: allora si ridiscute la cima della sola derivazione.
- La misura sul prototipo contraddice la curva R(I) del modello fra 2 e 20 mA.
