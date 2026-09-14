# ADR-026 — Il terzo livello di guadagno: due rami di R_g in parallelo, 3,57 kΩ e 866 Ω, su due relè

Data: 2026-09-14 · Stato: accettata

## Contesto

**ADR-019** chiede tre guadagni, 0 / +3 / +10 dB, con **riposo a 0 dB**, e
conserva il principio di **ADR-004**: si commuta R_g verso massa, mai R_f. Il
valore del gradino intermedio e il numero di relè li lascia al dimensionamento.

Il circuito ne aveva due: un solo ramo R_g = 698 Ω, su un polo di K1 per
canale (**NC-022**). Restavano tre scelte:
- come si combinano i rami;
- con quali valori;
- con quali relè.

## Decisione

**Due rami da FB verso massa, in parallelo, ciascuno col proprio contatto
normalmente aperto:**
- **R_g3 = 3,57 kΩ** su **K1**;
- **R_g10 = 866 Ω** su un relè nuovo, **K5**, anche lui un G6K-2F-Y con un polo
  per canale.

| Comando | K1 | K5 | R_g equivalente | Guadagno |
|---|---|---|---|---|
| riposo | aperto | aperto | ∞ | **0 dB** |
| +3 dB | chiuso | aperto | 3,57 kΩ | **+3,047 dB** |
| +10 dB | chiuso | chiuso | 696,9 Ω | **+9,972 dB** |

- **Finestra del gradino intermedio: +3 dB ± 0,1 dB.** È asserita sulla netlist
  dal diagramma a blocchi, insieme alla connettività in parallelo.
- **Il +10 dB resta nella finestra 9,5–10,5 dB** che il disegno asseriva già.

## Perché

**In parallelo, per sicurezza per costruzione.** Chiudere un ramo può solo
abbassare la R_g equivalente verso 3,57 k ∥ 866 Ω. Quindi:
- nessuno stato dei contatti, **saldati compresi**, supera il +10 dB;
- un guasto su una bobina dà **meno** guadagno di quello comandato. Il caso
  peggiore è K1 guasto con +10 dB comandato: resta il solo ramo da 866 Ω,
  cioè **+8,730 dB**;
- nessun contatto sta in serie a un altro, né in serie all'anello. È ADR-004
  com'era.

**I valori.** Fra le coppie E96, 3,57 k / 866 Ω è quella che lascia il
+10 dB più vicino alla rete che sostituisce: 696,9 Ω contro 698, uno scarto
dello 0,16 %. Quindi:
- il carico della rete sullo stadio d'uscita a +10 dB resta 2,2 kΩ;
- il rumore di R_f resta quello di prima;
- ogni cifra pubblicata a +10 dB si sposta di centesimi.

Il gradino intermedio cade a +3,047 dB: uno scarto di 0,047 dB, che non ha
bisogno di un'accettazione a parte.

**Il relè.** È la stessa parte di K1, già verificata:
- pinout letto in L21 e asserito da `check_relay_safe_state.py`, che riconosce
  «GAIN10» come relè di guadagno;
- T7/T8 della parte già chiusi in L8.

