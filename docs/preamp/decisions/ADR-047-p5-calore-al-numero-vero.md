# ADR-047 — P5 al numero vero: ~15–18 W nel telaio, e i 60 °C di ADR-021 reggono per stima

Data: 2026-09-26 · Stato: accettata

## Contesto

P5 (ADR-010) prevedeva ~3–4 W in mobile chiuso. Con gli otto blocchi (ADR-023) e la corrente di
riposo di ADR-042, la sola scheda audio dissipa **7,94 W** (NC-029). I 60 °C di ADR-021, su cui
poggia P7, sono «la stanza a 35 °C più ~25 °C di aumento in un telaio chiuso dentro una
libreria». NC-029 chiede una stima termica col totale, alimentatore compreso.

## Decisione

**P5 diventa: ~15 W nominali, 18 W nel caso peggiore, nel telaio, alimentatore compreso.** Con
questa cifra l'aria nel telaio resta ≤ 55 °C con la stanza a 35 °C, anche nel caso stretto. I
60 °C di ADR-021 reggono, e P7 non cambia. Le feritoie restano previste, come in ADR-010, ma non
sono necessarie ai 60 °C. È la strada 2 di NC-029.

## Perché

La stima è `data/2026-09-26/L30/termica/stima_telaio.py` (CALCOLATA).

| Voce | W (nominale / peggiore) |
|---|---|
| Scheda audio, 8 blocchi (ADR-042) | 7,94 / 7,94 |
| Regolatori ±15 V, Vin 20 / 22 V | 2,65 / 3,71 |
| Trasformatore | 2,5 / 3,5 |
| Bobine e LED (175 mA a 5 V, L35) e il loro regolatore | 1,58 / 1,75 |
| Raddrizzatore, LDR, sorvegliante, temporizzatore | 0,73 / 0,88 |
| **Totale** | **15,4 / 17,8** |

Il modello ha due salti in serie. Il telaio (Pesante 03PN, ~0,38 m² efficaci, sigillato, h da 4,5
a 6,5 W/m²K) aggiunge **7–10 °C**. Il vano chiuso della libreria (truciolare da 18 mm, U
~2,7 W/m²K) ne aggiunge:
- con 3 cm di gioco attorno al telaio: 8–10 °C → **51–55 °C** nel telaio;
- con 10 cm: 4–5 °C → 47–50 °C;
- all'aria: 42–45 °C.

Il limite di 60 °C si raggiunge solo con un vano che tocca il telaio su ogni lato.

## Alternative scartate

- **Ventilazione forzata o dissipatori esterni**: non servono ai 60 °C.
- **Riaprire ADR-021**: la stima non lo chiede.
- **R128 a 1,33 kΩ** (NC-029, 0,822 W per blocco): toglie 1,4 W, ma costa 0,5° di V1. Non serve.

## Da riaprire se

- La temperatura misurata nel telaio del prototipo supera i 60 °C (NC-029 punto 4, ADR-021).
- Nel vano c'è un'altra sorgente di calore. Il finale a valvole, per esempio, deve stare fuori.
- Il lotto dell'alimentatore sceglie un Vin dei regolatori molto sopra 22 V, o un trasformatore
  con perdite molto sopra 3,5 W.

Aggiorna **P5** (ADR-010) e conferma l'ipotesi di **ADR-021**.
