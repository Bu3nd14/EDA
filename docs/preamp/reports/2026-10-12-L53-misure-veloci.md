# 2026-10-12 — L53, le misure veloci prima di G1

**Documento datato: non si riscrive.** Le voci vivono in `../NONCOMPLIANCE.md`. Dati e comandi in
`../data/2026-10-12/L53/` (README). Cifre di modello: ngspice 47, i modelli di `models/`, il blocco
di `main` dopo L52. Nessuna modifica al circuito, al firmware, ai deck versionati o al dossier.

## Perché

In L52 l'utente ha chiesto, mentre legge il dossier in parallelo: «please run remedies, FMEA, and
all what is needed before G1 in the meantime». L'ordine l'ho scelto io: prima le misure veloci,
perché possono cambiare i lotti grandi. Questo lotto ha misurato NC-055 (la distorsione contro
l'impedenza di sorgente e sulla catena), NC-058 (V1 e V4 a 57 °C) e NC-059 (l'RCA a caldo). Le
cifre dell'architetto di L52 erano calcoli: qui sono misurate per la prima volta.

## Il risultato che conta: lo specchio d'ingresso e il calore (NC-060, nuova)

Misurando NC-058, a 57 °C uniformi la THD a 20 kHz del blocco cresceva 4–10 volte, fuori da V4 in
ogni modo, con lo spettro ancora a h2 dominante e indipendente dalla sorgente: qualcosa dentro
l'anello. La sequenza:

1. **Il punto di lavoro** cambia poco (`temp/op_temp.cir`): coda 4,51 → 4,39 mA, VAS 10,7 → 10,4 mA,
   finali 20,5 → 21,7 mA; la classe A regge.
2. **La sonda per gruppi** (`temp/sonda.py`, il parametro d'istanza `temp=27` su un gruppo alla
   volta, verificato che arriva): tenuto a 27 °C il solo **Q106, il generatore di coda**, la THD a
   57 °C torna 0,00059 % (era 0,00211); tenuti a 27 °C i suoi diodi di riferimento, 0,0090 %. La
   quasi-saturazione del modello MMBT5551 non c'entra (`QUASIMOD=0`, uguale). Il modello del
   LSK489 non ha dipendenza della corrente dalla temperatura in questo circuito (la coda la fissa).
3. **La corrente di coda** (`temp/coda.py`, R107 ±10 %): non un annullamento ma **un gradino**. A
   27 °C la THD è piatta (0,00053–0,00057 %) sotto ~4,6 mA, poi 0,0012 % a 4,73 mA e 0,011 % a
   4,98 mA. Il punto di lavoro, 4,51 mA, sta il 2–4 % sotto il gradino; a 57 °C il gradino scende a
   ~4,2 mA e il punto di lavoro cade oltre.
4. **Le giunzioni** (`temp/giunzioni.py`): lo specchio d'ingresso, Q121B (LS350), ha 0,79 V fra i
   morsetti e il modello del costruttore ha **RC 231 Ω**: a 2,16 mA perde ~0,5 V dentro il
   transistor, e la giunzione base-collettore interna è a ~+0,42 V, sull'orlo della saturazione. La
   tensione dello specchio la fissa la Vbe del VAS: più calore, meno Vbe, meno margine.
