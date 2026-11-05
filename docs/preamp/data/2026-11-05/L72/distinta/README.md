# L72 — la lista ammessa dei condensatori di segnale e le resistenze 0,1 % (2026-11-05)

Cercate da `bom-component-manager` il 2026-11-05, solo sul web. **Ogni codice d'ordine qui sotto è stato
letto su una pagina scaricata**: la pagina di DigiKey con la ricerca del codice esatto (o della famiglia),
oppure un datasheet del costruttore (copia scaricata, indicata). Mouser risponde «Access Denied» ai
programmi, TME, Farnell, RS rispondono 403, LCSC non dà risultati: **l'unico distributore verificato è
DigiKey**. Prezzi in dollari, a quella data; le scorte si muovono. «Stato (fonte)» dice dove ho letto la
riga: `DK` = pagina DigiKey scaricata; `DS` = datasheet del costruttore scaricato.

**Come leggo la condizione sulla perdita** (posizione a): «tau_IR ≥ 10 000 s × C[µF]» significa una
resistenza d'isolamento R_ins = tau / C ≥ **10 GΩ**, cioè la perdita del poliestere peggiore a 1 µF. Se
la intendeva diversamente va detto: i valori di tau del datasheet sono qui sotto, il conto si rifà.

**Sul 63 V**: tutti i pezzi sotto sono a ≥ 100 V DC (WIMA 100 V; TDK 250 V; Panasonic 450 V), tutti film di
**polipropilene** metallizzato (MKP), a foro passante, radiali. Nessun poliestere.

## Esito in breve

- **a) e e)** (1 µF ±5 %): tre costruttori, tutti compatibili. Raccomandato **TDK B32672L2105J003** (tau 30 000 s,
  1 342 pz, stesso pezzo e stessa impronta di C548/C552 di ADR-108). Alternativa piccola: Panasonic ECW-FE2W105J
  (10 320 pz) ma con tau 10 000 s: **sul limite, nessun margine**.
- **b) 6,8–10 µF**: **un solo costruttore con ±5 % e un codice letto: WIMA MKP 4.** 6,8 µF/100 V in scorta (648 pz);
  il 10 µF ±5 % è a scorta zero a 100 V (26 settimane) o a 250 V (833 pz, 19 × 32 × 41,5 mm).
- **c) e d) 4,7 µF**: **Panasonic ECW-FD2W475J** (4 362 pz) è il più piccolo (25,3 × 11,7 × 16,4 mm, passo 22,5),
  nonostante i 450 V; WIMA MKP 4 è la seconda fonte.
- **Resistenze**: **TE/Neohm YR1B** (0,1 %, ±15 ppm/K, 0,25 W, 2,3 × 6,3 mm) ha tutti e cinque i codici letti, ma a
  DigiKey **in scorta solo 1,5 k, 3,57 k, 866 Ω**; 845 Ω e 464 Ω no. Nessuna serie 0,1 % ha tutti e cinque i
  valori in scorta a DigiKey. Seconda serie: **Vishay Dale CMF55 ...BEEB** (cinque codici letti, scorta zero,
  26 settimane).

## Parte 1 — i condensatori in film di polipropilene

### Dati di serie (dai datasheet scaricati)

