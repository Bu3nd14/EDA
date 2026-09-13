# 2026-09-09 — dati misurati del preamplificatore

Questa directory raccoglie i dati **curati** prodotti il 2026-09-09 da due
lotti: il controfattuale del relè di guadagno (**L4**) e le risposte in
frequenza, il guadagno d'anello, il PSRR e la Z_out (**L5**). **L5e** ha
poi aggiunto i carichi del Blocco A, l'evidenza di NC-010.

Tutti i numeri vengono da **modelli segnaposto**
(`spice/preamp/placeholder_devices.lib`). Cosa si può citare e cosa no è
detto in fondo, sezione *Provenienza e limite*.

## Indice

| Sezione | File | Lotto |
|---|---|---|
| Controfattuale del relè (ADR-004) | `tb_switch_v2_counterfactual*` | L4 |
| Risposta in frequenza (ADR-014) | `tb_ac*` | L5 |
| Guadagno d'anello e margine di fase | `tb_loop_*` | L5 |
| Z_out al jack (E4) | `tb_zout_psrr_noise_zout_*` | L5 · **rifatto in L5b** |
| PSRR dei due rail | `tb_zout_psrr_noise_psrr*` | L5 · **rifatto in L5b** |
| Punti di lavoro | `tb_op.*` | L5b |
| Escursione in continua e saturazione | `tb_dc_headroom*` | L5b |
| **Carichi del Blocco A** (NC-010) | `tb_blockA_carichi*` | **L5e** |

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

> **Nota L14 (2026-09-13) — la colonna «scarto» qui sopra NON misura la claim
> di ADR-014** (NC-007). È lo scarto assoluto, e vale **lo stesso a ogni
> frequenza**: 0,0217 dB a 20 Hz e a 1 kHz in entrambe le modalità, 0,0216 dB
> (0 dB) e 0,0215 dB (+10 dB) a 20 kHz. È il partitore fra la sorgente da
> 2500 Ω e la Zin da 1 MΩ, a banda larga, e ci sarebbe anche senza cascode. La claim
> riguarda la **forma** della risposta: lo scarto a 20 kHz **riferito a 1 kHz**
> vale **4,35·10⁻⁵ dB** a 0 dB e **1,37·10⁻⁴ dB** a +10 dB, ricavati dai
> `print` di `tb_ac.log`. Il dossier pubblica queste cifre, e le due non vanno
> confuse. La tabella resta com'era scritta, come traccia.

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

Colonne (81 righe, 20 Hz – 200 kHz, 20 punti/decade):

| Colonna | Vettore |
|---|---|
| col0 | frequenza [Hz] |
| col1 | `Z` = \|v(JACK)\| = **ohm al jack** (quello che vede il cavo) |
| col2 | frequenza [Hz] |
| col3 | `ZA` = \|v(OUT)\| = ohm al nodo OUT, **prima** di R_iso |

| | 20 Hz | 1 kHz | 20 kHz | 100 kHz |
|---|---|---|---|---|
| 0 dB | 1693 Ω | 58,76 Ω | 48,05 Ω | 48,06 Ω |
| +10 dB | 1693 Ω | 60,58 Ω | 50,30 Ω | 51,07 Ω |

I 1693 Ω a 20 Hz **sono la reattanza del condensatore d'uscita da 4,7 µF**,
non l'impedenza dello stadio: al nodo OUT (col3) la Z vale 1,04 Ω in
modalità 0 dB. È la tensione fra E4 ed E8 già registrata in `STATE.md`:
E4 letta alla lettera non è soddisfacibile a 20 Hz da nessun circuito con
condensatore d'uscita.

## PSRR — `tb_zout_psrr_noise_psrr{p,m}_*`

Quattro file: `psrrp` = rail **+**, `psrrm` = rail **−**, per le due
modalità. 1 V AC in serie al rail, sorgente d'ingresso silenziata.

Colonne (81 righe, 20 Hz – 200 kHz):

| Colonna | Vettore |
|---|---|
| col0 | frequenza [Hz] |
| col1 | `P` = −db(v(JACK)) in **dB** — **più grande è meglio** |

| | 100 Hz | 1 kHz | 10 kHz | 100 kHz |
|---|---|---|---|---|
| PSRR+ 0 dB | 72,0 dB | 59,5 dB | 39,7 dB | 19,7 dB |
| PSRR+ +10 dB | 62,1 dB | 49,6 dB | 29,8 dB | **10,2 dB** |
| PSRR− 0 dB | 88,9 dB | 100,5 dB | 96,9 dB | 71,0 dB |
| PSRR− +10 dB | 79,0 dB | 90,5 dB | 86,9 dB | 61,4 dB |

Il rail **positivo** è il lato debole, e in modalità +10 dB perde i 10 dB di
guadagno: 29,8 dB a 10 kHz è il numero da tenere d'occhio quando arriverà
l'alimentatore (Fase 6).

## Provenienza e limite

