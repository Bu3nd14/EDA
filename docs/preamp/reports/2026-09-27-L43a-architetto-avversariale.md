# 2026-09-27 — L43, revisione dell'architetto avversariale

**Obiettivo 1, suona bene: regge con riserve.** Rumore, impedenze, risposta e stabilità sono solidi e li ho verificati. Ci sono però due riserve. Coi modelli del costruttore la distorsione in alta frequenza cresce di 2–3 ordini di grandezza fra 1 e 20 kHz, e il Miller da 1 nF la aggrava di 20–27 dB: è in conflitto diretto con PR-8. Il ronzio da anello di massa non ha nessun requisito.

**Obiettivo 2, nessun bump: regge con riserve.** Gli eventi elencati da PR-20 sono coperti (253 verdetti su 253). Restano due buchi fuori dalla matrice. La continua passa per il volume, e ogni scatto lascia un gradino. Il selettore d'ingresso non è progettato e l'ingresso è accoppiato in continua.

**Obiettivo 3, fallisce senza danni: regge con riserve.** I guasti dell'alimentatore sono coperti bene, sul circuito vero. I guasti singoli della scheda audio non li ha analizzati nessuno.

Fase 1 fatta alla cieca: ho letto solo PRB, REQUIREMENTS, ADR, dossier, `circuits/`, `spice/`, i dati, `models/` e SAFETY.md. La fase 2 (NONCOMPLIANCE.md e STATE.md) è arrivata dopo, e non ha tolto né ammorbidito nessun rilievo.

---

## Rilievi, dal più grave

