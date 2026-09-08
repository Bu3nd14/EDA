# Fase 2 — Bozza della topologia

Data: 2026-09-08 · Owner: `analog-topology-designer` · Tipo: report (datato)

**`circuits/` non è più vuota.** Questo è il primo circuito canonico del
repository.

## Verifica indipendente

I risultati sotto sono stati **riprodotti dall'orchestratore**, non
accettati sulla parola:

```
$ /Users/roberto/EDA/env/venv/bin/python3 circuits/preamp/gain_block.py
0 errors, 44 device lines
$ /Users/roberto/EDA/env/venv/bin/python3 circuits/preamp/preamp_audio.py
0 errors, 205 componenti
$ /usr/bin/python3 scripts/validate_models.py
TOTAL: 24 PASS, 0 FAIL, 0 SKIP
$ ngspice -b spice/preamp/tb/tb_op.cir
offset uscita -11,83 mV · rail -26,36 mA / +27,39 mA
$ ngspice -b spice/preamp/tb/tb_switch_v2_counterfactual.cir
chiuso -37,2 mV · APERTO -13,68 V · richiuso -37,2 mV
```

Tutto rigenera da zero.

## Topologia

Tre stadi, retroazione globale, nessun operazionale, nessun servo.

1. **Coppia differenziale LSK489 cascodata** (ADR-013/014), 2 mA per
   ramo, degenerazione 100 Ω, pozzo di coda 4,4 mA.
2. **Specchio THAT320** (degenerazione 47 Ω) → **VAS 2N5401**, 6,4 mA,
   Miller 470 pF.
3. **Inseguitore complementare Classe A MJE15032/33**, 14,7 mA,
   emettitori 22 Ω, moltiplicatore di V_be.

Riferimenti di bias: due 1N4148 sopra V−, bypassati **a V−**, non a
massa.

## Punto di lavoro (simulato)

| Dispositivo | I | V |
|---|---|---|
| LSK489, i due rami | 2,204 / 2,170 mA | V_ds 8,75 V · g_m 4,38 mS |
| Pozzo di coda | 4,406 mA | V_ce 14,6 V |
| Cascode | 2,186 / 2,152 mA | V_ce ≈ 4,5 V |
| Specchio THAT320 | 2,125 / 2,129 mA | V_ce 0,72 / 1,17 V |
| VAS 2N5401 | 6,443 mA | V_ce 13,4 V |
| MJE15032/33 | 14,71 mA | V_ce 14,7 V · 214 mW ciascuno |

**Rail per blocco: 26,36 / 27,39 mA.** Quattro blocchi: **105 / 110 mA,
3,22 W** — coerente con la stima di ADR-010 (3-4 W).

**Il generatore di bias è stato sbagliato due volte a mano**: 2,16 kΩ
(V_be da manuale, 0,62 V) dava 22,1 mA; 1,87 kΩ dava 17,5 mA. Solo una
spazzata simulata ha trovato **1,69 kΩ → 14,7 mA**. Il numero reale, non
"15". Sensibilità: 3% sulla resistenza sposta I_q del 5,3%, quindi
**domina la dispersione di V_be, non la tolleranza della resistenza**.
Da rifare con i modelli veri.

## Previsioni dichiarate (falsificabili)

Da verificare indipendentemente da `measurement-analyst` in Fase 5.

| Figura | Previsione |
|---|---|
| Guadagno 0 dB / +10 dB | −0,002 dB / +9,955 dB |
| −3 dB, 0 dB | 0,493 Hz / 2,45 MHz |
| **Scarto di risposta a 20 kHz al variare del volume** | **≤ 0,001 dB** (ADR-014 ne prevedeva −0,42 senza cascode) |
| Margine di fase 0 dB, senza carico C | **63,5°** (incrocio 954 kHz) |
| Margine di fase 0 dB, cavo 1 nF | 58,8° |
| Margine di fase +10 dB | 86,2° |
| Z_out al jack, 1 kHz | 58,8 Ω |
| PSRR da V+ (100 Hz / 1 k / 10 k) | 72,0 / 59,5 / 39,7 dB |
| PSRR da V− | 88,9 / 100,5 / 96,9 dB |
| Rumore in uscita, uso normale | 1,9 µV |
| Rumore, caso peggiore (volume max, +10 dB) | **7,4 µV** contro i 10 µV di E5 |
| Recupero da sovraccarico 5,6 dB | < 1 µs, nessun aggancio |
| THD | **nessuna — vedi sotto** |

**Il modo peggiore per la stabilità è 0 dB, cioè quello normale.** V1
aveva ragione a pretendere entrambi.

## V2 — l'anello non si apre mai

R_f è cablata fissa OUT→FB. Il relè collega solo l'estremo di R_g a
massa. Contatti aperti → guadagno esattamente 1; chiusi → 3,149;
**in rimbalzo → il guadagno scorre fra i due valori, con l'anello chiuso
per tutta la transizione**. A relè diseccitato si ha il guadagno
unitario, cioè la modalità normale: fallisce nel verso giusto.

Simulato con modello di contatto reale (R_ON 50 mΩ, 3 rimbalzi in
chiusura, 2 in apertura): l'uscita resta entro ±1,61 V, cioè
esattamente l'inviluppo del +10 dB.

**Il controfattuale è la parte istruttiva.** Mettendo il contatto dove
ADR-004 lo aveva rifiutato — in serie a R_f:

