# L29d — la sonda del contatto in serie al jack (2026-09-25)

**NC-028 resta aperta e bloccante. Nessuna ADR: la scelta è dell'utente.** È una **sonda**: le
celle peggiori di L29c sulle geometrie del contatto in serie, e ci si ferma (decisione dell'utente
del 2026-09-25). La matrice completa sulle geometrie scelte è **L29d2**.

- **Dati**: `data/2026-09-25/L29d/`, con README.
- **Banco**: `data/2026-09-25/L29d/deck/tb_v2_sonda_serie.cir`, generato dal generatore di L29c
  esteso (`--matrice sonda_l29d`). Il blocco CANALE è identico (`v2_metodo.py canale`). Il deck
  versionato di L29c, il controfattuale, `caldo` e le curve rigenerati col generatore esteso
  sono **byte-identici**.
- **Etichetta di ogni cifra**: il circuito e i modelli di L29c (L39, ADR-042). Le varianti
  esistono **solo nel banco** e sono ipotesi dichiarate, non un cambio di `circuits/`.

## 1. Perché una sonda e non la matrice: la previsione

Il mandato chiedeva (i) serie più derivazione e (ii) serie sola. Rileggendo il blocco CANALE:
- la posizione in serie sta **dopo** il condensatore d'uscita da 4,7 µF;
- con la serie aperta, il lato condensatore (`MAINC`, `FIXC1`, `FIXC2`) non ha un percorso veloce
  verso massa: nel blocco ha 1 TΩ, e L29a usava 220 k / 470 k;
- un salto d'offset preso a mute inserito resta quindi nel condensatore, e arriva al jack quando
  la serie si richiude. È il salto del cambio 0→+10 dB (66 mV) o dell'accensione.

**Il calcolo**: 66 mV · e^(−2 s / (220 k · 4,7 µF)) ≈ **9,6 mV** al rilascio, contro i 116 µV di L29c.
Con la derivazione al jack, (i) non cambia la cosa, perché la derivazione sta dal lato sbagliato.
La geometria che in teoria risolve è una terza: **(iii) serie più derivazione dal lato del
condensatore**.

Portato all'utente prima di correre. Risposta: **«Sonda e poi mi fermo»**.

## 2. Le geometrie e le ipotesi

Le geometrie (t_ins / t_rel: gli istanti del relè al jack di L29c):

