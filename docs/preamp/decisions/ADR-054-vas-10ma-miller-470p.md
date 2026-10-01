# ADR-054 — Il VAS a ~10,7 mA e il Miller a 470 pF

Data: 2026-10-01 · Stato: accettata — la continua d'uscita del blocco è −6,6 mV con R120 226 Ω, non −26 (ADR-056)

## Contesto

ADR-042 portò il Miller C124 da 470 pF a 1 nF per tenere V1 ≥ 60° coi modelli del costruttore,
la cui CJE da 3,06 nF dei MJE15032/33 abbassa il polo non dominante. L43a (NC-039) ha mostrato
il prezzo che ADR-042 non aveva misurato: la distorsione cresce verso gli acuti, e il PSRR del
rail + perde ~6,5 dB (NC-047). L46a ha misurato 25 varianti sullo stesso banco (report
`reports/2026-10-01-L46a-compensazione.md`, dati `data/2026-10-01/L46a/`): solo Miller, un
driver, il VAS più veloce, dispositivi d'uscita più veloci (ZXTN/ZXTP25040DZ), e le combinazioni.

## Decisione

**R123 e R126 passano da 91 a 56 Ω (VAS da 6,8 a ~10,7 mA), R128 da 1,69k a 1,58k (corrente
d'uscita ~20,5 mA come prima), C124 da 1 nF a 470 pF, C0G**, in tutte le otto istanze. Nessuna
parte nuova. Decisione dell'utente del 2026-10-01 (opzione A), con la tabella delle tre finaliste.

## Perché

**La leva è la corrente del VAS.** Il nodo del VAS carica la capacità dei MJE; a 6,8 mA non ce la
fa. A parità di Miller (1 nF) il VAS a 10,7 mA dimezza la THD a 20 kHz e compra 7° di V1; il
driver o i ZXT da soli comprano margine ma **non** distorsione (0,0029–0,0030 % contro 0,0017 %).

Al livello musicale deciso dall'utente (−20 dB, 0,2 V RMS, ~99 dB SPL a 1 m), peggiore sui tre modi
del blocco B; V1 col criterio di ADR-024:

| | 1 nF (ADR-042) | **VAS 10,7 mA, 470 pF** |
|---|---|---|
| V1 minimo / gruppo B di I_DSS | 62,08 / 62,19° | **64,94 / 65,13°** |
| PSRR+ a 10 / 20 kHz, +10 dB | 23,0 / 17,1 dB | **29,5 / 23,5 dB** |
| THD 1 / 20 kHz | 0,000044 / 0,0017 % | 0,000032 / **0,00059 %** |
| IMD CCIF (prodotto a 1 kHz) | −96,3 dB (~−3 dB SPL) | **−119,2 dB (~−26 dB SPL)** |
| armoniche dalla 5ª | −164 dB | −185 dB |
| THD 20 kHz a 2 V RMS (stress) | 0,17 % | **0,0070 %** |
| slew in discesa | −1,68 V/µs | −3,80 V/µs |
| E5 peggiore | 4,270 µV | 4,315 µV |

Regge le soglie di V4 fissate da ADR-055; il blocco di ADR-042 no.

**Il prezzo, dichiarato e accettato.**
- **+4,1 mA per rail per blocco** (36,7 / 37,7 mA), **~+1,0 W** a riposo sugli otto blocchi,
  +33 mA per rail sui regolatori (ADR-048): pesa sul bilancio termico (NC-029) e sull'alimentatore.
- Q122 (VAS) 0,142 W e Q125 (pozzo) 0,122 W, contro 310 mW di P7.
- La continua all'uscita del blocco da −15 a **−26 mV** (corrente di base del VAS): il blocco B la
  ferma col condensatore d'uscita, il **blocco A** la porta su trim e volume (NC-041, L48).
- Nel modello del costruttore il moltiplicatore di Vbe (Q127, 9,7 mA) lavora in
  quasi-saturazione (`QUASIMOD`, giunzione base-collettore interna +0,42 V): la corrente tarata
  regge e le cifre lo comprendono.

## Alternative scartate

- **VAS + ZXTN/ZXTP25040DZ, 220 pF** (opzione B): PSRR+ 36,0 dB, IMD −128,5 dB, V1 64,96°, senza
  parti in più. Scartata dall'utente: il PNP non ha disponibilità confermata, il SOT-89 arriva a
  ~100 °C di giunzione a 60 °C ambiente sul pad minimo, e l'analisi termica di ADR-021 va rifatta.
  I modelli restano in `models/` con la loro ricetta (L46a).
- **VAS + driver, 330 pF** (opzione C): V1 69,98°, PSRR+ 32,6 dB; 24 parti nuove e ~2,4 W in più.
- **Solo Miller** (820p / 680p): sotto o appena sopra 60°, e la distorsione resta quella di oggi.
- **Driver o ZXT senza VAS**: margine sì, distorsione no (sopra).
- **VAS con 390 / 330 pF**: 62,83 / 60,30°, troppo vicini a ADR-019 per 1,6 / 3,1 dB di PSRR+.
- **Compensazione a due poli**: non misurata; il piano la teneva per il caso in cui le altre non
  reggessero i 60°.

## Da riaprire se

- **L46b** non trova un rimedio del PSRR+ nel blocco o nell'alimentatore che stia nella quota di
  ADR-020 con 29,5 dB a 10 kHz: allora l'opzione B (220 pF, +6,5 dB) torna in discussione.
- La continua di −26 mV del blocco A non regge quanto L48 decide per trim e volume.
- Il bilancio termico del telaio o la corrente dei regolatori non reggono +1 W / +33 mA.
- Sul prototipo la f_T dei MJE è molto sopra il modello (NC-025): il margine sale, e il Miller
  si può rispazzare verso il basso con `data/2026-10-01/L46a/script/`.
