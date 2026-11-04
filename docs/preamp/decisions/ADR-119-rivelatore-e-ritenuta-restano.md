# ADR-119 — Il rivelatore di rete e la ritenuta restano: le due semplificazioni respinte coi numeri

Data: 2026-11-04 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Conferma ADR-102, punto 2** (la ritenuta dopo un guasto di rail) e **ADR-048, punto 5** (il rivelatore di
  rete): nessun cambio al sorgente, a P9 o al PRB.
- Risponde al «Da riaprire se» di ADR-102 («un guasto singolo del temporizzatore che toglie … la ritenuta»),
  che l'architetto in L65 dava per avverato con i 31 guasti latenti di ADR-115: riaperto, misurato, tenuto.
- Il buco di rete di 20 ms che toglie la musica (rilievo R12 di L65) resta, dichiarato: **NC-089**, minore.
- Dà un'evidenza nuova a **NC-073** (sotto), che resta aperta.

## Contesto

In L65 l'architetto avversariale ha proposto due semplificazioni dell'alimentatore: **S2**, togliere il
rivelatore di rete (resta il sorvegliante dei rail a 13,5 V), e **S1**, sostituire la ritenuta con un
fusibile sul secondario di T1 e R550 / R551 a film antifiamma. L'utente le ha volute studiare prima di G1.
L70 le ha misurate (`reports/2026-11-04-L70-semplificazioni.md`, `data/2026-11-04/L70/`): 150 sequenze del
banco dell'alimentatore su quattro varianti del sorgente, 25 corse del calore della scheda audio con un rail
solo, la catena al jack a tre reti, i datasheet SCHURTER FST 5×20 e Vishay PR02.

## Decisione

**Rivelatore di rete e ritenuta restano come sono.** Scelta dell'utente, 2026-11-04, fra tre opzioni coi
numeri: **«Tenere tutto»**.

## Perché

- **Il rivelatore da solo non si può togliere.** È lui a dire alla ritenuta che manca la rete e non c'è un
  guasto: senza, alla perdita di rete la ritenuta scatta, e dopo un buco di 200 ms l'apparecchio resta spento
  fino al frontale (a rete −10 / 0 / +10 %), contro P9 (b). S2 esiste solo insieme a S1.
- **Senza la ritenuta tre famiglie di guasto singolo diventano un sovraccarico senza fine**, che oggi la
  ritenuta chiude a ~125–171 ms:
  - la cella RC di un blocco in corto: U501 in limitazione a 1 A, **3,0 / 5,1 / 7,3 W, 156 / 227 / 298 °C** a
    calcolo con 60 °C d'aria (limite 125 °C, ADR-021); le due 20 Ω 0207 a 3,5 W l'una; il secondario a
    1,4 In di un fusibile T 1 A, che regge ≥ 60 min: non apre niente;
  - il piedino d'ingresso di un regolatore a massa (C509 / C510): R550 / R551 a **35 / 44 / 54 W** a regime
    (parte da 2 W): si chiude solo quando la resistenza brucia;
  - un serbatoio o un diodo del ponte in corto: 11,3–18,7 A efficaci nel secondario di T1 (1,67 A per capo)
    finché un fusibile non apre (≤ 0,3 s con un T 1 A).
  TI scrive di entrambi i regolatori che non vanno tenuti a regime in limitazione né nello spegnimento termico.
  Con un prototipo che deve funzionare al primo colpo (PR-12, ADR-118), «finisce quando una parte brucia» non
  è un comportamento da progettare.
- **Il guadagno di S1+S2 è reale ma piccolo**: il buco di 20 ms non si sentirebbe più (oggi ~0,6 s di
  silenzio), e la FMEA scenderebbe da 47 a 23 righe alte. Le righe che cadono sono però tutte accettate e
  dichiarate in P9 (e), mentre quelle che cambierebbero effetto (la cella RC, C509 / C510) sono già alte e
  diventerebbero più gravi.
- **La scheda audio con un rail solo regge** (25 corse, cinque posizioni, dissipatori di ADR-099): nessuna
  parte oltre i limiti, la Tj massima a 60 °C d'aria 75 °C contro 78 °C del mute con entrambi i rail. Vale anche
  oggi, per i guasti latenti di P9 (e), che lasciano K501 chiuso.

## L'evidenza nuova su NC-073

Il datasheet Vishay PR02 (rev. 08-Jul-2025, `vendor/resistor/vishay/PR01-PR03/`) ammette, letto dal grafico
dell'impulso, ~12 W per 100 ms. **Anche oggi, con la ritenuta**, R550 prende 6,1 / 7,7 / 9,4 J in ~0,16 s col
piedino di U501 a massa: la parte da 2 W a film antifiamma non basta a reggerlo, al più si apre senza fiamma.
NC-073 resta aperta, alla scelta della parte, con questo numero in più.

## Alternative scartate

- **Fusibili e niente rivelatore** (S1+S2): i sovraccarichi sopra.
- **Solo i fusibili** (S1): gli stessi sovraccarichi, senza il guadagno sul buco di 20 ms.
- **Solo il rivelatore tolto** (S2): non funziona (sopra).

## Da riaprire se

- La scelta della parte di R550 / R551 (NC-073) o della cella RC (NC-075) porta a parti che reggono a regime i
  sovraccarichi sopra: il costo di S1 cambierebbe.
- Il buco di rete di 20 ms che toglie la musica (NC-089) diventa un difetto d'ascolto che l'utente non accetta:
  la strada sarebbe allungare la tenuta del rivelatore, non toglierlo.
