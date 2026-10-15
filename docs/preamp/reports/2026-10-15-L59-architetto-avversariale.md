# 2026-10-15 — L59, revisione dell'architetto avversariale: il rivelatore di continua sulle uscite dei blocchi

Soggetto: il rivelatore di continua deciso in ADR-072, realizzato da ADR-079 e costruito in L45d2b1 (`circuits/preamp/dc_detector.py`). Lo giudico come circuito e come decisione, non come banco di prova.

**I tre obiettivi, per la parte che tocca il rivelatore:**
- **Suona bene: regge con riserve.** Il rivelatore non sta nel percorso del segnale e non tocca il rumore. La riserva è che può spegnere l'apparecchio per una sorgente sana, quando arrivano segnali sotto i 10 Hz sulle uscite fisse (R2). C'è anche un vincolo di massa da scrivere per il layout (R5).
- **Nessun bump fastidioso sulle uscite: regge con riserve.** C'è una corsa all'accensione con un guasto già presente (R4). In più, ogni scatto falso taglia la musica e spegne l'apparecchio (R2, R3).
- **Fallisce senza danneggiare la catena: non regge, finché un banco con la musica non mostra il contrario (R1).** Il rivelatore regge sui 762 guasti simulati, ma tutti sono stati simulati in silenzio. PR-30 e P10 chiedono il guasto «mentre si ascolta», e con la musica sopra la persistenza può non scattare.

---

## Come è stata fatta

**Fase 1, letti:**
- `PRB.md` (PR-2, PR-9, PR-14, PR-19, PR-22…PR-30);
- `REQUIREMENTS.md`: contesto d'uso, E6, E9, E12, P9, P10, l'architettura;
- ADR-069, ADR-072, ADR-079, e l'indice `decisions/README.md` (da lì ADR-064 e ADR-066 per l'ingresso);
- `circuits/preamp/dc_detector.py`;
- il report `reports/2026-10-14-L45d2b1-rivelatore-continua.md`;
- da `data/2026-10-14/L45d2b1/`: il README, `scelte/dimensiona.py`, `studio/dist_dc.py`, `banco/guasti.md`, le prime 40 righe di `banco/guasti.csv`, `banco/piccole.csv`, `banco/script/genera_rivelatore.py`;
- `data/2026-10-13/L45a/script/genera_canale.py`;
- `firmware/preamp_timer/README.md` e `spec/timer_spec.md`.

