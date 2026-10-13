# 2026-10-13 — L45b, i guasti dei controlli della scheda audio, e P10

Seconda parte di **L45**, l'analisi dei guasti singoli (NC-042, maggiore, prima di G1). Dati, deck e
comandi in `docs/preamp/data/2026-10-13/L45b/` (README). Nessun cambiamento al circuito: si misura e
si classifica. La scelta del rimedio è di **L45d**. Per scelta dell'utente («tutto in una
sessione») il lotto contiene anche la **rilettura dei guasti del blocco di L45a contro P10**: a
vuoto, con la durata sopra il tetto.

**P10** (PR-30, ADR-069): un guasto singolo della scheda audio durante l'ascolto porta su ogni uscita
al più **100 ms sopra 0,87 V**, misurati sul jack **senza filtro** e **a vuoto**. Il picco filtrato si
dichiara accanto, senza soglia.

## In breve

- **Nessun guasto ordinario dei controlli si avvicina al tetto.** Su 78 modi (relè del selettore,
  del guadagno, del permesso, del trim e del mute; piloti, diodi, commutatori, LED, condensatori
  d'uscita e C_T, bleed, 47 Ω, comandi del micro) il peggiore porta al jack **9,5 mV** (73 dB SPL a
  1 m), il guadagno o il trim che cambiano durante l'ascolto 1,3–7 mV (fino a 29,7 mV con la
  dispersione, ADR-051): **29 dB sotto il tetto**, e nessuna durata. Il mute che cade, rimbalza o
  si apre dà nanovolt.
- **Il solo modo dei controlli che supera il tetto è l'isolamento fra bobina e contatti che cede**
  (il relè lo garantisce a 1500 V c.a.: raro). Conta dove la bobina è a 12 V mentre il contatto
  porta il segnale. **Sul relè di mute mette 12 V in continua sul jack, per sempre, anche a mute
  inserito**: il NO è il jack, e la bobina di un relè di mute rilasciato ha tutti e due i capi a
  12 V. Nessun rivelatore che apra il mute lo toglie. Sul selettore porta il blocco A al rail, su
  tutti e tre i jack (fino a 3,1 s sulle fisse).
- **Il mute che non si inserisce più** (un NO saldato, o il sink Q501 in corto) non fa niente al
  guasto, ma toglie la protezione: allo spegnimento coi rail in rampa i jack collegati vedono
  **1,6–10,5 V per 14–348 ms**, secondo come scendono i rail. Il numero vero è del banco
  dell'alimentatore: **L45c**.
- **Il contratto, senza danno**: la bobina del permesso K6 aperta rende trim e guadagno comandabili
  fuori mute in silenzio (il «Da riaprire se» di ADR-027) e lascia il **LED rosso acceso con la
  musica**; un contatto saldato di K1 o K5 lascia il guadagno a riposo **sopra 0 dB** (PR-18) con i
  LED che dicono 0.
- **I guasti del blocco di L45a, a vuoto, contro P10: 257 modi su 544 stanno sopra 0,87 V più di
  100 ms** (48 / 53 / 53 / 49 / 54 per posizione), fino a 2 s al principale e 3,1 s sulle fisse.
  Tutti i modi che vanno al rail; 20 spostamenti lenti della continua che il tetto filtrato di L45a
  non vedeva; 23 colpi brevi che il tetto vedeva e P10 no.
- **Il rivelatore ideale di L45a basta per P10**: a vuoto il colpo dura il tempo del rivelatore più
  quello del contatto, **0,2–10,1 ms** contro 100 ms. Il picco resta 15 V.
- **La 47 Ω d'uscita in corto** (un modo che L45a non conteneva) non fa oscillare lo stadio con 100 pF,
  1 nF e 10 nF di cavo, nemmeno con un gradino d'ingresso.

## Il banco

Il canale di L45a (`L45a/script/genera_canale.py`, **importato** e non copiato: lo stesso sorgente
K11, C_IN, R_SEL, selettore, blocco A, buffer delle fisse, scala del trim, C_T, volume al massimo,
blocco B, le tre uscite con la geometria iii), **senza blocchi guasti**. Il guasto è in **un**
controllo, inserito a 0,3 s con lo stesso interruttore di L45a, durante l'ascolto e senza segnale:

