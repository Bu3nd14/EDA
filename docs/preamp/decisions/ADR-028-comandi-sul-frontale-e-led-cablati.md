# ADR-028 — Comandi sul frontale, e indicazioni a LED a pannello cablate a filo

Data: 2026-09-15 · Stato: accettata

## Contesto

I requisiti dicevano **quali** comandi esistono (F4, F5, F6, F8) e **quale**
indicazione (F9), non **dove** stanno né in che forma. Nel sorgente:
- il trim ha SW1, rotativo «a pannello», portato sulla scheda da un header
  (`circuits/preamp/trim.py`, `FP_SW`);
- il guadagno esiste solo come net `GAIN_CMD` / `GAIN10_CMD`, il mute solo come
  `MUTE_CMD`: nessun comando è istanziato;
- i LED del trim hanno footprint `LED_THT:LED_D3.0mm` **sulla scheda audio**.

È emerso nella sessione di domande del 2026-09-15
(`reports/2026-09-15-L34-decisioni-comandi-guadagno-telaio.md`).

## Decisione

Parole dell'utente, 2026-09-15: «il guadagno é rotativo a 3 posizioni sul
frontale», «il mute ha un comando sul pannello (switch)», «ne metterei uno rosso
per il mute», «i LED li colleghiamo con fili».

1. **Sul frontale**: selettore d'ingresso (rotativo, ADR-009), attenuatore a
   scatti (F4), **trim rotativo a 3 posizioni** (SW1, ADR-027), **guadagno
   rotativo a 3 posizioni**, **interruttore di mute**.
2. **LED a pannello**: i tre del trim (F9) e **uno rosso di mute**. I LED del
   guadagno li regola ADR-030.
3. **Tutti cablati a filo.** Sulla scheda audio restano gli header di cablaggio,
   non i LED.
4. **Il mute è inserito se l'interruttore lo chiede oppure se il temporizzatore
   d'accensione (ADR-012) non è scaduto.** L'interruttore non anticipa il
   rilascio all'accensione.
5. **Il LED di mute indica il mute inserito.** Da quale contatto lo legge lo
   sceglie L35. La preferenza è lo stato e non il comando, per la ragione di F9;
   ma i poli di K2–K4 portano tutti segnale, e i due NC di K6 sono in serie su
   `VTRIM`.

## Perché

- **Sul pannello non passa segnale.** ADR-009 usa i relè proprio per tenere
  l'audio lontano dal frontale: sui comandi passa solo la continua delle bobine,
  e sui LED la loro corrente. I comandi nuovi seguono la stessa regola.
- **Un rotativo a tre posizioni** ha le stesse tre posizioni di F5, e non ne
  ammette due insieme.
- **Un interruttore** tiene lo stato meccanicamente. Il mute è tenibile a tempo
  indefinito (ADR-021), e un pulsante con memoria vorrebbe logica (ADR-022).
- **Fili invece di una scheda di pannello**: scelta dell'utente. Il ritorno di
  bobine e LED sta già su `RLY_RET`, non sulla massa audio (`trim.py`, P4).

## Alternative scartate

- **LED sulla scheda audio**, com'è oggi in `trim.py`: dal frontale non si
  vedono.
- **Una scheda di pannello** per i LED: l'utente preferisce i fili.
- **Nessun LED di mute**: l'utente lo vuole rosso.

## Da riaprire se

- **Serve un altro elemento sul frontale** (accensione, sezione rete di P2,
  ventilazione) e i 450 mm di ADR-029 non bastano.
- **L35 non trova un contatto** da cui leggere il mute senza aggiungere un relè.
- **Il cablaggio dei LED** porta disturbo misurabile nella scheda audio, sul
  prototipo.
