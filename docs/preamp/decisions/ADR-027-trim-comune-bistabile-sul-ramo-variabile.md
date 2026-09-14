# ADR-027 — Il trim è uno solo, sul ramo dell'uscita variabile, a relè bistabili, con LED e interblocco dal mute

Data: 2026-09-14 · Stato: accettata

## Contesto

**ADR-011** voleva un partitore **a ponticello su ogni ingresso**, prima del
buffer. **ADR-019** gli ha aggiunto l'interblocco elettrico col mute (F8).
**ADR-015** lo rende portante: col K11 a fondo scala il +10 dB ha 0,58 dB di
margine senza trim.

Il 2026-09-14 l'utente ha deciso in tre passi, parole esatte in NC-023:
1. «rele», «trim per ingresso (meglio se possibile coi bistabili)»;
2. all'apertura di L16: «Credo sia meglio avere un guadagno comune per tutti gli
   ingressi, quindi Trim a valle della selezione, ma con un´indicazione a LED del
   guadagno selezionato». Discussi i costi, ha scelto i **LED presi dallo stato
   vero dei relè**;
3. dopo le prime misure: «le fisse come copia fedele della sorgente, é quello che
   deve fare un´uscita fissa bufferizzata, il TRIM riguarda solo il guadagno
   dell´uscita Variabile».

Il terzo passo nasce da una misura. **Nessun partitore passivo all'ingresso del
blocco A rispetta E3 ed E5 insieme.** Nella cella +10 dB, attenuatore al massimo,
trim a −6 dB il rumore al jack vale:

| Scala | Zin DC | Rumore al jack |
|---|---|---|
| nessun trim | — | 4,77 µV |
| 54,9 k / 29,4 k / 28,7 k | 101,5 kΩ | **10,60 µV** |
| 50 k / 25 k / 25 k, la più piccola possibile (già sotto E3) | 97,6 kΩ | **10,12 µV** |

Il limite è 9,90 µV (ADR-020, ADR-022). A −6 dB il blocco A vede almeno 25 kΩ di
Thévenin: è fisica, non una scelta di valori. E3 cadeva inoltre con 10–47 pF di
capacità del selettore (`data/2026-09-14/L16/esplorazione/`).

## Decisione

**1. Un solo trim, 0 / −6 / −12 dB, fra l'uscita del blocco A e l'attenuatore.**
- I buffer delle uscite fisse prendono l'uscita del blocco A **prima** del trim:
  sono una copia fedele della sorgente.
- Il trim regola soltanto l'uscita variabile.
- Scala per canale, a bassa impedenza: **845 Ω – 464 Ω – 464 Ω**.

**2. Due relè bistabili sul segnale, Omron G6KU-2F-Y**, a singolo avvolgimento,
un polo per canale come ADR-026:
- **K7 (T1)**: a reset l'attenuatore sta sull'uscita del blocco A, cioè
  **0 dB**; a set sta sul COM di K8;
- **K8 (T2)**: a reset sta sul nodo −6 dB, a set sul −12 dB.

Reset = 0 dB è lo stato in cui la parte esce di fabbrica.

**3. LED dallo stato vero (F9).**
- Due G6KU-2F-Y spia, **K9 e K10**, con la bobina in parallelo a K7 e K8.
- I loro contatti accendono uno di tre LED.
- Nessun LED dalla posizione del comando: fuori mute il comando può non
  corrispondere allo stato.

**4. Comando e interblocco (F8, NC-023).**
- Il comando è un commutatore rotativo a 4 poli e 3 posizioni (SW1, a
  pannello). Ogni coppia di poli fa da ponte H di contatti su una coppia di
  bobine, fra `VTRIM` e `RLY_RET`.
- `VTRIM` arriva da `VRELAY` attraverso **i due contatti NC in serie di K6**,
  un G6K-2F-Y monostabile con la bobina su `MUTE_CMD` accanto a K2–K4.
- Fuori mute K6 è eccitato: `VTRIM` è morta, il comando non muove niente, e i
  bistabili tengono lo stato senza corrente.
- In mute le bobine sono pilotate di continuo verso la posizione del comando.
- Ritorno di bobine e LED su `RLY_RET`, non sulla massa audio.

**5. Stato all'accensione: la posizione del comando.**
- L'apparecchio si accende in mute (ADR-012), quindi il trim viene portato al
  comando prima del rilascio.
- Vincolo consegnato a `psu-engineer`: il mute si rilascia **non prima di
  10 ms + 3 ms** (impulso minimo più tempo di set) da quando `VRELAY` è
  valida.

## Perché

**Le misure** (`data/2026-09-14/L16/dopo/`, deck versionati):

