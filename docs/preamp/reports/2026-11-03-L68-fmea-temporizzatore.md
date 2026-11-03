# L68 — la FMEA del temporizzatore a comparatori

Data: 2026-11-03 · Lotto: L68 · Decisioni: **ADR-115**. Non conformità: **chiusa NC-078**, **aperta
NC-079**. Dati: `data/2026-11-03/L68/` (README). Il circuito non è cambiato.

## In breve

- **Le scelte dell'utente**: la ritenuta cieca, **«Accettare come R585»**; R572 / R576 in corto, **«Non
  conformità maggiore»** (NC-079); i 5 V a massa da C545–C547 e TP507, **«Accettare come C536»**; i colpi
  al jack di J4 e dei test point, **«Accettare tutti»** (ADR-115).
- **125 righe nuove**: 97 delle 37 parti del temporizzatore, 11 dei pin dei 5 connettori, 17 dei test
  point. **34 alte, 3 medie, 88 basse.** La FMEA di oggi ha **sei fonti, 688 righe** (49 alte, 70 medie,
  564 basse, 5 escluse); **dell'alimentatore 0 parti su 187 senza riga**: NC-078 chiusa.
- **Le corse**: 662 sequenze sul banco di L64c (79 simulazioni distinte del temporizzatore × 8 eventi, 4
  dei connettori × 4, 13 test point in musica, la base in musica), ~25 s l'una, tre insieme; **nessun
  ripiego numerico**. Le due basi di controllo uguali a L64b colonna per colonna. La catena al jack su 20
  casi: il controllo `corto_u503` ridà **6,492 mV**.
- **Trovato**: 31 guasti singoli rendono cieca la ritenuta come R585 in corto; con R572 o R576 in corto la
  ritenuta che scatta tiene i 5 V a massa con 0,25 A e porta Q513 a ~209 °C (NC-079).
- **Il dossier rigenerato**: «OK», `index.html` 320 KB; **sabotaggi 61 su 61**.
- **L'ordine verso G1** (l'utente, «Prima la correzione»): **L69** (NC-079, il circuito cambia) → L65 → G1.

## Il banco

La copia del banco di L64c in `psu/`. I modi in `modi.py`, latenti da t = 0 (`RIGHE_L68`): per i tre
TLV1704 l'uscita di ogni canale aperta (il token dell'uscita su un nodo nuovo), bloccata bassa (in corto
verso RLY_RET; per un'uscita a collettore aperto «bloccata alta» è l'uscita aperta) e l'alimentazione
persa. Quest'ultima è **un'ipotesi**: le quattro uscite aperte, come fa il comparatore di comportamento
sotto 2 V (il datasheet non dice che cosa fa un TLV1704 senza alimentazione). Col piedino dei 5 V lasciato
flottante ngspice si fermava sul comparatore (`f_u513_alim_accs`, «timestep too small»): la primitiva
`aperti` di `genera_tb_psu.py` apre le quattro uscite insieme. I modi sugli stessi due nodi sono un caso
solo: le uscite di U513 A / B / C bloccate basse sono AT_PG a massa; U514 A / B bloccate e C549 in corto
sono AT_MRQ a massa; Q513 in corto base-emettitore, R583 e C554 in corto sono AT_BN a massa; le uscite di
U515 C / D bloccate e C553 in corto sono AT_F a massa, cioè R585 in corto di L58a2.

I connettori: le bobine dei relè e gli interruttori entrano nel deck dopo il guasto, quindi un pin si apre
dal lato dell'alimentatore (il pozzo e il suo bloccaggio per MUTE_CMD e PERMIT_CMD; il pull-up e il polo
d'ingresso per MUTE_SW e FRONT_SW). J510 aperto è la perdita di rete; J511 è il primario di T2 (la riga di
T2 «secondario aperto (o F501, J514, primario)»); J512 è K501 che si apre in musica (misurato come TP514,
MAINS_G a massa). I test point: la sonda che scivola sul riferimento accanto, in musica; i quattro
riferimenti (TP503, TP506, TP511, TP517) non fanno niente.

**I conti detti all'utente prima delle corse**: 125 righe, 79 + 4 + 13 simulazioni, ~660 corse, ~1,5 h a tre
insieme (misurata una corsa: 25 s).

## Le corse

662 corse, tutte con `ok.txt` e le opzioni della loro riga. `f_r570_corto_perds` si fermava a TE + 0,98 s
(«timestep too small» nel regolatore dei 5 V, a rete persa da ~1 s): accorciata a TE + 0,9 s
(`modi.TF`, ora anche per le sequenze), dopo il jack, il guadagno e K501 della perdita sana. Il confronto
(`confronto_l68.csv`) usa i criteri di L54b3b contro la corsa sana di ogni evento: L64b per gli eventi del
temporizzatore, la base nuova per la musica. `arm_pg_ms −1383,5` nelle accensioni a freddo è l'artefatto
di limitations #85 (i deck coi guasti sondano anche VREF), tolto dalle righe.

**Le famiglie** (righe di `fmea_l68.csv`; gravità 1: 29, 2: 51, 3: 8, 4: 31, 5: 6):