| Serie | Tensione DC | Tolleranza | Resistenza d'isolamento (datasheet) | Temperatura | Fonte |
|---|---|---|---|---|---|
| **WIMA MKP 4** | 100, 250, 400, 630 V… | ±20, ±10, **±5 %** | C ≤ 0,33 µF: ≥ 10^5 MΩ; **C > 0,33 µF: ≥ 30 000 s** (MΩ·µF), media 100 000 s; a +20 °C, 100 V, 1 min | −55…+105 °C; derating 1,35 %/K da 85 °C | `DS` WIMA, `e_WIMA_MKP_4.pdf`, ed. 03.26 |
| **TDK B32672L** (wound, 125 °C) | 250 V (e 450, 630…) | J = ±5 %, K = ±10 % | C > 0,33 µF: **30 000 s**; ≤ 0,33 µF: 100 GΩ; a 20 °C, umidità ≤ 65 % | −55…+125 °C | `DS` EPCOS, B32671L/B32672L, giugno 2018 (copia chipdip.ru) |
| **TDK B32674** (DC-link) | 300 V (D3), 450 V… | J = ±5 %, K = ±10 % | **tau > 10 000 s** dopo 1 min, a V_R | −40…+105 °C (custodia) | `DS` EPCOS, B32674–678, dic. 2021 (copia CERN) |
| **Panasonic ECW-FD** | 450 V (e 630 V) | J = ±5 %, K = ±10 % | C ≤ 0,33 µF: ≥ 30 000 MΩ; **C > 0,33 µF: ≥ 10 000 MΩ·µF** (20 °C, 100 V DC, 60 s) | −40…+110 °C; derating 0,62 %/°C da 85 °C | `DS` Panasonic ECWFD, 31-Jul-19 (copia chipdip.ru) e 01-Feb-16 (copia Conrad) |
| **Panasonic ECW-FE** | 450 V (e 630 V) | J = ±5 %, K = ±10 % | **≥ 10 000 MΩ·µF** per C > 0,33 µF (stesse condizioni) | vedi datasheet | `DS` Panasonic ECWFE, 31-May-19 (copia chipdip.ru) |

R_ins minima che ne viene (aritmetica mia, tau / C): WIMA e TDK B32672L a 1 µF **30 GΩ**; Panasonic a 1 µF
**10 GΩ** (esattamente il limite); a 2,2 µF WIMA 13,6 GΩ, Panasonic 4,5 GΩ (**sotto** i 10 GΩ); a 4,7 µF
Panasonic 2,1 GΩ, WIMA 6,4 GΩ; a 6,8 µF WIMA 4,4 GΩ; a 10 µF WIMA 3 GΩ. Con decine di mV ai capi la perdita è
dell'ordine dei picoampere in ogni caso; con un rail a 15 V (guasto) sono pochi nanoampere (15 V / 2 GΩ = 7,5 nA).

### a) C171–C174 / C371–C374, ingresso, 1–2,2 µF, ±5 %, tau_IR ≥ 10 000 s × C (8 pezzi)  
### e) C165 / C365, uscita fissa 2 (Stax), 1,0 µF ±5 % (2 pezzi)

Stesso elenco per entrambe: 1,0 µF ±5 % soddisfa la finestra stretta 0,895–1,265 µF (0,95–1,05 µF).
**Non esiste 1,1 µF** nelle serie lette (WIMA e Panasonic fanno 1,0 / 1,2 µF). Nota solo aritmetica: 1,2 µF ±5 %
dà 1,14–1,26 µF, che sta dentro 1,265; l'avevi escluso, lo riporto senza usarlo.

| Costruttore, serie | Codice (letto su) | Valore | V DC | Toll. | Passo | L × W × H (mm) | tau_IR minima | Stato (fonte, data) | Scorte / prezzo (DigiKey, 2026-11-05) |
|---|---|---|---|---|---|---|---|---|---|
| **TDK B32672L** | **B32672L2105J003** (`DK` + `DS`: 18,0 × 11,0 × 18,5 massimo) | 1 µF | 250 | ±5 % | 15,0 | **18,0 × 11,0 × 18,5** | **30 000 s** (30 GΩ) | Active (`DK`, 2026-11-05) | **1 342 pz**; 0,91 $ a 1, 0,283 $ a 5,1 k |
| **WIMA MKP 4** | **MKP4D041005D00JSSD** (`DK` + `DS` ed. 03.26) | 1 µF | 100 | ±5 % | 22,5 | **26,5 × 7,0 × 16,5** | 30 000 s (30 GΩ) | Active (`DK`) | **0 pz**; 760 attesi il 26-apr-2027; 26 settimane; 1,93 $ a 1, 1,297 $ a 10, 0,97 $ a 100 |
| **Panasonic ECW-FE** | **ECW-FE2W105J** (`DK`; `DS`: 17,5 × 7,0 × 12,5) | 1 µF | 450 | ±5 % | 15,0 | 17,5 × 7,0 × 12,5 (DigiKey: H 13,0) | 10 000 s (10 GΩ) **sul limite** | Active (`DK`) | **10 320 pz**; 0,96 $ a 1 |
| Panasonic ECW-FE, variante | ECW-FE2W105JA (`DK`) | 1 µF | 450 | ±5 % | 15,0 | 17,5 × 7,0 × 13,0 | come sopra | Active (`DK`) | 1 986 pz; 1,05 $ |
| **Panasonic ECW-FD** | **ECW-FD2W105J** (`DK`: solo la riga di ricerca; `DS`: 17,5 × 7,8 × 16,0, passo 15) | 1 µF | 450 | ±5 % | 15,0 | 17,5 × 7,8 × 16,0 | 10 000 s (10 GΩ) **sul limite** | stato e scorta **non letti** (la riga dà solo 1,05 $) | scorta non letta; 1,05 $ |

