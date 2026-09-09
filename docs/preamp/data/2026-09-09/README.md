# 2026-09-09 — dati misurati del preamplificatore

Questa directory raccoglie i dati **curati** prodotti il 2026-09-09 da due
lotti: il controfattuale del relè di guadagno (**L4**) e le risposte in
frequenza, il guadagno d'anello, il PSRR e la Z_out (**L5**).

Tutti i numeri vengono da **modelli segnaposto**
(`spice/preamp/placeholder_devices.lib`). Cosa si può citare e cosa no è
detto in fondo, sezione *Provenienza e limite*.

## Indice

| Sezione | File | Lotto |
|---|---|---|
| Controfattuale del relè (ADR-004) | `tb_switch_v2_counterfactual*` | L4 |
| Risposta in frequenza (ADR-014) | `tb_ac*` | L5 |
| Guadagno d'anello e margine di fase | `tb_loop_*` | L5 |
| Z_out al jack (E4) | `tb_zout_psrr_noise_zout_*` | L5 |
| PSRR dei due rail | `tb_zout_psrr_noise_psrr*` | L5 |

**Il rumore non è qui, di proposito.** I deck lo producono (L5 ne scrive gli
spettri in `results/`), ma `KF = 0` su ogni dispositivo segnaposto: non c'è
rumore 1/f in nessuna di queste simulazioni, quindi la cifra è un pavimento
termico+shot e non una previsione. Entrerà nel dossier dopo L6-L7. È la
stessa ragione per cui L4 aveva tenuto fuori `tb_noise_vectors`.

---

# L4 — controfattuale del relè di guadagno (ADR-004)

Prodotto in **L4**. Deck: `spice/preamp/tb/tb_switch_v2_counterfactual.cir`,
rieseguibile in qualsiasi momento con

```sh
/bin/zsh scripts/run_simulation.sh spice/preamp/tb/tb_switch_v2_counterfactual.cir \
         results/preamp/tb_switch_v2_counterfactual
```

## Perché questi numeri sono nel dossier