Modelli **segnaposto**, non vendor. Di questi dati sono credibili la
**forma** delle risposte in frequenza, i rapporti di guadagno, le impedenze
e i risultati in continua. **Non** lo sono le cifre di distorsione (assenti
di proposito) né quelle di rumore (escluse da questa directory), e i margini
di fase sono provvisori come detto sopra.


---

# L5b — punti di lavoro, escursione in continua, e la spazzata estesa

## Perché i file di Z_out e PSRR sono stati rifatti

Costruendo il dossier è emerso che **sei misure non venivano prodotte**:
`za100k` e `p100k` chiedono `find … at=100000` su una spazzata che
*finiva* a 100 kHz. `meas … find at=` interpola fra due punti, quindi sul
bordo ngspice rispondeva

```
Error: measure  za100k  find(AT) : out of interval
```

e il `print` che segue falliva a sua volta — trascinandosi dietro anche i
valori che erano stati calcolati bene. Il deck proseguiva e usciva 0,
quindi **dal codice di uscita il buco non si vedeva**.

La spazzata arriva ora a **200 kHz**, e i file qui sono stati rigenerati.

**Effetto collaterale, misurato e non assunto.** Con `dec 20 20 100k` la
spazzata copre 3,699 decadi: ngspice non usa un passo di 1/20 di decade e
poi si ferma, distribuisce 74 punti fra gli estremi, quindi il passo reale
era 0,0507 decadi. Con 200 kHz le decadi sono 4 esatte, i punti diventano
81 e il passo è esattamente 0,05. Quello che si è mosso:

| | prima | dopo | scarto |
|---|---|---|---|
| `z20` | 1693,41 Ω | 1693,41 Ω | identico (è il primo punto) |
| `z1k` | 58,8414 Ω | 58,7602 Ω | **−0,14%** |
| `z20k` | 48,0490 Ω | 48,0488 Ω | −4e-6 |
| `za20k` | 1,06873 Ω | 1,06866 Ω | −7e-5 |
| PSRR+ +10 dB a 10 kHz | 29,7747 dB | 29,7645 dB | −3e-4 |

Solo `z1k` si muove in modo visibile, e **non perché il circuito sia
cambiato**: 1 kHz non cade su un punto della griglia in nessuno dei due
casi, quindi `meas find at=1000` interpola, e i due vicini fra cui
interpola sono diversi. È la misura dell'errore di interpolazione di
`find at=` su una griglia da 20 punti/decade: circa 0,1%. Il valore nuovo
è il migliore dei due, perché la griglia è ora regolare.

Nessuna cifra già scritta altrove diventa falsa: tutte le altre variazioni
sono in quarta cifra significativa.

## Punti di lavoro — `tb_op.*`

Il CSV ha una riga sola e sei coppie `(scale, valore)`; lo *scale* di un
plot `op` non significa niente, i dati sono le colonne **dispari**:

| Colonna | Vettore |
|---|---|
| col1 | `v(OUT)` |
| col3 | `v(JACK)` |
| col5 | `v(FB)` |
| col7 | `v(SRC)` |
| col9 | `i(VPP)` |
| col11 | `i(VMM)` |

**La tabella dei punti di lavoro del dossier non viene però dal CSV**, ma
da `tb_op.log`: le correnti e le tensioni di ogni dispositivo sono
parametri di dispositivo (`@q106[ic]`, `@jq110[vgs]`) che il deck stampa e
che nel CSV non ci sono. Il log è versionato proprio per questo.

## Escursione in continua — `tb_dc_headroom*`

Due file, uno per modalità: `tb_dc_headroom.csv` è **0 dB** (relè aperto,
RRG = 1 GΩ), `tb_dc_headroom_10db.csv` è **+10 dB** (relè chiuso,
RRG = 0,1 Ω). Spazzata in continua di VIN da −14 a +14 V a passo 0,05 V,
561 punti.

| Colonna | Vettore |
|---|---|
| col0 | `v(IN)` [V] |
| col1 | `v(OUT)` |
| col3 | `v(D1N) − v(S1)` — V_DS del JFET non invertente |
| col5 | `v(D2N) − v(S2)` — V_DS del JFET invertente |
| col7 | `v(NX)` |
| col9 | `v(NY)` |

Le colonne pari sono `v(IN)` ripetuto.

**Cosa dicono, ed è un risultato di topologia.** Le due modalità **non
saturano allo stesso livello**: a guadagno unitario v(FB) insegue v(OUT),
quindi il modo comune visto dalla coppia d'ingresso sale insieme
all'uscita ed è lui a fermarsi per primo (uscita a **+9,37 V**); a +10 dB
v(FB) vale un terzo di v(OUT), il modo comune resta basso, e l'uscita
arriva a **+13,2 V**. Il ramo negativo è invece limitato dallo stadio
d'uscita e coincide quasi nelle due modalità. È una proprietà della
topologia; i valori esatti dipendono dal modello del JFET, che è
segnaposto.

---

## Carichi del Blocco A — `tb_blockA_carichi*`

Evidenza di **NC-010**, prodotta in **L5e** da
`spice/preamp/tb/tb_blockA_carichi.cir`.

