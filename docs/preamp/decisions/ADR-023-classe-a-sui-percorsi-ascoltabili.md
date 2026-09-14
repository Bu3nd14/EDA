# ADR-023 — Classe A su ogni percorso ascoltabile, e un buffer per ogni uscita fissa

Data: 2026-09-14 · Stato: accettata

## Contesto

**Il difetto (NC-010).** Per ADR-008 il blocco A pilotava l'attenuatore e le
due uscite fisse dallo stesso nodo, che è anche il suo nodo di
controreazione. Un apparecchio spento con Zin bassa su una fissa lo portava in
classe B:
- I_C(Q132) minima −0,23 µA a 10 Ω a valle;
- 2,40 mA a 100 Ω.

**Il limite di ADR-021.** Il punto 3 ammette la classe B a mute inserito e con
un corto al connettore. Quindi un corto su una fissa era **conforme**, e
portava in classe B lo stesso blocco A, e con lui il percorso principale e
l'altra fissa.

**La domanda.** L17 ha proposto all'utente due strade:
- (a) estendere l'eccezione di ADR-021 all'apparecchio spento;
- (b) un buffer sulle fisse.

La risposta, 2026-09-14, parole esatte:

> «Ti stai perdendo il punto principale, se c´é un corto sul un´uscita OPPURE
> se c´é un componente a bassa impedenza da spento e collegato a un´uscita
> secondaria, tutto l´ascolto "primario" non sará piú in classe A. Questo non
> é accettabile, mentre é ininfluente (se la termica é apposto) che un blocco
> NON in ascolto esca da classe A. Il punto della classe A é che deve restare
> per i path ascoltabili»

## Decisione

**1. La classe A si giudica sui percorsi ascoltabili.**

Le definizioni:
- **Un'uscita è silenziata** quando è mutata, in corto (≤ 0,01 Ω al
  connettore), o caricata da un apparecchio a valle con un'impedenza
  qualsiasi, spento compreso, che la porterebbe fuori dalla classe A.
- **Un percorso ascoltabile** è la catena di stadi fra un connettore
  d'ingresso e un'uscita non silenziata.

