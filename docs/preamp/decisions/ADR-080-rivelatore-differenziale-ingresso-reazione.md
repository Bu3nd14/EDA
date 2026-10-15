# ADR-080 — Il rivelatore di continua guarda la differenza fra l'ingresso e la reazione di ogni blocco, non la sua uscita

Data: 2026-10-15 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Supera in parte ADR-079**: la presa sulle sei uscite (F1, F2 e B per canale) e la ragione «la
  musica non lo fa scattare». Restano di ADR-079: la persistenza fuori da una finestra, l'alimentazione
  dal maggiore fra VPLUS e VRELAY, la linea `DC_FLT` su J4 pin 4 coi tre gate in hardware, la ritenuta
  nel firmware, l'inibizione all'accensione.
- **Lascia ADR-072 com'è**: che cosa fa il rivelatore quando scatta non cambia. La reazione a due tempi
  (NC-066) è una domanda aperta, non decisa qui.
- **Non tocca P10 né PR-30**: il limite resta 100 ms sopra 0,87 V.

## Contesto

La revisione avversariale di L59 (`reports/2026-10-15-L59-architetto-avversariale.md`) ha trovato
due difetti del rivelatore sulle uscite, opposti fra loro e con la stessa causa: il rivelatore vede
insieme il guasto e il segnale.
- **Con la musica sopra può non scattare** (NC-064). Il temporizzatore riparte a ogni rientro nella
  finestra: un avvallamento del basso ogni 63–82 ms tiene fuori P10 un guasto da +1,93 V su una fissa,
  ~0,88 s a calcolo. I 762 guasti di L45d2b1 erano tutti in silenzio.
- **Sotto la banda scatta su ingressi sani** (NC-065). Sulle fisse, a qualunque volume,
  un'ondulazione del disco fra 1 e 5 Hz da 0,4–1,35 V di picco, o una sorgente che si accende con
  0,65 V di continua, lo fanno scattare, e l'apparecchio si spegne fino al frontale.

Nessuna soglia e nessun tempo sulla sola uscita li risolve entrambi: in ~95 ms un segnale a 1 Hz e
la continua sono la stessa forma d'onda, e la media di un basso a 20 Hz da 4 V di picco su 85 ms
lascia fino a ~0,8 V (esiti di L59).

## Decisione

1. **La presa è differenziale.** Per ogni blocco il rivelatore confronta l'ingresso non invertente
   con il nodo di reazione (o, dove il guadagno è 1, l'ingresso con l'uscita). In un blocco sano la
   differenza è l'errore dell'anello, µV in banda, qualunque cosa passi.
2. **Subito sui buffer delle fisse e sul blocco d'uscita**:
   - F1 e F2: l'uscita del blocco A contro l'uscita del buffer, due nodi a bassa impedenza;
   - B: l'ingresso (dal cursore del volume, ≤ 2,5 kΩ) contro la reazione; la soglia tiene conto del
     guadagno, fino a 3,152 (a +10 dB l'errore vale un terzo della continua in uscita).
3. **Sul blocco d'ingresso (A) si decide in L60, dopo la prova** di corrente di presa, rumore e fronti
   dei comparatori al gate d'ingresso. Se non regge, A resta visto come oggi attraverso F1 e F2.
4. **Il resto di ADR-079 resta**: i comparatori, la persistenza, la linea, i gate, la ritenuta.
5. **Analogico, in hardware.** Il micro non entra nella protezione (PR-24).

Le parole dell'utente (2026-10-15), alla domanda sulla direzione: «Differenziale analogico, A dopo».

## Perché

- **Toglie i due difetti alla radice invece di scambiarli.** La musica, l'ondulazione e la continua
  di una sorgente arrivano uguali sull'ingresso e sulla reazione di un blocco sano, quindi non
  arrivano al confronto: il temporizzatore non riparte sul basso (NC-064) e non parte
  sull'ondulazione (NC-065). Un guasto che sbilancia l'anello resta fuori finestra in modo fisso.
- **P10 resta com'è**, senza curva a tempo inverso, e il contratto resta senza filtri (PR-19): il
  phono non ha bisogno di un filtro subsonico per il rivelatore.
- **Il principio della persistenza regge** (R7 di L59): è quello del brevetto Zenith US 4,301,330
  (B. Trump, 1981), zona morta e temporizzatore che riparte. Le sue debolezze note sono proprio il
  mascheramento e l'ondulazione, che la presa differenziale toglie.
- **Il costo si concentra in un punto solo**, il gate d'ingresso del blocco A (320 kΩ verso massa in
  continua: ogni 0,1 µA di presa sono 32 mV in uscita), ed è lì che la decisione resta aperta.

## Alternative scartate

- **Il rivelatore di oggi con il limite firmato** dall'utente: lascia NC-064 e NC-065 bloccanti.
- **Due rami (veloce sopra una soglia alta, lento e filtrato sotto) e un filtro subsonico del 3°
  ordine a ~12 Hz sul phono** (proposta dall'utente col Technics SU-9070 come esempio, e dal
  revisore, R1 (a)): P10 diventa una curva da firmare, il filtro tocca PR-19, i guasti sotto i 2 V
  restano fino a ~0,9 s al clip del finale, e l'ondulazione sugli ingressi linea resta.
- **Un passa-basso prima della finestra, con una persistenza più corta** (R1 (b)): attenua la musica
  che fa ripartire il temporizzatore, ma non l'ondulazione; va rifatto contro il clip asimmetrico di
  B.
- **Un rivelatore digitale** (domanda dell'utente; la proposta di un altro modello,
  `data/2026-10-15/L59/proposta-altro-modello.md`): stessa informazione, la presa sul gate più
  difficile (il campionatore vuole un buffer), la protezione nel firmware contro PR-24, prese
  analogiche attraverso J4. La derivata dell'altro modello porta un guasto con la musica a 1500 ms.
- **Una finestra lunga che ricorda il passato** (idea dell'utente): aiuta sull'ondulazione già in
  corso, non sulla puntina appena appoggiata né sul guasto durante un'ondulazione.

## Da riaprire se

- In L60 il banco con la musica mostra che il rivelatore di oggi **non** è mascherato (NC-064 non
  confermata) e l'ondulazione stimata resta sotto la finestra: la presa sulle uscite torna in gioco.
- L'errore di un blocco sano ad alta frequenza o al clip esce dalla finestra per più di T_HOLD su un
  segnale che il preamp deve far passare (E6).
- Un guasto che il differenziale non vede (il nodo d'ingresso che si sposta, le parti dopo il blocco,
  i corti della scelta 9) resta fuori P10.
- Sul blocco A la presa costa rumore o fronti misurabili rispetto a E3 / E5, e A non è coperto
  abbastanza attraverso F1 e F2.
