# Prompt per la sessione successiva — L45d2b2c, i massimi del blocco

Nome della sessione: **hi-fi preamp L45d2b2c** (la convenzione è in `CLAUDE.md`).

> Prompt messo da parte alla chiusura di L45d2b2a (2026-10-20), dal punto 3 del prompt di L45d2b2.
> Va in `docs/preamp/NEXT-SESSION.md` alla chiusura di L45d2b2b, aggiornato con quello che L45d2b2b
> avrà cambiato (vincoli e «Prima di tutto» come nel prompt di L45d2b2b).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b2c**, e si ferma. Se si rivela più grande di una sessione,
**dividilo con l'utente all'inizio**.

## Perché questo lotto

**NC-042** (maggiore, prima di G1). È la terza parte di L45d2b2 («Tre parti», 2026-10-20). Dopo
vengono L45d2b3, i guasti rifatti e la sintesi.

## Che cosa costruire

1. **Le tensioni massime delle parti del blocco** col rail fino a ±20,3 V, e la dissipazione dei
   finali (ADR-078; la scelta di `data/2026-10-14/L45d1/scelte_L45d2.pdf`).
   - Si lavora sul blocco coi quattro diodi di ADR-090. Ai loro capi c'è lo spread: ~2 V a riposo, e
     ~3 V coi guasti del moltiplicatore, quando portano la corrente del VAS (~10 mA).
   - Il sorvegliante della sovratensione si aggiunge **solo se** qualcosa esce dai limiti, e in quel
     caso **si torna all'utente**.
   - R550 / R551 (ADR-092) abbassano il grezzo di ~1,4 V a regime. ±20,3 V è il rail col regolatore
     in corto fra ingresso e uscita, quindi va riletto col percorso di oggi: il grezzo passa dalla
     resistenza.
2. Ogni opzione portata all'utente arriva già con la sua cifra contro il limite della parte.

## Prima di tutto

- `STATE.md` (le voci di L45d2b2a e L45d2b2b), `NONCOMPLIANCE.md` (NC-042, NC-072).
- ADR-078, ADR-090, ADR-092; `docs/limitations.md` #59, #62, #63, #65, #66.
- Il banco del blocco di L62b (`data/2026-10-19/L62b/`) e i deck di guasto rifatti dal blocco di
  oggi (limitations #62).

## NON fa parte di questo lotto

I guasti rifatti nella forma di ADR-070 e la sintesi (L45d2b3); il rame dei regolatori (G2); L54,
L55, L57, L58.