Si chiama **K5** e non K2 perché i tre relè di mute tengano i loro riferimenti
(limitazione #22).

**Il budget delle bobine**, dal datasheet in `vendor/relays/omron/G6K/`
(tolleranza ±10 %). Il caso peggiore sono **cinque bobine eccitate**: +10 dB,
fuori mute.

| Tensione di bobina | Per bobina | Cinque bobine | Prima (quattro) |
|---|---|---|---|
| 5 V | 21,1 mA | **105,5 mA** | 84,4 mA |
| 12 V | 9,1 mA | 45,5 mA | 36,4 mA |
| 24 V | 4,6 mA | 23,0 mA | 18,4 mA |

La tensione di `VRELAY` **non è ancora decisa**: è un dato per `psu-engineer`.

**Le misure**, in `data/2026-09-14/L27/`. Il criterio è quello di ADR-024: cavo
al jack, minimo della spazzata fino a 4,7 nF, sorgenti dell'attenuatore da
1 mΩ, 1 k e 2,5 k, carichi 100 k e 10 k.

| Blocco B | Minimo | Agli spigoli (C ±5 %, R ±1 %) | Prima (L12) |
|---|---|---|---|
| 0 dB | **61,83°** (2,5 k, 3,3 nF) | **61,45°** | 61,21° / 60,73° |
| +3 dB | **69,79°** (2,5 k, 2,8 nF, griglia fitta) | **68,67°** | — |
| +10 dB | 102,99° (2,5 k, 4,7 nF) | — | 102,96° |

Il margine a 0 dB **sale** di 0,62°. Con i contatti aperti, sul nodo FB
restano appesi due rami con i loro 15 pF di capacità parassita: 3,57 k e 866 Ω,
al posto di 698 Ω. Il costo del C_f di ADR-025 non cambia.

**Sul resto della matrice**, sempre dai deck versionati:

| Grandezza | Esito |
|---|---|
| **V2** | con due contatti che rimbalzano, in ogni passaggio fra 0, +3 e +10 dB e in entrambi gli ordini sul salto diretto, l'uscita resta dentro l'inviluppo del +10 dB: +1,5218 / −1,6263 V. L'anello non si apre |
| **P7**, +3 dB | MJE peggiore del blocco B 339,6 mW, Tj 81,2 °C (limite 125 °C); 47 Ω del MAIN 0,309 W |
| **ADR-023** | 0 righe ascoltabili fuori dalla classe A, in ogni modo |
| **E5**, +3 dB | 2,011 µV con 2,5 kΩ di sorgente |
| **PSRR** dal rail +, +3 dB | 69,07 / 56,53 / 36,73 dB a 100 Hz / 1 kHz / 10 kHz |
| **Banda** a +3 dB | −3 dB a 537 kHz, −0,013 dB a 20 kHz rispetto a 1 kHz |

## Alternative scartate

- **Due rami mutuamente esclusivi**: +3 dB con 3,65 k da solo, +10 dB con il
  698 Ω di prima da solo. Avrebbe lasciato ogni cifra del +10 dB identica. Ma
  con entrambi i contatti chiusi — un contatto saldato, o un errore del comando
  — la R_g scende a 586 Ω e il guadagno a **+11,03 dB**, **sopra** il livello
  massimo. Scartata per questo.
- **Un contatto d'abilitazione in serie a un selettore Form C** che sceglie fra
  i due rami. Anche questa non supera il +10 dB, ma:
  - mette **due contatti in serie** su ogni ramo;
  - nel passaggio +3 → +10 dB il selettore fa break-before-make, quindi il
    guadagno ripassa per 0 dB a ogni commutazione.
- **Un relè per canale**, coi due poli di ogni relè sui due rami dello stesso
  canale. Anche questa usa due relè, ma un guasto di bobina lascerebbe **i due
  canali a guadagni diversi**, contro T3/ADR-006. Coi rami per relè, un guasto
  tocca i due canali allo stesso modo.
- **Altre coppie E96**, calcolate:

  | R_g3 / R_g10 | +3 dB | +10 dB |
  |---|---|---|
  | 3,65 k / 866 | 2,990 | 9,947 |
  | 3,65 k / 845 | 2,990 | 10,065 |
  | 3,74 k / 845 | 2,929 | 10,038 |

  La scelta fatta è quella che sposta meno il +10 dB esistente.

## Da riaprire se

- **La Fase 4** (NC-017, NC-020, NC-025) cambia i modelli. La guardia agli
  spigoli a 0 dB è 1,45°.
- **La capacità parassita** di un contatto aperto, misurata sul prototipo,
  risulta molto diversa dai 15 pF simulati: il margine a 0 dB dipende da lei.
- **Il comando delle bobine** si progetta in un modo che non garantisce «K5 solo
  insieme a K1». La proprietà «mai sopra +10 dB» resta, ma K5 da solo diventa
  un modo raggiungibile (+8,73 dB), non un guasto.
- **L'utente** trova il gradino di +3 dB scomodo all'ascolto.

Precisa **ADR-019**, fissando valore del gradino e relè, ed **estende ADR-004**
senza superarla.