**La domanda.** Il Blocco A pilota **tre carichi in parallelo** senza
isolamento reciproco (ADR-008): l'attenuatore da 10 kΩ e le due uscite
fisse, ciascuna 47 Ω + 4,7 µF + 470 kΩ di scarico. Se un apparecchio a
valle di una fissa si spegne e la sua impedenza d'ingresso crolla, cosa
succede al Blocco A? Non è una domanda ipotetica: **V1 elenca il Singxer
con «Zin ignota»** fra i carichi da coprire, e nessuna misura lo copriva.

Livello 2,7 V RMS a 1 kHz (E6, cioè 3,818 V di picco), Blocco A a
guadagno unitario. `RJ1` — l'impedenza a valle della fissa 1 — è spazzata
su sei valori; il nome del file porta il valore in ohm.

| File | Colonne |
|---|---|
| `tb_blockA_carichi_<RJ1>.csv` | col0 tempo [s] · col1 `I_C(Q134)` [A] · col3 `I_C(Q135)` [A] · col5 `v(OUT)` [V] |
| `tb_blockA_carichi_ac_<RJ1>.csv` | col0 frequenza [Hz] · col1 `vdb(OUT)` · col3 `vdb(J1)` |

Le colonne pari sono lo scale ripetuto. `Q134` è l'NPN d'uscita, `Q135` il
PNP: la sua I_C **esce**, quindi ha segno negativo. **Classe A ⟺
`I_C(Q134)` resta > 0 e `I_C(Q135)` resta < 0 per tutto il periodo**: se
uno dei due tocca lo zero, quel dispositivo si è interdetto e lo stadio
sta lavorando in Classe B.

### Il risultato, e c'è una soglia

| RJ1 | I_C(Q134) max | I_C(Q134) **min** | I_C(Q135) **max** | Regime |
|---|---|---|---|---|
| 470 kΩ (normale) | 14,759 mA | **14,352 mA** | −14,376 mA | **Classe A** |
| 10 kΩ | 14,943 mA | 14,167 mA | −14,194 mA | Classe A |
| 1 kΩ | 16,552 mA | 12,524 mA | −12,621 mA | Classe A |
| 100 Ω | 27,956 mA | **2,396 mA** | −2,569 mA | Classe A, ma il margine è quasi finito |
| 10 Ω | 57,258 mA | **−0,23 µA** | +0,26 µA | **Classe B** |
| 0,01 Ω | 65,456 mA | **−0,34 µA** | +0,42 µA | **Classe B** |

La soglia sta **fra 100 Ω e 10 Ω** di impedenza a valle. Il carico che lo
stadio vede è `RSEP + RJ1` in serie (47 Ω più l'impedenza a valle), quindi
il numero che conta per un vincolo di progetto è la **serie**: a ~147 Ω lo
stadio è ancora in Classe A col 16% della corrente di riposo come margine,
a ~57 Ω non lo è più.

Il picco a `RJ1 = 0,01 Ω` — **65,46 mA** — è lo stesso ordine dei
**65,07 mA** che NC-001 misura per il mute a 0 dB. Stessa causa fisica (un
carico da qualche decina di ohm sul nodo d'uscita), due vie
d'ingresso diverse: **il rimedio pensato per NC-001 non copre questa.**

### La metà che la misura NON conferma

L'osservazione da cui nasce questa voce aveva una seconda parte: che il
carico di un ramo **modula il segnale** che entra nell'attenuatore del
volume. I file `_ac_` la misurano, ed è **trascurabile**:

| Frequenza | Scarto di livello su `v(OUT)`, fissa 470 kΩ → in corto |
|---|---|
| 20 Hz | 0,000 dB |
| 1 kHz | **−0,0034 dB** |
| 20 kHz | −0,0056 dB |
| 100 kHz | −0,0166 dB |

L'anello chiuso del Blocco A tiene il nodo: il livello praticamente non si
muove. Va detto per intero, perché è la parte dell'osservazione che i dati
**non** sostengono.

Ma «il livello non si muove» non vuol dire «il ramo è innocuo», e la
distinzione è il punto: il danno non è sul livello, è sul **regime di
lavoro**. Una spazzata AC di piccolo segnale non può vedere la Classe B,
e la distorsione che ne deriva non è calcolabile da questa libreria di
modelli segnaposto. Quel numero arriverà coi modelli vendor (L6-L7).

### Come è stato verificato

Passo del transitorio **5 µs** su una finestra di 2 ms, dopo 3 ms di
assestamento: 401 righe per file. Confrontato con una run a 2 µs, i valori
coincidono fino alla quinta-sesta cifra (`q134max` 1,475863e-02 contro
1,475864e-02; nel caso estremo 6,545587e-02 contro 6,545345e-02, cioè la
quarta cifra).

Ogni numero della tabella qui sopra è stato **ricalcolato dal CSV
versionato** e confrontato con il `meas` che ngspice ha stampato da sé nel
`.log`: coincidono su tutte le cifre stampate. Sono le due strade
indipendenti verso lo stesso numero che il generatore del dossier pretende.
