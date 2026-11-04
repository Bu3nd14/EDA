# ADR-120 — Il criterio del ritardo del permissivo è la regola fisica, a ogni distacco del jack

Data: 2026-11-04 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Precisa ADR-045, punto 2** (all'inserimento del mute prima `MUTE_CMD`, poi `PERMIT_CMD` dopo Δ, e Δ
  deve superare il rilascio massimo dei relè del jack, 3 ms): ne fa il criterio di verifica, e lo legge a
  **ogni** distacco del jack, non solo al primo evento della sequenza.
- **Supera, come criterio, la soglia di 16,9 ms** che i banchi del temporizzatore leggono da L41b
  (`analizza_mc.py`, colonna C3; la tabella dei dielettrici di ADR-105). Quella cifra era il Δ del vecchio
  temporizzatore al suo angolo minimo (ADR-049: «18,8 ms nominali e 16,9 ms all'angolo minimo»), diventata
  una soglia di controllo; non è un limite di una parte.
- Il circuito, P9, il PRB e la FMEA **non cambiano**. Chiude **NC-083** insieme a
  `reports/2026-11-04-L71-frontale-mosso.md`.

## Contesto

L71 ha simulato il frontale e il tasto del mute mossi durante una sequenza (NC-083): 230 corse del banco
del temporizzatore di oggi (`data/2026-11-04/L71/`), a rete −10 / 0 / +10 % e agli angoli peggiori delle
tolleranze di ADR-105 a 0 / 25 / 60 °C. Al jack tutto è sotto V2 e ogni stato finale è quello atteso. Esce
una cosa sola: se la musica arriva e se ne va in 3–4 ms (il frontale spento 6–7 ms prima che arrivi, o il
mute rimesso 6–7 ms dopo averlo tolto), il permissivo cade **10,0–16,9 ms** dopo il mute invece dei ~40 ms
delle sequenze a musica piena: sotto i 16,9 ms del controllo C3.

Il meccanismo, misurato (`script/delta_nodi.py`): Δ è la somma di due attese, AT_PRT (C550, caricato da
AT_MRQ attraverso un diodo) che scende fino a VREF e PERMIT_T (C528) che scende fino alla soglia di
PERMIT_G. All'accensione AT_MRQ sale lentamente e la musica arriva quando incrocia VREF: col frontale spento
lì, AT_PRT arriva appena sopra VREF (2,53 V; con la musica piena 4,24 V), la prima attesa vale quasi zero e
resta PERMIT_T, che con un impulso breve non si carica del tutto.

## Decisione

Il criterio del ritardo del permissivo è **la regola fisica di ADR-045**: a ogni distacco del jack dopo
una sua chiusura, il permissivo può rilasciare il guadagno **solo quando il contatto del jack è
sicuramente aperto**, con margine ≥ 0. Il conto si fa dal lato sfavorevole su entrambi i relè (G6K 12 V,
en-g6k.pdf p. 2–3): il jack aperto **al più tardi** (bobina sotto 1,2 V più 3 ms di rilascio massimo), il
guadagno libero **al più presto** (bobina di K6 sotto 9,6 V). I 16,9 ms restano la cifra delle sequenze a
musica piena, da riportare, non una soglia. Scelta dell'utente, 2026-11-04: **«Sì, regola fisica»**, dopo
la spiegazione di che cosa vuol dire «guadagno libero».

## Perché

- **È quello che il numero proteggeva.** Il permissivo esiste perché un cambio di guadagno porta all'uscita
  un gradino di ~6–114 mV (fino a ~90 dB SPL di picco a 1 m, ADR-045): conta solo che il gradino trovi i
  contatti del jack già aperti.
- **La regola regge con margine ovunque** (`stato_l71.csv`, colonna `r41_min_ms`): almeno **9,3 ms** a
  valori nominali (rete −10 %) e almeno **6,9 ms** all'angolo peggiore (0 °C, rete −10 %, il mute rimesso
  12,8 ms dopo averlo tolto). Il permissivo non è mai dopo il jack alla chiusura (`perm_dopo` 0 su 230) e il
  guadagno non è mai sbloccato con il jack chiuso (C2 dentro su 230).
- **Il fondo è robusto**: la musica più breve che chiude davvero il jack (bobina sopra 9,6 V) è 3,2–3,3 ms su
  ogni angolo; con impulsi più brevi il jack non si chiude e non c'è niente da proteggere. Le corse sono a
  0,05–0,2 ms l'una dall'altra attorno al bordo.
- **Al jack non si sente niente**: le stesse sequenze, nella catena V2, danno al più −55 dB SPL di picco a
  1 m senza segnale.

## Alternative scartate

- **Un rimedio nel circuito** (Δ indipendente dalla durata della musica, per esempio AT_PRT caricato da un
  nodo che non dipende dalla rampa dell'accensione): un lotto di progetto prima di G1, con sorgente, FMEA e
  sequenze rifatte, per un margine fisico che c'è già.
- **Tenerla aperta come non conformità minore**: avrebbe lasciato un criterio che misura un'altra cosa.

## Da riaprire se

- il margine fisico (`r41_min_ms`) scende sotto 0 in una corsa qualsiasi, sul circuito di oggi o su uno
  nuovo del temporizzatore;
- i relè del jack o K6 cambiano parte, o il rilascio massimo dei relè del jack supera 3 ms;
- cambiano C550, C528, R534 o il percorso da AT_MRQ ad AT_PRT.
