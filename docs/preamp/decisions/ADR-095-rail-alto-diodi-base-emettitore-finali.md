# ADR-095 — Il rail alto e la base dei finali: un 1N4148 in antiparallelo sulla base-emettitore di ciascun finale, nessun sorvegliante della sovratensione, i vincoli di distinta di oggi

Data: 2026-10-21 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- Risponde al punto 1 di **ADR-078** («prima leggere i massimi»): il suo «Da riaprire se» è scattato,
  perché col rail alto P7 usciva sulle resistenze d'uscita, e la scelta è tornata all'utente.
- Il sorvegliante della sovratensione che ADR-078 teneva di riserva **non si aggiunge**.
- I vincoli di distinta delle resistenze d'uscita restano quelli di **ADR-087**: 22 Ω ≥ 0,34 W e 47 Ω
  della principale ≥ 1,3 W a 60 °C.
- Il diodo è lo stesso 1N4148 di **ADR-090**, nelle stesse otto istanze del blocco.
- P7 è quello di **ADR-021**.

## Contesto

Dal banco di L45d2b2c (`data/2026-10-21/L45d2b2c/`, README).

- **Il rail alto di oggi.** I modi che alzano un rail sono quelli di L45c1, rifatti sul circuito di
  oggi (R550 / R551, il regolatore a 15,3 V sul piedino, lo Schottky in serie dopo) alle tre reti. Il
  peggiore è il regolatore in corto fra ingresso e uscita: **+20,05 / −19,97 V a rete +10 %**,
  +18,1 / −18,1 V a rete nominale, +16,2 / −16,2 V a −10 %. Il banco ridà i 20,33 V di L45c1 sul suo
  deck. Il firmware non lo vede e il jack resta collegato.
- **Le tensioni delle parti del blocco stanno tutte dentro**, anche con tutti e due i rail a ±20,3 V
  (272 massimi, 0 fuori; i limiti dai datasheet in `limiti_blocco.csv`):
  - LSK489: 12,7 V fra drain e source, nessuna giunzione di gate oltre i 60 V;
  - C145: 20,1 V contro 25 V; collettori ≤ 40 V contro 60–250 V;
  - a blocco fermo nessuna base-emettitore in inversa.
- **Il calore dei finali col rail alto sta dentro**:
  - 85,5 °C a riposo con 60 °C d'aria;
  - 112,9 °C sommando un guasto del moltiplicatore (doppio guasto);
  - in P7 al più 101 °C.
- **In P7 col rail alto escono le resistenze d'uscita.** Mute inserito o uscita in corto, musica a
  fondo scala, alle tre reti col rail misurato:
  - la 22 Ω del PNP 0,358 / 0,391 / 0,401 W contro 0,34 W;
  - la 22 Ω dell'NPN fino a 0,360 W;
  - la 47 Ω della principale 1,35 / 1,44 / 1,47 W contro 1,3 W.
- **E già a ±15 V, senza guasti, P7 esce sulla base del finale NPN.** Nella cella più dura (principale
  a +10 dB, 20 kHz a fondo scala, mute inserito o uscita in corto) la base di Q132 spento sale
  **5,18 V** sopra il suo emettitore, mentre Q133 porta la corrente del corto. Il MJE15032 ammette 5 V
  (onsemi MJE15032/D Rev 7); a 1 kHz sono 4,97 V. Nessun lotto lo aveva misurato: P7 leggeva potenze
  e correnti, non le giunzioni.

## Decisione

Parole dell'utente (2026-10-21): «Resistenze più robuste» e «Rimedio in questo lotto»; poi, visti i
numeri del rimedio, «Vincoli di oggi».

1. **Un 1N4148 in antiparallelo sulla base-emettitore di ciascun finale**, in tutte le otto istanze:
   - D158 da NEN a NBN (Q132: conduce solo quando l'emettitore sale sopra la base);
   - D159 da NBP a NEP (Q133: conduce solo quando la base sale sopra l'emettitore).
   A riposo e con la musica sono in inversa di una Vbe e non conducono.
2. **Nessun sorvegliante della sovratensione** (ADR-078).
3. **I vincoli di distinta restano quelli di ADR-087**: 22 Ω ≥ 0,34 W e 47 Ω della principale
   ≥ 1,3 W a 60 °C. Le resistenze più robuste scelte prima del rimedio non servono più.

## Perché

| P7, il peggiore sulle celle | Senza i diodi | **Coi diodi** |
|---|---|---|
| base-emettitore in inversa, NPN / PNP, a ±15 V | **5,18** / 3,27 V | **0,77 / 0,82 V** |
| idem, col rail alto (fino a ±20,3 V) | fino a 5,57 / 4,40 V | ≤ 0,77 / 0,84 V |
| 22 Ω, rail alto alle tre reti | fino a **0,401 W** (> 0,34) | ≤ 0,181 W |
| 47 Ω principale, rail alto alle tre reti | fino a **1,47 W** (> 1,3) | ≤ 0,78 W |
| 22 Ω / 47 Ω a ±15 V | 0,332 / 1,282 W | 0,158 / 0,683 W |
| finale PNP a ±15 V, 60 °C d'aria | 82,7 °C | **92,7 °C** |
| finale PNP, rail − alto a rete +10 % | 100,9 °C | **109,8 °C** (< 125) |
| i diodi | — | ≤ 29 mA di picco, ≤ 5 mW (1N4148: 300 mA, 440 mW) |

- **Il diodo fa anche da limite di corrente.** Con la base del finale spento agganciata al suo
  emettitore, la tensione del moltiplicatore fra le due basi fissa la corrente massima dell'altro
  finale a (spread + 0,77 − Vbe) / 22 Ω, circa 0,11 A sul lato PNP (era 0,214 A). Nel corto la
  corrente cala e le resistenze si raffreddano; il PNP lavora a corrente limitata con più tensione
  ai capi, e si scalda di più.
- **In uso normale il limite non interviene**: le correnti del blocco sono al più ~10 mA (la
  retroazione, la scala del trim, i carichi da 10 kΩ in su), contro ~110 mA. Lo conferma la
  regressione dei 21 deck veloci (report).
- **Il rail alto si chiude senza parti nell'alimentatore.** Un sorvegliante avrebbe portato un
  comparatore per rail, i suoi modi di guasto e una modifica al firmware.

## Alternative scartate

- **Resistenze più robuste senza i diodi**: 22 Ω ≥ 0,45 W, 47 Ω ≥ 1,6 W su un'assiale da 2 W. Era la
  prima scelta per il rail alto; coi diodi le resistenze di oggi bastano con margine (53 % e 60 %).
- **Il sorvegliante della sovratensione**: sopra.
- **Il rail alto accettato come non conformità**: un regolatore in corto e il mute inserito sono un
  guasto singolo in una condizione normale.
- **Un finale con una base-emettitore più robusta**: non cercato. Il diodo costa una parte da pochi
  centesimi e lascia il dispositivo d'uscita alla sua non conformità (NC-056).

## Da riaprire se

- Il finale PNP supera i 125 °C in un caso che questo lotto non ha corso, oggi al più 109,8 °C col
  rail alto. Il limite di corrente lo scalda di più dove prima scaldava le resistenze.
- I guasti dei diodi nuovi (L45d2b3) danno qualcosa di peggio che tornare al circuito di prima:
  - D158 / D159 aperti: si torna a 5,18 V e alle resistenze di prima;
  - D158 / D159 in corto: la base-emettitore di un finale in corto.
- La misura sul prototipo dà una distorsione o un clipping diversi a fondo scala sui carichi veri,
  per effetto del limite di corrente.
