# ADR-046 — Spegnimento morbido dall'interruttore, e alla perdita di rete un failsafe con tetto di non-danno

Data: 2026-09-26 · Stato: accettata

## Contesto

ADR-043 consegna a L30 due requisiti, lo spegnimento normale e un failsafe per il guasto
dell'alimentatore, e ADR-045 ne aggiunge un terzo: alla caduta di `VRELAY` il guadagno non deve
cambiare prima dello stacco dei jack. ADR-043 lascia aperte due domande: la forma del failsafe e
la soglia in caso di guasto.

Un fatto le cambia entrambe. Da ADR-044 (L29e) il relè al jack è un **deviatore in serie**, e a
riposo isola il jack. Le cifre di L29c (relè in derivazione, ~74 dB col relè chiuso) non valgono
più. Conta invece **quando il contatto si è aperto rispetto a quando i rail escono dalla
regolazione**.

Un secondo fatto è di misura. Il mute completo di ADR-039/040 dura ~6,6 s: la dissolvenza LDR in
6 s, poi i relè 0,5 s dopo. Con gli otto blocchi (~265 mA per rail) tenere i rail per 6,6 s con
dei condensatori chiede ~0,35 F per rail. È il «Da riaprire se» di ADR-043, «componenti non
ragionevoli».

## Decisione

Parole dell'utente, il 2026-09-26:
- «in caso di guasto una soglia di non-danno basta»;
- «le soglie vanno bene come tetto, non come target, dobbiamo stare più bassi, il resto OK»;
- «sì, interruttore morbido va bene».

1. **Lo spegnimento normale è l'interruttore «morbido».** L'interruttore di rete a pannello è un
   **ingresso** del temporizzatore, come SW3, e non stacca la rete.
   - All'apertura dell'interruttore, il temporizzatore esegue l'inserimento completo del mute:
     la dissolvenza, `MUTE_CMD` 0,5 s dopo d = 1, e `PERMIT_CMD` Δ dopo.
   - Solo dopo, con ≥ 50 ms di margine, rilascia il **relè di rete**. In tutto sono ~7 s.
   - Il relè di rete è sicuro per costruzione: diseccitato = rete staccata.
   - **Soglia: V2 intera** (100 µV, ~33 dB SPL di picco a 1 m).
2. **La perdita di rete improvvisa è un guasto**, come il cedimento di un regolatore o di un
   rail: blackout, spina staccata, fusibile. Il failsafe è di tre pezzi, tutti fuori dal
   percorso del segnale:
   - **un sorvegliante** che guarda i due rail audio, e facoltativamente la rete. Quando un rail
     scende sotto **|13,5 V|**, rilascia `MUTE_CMD` entro 1 ms, senza dissolvenza. Il comando è
     attivo-per-la-musica: se il sorvegliante perde la propria alimentazione o si guasta
     aperto, il mute entra;
   - **una tenuta dei rail dopo i regolatori**: ≥ 1500 µF **effettivi** per rail (2200 µF
     nominali, −20 %). A 265 mA il rail + va da 13,5 a 10,6 V in ≥ 16 ms, contro i 3 ms di
     rilascio più 1 ms di trasferimento del relè al jack;
   - **una tenuta di `VRELAY`** (ADR-045): per ≥ 25 ms dallo scatto del sorvegliante,
     `VRELAY` resta nella sua tolleranza normale. Il temporizzatore, alimentato dalla stessa
     tenuta, rilascia `PERMIT_CMD` Δ dopo `MUTE_CMD`. K6, K1/K5 e K11/K12 cadono quindi dopo lo
     stacco dei jack. Sulla scheda audio non cambia niente.
3. **Le soglie del guasto.**
   - **Tetto di non-danno**: ≤ **0,87 V di picco** al jack principale (~112 dB SPL). È l'ingresso
     che porta il MV50 (sensibilità 612 mV) alla piena potenza: il finale non va in clipping, e
     le Heresy (100–105 W continui) non vedono più di 30 W.
   - **Obiettivo di progetto**, molto sotto il tetto: ≤ **2 mV** (~60 dB SPL di picco a 1 m).
   - Con la musica in corso, il taglio netto del guasto porta al jack al massimo la musica di
     quell'istante: un click, non un danno.
4. **Il caso accettato**: il corto franco istantaneo di un rail, più veloce dei 3 ms del relè.
   Il finale può andare in clipping per un colpo. Lo si accetta con l'argomento dei 30 W del
   finale contro i 100–105 W delle Heresy, invece di aggiungere un elemento più veloce in serie
   al segnale. Nel banco non si integra (§ Perché); il peggiore misurato di quella forma è di
   L29d2, 2,3 V (~121 dB), col relè in ritardo di 100 ms su una rampa da 10 ms.