Il WIMA a 250 V (MKP4F041005D00…, 26,5 × 7 × 16,5, passo 22,5) c'è sul datasheet; a DigiKey ho letto solo la
versione ±20 % (MKP4F041005D00MSSD, 38 pz, rivenditore esterno) e **non** la ±5 %: non la propongo.

**2,2 µF, se serve** (finestra 1,0–2,2 µF di a): WIMA **MKP4D042205I00JSSD** (100 V, ±5 %, 26,5 × 11 × 21 mm
da datasheet, passo 22,5; `DK`: scorta 0, a 1 122 pz 1,235 $; tau 30 000 s = 13,6 GΩ: passa) oppure Panasonic
**ECW-FE2W225J** (450 V, ±5 %, passo 15, 17,5 × 10,0 × 15,5 da datasheet / 16,0 `DK`; **362 pz**, 1,38 $;
tau 10 000 s = 4,5 GΩ: **non passa** i 10 GΩ).

**Raccomandato per a) ed e)**: **TDK B32672L2105J003**, 1 µF, otto + due pezzi. Margine 3 × sulla perdita, scorta
reale, passo 15 mm (come C548/C552), 125 °C. **Il più grande dell'elenco**, per l'impronta: **WIMA
MKP4D041005D00JSSD, 26,5 × 7,0 × 16,5 mm, passo 22,5** (per area di base); il più alto è il TDK, 18,5 mm; per
volume il TDK (3,7 cm³) supera il WIMA (3,1 cm³). Se si ammette il 2,2 µF, il più grande è il WIMA 2,2 µF
**26,5 × 11 × 21, passo 22,5**.

### b) C265 / C465, C_T fra trim e volume, 6,8–10 µF (2 pezzi)

