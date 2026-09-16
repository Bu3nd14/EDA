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

## 6. Le varianti a contatto (`tb_v2_mute_varianti.cir`)

87 corse, **completo e verificato**: 87 `.dat`, 87 righe di manifesto, nessun file
mancante, 0 errori nel log, exit 0. Analisi: `corse/varianti.csv`, riassunto
`corse/varianti_riassunto.csv`. **SIMULATO.**

**Prima una scoperta sul metodo: A con musica non misura un gradino.** Su ogni
variante la cella con musica dà A ≈ **11,8–12,8 V** sulla principale e
**3,7–4,1 V** sulle fisse. È il picco del segnale al jack, 12,07 V, passato dal
filtro: col riferimento che tiene lo stato finale, nell'istante della commutazione
una corsa suona e l'altra no. La controprova è nel graduale (§7): anche una
dissolvenza di 3 s dà 12,7 V. Portata all'utente: **ADR-036**, A si giudica solo
senza segnale. Le tabelle sotto seguono quella regola.

Uscita principale, 100 kΩ; a 10 kΩ le cifre coincidono entro pochi per cento.

| Variante | A senza segnale | B1, residuo a mute | C2 con musica | Esito |
|---|---|---|---|---|
| v0 dopo il condensatore (oggi) | 22 pV ✓ | **20,1 mV** ✗ | **8,87 V** (10,4 V sullo zero) ✗ | respinta |
| v1 prima | **111 mV** ✗ | **19,7 mV** ✗ | **7,08 V** ✗ | respinta |
| v2 entrambi i lati | **111 mV** ✗ | 76 µV ✓ | **7,18 V** ✗ | respinta |
| v3 prima, offset annullato | 80 nV ✓ | **19,8 mV** ✗ | **7,07 V** ✗ | respinta |
| v4 serie | 16 pV ✓ | 1,65 µV ✓ | **7,10 V** ✗ | respinta |
| v5 serie + jack | 20 pV ✓ | 2,4 pV ✓ | **7,10 V** ✗ | respinta |
| v6 sequenza | 32 µV ✓ | 21 nV ✓ | **7,10 V** ✗ | respinta |

Sulle fisse la graduatoria è la stessa, scalata col guadagno: gradino d'offset di
v1 e v2 35 mV, C2 fra 2,2 e 3,4 V.

- **Il gradino d'offset del contatto prima del condensatore è confermato**:
  111 mV sulla principale, contro i 104 mV simulati in scratch dopo L11 (NC-028).
- **Tutti i contatti netti cadono su C**, come ADR-032 aveva previsto: la musica
  sparisce o ricompare di colpo. Nessun contatto netto può rispettare C.
- **B2 non è una lettura pulita con un mute da 100 ms.** Su v2, v4, v5 e v6 B2
  vale ≈ 7 mV mentre B1 della stessa variante sta a µV o meno: la finestra di B2
  comincia 20 ms dopo l'inserzione e il filtro sta ancora smaltendo il taglio.
  Il verdetto non ne dipende, perché C2 respinge tutte le varianti.

## 7. Il mute graduale (`tb_v2_mute_graduale.cir`)

108 corse, **completo e verificato** allo stesso modo. Analisi:
`corse/graduale.csv`, riassunto `corse/graduale_riassunto.csv`. Elemento
**ideale**: conduttanza log-lineare da 1e-12 a 10 S; la dissolvenza efficace è
circa 3/13 della rampa. **SIMULATO.**

**C2 con musica, 1 kHz, 100 kΩ**:

| Posizione | 20 ms | 200 ms | 1 s | 3 s |
|---|---|---|---|---|
| g1 al jack | 3,34 V | 420 mV | 321 mV | 318 mV |
| g2 prima del condensatore | 3,33 V | 456 mV | 382 mV | 381 mV |
| g3 prima, offset annullato | 3,26 V | 481 mV | 416 mV | 415 mV |
| **g4 serie, principale** | 3,07 V | 111 mV | 7,7–8,0 mV | **2,93–3,02 mV** |
| **g4 serie, fisse** | 983 mV | 35 mV | 2,4–2,5 mV | **0,84–0,87 mV** |

- **Solo in serie una rampa più lenta aiuta**, e C scende circa come 1/T. In
  derivazione C resta fermo a 0,32–0,42 V oltre 1 s, e B2 a mute inserito vale
  ≈ 20 mV.
- **A senza segnale, graduale prima del condensatore**: il gradino d'offset scende
  con la rampa — **68 mV** (20 ms), **10 mV** (200 ms), **636 µV** (1 s),
  **72 µV** (3 s, sotto soglia). Con l'offset annullato resta a nV.
- **A 20 Hz** esiste solo la rampa da 1 s, a 100 kΩ: serie 62 mV sulla principale
  e 20 mV sulle fisse, derivazione 88–368 mV. **Nessuna cella a 20 kHz.**
- **A con musica** vale 12,7 V (12,8 V a 20 Hz) per **ogni** posizione e **ogni**
  rampa: è la controprova di §6.

