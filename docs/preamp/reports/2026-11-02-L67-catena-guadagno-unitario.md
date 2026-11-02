# L67 — La distorsione delle istanze a guadagno unitario sulla catena (2026-11-02)

Chiude **NC-055** (maggiore, prima di G1). Decisione **ADR-112**. Dati `data/2026-11-02/L67/` (README,
con la sezione «Rifare»). Il circuito non cambia.

## Il banco e i casi noti

Il banco della catena di L56 (selettore, blocco A, le due fisse, trim a 0 dB, C_T, bilanciamento al
centro, volume, blocco B; carico di V4 su ogni jack) e quello della sorgente di L56, copiati col blocco
come argomento. Per il caldo si usano i blocchi di L66 (`v4caldo.py`, passo 4, finali col dissipatore,
VAS e carico in SOT-223), avvolti in un subckt; il blocco di oggi e `lim365` di L66 differiscono solo
per una riga di commento. Prima di leggere un numero nuovo:
- **la catena di L56 sul blocco di allora** (git 369f2aad2): **224 celle su 224**, salvo una h5+ della
  fissa 1 a −187,5 contro −187,6 dB, rumore numerico 47 dB sotto il tetto. I due casi fuori a
  0,001334 / 0,001059 %, come L56;
- **la sorgente di L56 sul blocco di allora**: 80 celle su 80;
- **il blocco caldo dentro un subckt**: il deck di L66 com'è ridà `sintesi_caldo.csv` di L66 (0,000695 /
  0,00705 % e 0,000725 / 0,00734 %), e lo stesso deck col blocco avvolto dà le stesse 48 THD;
- **il blocco di oggi avvolto** contro `gain_block.subckt`: 336 celle su 336.

## 1. Il punto di lavoro della catena (limitations #86)

Col blocco di oggi a 27 °C l'op della catena non convergeva in **nessuno dei 68 casi**: gmin e source
stepping falliti, poi il «Transient op» di ngspice, che esce coi condensatori grossi scarichi. In un
caso di prova, a fine corsa ogni blocco aveva VPF a **4,9 V** invece di 14,8, il +15 V dava **4,05 A**
(1 A per blocco nella cella RC da 10 Ω, C145 in carica con τ 10 ms), e la principale usciva a pochi µV.
Il blocco di L56 nella stessa catena converge sempre, e così il blocco di oggi da solo o a 57 °C. Il
controllo del livello al jack l'ha fermato. Il rimedio: `.nodeset` per ogni istanza dall'op del blocco
da solo (VPF 14,84 V, NX +1,02, NY −1,00 V, come il blocco sano di L66). Dopo, **0 casi non conversi** in
tutti e sette i blocchi; la catena di L56 coi nodeset ridà le sue cifre.

Una seconda trappola, più piccola: il volume a −10 dB esatti (6837,72 / 3162,28 Ω) col modo +10 a 2 V
non convergeva nemmeno da solo; a 6,8 / 3,2 kΩ (−9,9 dB) converge al primo passo. `m10` usa questi valori.

## 2. La sorgente (`sintesi_rs.csv`)

Il blocco a guadagno unitario con la sorgente a 0 / 1,5 / 2,5 / 5,6 kΩ, nei tre modi, a 27 e 57 °C
uniformi e nei quattro blocchi caldi: **60 su 60 dentro**, margine minimo **2,7 dB** (5,6 kΩ, aria a
57 °C, 2 V: 0,00734 % contro 0,01). Le cifre a temperatura uniforme sono quelle di L56 alla quarta
cifra. La crescita con l'impedenza di sorgente resta monotona, senza minimo a R_F.

## 3. La catena con V4 letto alla lettera (`sintesi_catena.csv`, `catena_*.csv`)

| Condizione | Griglia di L56 (56) | Peggiore | Volume a −10 / −20 dB (28) | Peggiore |
|---|---|---|---|---|
| oggi, 27 °C | 2 fuori | 0,001334 %, −2,5 dB | 9 fuori | 0,004785 %, −13,6 dB |
| aria 27 °C, rame / minima | 2 fuori | 0,001337 %, −2,5 dB | 9 fuori | 0,004796 %, −13,6 dB |
| aria 57 °C, rame / minima | **3 fuori** | 0,001427 %, −3,1 dB | 10 fuori | 0,005125 %, −14,2 dB |

- Fuori c'è solo la **principale**, a 20 kHz e 0,2 V. Le **fisse** sono tutte dentro, margine ≥ 2,5 dB;
  la h5+ è ≤ −149,7 dB ovunque.
