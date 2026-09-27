# Product Requirements Book — Preamplificatore di linea

**BOZZA del 2026-09-27 (L42c), da approvare dall'utente voce per voce.** Finché questa riga c'è,
il contratto non è firmato.

## Che cos'è, e come sta con gli altri documenti

È il **contratto fra l'utente e il team**: che cosa l'apparecchio deve fare, e perché, in al
massimo tre righe per voce. È l'ingresso di ogni revisione e di ogni lotto che segue.

Non è una seconda copia dei requisiti, perché lavora su un altro livello:
- **qui** c'è il *cosa* e il *perché*, nelle parole di chi usa l'apparecchio;
- **`REQUIREMENTS.md`** ha il *come si misura*: soglie, metodi, casi da coprire;
- **le ADR** (`decisions/`) hanno il *come si è deciso*.

La riga «Dettagli» di ogni voce nomina i requisiti tecnici e le ADR che la realizzano. Se un
requisito tecnico e una voce di qui si contraddicono, è un difetto da decidere con l'utente,
non una seconda verità. Cambiare una voce approvata vuole una ADR, come per `REQUIREMENTS.md`.

I gradini sulle uscite si dicono in **dB SPL di picco a 1 m**, con la catena di NC-028: il
finale ×21,1, le Heresy da 96 dB/1 W/1 m. Una stanza silenziosa sta a 25–35 dB(A).

---

## A. Lo scopo

**PR-1 · Sostituire il Technics SU-9070 e correggere la sua struttura di guadagno.** Con le
sorgenti e il finale di casa il volume deve lavorare a circa 30 dB di attenuazione, non a 46:
è la causa misurabile della mancanza di dinamica.
*Dettagli: E1, E3b · ADR-001 · il contesto d'uso in `REQUIREMENTS.md`.*

**PR-2 · Per questa catena, non per una generica.** Sorgenti: il phono MC a valvole (0,5 V,
430 Ω) e il FiiO K11 (2,7 V). Carichi: il cj EV250 sull'uscita principale, il Singxer SA-1 e
lo Stax SRM-T1 sulle due fisse. Diffusori Klipsch Heresy.
*Dettagli: «Contesto d'uso» in `REQUIREMENTS.md`.*

## B. Il suono

**PR-3 · Guadagno 0 dB di base, +3 e +10 dB quando servono.** Il preamplificatore non
amplifica per default. I due livelli in più servono a una sorgente debole.
*Dettagli: E1, E2, F5 · ADR-001, ADR-004, ADR-026.*

**PR-4 · Un circuito puro: classe A, tutto a componenti discreti, niente operazionali né
servo nel percorso del segnale.** Un solo stadio, progettato una volta e usato ovunque, così
ogni uscita suona uguale.
*Dettagli: T1, T2, T3, T6 · ADR-003, ADR-006, ADR-007, ADR-014, ADR-022, ADR-023.*

**PR-5 · Silenzioso sulle trombe.** Il rumore in uscita, alimentazione compresa, resta sotto
i 10 µV (circa +13 dB SPL a 1 m, inudibile in poltrona): le Heresy da 96 dB non perdonano.
*Dettagli: E5, E7 · ADR-015, ADR-020.*

**PR-6 · Invisibile alla catena.** Non carica il phono a valvole (Zin ≥ 100 kΩ), pilota il
finale e i cavi con Zout < 100 Ω costante col volume, e accetta i 2,7 V del K11 senza saturare.
*Dettagli: E3, E4, E6, E8, V3 · ADR-002, ADR-007, ADR-027 · NC-009.*

**PR-7 · Stabile con qualunque cavo e carico reale**, in ogni posizione di comandi e volume:
margine di fase ≥ 60°, una scelta severa e consapevole.
*Dettagli: V1 · ADR-019, ADR-024, ADR-025, ADR-042.*

**PR-8 · Il giudizio del suono è dell'utente, sull'hardware.** Condensatori di segnale e
resistenze critiche si cambiano senza dissaldare, per provarli all'ascolto. Nessun agente
dichiara come suona il circuito.
*Dettagli: P6 · `AGENTS.md`.*

## C. L'uso e i comandi

**PR-9 · Quattro ingressi, tre uscite.** Quattro ingressi RCA a relè. Un'uscita principale col
volume, per il finale; due uscite fisse, copia fedele della sorgente, per Singxer e Stax.
*Dettagli: F1, F3, T5 · ADR-008, ADR-009, ADR-023.*

**PR-10 · Il volume è un attenuatore a scatti**, con un commutatore rotativo e resistenze di
precisione.
*Dettagli: F4 · ADR-009.*

**PR-11 · Il trim (0, −6, −12 dB) agisce solo sull'uscita principale e si cambia solo in
mute.** Tre LED dicono il suo stato vero, non la posizione del comando.
*Dettagli: F2, F8, F9 · ADR-011, ADR-019, ADR-027.*

**PR-12 · Il guadagno si cambia solo in mute**, con tre LED del suo stato vero. A relè a
riposo, per un guasto o all'accensione, è sempre 0 dB: mai più alto.
*Dettagli: F5 e la sua nota, F11 · ADR-026, ADR-030, ADR-041.*

