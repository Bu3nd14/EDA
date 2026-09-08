# ADR-007 — Condensatore d'uscita invece di servo di continua

Data: 2026-09-08 · Stato: accettata

## Contesto

Lo stadio discreto ha un offset residuo in continua. Serve qualcosa che
impedisca a quella continua di raggiungere il finale e gli
amplificatori per cuffia.

L'ipotesi iniziale era un **servo di continua**, per tenere il percorso
del segnale senza condensatori. L'utente ha fatto notare che il cj
Evolution 250 ha 100 kΩ d'ingresso, e che quindi il condensatore
sarebbe piccolo.

## Decisione

**Accoppiamento capacitivo in uscita, in polipropilene. Nessun servo di
continua**, da nessuna parte nel progetto.

Valori: **4,7 µF** sull'uscita principale, **2,2 µF** sulle uscite fisse.

## Perché

**I conti danno ragione all'utente.**

| C | f_c su 100 kΩ (cj) | f_c su 10 kΩ (finale futuro) | Ampiezza a 20 Hz |
|---|---|---|---|
| 1 µF | 1,6 Hz | 16 Hz | −0,03 dB / −3,1 dB |
| 2,2 µF | 0,72 Hz | 7,2 Hz | −0,01 dB / −0,55 dB |
| 4,7 µF | 0,34 Hz | 3,4 Hz | ~0 dB / −0,12 dB |

Sul carico reale, anche 1 µF darebbe 1,6 Hz: a 20 Hz sono 0,03 dB di
attenuazione e 4,5° di rotazione di fase. Non è un compromesso, è un
non-evento.

**Ma la ragione decisiva è un'altra: il servo è il posto da cui
l'operazionale rientra dalla finestra.** Un servo è un integratore ad
alto guadagno e basso offset — cioè, per definizione, un operazionale.
Farlo a discreti significa uno stadio in più con un proprio offset, un
proprio rumore a bassa frequenza e una propria deriva: il problema si
morde la coda. Il vincolo di ADR-003 sarebbe stato violato da due
operazionali nascosti nei servo.

**Effetto a cascata**, che è il vero valore di questa decisione:

1. Condensatore in uscita → la continua non arriva a valle
2. → il motivo principale per appaiare la coppia d'ingresso cade (ADR-005)
3. → il rischio di approvvigionamento sui JFET si sgonfia
4. → niente servo: niente operazionale mascherato, niente stadio in più,
   niente rumore a bassa frequenza iniettato

**Il dimensionamento è per il finale futuro, non per quello attuale.** È
la stessa logica del guadagno commutabile (ADR-004) applicata a un altro
componente: se si prevede il +10 dB perché la catena può cambiare, allora
il condensatore va scelto per un carico più ostile dei 100 kΩ del cj.
Sulle uscite fisse invece 2,2 µF bastano, perché **quelle destinazioni
non cambieranno** (Stax ~50 kΩ → 1,4 Hz).

## Alternative scartate

- **Servo di continua discreto**: stadio in più con proprio offset,
  rumore LF e deriva; e viola in sostanza il vincolo "niente
  operazionali".
- **Accoppiamento diretto senza servo**: nessuna protezione del finale
  dalla continua.

## Da riaprire se

Il finale cambia con impedenza d'ingresso sotto i 10 kΩ, o se si vuole
risposta piatta sotto 1 Hz. Va riaperta anche se cambiano gli
amplificatori per cuffia (i 2,2 µF sono dimensionati sui carichi
attuali).

## Aperto

L'impedenza d'ingresso del **Singxer SA-1 V2 non è verificata** — in
rete si trovano solo le impedenze d'uscita (22,5 Ω sbilanciata / 45 Ω
bilanciata). Se risultasse ~10 kΩ, i 2,2 µF danno 7,2 Hz e vanno portati
a 4,7 µF. Verifica assegnata alla Fase 1.

---

## Aggiornamento 2026-09-08 — 4,7 µF anche sulle uscite fisse

Il testo sopra non è stato modificato.

La Fase 1 ha stabilito che l'impedenza d'ingresso del Singxer SA-1 V2
**non è pubblicata** — verificato leggendo il manuale ufficiale. Non è un
limite della ricerca: il dato non esiste in forma pubblica. La frequenza
di taglio su quell'uscita è quindi **inconoscibile**, e i 2,2 µF
sarebbero una scommessa.

**Adottati 4,7 µF su tutte e tre le uscite.** Sullo Stax i 2,2 µF
sarebbero bastati (50 kΩ → 1,4 Hz), ma un valore unico su tutte le
uscite toglie una riga di distinta e un errore di montaggio: montare il
condensatore sbagliato nella posizione sbagliata sarebbe **silenzioso**.

Il prezzo è area di circuito stampato, che il telaio unico di ADR-010
può assorbire.

Questo **chiude** la domanda aperta sull'impedenza del Singxer: non
serve più conoscerla.