| | Inserzione | Rilascio |
|---|---|---|
| **N** neutra = L29c | derivazione al jack chiude | derivazione apre |
| **iA** serie + derivazione al jack | serie apre, derivazione chiude +1 ms | derivazione apre, serie chiude +1 ms («l'inverso» del mandato) |
| **iB** idem, rilascio «serie prima» | come iA | serie chiude, derivazione apre +1 ms |
| **ii** serie sola | serie apre | serie chiude |
| **iii** serie + derivazione **lato condensatore** | serie apre, derivazione MAINC/FIXCx chiude +1 ms | derivazione apre, serie chiude +1 ms |

All'accensione ogni geometria parte a riposo: serie aperta, derivazione chiusa (NC, ADR-012).

**Le ipotesi, tutte dichiarate nel generatore:**
- **la serie**: interruttore nativo `SWK` (0,1 Ω, rimbalzi di L29c) in parallelo a `BSERx`, tenuto
  aperto, e al ponte `RBYx`, aperto;
- **il contatto aperto**: **5 pF** fra i capi («qualche pF»);
- **nessun cavo al jack**: è il caso peggiore per il passaggio capacitivo;
- **con la serie**, il lato condensatore ha il bleed di L29a, **220 k** (principale) e **470 k**
  (fisse). È un **valore del circuito**, non deciso;
- **il trasferimento fra i due contatti**: 1 ms, la stessa ipotesi del trim di L29c.

## 3. Come si è fatto fidare

| Controllo | Esito |
|---|---|
| 32 corse (`corri.sh` di L29c) | 32 rc=0; nessun «Transient op»; 3 partite alla seconda prova, senza `.nodeset` (`on_r300p_iA`, `on_r10m_iA`, `gm0x10_lz_ii`) |
| Punto di partenza (`verifica_partenza.py`) | 0 corse fuori su 32 |
| **Controfattuale**: N contro le stesse celle di L29c (`controfattuale_N.py`) | A e B2 entro **0,09 %** (111,5 → 111,4 µV); accensioni identiche; `sonda/controfattuale_N.csv` |
| La previsione, sulle forme grezze | iA: MAINC a −9,62 mV prima del rilascio, jack a **9,65 mV**; calcolato 9,6 mV |

## 4. I risultati

Senza segnale, +10 dB, 100 kΩ. Picco di A o B2 col metodo di V2: il peggiore sulle tre uscite, in
µV. Soglia 100 µV. In grassetto i valori fuori soglia.
Fonte: `sonda/verdetto.csv`, `sonda/tabella.csv`.

| Cella | Grandezza | N (= L29c) | iA | iB | ii | **iii** |
|---|---|---|---|---|---|---|
| cambio 0→+10 a relè chiuso | A del cambio | **111** | 0,008 | 0,008 | **3 445** | 6,8 |
| | A del rilascio 2 s dopo | 0,03 | **10 250** | **304** | **10 210** | 0,03 |
| | B2 | 0,37 | 0,00 | 0,00 | 1,1 | 0,00 |
| accensione, rampa 300 ms, rail + in ritardo | A dell'accensione | **11 280** | 0,22 | 0,22 | **192 700** | **205** |
| | A del rilascio | 0,03 | **63 510** | **1 890** | **63 730** | 0,03 |
| accensione, rampa 10 ms, rail − in ritardo | A dell'accensione | **6 450** | 0,13 | 0,13 | **115 100** | 44 |
| | A del rilascio | 0,03 | **189 700** | **5 582** | **189 600** | 0,03 |
| mute semplice | A_ins / A_rel / B2 | 0,01 / 0,03 / 0,01 | uguale | uguale | uguale | uguale |

**Cosa dicono.**
- **iA e ii sono le peggiori.** Il salto preso a mute inserito resta nel condensatore e arriva
  intero al rilascio: 10 mV dopo il cambio di guadagno, 64–190 mV dopo l'accensione.
  - La **ii** in più lascia passare l'accensione dal contatto aperto: 115–193 mV.
  - La **(ii) serie sola è da scartare**: nessuna cella la salva.
- **iB** chiude la serie mentre la derivazione al jack tiene ancora. Il condensatore si scarica
  attraverso 47 Ω (τ ≈ 0,22 ms), ma dopo 1 ms ne resta ~1/32 misurato (e^(−4,5) ≈ 1/90
  calcolato; i rimbalzi della chiusura accorciano la scarica): 0,3–5,6 mV all'apertura della
  derivazione. Il tempo fra i due contatti è la leva. Con qualche ms il residuo scenderebbe in
  modo esponenziale: **calcolato, non misurato**.
- **iii regge su tutto tranne una cella**: 6,8 µV sul cambio (16 volte meno di L29c) e 0,03 µV al
  rilascio; l'accensione rapida dà 44 µV. **Fuori**: l'accensione con la rampa da 300 ms,
  **205 µV** sulle fisse.

**Il meccanismo del residuo di iii**, sulla forma grezza (`script/forma.py`):
- a ~7 V di rail il buffer scatta. Il lato condensatore, a massa tramite la derivazione, ne vede
  1/471: FIXC1 va a −11 mV in ~15 µs;
- i **5 pF** del contatto aperto ne portano al jack la derivata, un impulso di 0,45 mV largo ~10 µs;
- è **passaggio capacitivo**, non carica immagazzinata. Scala con la capacità del contatto aperto
  e cala con quella del cavo al jack, che qui è zero per ipotesi. Con 100 pF di cavo il partitore
  capacitivo varrebbe circa 1/20: **calcolato, non misurato**.

## 5. Cosa resta all'utente (L29d2)

1. **Quali geometrie** vanno nella matrice completa. La misura indica la **iii**, e forse la iB
   con un trasferimento più lungo; la **ii** è da scartare.
2. **Lo stato sicuro (ADR-012).** Nella iii, a riposo e a macchina spenta, il jack è isolato e
   va a massa solo attraverso il bleed (220 k / 470 k), non attraverso un contatto. ADR-012
   dice «a macchina spenta le uscite sono a massa»: va deciso se il bleed basta, o se serve
   un secondo polo a massa sul lato jack (la iii più la derivazione al jack). La scelta tocca
   anche il failsafe di ADR-043.
3. **I valori da fissare**, oggi ipotesi del banco:
   - il bleed dal lato condensatore;
   - la capacità del contatto aperto, dal datasheet del relè scelto;
   - la capacità del cavo da considerare al jack;
   - il tempo di trasferimento.
4. **Il resto della matrice di L29c** sulle geometrie scelte:
   - i cambi di trim, e la dispersione peggiore (`dp…max`, 267 µV in L29c);
   - la musica (S, B2) a 1 kHz e 20 Hz, e B col contatto aperto;
   - il **carico da 10 kΩ**, ancora non fatto.

**Lo spegnimento** non è stato corso: è di L30 (ADR-043). Una geometria con la derivazione dal lato
condensatore cambia però anche la sua domanda: da verificare in L29d2.

## 6. I tempi

32 corse, 8 in parallelo, in ~12 minuti (111–249 s l'una). `analizza_par.py` con 8 processi:
227 s.
