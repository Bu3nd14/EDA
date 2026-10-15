# ADR-079 — Il rivelatore di continua com'è costruito: la persistenza fuori da una finestra, una linea in più fra le schede, la ritenuta nel firmware

Data: 2026-10-14 · Stato: accettata — la presa sulle uscite e «la musica non lo fa scattare» sono superate da ADR-080 (la presa differenziale, L59)

**Rapporti con le decisioni precedenti.**
- **Realizza ADR-072** (L45d2b1). Non la riapre: dei suoi «Da riaprire se» non ne scatta nessuno.
  - La soglia separa la continua dalla musica entro 100 ms (sotto, «Perché»).
  - I rail scendono in tempo: R144 resta sopra 1 W per 158 ms.
  - Il rivelatore cieco resta a L58.
- **Tocca J4**: il pin 4 nuovo. Fino a L45d2a J4 aveva tre pin (ADR-045, ADR-028).
- **Tocca il firmware**: PA1, libero da L47c1 (ADR-062), e una sequenza nuova, la 4.9 della specifica
  del temporizzatore.
- **Lascia il resto ai suoi lotti.**
  - La partenza morbida dei regolatori, trovata qui, è **NC-063**.
  - Il rivelatore cieco è di **L58**.
  - Il micro (L54) e NC-046 restano dove sono.

## Contesto

ADR-072 ha deciso che cosa fa il rivelatore: apre il mute, toglie la linea dei relè, spegne i rail
audio. Ha lasciato a L45d2b la soglia, la costante di tempo e la prova. Costruendolo sono venute
fuori tre cose che ADR-072 non poteva sapere.
1. **Un filtro passa-basso non basta.** Il jack è accoppiato in alternata (τ ~1 s a vuoto), quindi
   già ~0,95 V di continua all'uscita di un blocco lo tengono sopra 0,87 V per più di 100 ms. Fra i
   148 guasti di L45b fuori da P10, 15 finiscono sotto 1 V di continua e 57 sotto 2 V. Un filtro
   da 1 a 4 poli, abbastanza pronto da vedere 0,95 V entro ~95 ms, scatta anche sul primo
   semiperiodo di un basso a 20 Hz da 14 V (`data/2026-10-14/L45d2b1/studio/`).
2. **«La strada che esiste già» non tiene spento l'apparecchio.** Il rivelatore stacca il
   toroidale, i rail scendono e il rivelatore perde l'alimentazione e rilascia. Per il firmware è un
   buco di rete senza causa (classe 1) e poi un rail sceso, cioè l'accensione rifatta (spec 4.5):
   il toroidale torna, il guasto fa scattare di nuovo il rivelatore, e così via.
3. **La scelta 8** vuole il rivelatore vivo col filo del rail + aperto fra le schede, quindi non
   può vivere dei soli rail audio.

## Decisione

1. **La persistenza.** Per ognuna delle sei uscite (F1, F2 e B per canale; A si vede attraverso F1
   e F2) c'è una finestra a ±0,58 V (0,39–0,66 V agli angoli) e un temporizzatore che riparte da
   zero ogni volta che l'uscita rientra. Il rivelatore scatta se l'uscita resta fuori dallo stesso
   lato per **T_HOLD = 71,6 ms** (62,7–81,6 ms).
2. **L'alimentazione.** Il rivelatore sta fra **VDP = il maggiore fra VPLUS e VRELAY** e la massa,
   senza rail negativo. Ogni uscita arriva ai comparatori spostata a VDP / 2 da un partitore allo
   0,1 %, e **una 634 kΩ dall'uscita a VMINUS** toglie la corrente che lo spostamento vi mette
   (+0,18 µA netti coi due rail, invece di 24 µA).
3. **Una linea in più fra le schede**, `DC_FLT` su **J4 pin 4**: un collettore aperto verso
   RLY_RET.
   - Sull'alimentatore tre BAT54 tirano giù `MUTE_G`, `VR_G` e `MAINS_G`, **in hardware**.
   - Il pull-up è di 10 kΩ a V5.
4. **La ritenuta nel firmware.** PA1 legge la linea. Bassa per ≥ 2 ms **con l'alimentazione buona**
   porta a GUASTO, che dura fino al frontale.
5. **Un'inibizione all'accensione** di ~0,1 s (1,43 MΩ × 100 nF × ln 2), dal momento in cui VDP
   compare.

I valori stanno in `circuits/preamp/dc_detector.py`, ognuno con la sua ragione. Il dimensionamento
è in `data/2026-10-14/L45d2b1/scelte/dimensiona.py`.

## Perché

- **La musica non lo fa scattare.** Nella banda di E9 un segnale periodico passa per zero almeno
  ogni 50 ms, e T_HOLD minimo è 62,7 ms: niente scatta sopra i 16 Hz.
  - Sul banco del canale, con B a +10 dB, nessuno degli 11 segnali di prova lo fa scattare: seni a
    20 Hz fino al clip, quadra, impulsi al 90 %, un periodo isolato, 1 kHz e 5 kHz al clip 2,3 dB
    oltre E6.
  - Il margine minimo è degli impulsi a 20 Hz: TMAX a 5,3 V contro lo scatto a ~7,2 V.
