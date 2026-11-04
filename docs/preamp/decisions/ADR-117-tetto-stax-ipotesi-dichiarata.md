# ADR-117 — Il tetto di non-danno sulla Stax resta 0,87 V per 150 ms, dichiarato come ipotesi

Data: 2026-11-04 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Precisa ADR-081 e ADR-086** (il tetto sulla Stax, 0,87 V per al più 150 ms): i numeri non cambiano,
  cambia che cosa dicono. Aggiunge una frase ai «Dettagli» di **PR-30**; la voce resta com'è.
- Non chiude **NC-046** (la traduzione dei gradini delle fisse in dB SPL all'orecchio): quella è un'altra
  metrica, del fastidio e non del danno, e resta aperta.

## Contesto

La revisione dell'architetto avversariale di L65 (`reports/2026-11-04-L65-architetto-avversariale.md`,
rilievo **R5**) nota che 0,87 V è il punto in cui il finale da 30 W delle Heresy arriva al clipping
(~112 dB SPL di picco a 1 m): non è un limite della Stax. L'energizzatore SRM-T1 è accoppiato in continua
e ha 60 dB di guadagno (100 mV per 100 V); a volume massimo satura già con 0,1–0,3 V in ingresso. Stax non
pubblica un limite di danno.

## Decisione

Il tetto resta **0,87 V per al più 150 ms** col carico della Stax, ed è scritto come **ipotesi dichiarata**,
non come limite del costruttore. Scelta dell'utente, 2026-11-04: **«Tenere e dichiarare»**; firma sul testo
dei «Dettagli» di PR-30: **«Firmo così»**.

## Perché

- Un limite pubblicato non c'è: qualunque altra soglia sarebbe un'ipotesi anche lei, e questa ha il
  vantaggio di essere già misurata su tutta la FMEA.
- Il calcolo dell'architetto, col condensatore da 1 µF e il carico di 41,2 kΩ, gradino da 14 V: sopra
  0,87 V **115 ms**, sopra 0,3 V **158 ms**, sopra 0,1 V **204 ms** (al +5 % del condensatore: 120 / 166 /
  214 ms). Col volume dell'energizzatore a −20 dB la soglia equivalente sale a ~3 V e il tempo scende a
  **~63 ms**.
- Riformulare PR-30 sul «tempo in saturazione dell'energizzatore» vorrebbe un lotto di misura e potrebbe
  cambiare il circuito senza un dato del costruttore che lo giustifichi.

## Alternative scartate

- **Riformulare PR-30** come tempo in saturazione dell'energizzatore: un lotto e un possibile cambio di
  circuito, contro un limite che nessuno conosce.
- **Una regola d'uso** (il volume dell'energizzatore sotto −20 dB): non scelta dall'utente.

## Da riaprire se

- Stax, o una misura affidabile, pubblica un limite di danno per gli statori o per l'energizzatore in
  saturazione più basso di ~200 ms.
- A valle della fissa 2 entra un apparecchio diverso dall'SRM-T1 (PR-30: «un apparecchio nuovo a valle fa
  rivedere il preamp»).
