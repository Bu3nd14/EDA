# ADR-064 — Il selettore d'ingresso: un condensatore per ingresso col lato del preamp a 0 V, un relè monostabile per ingresso dalla manopola

Data: 2026-10-06 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Realizza ADR-009** sugli ingressi: «commutati a relè, pilotati direttamente da un commutatore
  rotativo». Niente telecomando e niente firmware nel selettore restano.
- **Precisa F1 e PR-14** (ADR-053) senza cambiarli: «ogni ingresso sta a 0 V» si legge sui due
  lati del condensatore, il jack (R_J) e il lato del preamp (R_SEL).
- Supera la frase di NC-040 «commutare sotto mute, ~13 s col profilo di oggi»: non si commuta
  sotto mute.
- Non tocca NC-041 (la continua del blocco A attraverso trim e volume): è di L48b.

## Contesto

Fino a L48a l'ingresso era uno per canale e andava in continua al blocco A (R_IN 1 MΩ a massa).
Cambiando sorgente, la differenza fra le continue delle sorgenti arrivava a tutte le uscite
(NC-040, rilievo R2 di L43a): sul banco di L48a 10 mV di continua danno **10,1 mV** al jack fisso
(~73 dB SPL contro una stanza silenziosa) e **31,6 mV** al principale a +10 dB (~83 dB SPL);
F1 chiede 100 µV (~33 dB SPL). Il selettore non era mai stato progettato (PR-14).

## Decisione

Le risposte dell'utente (2026-10-06, domande per nome e in dB SPL), all'apertura di L48:

1. **«Due parti»**: L48a il selettore con i condensatori d'ingresso, L48b la continua attraverso
   trim e volume.
2. **«Condensatore per ingresso»**: per ogni ingresso e canale,
   `IN<n> → C_IN 1 µF (polipropilene) → nodo SEL → NO del relè dell'ingresso → ingresso del blocco A`,
   con **R_SEL 470 kΩ** a massa sul nodo SEL e **R_J 10 MΩ** a massa sul jack. Nessun mute al
   cambio d'ingresso.
3. **«Monostabili dalla manopola»**: un G6K-2F-Y per ingresso (K13–K16), polo 1 il sinistro e
   polo 2 il destro; la manopola SW4 (a pannello, 4 posizioni) alimenta da `VRELAY` la sola bobina
   della sua posizione, che torna su `RLY_RET` con un 1N4148 di ricircolo. A riposo nessun ingresso
   è collegato e il blocco A sta sul suo R_IN.

## Perché

Misure di L48a (`data/2026-10-06/L48a/`, `spice/preamp/tb/tb_f1_selettore.cir`):

- **F1 / PR-14 — il gradino al cambio d'ingresso**, picco su ogni uscita, A a 0 V, B alla continua
  VB, trasferimento del relè 1 ms, perdita del condensatore al minimo del poliestere (10 000 s,
  un limite per eccesso per il polipropilene):

  | VB | fisso | principale 0 dB | +3 dB | +10 dB |
  |---|---|---|---|---|
  | 0 | 6,28 µV | 6,29 µV | 8,93 µV | 19,8 µV |
  | 10 mV | 6,28 µV | 6,29 µV | 8,93 µV | 19,8 µV |
  | 100 mV | 6,28 µV | 6,29 µV | 8,93 µV | 19,8 µV |
  | 1 V | 44,3 µV | 44,3 µV | 63,0 µV | **140 µV** |
  | oggi, 10 mV (controfattuale) | 10,1 mV | | | 31,6 mV |

  Fino a 100 mV il gradino è quello del contatto stesso, lo stesso con due sorgenti a 0 V:
  19,8 µV è ~19 dB SPL. Col relè che si chiude 1 ms **prima** che l'altro si apra (l'ordine di
  due monostabili non è garantito) è più piccolo: 3,5 µV a 100 mV, 70,8 µV a 1 V. Il residuo
  cresce con VB per la perdita del condensatore sul R_SEL dell'ingresso non scelto: ~120 µV per
  volt al principale a +10 dB, quindi **F1 regge fino a ~0,65 V di continua della sorgente**
  col poliestere peggiore. È un limite dichiarato, non un difetto: una sorgente di linea con più
  di qualche decina di mV di continua è guasta.
- **R_SEL 470 kΩ e non 1 MΩ.** Con 1 MΩ la perdita lascia il doppio: 303 µV a 1 V al principale.
  E3 la permette: 470 kΩ ∥ R_IN 1 MΩ.
- **E3**, minimo di |Zin| al jack su 20 Hz–20 kHz, con 68 pF di selettore: **108,2 kΩ**, uguale
  nelle tre posizioni del trim (era 114,7 kΩ col solo R_IN; limite 100 kΩ). Con 1 MΩ sarebbe
  112,5 kΩ.
- **E9**: la rete perde 0,0027 dB a 20 Hz (1 µF su ~310 kΩ, 0,5 Hz).
- **E5**: invariato, il peggiore **5,496 µV** (+10 dB, 430 Ω), come L47c2b2.
- **L'alimentatore**: una bobina in più sempre accesa, +9,1 mA su `VRELAY` (81,9 mA di bobine nel
  caso peggiore). La tenuta di `VRELAY_REG` ≥ 11,4 V dopo una perdita di rete passa da 61,1 a
  **48,3 ms** a rete −10 % (nominale 142,2 → 121,7); P9 chiede ≥ 25 ms. Regime invariato.
- **Monostabili dalla manopola, niente firmware**: col condensatore il cambio non ha bisogno del
  mute, e il salto fra i due programmi con la musica F1 lo accetta già. È la soluzione di ADR-009
  com'era scritta, e il guasto di una bobina lascia solo l'ingresso muto.

## Alternative scartate

- **Commutare sotto mute, senza condensatori.** Il mute taglia in ~24 ms (L47c2a), ma la continua
  della sorgente resta sui condensatori d'uscita e scarica con ~1 s sul principale e ~2,2 s sulle
  fisse (220 kΩ e 470 kΩ dal lato del condensatore): per scendere sotto i 33 dB SPL da ~73 dB SPL
  servirebbero ~10 s di mute a ogni cambio. Calcolo, non misura; la misura del controfattuale
  conferma il gradino intero.
- **Condensatori e cambio sotto mute.** Toglierebbe anche il salto fra i programmi con la musica,
  che F1 accetta; costava pin del microcontrollore, firmware e controlli nuovi.
- **Bistabili come il trim.** Nessuna corrente a regime, ma servono gli impulsi di set e reset per
  quattro relè: più parti e più prove per 9,1 mA.
- **Un condensatore solo dopo il selettore.** La continua di ogni sorgente starebbe sullo stesso
  condensatore: a ogni cambio il gradino intero. È il motivo del «per ingresso».

## Da riaprire se

- una sorgente reale ha più di ~0,5 V di continua all'uscita (misurarla al prototipo; il K11 non
  la pubblica);
- il condensatore scelto in distinta ha una costante d'isolamento sotto 10 000 s;
- E3 si deve misurare con più di 68 pF di selettore e cablaggio;
- si vuole il cambio sotto mute (il salto fra i programmi con la musica non più accettato in F1).
