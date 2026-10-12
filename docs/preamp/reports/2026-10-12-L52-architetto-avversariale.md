# 2026-10-12 — L43, revisione dell'architetto avversariale

*Lotto L52: è la seconda revisione dell'architetto, la prima fu L43a. Il titolo segue il formato della mia definizione.*

**Come è stata fatta.** In questa sessione Bash ha rifiutato ogni comando, anche `pwd` e `ngspice --version`, con «worktree-isolated session… refusing to run». Quindi **non ho rieseguito nessun deck né nessuno script**, e non ho scritto niente sotto `/tmp/l52/`.

Le cifre vengono da tre fonti:
- i file del prodotto che ho letto con lo strumento di lettura: il dossier, `circuits/preamp/*.py`, `docs/preamp/data/2026-10-01/L46a/sintesi.csv`, il datasheet e la nota applicativa dell'LSK489 in `vendor/`;
- i calcoli a mano che riporto nel testo;
- la letteratura, con l'URL.

Ogni conclusione che dipende da una simulazione che non ho rifatto lo dice.

Fase 1 fatta senza leggere `NONCOMPLIANCE.md`, `STATE.md`, `NEXT-SESSION.md` e `reports/`. In fase 2 ho letto `NONCOMPLIANCE.md`, una parte del diario di `STATE.md` e il report degli esiti di L43a. Nessun rilievo è stato tolto o ammorbidito dopo la fase 2.

## Verdetto per obiettivo

1. **Suona bene** — **regge con riserve**:
   - la topologia è di letteratura, e niente di ciò che la letteratura associa all'asprezza è presente;
   - riserva 1: tutte le cifre sono di modello;
   - riserva 2: un meccanismo di distortion d'ingresso non considerato fissa la distorsione ad alta frequenza delle istanze a guadagno unitario;
   - riserva 3: V4 non è verificato sulla catena né sulla sorgente peggiore.
2. **Nessun bump fastidioso** — **regge**, in simulazione:
   - 250 verdetti su 250, cioè gli esiti del banco del mute;
   - selettore ≤ 19,8 µV (~19 dB SPL);
   - spegnimento e perdita di rete a ~40 nV;
   - restano dichiarati il clic del rilascio (+5,2 dB sul taglio ideale, rimbalzi del contatto) e il corto della linea relè (76,9 dB SPL, guasto accettato).
3. **Fallisce senza danneggiare** — **regge con riserve**:
   - corti, mute e guasti dell'alimentatore sono coperti bene;
   - il guasto singolo di un componente nei blocchi audio e il relè del jack incollato non sono analizzati;
   - le uscite fisse, che vanno a due amplificatori per cuffia, non hanno un tetto di non-danno.

---

## Rilievi, dal più grave

### R1 — Guasti singoli nei blocchi audio, e nessun tetto sulle uscite fisse