| Grandezza | Esito |
|---|---|
| Attenuazione, col carico dell'attenuatore | **−6,003 / −11,939 dB** |
| **E3**, min \|Zin\| su 20 Hz–20 kHz | 1,00 MΩ; **121,1 kΩ con 68 pF** di selettore; identica nelle tre posizioni |
| **E5**, catena completa | nessuna cella sopra la catena senza trim: **4,92 µV** al peggio (+10 dB, attenuatore al massimo, phono). A −6 dB 3,73–3,84 µV |
| **V1 blocco B**, sorgente massima (10 k + 442 Ω)/4 = 2,611 kΩ | 0 dB **61,803°**, agli spigoli **61,422°**; +3 dB 69,773° / 68,644°; +10 dB 102,980°. Costo del trim: 0,027° |
| **V1 blocco A**, col partitore, cablaggio ≤ 1 nF | **63,495°** al peggio (0 dB, phono), senza trim 63,363° |
| **Headroom NC-009** (metrica M1, report) | a +10 dB **+6,58 dB** col trim a −6 dB; +0,58 dB a 0 dB |

**Il relè.**
- Pinout del G6KU-2F-Y letto su tre gambe indipendenti che concordano, sulle
  revisioni 11 e 16 del datasheet: a reset sono chiusi 3–2 e 6–7, il set vuole
  il pin 1 positivo.
- Stessa forma del G6K-2F-Y, compresa la trappola di NC-014.
- **T8**: il catalogo **K106-E1-16** (03/2026, `vendor/relays/omron/G6K-K106-E1-16/`)
  lo elenca ordinabile da 3 a 24 VDC. La pagina Omron degli avvisi di fine
  produzione **non è stata letta**, e la lacuna è dichiarata. T7 non si applica:
  non è un dispositivo attivo.

**Bistabili e alimentazione continua in mute.**
- Il valore resta all'uscita dal mute senza corrente (F8).
- Non ci sono cariche immagazzinate: fuori mute l'unico nodo flottante, `VTRIM`,
  non ha sorgenti, quindi niente percorsi parassiti. Questo è un ragionamento;
  la prova sulla netlist è il 2e.
- **Il 2e prova l'interblocco sulla netlist** (raggiungibilità da `VRELAY` in
  ogni stato dei relè di guadagno), e lo si è fatto fallire su netlist generate
  con il contatto sbagliato.

**Budget delle bobine** (5 V; 21,1 mA per bobina anche per il G6KU):
- fuori mute sei monostabili, **126,6 mA**;
- in mute K1, K5 e quattro bistabili, **126,6 mA** più circa 2 mA di LED.

## Alternative scartate

- **Trim per ingresso** (8 relè; ADR-011, prima decisione): nessun modo di vedere
  i valori impostati. Superato dall'utente.
- **Trim all'ingresso del blocco A**: E5 violata per struttura, tabella sopra.
- **Trim dopo il blocco A ma prima dei buffer**: le fisse avrebbero seguito il
  trim. Scartato dall'utente.
- **Monostabili alimentati attraverso il mute**: perdono il valore uscendo dal
  mute (F8). **Monostabili con una memoria di stato**: è logica, sotto ADR-022,
  e non serve dove un bistabile basta.
- **LED dalla posizione del comando**: fuori mute può mentire.
- **Impulsi a condensatore o pulsanti** al posto del ponte H: non valutati con
  misure. Il ponte a commutatore rotativo non ammette posizioni contemporanee
  per costruzione, e non accumula carica.

## Cosa supera

- **Supera ADR-011** nel «per ingresso», nel «a ponticello» e nel «prima del
  buffer». Resta il perché del trim (tre passi, 0 / −6 / −12 dB) e il suo peso
  per l'headroom.
- **Precisa ADR-019 §2**: il permissivo è un relè sul comando del mute, perché i
  poli dei relè di mute portano tutti segnale.
- **Precisa ADR-026**: il budget delle bobine.

## Da riaprire se

- **La pagina Omron** degli avvisi di fine produzione, o un catalogo successivo,
  segna il G6KU-2F-Y a fine vita (T8).
- **La bobina di K6 si interrompe**: il trim diventerebbe comandabile fuori mute,
  in silenzio. Se il prototipo o l'analisi dei guasti lo rendono rilevante, serve
  un permissivo che fallisca chiuso.
- **Il mute tenuto a lungo** scalda le bobine dei bistabili oltre quanto il
  datasheet ammette: must set a 60 °C circa l'80 % della nominale, «max
  estimated».
- **`VRELAY`** viene scelta diversa da 5 V: si ridimensiona la resistenza dei LED.
- **L'utente** vuole il trim anche sulle fisse, o un valore per ingresso.
