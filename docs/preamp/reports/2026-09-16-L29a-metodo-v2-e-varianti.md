# L29a — il metodo di V2 reso misurabile, e il confronto delle varianti di mute (2026-09-16)

Lotto **L29a**, ripresa della sessione sospesa il 2026-09-15. Registra
**ADR-035**. **NC-028 resta aperta e bloccante.** Dati:
`data/2026-09-16/L29a/`; i dati parziali di ieri restano sotto
`data/2026-09-15/L29a/`, sono di quella esecuzione.

**Provenienza dei modelli**, letta dagli `.include`: l'unico modello del
costruttore è l'**LS352** (`models/bjt_pnp/ls350.lib`); l'LSK489 è `LSK489X`,
segnaposto con `KF = 0`; ogni altro dispositivo è un segnaposto (**NC-017**).
Il **pavimento di C dipende dalla distorsione di questi modelli**, quindi è
una cifra provvisoria: è la ragione per cui la soglia di C, in ADR-035, è
dichiarata provvisoria.

## 1. Il metodo di V2 non separava i casi che L29 incontra

Il mandato di L29 dice: «se il metodo non separa i casi che L29 incontra, lo si
dice all'utente, non lo si aggiusta in silenzio». Prima di misurare qualunque
variante, tre cose — verificate sui dati di ieri, non riprese sulla fiducia.

### 1.1 C, com'era scritto, non lo passa nessun circuito reale

C sottraeva la sola fondamentale su una finestra di 10 ms, quindi **la
distorsione di regime restava per sempre nel residuo**. Su una corsa **mai in
mute** — nessun evento da misurare — al jack principale:

| | |
|---|---|
| Seconda armonica da sola | **887 µV** (`2026-09-15/L29a/esplorazione/armt_main.txt`) |
| Pavimento completo di C, 1 kHz | **1,23 mV** principale, **188 µV** fisse |
| a 20 kHz | **21,9 mV** |
| a 20 Hz | **167 µV** |
| a 0 dB invece che +10 dB | **184 µV** — sopra soglia anche lì |

Non è un difetto dei modelli segnaposto: qualunque stadio a discreti in classe A
a 12 V di picco ha una h2 ben sopra lo 0,0008 % che servirebbe per stare sotto
100 µV. **Nessun circuito reale può passare C a 100 µV.**

### 1.2 Il resto del pavimento è numerico, e non scende

Tolte h2..h20 restano **390 µV** sulla principale e **124 µV** sulle fisse:
rapporto **3,15**, cioè esattamente il rapporto di guadagno. Due spiegazioni
sono state **falsificate**:

- **non è il ricampionamento dello strumento**: l'autotest T7 lo misura a
  **4,4 µV** a 12 V e 1 kHz con passi da 10 µs, 280 volte sotto;
- **non è la precisione di scrittura**: quella darebbe fra le uscite un rapporto
  di 10 (il passo di quantizzazione cambia per decade), non di 3,15.

Un `reltol` diecimila volte più stretto muove il residuo solo da **112 a
87 µV RMS**, e il suo spettro **non ha righe** (la più alta è 2,6 µV,
`esplorazione/spettro_main_r7.txt`). Un tono puro in un circuito deterministico
può produrre **solo** armoniche, quindi il resto è numerico per necessità — ma
**non è attribuito**, e nessuna manopola del solutore provata lo abbassa in modo
utile. Resta una domanda aperta.

### 1.3 Nessuna dissolvenza di durata pratica passa C

Il residuo del fit scende solo come **1/T**: a 1 kHz una rampa **lineare da 10 s**
lascia ancora **1,5 mV** (`strumento/caratterizza_C_960.txt`). Non dipende dalla
parità della finestra: 960 e 961 campioni danno le stesse cifre. La frase di V2
«una dissolvenza più lenta di 10 ms resta nel tono ricostruito» **non è vera al
livello di 100 µV**.

## 2. Le risposte dell'utente, e ADR-035