5. **Il calore che SPICE non simula** (`temp/autoriscaldamento.py`, limitations #55): Tj = Ta +
   P·R_thJA coi datasheet in `vendor/` (MMBT5401 403 / 357 °C/W, MMBT5551 417, LS350 233 sulla
   coppia, LSK489 250 sulla coppia, MJE in TO-220 62,5). Il VAS a 141,7 mW sale a **77,6–84,1 °C**
   con l'aria a 27, il suo carico a 86,2, la coda a 53,7 (`tj.csv`). Con ogni giunzione alla sua
   temperatura, **48 casi su 48 fuori dai tetti di V4 a 20 kHz**:

| Aria | THD 20 kHz a 0,2 V (tetto 0,001 %) | a 2 V (tetto 0,01 %) |
|---|---|---|
| 27 °C, VAS su 15 × 15 mm di rame | 0,0024 % (0 dB) … 0,0074 % (+10 dB) | 0,035 … 0,11 % |
| 27 °C, piazzola minima | 0,0039 … 0,012 % | 0,053 … 0,17 % |
| 57 °C, rame | 0,020 … 0,060 % | 0,21 … 0,64 % |
| 57 °C, piazzola minima | 0,025 … 0,078 % | 0,26 … 0,79 % |

6. **La prova del meccanismo**: le stesse temperature con l'RC dell'LS350 quasi a zero (copia di
   prova): **24 casi su 24 dentro**, anche a 57 °C d'aria, margine 1,6–5,4 dB.
7. **Lo spettro resta benigno**: h2 −92,4 dB, h3 −121, h4 −153, h5 −189 (27 °C d'aria, 0,2 V). Cresce
   la seconda armonica.
8. **L'intermodulazione** CCIF, il prodotto a 1 kHz a 0,2 V (tetto −110 dB): da −130,8 / −130,7 /
   −125,6 dB (L51c) a **−92,9 / −89,8 / −82,8 dB** a 27 °C d'aria e **−74,6 / −71,5 / −64,5 dB** a
   57 °C (0 / +3 / +10 dB). In dB SPL: a 0,2 V (~99 dB SPL a 1 m) il prodotto cade a ~6–16 dB SPL a
   27 °C e **25–35 dB SPL** a 57 °C, il livello di una stanza silenziosa, col test a due toni a
   piena scala.
9. **V1 regge** (`v1/`), ma a 57 °C d'aria il guadagno d'anello a 10 Hz scende da 78,7 a
   69,8 / 67,7 dB: lo specchio in saturazione si mangia ~10 dB d'anello.

**Che cosa non so**: la RC dell'LS350 vera (il datasheet dà solo VCE(sat) ≤ 0,5 V a 1 mA, che la
ammette), la R_thJA vera sul rame della scheda, la temperatura vera del VAS. Sono cifre di modello e
di datasheet; il prototipo le dirà. Ma il margine è il 2–4 % di corrente di coda già a 27 °C
uniformi, prima di ogni calore e di ogni tolleranza.

**Decisione dell'utente**: **NC-060, bloccante per G1** («Blocking for G1»).

## NC-055 — la distorsione contro la sorgente e sulla catena (a 27 °C)

- **La prova dell'architetto** (`rs/`): la THD cresce con la sorgente **senza minimo** a R_F 1,5 kΩ
  (scansione 1–2 kΩ monotona): il meccanismo di R5 nella sua forma non c'è. A 0 dB, 20 kHz, 0,2 V:
  0,000326 / 0,000446 / 0,000526 / 0,000772 % a 0 / 1,5 / 2,5 / 5,6 kΩ.
- **La sorgente peggiore** (5,6 kΩ): dentro V4 in tutti i modi, margine minimo **2,1 dB**.
- **La catena** (`catena/`, quattro istanze, carico di V4): **53 su 56 dentro**; fuori il principale
  col volume a metà, 0 e +3 dB, 20 kHz, 0,2 V (0,0010–0,0016 %): A a 0,4 V e B con ~2,5 kΩ di
  sorgente sommano la seconda armonica. **La prima corsa l'ho scartata**: misuravo al jack, dopo il
  4,7 µF, e il suo transitorio di carica cadeva nel periodo della fourier (a 1 kHz armoniche finte a
  −96 dB). La seconda misura alle uscite dei blocchi, come il banco di V4; a 1 kHz resta un
  pavimento del metodo di ~−110 dB sulle armoniche alte (C_IN e C_T a monte, calcolo in
  `catena/script/genera.py`). Saltati i casi che chiedono al blocco A più di 2,7 V.

**Decisione dell'utente**: «Keep open, re-verify after fix».

## NC-058 — V1 e V4 a 57 °C

V1: il controllo ridà 64,42° di L48b; 64,02° a 57 °C uniformi; 63,72° / 66,40° / 67,55° con ogni
giunzione alla sua temperatura. V4: fuori, per NC-060. **Decisione dell'utente**: «Close, distortion
in new entry».

## NC-059 — l'RCA a caldo

Ipotesi in `rca/genera.py` (polo caldo 10 ms prima della massa; sorgente a terra con 10 mV e
0,65 V; sorgente in classe II con la massa a metà rete attraverso 1 nF e 3,46 nF). Al jack
principale, dB SPL di picco a 1 m con la catena di NC-028:

| Caso | Volume in cima | Posizione del K11 (−29 dB) |
|---|---|---|
| a terra, 10 mV | 74–83 dB SPL | 45–54 dB SPL |
| a terra, 0,65 V | 110 dB SPL; clip del finale a +10 dB | 81–91 dB SPL |
| classe II, 1 e 3,46 nF | **clip del finale, ~113,8 dB SPL** | 107 dB SPL a 0 dB; clip a +10 dB |

Il clip del finale sta sopra il tetto di non-danno di PR-23 (112,2 dB SPL). Le fisse prendono
**+10,9 dB** sul picco del K11 a piena scala. Il gate-gate dell'LSK489 del blocco A arriva a
**−28,1 V** contro ±30 V minimo (`rca/out_gate/gate.csv`): 1,9 V di margine. I picchi di 29–39 mA
nella corrente di gate sono lo spostamento capacitivo del fronte del contatto, risolto a 10 µs: non
mostrano conduzione della giunzione e non li uso.

**Decisione dell'utente**: «Remedy in circuit, major».

## Trappole nuove

- **limitations #55**: SPICE non scalda i dispositivi; `temp=` d'istanza con Tj = Ta + P·R_thJA.
- **limitations #56**: `.model LS350 (PNP …` dà «model type mismatch» a ogni istanza, e i parametri
  arrivano lo stesso.

## Le voci

| Voce | Prima | Dopo |
|---|---|---|
| NC-055 | aperta, maggiore | aperta, da rifare dopo NC-060 |
| NC-058 | aperta, minore | **chiusa** |
| NC-059 | aperta, minore | aperta, **maggiore**, rimedio nel circuito |
| NC-060 | — | **aperta, bloccante per G1** |

18 voci aperte, 2 bloccanti (NC-060 per G1, NC-044 per G2).

## Il lotto dopo

Proposta mia, l'utente non ha fissato l'ordine: **L56 lo specchio d'ingresso** (NC-060, poi NC-055
rifatta), perché è bloccante e ogni altra cifra di distorsione ne dipende; poi L45 la FMEA, L57
l'ingresso protetto per l'RCA a caldo (NC-059, dopo la FMEA che può portare un rivelatore e il
mute), L54 il micro e lo standby, L55 il dispositivo d'uscita (tocca anche il VAS: va dopo L56),
poi G1.