```
contatto CHIUSO  → v(out) = -37,2 mV
contatto APERTO  → v(out) = -13,68 V     ← anello aperto
richiuso         → v(out) = -37,2 mV
```

**−13,68 V, a 1,3 V dal rail.** È il numero contro cui ADR-004
proteggeva, ora misurato invece che argomentato.

## Tensioni fra requisiti — sollevate, non assorbite

1. **E6 × E2 contro E7.** 2,7 V a +10 dB richiedono 8,54 V RMS in
   uscita; il blocco satura a 9,31 V. **Margine 0,75 dB.** Strutturale:
   i rail ±15 V non hanno spazio per 2,7 × 3,16. La mitigazione è il
   trim di ADR-011 — vedi il suo addendum: **da comodità è diventato
   portante**.
2. **E4 contro E8 a 20 Hz.** La Z_out al jack a 20 Hz è ~1,7 kΩ, cioè la
   reattanza del condensatore d'accoppiamento. E4 letto alla lettera è
   insoddisfacibile a 20 Hz da *qualunque* uscita accoppiata in
   alternata. Costa 0,0075 dB sul carico reale: **problema di
   formulazione, non di circuito.** E4 è stato riformulato.
3. **ADR-008 a 100 Ω** poneva le uscite fisse *al* limite di E4, non
   sotto. Il progettista ha implementato la ADR come scritta e ha
   sollevato il conflitto invece di correggerlo da sé. **Adottati 47 Ω**
   (addendum a ADR-008).

## Deviazione dal percorso documentato

La Fase 2 **non** ha usato `generate_schematic()` →
`kicad-cli sch export netlist --format spice`: per ~40 componenti finisce
dritto nelle limitazioni #3 e #5. `spice_export.py` percorre invece gli
stessi oggetti SKiDL, quindi **la topologia resta definita una volta
sola**.

Il rischio però si sposta sull'esportatore, ed **è già morso una volta**
(vedi `limitations.md` #13). Da qui il nuovo requisito **V5**: le due
netlist vanno confrontate per equivalenza topologica prima di G2, in
modo automatizzato.

## Ciò che NON è verificato

Elencato dal progettista senza attenuanti, e va preso sul serio.

1. **Nessuna cifra di THD esiste.** Un testbench ne stampa una
   (0,00084%) ed è **priva di significato**: viene da modelli
   Gummel-Poon scritti a mano con IS/BF/VAF/TF inventati. La distorsione
   vive precisamente nei parametri che sono stati indovinati.
2. **Il margine di fase è provvisorio** — dipende da capacità e tempi di
   transito scelti a ordine di grandezza plausibile. Con i modelli
   generici del repo avrebbe risposto ~90° incondizionatamente, cioè una
   risposta che *sembra* evidenza.
3. **Il rumore non ha componente 1/f** (KF = 0 ovunque). Nota: il
   contributo dominante risulta **lo specchio, non i JFET** — ma quel
   ranking dipende da un r_bb' indovinato. I 4,98 nV/√Hz di R_f sono
   invece reali e indipendenti dal modello.
4. **Il guadagno d'anello scala con la g_m del JFET**, che è il
   parametro meno conosciuto.
5. **Non esiste un simbolo KiCad per l'LSK489.** Ora sono due
   `Q_NJFET_DGS`. Serve un simbolo a 2 unità con il piedinatura reale
   prima di G2.
6. **I pin dei transistor sono alfabetici** (B/C/E): la netlist è
   topologicamente corretta ma non mappa sui pad. Lavoro di G2.
7. **`.op` solo a 27 °C.** Nessuna spazzata di temperatura, nessuna
   verifica di deriva termica sul bias di Classe A.
8. **Transienti di accensione/spegnimento non simulati** (parte di V2):
   servono i modelli dell'alimentatore.

## Consegne per le fasi successive

**Per `psu-engineer`**: ±15 V, **105/110 mA**, 3,22 W. Rail separato per
i relè (4 × G6K-2F-Y). **V+ è il rail debole per il PSRR di ~30 dB**, ed
è strutturale — specchio e VAS poggiano entrambi su V+. Requisito:
**≤ 1 mV picco di ripple a 100 Hz su V+** e **≤ 30 µV di rumore a banda
larga sopra 10 kHz**, il che esclude di fatto un alimentatore a
commutazione non filtrato.

**Per `bom-component-manager`**: parti nuove non coperte dalla Fase 1 —
**2N5401** (VAS) e **2N5551** (cascode, pozzi, spreader). Più: stock
THAT320 e conferma **BV_ceo ≥ 35 V**; la trascrizione del modello LSK489
secondo ADR-013; **quale contatto del G6K-2F-Y è NO e quale NC** (il
progetto fallisce nel verso giusto solo se l'assegnazione è corretta);
C0G/NP0 obbligatorio per il Miller da 470 pF; polipropilene per i
condensatori di segnale.

## Una scelta di progetto sottile, da non perdere

È stato **rifiutato** un condensatore di shunt RF al gate. Un C fisso
verso massa forma un polo con l'impedenza di **sorgente**, che per il
blocco B è l'attenuatore che oscilla fra 0 e 2,5 kΩ: 470 pF metterebbero
quel polo a 124 kHz a metà corsa, **reintroducendo esattamente la
risposta dipendente dal volume che ADR-014 esiste per eliminare**. Se
l'EMC ne richiederà uno, deve essere ≤ 47 pF.