ADR-004 ha **scartato** l'idea di mettere il contatto del relè in serie a
R_f (il ramo dell'anello). Una decisione di progetto porta informazione
solo se la disposizione scartata è mostrata **fallire**: questo è il
mezzo falsificabile della verifica V2, e il transitorio del relè nel
dossier va affiancato proprio a questo controfattuale.

Con R_f aperto l'anello è rotto, la coppia d'ingresso vede solo il
proprio offset moltiplicato per tutto il guadagno ad anello aperto, e
l'uscita si appoggia al rail: **−13,68 V**.

## I tre file

| File | Stato | `v(OUT)` |
|---|---|---|
| `tb_switch_v2_counterfactual.csv` | A — contatto **chiuso**, R_f = 1,50 kΩ | −0,0372229 V |
| `tb_switch_v2_counterfactual_open.csv` | B — contatto **aperto**, R_f = 1e12 Ω | **−13,676851 V** |
| `tb_switch_v2_counterfactual_reclosed.csv` | C — richiuso, controprova di B | −0,0372229 V |

C esiste per escludere che B sia un artefatto del solutore: A e C
coincidono a tutte le cifre.

## Legenda delle colonne

`run_simulation.sh` intesta i CSV `col0…colN`, quindi l'identità delle
colonne vive solo qui e nel commento dentro il deck.

Un `wrdata` preso da un `.op` scrive **una riga** e, per ogni vettore
richiesto, una **coppia** di colonne `(scale, valore)`. Lo *scale* di un
plot `op` è un vettore arbitrario del plot e **non significa niente**. I
dati sono quindi le colonne **dispari**:

| Colonna | Vettore |
|---|---|
| col1 | `v(OUT)` |
| col3 | `v(FB)` |
| col5 | `v(NX)` |
| col7 | `v(NY)` |

Le colonne pari (col0, col2, col4, col6) sono lo scale ripetuto: si
ignorano.

## Provenienza e limite

Modelli **segnaposto** (`spice/preamp/placeholder_devices.lib`), non
vendor. Questo dato è un risultato **in continua**, cioè la parte che il
progetto dichiara credibile anche con i segnaposto: nessuna cifra di
distorsione o di rumore va ricavata da qui.

`tb_switch_v2_counterfactual.log` è l'evidenza: contiene gli stessi
`v(out)` stampati da ngspice, con cui i CSV sono stati confrontati.


---

# L5 — risposta, anello, Z_out e PSRR

Deck: `spice/preamp/tb/tb_ac.cir`, `tb_loop.cir`, `tb_zout_psrr_noise.cir`.
Rieseguibili con

```sh
/bin/zsh scripts/run_simulation.sh spice/preamp/tb/<deck>.cir results/preamp/<deck>
```

Ogni deck produce più file di quelli versionati qui: questa è la selezione
**curata** che il dossier impagina, non l'output grezzo. I `.log` accanto ai
CSV sono l'evidenza: contengono i `meas` con cui i CSV sono stati confrontati.

## Come si leggono i CSV

`run_simulation.sh` intesta i CSV `col0…colN` e basta, quindi l'identità
delle colonne vive **solo qui e nel commento dentro il deck**.

In un `wrdata` da un'analisi `ac`, per ogni vettore richiesto escono **due**
colonne: `(frequenza, valore)`. Le colonne **pari sono la frequenza
ripetuta**, i dati sono le **dispari**.

## Risposta in frequenza — `tb_ac_*`

Cinque file. Il nome porta la modalità di guadagno e l'impedenza della
sorgente in ohm.

| File | Modalità | R_sorgente | Cosa rappresenta |
|---|---|---|---|
| `tb_ac_0db_1.5.csv` | 0 dB (relè aperto) | 1,5 Ω | K11, sorgente ideale |
| `tb_ac_0db_2500.csv` | 0 dB | 2500 Ω | attenuatore a metà corsa |
| `tb_ac_10db_1.5.csv` | +10 dB (relè chiuso) | 1,5 Ω | |
| `tb_ac_10db_2500.csv` | +10 dB | 2500 Ω | |
| `tb_ac.csv` | 0 dB | 430 Ω | **la sezione fuori ciclo**: corner LF con RLOAD = 50 kΩ, 0,1–1000 Hz |

Colonne (≈1636 righe, 0,2 Hz – 30 MHz, 200 punti/decade; `tb_ac.csv` ne ha
801, 0,1–1000 Hz):

| Colonna | Vettore |
|---|---|
| col0 | frequenza [Hz] |
| col1 | `G` = \|v(JACK)\| in **dB** |
| col2 | frequenza [Hz] |
| col3 | `Gph` = fase di v(JACK) in **gradi** |

**Cosa dicono, ed è la claim falsificabile di ADR-014**: l'impedenza
dell'attenuatore va da 0 a 2500 Ω ruotando la manopola, e la risposta a
20 kHz **non deve muoversi**. Non si muove:

| | R_src = 1,5 Ω | R_src = 2500 Ω | scarto |
|---|---|---|---|
| 0 dB, 20 kHz | −0,00830 dB | −0,02993 dB | **0,022 dB** |
| +10 dB, 20 kHz | +9,9331 dB | +9,9116 dB | **0,022 dB** |

Corner LF con il carico da 50 kΩ: −0,0163 dB a 1 kHz, −0,0238 dB a 20 Hz,
−0,134 dB a 5 Hz.

## Guadagno d'anello — `tb_loop_*`

Quattro file: le due modalità ai due estremi della capacità di cavo.

| File | Modalità | C_cavo | f_incrocio | margine di fase |
|---|---|---|---|---|
| `tb_loop_0db_1f.csv` | 0 dB | ~0 | 954 kHz | **63,5°** |
| `tb_loop_0db_4.7n.csv` | 0 dB | 4,7 nF | 838 kHz | **56,9°** |
| `tb_loop_10db_1f.csv` | +10 dB | ~0 | 306 kHz | **86,2°** |
| `tb_loop_10db_4.7n.csv` | +10 dB | 4,7 nF | 296 kHz | **80,6°** |

Colonne (801 righe, 1 Hz – 100 MHz, 100 punti/decade):

| Colonna | Vettore |
|---|---|
| col0 | frequenza [Hz] |
| col1 | `Tdb` = \|T\| in **dB**, con T = v(FB)/v(G2) |
| col2 | frequenza [Hz] |
| col3 | `Tph` = fase di T in **gradi** |

**Attenzione a come si legge il margine.** G2 è l'ingresso **invertente**,
quindi T è negativo reale in continua e la sua fase lì vale 180°. Il margine
di fase si legge come **\|Tph\| dove Tdb attraversa lo zero**, non come
180 − \|Tph\|.

Il relè commuta la rete di controreazione, quindi **il margine è diverso
nelle due modalità** — è esattamente la ragione per cui `REQUIREMENTS.md`
chiede la matrice V1 e non un caso solo.

**Questi quattro numeri sono provvisori.** Il margine di fase dipende dalle
capacità e dai tempi di transito dei dispositivi, e nei modelli segnaposto
sono stati scelti a mano a un ordine di grandezza plausibile, non fittati su
un datasheet. Vanno rifatti sui modelli vendor prima di poter essere citati.

## Z_out al jack — `tb_zout_psrr_noise_zout_*`

Due file, uno per modalità. 1 A AC iniettato al jack, ingresso a massa,
carico rimosso; il bleeder da 220 kΩ resta perché il circuito vero ce l'ha.

Colonne (74 righe, 20 Hz – 100 kHz, 20 punti/decade):

| Colonna | Vettore |
|---|---|
| col0 | frequenza [Hz] |
| col1 | `Z` = \|v(JACK)\| = **ohm al jack** (quello che vede il cavo) |
| col2 | frequenza [Hz] |
| col3 | `ZA` = \|v(OUT)\| = ohm al nodo OUT, **prima** di R_iso |

| | 20 Hz | 1 kHz | 20 kHz |
|---|---|---|---|
| 0 dB | 1693 Ω | 58,8 Ω | 48,0 Ω |
| +10 dB | 1693 Ω | 60,7 Ω | 50,3 Ω |

I 1693 Ω a 20 Hz **sono la reattanza del condensatore d'uscita da 4,7 µF**,
non l'impedenza dello stadio: al nodo OUT (col3) la Z vale 1,04 Ω in
modalità 0 dB. È la tensione fra E4 ed E8 già registrata in `STATE.md`:
E4 letta alla lettera non è soddisfacibile a 20 Hz da nessun circuito con
condensatore d'uscita.

## PSRR — `tb_zout_psrr_noise_psrr{p,m}_*`

Quattro file: `psrrp` = rail **+**, `psrrm` = rail **−**, per le due
modalità. 1 V AC in serie al rail, sorgente d'ingresso silenziata.

Colonne (74 righe, 20 Hz – 100 kHz):

| Colonna | Vettore |
|---|---|
| col0 | frequenza [Hz] |
| col1 | `P` = −db(v(JACK)) in **dB** — **più grande è meglio** |

| | 100 Hz | 1 kHz | 10 kHz |
|---|---|---|---|
| PSRR+ 0 dB | 72,0 dB | 59,5 dB | 39,7 dB |
| PSRR+ +10 dB | 62,1 dB | 49,6 dB | 29,8 dB |
| PSRR− 0 dB | 88,9 dB | 100,5 dB | 96,9 dB |
| PSRR− +10 dB | 79,0 dB | 90,5 dB | 86,9 dB |

Il rail **positivo** è il lato debole, e in modalità +10 dB perde i 10 dB di
guadagno: 29,8 dB a 10 kHz è il numero da tenere d'occhio quando arriverà
l'alimentatore (Fase 6).

## Provenienza e limite

Modelli **segnaposto**, non vendor. Di questi dati sono credibili la
**forma** delle risposte in frequenza, i rapporti di guadagno, le impedenze
e i risultati in continua. **Non** lo sono le cifre di distorsione (assenti
di proposito) né quelle di rumore (escluse da questa directory), e i margini
di fase sono provvisori come detto sopra.
