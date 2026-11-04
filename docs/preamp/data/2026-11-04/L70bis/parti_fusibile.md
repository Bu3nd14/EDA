# L70 - dati da datasheet: fusibili secondario T1 e resistori R550/R551

Data: 2026-11-04. Solo datasheet (nessun prezzo/stock verificato presso un distributore in questa passata).
Metodo: PDF scaricati, testo estratto con pdftotext, grafici letti a occhio sul render (letture a occhio marcate "~", incertezza +-10 % sul valore, +-1 decade-div sul tempo).
Non ottenuto: Schurter FST/SPT/MST (fetch in timeout), Bel, Yageo FKN/FMP, TE ROX, Vishay CPF2 pulse (la copia trovata e' rev 08-Apr-05 e non ha sezione pulse), pagina "Pulse Load Handling" Vishay 28810.
La pagina littelfuse.com e' dietro Akamai (403): usate copie distributore/CERN, vedi rev per ogni fonte.

## A1) Littelfuse 218 (5x20 mm, T, 250 V, IEC 60127-2/3) - fonte: datasheet "218 Series", Revised BA.08/26/20, pag. 2 (Electrical Characteristics) e pag. 1 (opening time)
Copia: https://sy-dep-epc-lpc.web.cern.ch/components/datasheets/epc-lpc%20(converters)/0218080MXP_Fuse_(Littelfuse).pdf (PDF originale scaricato, 5 pag.)

| In (A) | codice | R fredda nominale (ohm) | I2t fusione nominale (A2s) | Caduta max a In (mV) | P max a 1.5 In (W) |
|---|---|---|---|---|---|
| 1 | 0218001. | 0.0613 | 6.73 | 150 | 1.6 |
| 1.25 | 0218 1.25 | 0.0446 | 12.65 | 150 | 1.6 |
| 1.6 | 021801.6 | 0.0336 | 23.35 | 150 | 1.6 |
| 2 | 0218002. | 0.0293 | 14.45 | 150 | 1.6 |
| 2.5 | 021802.5 | 0.0219 | 23.25 | 120 | 1.6 |
| 3.15 | 0218 3.15 | 0.0173 | 38.15 | 100 | 1.6 |

Condizione di prova dell'I2t: NON dichiarata nel datasheet (la colonna dice solo "Nominal Melting I2t"; la 372 invece dice "10xIn").
Anomalie PUBBLICATE (non mie): I2t(2 A)=14.45 < I2t(1.6 A)=23.35 e I2t(0.8 A)=3.37 (rev 2020) contro 1.938 nella tabella del catalogo 2006 (https://pccomponents.com/datasheets/LITT-218.PDF, pag. 417: 1 A 3.238; 1.25 A 5.648; 1.6 A 10.331; 2 A 14.412; 2.5 A 23.224; 3.15 A 38.171; R fredde 0.055/0.042/0.032/0.029/0.022/0.017). Tra le due revisioni l'I2t di 1 A, 1.25 A e 1.6 A e' circa raddoppiato/cambiato: non fidarsi del valore per 1-1.6 A senza chiedere a Littelfuse; il valore 2 A e' coerente tra le due revisioni, 2.5 e 3.15 A anche.

Tempi di apertura (pag. 1, ratings 0.125-6.3 A, valori garantiti, non curve tipiche):
| multiplo di In | tempo di apertura |
|---|---|
| 1.5 In | >= 60 min |
| 2.1 In | <= 120 s |
| 2.75 In | 600 ms min; 10 s max |
| 4 In | 150 ms min; 3 s max |
| 10 In | 20 ms min; 300 ms max |
Curve tempo-corrente medie per ogni taglia: grafico a pag. 2 (solo figura, nessuna tabella numerica).
Derating in temperatura (pag. 2, "Temperature Re-rating Curve"): ~100 % a 25 C, ~97 % a 60 C, ~92 % a 120 C (lettura a occhio). Il testo del datasheet non dice se vada applicato in aggiunta al 75 % continuo. Temperatura di esercizio dichiarata: -55..+125 C.

## A2) Littelfuse 372 (TR5 radiale, T, 250 V, IEC 60127-3) - fonte: "372 Series" Revised 03/11/15, pag. 1-2
File letto: https://static.chipdip.ru/lib/342/DOC027342729.pdf (copia distributore del datasheet Littelfuse 372, rev 03/11/15; la rev corrente su littelfuse.com non verificata)

| In (A) | codice | Caduta max a 1.0 In (mV) | Potenza max a 1.5 In (mW) | I2t di fusione a 10 In, MINIMO (A2s) | R fredda |
|---|---|---|---|---|---|
| 1.00 | 1100 | 110 | 360 | 5.5 | non pubblicata |
| 1.25 | 1125 | 95 | 450 | 9 | non pubblicata |
| 1.60 | 1160 | 95 | 450 | 14 | non pubblicata |
| 2.00 | 1200 | 85 | 600 | 23 | non pubblicata |
| 2.50 | 1250 | 80 | 700 | 35 | non pubblicata |
| 3.15 | 1315 | 80 | 1100 | 60 | non pubblicata |
(Un MINIMO, non un nominale: l'I2t reale e' piu' alto, estremo superiore non pubblicato. La R fredda si puo' solo maggiorare come caduta max / In: 1 A <=0.110 ohm, 1.25 A <=0.076, 1.6 A <=0.059, 2 A <=0.043, 2.5 A <=0.032, 3.15 A <=0.025, e' una mia derivazione, non un dato del datasheet.)
Tempi di apertura (pag. 1, tutti i ratings): 1.5 In >= 1 h; 2.1 In <= 2 min; 2.75 In 400 ms min - 10 s max; 4 In 150 ms min - 3 s max; 10 In 20 ms min - 150 ms max. Breaking capacity 35 A / 250 VAC (50 A per UL) fino a 3.15 A.
Derating (pag. 2): retta da ~120 % a -40 C a ~87 % a 85 C, ~102 % a 23 C, ~94 % a 60 C (lettura a occhio). Il 372 perde di piu' del 218 a caldo.

## A3) Schurter FST / SPT / MST, Bel 5ST/5HT
NON OTTENUTI: nessun valore riportato. Il datasheet FST 5x20 contiene (da indicizzazione dei risultati di ricerca, non verificato) colonne "voltage drop / power / melting I2t".

## B) Resistori 4.7 ohm flameproof / fusibili - fonte: Vishay PR01/02/03 (doc 28729), Revision 08-Jul-2025, https://www.vishay.com/docs/28729/pr010203.pdf
| Parametro | PR02 (Cu, 0411) | PR03 (Cu, 0617) | Pagina |
|---|---|---|---|
| P70 (R>=1 ohm) | 2 W | 3 W | 1 |
| Rth | 75 K/W | 60 K/W | 1 |
| Umax | 500 V | 750 V | 1 |
| Rivestimento | "Flameproof insulation coating meets UL 94 V-0"; prova accidental overload IEC 60115-1 12.3 superata (no fiamma); needle flame test | idem | 1, 15 |
| Fusing | "Defined fusing characteristics"; "interruzione" = R aumenta >= 100 volte | idem | 11-12 |
| Banda di interruzione, range di R | PR02 0.33-5 ohm (4.7 ohm incluso): inizia a ~55 W; a ~55 W 0.35-20 s; a ~100 W ~0.15-9 s (a occhio) | PR03 0.68-560 ohm: inizia a ~95 W; a ~100 W ~6-40 s; a ~200 W ~1-8 s | 11, 12 |
| Potenza di picco ammessa a ti = 0.1 s (grafico impulsi "on a regular basis") | ~3-4 W (curve tp/ti 2..1000); linea tratteggiata non spiegata nel testo, ~10 W | ~8-10 W (curve); tratteggiata ~20 W | 9, 10 |
| Energia a 0.1 s equivalente | ~0.3-0.4 J (tratteggiata ~1 J) | ~0.8-1 J (tratteggiata ~2 J) | derivato |

Nota: il datasheet non ha una curva "single pulse" separata: tutte le curve sono per impulsi ripetuti con rapporto tp/ti (2..1000); a ti = 0.1 s convergono tutte a ~3-4 W (PR02). La linea tratteggiata non e' identificata nel testo estraibile.
Risposta alla domanda: ~10 J in 0.1 s (= ~100 W) e' 10-30 volte oltre la capacita' di impulso dichiarata sia di PR02 sia di PR03 a 0.1 s. NON e' coperto. Il guasto da 66-102 W per 0.1 s e' invece sotto la banda minima di interruzione di PR02 (0.15-0.35 s a quella potenza): il resistore puo' non interrompersi in 0.1 s, ne' e' dichiarato che sopravviva.
Altri:
- Vishay NFR25H (fusibile, non infiammabile): P70 = 0.5 W, Rth 150 K/W, (NFR25 0.33 W) - Vishay doc 28737 (copia scaricata da https://www.vishay.com/docs/28737/nfr25.pdf, revisione non letta), pag. 1; troppo piccolo, escluso senza leggere i grafici impulsi.
- Vishay CPF2: 2 W a 70 C, "Flameproof, high temperature coating", rev 08-Apr-05 (https://pccomponents.com/datasheets/VISH-CPF.PDF): nessun dato di impulso in quella copia; non e' dichiarato fusibile.
- Yageo FKN/FMP, TE ROX, Vishay PR02/PR03 "Pulse Load Handling" (https://www.vishay.com/docs/28810/pulseloadhandling.pdf): non letti.
