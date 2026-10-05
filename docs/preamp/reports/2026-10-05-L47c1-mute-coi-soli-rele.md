# L47c1 — Il mute coi soli relè: la decisione, il contratto, l'hardware (2026-10-04/05)

**ADR-062. PR-21 riscritta e firmata. NC-043 chiusa per superamento; NC-049 e NC-053 superate nel
requisito, aperte fino alla matrice V2 di L47c2.** Dati: `data/2026-10-05/L47c1/` (README).

## Perché

Dopo L47b2b1 l'utente ha scelto **«Taglio coi soli relè»** (STATE, «Dopo L47b2b1»). La sfumatura
del mute serviva solo a PR-21. Il prompt di L47c chiedeva, prima di ogni modifica, cinque risposte
all'utente, da fare per nome.

## Le risposte dell'utente (2026-10-04)

| Domanda | Risposta |
|---|---|
| Il testo nuovo di PR-21 | **«Il mute taglia: con la musica il silenzio arriva di colpo, e al rilascio la musica torna di colpo al livello di prima»**. Firmato. **Nessun tetto al clic**: si misura e si dichiara |
| Il salto di livello S in V2 | **Tolto** (non resta come diagnostica) |
| Il tempo fra il tasto e i relè | **Subito** (restano l'antirimbalzo e il permissivo sfasato) |
| L'impronta propria della NSL-32SR3 | **Tolta** |
| Dividere il lotto | **Due parti**: L47c1 e L47c2 |

**Una correzione alla divisione, dichiarata all'utente nel piano.** La proposta metteva
l'alimentatore nella seconda parte. Ma il controllo del cablaggio fra le schede (2j) confronta J3
sulle due: J3 non può uscire da una sola. Quindi L47c1 toglie **tutto l'hardware** della
sfumatura, e L47c2 fa le misure dell'alimentatore, il firmware, V2 e i guasti.

## Che cosa cambia

- **La decisione e il contratto.**
  - **ADR-062** supera ADR-038 (la sfumatura; i relè al jack restano), ADR-039, ADR-040, ADR-058…061,
    e ADR-049 e ADR-050 sul solo pilota (il micro, Δ e Δ₂ restano).
  - **PRB**: PR-21 col testo firmato, e l'elenco delle voci cambiate dopo la firma in testa.
  - **REQUIREMENTS**: V2 senza S. C, il residuo del fit attorno al taglio, è il clic del taglio:
    misurato e dichiarato, senza soglia. La nota su E3 durante la sfumatura è superata, ed E5 ha
    la cifra nuova.
- **La scheda audio** (`preamp_audio.py`): via U101/U102/U301/U302 e J3 col suo contratto, e via
  `FP_NSL32`. Il connettore d'ingresso torna sull'ingresso del blocco A, come prima di L29b2; il
  contratto di J4 non nomina più la sfumatura.
- **L'alimentatore** (`psu.py`): via il pilota delle LDR, 33 parti (U510 MCP4822, U511, Q507–Q512,
  18 resistenze, 6 condensatori), e J3. Cinque pin del micro restano liberi: PA1, PA2, PA3, PA4,
  PB4. Il commento di `C_VRELAY` dice che le sue cifre non sono attuali (NC-051, L47c2).
- **L'impronta** `library/preamp.pretty/NSL-32SR3_LED3.30` è tolta.
- **I controlli.**
  - **2e**: `check_ldr` diventa `check_input`. Nessuna parte della libreria Isolator, nessun valore
    che nomini una LDR, e il pin 1 di IN_<canale> sul nodo di R_IN = 1 MΩ verso GND, col pin 2 su
    GND.
  - **2j**: J3, `LED_PINS`, `LDR_AUDIO` e la verifica dei PNP tolti. `LDR_CMD` e le sue reti
    devono mancare **su tutte e due** le schede.
  - **I falsi**: 9 su 9 cadono per il motivo giusto, comprese le netlist di `main`
    (`falsi/verdetti.txt`).