- I cambi del blocco da L56 (ADR-097, ADR-099, ADR-111) non spostano la catena: 0,001334 % identico.
- A caldo si aggiunge il volume a metà con la sorgente da 1,5 Ω, a −0,3 dB.
- **Il meccanismo è quello di L53.** La seconda armonica del blocco A cresce col suo livello e si somma
  a quella del blocco B, che col volume a metà vede ~2,5 kΩ. Col volume basso la principale a 0,2 V
  porta il blocco A a 0,63–2 V, e la sua distorsione passa attenuata insieme alla fondamentale.
- **In SPL**: seconda armonica di un tono a 20 kHz, quindi a 40 kHz; con la fondamentale a ~99 dB SPL a
  1 m, sta a ~2 dB SPL col volume a metà e ~13 dB SPL nel caso peggiore.

## 4. L'intermodulazione sulla catena (`imd_catena.csv`)

Il CCIF di V4 (19 + 20 kHz, picco composto di 0,2 V alla principale, il prodotto a 1 kHz) sulla catena,
il metodo del banco del blocco, su oggi e sui caldi a 27 e 57 °C, quattro volumi, due sorgenti, tre
modi: **0 su 78 fuori**, margine minimo **10,8 dB**, il prodotto ≤ −28 dB SPL a 1 m. Alla principale il
prodotto resta fra −121 e −139 dB anche col volume in cima, dove la fissa 1 dà −137…−141 dB: è
probabilmente un pavimento del metodo dovuto a C_T da 10 µF, che sta solo sul percorso della principale.
È quindi un limite superiore, e non cambia il verdetto.

## 5. Le opzioni, coi numeri

Presentate all'utente coi numeri dei punti 2–4:
- **ogni blocco al suo livello** (raccomandata): una regola nuova per la catena, nessun costo sugli altri
  requisiti;
- **V4 invariato e i casi accettati per nome**: lo stesso circuito, ma una regola che col volume basso
  vorrebbe il blocco A ~14 dB migliore a 2 V;
- **il cascode pilotato** sulle istanze a guadagno unitario: ~3 dB (volume a metà) e ~14 dB (volume
  basso) da trovare, topologia cambiata prima di G1, costo su margine di fase, rumore e calore non
  misurato;
- **NC-055 aperta fino al prototipo**: bloccava G1.

R_F adattata non è fra le opzioni: il minimo della THD a R_S = R_F che la giustificava non c'è.

**Decisione dell'utente: «Ogni blocco al suo livello»** (ADR-112). La THD a 20 kHz si giudica al livello
a cui lavora ciascuna istanza, con tetto(L) = 0,001 % × L / 0,2 V (ridà 0,001 % a 0,2 V e 0,01 % a 2 V),
e la principale contro il livello più alto lungo il percorso.

## 6. La verifica con la regola (`verifica_livello.csv`)

| Condizione | Griglia di L56 (28 a 20 kHz) | Volume basso (14 a 20 kHz) |
|---|---|---|
| oggi e aria 27 °C | 0 fuori (prima 2), margine ≥ 2,5 dB | 0 fuori (prima 9), margine ≥ 1,9 dB |
| aria 57 °C | 0 fuori (prima 3), margine ≥ 1,9 dB | 0 fuori (prima 10), margine ≥ 1,3 dB |

Il margine minimo di 1,3 dB è un caso a 2 V alla principale (modo +10, volume a −10 dB, 2,5 kΩ:
0,0086 % contro 0,01 %), già dentro con V4 letto alla lettera. `REQUIREMENTS.md` (V4) porta la regola.
NC-055 è chiusa. Cifre di modello: la verifica sul prototipo resta, come per ogni cifra di V4.

## Errori di questo lotto

- **I casi del volume basso mescolati alla griglia di L56.** La prima versione del banco li metteva
  negli stessi deck: avrebbe cambiato l'ordine delle corse e il punto di partenza dei casi di L56 che
  venivano dopo, e il caso noto non sarebbe più stato lo stesso banco. Corretto prima di leggere le
  cifre: deck a parte (`_vb`), e i deck della griglia di L56 uguali a quelli di L56 salvo titolo e
  include.
- **Il livello del blocco A moltiplicato per il guadagno del modo.** Il modo agisce sul blocco B, non su
  A: corretto nel lettore prima della sintesi.
- **Il primo lettore non guardava la convergenza dell'op.** La catena morta col blocco di oggi l'ha
  fermata il controllo del livello, non un controllo dell'op. Ora il lettore rifiuta anche «source
  stepping failed» (limitations #86).
