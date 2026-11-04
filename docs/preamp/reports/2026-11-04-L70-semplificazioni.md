# L70 — le due semplificazioni: togliere il rivelatore di rete, la ritenuta → fusibili (2026-11-04)

Lotto L70 (prompt di `NEXT-SESSION.md`, scelta dell'utente in L65 fra le semplificazioni dell'architetto,
righe S1 e S2 e rilievo R12 di `2026-11-04-L65-architetto-avversariale.md`). I dati e gli script sono in
`data/2026-11-04/L70/` (README). Il sorgente **non è cambiato** durante lo studio: le varianti sono copie di
`circuits/preamp/psu.py` scritte da `varianti/fai_varianti.py`, con le loro netlist.

## Le varianti

| Variante | Che cosa | Parti |
|---|---|---|
| oggi | il sorgente di `main` (L69) | 189 |
| **S2** | senza il rivelatore di rete: via R510, R554, R511, Q504, R512, R555, C518, U506 canale A, U513 canale D con R569, D533, D534, D535. Restano il sorvegliante dei rail a 13,5 V (U505) e quello di `VRELAY_REG` (U506 B) | 178 |
| **S1** | senza la ritenuta: via U515 canali C / D, R580, C552, D541, R581, C553, R585, R582, Q513, R583, C554, Q514, R584, C555 (e D534, D535); un fusibile per ramo del secondario di T1, **F502 / F503**, fra J513 e il ponte | 176 |
| **S1+S2** | le due insieme | 167 |
| **S1+S2 dc** | S1+S2 e un fusibile per rail anche sul lato continua, **F504** fra C501 e R550, **F505** fra R551 e C502 (aggiunta dopo le prime corse, sotto) | 169 |

Controllo: la netlist di oggi rigenerata è `circuits/preamp/psu.net` a meno della data; il deck di oggi
generato dal banco copiato è quello corso in L69b a meno del percorso (`script/prova_gen.sh`).

**Il fusibile nel banco** (`psu/genera_tb_psu.py --fusibile`): resistenza a freddo e un modello termico del
primo ordine, h' = i² − h/τ, che fonde quando h arriva all'I²t di fusione del costruttore; una corrente
continua lo fonde solo sopra una soglia ITH fra 1,5 e 2,1 In (IEC 60127-2, i tempi garantiti della
Littelfuse 218). Le corse usano **2,1 In**, il fusibile più lento: è il caso peggiore per la protezione.
Le cifre del costruttore sono in `parti_fusibile.md` (bom-component-manager, con le fonti):
Littelfuse 218 T 5×20, 1 A 6,73 A²s 0,0613 Ω; 1,25 A 12,65 A²s 0,0446 Ω; 1,6 A 23,35 A²s 0,0336 Ω (la
tabella del costruttore non è monotona fra 1 e 2 A: dichiarato); tempi garantiti 2,1 In ≤ 2 min, 2,75 In
0,6–10 s, 4 In 0,15–3 s, 10 In 20–300 ms.

**Un errore mio, corretto**: la prima versione del modello lasciava 1 Ω nel ramo invece di 0,1 mΩ (il
grezzo 1,15 V più basso). Quelle corse sono state buttate e rifatte.

Corse: **310**, tutte con `ok.txt` (nessun ripiego); 5 deck del blocco audio; la catena al jack di S1+S2 a
tre reti (54 corse).

## S2 — senza il rivelatore di rete

**Da solo non sta in piedi.** La ritenuta si arma «con la rete presente», e quell'informazione viene dal
rivelatore (AT_MD attraverso D533 / D534 / D535). Senza, a ogni perdita di rete l'alimentazione cattiva
arriva con la ritenuta armata e la ritenuta scatta:

