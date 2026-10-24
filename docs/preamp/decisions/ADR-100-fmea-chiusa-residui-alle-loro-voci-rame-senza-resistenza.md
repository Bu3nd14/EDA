# ADR-100 — La FMEA della scheda audio si chiude, i residui alle loro voci; il rame dei regolatori regge anche la resistenza in corto

Data: 2026-10-24 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Chiude NC-042** con la sintesi di ADR-070 dopo i rimedi (L45d2b3b3). Non cambia nessun criterio:
  ADR-069 / ADR-081 (PR-30, P10 sulla Stax ≤ 150 ms con ADR-086 / ADR-089 / ADR-098), ADR-021 (P7),
  la forma di ADR-070 e le due eccezioni di ADR-071.
- **Estende NC-072 e ADR-092**: il rame al layout sotto i regolatori dei rail va dimensionato anche per
  il guasto di R550 / R551 in corto.
- Le destinazioni dei residui sono quelle già decise: ADR-073, ADR-077, ADR-082, ADR-085, ADR-097 (le
  accettate e l'esclusa), ADR-071 / ADR-076 / ADR-078 (la diagnosi, L58), NC-073 e NC-075 (la scelta
  della parte), L45d2a (il fusibile e la massa a G2).

## Contesto

L45d2b3b3 (`data/2026-10-24/L45d2b3b3/`, README; report
`reports/2026-10-24-L45d2b3b3-sintesi-fmea.md`) ha messo le colonne dopo il rimedio di ADR-070 su ogni
riga: le 469 delle quattro tabelle di L45 e 70 righe nuove delle parti aggiunte dopo (61 misurate, 9 a
calcolo). Le regole, provate prima sulle colonne pubblicate (`verifica.py`: 469 + 173 + 112 righe e i
tassi delle quattro tabelle uguali; col sabotaggio 506 diverse). Le 44 corse della Stax sui modi delle
cinque parti di ADR-099, che nessun lotto aveva corso, provate prima su tre casi di L45d2b3b2b2 (uguali
al decimo di ms): il blocco al rail per tre modi, 115,5–124,0 ms, gli altri 0 ms.

Dopo i rimedi: **26 righe ad alta priorità** (erano 100 sulle tabelle di prima), **71 medie**, 441
basse, 1 esclusa. Nessuna riga fuori dal criterio è senza destinazione. Una riga nuova non ne aveva:
R550 / R551 in corto (calcolo) riportano il regolatore dov'era prima di ADR-092 — **91,6 / 113,7 /
135,9 °C** (+) e **91,6 / 114,4 / 137,2 °C** (−) a rete −10 / 0 / +10 % con la R_thJA del costruttore
(`data/2026-10-20/L45d2b2a/rpre.csv`, 0 Ω), contro 125 °C, senza un segno; ~0,025 FIT.

## Decisione

Parole dell'utente (2026-10-24), alle due domande coi numeri:

1. **«Nel rame del layout»**: R550 / R551 in corto vanno a **NC-072**. Il rame sotto il pad termico
   dei regolatori si dimensiona e si verifica **anche senza la resistenza**: ≤ 125 °C a rete +10 % con
   60 °C d'aria con R550 / R551 a 0 Ω (2,34 / 2,38 W). Il circuito non cambia.
2. **«Chiudere, residui alle loro voci»**: **NC-042 si chiude**. I residui:
   - **accettati** con la loro ADR: la riserva del firmware a 2,2 ms coi sorveglianti ciechi (ADR-073,
     10 righe alte), il regolatore dei 5 V che porta il corto e si spegne da sé (ADR-097, 2), Δ perso
     (ADR-077), il condensatore d'uscita in corto (ADR-082), le righe invariate di L45d2a;
   - **alla diagnosi, L58** (prima di G1): 46 righe latenti — il mute che non si inserisce (ADR-076, 8
     alte), il degrado silenzioso del blocco (ADR-071), lo standby acceso per guasto (ADR-078);
   - **alla scelta della parte**: NC-073 (C509 / C510 in corto, l'impulso in R550 / R551; la bobina di
     K501 in corto, R552 a 2,7 W per ~0,2 s) e NC-075 (C145 in corto, l'impulso in R144 / R152);
   - **a G2**: il fusibile F501 (L45d2a), il pin di massa di J1 (NC-044), C536 aperto (la stabilità dei
     regolatori dei 5 V senza il condensatore, al banco);
   - **a NC-072**: R550 / R551 in corto (punto 1).

## Perché

- **La FMEA è completa sul circuito di oggi.** Ogni riga ha l'effetto misurato (o calcolato, e scritto
  così) e la fonte; le 88 + 9 righe dei rimedi costruiti sono rimisurate (L45d2b3b1, L45d2b3b2b2,
  L45d2b2b1 / b2), i quindici guasti del calore sul blocco del sorgente con ADR-099.
- **Le righe alte rimaste non chiedono altro alla FMEA**: o sono una decisione già presa con la sua
  ADR, o un lotto che c'è già prima del congelamento (L58), o la scelta di una parte con la sua non
  conformità aperta. Tenere NC-042 aperta fino a L58 avrebbe duplicato la tracciatura di quel lotto,
  che nella tabella dei lotti porta già «NC-042 (i latenti)» ed è prima di G1.
- **Il rame di NC-072 regge già il caso, di poco.** La soglia di oggi, ≤ 27 °C/W, con 0 Ω dà
  60 + 27 × 2,38 = **124 °C** (121 °C con gli 0,1 W che lo Schottky in serie di ADR-093 toglie al
  regolatore), dentro 125 °C con ~1 °C di margine. ADR-100 lo rende un vincolo: senza, una scelta del
  rame tarata sui 122 °C del regolatore con la resistenza (fino a ~33 °C/W) lascerebbe il guasto a
  137 °C.
- **Sdoppiare R550 / R551 non basta**: con una metà da 2,2 Ω in corto resta 129,3 / 130,2 °C a rete
  +10 % (`rpre.csv`).

## Alternative scartate

- **Accettare R550 / R551 in corto** (0,025 FIT, latente; dentro a rete nominale, 114 °C): scelta
  dell'utente il rame.
- **Lasciare NC-042 aperta fino a L58**: vedi sopra.
- **Sdoppiare R550 / R551**: non chiude il caso (sopra), e porta due parti per regolatore.

## Da riaprire se

- Il layout non tiene il regolatore ≤ 125 °C con R550 / R551 a 0 Ω a rete +10 % (il calcolo o la
  misura sul prototipo, NC-072): si torna all'utente con la cifra.
- L58 trova che un guasto latente non si può vedere a un costo ragionevole (il «Da riaprire se» di
  ADR-071).
- Un lotto prima di G1 (L57, L54, L55, L58) cambia il blocco o l'alimentatore: le righe delle parti
  toccate si rifanno, e se una esce dal criterio senza destinazione la voce si riapre.
- Le righe invariate di L45 (275, misurate sul circuito di allora e non toccate da nessun rimedio)
  risultano toccate da un cambio successivo che la sintesi non ha visto.
