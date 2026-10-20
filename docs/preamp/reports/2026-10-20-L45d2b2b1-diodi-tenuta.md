# L45d2b2b1 — I diodi della tenuta e il regolatore negativo

Data: 2026-10-20 · Lotto: L45d2b2b1 (prima parte di L45d2b2b) · Dati: `data/2026-10-20/L45d2b2b1/`
(README) · Decisione: **ADR-093** · Non conformità: **NC-073 aperta**, NC-042 e NC-072 avanzano

## In breve

- **L45d2b2b in due parti** («Due parti», l'utente all'inizio): questa, i diodi della tenuta e U502
  (ADR-074, scelta 3); L45d2b2b2, il limite del comando e il limitatore sui 5 V (ADR-075, scelta 4).
- **Rifatta la misura di ADR-074 sul circuito di oggi**, come chiedeva il prompt: R550 / R551 (ADR-092)
  stanno ora fra il serbatoio e il piedino, e il quadro è cambiato in due versi opposti.
  - I corti **sul serbatoio** (C501, C502, D501) stanno meglio: la resistenza rallenta la scarica, il
    jack si apre prima del crollo, ~25–38 dB SPL. U502 resta però oltre il suo massimo: 0,52–0,55 V di
    uscita sopra l'ingresso per 61–105 ms, contro 0,3 V.
  - I corti **sul piedino** (C509 / C510 in corto; l'ingresso di un regolatore a massa al suo interno),
    che L45c1 dava uguali al serbatoio, sono il caso peggiore della serie: tutta la capacità del rail
    torna nel corto attraverso D510 / D511, **68 A** in un 1N5819, **3,9 V** oltre l'ingresso, il jack
    che si apre col rail a −0,7 V, **~78 dB SPL** (16,7 mV).
- **Il rimedio, «In serie, 4,7 Ω»** (ADR-093): uno Schottky SB340 in serie dopo ciascun regolatore, la
  retroazione sul piedino, la tensione impostata a ~15,3 V, due SB340 sul piedino. Sul sorgente:
  24 righe su 24 col jack prima del crollo, U502 a **0,278 V**, **~32 dB SPL**; regolatore 119,7 °C
  (era 122,2), riserva a rete −10 % **1,09 V**; tenuta e accensione come prima.
- **Trovato, e aperto come NC-073** («Non conformità aperta»): nei corti sul piedino R550 / R551 prendono
  80–100 W per ~0,1 s (5–9 J), finché il firmware non stacca la rete. Succede da ADR-092.

## Il banco

Il banco dell'alimentatore di L45d2b2a, copiato in `psu/`, con le righe di ADR-074 di L45c1 nel suo
`modi.py` (che era quello di L45c2, senza i rail) a tre reti, le sonde al piedino e sui diodi, e le
opzioni come argomenti (README).

**Controllato prima su due casi noti**: la netlist di prima di ADR-092 con le opzioni e il carico di
L45c1 ridà C501 e C502 in corto con gli stessi tempi e la stessa uscita oltre l'ingresso, **1,7562 /
1,7609 V**; la catena audio ridà C501 a **9,017 mV** (L45c1 9,0) e C502 a 0,2455 mV (L45c1 0,2353, la
scheda audio di oggi). Senza opzioni il deck della rete è quello di L45d2b2a riga per riga.

**La sonda nuova sui diodi spiega la cifra di L45c1**: 25,4 A in D511. Al modello generico del
1N5819 (Rs 50 mΩ) 25 A danno 1,76 V. Nessuno Schottky resta sotto 0,3 V portando la scarica del rail.

**Un caso che non converge**: C502 in corto a rete nominale si ferma a TE + 61 ms con «Timestep too
small» sulla sonda d'ingresso di U502, con tutti e due i metodi. A −10 e +10 % passa, con cifre quasi
uguali (0,550 / 0,547 V): le due reti lo racchiudono. Con la forma scelta converge.

## Le righe di ADR-074, oggi e con i rimedi

Il caso peggiore sulle 24 righe (`confronto_opzioni.csv`):

| | Oggi | Solo SB340 sul piedino | In serie, 4,7 Ω | In serie, 3,3 Ω | **Sorgente** |
|---|---|---|---|---|---|
| righe col jack dopo i 10,6 V | 6 (su 23) | 6 | 0 | 0 | **0** |
| uscita oltre l'ingresso di U502 | 3,94 V | 1,64 V | 0,307 V (0,279 con due SB340) | 0,312 V | **0,278 V** |
| tempo oltre 0,3 V | 105 ms | 77 ms | 0,1 ms (0) | 0,2 ms | **0** |
| corrente di picco sul piedino | 68 A | 82 A | 0,22 A | 0,25 A | **0,21 A** |
| rail − all'apertura del jack | −0,70 V | −0,62 V | −13,19 V | −13,19 V | **−13,19 V** |

**Il colpo al jack** (catena di L45c1, picco filtrato a 100 kΩ, principale): oggi C510 16,7 mV (~78 dB
SPL), C509 12,8 mV (~76, letto fino ai rimbalzi), C501 0,16 mV, D501 a / b 0,17 mV, gli altri ≤ 43 µV;
con la forma scelta il peggiore **86 µV (~32 dB SPL)**, tutte le corse passano la guardia.

**Il calore e la tenuta** (deck della rete, `rete_opzioni.csv`):

| | Oggi | In serie, 4,7 Ω | In serie, 3,3 Ω | **Sorgente** |
|---|---|---|---|---|
| U502 a rete +10 %, 60 °C d'aria | 122,2 °C | 119,1 °C | 123,5 °C | **119,7 °C** |
| riserva di U502 a rete −10 % (≥ 1 V) | 1,32 V | 1,02 V | 1,46 V | **1,09 V** |
| il diodo in serie | — | 0,098 W | 0,098 W | **0,099 W** |
| tenuta di `VRELAY` a −10 % (≥ 25 ms) | 46,37 ms | 46,37 ms | 46,37 ms | **46,37 ms** |

La tenuta di P9 (b) non cambia: i condensatori restano sul rail. Il «Da riaprire se» di ADR-074 non
scatta.

## Perché la retroazione sul piedino

La prima forma provata (`uscita_dsch`) regolava il rail, dopo il diodo: rail esatto a 15 V. Ma la
resistenza dinamica del diodo (~0,09 Ω a 0,3 A) con la capacità del rail (~3,6 mF) fa un polo vicino a
500 Hz dentro l'anello del regolatore. Il banco ha un regolatore comportamentale senza dinamica, e non
lo vede. Con la retroazione sul piedino l'anello è quello di oggi (il regolatore vede il suo 10 µF), e
il rail è il piedino meno la Vf: la tensione impostata sale di ~0,3 V. Costa la Vf sulla riserva in
tutte e due le forme.

Il rail ha ~0,1 Ω in più sotto ~400 Hz, dove la tenuta non lo copre ancora: è nel «Da riaprire se».

## Le parti

L'agente bom-component-manager (solo web) ha proposto e letto: **Vishay SB340** (40 V, 3 A, 120 A di
picco, DO-201AD; Vf tipica ~0,31 V a 0,3 A e ~0,42 V a 2,5 A, curva letta a occhio) per entrambi i
ruoli; onsemi MBR140ESF scartato (0,43 V a 0,3 A, 30 A di picco); ST STPS3L40S senza la curva; Nexperia
PMEG4010CEH non acquistabile fino al 2027. Disponibilità: Digi-Key ~5–6 mila pezzi (Mouser non letto).
Nessun modello SPICE del costruttore trovato: il banco usa i parametri ricavati dalla curva (README).

