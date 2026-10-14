# Le fonti dei tassi di guasto di L45c2 (ADR-070)

ADR-070 chiede i tassi da **SN 29500** o **IEC 61709** e la ripartizione dei modi da **FMD-2016**.
Nessuna delle tre è pubblica: SN 29500 si compra da Siemens, IEC 61709 dall'IEC, FMD-2016 da
Quanterion (l'estratto gratuito non ha le tabelle). È il caso del «Da riaprire se» di ADR-070, e
l'utente ha scelto (2026-10-14, «Stima dichiarata»):

- **integrati**: il tasso di riferimento di SN 29500-2 che il costruttore riporta nel suo documento
  «Functional Safety FIT Rate, FMD and Pin FMA», per il pezzo o il parente più vicino;
- **passive e discrete**: un **ordine di grandezza dichiarato come STIMA**, al telaio caldo (60 °C
  d'aria, ADR-021). Le classi di probabilità sono decadi: un fattore 2–3 cambia la classe di rado.
  Se la norma arriva, i valori di tabella entrano in **L45d**, che riporta comunque tutte le tabelle
  alla forma di ADR-070;
- **ripartizione dei modi**: **MIL-HDBK-338B, Tabella 7.8-1**, pubblica, dai dati di **FMD-91**
  (l'edizione 1991 della stessa raccolta di FMD-2016); il testo è in
  `mil_hdbk_338b_tab_7_8_1.txt`. Dove il costruttore dà la sua ripartizione, si usa quella.

| Tipo | FIT della parte | Fonte | Ripartizione |
|---|---|---|---|
| comparatore (U505, U506, U508: TLV1702) | 12, il doppio | TI SFFS282, TLV1812/1822-Q1: SN 29500-2 tab. 4, 12 FIT a 55 °C | TI: uscita aperta 15 %, alta 25 % (per un'uscita open-drain = rilasciata: cieco 40 %), bassa 25 %, fuori specifica 30 %, corto fra due pin 5 %; per canale la metà |
| regolatore (U503, U504) | 50 | TI SFFS612, TPS748A-Q1: SN 29500-2 tab. 4, «LDO > 1 W», 100 FIT a 90 °C; **dimezzato (STIMA)**: i nostri dissipano meno di 1 W e stanno più freddi | TI: niente in uscita 35 %, uscita che segue l'ingresso 10 %, fuori specifica 45 % (diviso sulle 8 righe di U503 che spostano la tensione), corto fra due pin 5 % |
| riferimento (U507: LM4040) | 20 | TI SNOAA48A, LM4040-N-Q1: SN 29500-2 tab. 5, 20 FIT a 55 °C | 338B «Diode, Zener, Voltage Reference»: deriva .69, aperto .18, corto .13 |
| resistenza a film | 0,5 | STIMA | 338B: aperto .59, deriva .36, corto .05 |
| ceramico | 1 | STIMA | 338B: corto .49, valore .29, aperto .22 |
| elettrolitico (C520, C523) | 10 | STIMA (sensibile alla temperatura) | 338B: corto .53, aperto .35, perdita .10, capacità .02 |
| diodo di segnale | 1 | STIMA | 338B: deriva .58, aperto .24, corto .18 |
| raddrizzatore, Schottky (per diodo) | 2 | STIMA | 338B: corto .51, aperto .29, deriva .20 |
| zener di bloccaggio | 2 | STIMA | 338B: aperto .45, deriva .35, corto .20 |
| MOSFET di segnale | 3 | STIMA | 338B: corto .51, uscita bassa .22, deriva .17, aperto .05, uscita alta .05; per un interruttore: acceso = .41 + .22, spento = .05 + .05, G-S e G-D .05 ciascuno (IPOTESI: la parte del gate presa dai .51) |
| bipolare di segnale | 2 | STIMA | 338B: corto .73, aperto .27 |
| relè di rete (K501) | 20 | STIMA (poche manovre: una per accensione) | 338B: non commuta .55 (IPOTESI: bobina aperta .25, un polo saldato .27, due poli .03), commuta da sé .26, corto .19 |
| piccolo trasformatore (T2) | 10 | STIMA | 338B: aperto .42, corto .42, deriva .16 |
| fusibile (F501) | 5 | STIMA | 338B: non apre .49, lento .43, apre da sé .08 |
| contatto o filo del cablaggio | 0,5 | STIMA | 338B «Connector/Connection»: aperto .61, intermittente .23, corto .16 |
| rame (NT501) | 0,05 | STIMA | 338B «Printed Wiring Assembly»: aperto .76, corto .24 |

I documenti dei costruttori, letti il 2026-10-14:
- TI SFFS282, *TLV1812-Q1, TLV1822-Q1 Functional Safety FIT Rate, FMD and Pin FMA*:
  https://www.ti.com/lit/pdf/sffs282
- TI SFFS612, *TPS748A-Q1 Functional Safety FIT Rate, FMD and Pin FMA*:
  https://www.ti.com/lit/pdf/SFFS612
- TI SNOAA48A, *LM4040-N-Q1 Functional Safety FIT Rate, FMD and Pin FMA*:
  https://www.ti.com/lit/pdf/snoaa48
- MIL-HDBK-338B, Section 7, Table 7.8-1 (pp. 7-193 – 7-199), copia letta:
  https://safetyconsult.tech/wp-content/uploads/2019/02/failure_modes_mil_hdbk_338b.pdf

**Che cosa non è stato fatto, e perché.** Il tasso non è portato alla temperatura di ogni parte col
modello di stress della norma (ADR-070 lo chiede): senza la norma il fattore di temperatura sarebbe
un'altra stima. Le stime sono già pensate per il telaio caldo; il regolatore è dimezzato per la
temperatura più bassa del riferimento di TI. Il micro (U509) non ha righe: i suoi guasti sono di
L54.
