# ADR-049 — Il temporizzatore: ATtiny3216 e MCP4822, firmware provato sull'host, Δ e Δ₂ in hardware, `VRELAY` tolta alla scheda audio in standby

Data: 2026-09-26 · Stato: accettata

## Contesto

ADR-048 (punto 6) ha deciso il temporizzatore **ibrido**: un microcontrollore per la sequenza e
l'ordine di sicurezza in hardware. Ha lasciato a L41b quattro cose:
- il micro e la sua specifica;
- il ritardo Δ fra `MUTE_CMD` e `PERMIT_CMD` in hardware;
- il pilota delle LDR (profilo v4, da 20 mA a 10 nA);
- lo standby di NC-037: le bobine del trim, pilotate di continuo in mute, fanno ~0,44 W contro un
  limite di 0,5 W.

`NEXT-SESSION.md` chiedeva di portare all'utente, prima di scrivere codice, la scelta del micro
(con i numeri: consumo in standby, reperibilità, programmazione) e il modo di provare il
firmware, che in SPICE non si simula.

## Decisione

**Dell'utente.** Il 2026-09-26 l'utente ha approvato, senza commenti, il piano di L41b che
conteneva tre proposte con le cifre:
1. **il micro è un ATtiny3216** (tinyAVR, 5 V, SOIC-20), **più un DAC doppio a 12 bit MCP4822**
   per le due stringhe delle LDR;
2. **il firmware vive in `firmware/preamp_timer/`**, fuori da `circuits/`. Ha una specifica a
   tabella (`spec/timer_spec.md`) come contratto, una logica pura in C provata sull'host con
   `clang`, e le forme d'onda dei test diventano le sorgenti del banco SPICE;