Il verbo, sul dominio di segnale di P7 (sinusoide 20 Hz–20 kHz fino a E6,
ogni posizione dell'attenuatore, ogni modalità di guadagno):
- **ogni stadio di un percorso ascoltabile resta in classe A**, qualunque
  condizione ci sia sulle **altre** uscite;
- **la classe B è ammessa solo negli stadi che servono esclusivamente uscite
  silenziate**, e sempre sotto il verbo di P7;
- classe A significa che **entrambi** i dispositivi d'uscita conducono per
  tutto il periodo.

**Rapporto con ADR-021.** Questa decisione precisa il punto 3 di ADR-021:
- il mute e il corto restano condizioni ammesse;
- quello che cambia è **quali stadi** possono andare in classe B;
- l'apparecchio a bassa Zin entra fra le condizioni, con lo stesso verbo
  termico;
- ADR-021 non si riscrive.

**2. Ogni uscita fissa ha il proprio buffer.** Supera ADR-008.
- **Il buffer è il `GAINBLOCK`** (T3, ADR-006), cablato come il blocco A:
  guadagno unitario per costruzione, R_g non montata. **R_IN non è montata**:
  il gate lo riporta a massa in continua l'uscita del blocco A.
- **Il blocco A pilota** l'attenuatore e i due ingressi dei buffer, e basta.
- **Dopo ogni buffer** restano 47 Ω, 4,7 µF e 470 kΩ di scarico, come prima.

Il blocco è ora usato quattro volte per canale.

## Perché

**Il principio.** Il segnale che si ascolta non deve dipendere da cosa è
collegato alle **altre** uscite. L'utente lo chiede per la ragione per cui ha
chiesto la classe A (ADR-003), e un blocco che nessuno ascolta non ha niente
da far sentire. Il criterio termico resta intero: P7 vale su ogni stadio,
ascoltato o no.

**Il buffer fa quello che il principio chiede, misurato**
(`spice/preamp/tb/tb_blockA_carichi.cir`, `data/2026-09-14/L17/`).

Con un apparecchio sulla fissa 1 da 470 kΩ a 0,01 Ω, a 1 kHz e 20 kHz:
- **blocco A**: I_C(Q132) minima **14,356 mA** in ogni riga;
- **buffer della fissa 2**: **14,509 mA** in ogni riga;
- **livello sul jack dello Stax**: si muove di 0,03 mV su 3,81 V.

**Lo stesso deck sa fallire.** Col cablaggio di ADR-008 ritrova il blocco A in
classe B a ≤ 22 Ω (1 kHz) e a ≤ 47 Ω (20 kHz). A 10 Ω e 1 kHz dà −0,2 µA,
contro i −0,23 µA di L11.

**La termica dei buffer passa P7** (`tb_mute_corto.cir`, 440 righe):
- MJE dei buffer al massimo **298,1 mW, Tj 78,6 °C**, col corto o col mute;
- l'apparecchio spento a 10 Ω scalda meno del corto: 261,3 mW;
- il blocco A non supera più il riposo: **214,0 mW** contro i 483,7 del mute
  di L11;
- nessun dispositivo supera **96,4 °C**;
- in 294 righe di percorsi ascoltabili, **0 fuori dalla classe A**.

**Il resto dei requisiti tiene** (`tb_uscite_fisse.cir`):
- **E4**: Re(Z) al jack della fissa al massimo **53,1 Ω**;
- **E5**: rumore della catena A → buffer **1,67 µV** con sorgente da 430 Ω,
  contro 9,90.

**Il costo, con i numeri:**
- **Parti**: quattro blocchi in più, da 197 a 357 componenti sulla scheda
  audio.
- **Calore**: a riposo **0,806 W per blocco**, **6,45 W** per i due canali
  contro circa 3,2 W prima. P5 prevede 3-4 W per tutto l'apparecchio: la
  differenza è **NC-029**.
- **Margine di fase**: il buffer ha lo stesso anello del blocco A di prima.
  - con la sonda da 4,7 nF sul nodo d'uscita: **40,98°**;
  - col cavo al jack, dove sta davvero: **≥ 61,74°**.

  Il rimedio di NC-002 è di L12, e ora vale per sei istanze su otto.

## Alternative scartate

- **(a) Un'ADR che estendesse l'eccezione di ADR-021 all'apparecchio spento.**
  Nessun componente, ma il percorso principale andava in classe B ogni volta
  che il Singxer o lo Stax, spenti, scendevano sotto circa 84 Ω (calcolato
  dai dati: 2·14,56 mA di riposo contro 3,818 V di picco su 47 Ω più il
  carico). Respinta dall'utente con le parole sopra.
- **Un solo buffer per le due fisse.** Metà del costo, ma una fissa silenziata
  porta in classe B anche l'altra, che si può star ascoltando. Viola il
  principio.
- **Un buffer che resti in classe A anche con l'uscita in corto.** Servirebbe
  I_q ≥ 40,6 mA con 47 Ω, calcolato: 81,2 mA di picco diviso 2. Sono circa
  4,9 W per i quattro buffer, e un secondo progetto contro T3. Il principio
  non lo chiede: un'uscita in corto non si ascolta.
- **Un'impedenza minima ammessa a valle.** Già scartata da ADR-021: il corto è
  proprio ciò che il progetto deve reggere.

## Da riaprire se

- **Si aggiunge un'uscita a livello fisso.** Serve un buffer in più, e lo
  stesso verbo si rimisura.
- **L12 cambia il blocco** in modo che il buffer non possa più essere il
  `GAINBLOCK`, per esempio con una compensazione diversa fra blocco A e
  blocco B. Allora T3 va riaperta.
- **La temperatura nel telaio**, con i quattro blocchi in più, supera i 60 °C
  su cui ADR-021 e questa decisione hanno misurato P7 (NC-029).
- **L'utente vuole la classe A anche sull'uscita che non si ascolta.**
