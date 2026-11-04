# 2026-11-04 — L70, le due semplificazioni: togliere il rivelatore di rete, la ritenuta → fusibili

**Documento datato: non si riscrive.** I dati sono in `data/2026-11-04/L70/` (README lì).

## Che cosa chiedeva il lotto

In L65 l'architetto ha proposto, e l'utente ha scelto di studiare prima di G1:

- **S2, togliere il rivelatore di rete** (Q504, R510–R512, R554, R555, C518, il canale A di U506, il canale D
  di U513, R569, D533–D535): resta il sorvegliante dei rail a 13,5 V. Toglie anche R12, il buco di rete di
  20 ms che oggi toglie la musica per ~613 ms.
- **S1, la ritenuta dopo un guasto di rail sostituita da fusibili** (Q513, Q514, R580–R585, C552–C555, D541 e
  i canali C / D di U515): un fusibile sul secondario di T1, R550 / R551 a film antifiamma. Si perde il
  toroidale che si spegne da solo dopo un guasto: resta acceso fino al frontale.

## Come si è misurato

Il banco dell'alimentatore di L69b copiato, su quattro varianti di `psu.py` ottenute per sostituzione di testo
(`oggi` ridà il netlist di oggi). **150 sequenze** (i 32 eventi sani × 3 varianti; i corti lato grezzo e la
cella RC su `oggi` e `s1`), **25 corse del calore** della scheda audio con un rail solo, **3 catene al jack**
(S1+S2). Tutte rc 0, nessun ripiego. Il fusibile non è modellato: la sua apertura si giudica dalla corrente,
contro il datasheet **SCHURTER FST 5×20** (ritardato, 21.07.2026: prearco a 10 In 20–300 ms, a 4 In 150 ms–3 s,
a 2,75 In 600 ms–10 s, a 2,1 In ≤ 120 s, a 1,5 In ≥ 60 min; I²t di fusione a 10 In 1 A 3,3, 1,6 A 10,5 A²s). La
resistenza antifiamma: **Vishay PR02** (2 W a 70 °C, punto caldo ≤ 220 °C, UL 94 V-0, rev. 08-Jul-2025; il
grafico dell'impulso letto a vista: ~12 W per 100 ms, ~9 W per 1 s). Littelfuse ha rifiutato il download.

## Due cose trovate leggendo il sorgente, poi misurate

1. **S2 da sola non sta in piedi.** Oggi è il rivelatore a dire alla ritenuta «manca la rete, non è un
   guasto» (D534 svuota AT_F, D535 disarma AT_T2S). Senza, alla perdita di rete la ritenuta **scatta**
   (`ritenuta = 1` in tutte le perdite di S2), e **dopo un buco di 200 ms la musica non torna**: K501 aperto,
   l'apparecchio resta spento finché non si gira il frontale (S2, `buco200` a −10 / 0 / +10 %). È contro P9 (b)
   («dopo un buco di rete che i rail hanno retto il mute si rilascia con la sequenza normale»). **S2 si può
   fare solo insieme a S1.**
2. **T1 ha la presa centrale e il ponte**: un fusibile «per rail» sul secondario non esiste; ogni capo del
   secondario porta i due rail a semionde alterne. Un fusibile in serie a R550 / R551 (posizione B) sarebbe
   per rail, ma **non vede** i corti dei serbatoi e del ponte, che stanno a monte.

## S2 (con S1): che cosa cambia

| Evento | Oggi (L69b) | Senza rivelatore (S1+S2) |
|---|---|---|
| Buco di rete di 20 ms | la musica tolta, torna dopo 613 ms | **la musica non si interrompe** (a −10 / 0 / +10 %) |
| Buco di 200 ms | torna dopo 682 ms | torna dopo 682 ms, uguale |
| Perdita di rete / spegnimento dal posteriore: relè del jack aperti dopo | 17,4 ms | **55 / 82 / 110 ms** (rete −10 / 0 / +10 %), quando un rail scende a 13,5 V |
| Perdita di rete: picco al jack principale | 3,7 nV (−55 dB SPL) | **15–17 µV: 16,9 / 17,3 / 17,7 dB SPL** (+10 / 0 / −10 %; `perdita_min` 17,1–17,9) |
| Guasti di rail, U503, spegnimento dal frontale | — | uguali a oggi alla cifra |

Il colpo alla perdita di rete passa da −55 a ~18 dB SPL: sotto i 33 dB SPL di una stanza silenziosa, e
sotto l'obiettivo di P9 (b), 2 mV (~60 dB SPL), di 42 dB. **Il PRB non cambia** (PR-23: le uscite si staccano
prima che il circuito esca di regolazione); P9 (b) perde «o quando mancano le semionde della rete».

## S1: che cosa cambia

**Gli eventi sani** sono uguali a oggi. Dopo un guasto di rail **K501 resta chiuso** (`guasto`,
`guasto_u501`, `accensione_u501`), il jack muto come oggi.

**La scheda audio con un rail solo, a tempo indefinito** (oggi dura ~129 ms): nessuna parte oltre i suoi
limiti in nessuna delle cinque posizioni; la Tj massima a 60 °C d'aria è 75 °C, contro i 78 °C dello stato
di mute con entrambi i rail. Il caso realistico è il rail «aperto» (D515 / D516 in serie non lasciano che il
rail morto assorba corrente): 0,1–27 mA dal rail vivo.

