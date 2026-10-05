# L47c2a — Il mute coi soli relè: il firmware e l'alimentatore col carico nuovo (2026-10-05)

**Nessuna ADR nuova** (la sequenza è di ADR-062; i pin liberi sono una scelta d'implementazione,
scritta nella specifica). **NC-051 chiusa; NC-050 e NC-037 aggiornate, aperte.** Dati:
`data/2026-10-05/L47c2a/` (README).

## Perché

L47c1 (ADR-062) ha tolto dall'hardware le quattro fotoresistenze e il loro pilota. Restavano due
incoerenze dichiarate: il firmware scriveva ancora sull'SPI verso il DAC tolto, e i deck V2
avevano ancora le celle. Il prompt di L47c2 chiedeva il firmware, l'alimentatore col carico
nuovo, V2 senza celle e i guasti, con tre punti da portare prima all'utente.

## Le risposte dell'utente (2026-10-05), per nome

| Domanda | Risposta |
|---|---|
| Dividere il lotto | **«Due parti»**: L47c2a il firmware e l'alimentatore (questo); **L47c2b** la matrice V2 senza celle col clic del taglio dichiarato, i guasti di L41c, la regressione dei 21 deck, NC-049 e NC-053 |
| I pin del micro rimasti liberi (PA1, PA2, PA3, PA4, PB4) | **«Buffer d'ingresso disattivato»** (raccomandato), fra quattro: buffer disattivato, ingressi con pull-up, uscite basse, lasciarli come sono |
| La tenuta della linea a 12 V dei relè col carico nuovo (portata coi numeri misurati) | **«Tenere 4700 µF»** (raccomandato), contro 3300 µF |

**PC3**, libero di proposito da L41b1, ha avuto lo stesso trattamento dei cinque: la domanda
nominava i pin liberati da L47c1, e la ragione (un pin aperto col buffer acceso) vale uguale. Lo
dico qui perché non era nella domanda.

## Il firmware

- **Via** da `timer_core.{c,h}`: la legge delle LDR, la calibrazione, la sfumatura (d), i tempi
  che la servivano (`T_FADE_US`, `T_MUTE_HOLD_US`, `T_CAL_*`), le uscite del DAC e gli ingressi
  delle correnti delle stringhe.
- **Le sequenze** (spec § 4):
  - inserzione: `MUTE_REQ` giù **nello stesso istante** in cui il debounce conferma il tasto,
    `PERMIT_REQ` 20 ms dopo. Non più reversibile: lo stato d'inversione non c'è;
  - rilascio: le due richieste insieme, 10 ms del G6K, poi il verdetto dell'hardware. Se
    `MUTE_G_IN` è ancora basso, BUCO_RETE; altrimenti MUSICA;
  - accensione senza zeri né calibrazione; spegnimento in ~0,12 s da MUSICA (prima ~7 s).
    ADR-046 diceva «~7 s» per la sfumatura che non c'è più.
- **I pin liberi** (spec § 2). Il core non tocca registri: espone la lista `TIMER_PIN_LIBERI` e
  `TIMER_PIN_LIBERI_ISC` = `INPUT_DISABLE` (0x4, DS40002205A § 16.5.11, p. 145). Il test
  `pin_liberi` li tiene contro i pin di U509 senza rete in `psu.net` e contro la piedinatura
  SOIC-20 del datasheet (§ 4.1, p. 14). È la raccomandazione del datasheet (§ 16.3.1, p. 131): «For
  lowest power consumption, disable the digital input buffer of unused pins».
- **I test sull'host**: via `test_legge.c` e il test della calibrazione; `test_sequenze`
  riscritto sulle sequenze nuove, più il rifiuto del rilascio, il tasto che torna a musica dentro
  Δ, e i pin liberi. **76 controlli, 0 falliti.**
- **I falsi: 19 su 19.** Il conto:
  - **10 sopravvissuti di L41b2** col loro numero (1, 4, 5, 6, 7, 9, 10, 15, 16, 18), perché i
    report di prima si leggano ancora;
  - **11 usciti con la legge, la calibrazione o la sfumatura**: 2, 3, 8, 11, 12, 13, 14, 17, 19,
    20, 21;
  - **9 nuovi** (22–30): `MUTE_REQ` che aspetta 0,5 s, la ritenuta della sfumatura rimasta; il
    rifiuto dell'hardware non guardato; `PERMIT_REQ` 20 ms dopo `MUTE_REQ` al rilascio; PB4
    dimenticato; PC2 al posto di PC3; il buffer acceso; `VRELAY_EN` al primo campione buono; la
    rete 80 ms dopo `VRELAY_EN`; lo spegnimento senza Δ.

  Dei nove nuovi, otto sostituiscono un falso uscito; il conto scende da 21 a 19.
