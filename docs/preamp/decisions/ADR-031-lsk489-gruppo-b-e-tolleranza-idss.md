# ADR-031 — Il JFET d'ingresso è l'LSK489B, e il progetto tollera l'intera finestra di I_DSS del gruppo B

Data: 2026-09-15 · Stato: accettata

## Contesto

ADR-013 sceglie l'LSK489 senza dirne il gruppo. Il sorgente dichiara
`value="LSK489B"` da L10 (`circuits/preamp/gain_block.py`), senza che un
documento lo abbia deciso. Il datasheet RevA40 (pag. 2) separa per gruppo la
sola I_DSS:
- **A**: 2,5 / 5,5 / 8,5 mA;
- **B**: 8,0 / 11,5 / 15,0 mA;
- V_GS(off) −1,5 … −3,5 V per entrambi.

Il modello del costruttore si chiama `LSK489A` e descrive un esemplare d'angolo:
I_DSS 2,593 mA (NC-013). NC-013 chiedeva quale dispersione il progetto tolleri.
In L20 all'utente è stato chiesto su quale finestra scriverla.

## Decisione

1. **Il JFET d'ingresso è l'LSK489 del gruppo B.** Parole dell'utente: «Solo B,
   il gruppo del sorgente».
2. **Il progetto tollera l'intera finestra B, I_DSS 8,0–15,0 mA** (V_DG = 15 V,
   V_GS = 0, 25 °C), con il criterio sotto. È misurato a 8,0 · 11,5 · 15,0 mA.
3. **Nessun valore del circuito cambia.**

| Criterio | Soglia | Peggiore nel gruppo B, misurato |
|---|---|---|
| Coppia in saturazione su tutto il modo comune di E6 (±3,82 V, 0 dB) | (V_D − V_G) − \|V_P\| > 0 | **2,415 V**, 15 mA, a +3,82 V |
| Gate in inversa a riposo | I_G < 0 | −10,3 … −11,2 pA |
| Q106 in zona attiva su tutto il modo comune | V_CE > 1 V | 11,40 V |
| Classe A: coda, cascode, VAS e uscita | entro lo 0,5 % del modello com'è | 0,15 %, la coda |
| E5, i cinque casi di `tb_noise_breakdown` | ≤ √(10² − 1²) = 9,95 µV (ADR-020) | **4,308 µV**, +10 dB, 2,5 kΩ |
| V1, blocco B a 0 dB, caso peggiore di L27/L16 | ≥ 60° | **62,708°**; nella stessa cella il gruppo varia di ≤ 0,104° |
| Offset in uscita | **nessuna soglia**: è di L29 (NC-028) | −17,280 … −17,300 mV |

La soglia dello 0,5 % sulla classe A è una **lettura del lotto**, non un numero
di un requisito. Dice che il punto di lavoro di P7 e di L11 non si sposta.

## Perché

**La coda impone la corrente, quindi I_DSS sposta solo V_GS.** Q106 fissa
4,37 mA, cioè 2,2 mA per metà. Una volta fissata I_D, gm = 2√(β·I_D) non dipende
da `Vto`. Dai dati di L20 (27 °C, 0 dB), da 2,59 a 14,93 mA di I_DSS:

| | a 2,59 mA (modello com'è) | a 14,93 mA (B massimo) | variazione |
|---|---|---|---|
| I_D di una metà | 2,21091 mA | 2,21272 mA | 1,8 µA |
| gm | 4,4958 mS | 4,4805 mS | −0,34 % |
| V_GS | −0,146 V | −1,988 V | 1,84 V |
| v(SRC) | −0,141 V | +1,701 V | 1,84 V |
| offset v(OUT) | −17,261 mV | −17,300 mV | 0,039 mV |
| rumore D | 4,3033 µV | 4,3076 µV | +0,004 µV |

**Ciò che si consuma è il margine a modo comune alto.** Il nodo di sorgente sale
con |V_GS|. Il margine di saturazione a +3,82 V scende da 4,26 V (2,59 mA) a
**2,42 V** (15 mA). Resta positivo con 2,4 V di scorta: è la riga del criterio da
guardare se cambia qualcosa a monte.

**V1 dipende dal modello, non da I_DSS.** Il passaggio dal segnaposto al modello
del costruttore alza il minimo del blocco B da 61,803° a 62,508°. Fra 2,59 e
15 mA la stessa cella si muove al più di 0,32°.

**Anche fuori dalla finestra B il criterio passa**: a 2,59 mA (il modello com'è)
e a 5,5 mA (il tipico A). Non si scrive come requisito, perché l'utente ha
scelto B. Dice però che la dipendenza da I_DSS non è ciò che limita il progetto.

## Costo accettato

- **Nessun modello del costruttore esiste per il gruppo B.** Le cifre B sono
  l'`LSK489A` con `Vto` −2,086 / −2,557 / −2,976 V e `Beta` 2,2m invariato, come
  NC-013 prescriveva. È un'ipotesi a un parametro, non un esemplare B misurato.
  - Va detto accanto a ogni cifra B (V4).
  - Per T7 il modello del costruttore della parte resta l'`LSK489A` (ADR-013).
- **Il `Beta` di un esemplare B non è vincolato.** Il datasheet dà solo un minimo
  di Gfs, 1,5 mS, e il criterio non è provato con un `Beta` diverso. Il
  ragionamento su gm dice che conta poco, ma è un ragionamento.
- **Il gruppo B non è verificato contro T8.** ADR-013 cita 921 pezzi su DigiKey
  senza dire il gruppo; L20 non ha letto disponibilità né ciclo di vita del
  gruppo B.
- Misurato a 27 °C, come ogni deck del repo. I 60 °C del telaio (ADR-021) non
  sono stati simulati.

## Alternative scartate

- **Solo il gruppo A**, cioè la finestra del modello: il sorgente nomina B, e
  l'utente ha scelto B.
- **A e B insieme** (2,5–15 mA): non scelta dall'utente. I punti A restano nei
  dati come riferimento.
- **Un `Vto` ritoccato in `models/jfet/lsk489.lib`**, o un modello «LSK489B» in
  un file nuovo. Il primo cancella la traccia della trascrizione (NC-013); il
  secondo non è un modello del costruttore, e `provenance()` lo rifiuta.

## Da riaprire se

- **Il costruttore pubblica un modello del gruppo B**, o un `Beta` diverso per
  il B. Si rieseguono `spice/preamp/tb/tb_idss_op_noise.cir` e
  `tb_idss_loop.cir` con quello.
- **La corrente di coda, il cascode o il nodo di sorgente cambiano** in
  `gain_block.py`: si rimisura il margine di saturazione a 15 mA.
- **Il livello di modo comune cresce** (E6 più alto, o un guadagno a monte del
  blocco B) e il margine a 15 mA scende sotto 1 V.
- **Il gruppo B risulta a fine vita o non ordinabile** (T8).
- **La Fase 4 (NC-017)** sostituisce gli altri modelli e un minimo di V1 si
  avvicina a 60° di meno di 0,5°. La dispersione di 0,32° va rimisurata sul
  circuito nuovo, e con il buffer delle fisse e il blocco A.

Precisa **ADR-013** sul gruppo, senza superarla.
