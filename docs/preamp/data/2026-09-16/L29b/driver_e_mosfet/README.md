# L29b — il driver VOM1271 e la coppia DMN6040SVT nei modelli del costruttore

**SIMULATO, ngspice 47.** Banchi di caratterizzazione, non misure di V2.

Modelli:
- `models/optocoupler/vom1271.lib`, derivato con due modifiche per ngspice
  (vedi `vom1271.provenance.json`; `deriva.py` le applica);
- `models/mosfet_n/dmn6040svt.lib`, blocco del costruttore copiato identico.

I banchi scrivono alcuni file nello scratch del job
(`/Users/roberto/.claude/jobs/c42646c7/tmp/vom/`): per rigenerarli vanno corretti
i percorsi. Le uscite di questa esecuzione sono `*.out.txt`.

## 1. Il driver con la coppia (`car.cir` → `car.out.txt`)

VOM1271 col LED pilotato in corrente, 1 MΩ fra gate e source comuni, coppia
contrapposta. Una tabella per tipo di risultato, perché le colonne non si
confrontano fra loro.

**Tensione di gate contro corrente nel LED** (letta a I_LED = 2 / 5 / 10 / 20 mA):

| I_LED | Vgs |
|---|---|
| 2 mA | 2,97 V |
| 5 mA | 6,66 V |
| 10 mA | 7,94 V |
| 20 mA | 8,60 V |

Sotto Voc, Vgs = 1,5e-3 · I_LED · 1 MΩ; poi si limita. Il datasheet dà Voc
8,4 V tipici a 10 mA con uscita aperta.

**Resistenza della coppia accesa**, con 1 mV ai capi:

| I_LED | Resistenza |
|---|---|
| 5 mA | 82,6 mΩ |
| 10 mA | 80,6 mΩ |
| 20 mA | 79,9 mΩ |

ADR-037 dà ≤ 120 mΩ al massimo dal datasheet.

**La seconda parte di `car.out.txt` (`yc`, «capacità della coppia aperta») NON
VALE**: è la trappola del punto 2. Il log contiene «stepping failed» e l'AC ha
linearizzato la coppia come resistiva. Si lascia com'è, come esempio.

## 2. La trappola del punto di lavoro (`t5.cir`, `opvar.py` → `opvar.out.txt`)

A LED spento, con l'anodo alimentato solo da un generatore di corrente a 0 A, il
punto di lavoro **non converge**: gmin stepping e source stepping falliscono, e
ngspice ripiega sul «transient op». **Nessun errore.** L'AC successiva vede la
coppia aperta come **7,02 mA per 1 V**, cioè ≈ 71 Ω resistivi per MOSFET,
attraverso il canale.

| Variante | op fallito | I(AC) coppia aperta a 1 kHz, 1 V |
|---|---|---|
| base | sì | 7,02 mA |
| 1 µA nel LED | no | 1,62 µA, capacitiva (≈ 258 pF a 0 V) |
| 1 MΩ dall'anodo a massa | no | 1,62 µA |
| 10 MΩ dal source a massa | sì | 7,02 mA |
| 1 V DC sul drain | sì | 10,1 mA |

Un MOSFET da solo, con gate e source a massa, è capacitivo: 58 pF a 25 V,
contro Coss 57 pF del datasheet. **Regola per ogni deck di L29b: l'anodo del LED
ha sempre un percorso in continua, e il log non deve contenere «stepping
failed».**

## 3. Il modello del MOSFET non ha regione sottosoglia (`sub.cir` → `sub.out.txt`)

Conduttanza drain-source a Vds = 10 mV contro Vgs:
- fino a 2,45 V: 40–47 nS, perdite del modello, che per di più **calano** al
  salire di Vgs;
- a 2,50 V: **0,70 S**; a 3,2 V: 16,2 S.

**Sette decadi in 50 mV.** Il blocco del costruttore è un LEVEL 3 senza `NFS`:
sotto `VTO` = 2,48 V il canale è spento del tutto. In questo modello il MOSFET è
un interruttore a 2,48 V.

Il datasheet non copre quella regione: la Fig. 4 (caratteristica di
trasferimento) è in scala lineare e in ampere. Pubblica invece:
- **Fig. 10**: Vth ≈ 2,0 V a 25 °C (ID = 1 mA), che scende circa 1,55 V a 125 °C;
- **Fig. 12**: Coss ≈ 500 pF a 0 V, ≈ 100 pF a 5 V, 57 pF a 25 V.

**Conseguenza.** Il mute graduale di ADR-037 vive proprio nella regione che né il
modello né il datasheet descrivono: fra ~1e-8 S e ~1e-3 S, cioè da −60 dB a 0 dB
al jack con ~68 kΩ di carico. Una misura di V2 fatta col modello com'è
vedrebbe un contatto netto.