| Che cosa | Righe | Gravità |
|---|---|---|
| Come la corsa sana, un margine (la base di Q513 a 0,46–0,60 V senza scattare), o un tempo fuori dal suo criterio col jack già staccato (il permesso 15,4–15,9 ms dopo il mute; K501 prima dei 50 ms dal permesso): al jack ≤ 13,9 µV, 16,3 dB SPL | 29 | 1 |
| Non si accende (mute tenuto, o la ritenuta che scatta all'accensione): nessun colpo | 35 | 2 |
| Una funzione persa che si vede (il tasto del mute, il frontale che non spegne), o la musica rilasciata all'alimentazione buona senza il ritardo (548,6 ms invece di 1209,3; dopo un buco 1,1 ms), come D536 aperto di L58a (~2 dB SPL) | 16 | 2 |
| Un colpo al jack sopra l'obiettivo, sotto il tetto (J4 PERMIT_CMD, sei test point a 69,7 dB SPL; TP501 / TP502 a 97,0 dB SPL all'uscita fissa 1) | 8 | 3 |
| **La ritenuta cieca**: K501 chiuso dopo un rail che cade, il mute che si inserisce | 31 | 4 |
| **I 5 V a massa**: C545–C547, TP507; e attraverso la ritenuta scattata, R572, R576 in corto | 6 | 5 |

## Il calore

`calore_5v.csv` su tutte le corse: C545 in corto **2,99 W, 245 °C** (come C536); TP507 in musica U504
232 °C, U512 132 °C; R570 in corto 0,59 W, 97 °C, dentro (i canali di U513 che tirano giù AT_PG sui 5 V: al
più 3 × 5 V × 20 mA di corto del datasheet, 0,3 W, 98 °C con 128,1 °C/W, dentro i 150 °C). **R572 e R576
in corto, col rail che cade** (o all'accensione con un rail morto): la ritenuta scattata ha l'anodo su
AT_ON, che è sui 5 V (R576) o li riceve da AT_MRQ attraverso D537 (R572). U504 va al limite, 0,25 A, e
dissipa 2,55 / 2,34 W, **218 / 205 °C**; la corrente passa da Q514 nella base di Q513 a V_BE 1,48 V: **Q513
~0,37 W, ~209 °C** (BC847, Diodes DS11108: 403 °C/W con la piazzola minima, Tj max 150 °C; e 0,25 A di
emettitore contro i 200 mA di picco).

## La catena al jack

20 casi (`catena/tabella_l68.csv`, criterio ≤ 2 mV scritto prima): il controllo `corto_u503` **6,492 mV**.
Sotto: i tempi del permesso e di K501 (≤ 13,9 µV, 16,3 dB SPL), J4 MUTE_CMD aperto (32 pV), TP514 (15,6
µV, 17,3 dB SPL). Sopra: **6,49–6,51 mV, 69,7 dB SPL** per J4 PERMIT_CMD aperto in musica (i relè del
guadagno cadono col jack collegato) e per TP504, TP505, TP507 (i relè insieme), TP509, TP510, TP516 (il
guadagno prima del jack): il colpo di U503 in corto. **0,15 V, 97,0 dB SPL all'uscita fissa 1** per TP502
(il rail − a massa). TP501 (il rail + a massa) si ferma 4 ms dopo il corto, nella scheda audio:
**dichiarato** per simmetria con TP502.

## Fuori dal criterio, all'utente

Le quattro domande, per nome e coi numeri (2026-11-03):

1. la ritenuta cieca, 31 righe: **«Accettare come R585»** → P9 (e) estesa (ADR-115);
2. R572 / R576 in corto, Q513 a ~209 °C: **«Non conformità maggiore»** → **NC-079**, prima di G1;
3. i 5 V a massa da C545–C547 e TP507: **«Accettare come C536»**;
4. i colpi a 69,7 dB SPL e i 97 dB SPL del rail a massa da test point: **«Accettare tutti»**.

## Il dossier

`build_dossier.py`: la sesta fonte in `FMEA_FONTI`, la FMEA di oggi e la copertura lette da L68, «Cosa
non dice» che non dichiara più la FMEA dell'alimentatore incompleta (e nomina i due limiti nuovi: i test
point senza tasso, l'alimentazione persa come ipotesi). Il primo giro rifiutava: NC-079 non era nel
registro. Dopo il registro e ADR-115, «OK». `sabotaggi.py`: quelli di L64a, L64b, L64c (i due su
`fmea_oggi.csv` e `copertura.csv` riportati sui file di L68, perché quelli di L64c non si leggono più) e
sei nuovi: **61 su 61 cadono**, il generatore sui file veri esce 0 prima e dopo.

## Trovato

- **La ritenuta ha un canale solo**: R585 in corto (ADR-109) non era un caso isolato; 31 guasti singoli del
  temporizzatore la rendono cieca. Il mute regge in tutti.
- **NC-079**: un pull-up sui 5 V che arriva all'anodo della ritenuta la trasforma in un corto dei 5 V, con
  un transistore SOT-23 fuori dai suoi limiti.
- Con U514 D cieco, R575 in corto, U515 B cieco o R579 in corto il toroidale resta acceso in standby: la
  musica arriva 14–17 ms dopo il frontale, su rail già fermi.

## Errori

- La prima lista di prova aveva due modi che il banco rifiutava (l'alimentazione persa col piedino
  flottante; i pin di J4 e di J508 su righe che entrano dopo il guasto): trovati con 6 corse di prova e
  `script/genera_solo.py` (un deck per caso senza correrlo), prima della lista lunga.
- La copia di `fmea_oggi.py` puntava la fonte di L64c alla propria cartella: corretto prima del primo giro.