## Perché

Il banco è `data/2026-09-26/L30/deck/tb_v2_l30.cir`. È generato dal generatore di V2
(`--matrice l30`) sul sorgente: geometria iii letta dalla netlist, senza segnale, +10 dB, 100 kΩ,
0 pF di cavo, metodo di V2. Report: `reports/2026-09-26-L30-spegnimento-failsafe-calore.md`.

| Caso | Corse | Peggiore al jack | dB SPL di picco a 1 m | Soglia |
|---|---|---|---|---|
| Spegnimento morbido: rampe 10 / 300 ms, simmetriche o con un rail in ritardo di 50 ms, guadagno a 0 dB all'inizio o a metà discesa | 12 su 12 | **2,7 µV** | **~+2 dB** | V2, 100 µV: sotto di 31 dB |
| Guasto: un rail o entrambi, tenuta 470 / 1000 / 2200 µF, relè al rilascio massimo | 9 su 9 | **1,77 mV** | **~58 dB** | tetto 0,87 V: sotto di 54 dB; obiettivo 2 mV |
| Guasto con `VRELAY` persa, guadagno a 0 dB Δmin = 10 ms dopo | 3 su 3 | uguali a sopra | ~58 dB | — |
| Controfattuale: senza Δ, guadagno a 0 dB col comando | 1 | **69 mV** | **~90 dB** | dice perché serve la tenuta di `VRELAY` |

- **La soglia di perdita della regolazione, rimisurata**: il rail **+** a **10,2–10,6 V**, per uno
  scostamento dell'uscita del blocco da 10 a 100 mV. Il solo rail − ne regge molto meno: −7,5 V
  per 10 mV. Il vincolo è sul rail +.
- **Perché 1500 µF effettivi e non 470.** Anche 470 µF passano, ma lasciano ~1 ms fra il contatto
  aperto (+4 ms) e i 10,6 V (+5,1 ms), senza tolleranza del condensatore né ritardo del
  sorvegliante. Con 1500 µF la discesa da 13,5 a 10,6 V dura 16,4 ms; tolti i 4 ms del contatto
  e 1 ms del sorvegliante restano ~11 ms.
- **Il residuo del guasto, 0,5–1,8 mV, ha due fonti.** Viene dal rail che scende da 15 a 13,5 V
  col jack ancora collegato (PSRR), e dall'apertura del contatto. Non viene dalla perdita della
  regolazione, che avviene a jack isolato.
- **Il residuo di 4 mV «non spiegato» di L29d2 è spiegato.** Cadeva a +427 µs, nel rimbalzo del
  contatto (il banco lo richiude fra +400 e +600 µs), mentre il rail aveva già cominciato a
  scendere. È un effetto dell'ordine dei tempi, non un percorso nascosto. Nell'ordine di questa
  ADR i relè hanno finito di muoversi quando il rail è ancora sopra 13,5 V.
- **Supervisore guasto.** Guasto aperto, o senza alimentazione: mute. Guasto «chiuso» insieme a un
  guasto dei rail: è un doppio guasto, fuori dal criterio.

## Alternative scartate

- **Tenere i rail per tutto il mute graduale dopo la perdita di rete**: ~0,35 F per rail.
- **Una dissolvenza accelerata solo allo spegnimento**: con 0,5 s servono ~50 000 µF per rail,
  e andrebbe dimostrato il criterio del salto di ADR-040.
- **V2 per intero anche nel guasto**: servirebbe un elemento più veloce del relè in serie al
  segnale. Non scelta dall'utente.
- **Una tenuta locale delle sole bobine di K6, K1/K5 e K11/K12 sulla scheda audio**: funziona, ma
  divide `VRELAY` sulla scheda. La tenuta di `VRELAY` all'alimentatore fa lo stesso senza
  toccarla.

## Da riaprire se

- Il circuito dell'alimentatore non riesce a dare la tenuta dei rail o di `VRELAY` con
  componenti ragionevoli, o il sorvegliante non scatta entro 1 ms.
- La corrente a riposo dei rail cambia molto (R128, ADR-042): la tenuta scala con I / C.
- Il corto istantaneo si rivela frequente, o capace di danni che l'argomento dei 30 W non copre
  (il finale, un diffusore diverso, le cuffie elettrostatiche dietro l'SRM-T1).
- Il finale o i diffusori cambiano (il tetto di 0,87 V è il loro).

Risponde alle due domande di **ADR-043** e ne realizza i punti 1 e 2. Realizza la nota per il
failsafe di **ADR-045**. **Precisa ADR-032**: V2 vale allo spegnimento dall'interruttore; alla
perdita di rete valgono il tetto e l'obiettivo di questa ADR.