| Caso (S2 da solo) | oggi | S2 |
|---|---|---|
| perdita di rete, jack | 17,4 ms | 55 / 82 / 110 ms (rete −10 / 0 / +10 %) |
| perdita di rete, ritenuta | no | **scatta** |
| buco di 20 ms | mute, musica dopo 613 ms | **nessun mute** |
| buco di 40 ms | 629 ms | nessun mute |
| buco di 60 / 80 / 100 ms | 630–680 ms | a −10 %: **ritenuta, spento fino al frontale**; a rete nominale e +10 % fino a 80 / 100 ms nessun mute |
| buco di 150 / 200 ms | 672–730 ms | **ritenuta, spento fino al frontale** |

(`an_buchi_oggi.csv`, `an_buchi_s2.csv`, `confronto_s2.txt`.) Un buco di rete di 60–200 ms lascerebbe
l'apparecchio spento finché chi ascolta non spegne e riaccende il frontale. **S2 ha senso solo con S1.**

Con **S1+S2** (nessuna ritenuta): il buco di 20 ms passa senza mute a tutte e tre le reti; quello di 200 ms
muta a 55 / 82 / 109 ms e la musica torna dopo 723 / 682 / 671 ms (`an_s1s2.csv`).

**Al jack principale** (la catena di L64b / L69b, `tabella_s1s2_*.csv`): la perdita di rete **17,7 / 17,3 /
16,9 dB SPL** (rete −10 / 0 / +10 %; oggi 4,3 / −55,2 / −55,3), sotto l'obiettivo di P9 (≤ 2 mV, ~60 dB) e
sotto i 100 µV (~33 dB) di PR-20. Ogni altro caso uguale a oggi: U501 spento 32,2 dB SPL, U503 in corto
69,7 dB SPL (accettato, ADR-051).

**P9 (b) andrebbe riscritto**: «quando mancano le semionde della rete» sparisce, e a rete −10 % `VRELAY`
non resta più in tolleranza 25 ms dopo lo scatto (lo scatto arriva quando `VRELAY_REG` o il rail − passano
la soglia: il banco `guasti` dava 6,6 ms). Il jack si apre comunque prima, come mostra la catena.

FMEA: escono 27 righe delle parti tolte (2 alte: D533 in corto, R569 aperta, entrambe «la ritenuta
cieca») e 2 dei canali tolti (basse).

## S1 — la ritenuta sostituita da fusibili

**Gli eventi sani** sono quelli di oggi a meno di qualche millisecondo (la resistenza dei fusibili):
l'accensione dà la musica a 1202 invece di 1209 ms (`confronto_s1.txt`). **Dopo un guasto di rail** il mute
e il jack sono uguali a oggi, ma K501 resta chiuso fino al frontale (oggi si apre a 129–162 ms); spento il
frontale, K501 si apre 110 ms dopo, e riacceso torna chiuso col rail ancora morto.

