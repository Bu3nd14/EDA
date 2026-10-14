# ADR-078 — Le voci a bassa priorità dei guasti: prima i massimi per le sovratensioni dei rail, lo standby acceso alla diagnosi, il tetto delle fisse alla sua non conformità

Data: 2026-10-14 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- Riguarda tre voci della lista di L45d2 che il PDF delle scelte lascia fuori dalle dieci scelte
  (`data/2026-10-14/L45d1/scelte_L45d2.pdf`, nota sotto la tabella). Sono a priorità bassa, ma il
  prompt del lotto chiedeva di decidere anche loro.
- Le sovratensioni vanno a **L45d2b**, lo standby a **L58**, il tetto delle fisse resta a
  **NC-046**.

## Contesto

1. **Le sovratensioni dei rail che nessuno vede** (9 righe, L45c1). Il sorvegliante vede solo il
   rail che scende; un guasto del regolatore può portare i rail fino a ±20,3 V. A questo si
   aggiunge la presa centrale del trasformatore aperta. Le tensioni massime delle parti del blocco
   non sono mai state lette, quindi non si sa se ±20,3 V siano un problema.
2. **Lo standby con la linea dei relè o il toroidale rimasti accesi per un guasto** (8 righe,
   L45c2): è consumo, non un colpo.
3. **Il tetto di non-danno sulle uscite fisse delle cuffie** (NC-046): nella sintesi non ha righe
   proprie.

## Decisione

Parole dell'utente (2026-10-14): «Prima leggere i massimi»; «Standby alla diagnosi».

1. **In L45d2b si leggono le tensioni massime delle parti del blocco**, e la dissipazione dei finali
   col rail alto. Il sorvegliante della sovratensione si aggiunge **solo se** qualcosa esce dai
   limiti, e in quel caso si torna all'utente.
2. **Lo standby acceso per guasto va a L58**: il firmware legge in standby la linea dei relè e il
   toroidale.
3. **Il tetto delle fisse resta nella sua non conformità** (NC-046), fuori da questo lotto.

## Perché

- **Un sorvegliante si aggiunge contro un limite noto, non contro un'ipotesi.** Leggere i massimi
  dai datasheet costa poco, e dice se il guasto è a gravità 5 o 1.
- **Lo standby acceso è una funzione persa**, gravità 2. Vederlo è un compito della diagnosi.

## Alternative scartate

- **Il sorvegliante della sovratensione subito**: un comparatore in più forse senza bisogno.
- **Lo standby acceso accettato senza diagnosi**: avrebbe lasciato il toroidale acceso senza
  nessun segno, per anni.

## Da riaprire se

- Una parte del blocco ha un massimo assoluto sotto ±20,3 V, o i finali col rail alto escono da
  PR-22 / P7: si sceglie il rimedio con l'utente in L45d2b.
- NC-046 fissa un tetto sulle fisse che il rivelatore di ADR-072 deve guardare.
