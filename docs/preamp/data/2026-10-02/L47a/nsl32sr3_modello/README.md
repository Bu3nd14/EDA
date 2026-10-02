# nsl32sr3_modello — il modello comportamentale della cella del mute (L47a, ADR-058)

Generato e verificato il 2026-10-02. Ogni cifra ricavata da
`models/optocoupler/nsl32sr3_comportamentale.lib` porta l'etichetta «modello comportamentale da
dati pubblicati, una sola cella misurata nella regione del mute, con estrapolazione dichiarata».

| File | Cosa fa |
|---|---|
| `digit.py` | legge a pixel il grafico «Photocell Resistance vs. LED Current» (Silonex Rev 07) |
| `genera_modello.py` | le fonti, le ipotesi e la composizione; scrive il `.lib`. **Il `.lib` non si edita a mano** |
| `verifica_statica.py` | nodi, buio, massimo a 20 mA, inviluppo dei 61 pezzi; un processo ngspice per punto |
| `verifica_dinamica.py` | salita, discesa e buio a 10 s sulla curva B, con le definizioni del costruttore |
| `sabotaggi.py` | quattro copie alterate del `.lib`: ognuna deve far fallire una verifica |

Le fonti: `vendor/optocoupler/silonex/NSL-32SR3/` (il grafico), `vendor/optocoupler/luna/NSL-32SR3/`
e `vendor/optocoupler/advanced_photonix/NSL-32SR3/` (le tabelle), `../fonti/` (le misure di
JC Maillet, con `fonte.txt`).

```sh
# il ritaglio che digit.py legge (fuori dal repo)
/opt/homebrew/bin/pdftoppm -r 300 -png <repo>/vendor/optocoupler/silonex/NSL-32SR3/nsl-32sr3-silonex-rev07.pdf <tmp>/sr3_rev07
sips -c 1100 1300 --cropOffset 1000 1250 <tmp>/sr3_rev07-1.png --out <tmp>/sr3_chart.png
sips -s format bmp <tmp>/sr3_chart.png --out <tmp>/sr3_chart.bmp
/usr/bin/python3 digit.py <tmp>/sr3_chart.bmp

/usr/bin/python3 genera_modello.py        # rigenera il .lib
/usr/bin/python3 verifica_statica.py      # esce col numero di controlli falliti
/usr/bin/python3 verifica_dinamica.py
/usr/bin/python3 sabotaggi.py             # esce col numero di sabotaggi non rilevati
```

## Esito (2026-10-02)

- **Lettura a pixel** (griglia: 109 px per decade di resistenza, 260 per decade di corrente). I
  cinque punti marcati:

  | Corrente | Resistenza |
  |---|---|
  | 0,101 mA | 2095 Ω |
  | 0,974 mA | 300 Ω |
  | 9,82 mA | 82,7 Ω |
  | 19,6 mA | 62,8 Ω |
  | 38,3 mA | 48,8 Ω |

  Il grafico a 5 mA dà ~120 Ω, la tabella dello stesso foglio 150 tipici: si segue il grafico.
- **Composizione.**
  - La cella di Maillet sta 1,456 volte sotto il tipico Silonex a 0,131 mA: la sua forma si
    scala di tanto.
  - Fattori dell'inviluppo rispetto alla tipica: al buio (10 µA) 0,252–1,404, accesa (2 mA)
    0,513–1,439.
  - I fattori alti scendono a 0,962 a 20 mA, per i 60 Ω massimi del costruttore.
- **Statica: 84 controlli su 84.**
  - I 70 nodi delle curve A–E entro lo 0,05 %.
  - 25 MΩ al buio su ogni curva, a 10 nA e a 1 nA.
  - C ed E a 60,0 Ω a 20 mA. B, la tipica del grafico, ne dà 62,4: è il grafico del
    costruttore, e si stampa senza giudicarlo.
  - L'inviluppo copre esattamente 103–289 Ω a 2 mA e 16–89 kΩ a 10 µA.
- **Dinamica, curva B: 5 punti su 5 entro il 3 %.**
  - Salita: R a 5 ms 191,25 Ω contro 191,26 (63 % della conduttanza finale).
  - Discesa: 99,8 kΩ 10 ms dopo lo spegnimento da 5 mA.
  - Buio: 24,98 MΩ a 10 s.
  - τ di salita 1,526 ms; discesa a 292 decadi/s fino a 100 kΩ, poi 0,238 decadi/s.
- **Sabotaggi: 4 su 4 rilevati.**
  - un nodo della curva B a 10 µA spostato di +0,1 decadi (statica);
  - τ di salita +30 % (dinamica);
  - il tasso di discesa fino a 100 kΩ −20 % (dinamica);
  - il tasso di coda −20 % (dinamica).

## Tre trappole trovate qui

1. **Il solo diodo per i 2,5 V massimi a 20 mA non converge.**
   - Con N = 2 serviva IS ≈ 2·10⁻²³. A 10 nA il punto di lavoro falliva (gmin, source stepping).
   - Poi il «transient op» finiva «successfully» con l'anodo a 0,2 V e la corrente del LED
     nella CIO: una resistenza negativa, senza errore (limitations #33).
   - Ora è il diodo della VTL5C4 più 42,5 Ω in serie.
2. **Con `abstol=1e-15` e 1 mV sulla cella** (le opzioni della verifica di L29b) l'op dipende dal
   percorso di Newton.
   - Al buio falliva a 7,30, 7,3979 e 7,45 decadi e convergeva a 7,35, 7,39, 7,40.
   - Con un'induttanza di 10¹² H fra stato e bersaglio (provata e tolta) falliva invece alle
     correnti basse, e il «transient op» lasciava lo stato a 7,38 decadi contro 4,80.
   - Con le opzioni dei banchi veri (`reltol=1e-6 vntol=1e-6 abstol=1e-12`, come
     `tb_v2_casopeggiore.cir`) e 1 V sulla cella converge ovunque, senza l'induttanza.
   - L'intestazione del `.lib` lo dichiara: **un banco con `abstol` più stretto va guardato nel
     log.**
3. **Il gmin stepping che finisce «completed» stampa prima «Dynamic gmin stepping failed».**
   - Cercare «failed» nell'output scarta un op valido.
   - Le verifiche cercano «Transient op» e l'assenza del risultato.