3. **L41b si divide in L41b1** (l'hardware e la specifica) **e L41b2** (il firmware).

**Di progetto** (non dell'utente; cifre in `docs/preamp/data/2026-09-26/L41b1/`):
4. **Δ in hardware.**
   - `PERMIT_T` si carica attraverso un diodo da `MUTE_REQ` **o** da `PERMIT_REQ`, e si scarica
     in 332 kΩ · 100 nF C0G.
   - U508 A (TLV1702) lo confronta con `VREF`.
   - Δ = 19,9 ms di calcolo; sul circuito 18,8 ms nominali e 16,9 ms all'angolo minimo.
   - Un diodo Schottky tiene `MUTE_G` ≤ `PERMIT_G`: i jack non si eccitano prima del
     permissivo.
5. **`VRELAY` si toglie alla scheda audio in standby** (NC-037).
   - Q505 (AO3401A) sul lato alto, fra l'uscita di U503 (`VRELAY_REG`) e J1 pin 4, che conserva
     il nome `VRELAY` del contratto.
   - **L'interruttore è tenuto in hardware**: `VR_T` si carica da `PERMIT_T` e da `VRELAY_EN`, e
     si scarica tre volte più lento. Si apre ≥ Δ₂ dopo `PERMIT_G`: 56–60 ms sul circuito.
   - Senza questo, un micro che va in reset con la musica in corso toglierebbe tutte le bobine
     insieme: il caso «senza Δ» di L30, 69 mV, ~90 dB SPL di picco a 1 m.
   - Sorvegliante, tenuta, logica e K501 restano su `VRELAY_REG`, come in L41a.
6. **Il pilota delle LDR**: un convertitore esponenziale per stringa.
   - Il circuito: una coppia NPN accoppiata (BCM847BS), la base di Q1 a `VREF` con I_ref =
     100 µA tenuta da un op-amp (MCP6004) attraverso un inseguitore PNP, la base di Q2 comandata
     dal DAC attraverso un buffer, e uno specchio PNP degenerato che fornisce la corrente
     all'anodo di J3.
   - Il ritorno: catodo a GND attraverso 10 Ω, la lettura del micro.
   - Il firmware compensa Vt col sensore di temperatura del micro, e calibra a due punti (20 mA
     e 2 mA) la parte ohmica e gli offset.
   - Un pull-down da 100 k sull'uscita del DAC fissa il minimo col DAC in reset: 2–9 nA, mai 0.
   - Tutto sta su V5: coi LED al massimo (2,0 V a 20 mA) restano 0,34 V di margine sullo specchio.
7. **Ogni comando del micro ha un pull-down**, e la rilettura di `MUTE_G` passa per 1 MΩ, così un
   pin configurato male non lo può alzare. Il 2e lo asserisce (`--timer`, ADR-022 condizione 1).

## Perché

**Il micro** (letto sui datasheet, `vendor/microcontroller/microchip/ATtiny3216`):
- power-down 0,1 µA tipici, 2 µA massimi a 25 °C: nel bilancio dello standby è meno dell'1 %;
- dopo un reset le uscite sono in alta impedenza, quindi coi pull-down il reset vale riposo;
- 5 V come il resto della logica (`V5`, comparatori). Un micro a 3,3 V vorrebbe un regolatore e
  le traslazioni di livello;
- si programma con un solo filo (UPDI), con strumenti liberi su macOS.

**Il DAC** e non la PWM: il nodo delle LDR è a 1 MΩ e vede l'anodo attraverso 0,5 pF, col limite
di 0,69 mV/√Hz (ADR-039). Il residuo di una PWM filtrata andrebbe dimostrato. Col DAC il rumore
all'anodo è ~1,4 µV/√Hz nel caso peggiore, e il passo è 0,06 dB per LSB.

**I ritardi a comparatore** e non sulla soglia del 2N7002: col solo Vth (1,0–2,5 V) Δ varierebbe
di ~2,6 volte.

**La compensazione e la calibrazione.** Senza compensazione di Vt il profilo sbaglia di +8,7 dB a
60 °C sul riposo e di +5,9 dB sul ginocchio. Con la compensazione sta entro ±0,3 dB, tranne la
cima (−3 dB, la parte ohmica dei transistor). Con la calibrazione sta entro ±0,92 dB.

## Alternative scartate

- **Un micro a 3,3 V** (STM32, RP2040): un regolatore e le traslazioni in più. L'RP2040 in
  «dormant» fa ~0,2 mA.
- **Il DAC interno a 8 bit dell'ATtiny**: 0,5 dB per passo, e una sola uscita.
- **La PWM filtrata**: il residuo sul nodo a 1 MΩ va dimostrato.
- **Il ritardo RC solo su `PERMIT_REQ`** (la lettura letterale di `NEXT-SESSION.md`): un firmware
  che abbassa `PERMIT_REQ` prima di `MUTE_REQ` violerebbe Δ. Caricare `PERMIT_T` anche da
  `MUTE_REQ` lo impedisce.
- **L'interruttore di `VRELAY` comandato solo dal micro**: il reset del micro diventa il caso
  «senza Δ».
- **Il pilota sui 12 V**: più potenza dissipata nello specchio e nella coppia. Sui 5 V la
  tensione di conformità basta.
- **Il 13 ms di ADR-027 in hardware**: resta del firmware (§ 4.1 della specifica). Il mandato lo
  mette fra i compiti del micro, e un errore lì sbaglia lo stato del trim, non l'ordine dei
  jack.

## Da riaprire se

- La calibrazione a due punti non tiene la cima entro ±1 dB sul prototipo: per esempio
  l'autoriscaldamento di Q2 a 20 mA (~44 mW, non modellato), o l'ADC che non risolve 20 mV.
- SPI0 in modalità host non lascia usare PA2 come ingresso analogico: la SPI va in software
  (specifica § 2).
- La perdita a vuoto di T2 supera ~0,40 W: lo standby esce da 0,5 W (NC-037).
- NC-038 si chiude cambiando la cima della tabella: cambia la calibrazione, non il circuito.

**Precisa ADR-048** al punto 6: l'RC di Δ si carica dalla richiesta di mute oltre che da
`PERMIT_REQ`, e lo standby toglie `VRELAY` alla scheda audio attraverso un interruttore tenuto in
hardware.
