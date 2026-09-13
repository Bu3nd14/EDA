# ADR-020 — Quota del ripple d'alimentazione nel budget di E5: 1 µV RMS in uscita

Data: 2026-09-13 · Stato: accettata

## Contesto

E5 chiede **< 10 µV RMS** in uscita, 20 Hz–20 kHz, non pesati. Un voltmetro
in banda non distingue il ripple dei rail dal rumore del circuito, quindi il
ripple consuma lo stesso budget. Il PSRR del rail + è basso: a +10 dB vale
**29,82 dB** a 10 kHz, contro 86,23 dB del rail −. Ma nessun requisito diceva
all'alimentatore, che non è ancora progettato, quanto ripple può lasciare
(**NC-011**).

Una quota esisteva, **informale**: `gain_block.py` e
`reports/2026-09-08-fase2-bozza-topologia.md` (righe 170-174) consegnavano a
`psu-engineer` «≤ 1 mV picco a 100 Hz su V+, così il contributo resta sotto
1 µV in uscita». Stava in un commento, con cifre del THAT320, e solo a 100 Hz.

## Decisione

**Il ripple e il rumore dei due rail, riportati in uscita, stanno sotto
1 µV RMS in 20 Hz–20 kHz.** Il verbo:

√( Σ_rail∈{+,−} Σ_k [ V_rail,k · 10^(−PSRR_rail(f_k)/20) ]² ) **≤ 1 µV**

- **k** percorre ogni componente fra 20 Hz e 20 kHz. Il rumore a banda larga
  entra come integrale della sua densità pesata allo stesso modo.
- **V_rail,k** è il valore RMS al **nodo di alimentazione del blocco**, a valle
  di ogni filtro che non sta dentro il blocco.
- **PSRR(f)** è il **minimo fra le modalità di guadagno**, sulla topologia
  vigente al momento della verifica. Oggi è +10 dB su tutti gli 81 punti di
  entrambi i rail; con L27 sarà il minimo dei tre livelli.

La tabella per tono e il criterio di passaggio stanno in `REQUIREMENTS.md`,
«Nota su E5 — la quota del ripple d'alimentazione».

## Perché

- **Serve una quota fissa, e non «quel che avanza».** Il rumore del circuito
  non è noto. 4,231 µV è un pavimento senza 1/f (**NC-004**), e l'1/f manca
  proprio sui contributori dominanti. Un alimentatore dimensionato sul
  residuo andrebbe rifatto a ogni rimisura del rumore.
- **1 µV è l'1% della potenza di E5.** Al rumore del circuito restano
  √(10² − 1²) = **9,95 µV**, cioè la quota non vincola in pratica il progetto
  del blocco.
- **È il numero che il progetto usava già.** Il precedente di Fase 2 (1 mV di
  picco a 100 Hz), rifatto sul PSRR di oggi, dà **0,551 µV** in uscita.
  Questa ADR lo rende un vincolo; non ne cambia l'ordine di grandezza.
- **In ascolto.** Con la Nota su E5 (10 µV ≈ +13 dB SPL a 1 m sulle Heresy),
  1 µV sta 20 dB sotto, a circa −7 dB SPL a 1 m.
- **Preferenza dichiarata.** La scelta di 1 µV invece di 0,5 o 2 µV non ha un
  numero dietro. È un ordine di grandezza sotto E5: resta udibilmente
  irrilevante e lascia intatto il budget del circuito.

**È una ADR perché cambia l'insieme dei progetti conformi** (criterio di L15).
Un progetto con 5 µV di rumore e 5 µV di ripple fa 7,07 µV e passava E5; con
questa quota non passa più.

## Alternative scartate

- **Metà e metà della potenza (7,07 µV ciascuno).** Il rumore del circuito
  potrebbe salire solo a 1,67× il pavimento senza flicker, prima di sapere
  quanto flicker c'è.
- **Il residuo di E5 dopo la misura del rumore.** Non è decidibile oggi
  (NC-004), e lega l'alimentatore a una cifra che cambierà in Fase 4.
- **Un limite sul solo rail +.** Il rail − è 12-56 dB più robusto fra 100 Hz
  e 10 kHz, ma non è immune: a 50 Hz il suo PSRR è 69,51 dB. Scriverlo nel
  verbo non costa nulla.

## Cosa non supera, e cosa non decide

**Non supera** E5, ADR-010 né ADR-015: E5 resta 10 µV totali, e questa ADR ne
riserva una parte.

**Non decide:**
- **il rimedio** — regolatore a bassissimo rumore o moltiplicatore di capacità
  per gli stadi d'ingresso. È del lotto dell'alimentatore, con i numeri di
  dropout e di calore che solo quel progetto ha;
- **sopra 20 kHz.** E5 non vede quella banda, e il verbo è cieco: 100 mV a
  100 kHz sul rail + passano. Eppure lì il PSRR+ vale **10,20 dB** a +10 dB e
  lì lavora uno switching. Il limite fuori banda va deciso con l'alimentatore;
- **l'accoppiamento magnetico del toroide** (ADR-010, conseguenza 2), che non
  passa dai rail.

## Da riaprire se

- Il rumore del circuito misurato con i modelli veri, oppure sul prototipo,
  **supera 9,95 µV**: allora la quota va ripartita di nuovo, con una ADR nuova.
- Il rimedio non riesce a stare in 1 µV senza violare il budget termico di
  ADR-010 e ADR-015.
- Il dimensionamento della Fase 4 o di L27 abbassa il PSRR+ minimo: la quota
  resta, ma i limiti per tono della nota si ricalcolano.