**I corti lato grezzo**, a rete −10 / 0 / +10 %:

| Guasto | Oggi (con la ritenuta) | Senza ritenuta |
|---|---|---|
| Serbatoio C501 / C502 o un diodo del ponte in corto | K501 aperto a 129–171 ms; 21–57 A²s nel secondario | **11,3–18,7 A efficaci** nel secondario, per sempre (T1: 1,67 A per capo). Un fusibile T 1 A sul secondario apre: 11–19 In, ≤ 300 ms (un 1,6 A: 7–12 In, ≤ 3 s) |
| Piedino di U501 / U502 a massa (C509 / C510) | K501 a 129–162 ms; R550 66 / 83 / 102 W di picco, **6,1 / 7,7 / 9,4 J** | R550 **35 / 44 / 54 W a regime**; il secondario solo 3,0–3,7 A: un T 1 A apre in ≤ 10 s, un 1,6 A forse mai. **R550 brucia prima**: è lei il fusibile |
| La cella RC di un blocco in corto (10 Ω sul rail +) | K501 a 125–131 ms; R550 0,6–0,8 J | **niente si apre**: U501 in limitazione a 1 A, **3,0 / 5,1 / 7,3 W, 156 / 227 / 298 °C** a calcolo (limite 125 °C, ADR-021; lo spegnimento termico del TPS7A47 a ciclo); R550 4,7 W; le due 20 Ω 0207 **3,5 W l'una**; il secondario 1,37–1,42 A = 1,4 In di un T 1 A, che regge ≥ 60 min |

TI scrive di entrambi i regolatori che non sono fatti per stare in limitazione a regime (TPS7A47, 6.3.1;
TPS7A33, 7.3.1, «continuously running into thermal shutdown degrades device reliability»). **Con S1 tre
famiglie di guasto singolo che oggi finiscono a ~130 ms diventano un sovraccarico che finisce solo quando una
parte brucia**: R550 / R551 (che a film antifiamma si aprono senza fiamma: è il loro scopo) e le resistenze
della cella. È la questione di NC-073 e NC-075, che oggi la ritenuta tiene a 4,7–9,4 J e che senza diventa
«quale parte si apre per prima».

Nota su NC-073 vista da qui: **anche oggi** R550 prende 6,1–9,4 J in ~0,16 s, contro i ~1,2 J per 100 ms
che il PR02 ammette a lettura del grafico. Con la ritenuta R550 è già sovraccaricata in quel guasto; il
datasheet scelto lo conferma, non lo risolve.

**Il fusibile sul secondario in uso normale**: 0,69 / 0,70 A efficaci per capo (rete nominale / +10 %), cioè
il 70 % di un T 1 A, il 44 % di un 1,6 A; all'accensione 16,4 A di picco e 1,0 A²s nei primi 100 ms, contro
3,3 A²s (1 A) e 10,5 A²s (1,6 A) di fusione. Il datasheet non dà un declassamento in temperatura (solo
−55…125 °C d'ambiente ammesso).

## La FMEA

`fmea_l70_conti.csv`, sulla FMEA di oggi (692 righe, 47 alte), **prima** delle righe nuove dei fusibili:

| Variante | Righe | Alte | Come |
|---|---|---|---|
| oggi | 692 | 47 | — |
| solo il rivelatore tolto | 661 | 45 | D533 in corto, R569 aperto escono con le parti (ma la variante non funziona, sopra) |
| solo i fusibili | 652 | **23** | 17 escono con la ritenuta, 7 scendono (il loro effetto, «K501 resta chiuso», diventa il progetto); restano alte U514 D, U515 B, U514 senza alimentazione, R574, R578 (anche altri effetti) |
| entrambe | 627 | **23** | come sopra, con D533 e R569 tolti invece che scesi |

L'architetto stimava ~25. Con S1 entrerebbero però le righe dei fusibili, e le tre famiglie della tabella
sopra cambierebbero effetto (da «K501 a 130 ms» a «una parte brucia»): C509 / C510 / C145 sono già alte oggi,
e resterebbero alte con una gravità più seria.

## Le opzioni portate all'utente

1. **Tenere tutto com'è** (rivelatore e ritenuta). Il buco di 20 ms toglie la musica per ~0,6 s (R12, minore).
2. **Togliere solo il rivelatore**: non funziona da sola (l'apparecchio resta spento dopo un buco di 200 ms).
3. **Solo i fusibili**: −24 righe alte; il prezzo è la tabella dei corti sopra.
4. **Entrambe**: in più il buco di 20 ms non si sente e il colpo alla perdita di rete sale a ~18 dB SPL.

La scelta dell'utente e le sue conseguenze sono nella sezione che segue (aggiunta alla risposta).

## La scelta dell'utente

Domanda posta con le tre opzioni reali (la quarta, il solo rivelatore tolto, detta come non funzionante), i
colpi al jack in dB SPL e le temperature contro i limiti a rete −10 / 0 / +10 %. Risposta: **«Tenere tutto»**
(l'opzione consigliata).

- **ADR-119**: rivelatore di rete e ritenuta restano; il sorgente, P9 e il PRB non cambiano.
- **NC-089**, minore, aperta: il buco di rete di 20 ms che toglie la musica per ~0,6 s, dichiarato.
- **NC-073** avanza: il numero del PR02 contro i 6,1–9,4 J di oggi.
- La FMEA non cambia (692 righe, 47 alte): `fmea_l70.csv` resta come studio.