- **Voce/requisito**: PR-22, PR-23, PR-24 · P7, P9 · ADR-043, ADR-046, ADR-051.
- **Il rilievo**: il guasto di un dispositivo dei blocchi, o un contatto del mute incollato, porta al jack un gradino di decine di dB sopra il tetto di non-danno, e nessun requisito né banco lo esercita. PR-23 dà il tetto (0,87 V, 112,2 dB SPL) solo al jack principale e solo per i guasti dell'alimentatore.
- **L'evidenza** (calcolo, non simulato):
  - **Un blocco che va a un rail** (MJE in corto, VAS o coda guasti) porta OUT al clip: +13,1 / −13,8 V (dossier §17). Il 4,7 µF film lo passa intero al jack: 13,8 V, cioè 136 dB SPL con la formula del PRB. Il finale da 30 W lo limita a ~21,9 V di picco su 8 Ω, ~114 dB SPL: oltre il tetto di 112,2.
  - **Sulle fisse** la Stax SRM-T1 ha 60 dB di guadagno e 300 V RMS massimi ([kenrockwell.com](https://kenrockwell.com/audio/stax/srm-t1.htm)): un gradino di 13,8 V la porta al clip. È ~+11 dB sopra il picco del K11 (3,8 V) e ~+26 dB sopra il phono (0,7 V di picco).
  - **Il caso si limita da sé solo in parte.** Con la geometria iii, un guasto che avviene a mute inserito non arriva al rilascio: il lato del condensatore è a massa, il condensatore si carica alla continua guasta, e al rilascio il jack resta a ~0 V. Il guasto **durante l'ascolto** arriva intero, e decade con τ = 4,7 µF × 69 kΩ ≈ 0,32 s.
  - **Un contatto del mute incollato** toglie ogni protezione all'accensione e alla perdita di rete. ADR-043 riporta 8,9–17,5 V al jack quando i rail collassano col contatto chiuso (dati L29c).
- **Severità proposta**: **maggiore**, da decidere **prima di G1** e non solo prima di G2. Il rimedio naturale tocca la topologia: un rivelatore di continua sulle uscite dei blocchi, ingresso di sola rilevazione ammesso da ADR-022, che apra il sink di `MUTE_CMD` esistente.
- **Fase 2**: **già noto (NC-042, aperta; la FMEA è a piano come L45; anche NC-046 per la metrica delle cuffie)**. La voce ha la severità giusta, ma il termine «prima di G2» non mi convince: se la FMEA conclude per un rivelatore, il circuito cambia dopo il congelamento.

### R2 — +3/+10 dB e trim non servono alla catena dichiarata, e oggi costano più di quando furono difesi

- **Voce/requisito**: PR-2 contro PR-3, PR-17, PR-18 · E2, F2, F5, F8, F9 · ADR-004, 019, 026, 027, 030, 033, 041, 045, 051.
- **Il rilievo**: con le sorgenti e il finale di PR-2 il guadagno sopra 0 dB non serve mai. Il trim serve soprattutto a dare margine al +10 dB col K11. Insieme si portano dietro metà della logica dei relè e l'unico guasto accettato sopra l'obiettivo.
- **L'evidenza**:
  - **Il phono a 0 dB** porta 0,5 V a un finale che va in piena potenza con 0,612–0,75 V. Fanno 30 W × (0,5/0,68)² ≈ 16 W, cioè ~108 dB SPL a 1 m in continua; i picchi del vinile sopra i 5 cm/s mandano già il finale in clip.
  - **Il K11** chiede −29 dB al volume, il centro della corsa (ADR-001).
  - **Il commento HEADROOM di `gain_block.py`** dice del trim «This is what the trim is FOR»: dare margine al +10 dB col K11.
  - **Il costo, aggiunto dopo che R4 di L43a fu respinto**:
    - i relè di autoritenuta K11/K12 col polo ponte (ADR-041);
    - il permissivo K6, `PERMIT_CMD` e Δ in hardware (ADR-045);
    - la tenuta di `VRELAY` per Δ (NC-050);
    - **l'unico guasto singolo accettato sopra l'obiettivo dei 2 mV**: il corto della linea a 12 V, 14,86 mV, 76,9 dB SPL. Esiste solo perché il guadagno cade da +10 a 0 dB coi jack ancora collegati (ADR-051: «69 mV è il salto del blocco a +10 dB → 0 dB a jack collegato»);
    - il caso peggiore di E5 (5,5 µV contro ~1,6 a 0 dB);
    - il margine di +0,28 dB di NC-009;
    - la matrice V1 triplicata.
  - **Che cosa resta togliendoli**: PR-6 regge (K11 a 0 dB con +6,58 dB di margine, M1, dossier §10), e PR-20 regge con meno eventi.
  - **Che cosa si perde**: il guadagno per un finale o una sorgente futuri (ADR-001, «Da riaprire se»). Si può tenere aperta l'opzione lasciando le impronte non montate.
- **Severità proposta**: **maggiore** (proposta di semplificazione del PRB).
- **Fase 2**: **già deciso: respinto dall'utente in L43a (R4)**, senza una ADR. Non mi convince più per una ragione nuova: dopo il rifiuto la complessità è cresciuta di tre ADR (041, 045, 051), e il guasto accettato di ADR-051 è figlio diretto del +10 dB.

### R3 — Il microcontrollore e il firmware non hanno più la loro ragione dopo ADR-062

- **Voce/requisito**: PR-24, PR-25 · P9 · ADR-048 punto 6, ADR-049, ADR-062.
- **Il rilievo**: ADR-048 scelse il temporizzatore ibrido scartando quello «tutto analogico», con due ragioni. Una era il convertitore esponenziale delle LDR su 6 decadi, che ADR-062 ha tolto. L'altra erano i «molti stati». Nessuna ADR ha riesaminato il micro senza le LDR.
- **L'evidenza**:
  - ADR-062 toglie DAC, convertitori e profilo, e dice solo «il micro, Δ e Δ₂ in hardware … restano».
  - L'ordine di sicurezza è già tutto in hardware: Δ RC su comparatore, il sorvegliante sul gate del sink, i pull-down (ADR-049).
  - Il firmware fa ancora: debounce, OR con SW3, accensione, spegnimento morbido, buco di rete, ritenuta dopo un guasto.
  - Il dossier §27 dice: «`src/main_attiny.c` non è scritto» e «nessun falso è stato fatto fallire sul circuito dopo L41b2».
  - Senza lo standby (R4) gli stati si riducono a ritardo d'accensione, mute dal tasto e mute dal sorvegliante. Lo fanno i comparatori TLV1702 già presenti con qualche RC, e PR-24 diventa vero per costruzione.
- **Severità proposta**: **maggiore** (semplificazione, tocca la topologia dell'alimentatore prima di G1).
- **Fase 2**: **nuovo**. NC-045 trattava il pilota delle LDR e annotava «il micro resta per il trim e il permissivo». Il permissivo però è già un RC in hardware.

### R4 — Lo spegnimento morbido e lo standby non servono a PR-20: la perdita di rete fa lo stesso lavoro

- **Voce/requisito**: PR-25, PR-20 · P3, P9(a) · ADR-046, ADR-048 punti 2–4 · NC-037.
- **Il rilievo**: il silenzio allo spegnimento lo garantisce già il rivelatore di rete. Il secondo trasformatore, il relè del toroidale K501, lo standby e i due stati del firmware comprano solo un interruttore frontale a bassa tensione e lo standby.
- **L'evidenza**:
  - Dossier §24, picco al jack:
    - spegnimento morbido 33,9 nV;
    - **perdita di rete 39,2 nV** (−34,7 dB SPL);
    - entrambe ~68 dB sotto la soglia di V2.
  - Il mute si rilascia a 14,3 ms dalla perdita, mentre i rail arrivano a 13,5 V dopo 63–123 ms (§20).
  - Un interruttore di rete diretto, sul retro o al frontale con un'asta di rinvio, dà quindi lo stesso risultato acustico.
  - ADR-048 punto 3 voleva `VRELAY` su un avvolgimento proprio perché il rail + era «il rail debole (PSRR+ ~23 dB a 10 kHz)». Con la cella di ADR-056 il PSRR+ vale 78,5 dB a 10 kHz (§11), quindi la premessa non vale più.
  - Si guadagna circa 1 W nel telaio (`VRELAY` regolata, rame e ferro di T2: §18), e NC-037 scompare.
- **Severità proposta**: **minore** (proposta).
- **Fase 2**: **già deciso (ADR-048, scelta dell'utente «la 3 con l'interruttore posteriore»)**. L'argomento acustico è nuovo: non era sul tavolo quando fu scelto.

### R5 — Nelle istanze a guadagno unitario la distorsione ad alta frequenza sembra fissata da un meccanismo d'ingresso, e V4 non guarda dove peggiora

- **Voce/requisito**: PR-8, PR-15 · V4 · ADR-014, ADR-055, ADR-065.
- **Il rilievo**:
  - la premessa di ADR-014, «V_ds costante significa parametri che non ondeggiano col segnale», è falsa nei sei blocchi su otto che lavorano a guadagno unitario. Lì le sorgenti dei JFET seguono il segnale e il cascode tiene fermo il drain, quindi V_dg oscilla di tutto il modo comune;
  - la C_gd non lineare, vista attraverso l'impedenza di sorgente, produce una distorsione davanti all'anello, che la controreazione non corregge;
  - V4 la misura con una sorgente da 2,5 kΩ, che per questo meccanismo è quasi il caso migliore;
  - V4 non è misurato sulla catena, mentre il requisito dice «su ogni uscita».
- **L'evidenza**:
  - **Indizio 1** (dossier §13): a parità d'uscita il modo 0 dB distorce quasi quanto il +10 dB a 20 kHz (0,000526 % contro 0,000596 %), pur avendo 10,7 dB di guadagno d'anello in più (78,72 contro 68,02 dB, §6). Una distorsione limitata dall'anello starebbe ~10 dB più in basso.
  - **Indizio 2** (`sintesi.csv`, VAS 56 Ω): il Miller da 1 nF a 330 pF compra +9,6 dB d'anello a 20 kHz, ma la THD a 20 kHz scende solo da 0,00098 a 0,00050 % (−5,8 dB). C'è un pavimento che l'anello non tocca.
  - **Il meccanismo è documentato**:
    - TI, Caldwell, «Distortion and source impedance in JFET-input op amps» ([slyt595](https://ti.com/lit/pdf/slyt595)): la capacità d'ingresso varia col modo comune; la corrente distorta, presa dalla sorgente, cade sulla R_S; il rimedio è un'impedenza uguale sul ramo di controreazione;
    - Cordell per Linear Systems ([nota applicativa LSK489](https://www.linearsystems.com/applicationnotes/lsk489-app-note)): «the JFET junction capacitances are nonlinear», con IMD che cresce con la frequenza se la sorgente è ad alta impedenza;
    - Self lo misura sugli inseguitori ([eeNews Europe](https://www.eenewseurope.com/en/op-amps-in-small-signal-audio-design-part-2-distortion-in-bipolar-and-jfet-input-op-amps/)).
  - **Ordine di grandezza, calcolo**:
    - h2/h1 ≈ R_net · C_gd · ω · a · V_p / 2;
    - C_gd ≈ 2,5 pF (Crss 2 pF a 15 V dal datasheet, `LSK489DSRevA38.pdf` p. 2);
    - a = m/(φ+V_dg) ≈ 0,5/9,7 ≈ 0,052/V;
    - R_net è la differenza fra l'impedenza di sorgente e quella del ramo di controreazione, cioè R_F 1,5 kΩ, perché a 0 dB R_g è aperta.
  - **Che cosa ne viene**:
    - sul banco di V4 (2,5 kΩ, R_net 1 kΩ), 0,2 V a 20 kHz: ~0,0002 %, lo stesso ordine del pavimento del modello;
    - **volume in cima** (sorgente ~0, R_net 1,5 kΩ): peggio del banco;
    - **bilanciamento girato** (5,6 kΩ, R_net 4,1 kΩ), 2 V: ~0,009 %, a ridosso del tetto di stress di 0,01 %;
    - **blocco A col K11 e buffer delle fisse** (sorgente ~0, R_net 1,5 kΩ), 2,7 V a 20 kHz: ~0,005 % ciascuno, e sulle fisse si sommano due stadi.
  - **Sull'udibilità**: il meccanismo produce soprattutto h2 ultrasonica. Il prodotto di differenza in banda è ridotto dalla derivata (i ∝ d(v²)/dt), circa −26 dB a 1 kHz contro 40 kHz, coerente col CCIF a −125,6 dB. Per carattere è benigno.
  - **La prova che lo falsifica**: correre `data/2026-10-10/L51c/distorsione/deck/oggi/thd_20k.cir` a 0 dB con la sorgente a 0 / 1,5 / 2,5 / 5,6 kΩ. Se la THD segue |R_S − 1,5 kΩ| è questo meccanismo. Rimedi di letteratura: il cascode pilotato, che tiene costante V_ds ([Linear Systems](https://www.linearsystems.com/post/boosting-performance-with-low-noise-cascode-structures)) e risolve anche il margine di modo comune che `gain_block.py` ha dovuto comprare alzando il riferimento; oppure R_F adattata nelle istanze a guadagno unitario.
- **Severità proposta**: **minore** per il suono. **Maggiore** per la verifica: V4 va rifatto sulla sorgente peggiore e sulla catena, prima di dichiararlo conforme.
- **Fase 2**: **nuovo**. NC-039 parlava della crescita verso gli acuti dovuta al Miller, un meccanismo diverso. La chiusura di NC-039 annota che «la h2 domina a ogni frequenza»: è coerente con questa ipotesi.

### R6 — Il dispositivo d'uscita è sovradimensionato, e la sua capacità ha guidato tre ADR di compensazione

- **Voce/requisito**: PR-7, PR-8 · ADR-017, ADR-025, ADR-042, ADR-054.
- **Il rilievo**:
  - il MJE15032/33 è un 8 A / 250 V. Il datasheet specifica h_FE e f_T a 0,5 A ([onsemi](https://www.onsemi.com/pdf/datasheet/mje15032-d.pdf), p. 2), mentre qui lavora a 20 mA;
  - la CJE di 3,06 nF del modello è la causa isolata della caduta di V1 (ADR-042) e della distorsione verso gli acuti (NC-039);
  - la potenza peggiore, 0,36 W, sta in un contenitore da driver con C_ob di decine di pF: per esempio il 2SA1837 Toshiba, 30 pF;
  - restano da verificare T7 e T8.
- **Severità proposta**: **minore**. Oggi i numeri reggono.
- **Fase 2**: **già noto (NC-039) e già deciso (ADR-054)**. Lì i ZXT «da soli compravano margine ma non distorsione». Mi convince per i ZXT; un driver di taglia intermedia non risulta valutato. Da riaprire con «Da riaprire se» di ADR-042, misurando la f_T sul prototipo.

### R7 — E3 misura una cosa diversa dalla ragione per cui esiste

- **Voce/requisito**: PR-6 · E3 e la sua nota.
- **Il rilievo**: E3 nasce dal condensatore d'uscita del phono, cioè dal taglio in bassa frequenza. Lo si misura invece come minimo di |Zin| su 20 Hz–20 kHz, e il minimo, 108,2 kΩ, lo fanno i 68 pF del selettore a 20 kHz.
- **L'evidenza**: 68 pF davanti a un cathode follower da 430 Ω mettono il polo a 1/(2π·430·68 pF) ≈ 5,4 MHz, irrilevante. Il margine dell'8 % che vincola R_SEL (ADR-064) è artificiale: la grandezza pertinente è la parte resistiva a 20 Hz (~320 kΩ).
- **Severità proposta**: **minore**.
- **Fase 2**: **nuovo**.

---

## La domanda dell'utente: il blocco di guadagno ha caratteristiche sonore buone?

La premessa va precisata. Il suono della principale passa per **due** istanze del blocco in serie (A, poi B) più i passivi: il condensatore d'ingresso PP da 1 µF, il trim, C_T PP da 10 µF, il bilanciamento MN, l'RK27 al carbone, il 4,7 µF film e i contatti G6K. Le fisse passano per A e per un buffer. Quindi sì: il blocco è l'elemento attivo che decide, e conta due volte.

**Topologia.** È la classica a tre stadi di Lin: ingresso differenziale, VAS integratore, inseguitore d'uscita. È quella di Self per il «Blameless», e Self elenca come cure dell'ingresso il bilanciamento con specchio e il cascode, presenti qui ([sintesi hifisonix](https://hifisonix.com/wp-content/uploads/2010/10/Douglas-Selfs-8-Distortions-and-a-Few-More.pdf)). Qui ci sono in più l'ingresso JFET cascodato e l'uscita in **classe A**: 20 mA contro 3,9 mA di picco sul carico peggiore, cinque volte di margine. Questo toglie la distorsione d'incrocio, che nella letteratura è la sorgente principale di armoniche alte. Una sola osservazione: il VAS è a transistor singolo, senza potenziamento del β né buffer, che Self raccomanda per alzare il guadagno locale. Qui il carico del VAS è leggero e i numeri reggono, quindi non lo sollevo come rilievo.

**I dispositivi** (non c'è un operazionale: PR-4).
- L'LSK489 è la scelta giusta per capacità e rumore: Ciss 4 pF, Crss 2 pF, en 1,8 nV/√Hz (datasheet).
- L'LS352 dà l'appaiamento monolitico.
- Il MJE15032/33 è sovradimensionato (R6).
- Self sostiene che un buon operazionale moderno pareggia un discreto ben fatto. La letteratura non mostra un vantaggio udibile del discreto in sé, e nemmeno una penalità, se è progettato bene: questo lo è.

**Compensazione.**
- Miller 470 pF più C_f 330 pF.
- Guadagno d'anello 78,7 dB a 10 Hz; incrocio a 807 kHz, quindi ~32 dB a 20 kHz (20·log(807/20), calcolo).
- Margine ≥ 64,4° al jack su tutta la matrice; il +10 dB a 105°.
- Slew 3,75 V/µs. Servono 2πfV_p = 1,51 V/µs per 12 V di picco a 20 kHz (2,5 volte di margine) e 0,48 V/µs per i 3,8 V del K11 sulle fisse (7,8 volte). Sulla principale il finale va in clip sopra ~1 V di picco.
- Sulla controreazione: Putzeys sostiene che non esiste troppa controreazione ([Linear Audio](https://linearaudio.net/node/410)). Pass mostra che fra 7 e 15 dB di controreazione le armoniche alte crescono, e oltre ~40 dB calano tutte ([passdiy](https://www.passdiy.com/project/articles/audio-distortion-and-feedback)). A 32–79 dB il blocco sta nella zona in cui la controreazione abbassa tutte le armoniche.

**Carattere della distorsione e spettro** (cifre di modello).
- Dalla 5ª in su a −192,6 dB, il fondo del metodo.
- CCIF a −125,6 dB.
- La h2 domina a ogni frequenza.
- A 0,2 V i prodotti cadono a ~0 dB SPL o sotto, e sopra i 20 kHz.
- Geddes e Lee trovano che THD e IMD non correlano col giudizio degli ascoltatori, e che conta lo spettro ([AES 5891](https://aes2.org/publications/elibrary-page/?id=12465)). Lo spettro di questo blocco è il più benigno che la letteratura descriva: ordini bassi, decrescenti, in banda trascurabili.
- L'unico punto aperto è R5: un meccanismo d'ingresso, da h2 ultrasonica, che fissa la cifra delle istanze unitarie e non è misurato dove peggiora.

**Rumore.**
- Per blocco 1,28–1,57 µV a 0 dB; la catena al peggio 5,6 µV, ~8 dB SPL, come limite per eccesso.
- All'ascolto normale (volume a −29 dB) conta quasi solo il blocco B: ~1,5 µV, cioè 96 + 20·log(1,5 µV × 21,1 / 2,83 V) ≈ **−3 dB SPL a 1 m**. Inudibile sulle Heresy.

**Carichi reali.**
- EV250 da 100 kΩ, Stax da 50 kΩ, Singxer ignoto, tutti in classe A larga.
- Re(Z) al jack ≤ 60 Ω, costante col volume.
- La 47 Ω tiene il cavo fuori dall'anello, la pratica standard.
- Il margine regge fino a 4,7 nF di cavo.

**In sintesi.** Le scelte del blocco sono quelle che la letteratura associa a un suono pulito e senza asprezza, e non ho trovato niente che la letteratura colleghi a un carattere aspro. Due cose vanno fatte prima di dire che V4 è verificato:
1. la prova di R5 sulla sorgente peggiore e sulle istanze unitarie;
2. V4 sulla catena intera.

Come suonerà lo dirà l'utente sul prototipo (PR-12).

---

## ADR che riaprirei

- **ADR-048 punto 6 e ADR-049**: il micro era giustificato dal convertitore delle LDR, che ADR-062 ha tolto (R3).
- **ADR-048 punto 3**: `VRELAY` su un trasformatore proprio per il «rail debole»; il PSRR+ è passato da ~23 a 78,5 dB con ADR-056 (R4).
- **ADR-014**: «V_ds costante» è falso a guadagno unitario. Il suo «Da riaprire se» (il cascode costa margine di tensione) si è già avverato, come dice il commento di `gain_block.py` (R5).
- **ADR-055**: la sorgente da 2,5 kΩ del banco non è più la peggiore da ADR-065 (5,6 kΩ), e il banco non è la catena (R5).
- **ADR-004, 026, 027, 041, 045, 051**: insieme, via PR-3, PR-17, PR-18 (R2; già respinto una volta).
- **ADR-042 / ADR-017**: il MJE, alla misura della f_T sul prototipo (R6).

## Semplificazioni proposte

| Sottosistema | Che cosa si toglie | Che cosa si perde | Quale voce regge comunque, e perché |
|---|---|---|---|
| Guadagno commutato e trim | K1, K5, K11, K12, K6, K7–K10, la scala del trim, sei LED, Δ, gli interblocchi | +3/+10 dB per una catena futura (si possono lasciare le impronte vuote) | PR-6 (+6,58 dB col K11 a 0 dB), PR-20, PR-23: sparisce il guasto di ADR-051, 76,9 dB SPL |
| Micro e firmware | ATtiny3216, `main_attiny.c` (non scritto), i test sull'host | flessibilità di sequenza | PR-24 per costruzione; PR-20 e PR-23 coi comparatori e gli RC che ci sono già |
| Standby e spegnimento morbido | T2, K501, la logica di standby, NC-037 | l'interruttore frontale a bassa tensione e lo standby | PR-20: perdita di rete 39 nV al jack contro 34 nV del morbido (§24); PR-28 guadagna ~1 W |
| Buffer delle fisse, uno solo per due uscite (bassa priorità) | 2 blocchi, ~2,2 W | la classe A dell'altra fissa se una è in corto | PR-15; ma vale solo se la Zin del Singxer spento è alta, da misurare. Già respinta in L43a e in ADR-023 |

Da tenere com'è: i relè al jack in geometria iii (la derivazione sola attenuava 1/471, misurato), il sorvegliante con il rivelatore di rete, la cella RC, il margine di 60° (oggi non costa più niente).

## Omissioni cercate

- **Guasto singolo nei blocchi, contatto del mute incollato, tetto sulle fisse** (R1): già noto, NC-042 e NC-046.
- **V4 sulla catena e sulla sorgente peggiore, e la distorsione d'ingresso a modo comune** (R5): nuovo.
- **V1 e V4 alla temperatura del telaio** (fino a 57 °C dentro): il dossier non dice che siano stati corsi a caldo. Dice solo che V1 non è misurato agli spigoli di tolleranza (§27).
- **Inserire a caldo un cavo RCA su un ingresso selezionato**: nessun banco lo esercita. È un gesto dell'utente più che un cambio di configurazione, ma il primo contatto del polo caldo prima della massa arriva al finale intero.

Rilievi gravi al livello «bloccante» non ne ho trovati. Il più serio, R1, era già registrato.

## Fonti

- [TI, Caldwell — Distortion and source impedance in JFET-input op amps (SLYT595)](https://ti.com/lit/pdf/slyt595)
- [Linear Systems — LSK489 Application Note (Cordell)](https://www.linearsystems.com/applicationnotes/lsk489-app-note); copia in repo `vendor/jfet/linear_systems/LSK489/4be30b_49c5a96bc52f4868a7bf2a5c17150351.pdf`
- [Linear Systems — driven cascode](https://www.linearsystems.com/post/boosting-performance-with-low-noise-cascode-structures)
- [Self — Op amps in small-signal audio design, Part 2 (eeNews Europe)](https://www.eenewseurope.com/en/op-amps-in-small-signal-audio-design-part-2-distortion-in-bipolar-and-jfet-input-op-amps/)
- [Self's distortions, sintesi hifisonix](https://hifisonix.com/wp-content/uploads/2010/10/Douglas-Selfs-8-Distortions-and-a-Few-More.pdf)
- [Pass — Audio, Distortion and Feedback](https://www.passdiy.com/project/articles/audio-distortion-and-feedback)
- [Putzeys — The F-word (Linear Audio vol. 1)](https://linearaudio.net/node/410)
- [Geddes & Lee — Auditory Perception of Nonlinear Distortion, AES 5891](https://aes2.org/publications/elibrary-page/?id=12465)
- [onsemi — datasheet MJE15032/33](https://www.onsemi.com/pdf/datasheet/mje15032-d.pdf)
- [Toshiba — datasheet 2SA1837](https://www.mouser.com/catalog/specsheets/toshiba_2SA1837.pdf)
- [Ken Rockwell — Stax SRM-T1](https://kenrockwell.com/audio/stax/srm-t1.htm)

## File letti

- `/Users/roberto/EDA/docs/preamp/PRB.md`
- `/Users/roberto/EDA/docs/preamp/REQUIREMENTS.md`
- `/Users/roberto/EDA/docs/preamp/dossier/index.html`
- `/Users/roberto/EDA/circuits/preamp/gain_block.py`
- `/Users/roberto/EDA/circuits/preamp/preamp_audio.py`
- `/Users/roberto/EDA/docs/preamp/data/2026-10-01/L46a/sintesi.csv`
- `/Users/roberto/EDA/vendor/jfet/linear_systems/LSK489/LSK489DSRevA38.pdf`
- in `/Users/roberto/EDA/docs/preamp/decisions/`: ADR-001, 003, 014, 017, 023, 033, 042, 043, 044, 045, 048, 049, 051, 055, 062, 064

Letti dal worktree `/Users/roberto/EDA/.claude/worktrees/L52/`, allo stesso percorso relativo.