**Rieseguito: niente.** Ogni comando Bash è stato rifiutato dal guardiano del worktree, anche `pwd` («this command's working directory resolved to the shared checkout … Refusing to run it there»). Non ho girato né ngspice né `dimensiona.py`. **Tutte le cifre che seguono sono calcoli a mano**, ognuno scritto accanto al rilievo, oppure cifre del dossier che dichiaro come tali. Le cifre del dossier che ho ricontrollato a mano tornano:
- T_HOLD = 976k · 100n · ln((14,35 − 0,35)/(14,35 − 7,175 − 0,45)) = **71,6 ms**;
- VT = 0,04036 · VDP = **0,579 V** con VDP a 14,35 V, e **0,458 V** con VDP a 11,35 V (da VRELAY);
- il taglio peggiore ≤ **86,2 ms** per una continua da 0,81 V in su;
- il tempo sopra 0,87 V al jack fisso, a vuoto (τ = 4,7 µF · 235 kΩ = 1,1 s): 0,142 s per −0,99 V e 0,875 s per 1,93 V, uguali ai 139 e 880,7 ms di `guasti.csv`.

**Cercato in rete:** i protettori di continua dei finali (µPC1237, ESP AN-017 e P33, Silicon Chip), i brevetti sui rivelatori (a filtro con finestra, a intervallo), le ondulazioni dei dischi e la risonanza braccio-testina, l'organo e il cinema sotto i 20 Hz, il datasheet del TLV1704, la costante termica della bobina mobile. L'elenco completo è in fondo.

**Fase 2:** l'ho letta solo a rilievi scritti. Dettagli in fondo.

---

## Rilievi

### R1 — Con la musica sopra, la persistenza può non scattare: i guasti con poca continua tornano fuori da P10 proprio «mentre si ascolta», e nessun banco lo prova

- **Requisito:** PR-30 · P10 («che avviene **mentre si ascolta**», `REQUIREMENTS.md`:326) · ADR-072 (vincolo «la musica non deve farlo scattare» e il suo primo «Da riaprire se») · ADR-079 («Perché», «Il taglio arriva in tempo»).

**L'evidenza.**
1. **Tutte le 762 corse dei guasti sono in silenzio.**
   - `banco/script/genera_rivelatore.py`:215 chiama `gc.deck_tr(pos, gain, modo, False, False, …)`.
   - In `L45a/script/genera_canale.py`:237 `musica=False` vuol dire `sig = "DC 0"`.
   - I casi con la musica (`piccole.csv`) sono tutti senza guasto.
2. **Il meccanismo, a calcolo.**
   - Il temporizzatore del lato + riparte da zero appena l'uscita torna sotto +VT (`dc_detector.py`:26–30).
   - Con un guasto che porta l'uscita a VX e la musica m(t) sopra, il rivelatore non scatta finché m(t) scende sotto VT − VX almeno una volta ogni T_HOLD (62,7–81,6 ms).
   - Lo scarico è immediato: 100 nF da 3,3 V a ~20 mA (corrente di corto tipica del TLV170x) ≈ 16 µs. Basta quindi un solo avvallamento del basso.
3. **Dove morde: le uscite fisse.** Lì passa la sorgente a 0 dB, a qualunque volume: il K11 fino a 2,7 V RMS (3,8 V di picco, E6), il phono ~0,5 V. Due casi del blocco A presi da `banco/guasti.csv`, con P10 prima del rivelatore:

   | Guasto | Continua all'uscita | P10 prima | Basta che la musica… | Tempo sopra 0,87 V se il rivelatore resta fermo |
   |---|---|---|---|---|
   | JQ110B_gs | −0,99 V | 139 ms | salga sopra **+0,41 V** una volta ogni ~63–82 ms | ~140 ms, P10 fuori |
   | Q121A_ce | +1,93 V | 880 ms | scenda sotto **−1,35 V** una volta ogni ~63–82 ms | ~0,88 s, P10 fuori di ~9 volte |

   Il primo è banale per qualunque musica. Il secondo è ordinario col K11 in un passaggio forte. Il tempo sopra 0,87 V è quello di una corsa letta come differenza dalla corsa senza guasto, cioè dal gradino che decade col condensatore d'uscita.
4. **Quanti.** Sono esposti i guasti che lasciano il blocco lineare con un offset; quelli al rail no, perché lì non passa musica. Dei 148 guasti fuori da P10 senza rivelatore, **57 finiscono sotto 2 V** (ADR-079; non ricalcolato).
5. **Anche la principale**, ascoltando forte: al volume d'ascolto il blocco B porta ~1 V di picco sul basso, quindi sono esposti i guasti di B fino a ~1,5 V.
6. **La letteratura.**
   - Il principio è quello del brevetto Zenith US 4,301,330 (B. Trump, 1981): una zona morta a ±2 V e un temporizzatore da 50 ms (10 Hz) che si scarica appena il segnale rientra. Il brevetto non tratta il caso di una continua con un segnale sopra.
   - I protettori a filtro, invece, mediano: «the average value of an audio signal over any significant time period is zero» (US 5,224,169). È la loro forza contro il mascheramento, e la loro lentezza.
   - ADR-079 ha scelto la velocità sulla continua bassa. Il prezzo è il mascheramento, e non è scritto da nessuna parte.
7. **Un difetto di metodo.** P10 è scritto per un jack senza musica: con la musica |v(jack)| > 0,87 V è vero anche senza guasto. Serve la stessa lettura «per differenza dal riferimento» che V2 usa per A.

- **Severità proposta: bloccante per G1.** Per la definizione del registro: «manca l'evidenza per dire se [il requisito] lo è». È la condizione che PR-30 nomina. Il primo «Da riaprire se» di ADR-072 («nessuna soglia separa la continua di un guasto dalla musica … entro i 100 ms») scatta nel verso opposto a quello previsto: è la musica a nascondere la continua.

**Che cosa proporrei.**
1. Un banco con la musica sui guasti con poca continua (|VX| < ~3 V) nelle sette posizioni, P10 letto su d(t) = v_jack(guasto + musica) − v_jack(musica). Musica di prova: il K11 a −10…0 dBFS con energia a 40–80 Hz, più il phono a 0,5 V.
2. Se il calcolo è confermato, si torna all'utente coi numeri. Le strade che ADR-079 non ha considerato:
   - **(a) un ramo a filtro in parallelo (OR)**, lento: non tiene i 100 ms per la continua bassa, ma mette un tetto al tempo mascherato;
   - **(b) un passa-basso prima della finestra, con una persistenza più corta.** Un polo a ~10 Hz attenua di ≥ 14 dB a 50 Hz la musica che oggi fa ripartire il temporizzatore. Lo scambio va rifatto col clip asimmetrico di B, che col filtro da 3,5 ms faceva scattare;
   - **(c) la rilevazione differenziale**, uscita contro ingresso del blocco: è sorda alla musica e alla sorgente per costruzione (R2). Per i buffer delle fisse costa poco, OUTF − OUTA, due nodi a bassa impedenza. Per il blocco A serve il nodo d'ingresso, e va pesata contro E3 ed E5.

- **Fase 2:** nuovo, per quanto ho letto. Non è in NC-063 e non l'ho trovato nelle voci lette del registro.

---

### R2 — Il rivelatore impone una banda minima che il PRB esclude: sulle fisse (che non dipendono dal volume) un'ondulazione del disco, l'accensione di una sorgente o la continua di una sorgente lo fanno scattare, e lo scatto spegne l'apparecchio fino al frontale

- **Requisito:** PR-9 ed E9 («Nessuna banda minima o massima imposta oltre questo»), PR-19 («niente toni o filtri»), PR-2 (il phono MC a valvole di casa), PR-14 / ADR-066 (fino a ~0,65 V di continua dalla sorgente) · ADR-079 (limite dichiarato e «Da riaprire se»).

**L'evidenza.**
1. **L'argomento della musica presuppone una sorgente limitata a ≥ 20 Hz.** ADR-079: «nella banda di E9 un segnale periodico passa per zero almeno ogni 50 ms» (anche `dc_detector.py`:22–24). Nessun requisito lo garantisce, e PR-9 lo esclude. L'ingresso lascia passare quasi tutto:
   - C_IN 1 µF su 470 k ∥ 1 M = 320 kΩ (ADR-064, `genera_canale.py`:16–17, 183–186) dà τ = 0,32 s, cioè **0,50 Hz**;
   - le fisse sono accoppiate in continua al blocco A.
2. **Dove scatta un seno, a calcolo.** Il tempo sopra VT per ciclo è T·(½ − asin(VT/A)/π).
   - Sopra ~8 Hz un seno non scatta mai: il mezzo periodo è più corto del T_HOLD minimo.
   - Sotto, l'ampiezza minima di picco che fa scattare, all'uscita del blocco:

   | Frequenza | Nominale (VT 0,58 V, T_HOLD 71,6 ms) | All'angolo peggiore (0,39 V, 62,7 ms) |
   |---|---|---|
   | 5 Hz | 1,35 V | 0,71 V |
   | 3 Hz | 0,74 V | 0,47 V |
   | 1 Hz | 0,60 V | 0,40 V |

   - A 1 Hz l'ingresso toglie ~1 dB.
   - Il phono di casa dà ~0,5 V nominali, cioè ~0,7 V di picco. Un'ondulazione che arrivi al livello nominale fra 1 e 5 Hz basta.
3. **Le ondulazioni, in letteratura.**
   - Rod Elliott: «Any warp in a vinyl disc will cause large outputs in the infrasonic region» (ESP P99).
   - US 4,032,855: le ondulazioni hanno il picco «on the order of 4 Hz», e la risonanza braccio-testina sta fra 4 e 8 Hz «with a moderately high Q».
   - Un brevetto canadese (CA 1079202): con la risonanza a 5–14 Hz l'uscita della testina può essere «many times larger» di quella della modulazione voluta. È letto dal riassunto della ricerca; la pagina non si è aperta.
   - Lo stadio RIAA tiene ~+20 dB rispetto a 1 kHz sotto i 50 Hz, se non ha il polo IEC: lo dice il calcolo della curva.
   - **Un livello misurato in volt non l'ho trovato** (Holman 1975–76 è dietro pagamento all'AES; di Self non ho trovato un estratto). Non lo suppongo: va misurato.
