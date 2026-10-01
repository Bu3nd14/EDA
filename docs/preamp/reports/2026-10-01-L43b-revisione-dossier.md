# 2026-10-01 — L43b, la revisione dell'utente col PRB come contratto, e la sintesi con l'architetto

**Documento datato: non si riscrive.** Le voci che apre vivono in `../NONCOMPLIANCE.md`. La metà
dell'architetto è in `2026-09-27-L43a-architetto-avversariale.md` (verbatim) e
`2026-09-27-L43a-esiti-architetto.md` (le decisioni dell'utente).

## Che cosa è stato questo lotto

È la **seconda revisione umana del dossier**, dopo L5e (`2026-09-09-revisione-utente-dossier.md`),
e la prima **col PRB come contratto** (ADR-053). L'utente ha letto il dossier di L42 così
com'era, non rigenerato dopo L43a, nel PDF A4 di `stampa_a4.py`, scritto fuori dal repo e
copiato sulla sua macchina.

**La cecità.** L'utente **non** era cieco rispetto all'architetto: aveva visto i suoi rilievi in
L43a, prima di finire la lettura. Era cieco rispetto all'orchestratore, che non ha cercato
difetti per conto suo e ha tenuto per sé i tre punti «per L43» di `STATE.md` fino a quando
l'utente ha dichiarato finita la lettura («ho finito con le mie osservazioni»).

## Che cosa ha fatto l'orchestratore

- Ha generato il PDF A4 e l'ha copiato con `scp` sulla macchina dell'utente, come richiesto.
- **Ha risposto a una domanda dell'utente** coi dati del repo, senza rieseguire niente: «mi dici
  il rumore (ripple) residuo dell'alimentatore? e come si rapporta alla PSRR a 10 kHz sul rail
  positivo?». La risposta: il residuo dei rail **non è mai stato simulato** (regolatori
  comportamentali senza PSRR né rumore; il modello TI del TPS7A4701 dà un punto di lavoro
  sbagliato). Il budget di ADR-020 a 10 kHz invece è noto: PSRR+ 23,03 dB e 14,2 µV RMS per un
  tono. Dalla domanda è nato il primo rilievo.
- Cercando il CSV del PSRR per l'evidenza di quel rilievo, **ha trovato per caso** che la nota su
  E5 cita dei CSV che non esistono. L'ha tenuto per sé fino alla fine della lettura, come i punti
  «per L43».
- Ha registrato le voci, con la severità decisa dall'utente; dove la severità era una proposta
  dell'orchestratore, la voce lo dice.

## Tutti i rilievi, con chi li ha trovati

| Rilievo | Chi l'ha trovato | Già noto o deciso? | Severità | Voce |
|---|---|---|---|---|
| Distorsione crescente verso gli acuti, il Miller da 1 nF (R1) | architetto | ADR-042 lo aveva scelto per V1 | bloccante (G1) | NC-039 |
| Ingresso in continua, cambio d'ingresso (R2) | architetto | nuovo | bloccante (G1) | NC-040 |
| Continua del blocco A attraverso trim e volume (R3) | architetto | nuovo; il dossier diceva il contrario | bloccante (G1) | NC-041 |
| I tre livelli di guadagno non servono (R4) | architetto | ADR-004, ADR-026 | **respinto** | — |
| Nessuna FMEA della scheda audio (R5) | architetto | nuovo | maggiore, prima di G2 | NC-042 |
| VTL5C4 fuori produzione (R6) | architetto | nuovo | bloccante (G2) | NC-043 |
| Anello di massa senza requisiti (R7) | architetto | nuovo | bloccante (G2) | NC-044 |
| Pilota delle LDR e mute da 6 s oltre il necessario (R8) | architetto | ADR-039, ADR-049, ADR-050 | minore | NC-045 |
| Metrica dei gradini senza le cuffie (R9) | architetto | nuovo | minore | NC-046 |
| **Il PSRR del rail positivo è troppo basso per contare sul solo alimentatore** | **utente** | **in parte**: NC-011 (aperta dall'utente in L5e) e ADR-020; nuovo è che il rimedio possa servire nel blocco | **bloccante (G1)** | **NC-047** |
| **Nessun placement e routing di prova: il dossier non garantisce la fattibilità** | **utente** | **nuovo**; P8 rimandava la verifica dei PCB a G2 | **bloccante (G1)** | **NC-048** |
| S del mute con le LDR a 12 mA mai misurato | orchestratore (L42a, «per L43») | ADR-050 | maggiore | NC-049 |
| Tenuta di `VRELAY` scesa da 62,8 a 36,1 ms | orchestratore (L42b, «per L43») | P9 (b) regge | minore | NC-050 |
| Commento di `C_VRELAY` con le cifre di L41a | orchestratore (L42b, «per L43») | — | minore | NC-051 |
| La nota su E5 cita CSV che non esistono | orchestratore (L43b, per caso) | — | minore | NC-052 |

**Nessun rilievo è stato trovato da entrambi.** L'utente non ha registrato niente che coincida con
NC-039…NC-046, quindi nessuna di quelle voci porta la nota «trovato anche dall'utente».

Il rilievo sul PSRR **tocca** però due cose dell'architetto. R4 citava il PSRR+ a 10 kHz (32,96 dB
a 0 dB, 23,03 dB a +10 dB) come argomento contro il guadagno +10 dB, non come difetto, e R4 è
stato respinto. NC-039 ha la stessa radice: il Miller da 1 nF è costato ~6,5 dB di PSRR+ (L40).
Visto che l'utente aveva già letto l'architetto, non si può dire che l'abbia trovato in modo
indipendente; ma l'architetto non l'ha mai formulato come rilievo.

## La taratura

**Letta sapendo che l'utente aveva già letto l'architetto.** Una coincidenza sarebbe stata poco
informativa; l'assenza di coincidenze invece dice qualcosa: l'utente non ha ripreso nessuno dei 9
rilievi, ha cercato altrove.

**Cosa ha trovato l'architetto che l'utente non ha visto.** Tutti gli otto rilievi accettati. È
atteso, perché l'utente li aveva già letti e non aveva motivo di ripeterli. Non è una misura di
quello che l'utente avrebbe visto da solo.

**Cosa ha trovato l'utente che l'architetto non ha visto.**
- **Il PSRR come problema del blocco, non solo dell'alimentatore.** L'architetto ha letto il
  PSRR+ e l'ha usato come argomento di prodotto (R4), senza confrontarlo col budget di ADR-020 né
  col fatto che il residuo dei rail non è mai stato simulato. L'utente ha unito i due capi.
  **È la stessa debolezza che aveva segnalato in L5e** (NC-011, «il PSRR del rail positivo non
  vincola nessuno»): tre settimane dopo, ci è tornato sopra dal lato del rimedio.
- **La fattibilità fisica.** Né il dossier né l'architetto ragionano sullo spazio. L'architetto è
  per mandato in sola lettura su architettura, requisiti e ADR, e il dossier per costruzione non
  contiene una scheda. È un'omissione di **processo** (l'ordine delle fasi rimandava la verifica
  dei PCB a dopo il congelamento), non di circuito; solo chi guarda il progetto dall'esterno del
  suo metodo poteva vederla.