### R1 — Coi modelli la distorsione cresce di 2–3 ordini di grandezza verso gli acuti. Il Miller da 1 nF ne costa 20–27 dB
- **Voce/requisito:** PR-8, PR-7 · V4, V1 · ADR-042, ADR-019 §1, ADR-053.
- **Il rilievo:** PR-8 chiede che la distorsione non cresca verso gli acuti. Coi modelli del costruttore la THD a 20 kHz vale 140–420 volte quella a 1 kHz. Buona parte di questo viene dal Miller portato a 1 nF per tenere i 60° (ADR-042), e il prezzo non è mai stato misurato né confrontato con PR-8.
- **L'evidenza:** un deck mio in `/tmp/l43a/`, fuori dal repo. Un blocco da `spice/preamp/gain_block_flat.inc` coi 7 modelli del costruttore, sorgente 2,5 kΩ, carico 10 kΩ dopo 47 Ω e 4,7 µF, uscita 2 V RMS, `.four` con griglia 8192 e passo 0,02 µs. **Sono cifre di modello, non misure** (`docs/limitations.md`). Il trend dipende dalla pendenza del guadagno d'anello, quindi è più robusto della cifra assoluta.

  | Caso | 1 kHz | 10 kHz | 20 kHz, 1 nF | 20 kHz, 470 pF |
  |---|---|---|---|---|
  | 0 dB | 0,00044 % | — | **0,0616 %** | 0,0060 % |
  | +10 dB | 0,00040 % | 0,0112 % | **0,168 %** | 0,0118 % |

  - Con la sorgente a 1,5 Ω il 20 kHz a 0 dB dà 0,0622 %: la causa non è l'impedenza di sorgente.
  - Da 10 a 20 kHz la THD sale di circa 23 dB per ottava. È il meccanismo di Self: la corrente dell'ingresso che pilota il Miller raddoppia a ogni ottava, e la controreazione cala di 6 dB/ottava. Da qui una salita di 18 dB/ottava, che cresce col valore del Miller ([Self, Part II](https://www.burosch.de/en/audio/1013-douglas-self-distortion-in-power-amplifiers-part-ii-the-input-stage.html)).
  - IMD CCIF (19 + 20 kHz, 1,909 V di picco per tono, cioè il K11 a fondo scala) sul blocco A a guadagno unitario:
    - con 1 nF: prodotto a 1 kHz a −59,6 dB, prodotti a 18 e 21 kHz a −64 dB;
    - con 470 pF: −85,4 dB e −91,6 dB.
  - Lo slew dichiarato da ADR-042 è −1,68 V/µs. A +10 dB, fondo scala, 20 kHz (1,51 V/µs) il rapporto segnale/slew vale 0,9. Jung indica ≤ 0,4 come soglia conservativa per il TIM, e dice che per la distorsione totale serve anche di meno ([Jung, Stephens, Todd, SID/TIM](https://hifisonix.com/wp-content/uploads/2018/03/SID_and_TIM_W_Jung_77-79.pdf)).
  - La radice sta in ADR-042 stessa: la caduta di V1 viene tutta dalla CJE di 3,06 nF dei MJE15032/33, verificata in `models/bjt_npn/mje15032.lib`. È un transistor da 8 A e 250 V usato per erogare milliampere, pilotato direttamente dal VAS.
  - ADR-042 ha scartato solo alternative di compensazione. Non ha valutato un dispositivo d'uscita con meno capacità, uno stadio driver, o più corrente di coda con degenerazione, che è il rimedio di Self (−20 dB).
  - PR-7 applica 60° al caso peggiore di 4,7 nF, che è già un margine: si mette margine su margine. La regola corrente per un amplificatore di controreazione è 45°, e 60° si riserva ai sistemi che non tollerano sovraelongazione ([EDN, «Why 45°»](https://www.edn.com/why-45%E2%81%B0c-an-overview-of-loop-stability-in-operational-amplifiers/)).
  - Anche il criterio di V4 è mal posto. «La THD a 20 kHz dello stesso ordine di quella a 1 kHz» premia un circuito mediocre a 1 kHz, e nessuno stadio compensato col Miller lo soddisfa. Meglio un tetto assoluto a 20 kHz e sui prodotti IMD in banda, a un livello dichiarato.
  - Per equità: lo spettro a 20 kHz scende in ordine (h2 −66, h3 −70, h5 −85, h7 −109 dB), quindi la seconda clausola di PR-8 regge nel modello. L'udibilità non la giudico. In uso reale il blocco B lavora a ~85 mV, mentre il blocco A e i buffer portano sempre il livello pieno della sorgente.
- **Severità proposta:** **bloccante per G1**. Il rimedio (dispositivo d'uscita, driver o corrente di coda) tocca la topologia, e si somma a NC-004.
- **Fase 2:** in parte già noto. NC-004 dice che V4 è senza evidenza, NC-025 che il modello dei MJE ha la f_T sotto il datasheet, e ADR-042 dichiara «il prezzo: slew». **Nuovi:** la quantificazione (20–27 dB di THD e IMD dovuti al Miller), il conflitto con la PR-8 firmata e le alternative topologiche non valutate. Scatta la clausola di ADR-042 «Da riaprire se: lo slew a 20 kHz si sente o si misura», al livello del modello. La decisione di ADR-042 non mi convince: ha pagato con la distorsione un difetto di un dispositivo sovradimensionato. Nota a margine: la frase di ADR-053 «la coppia differenziale cancella la 2ª» non regge a 20 kHz nel modello, dove la h2 è la prima armonica.

### R2 — PR-14 non è verificabile, e l'ingresso in continua lo rende difficile per costruzione
- **Voce/requisito:** PR-14, PR-20 · F1, V2 (A) · ADR-038.
- **Il rilievo:** il selettore «è ancora da progettare». Il blocco A è accoppiato in continua alla sorgente: R113 da 1 MΩ a massa, nessun condensatore d'ingresso, LDR in serie. Quindi cambiare ingresso lascia sulle uscite un gradino pari alla differenza fra le continue delle due sorgenti.
- **L'evidenza:**
  - Dalla netlist `circuits/preamp/preamp_audio.net`: IN_SRC → LDR_S → ingresso del blocco A → uscita del blocco A → buffer delle fisse, tutto in continua. Il gradino arriva quindi intero ai jack fissi, e scalato dal volume al principale.
  - Il phono a valvole esce con un condensatore dal catodo (tensione di catodo ignota). Un film da 1 µF ha una resistenza d'isolamento minima di 10 000 s (MΩ·µF) secondo il datasheet [WIMA MKS 4](https://www.wima.de/wp-content/uploads/media/e_WIMA_MKS_4.pdf). Con 100 V fa 10 nA su 1 MΩ, cioè **~10 mV**, 100 volte i 100 µV al jack fisso. Se quel condensatore è un elettrolitico, la cifra è molto peggiore.
  - La continua del K11 non è pubblicata: ho cercato e non l'ho trovata.
  - Il rimedio classico è un condensatore per ingresso, ciascuno con la sua resistenza verso massa dal lato del preamp: ogni ingresso resta carico alla propria continua. Oppure si commuta sotto mute, ma col mute di oggi un cambio d'ingresso costerebbe ~13 s.
- **Severità proposta:** **bloccante per G1**. Il selettore fa parte della topologia, e il rimedio cambia l'ingresso del blocco A (E3, E5).
- **Fase 2:** il selettore non progettato è già noto (STATE, L42c: «da fare altrove»). **Nuovo** il meccanismo che rende PR-14 difficile, e la stima.

### R3 — La continua del blocco A attraversa trim e volume: ogni scatto del volume lascia un gradino, e nessun banco lo guarda
- **Voce/requisito:** PR-20, PR-16 · V2, F4 · ADR-007.
- **Il rilievo:** fra l'uscita del blocco A e il blocco B non c'è nessun condensatore. La continua passa per la scala del trim e per l'attenuatore, e ogni scatto del volume cambia la continua all'ingresso del blocco B. Il volume non compare fra gli eventi di PR-20.
- **L'evidenza:**
  - Netlist: la rete di uscita del blocco A L contiene R134/R135/R136/C137, R901 (la cima della scala del trim), K7 pin 2, e R508/R608 (i buffer delle fisse). Nessun condensatore.
  - Il blocco B ha `r_in=None`, e la sua continua la dà l'attenuatore (`preamp_audio.py`).
  - Il dossier (sezione 3, `build_dossier.py` riga ~2568) scrive: «Il trim sta dopo il condensatore d'uscita del blocco A e non tocca la continua». **Sulla netlist è falso.**
  - L'offset del blocco A è −15,45 mV (`data/2026-09-27/L42/dopo/tb_op/tb_op.log`).
  - Il calcolo: gradino al jack = V_A · Δ(rapporto dell'attenuatore) · G_B, poi dB SPL con la catena di NC-028.

  | Scatto | a 0 dB | a +10 dB |
  |---|---|---|
  | da 0 a −2 dB, in cima alla corsa | 3,2 mV · **63,5 dB SPL** | 10 mV · **73,5 dB SPL** |
  | da −29 a −27 dB, all'ascolto | 0,14 mV · 36,5 dB SPL | 0,45 mV · 46,5 dB SPL |

  - V2 è 33 dB SPL, e il calcolo vale senza musica. La dispersione dell'LSK489 (±20 mV) aggiunge fino a +7 dB, e la continua della sorgente (R2) si somma. Letteratura: «DC should not be allowed to flow through any pot used for audio control» ([ESP, pots](https://sound-au.com/pots.htm)).
  - Rimedio economico: un condensatore all'ingresso del blocco B, con la sua resistenza di gate. In banda la sorgente è l'attenuatore, quindi il costo di rumore è trascurabile.
- **Severità proposta:** maggiore. È un'omissione di PR-20 (il volume) e un'affermazione falsa del dossier.
- **Fase 2:** **nuovo**. NC-028 dice «il volume non riduce» l'offset del blocco B: è un'altra cosa.

### R4 — PR-2 e PR-3 si contraddicono: i tre livelli di guadagno non servono a nessun apparecchio della catena
- **Voce/requisito:** PR-2 contro PR-3 · E2, F5 · ADR-004, ADR-019 §3, ADR-026, ADR-030, ADR-041.
- **Il rilievo:** PR-2 dice «per questa catena, non per una generica». PR-3 giustifica +3 e +10 dB con «una sorgente debole», e ADR-004 con un finale futuro da 1,5–2 V. Nessuno dei due esiste in PR-2.
- **L'evidenza:**
  - ADR-001: il phono a 0,5 V è già quasi i 0,61–0,75 V del cj. A 0 dB, volume al massimo, sono ~14 W, ~107 dB SPL a 1 m sulle Heresy. «Guadagno unitario va bene per entrambe le sorgenti».
  - Il +10 dB è il modo peggiore su tutto (numeri del dossier, e il rumore l'ho rieseguito con `tb_noise_breakdown.cir` in `/tmp/l43a/noise`, cifre identiche):

    | Grandezza | a 0 dB | a +10 dB |
    |---|---|---|
    | rumore del blocco B | 1,486 µV | 4,270 µV |
    | PSRR+ a 10 kHz | 32,96 dB | 23,03 dB |
    | headroom col K11, trim a 0 | +6,41 dB | +0,48 dB |
    | THD a 20 kHz (R1) | — | 2,7 volte quella a 0 dB |
    | risposta a 20 kHz, riferita a 1 kHz | — | −0,134 dB, contro i 0,2 di PR-9 |

  - Il +10 dB porta con sé K1, K5, K11, K12, SW2, sei diodi, tre LED, `gain_interlock.py`, il gruppo 1 di V2, parte di ADR-045 e il ruolo portante del trim.
- **Severità proposta:** maggiore. È un difetto del contratto da decidere con l'utente.
- **Fase 2:** **nuovo**. NC-022 chiedeva il terzo livello, non ne discuteva la necessità.

### R5 — Nessuna analisi dei guasti singoli della scheda audio
- **Voce/requisito:** PR-22, PR-23, PR-24 · P7, P9 · ADR-027 («Da riaprire se» sulla bobina di K6), ADR-051.
- **Il rilievo:** il tetto di non-danno (0,87 V, ~112 dB SPL) vale solo per i guasti dell'alimentatore. Nessuno ha esaminato i guasti singoli della scheda audio.
- **L'evidenza:**
  - Cerco «guasto singolo», «FMEA» e «analisi dei guasti»: escono solo ADR-051 (la linea a 12 V) e le clausole di ADR-027 e ADR-033. `psu.py` non ha nessun rivelatore di continua sulle uscite dei blocchi.
  - Casi non esaminati:
    - **Un finale dei MJE in corto:** OUT va vicino al rail (~13 V), e il gradino passa dal 4,7 µF con τ 0,32 s. Sono ~23 dB sopra il tetto. La corrente, 30 V su 44 Ω = 0,68 A, probabilmente non fa scendere il rail sotto 13,5 V, quindi il sorvegliante non interviene. È un calcolo, non una simulazione.
    - **La bobina di K6 aperta:** il trim e il guadagno diventano comandabili fuori mute, col jack collegato. Il gradino di guadagno a caldo era stimato 6–114 mV, cioè fino a ~95 dB SPL.
    - **Il relè di mute con un contatto saldato:** l'accensione arriva al jack senza protezione.
    - **Un difetto del firmware che accende entrambe le stringhe delle LDR:** la sorgente vede ~226 Ω. ADR-038 punto 3 lo evita solo col profilo, cioè col firmware, contro lo spirito di PR-24. Probabilmente senza danni per K11 e per un cathode follower.
    - **Il condensatore d'uscita in corto:** −15 / −49 mV di continua verso il cj.
  - Sulle uscite fisse il guasto finisce in una Stax SRM-T1, 60 dB di guadagno, 300 V RMS massimi ([Ken Rockwell](https://www.kenrockwell.com/audio/stax/srm-t1.htm)): un gradino di rail passa l'intera escursione alle elettrostatiche.
- **Severità proposta:** maggiore. È un'omissione dell'obiettivo 3, da chiudere prima di G2: un'analisi FMEA della scheda audio, e decidere se un rivelatore di continua deve comandare il sink di MUTE_CMD che esiste già.
- **Fase 2:** **nuovo**. Due singoli casi erano già noti come clausole di ADR-027 e ADR-033, non come analisi.

### R6 — La VTL5C4 dell'Excelitas è fuori produzione: T8 la squalifica al gate
- **Voce/requisito:** PR-29 · T8 · ADR-038 e ADR-039 («Da riaprire se la VTL5C4 non si trova»).
- **Il rilievo:** la sorgente nomina la VTL5C4 dell'Excelitas, con un modello tratto dal suo datasheet. Excelitas ha chiuso tutta la serie VTL (ultimo ordine settembre 2015), e T8 squalifica una parte con un annuncio di fine vita pubblicato.
- **L'evidenza:** [modularsynthesis.com](https://modularsynthesis.com/vactrols/vactrols.htm): «Excelitas manufactured vactrols until 2015; CoolAudio … VTL5C3 and Xvive … a complete line», con una variabilità significativa fra i campioni dei sostituti. Titolo del thread su [modwiggler](https://www.modwiggler.com/forum/viewtopic.php?t=140065). Il distributore non l'ho potuto verificare (403).
- **Severità proposta:** maggiore. Si chiude con la Xvive, il suo datasheet e il modello rigenerato.
- **Fase 2:** **già noto** in STATE (L29b2: «fuori produzione», con la riedizione Xvive, «prima di G2»), ma non è registrato come NC, e il sorgente cita ancora l'Excelitas. La condizione di ADR-038 si è avverata in parte.

### R7 — Il ronzio da anello di massa non ha nessun requisito, in una catena di cinque apparecchi sbilanciati sulle trombe
- **Voce/requisito:** PR-5, PR-2 · E5, P4, SAFETY.md.
- **Il rilievo:** E5 conta solo il rumore proprio e il ripple. Il preamp collega fra loro il cj, il Singxer, la Stax e due sorgenti, tutti alimentati da rete e tutti sbilanciati. Nessun requisito, nessuna ADR e nessuna voce di SAFETY.md parlano di come la massa di segnale si lega alla terra di protezione.
- **L'evidenza:**
  - 500 µV di ronzio al jack principale (per esempio 10 mA di corrente d'anello su 0,05 Ω di schermo) valgono ~47 dB SPL a 1 m, oltre la stanza silenziosa.
  - Rod Elliott documenta anelli di 1 V fra le terre delle prese, e la rete 10 Ω ∥ C ∥ diodi fra la massa del circuito e la terra ([ESP, Earthing](https://sound-au.com/earthing.htm)).
  - SAFETY.md prevede la terra direttamente al telaio, senza indicare dove si collega la massa audio.
- **Severità proposta:** maggiore, da decidere prima di G2.
- **Fase 2:** **nuovo**.

### R8 — Il pilota delle LDR e il profilo di 6 s sono calibrati su un criterio che non esiste più
- **Voce/requisito:** PR-21, PR-24 · V2 (S) · ADR-039, ADR-040, ADR-049, ADR-050.
- **Il rilievo:** DAC a 12 bit, due convertitori esponenziali, compensazione col sensore di temperatura e calibrazione a due punti (±1 dB) servono una precisione del profilo che nessuna voce del PRB chiede. S misura 7,16 dB contro 20: ci sono 12,8 dB di margine. Td = 6 s fu scelto il 2026-09-21, quando decideva C ≤ 1 mV (ADR-040 punto 1: a 20 Hz servivano oltre 14 s). ADR-040 ha cambiato il criterio e non ha riesaminato Td.
- **L'evidenza:** dossier, sezione 12 (S 7,16 / 5,45 dB) e sezione 21. ADR-049, «La compensazione e la calibrazione», non cita nessun requisito. Il PRB non fissa un tempo massimo del mute: oggi i primi 100 ms tolgono 7 dB, mentre il Technics di riferimento toglieva 20 dB subito.
- **Severità proposta:** minore, come semplificazione (sotto).
- **Fase 2:** **nuovo**.

### R9 — La metrica in dB SPL ignora le cuffie, e il tetto di non-danno vale solo per il jack principale
- **Voce/requisito:** PR-20, PR-23, intestazione del PRB.
- **Il rilievo:** due uscite su tre vanno a cuffie (Singxer, Stax). Il PRB traduce tutto in dB SPL sulle Heresy, e il tetto è dichiarato solo al jack principale.
- **L'evidenza:**
  - SRM-T1: 60 dB di guadagno ([Ken Rockwell](https://www.kenrockwell.com/audio/stax/srm-t1.htm)). SR-L300: 101 dB con 100 V RMS ([Stax](https://stax-international.com/products/sr-l300/)).
  - 100 µV al jack fisso diventano **41 dB SPL all'orecchio** col volume della Stax al massimo. A un volume d'ascolto realistico, circa −35 dB, sono ~6 dB SPL.
  - Il Singxer ha +11 dB di guadagno alto ([Apos](https://apos.audio/products/singxer-sa-1-fully-balanced-amplifier)).
  - Conclusione: la soglia di 100 µV regge anche per le cuffie. Manca però un tetto di non-danno sulle fisse (R5).
- **Severità proposta:** minore.
- **Fase 2:** **nuovo**. ADR-012 cita le elettrostatiche, non una metrica.

---

## ADR che riaprirei
- **ADR-042** (Miller 1 nF): la sua clausola sullo slew è soddisfatta al livello del modello (R1), e le alternative topologiche mancano: dispositivo d'uscita con CJE bassa, driver, corrente di coda.
- **ADR-004, ADR-026, ADR-019 §3** (tre guadagni): non servono alla catena di PR-2 (R4). Il futuro si copre con R_g da montare a richiesta, come già si fa per il blocco A (ADR-006).
- **ADR-027** (il trim): senza +10 dB perde il ruolo portante. Il suo «Da riaprire se» sulla bobina di K6 appartiene alla FMEA (R5).
- **ADR-049 e ADR-050** (micro, DAC, calibrazione): la precisione di ±1 dB non la chiede nessun requisito (R8).
- **ADR-039**: Td = 6 s è figlio del criterio C, superato da ADR-040 (R8).
- **ADR-038 e ADR-039**: la parte VTL5C4 è fuori produzione (R6).

## Semplificazioni proposte
1. **Togliere la commutazione del guadagno.**
   - Via: K1, K5, K11, K12, SW2, D10–D15, J6 e tre LED, `gain_interlock.py`, il gruppo 1 di V2. Le R_g restano come piazzole da montare a richiesta.
   - Si perde: PR-3 e il senso di PR-18.
   - Reggono con più margine: PR-1, PR-2, PR-5 (1,49 contro 4,27 µV), PR-6 (+6,41 dB di headroom senza trim), PR-8 (R1), PR-9, PR-24 (meno stati).
2. **Togliere il trim**, dopo la 1.
   - Via: K6–K10, SW1, la scala, J5 e tre LED, e con loro il permissivo e il Δ hardware (`PERMIT_CMD`, U508A, C528), VHOLD e i 13 ms.
   - Si perde: PR-17. Il trim comune (ADR-027) è già solo un volume grossolano, e cambiando sorgente si ritocca comunque qualcosa.
   - Regge: PR-16. L'attenuatore lavora a −15 dB col phono e a −29 col K11 (ADR-001).
3. **Pilota delle LDR analogico**, con RC più generatore di corrente, al posto di micro, DAC, convertitori e calibrazione. Dopo la 2 il micro può sparire del tutto.
   - Si perdono: la precisione e la programmabilità del profilo.
   - Regge: PR-21 (S ha 12,8 dB di margine). Migliora PR-24: nessun firmware.
   - Da verificare con `tb_v2_casopeggiore.cir` sul profilo nuovo.
4. **Td più corto** (1–2 s), da misurare contro il limite di spegnimento della cella. Si ottiene un mute che muta. S regge se resta ≤ 20 dB.
5. **Buffer delle fisse** (possibile, **non** raccomandata senza la Zin del Singxer).
   - Via: quattro blocchi, cioè ~4 W, metà della scheda audio. Al loro posto 470 Ω dal blocco A.
   - Regge PR-4: in corto, 3,8 V / 235 Ω + 2,5 mA ≈ 19 mA, sotto i 40 mA di classe A.
   - Si perdono: E4 sulle fisse, e E13 se la Zin del Singxer è bassa.
6. **Non** toglierei il sorvegliante col rivelatore di rete, i due trasformatori (lo standby col frontale a bassa tensione ne ha bisogno) né la geometria iii del relè al jack. Sono prassi corrente e le cifre li reggono.

## Omissioni cercate
Tutte **nuove**, tranne dove indicato:
- La continua attraverso il volume (R3).
- La continua delle sorgenti al cambio d'ingresso (R2).
- L'anello di massa (R7).
- La FMEA della scheda audio (R5).
- La metrica per le cuffie (R9).
- Un tempo massimo del mute (R8).
- Entrambe le stringhe delle LDR accese per un errore del firmware (R5).

Non ho trovato altro di grave. Rumore, Zin, Zout, V1 ai valori nominali, P7 e i guasti dell'alimentatore reggono sulle cifre che ho letto o rieseguito.

**Cosa ho rieseguito:**
- `run_simulation.sh tb_noise_breakdown.cir` in `/tmp/l43a/noise`: 1,176 / 1,235 / 1,486 / 4,270 / 2,033 µV, uguali al dossier.
- I deck di THD e IMD in `/tmp/l43a/` (`thd_*.cir`, `imd_A*.cir`, `gb_470p.inc`). Sono copie di `tb_v3_overload.cir` con un solo cambio ciascuna.

**Cosa non ho rieseguito:** V1, V2 e l'alimentatore, che cito dal dossier.
