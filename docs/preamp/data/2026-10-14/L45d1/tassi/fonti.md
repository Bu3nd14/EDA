# Le fonti dei tassi di guasto del riporto di L45d1 (ADR-070)

La regola è quella di L45c2 (`../../L45c2/tassi/fonti.md`), scelta dall'utente il 2026-10-14
(«Stima dichiarata») e confermata all'inizio di L45d1 («No, stima dichiarata»: né SN 29500 né
FMD-2016 sono arrivati):

- **integrati**: il tasso di riferimento di SN 29500-2 dal documento di sicurezza funzionale del
  costruttore;
- **passive e discrete**: un **ordine di grandezza dichiarato come STIMA**, al telaio caldo (60 °C
  d'aria, ADR-021);
- **ripartizione dei modi**: **MIL-HDBK-338B, Tabella 7.8-1** (il testo è in
  `../../L45c2/tassi/mil_hdbk_338b_tab_7_8_1.txt`); un'**IPOTESI** dichiarata dove la tabella non ha
  il modo.

I tipi di L45c2 valgono come sono (`script/tipi.py` li legge da `classi_l45c2.py`, non li copia). I
tipi nuovi, per le parti del blocco di guadagno, dei controlli e dei rail:

| Tipo | Parti | FIT della parte | Fonte | Ripartizione |
|---|---|---|---|---|
| bipolare di segnale (`BJT_S`) | Q106, Q117, Q118, Q121A/B (LS352), Q127, Q146, Q148 | 2 | STIMA | 338B «Transistor, Bipolar»: corto .73, aperto .27; **IPOTESI**: il corto diviso a metà fra C-E e B-E (.365 ciascuno), l'aperto è l'emettitore aperto del banco di L45a |
| bipolare SOT-223 (`BJT_V`) | Q122, Q125 (DZT5401 / DZT5551) | 5 | STIMA (VAS e carico a ~84 °C di giunzione, L56) | come sopra |
| finale (`BJT_P`) | Q132, Q133 (MJE15032 / MJE15033) | 10 | STIMA (classe A, il più caldo del blocco) | come sopra |
| JFET (`JFET`) | JQ110A/B (le due metà dell'LSK489) | 3 | STIMA, per metà | 338B «Transistor, FET», come il MOSFET di L45c2: corto D-S .41 + uscita bassa .22, source aperto .05 + uscita alta .05, G-S .05 (**IPOTESI**, come L45c2) |
| film plastico (`C_film`) | C_OUT 4,7 µF, C_T 10 µF, C_IN 1 µF | 1 | STIMA | 338B «Capacitor, Plastic»: aperto .42, corto .40, valore .18 |
| relè di segnale (`RELE_S`) | G6K: K1–K16 | 10 | STIMA (poche manovre al giorno) | 338B «Relay»: non commuta .55 (**IPOTESI** come K501: bobina aperta .25, un polo saldato .27, due poli .03), commuta da sé .26 (un polo che si apre, un rimbalzo, un bistabile che cambia da solo), corto .19 (**IPOTESI**: bobina .14, **isolamento fra bobina e contatti .05**) |
| LED (`LED`) | i LED a pannello | 1 | STIMA | 338B «Optoelectronic LED»: aperto .70, corto .30 |
| commutatore (`ROT`) | SW1, SW2, SW4 | 10 | STIMA | 338B «Rotary Switch»: uscita errata .53, contatto .47 |
| regolatore > 1 W (`LDO_P`) | U501 (TPS7A4701), U502 (TPS7A3301) | 100 | TI SFFS612 (TPS748A-Q1): SN 29500-2 tab. 4, «LDO > 1 W», 100 FIT a 90 °C — **non dimezzato**: U501 e U502 cadono ~5 V a ~0,3 A, 1,5 W | TI, come U503: niente in uscita .35, segue l'ingresso .10, fuori specifica .45 (diviso sulle 10 righe di U501 che spostano la tensione), corto fra due pin .05 |

Gli altri tipi delle parti nuove sono già di L45c2: resistenza a film 0,5, ceramico (anche i C0G
C124 e C137) 1, elettrolitico 10 (C104, C116, C141, C142, C145, C501, C502, C505, C506), diodo di
segnale 1 (D102, D103, D3, D12–D19), raddrizzatore / Schottky 2 (D501, D510, D511, D10, D11),
zener 2 (D1, D2), contatto o filo 0,5 (J513, J1).

**Le istanze** (la colonna `frazione` dice «x N»): una riga che vale per N parti uguali moltiplica il
tasso per N, la regola già usata in L45c2 per J514 e R544–R547. Il blocco di guadagno ha 8 istanze
(blocco A, buffer F1 e F2, blocco B, per due canali), R113 4, R138 / R143 2, il disaccoppiamento
C139–C142 di L45c1 8 per parte. I relè sono condivisi fra i canali (un polo per canale) e contano
una volta. Le istanze dei controlli che la fonte non dice sono **IPOTESI** scritte in
`script/classi_l45b.py` (otto ingressi, sei uscite, sei LED a pannello).

**Che cosa non è stato fatto**, come in L45c2: il tasso non è portato alla temperatura di ogni parte
col modello di stress della norma. Il micro (U509) resta senza tasso: è di L54.