| Costruttore, serie | Codice (letto su) | Valore | V DC | Toll. | Passo | L × W × H (mm) | tau_IR minima | Stato (fonte, data) | Scorte / prezzo (DigiKey, 2026-11-05) |
|---|---|---|---|---|---|---|---|---|---|
| **WIMA MKP 4** | **MKP4D046806F00JSSD** (`DK` + `DS`) | 6,8 µF | 100 | ±5 % | 27,5 | **31,5 × 15,0 × 26,0** | 30 000 s (4,4 GΩ) | Active (`DK`) | **648 pz**; 5,83 $ a 1, 4,257 $ a 10, 3,62 $ a 50; 26 settimane |
| **WIMA MKP 4** | **MKP4D051007C00JSSD** (`DK` + `DS`) | 10 µF | 100 | ±5 % | 37,5 | 41,5 × 13 × 24 | 30 000 s (3 GΩ) | Active (`DK`) | **0 pz**; 4,41 $ a 588 (in blocco); prezzo a 1 non letto |
| **WIMA MKP 4** | MKP4D051006G00… (solo `DS`) | 10 µF | 100 | ±5 % con suffisso J | 27,5 | 31,5 × 17 × 29 | 30 000 s | **non cercato a DigiKey** | — |
| **WIMA MKP 4** | **MKP4F051007F00JSSD** (`DK` + `DS`) | 10 µF | 250 | ±5 % | 37,5 | **41,5 × 19 × 32** | 30 000 s (3 GΩ) | Active (`DK`) | **833 pz**; 8,64 $ a 1, 6,461 $ a 10, 5,59 $ a 50 |
| TDK B32674 | B32674D3685+000 (6,8 µF, 300 V, +: J = ±5 %) e B32674D3106+000 (10 µF), dal solo `DS` | 6,8 / 10 µF | 300 | J = ±5 % sul datasheet | 27,5 | 18,0 × 27,5 × 31,5 / 21,0 × 31,0 × 31,5 (w × h × l) | tau > 10 000 s | **a DigiKey il suffisso J non risponde** (B32674D3475J000 e D3106J000: nessun risultato); ho visto solo B32674D3106K000 (±10 %, 1 048 pz, 5,73 $) | **non idoneo come letto**: ±10 % |
| KEMET R76 | R76IW51004030K / R76IW51005030K (`DK`) | 10 µF | 250 | **±10 %** | 37,5 | 41,5 × 24,0 × 44,1 | ≥ 30 000 MΩ·µF (dalla ricerca, datasheet non letto) | Active, scorta 0 | **escluso**: solo ±10 % |

**Raccomandato per b)**: **WIMA MKP4D046806F00JSSD, 6,8 µF/100 V** (l'unico con ±5 %, scorta e codice letti nella finestra).
Va tutto in un solo costruttore: **non ho trovato un secondo tipo ±5 % con codice letto** a 6,8–10 µF
(TDK B32674 in J esiste solo sul datasheet; KEMET R76 solo ±10 %). **Il più grande dell'elenco**:
**MKP4F051007F00JSSD, 41,5 × 19 × 32 mm, passo 37,5** (10 µF a 250 V); con il 10 µF a 100 V: 41,5 × 13 × 24
(passo 37,5) oppure 31,5 × 17 × 29 (passo 27,5). Per 6,8 µF: 31,5 × 15 × 26, passo 27,5.

### c) C262 / C462, uscita principale, 2,2–10 µF, almeno 4,7 µF (2 pezzi)  
### d) C162 / C362, uscita fissa 1 (Singxer), 4,7–10 µF (2 pezzi)

Stessa lista (4,7 µF ±5 %); per d) 4,7–10 µF vale anche il 6,8 µF e il 10 µF di b).

| Costruttore, serie | Codice (letto su) | Valore | V DC | Toll. | Passo | L × W × H (mm) | tau_IR minima | Stato (fonte, data) | Scorte / prezzo (DigiKey, 2026-11-05) |
|---|---|---|---|---|---|---|---|---|---|
| **Panasonic ECW-FD** | **ECW-FD2W475J** (`DK` + `DS`) | 4,7 µF | 450 | ±5 % | 22,5 (diritto) | **25,3 × 11,7 × 16,4** | 10 000 s (2,1 GΩ) | Active (`DK`) | **4 362 pz**; 1,88 $ a 1 |
| Panasonic ECW-FD | ECW-FD2W475JB (`DK`: passo 15, piedini piegati) | 4,7 µF | 450 | ±5 % | 15,0 | 25,3 × 11,7 × 21,4 | come sopra | Active | 1 557 pz; 1,95 $ |
| Panasonic ECW-FD | ECW-FD2W475JC (`DK`: piedini tagliati) | 4,7 µF | 450 | ±5 % | 22,5 | 25,3 × 11,7 × 16,4 | come sopra | Active | 117 pz; 1,95 $ |
| **WIMA MKP 4** | **MKP4F044706F00JSSD** (`DK` + `DS`) | 4,7 µF | 250 | ±5 % | 27,5 | **31,5 × 15,0 × 26,0** | 30 000 s (6,4 GΩ) | Active (`DK`) | **320 pz**; 4,87 $ a 1, 3,495 $ a 10, 2,95 $ a 50; 26 settimane |
| **WIMA MKP 4** | **MKP4D044706D00JSSD** (`DK` + `DS`) | 4,7 µF | 100 | ±5 % | 27,5 | 31,5 × 13 × 24 | 30 000 s (6,4 GΩ) | Active (`DK`) | **0 pz** (lead time); 2,047 $ a 756 (in blocco) |
| KEMET R76 | R76IW4470SE30K (`DK`) | 4,7 µF | 250 | **±10 %** | 37,5 | 41,5 × 19,0 × 32,1 | — | Active, scorta 0, 20 sett. | **escluso**: ±10 % |

