# Registro delle non conformità — preamplificatore

**Documento vivo**: sempre vero al presente. Le voci si aprono e si
chiudono qui; il *perché* di ognuna sta nel report di gate datato che
l'ha aperta, in `reports/`, che non si riscrive mai.

Ultimo aggiornamento: **2026-09-09** (creato in L3c; **nessuna voce
aperta**, perché nessun gate è ancora stato eseguito)

---

## A cosa serve

Deciso il 2026-09-09: **il gate non è attaccato alla PR, è attaccato ai
risultati dei test.** Un diff è l'artefatto sbagliato su cui giudicare un
progetto analogico — le righe modificate di `gain_block.py` non dicono
niente sul margine di fase, e nel momento in cui una PR è aperta le
misure che risponderebbero alla domanda del gate non esistono ancora.

Quindi `design-reviewer` gira **offline, dopo il merge**, su `main`, sul
dossier e sui dati, e produce **non conformità** invece di un veto. Il
lavoro non si ferma ad aspettare un gate: il gate lo genera.

## Severità, e cosa blocca davvero

| Severità | Significato | Effetto |
|---|---|---|
| **bloccante** | un requisito non è soddisfatto, oppure manca l'evidenza per dire se lo è | la fase successiva non si apre: niente layout, niente fabbricazione |
| **maggiore** | scostamento reale, con margine residuo o rimedio noto | va chiusa prima del gate successivo |
| **minore** | osservazione da registrare, nessun rimedio richiesto ora | resta aperta e visibile |

**Il BLOCK non è sparito, si è spostato.** Prima era un veto su un merge;
ora è una non conformità bloccante che impedisce l'**avanzamento di
fase**. È ciò che quella regola voleva dire fin dall'inizio. In
particolare: **su un progetto collegato alla rete elettrica l'assenza di
un'analisi di sicurezza è una non conformità bloccante automatica a G3**,
e questa riga non si annacqua per omissione.

## Formato di una voce

```
### NC-<numero> — <titolo>

| | |
|---|---|
| Requisito | E4 / V2 / ADR-008 — quello che la voce viola |
| Severità | bloccante / maggiore / minore |
| Aperta da | reports/<data>-gate-G<n>.md |
| Stato | aperta / chiusa il <data> da <cosa l'ha chiusa> |

**Evidenza.** Il file di dati e la misura, non un'impressione.
**Cosa serve per chiuderla.** Concreto e verificabile.
```

Ogni voce nomina il **file di dati** che la sostiene, sotto
`docs/preamp/data/<YYYY-MM-DD>/`. Una non conformità senza evidenza
apribile non è una non conformità, è un'opinione.

---

## Voci aperte

*Nessuna. Nessun gate è ancora stato eseguito — G1 arriva dopo il giro
componenti (vedi il piano in `STATE.md`).*

## Voci chiuse

*Nessuna.*