- **`ponte.c`** senza le colonne delle correnti, perché resti compilabile per i guasti di L47c2b.
- **Il contratto di J4** (`preamp_audio.py`): già scritto per il taglio da L47c1, coerente col
  firmware nuovo. Cambia solo il rimando: il lato dell'alimentatore è verificato qui, il jack in
  L47c2b. Un commento; la netlist audio non è rigenerata.

## Il firmware sul circuito

La catena di L41b2: il core al posto del micro nel banco dell'alimentatore, iterato fino al punto
fisso. Il generatore è quello di L42b, adattato al `psu.net` senza U510, U511, Q507–Q512 e senza
le LED di J3 (differenze nell'intestazione). I criteri che la sfumatura definiva sono riscritti
**prima** delle corse (`analizza_seq.py`).

**6 sequenze su 6**, tutte al punto fisso con 0 sostituzioni:
- rilascio: relè eccitati **21,1 ms** dopo il tasto;
- spegnimento: relè rilasciati **21,2 ms** dopo il pin del frontale, il relè di rete 63,4 ms dopo
  il permissivo;
- buchi di 20 e 200 ms: jack a 14,4 ms, classe 1 e classe 2;
- guasto: jack a 10,7 ms, rete aperta e tenuta;
- Δ a ogni rilascio ≥ 20,3 ms.

L'inversione non c'è più.

## L'alimentatore col carico nuovo

| | L47c2a | L42b (col pilota) | L41a |
|---|---|---|---|
| Tenuta di `VRELAY_REG` ≥ 11,4 V, rete −10 / nom / +10 % | **61,1** / 142,2 / 223,6 ms | 36,1 / 102,1 / 168,5 | 62,8 / 144,9 / 227,3 |
| Δ nominale / angolo minimo | 18,84 / **16,91** ms | uguali | uguali |
| Standby, dal secondario di T2 | **80,5 mW** | 92,5 | — |
| U503 spento: jack a | 15,65 ms | 13,29 | 15,8 |

- **La tenuta** è tornata quasi a L41a: il pilota delle LDR era il carico che L42b aveva trovato.
  Le varianti per la domanda (`varianti/`): 3300 µF 41,0 ms, 2200 µF 25,1 ms. **«Tenere 4700 µF»**:
  il commento di `C_VRELAY` è riscritto con queste cifre, e la netlist è uguale per connettività.
- **Il controfattuale** (il carico di L41a) dà 64,3 ms, **1,5 ms sopra L41a**: non «uguale» come in
  L42b. Il metodo d'integrazione non c'entra (gear e trapezoidale sul deck di oggi: 61,112 contro
  61,097 ms). **Ipotesi, non provata**: il banco carica i regolatori della loro corrente di riposo
  per parte da L41b1 (2 µA sul MCP1703), L41a dava 1 mA a ciascuno; in L42b i ~0,8 mA del DAC e
  degli amplificatori del pilota compensavano per caso. Il controfattuale ha richiesto il metodo
  gear: col trapezoidale `regime_m10` si fermava al fronte di `VRELAY_EN` (Timestep too small).
- **Lo standby**: −12 mW dal secondario di T2. Il criterio di NC-037 sulla perdita a vuoto di T2
  diventa **≤ 0,42 W**.

## Verifica

- `run_host_tests.sh --falsi`: 9 test su 9, 19 falsi su 19 (`falsi/esito.txt`).
- Il core sul circuito: 6 su 6 (`seq/analisi_seq.txt`).
- Il temporizzatore: nominale e angolo minimo PASSA (`timer/analisi_timer.txt`).
- `psu.net` rigenerata: 118 componenti, 61 reti, uguale per connettività; ERC 24 / 2 come prima.
- **`run_tests.sh`: 13 passed / 0 failed**, dal worktree (`validate_models.py` 59/59; il 2k coi
  19 falsi).

## Non fatto qui, per L47c2b

- La matrice V2 senza celle (i generatori e i deck, S fuori da `scripts/v2_metodo.py`, la guardia
  di L47b2b1): A, B senza segnale, il silenzio dei cambi, l'accensione, **B a mute inserito**
  (NC-053), **il clic del taglio** in picco e dB SPL a 1 m; NC-049.
- La catena dei guasti di L41c sull'alimentatore nuovo: il generatore di qui ha già i casi di L41c
  (`spegnimento_l` accorciato a TE + 1,1 s, da confermare), il ponte va adattato (le correnti delle
  LED).
- I 21 deck veloci (`L47c1/script/regressione.sh`).
- L'adattatore `main_attiny.c` (dove si scriverà `ISC`) resta da scrivere, come da L41b2.
