# L45d2b2c — i massimi del blocco col rail alto, e la base dei finali (2026-10-21)

Lotto di **NC-042** (prima di G1), ultima parte di L45d2b2. Risponde al punto 1 di **ADR-078** con
**ADR-095**. Dati: `data/2026-10-21/L45d2b2c/` (README). All'inizio l'utente: **«Una sessione»**.

## Che cosa si è misurato

ADR-078 chiedeva di leggere le tensioni massime delle parti del blocco col rail fino a ±20,3 V, e la
dissipazione dei finali, prima di decidere un sorvegliante della sovratensione.

1. **Il rail alto vero**, sul banco dell'alimentatore di L45d2b2b2 coi modi di L45c1 che alzano un rail
   (spariti dai banchi da L45c2), rifatti sul circuito di oggi (R550 / R551, il regolatore a 15,3 V sul
   piedino, lo Schottky in serie dopo), alle tre reti. Controllato rieseguendo i deck di L45c1: 20,3253 /
   −20,2980 V, cifra per cifra.
2. **Il blocco col rail alto**, sul banco di L62b coi rail sostituiti, nella posizione della
   principale: blocco sano e i quattro guasti del moltiplicatore, le tensioni fra ogni coppia di
   terminali di ogni parte, contro i massimi dei datasheet (`limiti_blocco.csv`, agente
   bom-component-manager, solo web). Lo strumento controllato con la legge di Ohm su 15 resistenze e un
   sabotaggio; a ±15 V il banco ridà L62b.
3. **P7** (mute inserito o uscita in corto, con la musica) coi rail alti, alle tre reti, e per la prima
   volta con le **giunzioni base-emettitore dei finali in inversa**.

## Il rail alto

| | rete −10 % | nominale | +10 % |
|---|---|---|---|
| U501 ingresso-uscita in corto | +16,2 V | +18,1 V | **+20,05 V** |
| U502 ingresso-uscita in corto | −16,2 V | −18,1 V | **−19,97 V** |

SENSE aperto, R501 aperta e il pin ANY-OUT a massa stanno sotto (fino a +19,8 / −19,8 V). Il firmware
non vede niente, e il jack resta collegato. Il percorso di oggi toglie ~2,2 V rispetto ai 20,3 V di
L45c1 a rete nominale; a +10 % si torna appena sotto. Il blocco è stato corso a ±20,3 V, per eccesso.

## Il blocco

- **Tensioni: 272 massimi, 0 fuori**, anche con tutti e due i rail a ±20,3 V:
  - LSK489 al più 12,7 V fra drain e source, contro i 60 V delle sue giunzioni di gate;
  - C145 20,1 V contro 25 V; i collettori ≤ 40 V contro 60–250 V;
  - a blocco fermo nessuna base-emettitore in inversa.
- **Calore dei finali** (60 °C d'aria): 85,5 °C a riposo col rail alto; 112,9 °C sommando un guasto del
  moltiplicatore (doppio guasto).
- **P7 col rail alto: fuori le resistenze d'uscita.** Alle tre reti col rail misurato:
  - la 22 Ω del PNP 0,358 / 0,391 / 0,401 W contro 0,34 W (ADR-087);
  - la 22 Ω dell'NPN fino a 0,360 W;
  - la 47 Ω della principale 1,35 / 1,44 / 1,47 W contro 1,3 W.
  I finali al più 101 °C.
- **P7 già a ±15 V, senza guasti: fuori la base del finale NPN.** Nella cella più dura (principale a
  +10 dB, 20 kHz a fondo scala, mute o corto) la base di Q132 spento sale **5,18 V** sopra l'emettitore,
  mentre Q133 porta la corrente del corto; il MJE15032 ammette 5 V. A 1 kHz 4,97 V. P7 non l'aveva mai
  misurato (limitations #69).

## Le scelte dell'utente

1. Il rail alto: **«Resistenze più robuste»** (22 Ω ≥ 0,45 W, 47 Ω ≥ 1,6 W), contro il sorvegliante e
   l'accettazione.
2. La base dei finali: **«Rimedio in questo lotto»**, contro una non conformità maggiore o minore.

## Il rimedio

Un 1N4148 in antiparallelo sulla base-emettitore di ciascun finale, provato prima come variante del
blocco in P7 su dieci rail:

| P7, il peggiore | Senza | Coi diodi |
|---|---|---|
| base-emettitore in inversa a ±15 V | 5,18 V | 0,77 / 0,84 V |
| 22 Ω, rail alto, tre reti | ≤ 0,401 W | ≤ 0,181 W |
| 47 Ω principale, rail alto, tre reti | ≤ 1,47 W | ≤ 0,78 W |
| finale PNP a ±15 V | 82,7 °C | 92,7 °C |
| finale PNP, rail − alto a +10 % | 100,9 °C | 109,8 °C |
| i diodi | — | ≤ 29 mA, ≤ 5 mW |

**Il diodo fa anche da limite di corrente.** La base del finale spento resta agganciata al suo
emettitore, e lo spread del moltiplicatore fissa la corrente dell'altro finale a ~0,11 A sul lato PNP
(era 0,214). Le resistenze si raffreddano, il PNP si scalda di più. In uso normale il blocco porta al
più ~10 mA, e la regressione lo conferma.

Coi diodi la prima scelta non serviva più. Riportata all'utente coi numeri: **«Vincoli di oggi»**. Le
22 Ω restano ≥ 0,34 W e la 47 Ω ≥ 1,3 W. Nessun sorvegliante. → **ADR-095**.

## Il sorgente

- `gain_block.py` sezione 12, D158 / D159 in fondo (limitations #22). La scheda audio passa da 554 a
  **570 parti**, senza sigle doppie: 16 diodi sui finali nel verso giusto (blocco A D156 / D157,
  blocco B D257 / D258, fisse D555 / D556 e D655 / D656, e l'altro canale).
- Il disegno del blocco: 61 dispositivi, guardato a occhio, e rifiuta il blocco di prima.
- I commenti delle 22 Ω e della 47 Ω coi numeri nuovi.
- **La regressione dei 21 deck veloci**, prima (main 82a94e57) e dopo, sulle misure dei log:
  - fuori da P7 tutto entro 3e-3 relativo, i margini di fase −0,004° al più;
  - in P7 le cifre della variante, uguali.
- `run_tests.sh` **13 / 0**.

## Non conformità

- **NC-042 avanza**: L45d2b2 è finito; restano i guasti rifatti e la sintesi (L45d2b3).
- **NC-074 aperta e chiusa**: la base dei finali in P7 oltre i 5 V, rimediata nello stesso lotto per
  decisione dell'utente.
- Il rail alto non apre voci: rientra coi diodi.

## Che cosa resta

- **L45d2b3**, coi modi delle parti nuove. Ci sono anche D158 / D159:
  - aperti, si torna ai 5,18 V e alle resistenze di prima;
  - in corto, la base-emettitore di un finale in corto.
- **Gli elettrolitici del blocco** non hanno una tensione scritta nel sorgente: C141 / C142 vedono fino
  a 20,3 V col rail alto, C116 13,4 V. È da fissare alla scelta delle parti.
- **La tabella dei vincoli di distinta di REQUIREMENTS** (nota su P7) era ferma a L46a; riallineata ad
  ADR-087 / ADR-095.
- **La richiesta dell'utente a fine lotto**: lo schematico completo, in due pagine (scheda audio e
  alimentatore), anche A3. Diventa il lotto **L63**, il prossimo, prima di L45d2b3.
