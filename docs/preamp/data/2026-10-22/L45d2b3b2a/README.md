# L45d2b3b2a — il calore dei guasti del blocco: lo stato dopo, i rimedi, la scelta (2026-10-22)

Prima parte di **L45d2b3b2** (diviso dall'utente all'inizio, «Due parti»: a lo stato dopo, i rimedi
misurati e la scelta; b il sorgente e le verifiche). Report
`../../../reports/2026-10-22-L45d2b3b2a-calore-guasti-blocco.md`. Decisione **ADR-099**; NC-042 avanza.
**Il circuito non cambia**: i rimedi sono varianti testuali del blocco generato. `<L>` = questa
cartella. Python con `/usr/bin/python3 -I`.

## Il banco, e il suo caso noto

`script/genera.py` importa `genera_calore.py` di L45d2b3b1 (e attraverso lui L62b e il canale di
L45a: rail ideali a ±15 V, le tre uscite, il guasto a 0,3 s, 2,3 s, le potenze medie degli ultimi
10 ms) e punta qui i percorsi. Le copie guaste si riscrivono dal blocco della variante (limitations
#62). Una corsa dura ~4 s e pesa ~50 MB: R120 in corto, il caso lento di #75, non è fra i quindici.

| Variante | Che cosa | Esito |
|---|---|---|
| `b1` | il blocco su cui L45d2b3b1 ha corso i quindici (prima di ADR-097, R153 da 4,7 kΩ): IL CASO NOTO | `confronta_b1.py`: **5920 celle, 0 diverse** contro `calore_oggi.csv` e `analisi_jack_oggi.csv` di b1 |
| `oggi` | il blocco di oggi (R153 + R160): la base | 15 su 15 oltre i limiti, come b1 (`sintesi_oggi.csv`) |

`script/sintesi.py` è `sintesi_calore.py` di b1 per una variante qualsiasi, più la corrente in eccesso sui
rail e il verdetto («oltre P7, sotto 150 °C»). `analizza_calore.py` di b1 divide il nome della cartella
al primo «_»: la sintesi ricompone la posizione (le varianti `d_…`).

## Lo stato dopo (`sintesi_d_*.csv`, `sintesi_d2*.csv`)

La parte che il guasto porta oltre i limiti si rompe: aperta (la riga tolta, 1 GΩ a massa su ogni suo
nodo) o in corto collettore-emettitore (1 mΩ), da t = 0 nella copia guasta; il guasto di partenza a 0,3 s.

| Primo guasto | Parte bruciata | Aperta | In corto |
|---|---|---|---|
| R149 cc, Q121A be / ae, R119 ap | Q148 | entro | lo specchio Q121 a 493–577 °C; con R149 in corto le 20 Ω della cella a **45 W** |
| R107 cc, Q106 ce | Q148 | Q117 132 °C, Q106 127 °C, R136 0,35 W | Q121 565–577 °C |
| D102 / D103 ap | Q148 | il carico del VAS Q125 211 °C → (2° giro) aperto: Q117 122 °C; in corto: Q122 236 °C | Q121 493 °C |
| Q148 ce | Q121 (le due metà) | entro | Q121 631 °C, Q146 207 °C, R123 5,2 W |
| Q133 ce, Q125 ce | Q122 | entro | il finale NPN 309 °C, R123 5,8 W |
| R126 cc | Q125 | entro | Q122 274 °C → (2° giro) aperto: entro; in corto: il finale NPN 185 °C, R123 8,2 W |
| R101 cc | D102 (il primo che si apre) | R107 1,46 W, R126 3,52 W → (2° giro, aperte): entro | (tutti e due in corto: il rail − a massa, un guasto dell'alimentatore) |

Q121B base-emettitore in corto (Q148 149 °C) e Q132 in corto (Q133 149 °C) restano sotto i 150 °C
assoluti: non si rompono, e non sono qui.

## I rimedi (`sintesi_<v>.csv`, `regressione/misure_<v>.csv`, `p7_<v>.csv`)

Varianti in `script/genera.py`, `RIMEDI`; sigle nuove da 161. Ognuna sui 15 modi, rif e i modi delle sue
parti nuove, nelle cinque posizioni; la regressione dei 21 deck veloci con gli include puntati alla
variante (`prepara_regressione.py`, `regressione.sh`); P7 dalla tabella del deck, con R123 / R126 al
valore della variante e le parti nuove misurate (`p7_confronto.py`).

| Variante | Parti | Oltre i limiti | Il blocco sano |
|---|---|---|---|
| `rc148` | 10 kΩ collettore di Q148 → V− | 9 (chiude i 6 di Q148 e dello specchio) | margine −0,2°, PSRR −0,4 dB |
| `sdopp` | R101, R107, R126 in due; D102 / D103 doppi | 10 | **sposta il punto di lavoro**: finali −3 %, Q121A Vbc −40 → −95 mV |
| `vaslim` | R123 33 + 22 Ω, MMBT5401 sulla base del VAS | 11 (chiude il VAS) | margine +0,3…+0,8° |
| `tutti` | le tre | 3 | come `sdopp` |
| `coda` | 1 kΩ collettore di Q106 | 13 | (non in regressione: è dentro `rv2`) |
| **`rv2`** | `rc148` + `vaslim` + `coda` + R101 in due | **2** (i corti dei finali) | margine 43,1 → 43,6°, PSRR ±0,34 dB, rumore ≤ 0,006 %, P7 non peggiora |

- **`rv2` coi dispositivi a 60 °C** (`script/caldo.py`, `sintesi_rv2t60.csv`): il VAS 123 → 119 °C nei
  quattro guasti che lo limitano.
- **A riposo, a caldo** (`script/op_caldo.py`, `op_caldo.csv`): Q168 0,06 / 0,9 / 7,5 µA a 27 / 60 / 90 °C;
  il VAS e la continua d'uscita uguali a oggi entro 3 µA e 0,04 mV.
- **Le parti nuove nei guasti** (`script/nuove_max.py`, `nuove_max_rv2.csv`): R169 **0,236 W** con R107 in
  corto (→ ≥ 0,5 W in distinta), le altre ≤ 0,089 W, Q168 ≤ 69 °C.
- **I finali col dissipatore** (`script/dissipatore.py`, `dissipatore.csv`): Ohmite WA-T220-101E, 20 °C/W
  a 1 W (la curva del costruttore), 2,5 °C/W giunzione-case (onsemi), 2 °C/W d'interfaccia (ipotesi):
  i corti dei finali 160 / 149 → **99 / 95 °C**, P7 85 → 70 °C, riposo 79 → 67 °C. L'avviso di fine
  produzione del datasheet Ohmite riguarda solo il modello DT2; DigiKey il 2026-10-22: «Active».

Le misure dei log della regressione (`misure_<v>.csv`) hanno ~150 righe di `pq121a` «da una parte sola»
in `tb_mute_corto`: i due log ne hanno 600 ciascuno, è il contatore delle occorrenze che si sfasa
(#37). P7 si legge dalla tabella CSV del deck, non dai log.

## Rifare

```sh
/usr/bin/python3 -I <L>/script/genera.py noto
/bin/zsh <L>/script/corri.sh <L>/deck/lista_noto.txt 6
/bin/zsh <L>/script/corri.sh <L>/deck/lista_oggi.txt 6
/usr/bin/python3 -I <L>/script/analizza.py b1 oggi
/usr/bin/python3 -I <L>/script/confronta_b1.py
/usr/bin/python3 -I <L>/script/genera.py dopo
/bin/zsh <L>/script/corri.sh <L>/deck/lista_dopo.txt 6
/usr/bin/python3 -I <L>/script/genera.py dopo2
/bin/zsh <L>/script/corri.sh <L>/deck/lista_dopo2.txt 6
/usr/bin/python3 -I <L>/script/genera.py rimedi rc148 sdopp vaslim tutti
/bin/zsh <L>/script/corri.sh <L>/deck/lista_rimedi_rc148_sdopp_vaslim_tutti.txt 6
/usr/bin/python3 -I <L>/script/genera.py rimedi coda rv2
/bin/zsh <L>/script/corri.sh <L>/deck/lista_rimedi_coda_rv2.txt 6
/usr/bin/python3 -I <L>/script/analizza.py d_Q148ap d_Q148cc d_Q121ap d_Q121cc d_Q122ap d_Q122cc d_Q125ap d_Q125cc d_D102ap d2Q148apQ125ap d2Q148apQ125cc d2Q125ccQ122ap d2Q125ccQ122cc d2D102apR107ap rc148 sdopp vaslim tutti coda rv2
/usr/bin/python3 -I <L>/script/sintesi.py oggi rc148 sdopp vaslim tutti coda rv2
/usr/bin/python3 -I <L>/script/caldo.py rv2 60 D102_ap D103_ap Q125_ce R126_cc Q133_ce Q132_ce
/bin/zsh <L>/script/corri.sh <L>/deck/lista_rv2t60.txt 6
/usr/bin/python3 -I <L>/script/analizza.py rv2t60 ; /usr/bin/python3 -I <L>/script/sintesi.py rv2t60
/usr/bin/python3 -I <L>/script/prepara_regressione.py oggi rc148 sdopp vaslim tutti rv2
/bin/zsh <L>/script/regressione.sh oggi      # e rc148, sdopp, vaslim, tutti, rv2, uno alla volta
/usr/bin/python3 -I <L>/script/confronta_regressione.py rc148 sdopp vaslim tutti rv2
/usr/bin/python3 -I <L>/script/p7_confronto.py oggi rv2
/usr/bin/python3 -I <L>/script/op_caldo.py ; /bin/zsh <L>/script/corri.sh <L>/deck/lista_op_caldo.txt 6 ; /usr/bin/python3 -I <L>/script/op_caldo.py leggi
/usr/bin/python3 -I <L>/script/nuove_max.py rv2
/usr/bin/python3 -I <L>/script/dissipatore.py
```

`run/` (le corse) e le forme d'onda grandi della regressione non stanno nel repository: si rifanno.