- **Gli schemi a blocchi.** Su quello della scheda audio il selettore va dritto al blocco A, e le
  asserzioni vogliono J101/J301 sul nodo di R_IN, niente Isolator, niente J3. Su quello
  dell'alimentatore il pannello 3 dice che il pilota non c'è più, e le asserzioni vogliono U510,
  U511, J3 e le loro reti assenti.
- **I deck.** `tb_e3_e5_ldr.cir` diventa `tb_e3_e5.cir`, senza celle e senza accoppiamento
  LED-cella. In `tb_trim.cir` e `tb_e3_e5.cir` il minimo di E3 si prende con `vecmin()`
  (limitations **#45**).
- `trim.py` e `gain_interlock.py` non nominavano né J3 né le celle: non toccati. In `gain_block.py`
  cambiano solo i commenti di E3, E5 e del mute.

## Le misure

| | senza celle (L47c1) | con le celle (L47b2b1) |
|---|---|---|
| E3, minimo vero al connettore (20 kHz, selettore 68 pF) | **114,7 kΩ** (≥ 100) | 105,8 kΩ |
| E5, peggiore (trim 0, +10 dB, attenuatore al massimo, 430 Ω) | **5,496 µV** (≤ 9,90), ~8,2 dB SPL a 1 m | 5,530 µV |

- **Le netlist, confrontate per connettività**:
  - scheda audio: escono solo le cinque parti, e J101/J301 entrano in `AL_IN`/`AR_IN`. ERC 47
    avvisi e 0 errori, come prima;
  - alimentatore: escono solo le 33 parti, e i 5 pin del micro restano soli. ERC da 21 a 24
    avvisi, gli stessi 2 errori spiegati.
- **La regressione dei 21 deck veloci**: rc 0 su 21. Su 248 file cambia **solo** la colonna
  `zmin_ohm` di `tb_trim_e3.csv`, −4,4 % al massimo (la #45), più il deck rinominato. E5 coincide
  con la riga «nessuna» di L47b2b1 entro 5,4·10⁻⁶.

## Trovato strada facendo: limitations #45

`meas ac zmin min zmag from=20 to=20000` salta l'ultimo punto della scansione, i 20 kHz, dove
|Zin| è minima. Così E3 riportava un minimo **più alto** di `z20k`, cosa che un minimo non può
essere. La sonda: `meas min` 120 051 Ω a 19,1 kHz, `vecmin()` e `find at=20000` 114 721 Ω.
- **Con le celle** E3 era quindi **105,8 kΩ, non i 110,7 dichiarati da L47b2a**: dentro, con meno
  margine.
- **`tb_trim.cir`** è stato corretto.
- **Nessun altro deck canonico** usa un `meas min/max` su una finestra.

## Cosa resta, per L47c2

- **Il firmware.** Via `LDR_*`, le tabelle del profilo, `timer_cal_*`, `T_FADE_US` e
  `T_MUTE_HOLD_US`; i relè subito dopo il tasto; `spec/timer_spec.md` §4–§5; il blocco 2k e i suoi
  falsi.
- **Un'incoerenza transitoria, dichiarata.** Fino a L47c2 il firmware scrive ancora sull'SPI verso
  un DAC che non c'è più (i pin restano liberi; sull'host non cambia niente).
- **L'alimentatore col carico nuovo**: la tenuta di `VRELAY` a rete −10 % (NC-050), il commento di
  `C_VRELAY` (NC-051), lo standby (NC-037).
- **V2.**
  - I generatori e i deck (`tb_v2_casopeggiore.cir`, `tb_v2_mute_ldr.cir`), che hanno ancora le
    celle, rigenerati senza.
  - La matrice con la guardia di L47b2b1: A e B senza segnale, i cambi di guadagno e trim,
    l'accensione, B a mute inserito (NC-053) e **il clic del taglio con musica**, cioè C, in picco
    e dB SPL.
  - La chiusura di NC-049.
- **La catena dei guasti di L41c** sull'alimentatore nuovo, e la regressione.
- **Per la rigenerazione del dossier** (fuori lotto): `build_dossier.py` cita `tb_e3_e5_ldr.cir`
  e descrive il mute graduale, e le righe `Stato:` delle ADR superate da ADR-062 non lo dicono.