**Il guadagno di spazio è dalla parte dei 450 V**: il Panasonic ECW-FD a 4,7 µF è più corto e più basso del
WIMA a 100 V (25,3 × 11,7 × 16,4 contro 31,5 × 13 × 24) — controllato sul datasheet Panasonic, non solo su
DigiKey. Le «versioni a 63–100 V più piccole» **non** lo sono: per questa capacità il 100 V WIMA ha quasi lo
stesso ingombro del 250 V (13 × 24 contro 15 × 26, stessa lunghezza 31,5).

**Raccomandato per c) e d)**: **Panasonic ECW-FD2W475J** (più piccolo, scorta reale, 450 V). Seconda fonte:
WIMA MKP4F044706F00JSSD. **Il più grande dell'elenco**, 4,7 µF: **WIMA MKP4F044706F00JSSD, 31,5 × 15,0 × 26,0
mm, passo 27,5**. Se per d) si volesse 10 µF: vedi il WIMA 10 µF di b).

### Cosa dice il dielettrico

Tutti polipropilene metallizzato: nessuna dipendenza dalla tensione apprezzabile (a differenza della X7R),
tan δ dell'ordine di 1 × 10⁻³ o meno: WIMA ≤ 6 × 10⁻⁴ a 1 kHz (C ≤ 1 µF e oltre, datasheet 03.26), TDK
B32672L ≤ 0,8 × 10⁻³ a 1 kHz, Panasonic ECW-FD < 0,1 % a 1 kHz. Per e) (al 20 Hz cade il 19 % del segnale) la
cifra rilevante è l'assorbimento dielettrico: WIMA 0,05 % da datasheet; negli altri non l'ho letto.

## Parte 2 — resistenze 0,1 % a foro passante, assiali, in DIN0207

Valori: **1,50 kΩ (2), 3,57 kΩ (2), 866 Ω (2), 845 Ω (2), 464 Ω (4).** Dissipazione peggiore ~60 mW
(1,5 kΩ al rail) e ~55 mW (845 Ω): 24 % di 0,25 W; in uso normale ~10 mW.

### Serie 1 — TE Connectivity / Neohm **YR1B** (0,1 %, ±15 ppm/°C, 0,25 W, 2,3 × 6,3 mm)

| Valore | Codice | Stato (fonte, data) | Scorte / prezzo (DigiKey, 2026-11-05) |
|---|---|---|---|
| 1,50 kΩ | **YR1B1K5CC** | Active (`DK`) | **2 398 pz**; 1,02 $ a 1 (nastro tagliato) |
| 3,57 kΩ | **YR1B3K57CC** | Active (`DK`) | **3 427 pz**; 1,02 $ a 1 |
| 866 Ω | **YR1B866RCC** | Active (`DK`) | **1 453 pz**; 1,02 $ a 1 |
| 845 Ω | **YR1B845RCC** | Active (`DK`) | **non tenuto in scorta**; 23 settimane; il primo scaglione letto è 10 000 pz a 0,29069 $ (nastro e scatola); prezzo a 1 non letto |
| 464 Ω | **YR1B464RCC** | Active (`DK`) | **non tenuto in scorta**; 13 settimane; stesso scaglione da 10 000 pz a 0,29069 $ |