4. **Il limite dichiarato è sbagliato nella forma** (ADR-079, «Limiti»; `dc_detector.py`:49–50).
   - «A volume massimo» non vale per le fisse, che portano la sorgente a 0 dB a qualunque volume.
   - «Il futuro stadio phono»: il phono è già una sorgente di PR-2.
   - «Sotto i 16 Hz» vale per una forma d'onda asimmetrica. Per un seno il limite è ~8 Hz: il banco lo conferma, il seno a 10 Hz al clip non scatta (`piccole.csv`:8, TMAX 5,68 V), anche se `genera_rivelatore.py`:153 lo etichetta «atteso lo scatto».
5. **La continua di una sorgente, contro ADR-066.** Una sorgente che si accende mentre è selezionata porta un gradino Vdc attraverso C_IN, e le fisse restano sopra VT per 0,32 · ln(Vdc/VT):
   - con Vdc = 0,65 V (il limite dichiarato da PR-14): 36 ms al nominale (non scatta), **163 ms all'angolo basso (scatta)**;
   - con 0,5 V all'angolo basso: 80 ms, contro 62,7–81,6 ms di T_HOLD.

   La finestra 0,39–0,66 V e il limite di 0,65 V di ADR-066 si sovrappongono.
6. **L'accensione dello stadio phono a valvole collegato e selezionato.** Il catodo sale in decine di secondi dietro un condensatore d'uscita. A calcolo d'ordine di grandezza può tenere le fisse sopra ~1 V per più di 100 ms. È un'ipotesi, non una misura: lo schema del phono non è disponibile (`REQUIREMENTS.md`, «Aperti»).
7. **Che cosa succede quando scatta.** GUASTO: il toroidale staccato, poi il frontale va spento e riacceso (spec 4.9). Per un evento della sorgente è una reazione pesante (R3).
8. **Gli altri fanno lo stesso, ma a valle.** ESP P33 vuole 50 V RMS a 16 Hz senza scatto e lo scatto a 10 Hz (AN-017); Zenith taglia a 10 Hz. Lo stesso confine sta nei finali, dove però a valle non c'è più niente. Un preamplificatore con un rivelatore sulle uscite non l'ho trovato fra i commerciali (sotto, «Fonti»). Lì la pratica è il condensatore d'uscita e il mute temporizzato (ESP, articolo sul muting).
9. **Casi limite, solo per completezza.**
   - Un registro da 64' ad ancia (8,18 Hz, asimmetrico): esiste a Sydney e ad Atlantic City.
   - Il cinema con effetti sotto i 10 Hz: notizie aneddotiche (Audioholics). Le sorgenti di oggi sono musica.