**Cosa non ha trovato nessuno dei due.** I tre punti «per L43» e i CSV della nota su E5. Sono
tutti dell'**evidenza** (una misura mancante, un margine ridotto, un commento superato, una fonte
non apribile), non del giudizio. Si trovano rieseguendo, e nessuno dei due revisori ha
rieseguito l'alimentatore o il mute. È la stessa lezione di G0 in L5d, rovesciata: lì il metodo
che incrocia affermazioni e sorgenti trovava le affermazioni false e non le omissioni di
giudizio; qui due revisori di giudizio trovano le omissioni e non le evidenze scadute.

**In sintesi.** L'architetto è forte sulle omissioni di giudizio dentro il circuito (continua,
guasti, massa, obsolescenza). L'utente è forte su quelle di sistema e di processo (budget fra le
due schede, fattibilità fisica). Le evidenze scadute le trova solo chi riesegue: il dossier
rigenerato (L42) le ha trovate, e i revisori no.

## Il confronto con L5e

| | L5e (2026-09-09) | L43b (2026-10-01) |
|---|---|---|
| Rilievi dell'utente | 4 | 2 |
| Bloccanti fra questi | 1 | 2 |
| Classe | omissioni di giudizio (il blocco A che pilota tre carichi) | omissioni di sistema e di processo |
| Tema ricorrente | il PSRR del rail + (NC-011) | il PSRR del rail + (NC-047) |

## I tre punti «per L43»

| Punto | Trovato dall'architetto | Trovato dall'utente | Esito |
|---|---|---|---|
| S del mute con la cima delle LDR a 12 mA mai misurato (ADR-050) | no | no | **NC-049**, maggiore: si misura nel lotto della cella del mute, prima di G1 |
| La tenuta di `VRELAY` scesa da 62,8 a 36,1 ms a rete −10 % (P9 ≥ 25 regge) | no | no | **NC-050**, minore: margine da ricontrollare quando il carico cambia |
| Il commento di `C_VRELAY` in `psu.py` con le cifre di L41a | no | no | **NC-051**, minore: si corregge nel prossimo lotto che tocca `psu.py` |

## L'ordine dei lotti di rimedio, scelto dall'utente

Proposto dall'orchestratore e scelto dall'utente così com'era («la proposta così com'è»). La
regola dietro l'ordine: prima il cuore del blocco, poi ciò che cambia footprint, il placement e
routing di prova per ultimo, sulla topologia stabile.

1. **L46 — il blocco di guadagno: compensazione, distorsione verso gli acuti, PSRR+** (NC-039,
   NC-047; NC-052 col ricalcolo dei limiti di ADR-020).
2. **L44 — il rumore 1/f** (NC-004), sul blocco di L46. Prima di questa revisione era il primo.
3. **L47 — la cella del mute**: il sostituto della VTL5C4, il pilota nuovo, il mute più corto, S
   misurato (NC-043, NC-045, NC-049); il pilota sta in `psu.py`, quindi anche la tenuta di
   `VRELAY` e il suo commento (NC-050, NC-051).
4. **L48 — il selettore d'ingresso e la continua** (NC-040, NC-041).
5. **L49 — placement e routing di prova** delle due schede (NC-048), subito dopo il selettore,
   come aveva chiesto l'utente.
6. **G1.**
7. **L45 — la FMEA** (NC-042, con NC-046), prima di G2.
8. **L50 — la massa e la terra** (NC-044), prima del layout di G2.

## Il registro, a fine lotto

**23 voci aperte, 8 bloccanti**: NC-004, NC-039, NC-040, NC-041, NC-047 e NC-048 per G1;
NC-043 e NC-044 per G2. Nessuna ADR scritta, nessuna voce del PRB cambiata, nessuna modifica al
circuito, al firmware, ai deck o al dossier.