**PR-13 · Tutto sul frontale, niente di più.** Selettore, volume, trim, guadagno e
l'interruttore di mute, rotativi, col LED rosso di mute. Niente telecomando, niente
digitale, niente toni o filtri, niente bilanciato, niente phono integrato.
*Dettagli: F7, F10, F11, «NON-obiettivi» · ADR-009, ADR-028.*

## D. Nessun rumore fastidioso sulle uscite

**PR-14 · Nessuna commutazione si sente.** Cambiare ingresso, guadagno o trim, inserire o
togliere il mute, accendere o spegnere dal frontale: su ogni uscita al più 100 µV di picco
(~33 dB SPL a 1 m, il livello di una stanza silenziosa), in ogni condizione.
*Dettagli: V2 (A e B) · ADR-032, ADR-035, ADR-036, ADR-044, ADR-045.*

**PR-15 · Il mute sfuma, non taglia.** Con la musica, inserire o togliere il mute non fa
saltare il livello più di 20 dB in 100 ms: come il pseudo-mute del Technics, che non ha mai
dato fastidio.
*Dettagli: V2 (S) · ADR-038, ADR-039, ADR-040, ADR-050.*

## E. Fallire senza danni

**PR-16 · Il mute regge a tempo indefinito, e ogni uscita regge un corto, anche permanente,**
senza che niente si scaldi oltre i propri limiti.
*Dettagli: F6, P7, T1 (eccezione) · ADR-012, ADR-021, ADR-023.*

**PR-17 · Se manca la rete o si guasta l'alimentatore, le uscite si staccano da sole, in
hardware, prima che il circuito esca di regolazione.** Al jack principale l'obiettivo è ≤ 2 mV
(~60 dB SPL a 1 m), e in nessun caso più di 0,87 V (~112 dB, il tetto di non-danno).
*Dettagli: P9 (b) · ADR-043, ADR-046, ADR-048, ADR-051.*

**PR-18 · La sicurezza non dipende dal firmware.** Senza firmware, con il micro bloccato o
in reset, l'apparecchio resta muto e il guadagno non può cambiare con le uscite collegate.
*Dettagli: F7 · ADR-022, ADR-045, ADR-049.*

**PR-19 · Accensione e spegnimento morbidi dal frontale; l'interruttore posteriore stacca
tutto.** Da spento sul frontale l'apparecchio resta in standby, con un consumo entro il
regolamento europeo.
*Dettagli: P9 (a) · ADR-046, ADR-048 · NC-037.*

**PR-20 · Collegato alla rete, sicuro.** Un'analisi di sicurezza di rete è obbligatoria prima
della fabbricazione; senza, il progetto non va avanti.
*Dettagli: P2 · ADR-010.*

## F. Il fisico

**PR-21 · Un solo telaio, grande quanto il SU-9070** (450 × 130 × 367 mm), con
l'alimentatore a bordo, due trasformatori toroidali e **nessun alimentatore switching**.
*Dettagli: P1, P3, P4, P8 · ADR-010, ADR-029, ADR-048.*

**PR-22 · Sta in un vano chiuso della libreria**: con la stanza a 35 °C, dentro il telaio non
più di 60 °C, se attorno restano almeno 3 cm.
*Dettagli: P5 · ADR-021, ADR-047.*

**PR-23 · Si può costruire e riparare.** Nessuna parte a fine vita, e ogni dispositivo attivo
del segnale ha un modello del costruttore, così le misure simulate sono credibili.
*Dettagli: T4, T7, T8 · ADR-013, ADR-016, ADR-017, ADR-031.*

---

## Cosa il contratto non dice ancora

Rileggendo `REQUIREMENTS.md` per scrivere le voci di qui sopra, questi punti **non hanno un
requisito**, o ne hanno uno che non si può verificare. Non sono difetti del circuito: sono
domande del contratto, da decidere con l'utente.

1. **La distorsione non ha una soglia.** V4 chiede di misurarla, ma nessun requisito dice
   quanto basta. «Suonare bene» oggi è PR-4 (la tecnica) più PR-8 (l'ascolto), e nessun numero.
2. **La risposta in frequenza non ha una soglia**: né la banda, né la piattezza, né il taglio
   in basso. ADR-014 ne afferma una sulla forma, e il dossier la misura; il requisito manca.
3. **L'equilibrio fra i canali e la diafonia** non sono requisiti.
4. **Il cambio d'ingresso a caldo** sta in V2 come caso da coprire, ma il dossier non ha
   ancora una sua misura.
5. **L'offset in continua alle uscite** non ha una soglia (T4: «è di L29»). Il condensatore
   d'uscita lo blocca a regime, e i transitori sono V2.
6. **Le uscite fisse** sono «copia fedele della sorgente»: fedele quanto? Oggi vale lo stesso
   blocco (PR-4) e il guadagno 1, nessun numero.
7. **Il consumo in standby** è «entro il regolamento europeo»: il testo del Reg. (UE) 2023/826
   non è stato letto (L41a), e il numero di NC-037 (0,5 W) viene da lì.