## Il sorgente

`psu.py` 124 parti (D513–D516 nuove; D510 / D511 SB340; U501 «15.3V», R501 120 kΩ; `VPLUS_REG`,
`VMINUS_REG`); i due «errori» dell'ERC di sempre, ora su `VPLUS_REG`, 22 avvisi. Il disegno
dell'alimentatore ha il diodo nel riquadro del regolatore e asserisce la forma; la netlist di prima è
rifiutata. Sul sorgente il banco ridà l'opzione: le 26 righe, la rete, l'accensione (jack a 716 ms,
MUSICA a 726 ms, anche a −10 %), i colpi.

## Limiti dichiarati

- **La Vf dell'SB340 è letta a occhio da una curva tipica a 25 °C** (±0,03–0,05 V): i 22 mV di margine
  sull'uscita di U502 stanno dentro l'incertezza. A freddo la Vf sale.
- **Il regolatore è comportamentale**: niente corrente inversa, niente dinamica d'anello. I modelli
  del costruttore dei due regolatori sono in `vendor/` ma non sono mai stati usati in ngspice.
- **Le temperature** usano i 32,5 °C/W della scheda JEDEC del costruttore (ADR-092).
- **Il NR/SS di U502 verso l'ingresso** (massimo −0,3 V) ha lo stesso limite dell'uscita: in un corto
  sul piedino il suo condensatore da 470 nF resta a −1,2 V per un istante. È la carica di 0,5 µC di un
  condensatore che il costruttore raccomanda; non è letto dal banco.

## Che cosa resta, e a chi

- **L45d2b2b2**: il limite di corrente sul comando e il limitatore sui 5 V (ADR-075).
- **NC-073**: l'impulso di R550 / R551, alla scelta della parte.
- **L45d2b3**: le righe di ADR-074 nella forma di ADR-070, coi modi nuovi delle parti nuove (D515 /
  D516 aperti o in corto, D513 / D514).
- **NC-072**: il rame sotto i regolatori, al layout dell'alimentatore.
