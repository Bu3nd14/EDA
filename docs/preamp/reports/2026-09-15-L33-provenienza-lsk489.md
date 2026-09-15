# L33 — Le etichette di provenienza dell'LSK489 (2026-09-15)

Lotto **L33**. Chiude **NC-031**. Nessuna ADR. Dati: `data/2026-09-15/L33/`
(vedi il suo `README.md`).

**Nessun numero è stato rieseguito, e nessun valore del circuito o modello è
cambiato.** Il lotto corregge frasi. Cosa si simula resta com'era:
- l'LSK489 è **`LSK489X`**, segnaposto scritto a mano in
  `spice/preamp/placeholder_devices.lib`, `KF = 0`;
- l'unico modello del costruttore è l'**LS352** (`models/bjt_pnp/ls350.lib`),
  senza `KF`;
- **nessun dispositivo simulato ha rumore 1/f** (NC-004).

## 1. La baseline, contata

`esplorazione/conta.py` cerca le forme trovate leggendo, su ogni file di testo
di `spice/`, `circuits/`, `scripts/` e sui README di `docs/preamp/data/`. Output:
`esplorazione/conta.txt`.

| | NC-031 diceva | Contato |
|---|---|---|
| Deck con una frase falsa | 13 | **15** |
| README datati, frase esplicita | 3 | **5** |
| README datati, frase implicita | — | **2** |

- **Deck.**
  - 12 col commento di L22, «VENDOR model – the only real device model in this
    deck besides the LSK489»;
  - `tb_trim.cir:43`, «KF = 0 but on the LSK489»;
  - **i due che NC-031 non elencava**: `tb_blockA_carichi.cir:40` e
    `tb_mute_corto.cir:54`, «tutto tranne LS352 e LSK489 e' segnaposto». La
    ricerca di L32 cercava «vendor»/«real»; queste due dicono la stessa cosa in
    italiano.
- **README espliciti.**
  - `data/2026-09-14/L12`, `L27`, `L16`: «segnaposto più LS352 e LSK489 vendor»;
  - `data/2026-09-14/L17`: «tranne LS352 e LSK489»;
  - `data/2026-09-10`: «nel percorso di segnale solo lo specchio e l'LSK489
    hanno un modello del costruttore».
- **README impliciti.** `data/2026-09-13` (due punti) e `data/2026-09-14`
  scrivono «LSK489 fuso in una Part, specchio LS352 a 220 Ω, ogni altro
  dispositivo ancora segnaposto», che si legge come se l'LSK489 non lo fosse.
- **Fuori conto**: la copia datata
  `data/2026-09-14/L16/esplorazione/deck/tb_blockA_carichi_trim.cir:40`. È
  output di L16 e non si tocca.
- **Non false, e non toccate**: `tb_zout_psrr_noise.cir:12` (dice che l'1/f
  dell'LSK489 *manca*), l'elenco dei nomi in `tb_mute_corto.cir:49`,
  `circuits/preamp/gain_block.py` (righe 89 e 294 parlano di simbolo e datasheet).

**Da quando è falsa.** Non è mai stata vera nei deck del blocco:
- `LSK489X` c'è dalla Fase 2 (`git log -S LSK489X`: introdotto in `d9ca07f`,
  mai tolto);
- `git log -S "jfet/lsk489.lib" -- spice circuits` è **vuoto**;
- `LSK489A` in `circuits/` compare solo come testo «(LSK489A/B)» nella
  descrizione del simbolo dentro le netlist KiCad, cioè il grado, non il
  modello.

## 2. Il guardiano: sì, blocco 2h

**La decisione.** La frase è viaggiata **copiando l'intestazione di un deck**:
dodici deck identici da L22, rimasti falsi per dieci lotti. Nella Fase 4 i modelli
cambieranno e le intestazioni verranno copiate di nuovo. E il dossier da L32 non
crede più ai commenti, ma chi apre un deck sì. Un controllo meccanico costa poco,
se il criterio non va riscritto.

**Cosa fa.** `scripts/check_deck_provenance.py`:
- **la verità** è la `provenance()` di `docs/preamp/dossier/build_dossier.py`,
  **importata**: include → `.model` → nomi istanziati nel blocco → `models/` con
  `.provenance.json` (costruttore) o `placeholder_devices.lib` (segnaposto). Il
  modulo si importa senza effetti: `refuse()` accumula in una lista, e il
  guardiano la legge;
- **le affermazioni** vengono dalle righe `*`, lette a paragrafi e frasi, in sei
  forme: «vendor/real device/costruttore … besides PARTE», «tranne PARTE [e
  PARTE] … segnaposto», «solo PARTE … modello del costruttore», «KF = 0 but on
  PARTE», «PARTE … vendor» e «PARTE … placeholder». Le ultime due valgono entro
  40 caratteri, senza negazioni, parola opposta o altra parte nel mezzo;
- **esce** 0, 1 con contraddizioni, 2 se la provenienza non si legge o se non
  trova nessuna affermazione in nessun deck.

**Cosa non vede**: un modo nuovo di dire «vendor». È una rete tessuta sulle frasi
trovate, non un lettore; lo dice la sua docstring.