| Controllo | Nel banco |
|---|---|
| Condensatori d'uscita, C_T, C_IN, bleed, 47 Ω | un corto da 10 mΩ, o un terminale staccato |
| Il mute (K2–K4) | il NO del deviatore che si apre; il comando che cade (NO apre, NC chiude 1 ms dopo); un rimbalzo di 0,5 ms |
| Il guadagno (K1, K5) | i rami del blocco B a massa che si chiudono (0 → +3, 0 → +10) o si aprono (+3 → 0, +10 → 0, +10 → +3) |
| Il trim (K7, K8) | la cima di C_T che passa dall'uscita del blocco A alla presa −6 o −12; il comune che si apre |
| Il selettore | il contatto che si apre |
| L'isolamento fra bobina e contatti | i 12 V di `VRELAY` sul nodo del contatto con 10 Ω (il capo della bobina dal lato di `VRELAY`) o 1 kΩ (a metà bobina) |
| I guasti latenti del mute | il mute rilasciato mentre i rail si spengono (15 → 0 V in 110 ms, simmetrici e asimmetrici) o si accendono (0 → 15 V in 50 ms) |

**A vuoto** vuol dire tolti i tre carichi (cj 100 kΩ, Singxer 10 kΩ, Stax 50 kΩ): restano i bleed
sul lato del condensatore e sul jack. Ogni modo è corso anche coi carichi di oggi.

**Lo strumento della durata** (`analizza_p10.py`): il tempo complessivo con |v(jack)| > 0,87 V dal
guasto, sul segnale senza filtro, ricampionato a 96 kHz come `v2_metodo.py`. Controllato prima di
usarlo su due casi noti: un esponenziale di 14,9 V con τ 0,517 s (atteso τ ln(14,9 / 0,87) =
1468,6 ms, misurato **1468,6 ms**) e un seno di 1 V a 997 Hz per 1 s (atteso 328,2 ms, misurato
**328,2 ms**). A 1 kHz esatto dava 312,5 ms: 96 campioni per periodo cadono sempre alle stesse fasi,
e lo si dice perché è un errore che una prova a 1 kHz nasconderebbe.

**Controlli del banco.**

| Controllo | Atteso | Misurato |
|---|---|---|
| Corsa senza guasto, a 0 / +3 / +10 dB | nessun gradino | ≤ 15 nV su ogni jack |
| L'uscita del blocco B in corto col rail +, a vuoto (deve superare) | ~1,5 s sopra 0,87 V al principale (ADR-069, a calcolo) | **1472 ms**, 15,2 V grezzi |
| Lo stesso, buffer della Stax, fino a 6 s | ~3,1 s sulla Stax (ADR-069) | **3145 ms**, 15,2 V |
| Lo stesso, blocco A, fino a 6 s | sulle fisse ~3,1 s, al principale attraverso C_T | fisse **3147 ms**, principale 177 ms |
| Un deck di L45a ricorso così com'è (`tr_B/Q132_ce`, coi carichi) | i numeri di L45a | **6,201 V** grezzi, **3,423 V** filtrati: gli stessi |

## I guasti dei controlli

La tabella completa, **78 modi** in sette gruppi, un modo per riga col suo effetto, i numeri al jack,
la durata P10 a vuoto e coi carichi, i requisiti toccati e il lotto a cui va, è in
`data/2026-10-13/L45b/fmea_controlli.md` (e `.csv`). Le righe «calcolo» dicono il ragionamento e il
numero a cui rimandano; le righe «simulato» il modo della corsa.

### Per classe

| Che cosa fa il guasto | Modi tipici | Al jack (grezzo, a vuoto) | P10 |
|---|---|---|---|
| **Niente al jack**: un'uscita o un ingresso tace, un contatto rimbalza, il mute cade | bobine aperte, contatti aperti, NC saldati, rimbalzi, C_OUT, C_T e 47 Ω aperti, bleed aperti | < 10 µV | 0 ms |
| **Un gradino di millivolt**: il guadagno o il trim che cambiano durante l'ascolto, un condensatore d'uscita o C_T in corto | K1/K5 e ausiliari, i loro diodi, K6 o Q502 aperti, i bistabili del trim, C_OUT, C_T | **1,3–9,5 mV** (55–73 dB SPL a 1 m); 6,7 mV sulle fisse | 0 ms |
| **La linea dei relè in corto**: una bobina, un ricircolo, un TVS in corto | ogni bobina in corto, D3, D14–D19, D1/D2 | la classe di ADR-051, ≤ 29,7 mV | 0 ms |
| **I 12 V di una bobina nel segnale**: l'isolamento fra bobina e contatti che cede | il mute (K2–K4), il selettore | **12–14 V** | **da 147 ms a permanente** |
| **Latente**: al guasto niente, ma il mute non si inserisce più | NO del mute saldato, Q501 in corto | allo spegnimento **1,6–10,5 V** | **14–348 ms** allo spegnimento |
| **Il comando sbagliato**, senza danno: il guadagno a riposo non è 0 dB, i comandi vivi fuori mute, un LED che mente | K1 saldato, K11 di tenuta saldato, K6 o Q502 aperti, D10/D11 in corto | i mV della seconda riga | 0 ms |

