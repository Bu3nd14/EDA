# ADR-051 — Il corto della linea a 12 V dei relè è un guasto singolo accettato sotto il tetto

Data: 2026-09-26 · Stato: accettata — col blocco di ADR-056 il corto vale 29,7 mV, non 69,4 (L46b)

## Contesto

ADR-046 vuole che, alla caduta di `VRELAY`, il guadagno non cambi prima dello stacco dei jack
(ADR-045). Lo garantisce la tenuta C523 dopo U503: se U503 si **apre**, il sorvegliante rilascia
i jack mentre C523 tiene K6, K1/K5 e K11/K12 per Δ. L41c lo ha verificato sul circuito vero:
75 nV al jack (`data/2026-09-26/L41c/tabella.csv`, `guasto_u503`).

Resta aperta una domanda, portata da L41a e rimandata a L41c: il **corto** della stessa linea.
Sul nodo `VRELAY_REG` stanno insieme:
- l'uscita di U503;
- la tenuta C523 e il ceramico C524;
- l'ingresso di U504, che alimenta il temporizzatore;
- attraverso Q505, `VRELAY` fino a J1 e alle bobine della scheda audio.

Un corto su uno qualsiasi di questi punti scarica anche la tenuta. Tutte le bobine cadono
insieme, e il guadagno si muove col jack ancora collegato: è il caso «senza Δ» di L30.

**Misurato in L41c**, con l'alimentatore vero e il firmware al punto fisso (`corto_u503`): il
guadagno cade al più presto 0,1 ms dopo il corto, il jack si apre al più tardi 3,1 ms dopo.
- Al jack principale: **69,4 mV di picco**, **~90 dB SPL di picco a 1 m**.
- Rispetto al tetto di non-danno di ADR-046 (0,87 V, ~112 dB): 22 dB sotto.
- Rispetto all'obiettivo (2 mV, ~60 dB): 30 dB sopra.

## Decisione

Parole dell'utente, il 2026-09-26: «accetto la 1, scrivi l'ADR e chiudi NC-036».

1. **Un corto sulla linea a 12 V dei relè è un guasto singolo, e per questo guasto vale il solo
   tetto di non-danno di ADR-046** (≤ 0,87 V di picco al jack principale), non l'obiettivo di
   2 mV. La classe comprende:
   - l'uscita di U503 a massa;
   - C523 o C524 in corto;
   - l'ingresso di U504 in corto;
   - `VRELAY` in corto a valle di Q505, nel cablaggio verso J1 o sulla scheda audio.
2. **Nessuna modifica all'hardware.** `psu.py` e la scheda audio restano come sono.
3. **L'argomento è quello di ADR-046 punto 4** per il corto istantaneo di un rail. Il finale
   (MV50, 612 mV per la piena potenza) vede ~0,2 W di picco, contro i 30 W che il tetto
   ammette e i 100–105 W continui delle Heresy. È un click forte, non un danno.

## Perché

- **La cifra è lontana dal tetto**: 22 dB, e il caso è singolo e raro (un componente in corto,
  o un cablaggio danneggiato).
- **Proteggerlo lo sposta, non lo toglie.** L'alternativa portata all'utente era una tenuta
  propria per le bobine di K6 e K1/K5, dietro un diodo e separata da `VRELAY_REG`. Avrebbe
  coperto il corto di U503, C523/C524 e U504, ma non un corto sulla linea stessa di quelle
  bobine. Chiedeva un pin in più su J1, quindi toccava la scheda audio, e avrebbe richiesto un
  lotto per rifare il 2j, il 2e e il banco di L41c.
- **È coerente con le decisioni precedenti dell'utente sul guasto**: «in caso di guasto una
  soglia di non-danno basta» (ADR-046). E «le soglie vanno bene come tetto, non come target»
  resta vero per tutti gli altri guasti: su perdita di rete e guasto di un regolatore, L41c
  misura ≤ 1,37 mV (~56 dB).

## Alternative scartate

- **Una tenuta separata per le bobine di K6, K1/K5 e K11/K12 dietro un diodo** (lotto L41d): vedi
  sopra.
- **Un elemento più veloce del relè in serie al segnale**: già scartato da ADR-046.

## Da riaprire se

- Il finale o i diffusori cambiano: il tetto di 0,87 V è il loro, come in ADR-046.
- La corrente a riposo dei blocchi o la loro risposta al cambio di guadagno cambia molto: 69 mV
  è il salto del blocco a +10 dB → 0 dB a jack collegato (L30, L41c).
- Un'esperienza sul prototipo mostra che la linea a 12 V va in corto più spesso di quanto si
  pensi. Per esempio un cablaggio fra le schede che si danneggia.

Precisa **ADR-046** (la classe di guasti a cui vale il solo tetto) e chiude la domanda lasciata
aperta in NC-036 da L41a. Evidenza: `reports/2026-09-26-L41c-banco-l30-circuito-vero.md`.