**Fatto cadere, prima di correggere** (`prima/`):
- sui 17 deck di `main`, **rc 1, esattamente 15 contraddizioni**, una per deck.
  `tb_loop_bufferfissa` e `tb_uscite_fisse` OK, zero affermazioni
  (`prima/guardiano.txt`);
- `run_tests.sh`: **8 passed, 1 failed**, il 2h;
- sui 16 deck di `6748fbc` (L12, prima di L27), **14**: la stessa frase, e
  `tb_trim` non esisteva ancora (`prima/guardiano_6748fbc.txt`);
- **11 sabotaggi su 11** come attesi (`esplorazione/falsi/esito.txt`), partendo
  dai deck corretti:

  | Caso | rc |
  |---|---|
  | deck corretto intatto | 0 |
  | frase di L22 rimessa | 1 |
  | LSK489 rimesso fra le eccezioni di «tranne» | 1 |
  | «KF = 0 but on the LSK489» rimesso | 1 |
  | «The LSK489 is a vendor model» | 1 |
  | «solo LS352 e LSK489 hanno un modello del costruttore» | 1 |
  | LS352, del costruttore, detto segnaposto | 1 |
  | include `ls350.lib` tolto | 2 |
  | «The LSK489 is not a vendor model» | 0 |
  | «The 2N5551 is a placeholder» | 0 |
  | «The 2N5551 is a vendor model» | 1 |

## 3. I deck, solo nei commenti

`esplorazione/correggi.py` applica sostituzioni esatte, e ciascuna deve
comparire una volta sola, altrimenti rifiuta senza scrivere. La frase nuova dice
cosa danno gli include:
- **12 deck di L22**: l'LS352 è il solo modello del costruttore; l'LSK489 no,
  `LSK489X` con `KF=0`, e `models/jfet/lsk489.lib` non lo include nessun deck
  (Fase 4, NC-017); nessun dispositivo ha 1/f;
- **`tb_trim`**: «KF = 0 on every model, the LSK489's LSK489X placeholder too»;
- **`tb_blockA_carichi`, `tb_mute_corto`**: «tutto tranne LS352 e' segnaposto,
  LSK489 compreso (LSK489X in placeholder_devices.lib, KF=0; NC-017, NC-031)».

**La prova che tocca solo commenti** è `esplorazione/solo_commenti.py`. Legge i
deck di `main` estratti con `git archive -o`, poi confronta con `difflib`:
- ogni riga tolta o aggiunta deve cominciare con `*`;
- la sequenza delle righe non di commento deve essere identica;
- l'insieme dei file deve coincidere.

Esito (`dopo/solo_commenti.txt`): **15 deck cambiati, 0 con righe non di
commento**, rc 0. **Fatto cadere** su una copia con `VPP VPLUS 0 DC 16` in
`tb_op.cir`: rc 1, la riga indicata.

Dopo: guardiano **rc 0 sui 17 deck** (`dopo/guardiano.txt`), 2g verde,
`run_tests.sh` **9 passed / 0 failed**.

## 4. I README datati, annotati

`esplorazione/annota.py` aggiunge **in coda** a ciascuno dei sette una sezione
«Nota di L33 (2026-09-15) — la provenienza dell'LSK489». Cita la frase sbagliata,
dice cosa si simulava, e rifiuta se la frase non c'è o la nota c'è già. Il testo
sopra non cambia: `git diff main` su quei file ha **solo righe aggiunte**.

**Trovato, nel README del 2026-09-10**: «il contributo del JFET qui è
conservativo» (NC-013). Non si applica a quei dati: il modello d'angolo di NC-013
è `LSK489A`, e lì non era simulato. È annotato nella stessa nota. **Non rende
falso nessun numero pubblicato**: è un giudizio su un numero, e cade.

## 5. Cosa non è cambiato, verificato

- **Il dossier non si rigenera, e non serve.** `docs/preamp/dossier/index.html`
  ha 16 righe di provenienza, tutte «Modelli del costruttore: **LS352** ·
  segnaposto scritti a mano: **1N4148, 2N5401, 2N5551, LSK489, MJE15032,
  MJE15033**». La premessa del mandato («da L32 legge la provenienza dagli
  `.include`») è vera, e il 2h usa proprio quella funzione.
- **NC-004** dice «nel repo solo l'LSK489 ha rumore 1/f». È precisata nella voce
  e in `STATE.md`: vero di `models/`, non delle simulazioni. Nessuna ADR
  toccata.
- **Nessuna cifra rieseguita**, `vendor/` non toccato.

## 6. Osservazioni, fuori lotto

- **Il mandato contava male anche i lotti.** Diceva «è il più piccolo fra gli
  aperti; gli altri aspettano qualcosa», e nominava L29, L30 e L28. **L13** e
  **L20** sono «da fare» nella tabella e non aspettano nessuno. Il prossimo
  lotto è **L13**.
- **Per L20**: nessuna cifra simulata del repo usa `LSK489A`. Il lotto sarà la
  prima volta che quel modello entra in un deck del blocco, e il 2h controllerà
  la frase che lo annuncia.