### Il guadagno e il trim che cambiano durante l'ascolto

| Cambio | Al principale, grezzo |
|---|---|
| 0 → +3 dB | 1,37 mV |
| 0 → +10 dB | 7,01 mV |
| +3 → 0 dB | 1,25 mV |
| +10 → 0 dB | 6,32 mV |
| +10 → +3 dB | 5,04 mV |
| trim 0 → −6 dB | 1,54 mV |
| trim 0 → −12 dB | 2,36 mV |

È il gradino d'offset del blocco B alla sua continua nominale (−2,9 mV). Con la dispersione delle
parti è più grande, fino ai **29,7 mV** che ADR-051 ha misurato per il cambio +10 → 0 a jack
collegato: **29 dB sotto il tetto** nel caso peggiore, e senza durata.

Il guadagno o il trim si muovono fuori mute in sei modi: la bobina di K6 aperta o il suo pilota Q502
aperto (il «Da riaprire se» di ADR-027: **trim e guadagno** seguono la manopola fuori mute, in
silenzio), D10 o D11 in corto (il trim), D12 o D13 aperti e K11 o K12 che cadono (il guadagno solo
verso il basso), il bistabile che commuta da solo. **Nessuno arriva vicino al tetto**: sono
violazioni di PR-17 e PR-18, non danni.

### L'isolamento fra bobina e contatti

L'unico modo dei controlli che supera il tetto. Il G6K garantisce **1500 V c.a.** fra bobina e
contatti per un minuto e 1000 MΩ di isolamento (en-g6k.pdf, tabella delle caratteristiche): perché
ceda a 12 V serve un difetto del relè, non un sovraccarico. È un guasto singolo raro; lo si misura
perché è l'unico che porta i 12 V di `VRELAY` nel segnale.

Conta **solo dove la bobina è a 12 V mentre il contatto porta il segnale**:

