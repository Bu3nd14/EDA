# 2026-10-10 — L51c, il dossier rigenerato: le schede di prova e la chiusura

**Documento datato: non si riscrive.** È la terza delle tre parti di L51 («Tre parti», l'utente
il 2026-10-09). Dati e comandi: `../data/2026-10-10/L51c/README.md`. Nessuna ADR nuova, nessuna
non conformità aperta o chiusa. Circuito, deck versionati e firmware non toccati. L'unica
eccezione sono due commenti di `psu.py`, autorizzati dall'utente.

## In breve

- **Il dossier è completo**: `PARTI = ("audio", "alimentatore", "schede")`. Il generatore
  scrive il primo `index.html` da L42: 206 KB, 28 sezioni più il contratto e le due appendici.
  La pagina autoconsistente fuori dal repo pesa 3,7 MB, il PDF A4 ha 50 pagine.
- **Sezioni nuove**: la distorsione (V4) sul blocco di oggi, e le schede di prova con
  l'assieme. **«Cosa questo dossier non dice»** è riscritta sul progetto di oggi. **La
  provenienza** copre ora anche l'alimentatore e le schede.
- **Quindici righe `Stato:`**, scelte dall'utente una per una: le dieci della lista, più cinque
  trovate rigenerando.
- **Sabotaggi 71 su 71**: i 15 nuovi, i 26 di L51a, i 29 di L51b e la pagina autoconsistente
  nel repo. Un difetto del generatore trovato così, e corretto.
- `run_tests.sh` 13 / 0.

## Le scelte dell'utente

All'inizio, coi numeri misurati prima:
- le schede di prova: **«Essenziale»**: per ciascuna il render 3D e il rame, più la pianta
  dell'assieme che ci sta; misure, DRC e vincoli in tabella, coi PDF vettoriali nominati;
- la DRC: **«Rifarlo oggi»**;
- la distorsione: **«Rifarla e mostrarla»**;
- i due commenti superati di `psu.py`: **«Sì, in questo lotto»**.

Le righe `Stato:`, una per una con la mia frase. Le richieste dell'utente lungo la strada:
- «la tua frase ha troppe referenze e acronimi, non é comprensibile facilmente rendila piú
  parlante» (il trim, ADR-027);
- «le soglie devo sempre essere in dB non in V» (la soglia del gradino, ADR-032: 100 µV
  diventano circa 33 dB SPL di picco a 1 m);
- «anche questa rendila piú chiara» (ADR-038), «non si capisce, rendila comprensibile»
  (ADR-062);
- sulle cinque in più: «il rele resta lo stato sicuro non é italiano, rivedi un po´ la frase»
  (ADR-012), «specifica meglio» (ADR-030), «anche qui non si capisce bene, fai meglio» (ADR-035).

Le frasi finali stanno in `../data/2026-10-10/L51c/script/stati.py`:
- **superate da ADR-062**: 038, 039, 040, 050, 061;
- **accettate con la riga riscritta**: 009, 012, 021, 027, 030, 032, 035, 036, 049, 062.

Le cinque in più (012, 021, 030, 035, 036) erano accettate e rimandavano al mute graduale. Due
dicevano il contrario di oggi:
- il relè di mute «non taglia mai la musica» (012);
- a mute inserito gli stadi d'uscita «non hanno più segnale» (021).

## La distorsione sul blocco di oggi

`gain_block.py` da L46b (5dc5c8b1) ha cambiato solo commenti, e il blocco rigenerato oggi dal
sorgente è uguale byte per byte a quello versionato. I banchi di L46b (blocco B nei tre modi,
sorgente 2,5 kΩ, carico 47 Ω + 4,7 µF + 10 kΩ) sono stati ricorsi sulla variante `oggi`, il
blocco senza modifiche.

| Clausola di V4 (ADR-055) | Tetto | Oggi, il peggiore sui tre modi |
|---|---|---|
| THD a 20 kHz, 0,2 V | 0,001 % | **0,000596 %** |
| armoniche dalla 5ª in su, 0,2 V | −140 dB | −192,6 dB |
| intermodulazione 19 + 20 kHz, 0,2 V | −110 dB | **−125,6 dB** |
| THD a 20 kHz, 2 V | 0,01 % | **0,0068 %** |