- **Severità proposta: maggiore**, da chiudere prima di G1. È una restrizione funzionale che il PRB esclude. Va decisa dall'utente coi numeri: un limite sotto i 16 Hz si chiede, non si dichiara.

**Che cosa proporrei.**
1. Misurare il phono di casa su un disco ondulato: picco e spettro sotto 10 Hz alla sua uscita, oppure alle fisse.
2. Riscrivere il limite: le fisse, i ~8 Hz del seno, la continua di ADR-066.
3. Portarlo all'utente. Le strade:
   - accettarlo e firmarlo;
   - la rilevazione differenziale di R1 (c), che toglie il problema alla radice;
   - una reazione a due tempi (R3).

- **Fase 2:** già deciso come limite dichiarato in ADR-079. La decisione non mi convince: l'utente non l'ha firmato, la forma è sbagliata, e il suo «Da riaprire se» non è verificabile senza misurare il phono. La parte su ADR-066 e sull'accensione della sorgente è nuova. È vicina a NC-059 (l'RCA inserito a caldo), che non considera il rivelatore.
- **Dichiarazione:** fin dall'inizio avevo nel contesto il titolo di una nota di memoria dell'utente, «Sotto i 16 Hz è plausibile — un ingresso subsonico non è un guasto». Il rilievo nasce dai documenti, ma non posso escludere che quel titolo mi abbia orientato.

---

### R3 — La stessa reazione per un guasto della scheda e per un evento della sorgente: la ritenuta col toroidale staccato è giusta per il primo e sproporzionata per il secondo

- **Requisito:** ADR-072 (vincolo «resta spento fino al frontale»), ADR-079 (punto 3, la linea su J4 coi tre gate; punto 4, la ritenuta nel firmware), PR-24.

