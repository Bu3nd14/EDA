# ADR-119 — Il rivelatore di rete e la ritenuta restano: le due semplificazioni dell'architetto misurate e non scelte

Data: 2026-11-04 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Conferma ADR-048 punto 5** (il rivelatore di rete) e **ADR-102 punto 2** (la ritenuta dopo un guasto
  di rail con la rete presente): il circuito non cambia.
- Risponde alle semplificazioni **S1** e **S2** e al rilievo **R12** dell'architetto avversariale di L65
  (`reports/2026-11-04-L65-architetto-avversariale.md`), che l'utente aveva scelto di studiare prima di G1.
- **NC-073** resta aperta com'è (R550 / R551 nel corto sul piedino del regolatore, alla scelta della
  parte): questa ADR aggiunge l'evidenza che la ritenuta è ciò che oggi limita quell'impulso a 6–9 J.
- **NC-077**, **ADR-109**, **ADR-115** (la ritenuta cieca accettata in P9 (e)) restano come sono.
- **R12** (un buco di rete di 20 ms toglie la musica per ~0,6 s) resta un difetto d'uso accettato.

## Contesto

L70 ha misurato le due semplificazioni sul banco del temporizzatore e dei guasti di L69b, copiato
(`data/2026-11-04/L70/`, report `reports/2026-11-04-L70-semplificazioni.md`), su copie del sorgente:
**S2** senza il rivelatore (178 parti invece di 189), **S1** senza la ritenuta con un fusibile per ramo del
secondario di T1 (176), le due insieme (167), e le due insieme con un fusibile per rail anche sul lato
continua (169). 310 corse a rete −10 / 0 / +10 %, la catena al jack, il blocco audio con un rail solo.

- **S2 da sola non funziona**: la ritenuta si arma «con la rete presente» grazie al rivelatore; senza,
  scatta a ogni perdita di rete e nei buchi di 60–200 ms, e l'apparecchio resta spento fino al frontale.
- **S1+S2**: il buco di 20 ms non toglie più la musica; la perdita di rete al jack 16,9–17,9 dB SPL (sotto
  i ~60 dB dell'obiettivo e i ~33 dB di PR-20); dopo un guasto di rail il toroidale resta acceso fino al
  frontale, la scheda audio su un rail solo al più a 75 °C con 60 °C d'aria (limite 125 °C); circa 24
  delle 47 righe alte della FMEA escono.
- **Ma il corto sul piedino d'ingresso di un regolatore** (C509 / C510): oggi la ritenuta apre K501 in ~0,1
  s e R550 riceve 6,1 / 7,7 / 9,4 J. Coi fusibili sul secondario (1,6 A) nessun fusibile fonde (2,9–3,6 A
  nel ramo) e R550 riceve 34–53 W di continuo; con un fusibile da 1 A anche sul lato continua R550 riceve
  34–43 J nel modello, fino a ~430 J coi tempi garantiti dal costruttore (0,4–10 s a ~3 In). La resistenza
  antifiamma proposta (Vishay PR02 / PR03) dichiara ~0,3–1 J a 0,1 s.

## Decisione

L'utente, 2026-11-04, sulla domanda coi numeri qui sopra: **«Tenere com'è»**.

1. Il circuito non cambia: il rivelatore di rete (Q504, U506 A, U513 D e le loro parti) e la ritenuta
   (Q513, Q514, U515 C / D e le loro parti) restano.
2. P9 (b), P9 (e), il PRB e la FMEA restano come sono.

## Perché

- La ritenuta protegge un guasto reale, non solo una riga della FMEA: nel corto sul piedino del regolatore
  è l'unica cosa che limita l'energia in R550 a pochi joule. Nessuna taglia di fusibile che regga le
  accensioni (I²t di un'accensione 3,0 A²s nei rami del secondario) fonde abbastanza in fretta a ~3 A.
- Le righe alte che sparirebbero sono già accettate (P9 (e), ADR-109, ADR-115): il guadagno sarebbe di
  carta, mentre la riga del corto sul piedino peggiorerebbe a gravità 5.
- Togliere il rivelatore richiede di togliere la ritenuta (sopra).
- Il buco di 20 ms è un difetto d'uso, non un colpo: al jack non arriva niente.

## Alternative scartate

- **S1+S2 con quattro fusibili** (due sul secondario da 1,6 A, due sul lato continua da 1 A): offerta coi
  numeri, non scelta.
- **Solo S1** (la ritenuta → fusibili, il rivelatore resta): offerta, non scelta.
- **Solo S2**: non offerta come opzione da sola, perché la ritenuta lascerebbe l'apparecchio spento dopo
  un buco di 60–200 ms.
- **Un rivelatore più lento** (~20–24 ms invece di 14,4, perché il buco di 20 ms non si senta, con
  `VRELAY` che a rete −10 % regge 50,3 ms contro i 25 ms dopo lo scatto di P9 (b)): offerto come lotto da
  studiare, non scelto.

## Da riaprire se

- La parte scelta per R550 / R551 (NC-073) non regge l'impulso di oggi e nessuna forma lo toglie: allora
  la ritenuta va riletta insieme ai fusibili sul lato continua.
- Il prototipo mostra buchi di rete frequenti nella casa dell'utente: allora il rivelatore più lento.
- Una revisione trova un guasto singolo della ritenuta con un effetto peggiore del toroidale acceso fino
  al frontale.