| Relè | La bobina durante l'ascolto | Il cedimento | Al jack, grezzo | P10 a vuoto | Coi carichi |
|---|---|---|---|---|---|
| **K2–K4, sul NO (il jack)** | 12 V sempre (pin 1 su `VRELAY`, pin 8 su `MUTE_CMD`) | **12 V in continua sul jack, anche a mute inserito** | 12 V | **permanente** | permanente |
| K2–K4, sul comune | idem | 12 V al jack finché il mute non si inserisce | 12 V | permanente senza mute | permanente |
| **K13–K16** (il selettore) | 12 V la bobina scelta | 12 V all'ingresso del blocco A: il blocco A al rail, su **tutti e tre i jack** | 13,6 / 13,9 V | principale 579 ms, fisse **3082 ms** | 510 / 127 / 542 ms |
| lo stesso, 1 kΩ | | | 13,3 / 14,2 V | 147 ms, fisse 2530 ms | 258 / 104 / 446 ms |
| K7, K8 (il trim) | 12 V **solo in mute** (`VTRIM`) | durante l'ascolto niente; in mute spinge l'uscita del blocco A, e al rilascio i condensatori tornano carichi | limite superiore 5,9 V (12 V durante l'ascolto) | 119 ms, fisse 1875 ms (limite) | — |
| K1, K5 (il guadagno) | 12 V solo a contatto **chiuso a massa** | non fisico: mette solo `VRELAY` a massa (ADR-051) | — | — | — |

Due cose che L45d deve avere davanti:

- **Sul NO del mute nessun rimedio di quelli discussi funziona.** Il NO è il jack stesso: un
  rivelatore che apra il sink di `MUTE_CMD` stacca il comune, ma i 12 V restano sul jack. Li toglie
  solo lo spegnimento di `VRELAY`. La ragione è il pilotaggio dal lato basso: la bobina di un relè
  di mute rilasciato ha **tutti e due** i capi a 12 V. Un pilotaggio dal lato alto (il pin 1
  commutato, il pin 8 su `RLY_RET`) lascerebbe la bobina rilasciata a 0 V. È un'osservazione, non
  una proposta: cambia ADR-045 e il banco di L41c.
- **Sul selettore** il rivelatore funzionerebbe come per il blocco A di L45a: il blocco va al rail,
  e il mute stacca i jack.

### I guasti latenti del mute

Un NO di K2–K4 saldato, o il sink Q501 in corto D-S, al momento del guasto non fanno niente. Ma da
lì in poi **il mute non si inserisce più**: né dal frontale, né allo spegnimento, né dal sorvegliante,
che agisce sul gate di Q501. Il LED rosso non lo vede (il limite che ADR-028 dichiara per il NO
saldato; per Q501 in corto il LED si accende normalmente, perché legge K6). Il primo spegnimento, la
prima perdita di rete o il primo guasto dell'alimentatore trovano i jack **collegati**:

| Rail (rampa lineare, rail ideali) | Principale grezzo / sopra 0,87 V | Fisse |
|---|---|---|
| Tutti e due in 110 ms | **7,5 V / 56 ms** | 7,5 V / 58 ms |
| Lo stesso a +10 dB | 8,1 V / 55 ms | 7,5 V / 58 ms |
| Il + in 220 ms, il − in 110 ms | 1,6 V / 14 ms | 1,65 V / 15 ms |
| **Il − in 220 ms, il + in 110 ms** | **10,5 V / 348 ms** | 10,7 V / 150 ms |
| Accensione, 0 → 15 V in 50 ms | 1,2 V / 12 ms | 2,0 V / 17 ms |

Il picco supera il tetto di PR-23 in ogni caso (quello che PR-23 scrive per la rete e l'alimentatore),
e la durata **dipende da come scendono i rail**: da 14 a 348 ms nelle rampe provate. Il caso vero lo
dà solo il banco dell'alimentatore (L41c) con questo guasto: è di **L45c**. Non è un guasto di P10
(al guasto non succede niente): è un guasto **latente** che toglie la protezione di PR-23.

Lo stesso per un **C_OUT in corto**: al guasto 3,3 mV (6,7 mV sulle fisse), ma da lì l'uscita è
accoppiata in continua, e un guasto successivo del blocco non decade più (P10 permanente, come
guasto doppio).

### Il comando sbagliato e i LED

Senza danno al jack, ma contro il contratto:

- **K1 o K5 con un contatto saldato**: a riposo quel canale resta a +3 (o +10) dB. È il solo modo in
  cui il guadagno a riposo non è 0 dB, contro **PR-18** («mai più alto»), e i LED, letti dagli
  ausiliari, dicono 0 dB. ADR-033 aveva accettato il disaccordo fra un relè e il suo gemello per il
  trim; qui il disaccordo è sul guadagno, e verso l'alto.
- **K11 o K12 col polo di tenuta saldato**: al rilascio del mute il guadagno sale alla posizione
  precedente anche se la manopola è a 0, insieme al collegamento dei jack (1,4 mV). Il LED dice il
  vero.
- **K6 o Q502 aperti, D10 o D11 in corto**: il **LED rosso del mute resta acceso con la musica**. È
  l'unico modo in cui un LED dice «muto» con un jack collegato: ADR-028 punto 5 ne garantiva il
  contrario.
- **Q502 in corto**: K6 sempre eccitato, trim e guadagno fermi; all'accensione i bistabili del trim
  non vengono pilotati (ADR-027).

### La 47 Ω d'uscita in corto

Un modo che L45a non conteneva, perché la 47 Ω è fuori dal blocco. In corto mette la capacità del
cavo direttamente sullo stadio, fuori dalla resistenza che la teneva fuori dall'anello. Col cavo
come capacità sul jack (100 pF, 1 nF, 10 nF), senza segnale e poi con un gradino d'ingresso di
0,2 V con fronti di 1 µs: **nessuna oscillazione**. Il residuo 10–19 ms dopo il gradino è lo stesso
della corsa sana (20 mV picco-picco, la caduta di C_T), e ngspice non ha mai preso un passo sotto il
massimo di 1 µs. Con 10 nF la sovraelongazione del fronte al jack sale di qualche punto sulla corsa
sana. È una prova nel tempo, non una misura del margine di fase con la capacità sull'uscita: se
L45d o L55 ne vogliono una, va fatta col banco dell'anello.

### Il firmware

- **Le LDR non ci sono più** (ADR-062): il caso di NC-042 «un firmware che accende tutte e due le
  stringhe» non esiste.
- **Un firmware bloccato** lo resetta il watchdog (≤ 250 ms, `timer_spec.md` § 4.8); in reset le
  uscite sono in alta impedenza e i pull-down le portano a riposo: il mute si inserisce, con Δ in
  hardware.
- **`MUTE_REQ` bloccata alta** (il pin, non il programma): la musica resta, e né il commutatore del
  mute né lo spegnimento morbido la tolgono; il sorvegliante e il rivelatore di rete sì. **PR-24**
  dice «con il micro bloccato l'apparecchio resta muto»: un pin bloccato alto non lo rispetta. È di
  **L54** (NC-054).
- `PERMIT_REQ` bloccata alta tiene K6 eccitato (trim e guadagno fermi); `MAINS_REQ` alta tiene il
  trasformatore grande acceso in standby. L54.

## I guasti del blocco di L45a contro P10, a vuoto

**Ogni** corsa di L45a (559 deck, le stesse impostazioni: accorciate, gear, il rivelatore ideale)
rifatta coi tre carichi tolti, e letta con lo strumento della durata. Dati in
`data/2026-10-13/L45b/p10_blocco.md` (e `.csv`, un modo per riga e posizione).

| Posizione | Modi | **Fuori da P10** | di cui ancora sopra alla fine della corsa | L45a: sopra il tetto filtrato | Principale, tempo sopra (mediana / max) |
|---|---|---|---|---|---|
| Blocco A | 108 | **48** | 34 | 50 | 181 / 578 ms |
| Buffer del Singxer | 106 | **53** | 33 | 49 | — (solo la sua fissa) |
| Buffer della Stax | 106 | **53** | 33 | 49 | — |
| Blocco B, 0 dB | 112 | **49** | 6 | 52 | 1047 / 1999 ms |
| Blocco B, +10 dB | 112 | **54** | 4 | 52 | 1203 / 1749 ms |

- **257 modi su 544** stanno sopra 0,87 V più di 100 ms. Al principale da 116 ms a 2 s (mediana
  818 ms); sulle fisse quasi sempre fino alla fine della corsa: con le corse lunghe (6 s) il blocco
  al rail tiene le fisse sopra il tetto **3,15 s** e il principale **1,47 s**, i numeri di ADR-069.
- **Per classe** (quella di L45a): **tutti** i modi che vanno al rail (102 su 102), 146 su 193 di
  quelli che spostano la continua, 4 su 242 di quelli che in L45a non facevano niente al jack (le
  derive lente, sotto), 5 su 7 dei casi che in L45a non erano arrivati in fondo.
- **Il colpo che torna in meno di 100 ms**: 23 modi superano 0,87 V grezzi ma restano entro P10.
  Sono i corti che portano il blocco al rail per un istante e lo lasciano tornare: la coda (Q106) in
  corto B-E, 17–90 ms; un gate del JFET d'ingresso in corto G-S, 65 ms; R126 in corto, 34–54 ms; il
  nodo dei cascode (C116, R115) in corto, ≤ 1,4 ms. Per PR-23 erano sopra il tetto, per P10 no.
- **I due criteri non coincidono**, e la tabella dei disaccordi è in `p10_blocco.md`. Oltre ai colpi
  brevi qui sopra, **20 modi sono fuori da P10 ma sotto il tetto filtrato di L45a**: sono
  **spostamenti lenti della continua** (lo stopper di gate aperto, R108, che porta le fisse a
  2,4 V per 1,9 s; la resistenza di retroazione aperta, R144 a +10 dB, 8,9 V per 1,7 s al
  principale). Il filtro 20 Hz–20 kHz di PR-23 li toglieva; un apparecchio accoppiato in continua
  no, ed è il caso che ADR-069 assume. Uno dei venti (il finale del buffer della Stax in corto, F2
  `Q146_ce`) in L45a era nella tabella principale come corsa interrotta, e la sua rifatta gear era
  già oltre il tetto.
- **Il rivelatore ideale** (il mute inserito 0,1 / 1 / 3 / 10 ms dopo il guasto, dalle corse di
  L45a): a vuoto il tempo sopra il tetto diventa **0,2 / 1,1 / 3,1 / 10,1 ms**, cioè il tempo del
  rivelatore più quello del contatto, su tutti i jack. Il picco resta 14,7–16 V. Per P10 il
  rivelatore **basta, con margine**: ogni tempo fino a ~90 ms rispetterebbe i 100 ms. Due corse (il
  finale PNP staccato, taglio a 0,1 e 3 ms) si fermavano al taglio con «timestep too small» (#33):
  rifatte col metodo gear, 0,2 e 3,1 ms.
- **Coi carichi di oggi** le durate sono più corte (τ 0,25 s al principale, 0,20 s sulla Stax,
  0,045 s sul Singxer): `tr_B/Q132_ce` di L45a, il finale NPN in corto, sta sopra 0,87 V **97 ms**
  col cj (entro) e **204 ms** a vuoto (fuori). P10 si misura a vuoto per scelta (ADR-069).

## Quello che il banco non dice

- **I contatti sono interruttori ideali** da 0,1 Ω o 10 mΩ: niente arco, niente capacità del
  contatto aperto (ADR-044 la vuole sotto 2,4 pF, un vincolo di G2).
- **Senza segnale**, salvo la 47 Ω col gradino: un guasto del guadagno con la musica è un salto di
  livello della musica, non un gradino in continua, e P10 non lo misura.
- **La continua dei blocchi è la nominale** (−2,9 mV): i gradini di guadagno e trim crescono con la
  dispersione, fino ai 29,7 mV di ADR-051.
- **L'isolamento che cede è un resistore** da 10 Ω o 1 kΩ verso 12 V ideali: `VRELAY` vera ha un
  limite di corrente, e un cedimento ad alta resistenza dà meno. Con 1 kΩ i numeri restano oltre il
  tetto.
- **I latenti hanno rail ideali con rampe lineari**: le durate dipendono dalla rampa (14–348 ms),
  e il caso vero è del banco dell'alimentatore.
- **I guasti del temporizzatore** (Q501, Q502, D522, le resistenze dei gate) sono qui solo per il loro
  effetto al jack; il circuito è di L54.

## Che cosa resta, e a chi

- **L45c** — l'alimentatore componente per componente; in più, da qui: **il mute che non si
  inserisce** (NO saldato, Q501 in corto) sul banco vero dell'alimentatore, allo spegnimento e alla
  perdita di rete.
- **L45d** — la decisione, coi numeri di L45a, di qui e di L45c:
  - il rivelatore di continua, che per P10 basta (0,2–10,1 ms a vuoto) e per i 257 modi del blocco
    è l'unico candidato misurato;
  - l'isolamento fra bobina e contatti del relè di mute, che **nessun rivelatore sul mute copre**:
    accettarlo come raro e dichiararlo, o cambiare il pilotaggio dei relè di mute (dal lato alto la
    bobina rilasciata starebbe a 0 V), o altro;
  - il mute che non si inserisce più (NO saldato, Q501 in corto): se e come rilevarlo, coi numeri
    di L45c;
  - il permesso che fallisce aperto (la bobina di K6, il «Da riaprire se» di ADR-027) e il LED rosso
    acceso con la musica; i contatti saldati di K1/K5 contro PR-18; un C_OUT in corto che rende
    l'uscita accoppiata in continua per il guasto successivo.
- **L54** — `MUTE_REQ` bloccata alta contro PR-24; Q502 in corto all'accensione; D522.

## Requisiti

- **NC-042**: avanza; si chiude con L45d.
- **P10 / PR-30**: **non rispettato oggi**, come ADR-069 aveva calcolato: 257 modi del blocco su 544,
  e l'isolamento bobina–contatti del mute e del selettore fra i controlli. Il rivelatore ideale lo
  porterebbe entro per tutti i modi del blocco provati, non per l'isolamento sul NO del mute. Il
  rimedio è di L45d.
- **PR-17, PR-18**: K6 o Q502 aperti (trim e guadagno vivi fuori mute, il «Da riaprire se» di
  ADR-027), K1/K5 saldati (il guadagno a riposo non è 0 dB), K11/K12 di tenuta saldati. Nessuno
  supera il tetto; li pesa L45d.
- **PR-19** (il LED di mute): acceso con la musica per K6 o Q502 aperti, D10/D11 in corto.
- **PR-23**: il mute che non si inserisce più (NO saldato, Q501 in corto) è un guasto latente che
  toglie la protezione; il numero vero è di L45c.
- **PR-24**: `MUTE_REQ` bloccata alta; L54.
