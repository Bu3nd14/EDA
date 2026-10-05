# `firmware/preamp_timer/` — il firmware del temporizzatore dell'alimentatore

Il micro è U509 (ATtiny3216) in `circuits/preamp/psu.py`. Decisioni: **ADR-048** punto 6
(il temporizzatore ibrido), **ADR-049** (il micro, dove vive il firmware e come si prova) e
**ADR-062** (il mute taglia: dal lotto L47c2a il firmware non ha più la legge delle LDR, la
calibrazione, la sfumatura né la SPI verso il DAC, che sono usciti dal circuito).

Il firmware **non** è topologia, quindi non sta in `circuits/`. **In SPICE non si simula**: si
prova sull'host, e le sue uscite diventano le sorgenti del banco.

| Percorso | Cosa | Lotto |
|---|---|---|
| `spec/timer_spec.md` | **il contratto**: ingressi, uscite, pin liberi, stati, sequenze, tempi con la loro ADR | L41b1, L47c2a |
| `src/timer_core.c` | la logica pura: `tick(ingressi, dt) → uscite`, nessun registro | L41b2, L47c2a |
| `src/main_attiny.c` | l'adattatore verso i registri dell'ATtiny: **non ancora scritto** | — |
| `test/` | i test sull'host (`clang`), uno per sequenza e uno per i pin liberi, ciascuno fatto fallire su un falso (19) | L41b2, L47c2a |

La **sicurezza non dipende dal firmware**: con il micro in reset, a zero, bloccato alto o coi pin
in alta impedenza l'ordine jack → permissivo → `VRELAY` lo tiene l'hardware. È verificato in
L41b1 e asserito dal 2e (`check_relay_safe_state.py --timer`).

**La programmazione** (quando esisterà una scheda): UPDI su J515 (UPDI, V5, RET), con un
adattatore USB-seriale più una resistenza, e `avrdude` o `pymcuprog`. `avr-gcc` oggi non è
installato: si installa quando serve, non prima.