Corpo 2,30 × 6,30 mm (`DK`): entra nell'impronta DIN0207 con più margine del 2,5 × 6,3 di CMF55. Potenza 0,25 W,
campo −65…+155 °C, serie «YR, Neohm». **Derating a 60 °C: il datasheet TE non l'ho letto** (403/500/567 dal
sito TE); dai riassunti dei rivenditori la potenza nominale è data a 70 °C, quindi a 60 °C d'aria non c'è
riduzione, ma **è un riassunto, non il datasheet**. Il pezzo è a margine di potenza ×4 (60 mW su 250 mW).
Con 845 Ω e 464 Ω fuori scorta (6 pezzi su 12) la serie 1 intera **non** si compra a DigiKey in piccola
quantità: o si ordinano altrove (non verificato), o si usa un'altra serie per quei due valori.

### Serie 2 — Vishay Dale **CMF55** …BEEB (0,1 %, 25 ppm/K, 0,6 W a 70 °C, 2,29 × 6,10 mm)

| Valore | Codice | Stato (fonte, data) | Scorte / prezzo (DigiKey, 2026-11-05) |
|---|---|---|---|
| 1,50 kΩ | **CMF551K5000BEEB** (pagina del codice) | Active (`DK`) | non normalmente a scorta; 26 settimane; 1 000 pz a 0,8879 $ |
| 3,57 kΩ | **CMF553K5700BEEB** (riga in elenco) | Active (`DK`) | scorta 0; 1 000 pz a 0,8879 $ |
| 866 Ω | **CMF55866R00BEEB** (riga in elenco) | Active (`DK`) | scorta 0; 1 000 pz a 0,8879 $ |
| 845 Ω | **CMF55845R00BEEB** (riga in elenco) | Active (`DK`) | scorta 0; 1 000 pz a 0,8879 $ |
| 464 Ω | **CMF55464R00BEEB** (riga in elenco) | Active (`DK`) | scorta 0; 1 000 pz a 0,8879 $ |

