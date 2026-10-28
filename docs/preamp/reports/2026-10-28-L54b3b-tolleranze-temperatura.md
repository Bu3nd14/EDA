# L54b3b — le tolleranze e la temperatura del temporizzatore (2026-10-28)

Seconda parte di L54b3, il punto 7 del prompt di L54b («la robustezza del temporizzatore, al banco e non
al prototipo»): le tolleranze e la temperatura. Dati, criteri, metodo e comandi:
`data/2026-10-28/L54b3b/README.md`. Decisione: **ADR-105**.

## In breve

- **Il banco**: `--temp`, `--toll` (un fattore per R / C, VREF, lo scostamento di ognuno dei diciotto
  canali di comparatore e la loro corrente d'ingresso, `CMPTAV`), `--perdita` (la perdita massima del
  datasheet di un diodo), i gruppi di hFE della ritenuta. Senza opzioni i deck di L54b3a riga per riga;
  ogni opzione provata su un caso di cui si sapeva la risposta (R571 × 1,1 → +9,7 %).
- **Il Monte Carlo a 25 °C**, 700 corse, i condensatori in C0G: nessun verdetto diverso dal nominale; il
  margine più stretto la musica dopo un buco di 20 ms, 532 ms (≥ 500). La regressione lineare dei margini
  (residui ≤ 0,75 ms) dà il segno di ogni parametro: **gli angoli peggiori**, corsi a 0 / 25 / 60 °C alle
  tre reti con la perdita massima dei diodi alla temperatura.
- **Tre prove fallite**, ognuna portata all'utente coi numeri:
  1. **a 60 °C la ritenuta scatta all'accensione a freddo col frontale acceso**, anche coi valori
     nominali: la perdita massima di D534 (BAT54, ~19 µA) nel nodo d'innesco porta la base di Q513 a
     0,88 V. **«Solo D534 a bassa perdita»**: 0,27 V, 0,31 V nell'angolo col comparatore da 2,2 V;
  2. **a 0 °C la musica dopo un buco di 20 ms** nell'angolo peggiore a 491 ms: **«R571 a 1,1 MΩ»**,
     537 ms; la musica all'accensione dal frontale +60 ms (1209 ms);
  3. **in X7R** C548 porterebbe la musica sotto i 400 ms e C551 / C529 K501 a 43 ms dopo il permissivo
     (≥ 50): **«Tutti C0G»**, i dieci condensatori dei ritardi.
- **Sul sorgente di ADR-105**: i 69 angoli passano tutti (il minimo: la musica dopo il buco 537,1 ms, il
  permissivo 31,4 ms, K501 63,8 ms, la base 0,311 V); la lista della sicurezza ha gli stessi verdetti a
  0 / 25 / 60 °C e a 25 °C gli istanti di sicurezza di L54b3a; i gruppi di hFE A / C come il B; il
  controllo numerico a 5 µs identico.
- Il «Da riaprire se» di ADR-104 sui BAT54 rimasti **scatta** (D534) ed è chiuso; quello sulla musica
  dopo il buco scatta a 0 °C ed è chiuso; quello di ADR-103 sulla base all'accensione **non scatta**.
- **Nessuna non conformità aperta o chiusa**: 17 aperte, 1 bloccante. `run_tests.sh` alla chiusura.

## 1. Il metodo

I parametri sono uniformi sul loro intervallo (gli estremi probabili quanto il centro; un massimo di
datasheet non è una sigma). La regressione lineare dei margini sui parametri normalizzati è quasi
esatta (i tempi sono RC per un logaritmo): il suo segno costruisce, per ogni criterio, l'angolo che lo
peggiora, coi valori dell'intervallo della temperatura e del dielettrico. L'angolo si **corre**: il
modello è lineare, il circuito no. La temperatura entra nei modelli a giunzione del costruttore
(`.options temp`) e, per le parti comportamentali, negli intervalli (la deriva dello scostamento, il
coefficiente dell'LM4040, delle R, dei condensatori); la perdita dei diodi al massimo del datasheet
alla temperatura, sommata a quella del modello (per eccesso, dichiarato).

## 2. Le prove fallite e le scelte

Le tabelle sono in ADR-105 («Perché») e nel README («Gli esiti»). La diagnosi della ritenuta a 60 °C ha
separato temperatura e perdita: senza perdite aggiunte la base è a 0,372 V; con la sola perdita massima
dei tre BAT54 0,883 V; la stessa perdita a 25 °C 0,538 V senza scatto (la VBE più alta). Il rimedio sui
tre BAT54 toglie lo scatto ma accorcia la musica dopo il buco a 461 ms (D533 lascia AT_PG più alto con la
rete mancante): il solo D534 basta.

## 3. Cosa resta fuori, e dove va

- **A 60 °C la musica dopo il rilascio del tasto del mute** a 7,7 ms invece di 18,1 (la perdita massima
  di D537 nel filtro dei rimbalzi): i rimbalzi veri (1–5 ms) restano coperti; nel «Da riaprire se» di
  ADR-105.
- **La conferma del BAS416 e dei C0G da 1 µF in 1206 alla distinta**: L58.
- **Al prototipo**: i disturbi irradiati, le perdite superficiali della scheda sui nodi da megaohm e su
  AT_F / AT_MD, la perdita vera dei pezzi comprati.
- Il prossimo lotto: **L55** (il dispositivo d'uscita), poi L58, L64, L65, G1.