- **Il taglio arriva in tempo.**
  - A calcolo, nel caso peggiore, ≤ 86,2 ms dal guasto per ogni continua da 0,81 V in su.
  - Sul banco dei guasti del blocco, 762 corse in sette posizioni (A, F1, F2, B, B a +10 dB, e i
    due condensatori d'uscita in corto della scelta 9), **nessun guasto fuori da P10**.
  - Senza rivelatore ne uscivano 45–53 per posizione. Il peggiore ora è 90,0 ms, lo scatto tipico a
    73 ms (`data/2026-10-14/L45d2b1/banco/guasti.md`).
- **La scelta 8 e il suo simmetrico.**
  - Il filo del + aperto fra le schede: scatta a 221–223 ms, il jack resta sopra 0,87 V ≤ 73 ms.
  - Il filo del − aperto: scatta a 451–460 ms, il jack ≤ 60 ms.
  - I rail della scheda scendono piano, e il jack non passa il tetto prima.
- **La catena in hardware sul banco dell'alimentatore**, col firmware al punto fisso:
  - il mute subito (i relè dei jack si staccano in ≤ 3 ms);
  - K501 aperto a 3,5 ms;
  - `VRELAY` sotto 6 V a 19,7 ms, dopo i jack;
  - VPLUS sotto 13,5 V a 92 ms e sotto 1 V a ~0,8 s;
  - GUASTO a 2 ms, la rete giù a 82 ms, l'apparecchio spento col frontale ancora acceso.
- **La scelta 10.** Con C145 in corto (R144, 10 Ω, sul rail +) il rail cede subito, e il
  sorvegliante muta già da sé. Il rivelatore anticipa lo stacco del toroidale da 106 a 75 ms.

  | | Col rivelatore | Senza |
  |---|---|---|
  | Energia in R144 | 1,14 J | 1,37 J |
  | Tempo sopra 1 W | 158 ms | 191 ms |
  | Picco | 22,5 W | 22,5 W |

  Il calore finisce con la scarica dei rail. Se R144 lo regge è una domanda sulla parte, alla
  distinta (G2), non sul tempo.
- **La ritenuta nel firmware e non in hardware**:
  - GUASTO esiste già, ed esce solo col frontale come dopo un guasto dell'alimentatore, come chiede
    ADR-072;
  - la sicurezza resta in hardware (PR-24): mute, linea dei relè e toroidale li stacca il
    rivelatore da solo;
  - con il micro in reset le uscite sono in alta impedenza e `MAINS_REQ` è tirato giù: il
    toroidale resta staccato comunque.
  - La linea conta solo con l'alimentazione buona: con la rete che manca i rail scendono e il
    rivelatore può scattare durante la discesa. È un buco di 4.5, che riparte da solo, non un guasto
    da frontale (test `guasto_dc`, falso 34).

## Alternative scartate

- **Un filtro passa-basso** (1–4 poli, 10–70 ms): o è lento sulla continua bassa, o scatta
  sull'attacco del basso.
- **Un filtro d'ingresso da 3,5 ms** (la prima stesura): mediava il clip asimmetrico di B a 1 kHz,
  −1,1 V di media, e scattava dopo 325 ms di clip pesante.
- **Il rivelatore sui soli rail audio**: cieco proprio al filo del + aperto (scelta 8).
- **Lo spostamento senza compensazione** (la prima stesura): spingeva 24 µA in ogni uscita. In un
  blocco col guasto che toglie la spinta all'uscita (Q106 in corto base-emettitore, ~150 kΩ) la
  portava da −0,81 a +2,9 V. L'uscita passava per zero, il temporizzatore ripartiva e P10 saliva
  sul principale da 66 a 122 ms: il rivelatore cambiava il guasto che doveva vedere.
- **Le prese dopo il condensatore d'uscita**: vedrebbero solo il transitorio, e non il caso della
  scelta 9.
- **La ritenuta in hardware** (un latch sui 5 V azzerato dal frontale): più parti, per rifare quello
  che il firmware fa già.
- **Nessuna inibizione all'accensione**: mentre i rail salgono le uscite fisse vanno a +1,4…+4 V
  per 30–50 ms. Si sono viste anche soglie e ingressi coi ritardi diversi, una svista della prima
  stesura corretta con costanti di tempo uguali.

## Limiti dichiarati

- Un segnale **sotto i 16 Hz** che resti oltre ~0,6 V su un'uscita può farlo scattare, per esempio
  un disco ondulato a volume massimo attraverso il futuro stadio phono.
- Per ~0,1 s dall'accensione non scatta. L'inibizione è dimensionata sui rail del banco: rail in
  31 ms, jack 179 ms dopo. Con le partenze morbide dei datasheet scatterebbe a 0,79 s, ed è
  **NC-063**.
- Con un firmware vivo ma sbagliato (un secondo guasto) l'apparecchio può riaccendersi e riscattare
  in ciclo.
- Il modello del comparatore è **comportamentale**: quello del costruttore non gira in ngspice.

## Da riaprire se

- Chiusa NC-063, le rampe vere dei rail superano l'inibizione: si ridimensiona R_POR / C_POR sul
  banco della scheda audio (`genera_rivelatore.py accensione`).
- Una sorgente, o lo stadio phono, porta sotto i 16 Hz più di ~0,5 V a un'uscita.
- La diagnosi (L58) o il riesame del micro (L54) tolgono PA1 o il micro.
- NC-046 fissa un tetto sulle fisse che il rivelatore deve guardare (come in ADR-078).