**L'evidenza.**
1. Il µPC1237 lascia scegliere fra ritenuta e riarmo automatico (pin 3, «Work as either latching function or automatic resetting function»; datasheet UTC). Zenith riarma da sé dopo ~5 s. Nota sulla variante che stacca l'alimentazione: «The use of a latching relay would avoid this problem but the listener would be required to manually reset». È la stessa oscillazione che ADR-079 ha trovato (Contesto, punto 2): **qui ADR-079 è confermata dalla letteratura.**
2. **Una distinzione che oggi non si usa.** Lato sorgente l'ingresso è in alternata (0,5 Hz, τ 0,32 s): una sorgente non può tenere una continua all'uscita del blocco per più di ~1 s; un blocco guasto sì.
3. **Come si potrebbe dividere la reazione.** Subito e in hardware, mute e VRELAY (le scelte 1 e 6 di ADR-072, ridotte all'essenziale). Il toroidale e la ritenuta solo se la continua resta oltre ~1 s.
   - Il prezzo è la scelta 10, il calore di R144. Ma nel caso C145 in corto il sorvegliante e il firmware staccano il toroidale da soli a 106 ms (ADR-079, tabella).
   - Togliere VRELAY lascia cadere anche i relè del selettore: il ritorno dopo l'evento chiede al firmware una sequenza, come per il buco di rete.

- **Severità proposta: minore.** Conta se R2 si conferma.
- **Che cosa proporrei:** portare all'utente, con R2, la reazione a due tempi.
- **Fase 2:** già deciso (ADR-072, parole dell'utente). Mi convince per i guasti della scheda; lo riaprirei solo se la misura di R2 mostra scatti dalle sorgenti.

---

### R4 — All'accensione con un guasto già presente, lo scatto e la chiusura dei jack cadono negli stessi millisecondi

- **Requisito:** PR-30 / P10 (il colpo), V2 all'accensione · ADR-079 punto 5 · spec 4.1.

**L'evidenza, a calcolo, non simulata col firmware.**
1. **Il rivelatore:** l'inibizione dura 99 ms (93–105 ms agli angoli) da quando compare VDP, più T_HOLD 62,7–81,6 ms.
   - Sul banco del rivelatore da solo lo scatto arriva 180 ms dopo l'inizio della rampa (`README`, «Il controllo»; il report).
   - Sull'alimentatore del banco i rail salgono in ~31 ms: lo scatto cade a ~180–200 ms dallo stacco del toroidale, ~215 agli angoli.
2. **Il firmware** (spec 4.1): rail buoni per 100 ms, poi `VRELAY_EN`, poi ≥ 50 ms, poi il rilascio. I jack si chiudono a ≥ 34 + 150 ms + il tempo d'operazione del G6K, cioè a **~185–190 ms**.
3. Il commento di `dc_detector.py`:150–153 dice che l'inibizione «ends before the jacks can close». È vero, ma non basta: dopo l'inibizione serve ancora T_HOLD.
4. **L'effetto:** un colpo di qualche ms fino a ~20 ms, fino al clip del finale (~114 dB SPL di picco a 1 m, ADR-069). Resta dentro i 100 ms di P10, ma il resto del progetto lo evita del tutto.
5. Con NC-063 i tempi cambiano.

- **Severità proposta: minore.**
- **Che cosa proporrei:** nel firmware, nessun rilascio prima di (inibizione + T_HOLD massimo + margine) dalla comparsa dei rail, cioè ~250 ms, con `DC_FLT` alta. È una riga di spec e un test con un falso. Va verificato al punto fisso su un caso «guasto già presente».
- **Fase 2:** nuovo. È vicino a NC-063, che riguarda la durata dell'inibizione e non questa corsa.

---

### R5 — Le correnti del rivelatore scorrono nella massa audio

- **Requisito:** PR-5 / E5, PR-8 · P4 (massa a stella).

**L'evidenza.**
1. I comparatori, C_T, C_SH e C_REF stanno sulla massa audio (`dc_detector.py`:225–263; la porta 0 del subcircuito è la massa audio).
2. **Lo scarico di C_T:** a ogni rientro nella finestra il comparatore scarica fino a ~0,33 µC (100 nF a 3,3 V, il TMAX dei casi a 20 Hz) a ~20 mA, in ~16 µs. Il TLV170x ha 20 mA tipici di corto in assorbimento (datasheet TI SBOS589D).
   - Su 1 mΩ di rame condiviso fanno 20 µV di picco, ~19 dB SPL a 1 m.
   - Su 10 mΩ fanno 200 µV, ~39 dB SPL.
   - Succede solo con la musica oltre ±0,58 V, quindi è mascherato, e V4 a 0,2 V non lo vede mai.
3. **La corrente di segnale verso C_SH:** fino a ~47 µA, attraverso 300 kΩ.

- **Severità proposta: osservazione**, da scrivere come vincolo di layout per G2.
- **Che cosa proporrei:** il rivelatore su un'isola di massa propria, riportata alla stella in un punto. Una resistenza di qualche centinaio di Ω in serie fra l'uscita di ogni comparatore e il suo C_T: lo scarico resta ≪ un semiperiodo.
- **Fase 2:** nuovo.

---

### R6 — Cifre vecchie e un'etichetta sbagliata attorno al rivelatore

- **Requisito:** la regola di tracciabilità di `CLAUDE.md` (i commenti in `circuits/` puntano al ragionamento).

**L'evidenza.**
1. `dc_detector.py`:32–33 e 130 dicono «the cut <= 91,5 ms»; ADR-079 e `dimensiona.py` dicono **86,2 ms**. 91,5 = 81,6 + 5,9 + 1 + 3: è il filtro da 3,5 ms della prima stesura.
2. `genera_rivelatore.py`:153: il seno a 10 Hz «atteso lo scatto». Non scatta, e non deve (R2, il limite di ~8 Hz).

- **Severità proposta: minore.**
- **Che cosa proporrei:** correggere i due commenti.
- **Fase 2:** nuovo.

---

### R7 — Il principio ha un precedente che ADR-079 non cita, e la finestra è larga ±26 % agli angoli

- **Requisito:** ADR-079 («Alternative scartate») · la soglia contro P10.

**L'evidenza.**
1. **Il precedente.** Zenith US 4,301,330 (1979–81) è lo stesso principio: soglia, temporizzatore che riparte, 50 ms per 10 Hz, la menzione del «turntable rumble». Citarlo avrebbe portato con sé le sue debolezze note (R1, R2) e la sua soluzione al ciclo (R3). **Il principio regge**: è una scelta nota e difendibile, non un'invenzione fragile.
2. **La finestra.**
   - VT va da 0,39 a 0,66 V perché è la piccola differenza di due tensioni grandi: S sta a VDP/2 ≈ 7,2 V e la finestra vale ±0,145 V su S. Lo 0,1 % su 7,2 V dà ~7 mV per resistenza, ×4 riportato all'uscita.
   - È anche proporzionale a VDP: 0,458 V da VRELAY. «Ratiometrico» vale per T_HOLD, non per VT.
   - L'angolo basso è quello che peggiora R2.

- **Severità proposta: osservazione.**
- **Che cosa proporrei:** citare il precedente nell'ADR che verrà; stringere VT agli angoli se R2 resta con la soluzione di oggi.
- **Fase 2:** nuovo.

---

### Quello che ho controllato e regge

- **L'alimentazione.** Da VDP = max(VPLUS, VRELAY) con due diodi, perché il filo del + aperto (scelta 8) sia visto: corretto e a basso costo.
- **La 634 kΩ verso VMINUS.** Annulla la corrente dello spostamento in un punto solo; a calcolo +0,18 µA a 0 V, carico incrementale ~4 µS.
  - Il rumore e il ripple di VMINUS e di VDP che passano dai 634 k e dai 300 k nell'uscita del blocco (< 1 Ω) sono trascurabili.
  - Le variazioni di pochi µA sulla corrente di VPLUS ai cambi di stato dei comparatori, a calcolo, valgono nV ai rail.
- **I 12 canali.** Con le uscite a collettore aperto, «tieni il temporizzatore a zero se sei dentro la finestra» chiede un AND che il collegamento in OR dei collettori non fa. Due temporizzatori per uscita sono la realizzazione naturale; non ho trovato una versione più economica equivalente.
- **La linea su J4, i tre BAT54, la ritenuta nel firmware con i 2 ms «ad alimentazione buona», la logica senza firmware.** Coerenti con PR-24. Il ciclo con un firmware vivo ma sbagliato è dichiarato. Sarebbe comunque innocuo per i jack, perché all'accensione il guasto si vede prima della chiusura, salvo R4.
- **I tempi contro P10, in silenzio.** Le cifre del dossier tornano coi miei calcoli. La costante termica della bobina mobile è «of the order of a few seconds» (US 8,259,953): 100 ms è prudente per il calore.

---

## Fase 2: che cosa ho letto, e che cosa cambia

**Letto:**
- in `NONCOMPLIANCE.md`, la voce **NC-063**;
- cercandola, la testata del registro, le voci NC-059, NC-061 e NC-062, e parte delle voci chiuse;
- non ho letto `STATE.md`, `NEXT-SESSION.md` né gli altri report.

**Non ho tolto né ammorbidito nessun rilievo.** Le note di stato sono nei singoli rilievi.
- **NC-063** (la partenza morbida contro l'inibizione) la confermo. Aggiungo che, chiudendola, va ricontrollata anche la corsa di R4.
- **NC-059** (l'RCA inserito a caldo) si incrocia con R2: col rivelatore, inserire a caldo una sorgente a terra con 0,65 V di continua può anche bloccare l'apparecchio in GUASTO all'angolo basso.

## Le ADR che riaprirei

- **ADR-079**: le motivazioni «la musica non lo fa scattare» e «nessun guasto fuori da P10» valgono in silenzio e per una sorgente limitata a ≥ 20 Hz (R1, R2). Il suo «Da riaprire se» sulle sorgenti sotto i 16 Hz non è verificabile senza misurare il phono di PR-2.
- **ADR-072**: il primo «Da riaprire se» è scattato nel verso del mascheramento (R1). La ritenuta col toroidale, solo se R2 si conferma (R3).

## Le semplificazioni proposte

| Sottosistema | Che cosa si toglie | Che cosa si perde | Voce del PRB che regge comunque |
|---|---|---|---|
| Rivelatore, 12 canali | niente | — | nessuna economia equivalente trovata con la logica a collettore aperto |
| Compensazione a 634 kΩ (6 resistenze) | si toglie alzando di 10× lo spostamento (3 M / 1,5 M / 3 M, 0,47 nF) | 10× più sensibilità alla corrente d'ingresso del comparatore (da verificare sul datasheet) e resistenze da MΩ allo 0,1 % | PR-30, se l'errore resta ≪ 0,58 V; guadagno modesto, non la raccomando con forza |
| Reazione allo scatto | la ritenuta per gli eventi brevi (R3) | parte della rapidità sul calore della scelta 10, già coperta dal sorvegliante | PR-30 e PR-24 restano: il mute e VRELAY subito, in hardware |

**Un'osservazione sull'eccesso.** Il rivelatore non è sovradimensionato rispetto a ciò che PR-30 chiede. È PR-30, con un apparecchio a valle generico in continua e senza protezione, a renderlo necessario. Nei preamplificatori di riferimento che ho cercato non ho trovato un rivelatore sulle uscite.

## Le omissioni cercate

1. Il guasto con la musica (R1): l'omissione principale.
2. Le sorgenti e i loro gesti: le ondulazioni del disco, l'accensione del phono selezionato, la continua di una sorgente contro ADR-066 (R2).
3. L'accensione con un guasto già presente, col firmware al punto fisso (R4).
4. **Un buco di rete parziale.** VDP scende senza azzerarsi: il diodo scarica POR solo fino a ~VDP + 0,6 V, POR resta sopra VDP/2, e l'inibizione non si riarma mentre i blocchi si ripolarizzano. Non ho trovato una corsa «discesa parziale e ritorno»; quelle di `accensione` scendono fino a zero. Minore. Il firmware forse va già in GUASTO in un abbassamento di rete per altre vie (spec 4.5); non l'ho verificato.
5. **Un guasto del rivelatore che lo fa scattare** (per esempio la 300 k verso massa aperta, che porta S a 2/3 di VDP). L'apparecchio non si accende più, senza dire perché. È nella direzione sicura, da girare alla diagnosi (L58).

## Fonti consultate

- [ESP AN-017, DC detection](https://sound-au.com/appnotes/an017.htm): «All DC protection schemes rely on a filter…»; P33 col filtro 100 k / 10 µF (0,16 Hz), 50 V RMS a 16 Hz senza scatto e lo scatto a 10 Hz; soglie ±0,58…±4 V; < 40 ms con 35 V.
- [ESP Project 208](https://sound-au.com/project208.htm): solo il riassunto della ricerca, gli scatti falsi con troppa potenza a bassissima frequenza.
- [ESP Project 99](https://sound-au.com/project99.htm): le ondulazioni «large outputs in the infrasonic region», 0,55 Hz; il rumble a 10 Hz, −32 dB.
- [ESP, il muting](https://sound-au.com/articles/muting.html): solo il riassunto; nei preamplificatori il mute temporizzato all'accensione.
- [Zenith US 4,301,330 (B. Trump)](https://patents.google.com/patent/US4301330A/en): zona morta ±2 V, 50 ms, 10 Hz; riarmo dopo ~5 s; ciclo e ritenuta manuale.
- [US 5,224,169](https://patents.google.com/patent/US5224169): passa-basso più finestra; «the average value of an audio signal … is zero».
- [µPC1237, datasheet UTC](https://www.hifisonix.com/wp-content/uploads/2021/09/UPC1237.pdf): soglie del pin 2 +0,62 / −0,17 V; filtro d'esempio 56 k / 330 µF; ritenuta o riarmo a scelta.
- [Linear Audio, UK-3](https://linearaudio.net/sites/linearaudio.net/files/UK-3%202008050501.pdf): solo il riassunto, una soglia del µPC1237 a 0,6 V.
- [Silicon Chip, Multi-Channel Speaker Protector](https://siliconchip.com.au/Issue/2022/January/Multi-Channel+Speaker+Protector): solo il riassunto, filtro a 0,25 Hz, 40 V in ~100 ms.
- [US 4,032,855](https://patents.google.com/patent/US4032855A/en): ondulazioni ~4 Hz, risonanza 4–8 Hz, nessuna ampiezza.
- [CA 1079202](https://brevets-patents.ic.gc.ca/opic-cipo/cpd/eng/patent/1079202/summary.html): «many times larger»; letto dal riassunto, la pagina dà HTTP 500.
- [Stereophile, commento di un lettore](https://www.stereophile.com/comment/355637): solo il riassunto, la risonanza da ~10 a ~5 Hz con braccio pesante.
- [Holman, AES](https://aes2.org/publications/elibrary-page/?id=3054): dietro pagamento, **nessun dato**.
- [Self, Electronics for Vinyl](https://www.routledge.com/Electronics-for-Vinyl/Self/p/book/9781138705456) e il suo thread su diyAudio: **nessun dato**, il thread è bloccato dalla verifica del browser.
- [Cordell, Designing Audio Power Amplifiers](https://www.routledge.com/Designing-Audio-Power-Amplifiers/Cordell/p/book/9781138555440): solo l'indice, **nessun dato**.
- [Wikipedia, List of pipe organs](https://en.wikipedia.org/wiki/List_of_pipe_organs): due soli 64' veri.
- [Audioholics](https://forums.audioholics.com/forums/goto/post?id=1200793): il cinema sotto i 10 Hz, aneddotico.
- [Home Theater Forum, 25 brani sotto i 20 Hz](https://www.hometheaterforum.com/25-infrasonic-music-tracks-that-prove-why-a-world-class-subwoofer-is-essential/): HTTP 403, **nessun dato**.
- [TI TLV1704, SBOS589D](https://www.ti.com/document-viewer/TLV1704/datasheet/specifications): corrente di corto in assorbimento 20 mA tipici, 55 µA per canale.
- [US 8,259,953](https://patents.justia.com/patent/8259953): solo il riassunto, la costante termica della bobina «a few seconds».
- **Non trovati:** un livello misurato in volt delle ondulazioni all'uscita di un phono; un preamplificatore commerciale con un rivelatore di continua sulle uscite; le pagine di Self e Cordell sulla protezione dalla continua.

## Sintesi

1. Il principio (la persistenza fuori da una finestra) è noto e difendibile: è il brevetto Zenith del 1981. In silenzio tiene P10 su tutti i 762 guasti del dossier.
2. Tutti i guasti sono stati simulati in silenzio. Con la musica sopra, il temporizzatore riparte, e i guasti con poca continua sulle fisse (e sulla principale ascoltando forte) possono restare fuori da P10: R1, bloccante proposta, da provare su un banco con la musica.
3. L'argomento «la musica non ha continua» presuppone una sorgente limitata a ≥ 20 Hz, che PR-9 esclude. Sulle fisse, a qualunque volume, un'ondulazione fra 1 e 5 Hz da ~0,6–1,35 V di picco (0,4–0,7 V agli angoli) o una sorgente con la continua di ADR-066 lo fanno scattare e bloccano l'apparecchio: R2, maggiore. Va misurato il phono di casa.
4. Minori: la corsa all'accensione fra scatto e jack (R4), le correnti nella massa audio (R5), cifre vecchie nei commenti (R6). La ritenuta col toroidale è sproporzionata per gli eventi della sorgente (R3).
5. Alimentazione, 634 kΩ, linea su J4, gate in hardware e ritenuta nel firmware reggono. Non ho trovato eccesso di progetto. Nulla è stato rieseguito: Bash era bloccato e ogni cifra è un calcolo a mano.

**File citati:**
- `/Users/roberto/EDA/circuits/preamp/dc_detector.py`
- `/Users/roberto/EDA/docs/preamp/decisions/ADR-072-rivelatore-di-continua-sulle-uscite.md`
- `/Users/roberto/EDA/docs/preamp/decisions/ADR-079-rivelatore-persistenza-linea-ritenuta.md`
- `/Users/roberto/EDA/docs/preamp/data/2026-10-14/L45d2b1/banco/script/genera_rivelatore.py`
- `/Users/roberto/EDA/docs/preamp/data/2026-10-14/L45d2b1/banco/guasti.csv`
- `/Users/roberto/EDA/docs/preamp/data/2026-10-14/L45d2b1/banco/piccole.csv`
- `/Users/roberto/EDA/docs/preamp/data/2026-10-13/L45a/script/genera_canale.py`
- `/Users/roberto/EDA/firmware/preamp_timer/src/../spec/timer_spec.md`