I controlli sono tre:
- la THD stampata da ngspice nel log contro la tabella di `leggi_four.py`, caso per caso;
- il blocco corso contro il `gain_block_flat.inc` di oggi, e i deck contro quelli di L46b;
- le 24 righe contro la variante scelta di L46b (`sv_r10_esr0_r120_226`): ampiezza, THD, h2, h3
  e i due prodotti d'intermodulazione sono **uguali alla cifra**. Cambiano solo il pavimento
  numerico e le armoniche sotto ~−190 dB, il fondo del metodo.

La pagina le dice **cifre di modello, sul blocco da solo**: il tetto di THD+N si fissa sul
prototipo. La nota «Leggere prima questo» non dice più «nessuna cifra di distorsione». La riga
V4 della tabella dei requisiti ha le cifre e i tetti, letti dalla tabella di V4 in
`REQUIREMENTS.md`.

## Le schede di prova

Dai dati di L49a e L49b. La DRC è rifatta oggi sulle copie (`run_drc.sh`, kicad-cli 10.0.6):
**0 / 0 su tutte e due**, come il 9 ottobre. Il generatore pretende che siano la stessa scheda,
la stessa versione e gli stessi conteggi. Le misure dai `measure.json` si incrociano coi
`placement.json` e con `assembly.json`, che deve avere la sola variante A che ci sta. I vincoli
per il pre-layout si leggono dai due report (7 + 10, numerati), non si riscrivono.

**Un dettaglio che la pagina dice com'è.** L49b scriveva che i 114 tratti ristretti
dell'alimentatore stanno «solo ai piedini fini». In `measure.json`, 45 di loro non toccano un
piedino a nessuna delle due estremità. Sono tutti ≤ 1,9 mm e attorno alle parti a passo fine.
La pagina riporta il conteggio e non interpreta.

## «Cosa questo dossier non dice», riscritta

Tolte:
- il rumore senza 1/f e la NC-004 bloccante: chiusa da L44;
- S del mute con la cima a 12 mA, l'autoriscaldamento di Q2, i LED delle LDR: non esistono più;
- i 265 mA per rail: oggi il carico è quello di `tb_op`;
- il commento di `C_VRELAY`: corretto;
- «Niente distorsione».

Dentro, ogni cifra letta dai dati:
- la distorsione di modello;
- il rumore 1/f al tetto di ADR-057;
- V1 agli spigoli di resistenze e condensatori non misurato. La dispersione di I_DSS sì, in
  L46b: ≥ 65,16°;
- le forme d'onda non versionate;
- il relè dell'interblocco dichiarato;
- l'alimentatore coi modelli dichiarati. Al posto del micro, le uscite del firmware vero
  iterate fino al punto fisso. Niente PSRR né rumore dei regolatori (NC-011);
- il carico della scheda audio dichiarato;
- il calore stimato, col ferro dei trasformatori come unica ipotesi (1,95 W);
- le schede di prova che non sono il layout;
- `main_attiny.c` non scritto, e nessun falso sul circuito dopo L41b2;
- nessuno giudica come suona.

## I due commenti di `psu.py`

`C_RAW` dice ora la valle di oggi: **17,89 V** a rete −10 % (L41a: 18,05). `C_VRELAY` dice ora
la tenuta di oggi: **48,3 / 121,7 / 195,4 ms** (prima 61,1 senza il selettore). Le fonti sono in
`data/2026-10-09/L51b/rete/analisi.csv`. `psu.net` rigenerata: cambiano solo la data e i numeri
di riga di SKiDL. ERC 24 / 2 come prima.

## Trovati e corretti nel generatore

- **`stessi_byte()` si rompeva su un file mancante.** Il sabotaggio di L51a che rinomina il
  relè del selettore, rieseguito con l'alimentatore nella pagina, faceva fallire anche il
  generatore del deck di V2 dell'alimentatore. Il dossier cadeva in un `FileNotFoundError`
  invece di rifiutare. L51b non l'aveva visto perché non rieseguiva i sabotaggi di L51a. Ora
  rifiuta come `stesso_deck()`.
- **Il trasformatore T1 era un link al requisito T1** (classe A pura) nella frase dell'assieme:
  il nome letto da `assembly.json` ora è marcato come parte.
- **Rimosse** `fig_mute.svg` e `fig_ldr_drive.svg`: nessuna sezione le usa più.
- La V3 diceva che il `.four` «con questi modelli è priva di significato»: ora dice che è presa
  in saturazione, e che la distorsione si giudica nella sua sezione.

## Non fatto

- L'architetto avversariale (**L52**) e il gate (**G1**).
- Le immagini del rame hanno molto bianco attorno: sono i PNG di L49 com'erano, e i PDF
  vettoriali sono nominati accanto.