Portate all'utente il 2026-09-16 con le cifre sopra. Le sue decisioni:

| | |
|---|---|
| Soglia di **C** | **1 mV**; **A e B restano 100 µV** |
| Verdetto di **C** | **C2, la differenza dal riferimento**; C1 e le armoniche diagnostiche |
| Solutore | **trap**, `gear` rifiutato |
| Deck graduale | **rampa da 3 s** aggiunta a 20 ms / 200 ms / 1 s |

**Un'interpretazione, dichiarata.** Una differenza *cruda* `v_ev − v_rif`
respingerebbe **ogni** mute, anche uno infinitamente lento: il mute toglie per
forza volt di musica, e quel residuo sta alla frequenza del tono, non a 1/T,
quindi il passa-alto a 20 Hz non lo tocca — è il problema che il fit di ADR-032
esisteva per evitare. La forma adottata è la **differenza dei residui del fit**:

```
C2(t) = [v_ev(t) − tono_fit,ev(t)] − [v_rif(t) − tono_fit,rif(t)]
```

La distorsione di regime, identica nelle due corse, si cancella; una dissolvenza
lenta resta dentro il fit e passa; un taglio netto sopravvive e cade.
**Non serve fittare le armoniche dentro C2**: la differenza dal riferimento
cancella *ogni* contenuto di regime, non le prime venti armoniche soltanto.

## 3. Il difetto che rendeva i deck non eseguibili

**Trovato in questa sessione, e spiega perché ieri varianti e graduale erano
rimasti «fermati».**

I tre deck portavano `.options reltol=1e-6 vntol=1e-9 abstol=1e-15`. Dove il
jack sta vicino a zero — cioè in **ogni cella senza segnale a mute inserito** —
un `vntol` da 1 nV domina il controllo del passo del transitorio: il passo
collassa e non risale. Non ci sono errori di convergenza nel log: sono passi
minuscoli, non tentativi falliti.

| Cella `var0_100k_lz` | |
|---|---|
| Avanzamento con `vntol=1e-9` | **2,71 ms di transitorio ogni 100 s di calcolo** |
| Estrapolato alla cella intera | **~41 ore**, per **una** cella su 87 |
| Con `vntol=1e-6 abstol=1e-12` | **5,5 s** |

Le celle **con** segnale non ne soffrivano, perché lì `reltol × |v|`
(1e-6 × 12 V = 12 µV) domina su `vntol`; per questo il deck del pavimento, che
non ha celle in mute, girava.

**Che il cambio non sposti la misura è verificato, non assunto.** Stessa cella
con segnale, due tolleranze, analizzata col metodo
(`data/2026-09-16/L29a/tolleranze/`):

| Grandezza | `vntol=1e-9` | `vntol=1e-6` | scarto |
|---|---|---|---|
| A_rel MAINJACK | 12,16 V | 12,11 V | 0,4 % |
| B2 MAINJACK | 33,23 mV | 33,03 mV | 0,6 % |
| C2_rel MAINJACK | 8,875 V | 8,871 V | 0,05 % |
| **pavimento di C, MAINJACK** | 1,256 mV | 1,270 mV | ~1 % |
| **pavimento di C, fisse** | 184,7 µV | 187,8 µV | ~2 % |

Il pavimento è la cifra che decide se un valore è una misura o rumore, ed è
**invariata**. `vntol=1e-6` resta 100 volte sotto la soglia di A e B e 1000
volte sotto quella di C. **Limite dichiarato**: sulle celle *senza* segnale il
confronto non è possibile, perché lì la tolleranza stretta non termina.

## 4. Lo strumento, e i controlli che lo fanno cadere

`scripts/v2_metodo.py`. **22 controlli, 0 caduti; 11 sabotaggi su 11 ne fanno
cadere almeno uno** (`data/2026-09-16/L29a/strumento/autotest_e_sabotaggi.txt`).

I controlli nuovi di questa sessione, ognuno col sabotaggio che lo abbatte:

| Controllo | Cifra | Sabotaggio che lo fa cadere |
|---|---|---|
| C1 conta la distorsione di regime (h2 900 µV iniettata) | 898 µV | `fit_perfetto` |
| **C2 la cancella: corsa identica al riferimento** | **esattamente 0** | `rif_sfasato`, `c2_senza_riferimento` |
| C2 di una dissolvenza a coseno da 3 s, 12 V pk, 1 kHz passa | 503 µV | `senza_fit`, `freq_sbagliata` |
| C2 di un taglio netto a 12 V cade, alle tre frequenze | 9,05 / 6,71 / 4,18 V | `fit_perfetto` |
| C2 al rilascio col riferimento «mai in mute» passa | 503 µV | `senza_fit`, `freq_sbagliata` |
| Le soglie sono due, 1 mV e 100 µV | — | `soglia_unica` |

Il sabotaggio `c2_senza_riferimento` è la dimostrazione diretta che C2 fa il suo
lavoro: togliendogli il riferimento, C2 risale **esattamente ai 898 µV** di
distorsione che deve cancellare.

## 5. Il pavimento di C2, misurato

Deck del pavimento rifatto con le tolleranze corrette, celle a **evento nullo**
(`data/2026-09-16/L29a/corse/pavimento.csv`). È la cifra che va letta accanto a
ogni verdetto di C.

| Condizione | pavimento C1 | **pavimento C2** | soglia 1 mV |
|---|---|---|---|
| 1 kHz, MAINJACK, 100 kΩ | 1,222–1,244 mV | **0,57–0,80 mV** | decidibile |
| 1 kHz, MAINJACK, 10 kΩ | 1,030 mV | **0,58 mV** | decidibile |
| 1 kHz, uscite fisse | 173–188 µV | **180–253 µV** | decidibile |
| 20 Hz, MAINJACK | 167 µV | **9,8 µV** | decidibile |
| 20 Hz, uscite fisse | 10,2 µV | **3,1 µV** | decidibile |
| **20 kHz, MAINJACK** | 21,9 mV | **1,08 mV** | **NON decidibile** |
| 20 kHz, uscite fisse | 216–244 µV | **287–326 µV** | decidibile |
| 1 kHz a 0 dB, MAINJACK | 186–188 µV | — | decidibile |

**La scelta dell'utente è quella che rende il metodo utilizzabile**, e si vede
dove la distorsione è grande — **sull'uscita principale**, che è il caso
peggiore: C2 abbassa il pavimento di **1,9 volte** a 1 kHz, di **17 volte** a
20 Hz e di **20 volte** a 20 kHz. Con C1 e una soglia di 1 mV, la principale a
1 kHz e a 20 kHz sarebbe già fuori senza nessun evento.

**Sulle uscite fisse C2 non guadagna, e leggermente perde** (180–253 contro
173–188 µV a 1 kHz; 287–326 contro 216–244 µV a 20 kHz). È coerente col
meccanismo: lì la distorsione da cancellare è piccola (h2 vale 71 µV,
`armt_fix.txt`), mentre la differenza fra due corse somma i rumori numerici di
entrambe, circa √2. C2 conviene dove c'è distorsione da togliere; dove non ce
n'è, costa. Entrambe restano molto sotto 1 mV, quindi la scelta non cambia
nessun verdetto sulle fisse.

**L'eccezione va scritta, non aggirata**: a **20 kHz sulla principale** il
pavimento di C2 vale 1,08 mV, cioè **sopra** la soglia di 1 mV. Quella cella
**non è decidibile**, e per essa questo report non dà un verdetto di C.

Per confronto, il pavimento di **A** con musica a 1 kHz vale **0,68–0,70 mV**
sulla principale e 0,22 mV sulle fisse: sopra i 100 µV di A. Anche per A, con
musica a 1 kHz, valgono solo i **rifiuti**. Senza segnale e a 20 Hz A misura
benissimo (9,5 µV a 20 Hz, picovolt senza segnale).