**La corrente nei rami del secondario** (S1+S2 dc, eventi sani, i tre valori di rete): 0,69 A efficaci al
più, 24,5 A di picco all'accensione, I²t di un'accensione **3,0 A²s**. La regola del costruttore per gli
impulsi ripetuti (~22 % dell'I²t di fusione) chiede ≥ 14 A²s: **1,6 A** (23,35) sì; 1,25 A (12,65) no.

**Il blocco audio con un rail solo, a regime** (`blocco/`, mai misurato prima: con S1 è lo stato dopo ogni
guasto di rail, finché qualcuno spegne): i deck di riferimento di L66 (il canale intero, ADR-111) con un rail
a 0 V o a ±0,6 V. Il riferimento ridà L66 (151,7 / 155,8 mA, Q106 a 78 °C con 60 °C d'aria). Con un rail
solo la giunzione più calda è a **60–75 °C con 60 °C d'aria**, contro 125 °C; nessuna resistenza sopra
0,02 W. Nessuna parte fuori.

**I guasti del lato grezzo** (38 casi della FMEA, a −10 / 0 / +10 %; `fusibili_*.csv`):

| Guasto | oggi (K501 per la ritenuta) | S1+S2, F502 / F503 da 1,6 A | S1+S2 dc, più F504 / F505 da 1 A |
|---|---|---|---|
| C501 / C502 in corto (il serbatoio) | K501 aperto | il fusibile fonde in 125–198 ms | uguale |
| un diodo del ponte in corto | K501 aperto | 107–177 ms | uguale |
| **C509 / C510 in corto (il piedino del regolatore, NC-073)** | **R550 6,1 / 7,7 / 9,4 J** in ~0,1 s | **nessun fusibile fonde**: 2,9–3,6 A nel ramo; R550 **34 / 43 / 53 W di continuo** | F504 fonde a — / 998 / 759 ms (a −10 % ~1,4 s dal modello): R550 **34–43 J**; col tempo garantito a ~3 In (0,4–10 s) **fino a ~430 J** |
| D510 / D511, D515 / D516 in corto o aperti | R550 ≤ 0,66 W | uguale | uguale |

**Il punto che decide**: la R550 antifiamma (Vishay PR02 / PR03, `parti_fusibile.md`) dichiara a 0,1 s
~3–4 / 8–10 W, cioè ~0,3–1 J, e a ~100 W si interrompe in 0,15–9 s. Oggi riceve 6–9 J (NC-073, già oltre);
**senza la ritenuta ne riceverebbe da 34 J a qualche centinaio**. La ritenuta è ciò che oggi apre il
toroidale in ~0,1 s nel corto sul piedino: i fusibili non lo sostituiscono.

**FMEA**: escono 36 righe delle parti tolte (15 alte), 9 dei canali di U515 (3 alte); 5 righe alte di parti
che restano (U513 canali A / B e la sua alimentazione, R570 e R571 in corto) sono alte solo per «la
ritenuta cieca», e senza ritenuta il loro effetto diventa il comportamento previsto. Con S1+S2 escono
circa **24 delle 47 alte**; entrano le righe dei quattro fusibili, e **C509 / C510 in corto diventano
gravità 5** (R550 oltre i suoi limiti per secondi). Il conteggio è di `script/fmea_k501.py` su
`fmea_oggi.csv` di L69; le righe nuove non sono scritte.

## Le opzioni

| | oggi | S1+S2 dc (4 fusibili) | solo S1 (4 fusibili) |
|---|---|---|---|
| parti dell'alimentatore | 189 | 169 (−24, +4 portafusibili) | 178 circa |
| buco di rete di 20 ms | musica via per 613 ms | nessun mute | 613 ms (come oggi) |
| perdita di rete al jack | −55 / 4,3 dB SPL | 17–18 dB SPL | come oggi |
| dopo un guasto di rail | toroidale spento in 129–162 ms | acceso fino al frontale, la scheda audio su un rail solo (≤ 75 °C) | uguale |
| corto sul piedino del regolatore | R550 6–9 J (NC-073) | R550 34–430 J | uguale |
| righe alte della FMEA | 47 | ~23, più quelle nuove | ~25, più quelle nuove |
| P9 (b), P9 (e) | come sono | da riscrivere | P9 (b) da riscrivere |

## Raccomandazione

**Tenere il circuito com'è.** I due guadagni sono veri (venti parti in meno, il buco di 20 ms che non si
sente più, metà delle righe alte che spariscono), ma le righe che spariscono sono già accettate, e la parte
che regge oggi un guasto reale, la ritenuta che stacca il toroidale in un decimo di secondo nel corto sul
piedino, nessun fusibile la sostituisce: R550 passerebbe da 6–9 J a decine o centinaia di joule, e la
resistenza antifiamma ne regge uno. Il buco di 20 ms (R12) resta un difetto d'uso minore; se l'utente lo
vuole togliere, la strada da misurare è un rivelatore più lento (oggi scatta a ~14,4 ms; `VRELAY` regge
50,3 ms a rete −10 %, e P9 (b) vuole 25 ms dopo lo scatto), non toglierlo.

## La decisione

L'utente, 2026-11-04: **«Tenere com'è»** (la raccomandazione), contro «Tenere, e studiare un rivelatore più
lento», «Entrambe, con 4 fusibili» e «Solo la ritenuta → fusibili». **ADR-119.** Il circuito non cambia:
niente sorgente, netlist, disegni o FMEA da rifare; NC-073 resta aperta com'è, con l'evidenza di qui.