`BEEB` = 0,1 % (B), 25 ppm (E), confezione «ammo pack da 1 000» (`DS`, Vishay documento 31018, rev. 21-feb-2025).
I codici `…BER6` e `…BERE` esistono ma sono segnati **Obsolete**: non usarli. Datasheet: CMF55 è 0,1 % a
25 ppm da 43 Ω a 1 MΩ (tutti e cinque i valori dentro); corpo massimo 2,5 × 6,5 mm, piedino 0,6 mm; **0,6 W a
70 °C** (0,4 W per una deriva di carico ≤ 0,5 % in 8 000 h); intervallo −55…+155 °C. **Derating a 60 °C: nessuno**, 60 °C
sta sotto il ginocchio di 70 °C (la curva è un'immagine, la potenza a 70 °C la dà la tabella). 60 mW sono il 10 %
di 0,6 W. Limite pratico: pacchi da 1 000 pz e 26 settimane, per 12 pezzi.

### Serie 3 (codici letti, nessuna scorta) — Stackpole **RNF14BTE** (0,1 %, 25 ppm, 0,25 W, 2,35 × 6,35 mm)

RNF14BTE1K50, RNF14BTE3K57, RNF14BTE866R, RNF14BTE845R, RNF14BTE464R: tutti letti nelle liste DigiKey, Active,
scorta 0, bobina da 5 000 pz a 0,1623 $ (464 Ω: 20 000 pz a 0,1617 $). Datasheet **non letto**: i dati (0,1 %,
25 ppm, 0,25 W) sono quelli dei campi DigiKey. Ne parlo solo come riserva: per una dozzina di pezzi non serve.

### Altre serie provate e scartate come «serie con tutti e cinque»

- **Yageo MFP-25BRD52** (0,25 W, 0,1 %, 25 ppm, 2,4 × 6,3): a scorta (1,5 kΩ: MFP-25BRD52-1K5, 13 473 pz, 0,67 $; 42
  codici nella famiglia) ma **la serie sembra E24**: MFP-25BRD52-3K57, -866R, -845R, -464R rispondono «nessun
  risultato». Il fratello a 0,5 W **MFP50SBRD52** ha 1K5, 3K57, 866R, 464R (scorta 0, 5 000 pz a 0,17733 $), ma
  l'845R non l'ho visto nella lista (troncata).
- **Vishay MBB0207VD…BC100** (0,4 W, 0,1 %, 25 ppm, 2,5 × 6,3): a scorta (1,5 kΩ: MBB0207VD1501BC100, 843 pz,
  1,95 $) ma MBB0207VD3571BC100 e MBB0207VD8660BC100 non esistono.
- **TE Holco H8** (0,1 %, 25 ppm, 0,25 W): H81K5BDA, H83K57BDA, H8866RBDA, H8845RBDA, H8464RBDA sono tutti letti
  (`DK`), nessuno a scorta (15 settimane per il 1,5 k, 3 000 pz a ~0,91 $). **Corpo 2,5 × 7,2 mm**: più lungo
  di 6,3, in 10,16 mm di passo resta poca luce. Non raccomandato.
- **Ohmite MRA0207**: MRA0207 1K5 B esiste (769 pz, 1,07 $) ma 3K57, 866R, 464R non rispondono.
- **TT/Welwyn RC55Y-1K5BI** (±15 ppm, 0,25 W, 2,5 × 7,2): 1 000 pz in un listino di rivenditore esterno; altri valori non cercati.

## Non verificato (detto per nome)

- **Mouser, TME, Farnell, RS, LCSC**: pagine non scaricabili (403, «Access Denied», timeout o nessun risultato).
  Scorte e prezzi sono **solo DigiKey**. In particolare 845 Ω e 464 Ω YR1B, e i WIMA a scorta zero, potrebbero
  esserci altrove. Nessun codice d'ordine Mouser/Farnell/RS è riportato.
- **La scorta di Panasonic ECW-FD2W105J** (letta solo la riga a 1,05 $) e il suo stato.
- **Il datasheet TE/Neohm YR1** (derating a 60 °C, curva, tensione di lavoro, rumore): non letto; la potenza a 70 °C
  e il campo −65…+155 °C vengono dai riassunti di ricerca e dai campi DigiKey.
- **Il datasheet di Stackpole RNF14** e di Yageo MFP: non letti.
- **Il tau_IR di KEMET R76**: ≥ 30 000 MΩ·µF solo dal riassunto di una ricerca; datasheet non scaricato.
- **L'assorbimento dielettrico** di TDK B32672L e Panasonic ECW-F: non letto (WIMA 0,05 % sì).
- **Le dimensioni di H del Panasonic ECW-FE**: datasheet 12,5 (1 µF) e 15,5 (2,2 µF), DigiKey 13,0 e 16,0: progettare
  col valore più grande finché non si legge il disegno.
- **Il WIMA a 250 V ±5 % da 1 µF** a DigiKey (letta solo la ±20 %).
- **La tolleranza «J» dei TDK B32674** a 4,7 / 6,8 / 10 µF: sul datasheet c'è, a DigiKey i codici J provati non esistono
  (6,8 µF J non provato).
- **I prezzi «a 1»** di WIMA 10 µF a 100 V, YR1B 845 Ω / 464 Ω, CMF55: non letti (solo scaglioni da 588, 1 000 o
  10 000 pz); il minimo d'ordine reale di questi codici non è confermato.
- **Un secondo costruttore ±5 % a 6,8–10 µF**: cercato, non trovato con codice letto (TDK solo datasheet, KEMET solo ±10 %).
  Mundorf, Jantzen, Vishay MKP1837/MKP1840, KEMET R75/PHE450, Cornell Dubilier 940C: non verificati (Vishay MKP1837,
  dalla ricerca, ha 160 V DC e valori piccoli, nessun codice 1 µF o più trovato).
- **Se il 10 GΩ** (tau_IR ≥ 10 000 s × C) vada letto come l'ho letto io: vedi l'inizio.
- **Il rumore in eccesso** delle resistenze e il coefficiente di tensione dei film: non letti.