**Nessuna posizione e nessuna rampa rispetta A, B e C insieme.**

## 8. Le decisioni dell'utente — ADR-036 — e cosa aspettarsi all'ascolto

Portate all'utente con le cifre di §6 e §7. Le sue risposte:

1. **A si giudica solo senza segnale; con musica decide C.** «Come misurare seguo
   il tuo consiglio». `v2_metodo.py` (`base_di`) tiene A con musica come
   diagnostica, `A_musica`; controllo T14 e sabotaggio `a_con_musica` (23
   controlli, 12 sabotaggi su 12).
2. **Per ora si accetta il mute graduale in serie con rampa da 3 s**, con C fuori
   soglia sulla principale. «per ora usiamo (ii), accettiamo la serie da 3s».

**La variante accettata, su tre uscite e due carichi** (`corse/serie_3s.csv`):

| Grandezza | Principale 100 k / 10 k | Fisse 100 k / 10 k | Soglia | Esito |
|---|---|---|---|---|
| A senza segnale | 16 / 13 pV | 13 / 4 pV | 100 µV | ✓ |
| B1 e B2 | 1,65 / 0,23 µV | 0,63 / 0,075 µV | 100 µV | ✓ |
| C2 a 1 kHz | **2,93–3,02 / 2,93–3,05 mV** | 0,84–0,87 / 0,83–0,86 mV | 1 mV | **✗ principale**, ✓ fisse |
| C2 a 20 Hz | 62 mV, **rampa 1 s** | 20 mV, rampa 1 s | 1 mV | ✗ — 3 s non misurata |
| C2 a 20 kHz | non misurato | non misurato | 1 mV | — |

Il C2 della principale sta 3,7–5,4 volte sopra il suo pavimento: è una misura.
Seguendo 1/T servirebbero circa 9 s di rampa per stare sotto 1 mV: **calcolato**.

### Cosa aspettarsi all'ascolto

Documentato per esteso in **ADR-036**, «Cosa aspettarsi all'ascolto». In breve,
con cifre **calcolate** con la formula di NC-028 (limite superiore grossolano):

- **Il gesto**: il mute non taglia, dissolve. La rampa dura 3 s, la dissolvenza
  udibile circa **0,7 s**, come un abbassamento rapido del volume.
- **Senza musica e a mute inserito: silenzio.** Gradino d'offset a pV, residuo a
  µV. Niente «tump».
- **Il botto di oggi sparisce**: in serie il condensatore d'uscita non si carica
  con la musica.
- **Durante la dissolvenza, sulla principale, 2,93–3,05 mV di C**: non un clic, ma
  la parte della dissolvenza che non è perfettamente liscia, sopra la musica e non
  nel silenzio. Al livello della prova (12 V di picco al jack) ≈ **63 dB SPL** di
  picco; a un livello d'ascolto normale, 30–40 volte meno, **≈ 31–34 dB SPL**
  (stima), mascherato dalla musica che sta cambiando di volume.
- **Uscite fisse: 0,83–0,87 mV, sotto soglia.** In dB non si calcola: il guadagno
  di Singxer e Stax non è noto.
- **Le incognite**: i bassi (20 Hz con la rampa da 3 s mai misurati; con 1 s
  ≈ 89 dB SPL calcolati, attenuati da orecchio e diffusori in misura non
  quantificata); i 20 kHz; **l'elemento reale**, che nel deck è ideale; i modelli
  segnaposto. **L'ascolto del prototipo resta l'arbitro.**

## 9. Cosa resta aperto

- **NC-028 resta aperta e bloccante.** La scelta c'è, il rimedio no: esiste solo in
  un deck, con un elemento ideale. Si chiude quando il mute graduale in serie è un
  circuito reale nel sorgente, misurato col metodo di V2.
- **A L29b**, come da ADR-036:
  - l'elemento graduale reale, nel sorgente, e la sua misura;
  - **C a 20 Hz con la rampa da 3 s**, e una cella a 20 kHz;
  - il caso peggiore di V2 non coperto qui: passaggi di guadagno e criterio 3 di
    ADR-030, trim, dispersione dell'LSK489, accensione e spegnimento;
  - **P7** per la posizione in serie;
  - lo **stato sicuro** di ADR-012 col mute in serie, e
    `check_relay_safe_state.py`: un cambio è un'ADR nuova.
- **Il pavimento diffuso** di C resta non attribuito (§1.2).

## Dati

`data/2026-09-16/L29a/`:
- `strumento/autotest_e_sabotaggi.txt` — 23 controlli, 12 sabotaggi;
- `tolleranze/` — la prova che `vntol=1e-6` non cambia la misura;
- `corse/pavimento.csv`, `varianti.csv`, `graduale.csv` e i `_riassunto.csv`;
- `corse/serie_3s.csv` — la variante accettata;
- i manifesti dei tre deck.

Le forme d'onda (`.dat`, diversi GB) non sono versionate: si rigenerano dai tre
deck con `run_simulation.sh`, in circa tre ore di calcolo.
