# ADR-075 — Il comando dei relè: un limite di corrente nel ramo dei clamp, e un limitatore sulla linea a 5 V della logica

Data: 2026-10-14 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- È la **scelta 4** di `data/2026-10-14/L45d1/scelte_L45d2.pdf` (8 righe alte, L45c2).
- La realizzazione è di **L45d2b**. Il micro bloccato e lo standby restano a L54.

## Contesto

Sono guasti che non danno colpi al jack ma portano parti oltre i loro limiti (gravità 5):
- **un diodo di bloccaggio in corto** (D505, D506, D508), o la bobina di K501 in corto: la linea dei
  relè va a massa attraverso un piccolo MOSFET (Q501, Q503: 2N7002, 115 mA continui), con U503 al
  suo limite di ~1 A per ~20 ms o finché il firmware non reagisce;
- **una resistenza in corto** del riferimento o del rivelatore di rete (R503, R510, R512): il
  riferimento o Q504 si distruggono;
- **U504 in corto fra ingresso e uscita**: i 12 V della linea dei relè arrivano sulla linea a 5 V,
  e l'ATtiny3216 (6 V di massimo assoluto) si guasta.

## Decisione

Parole dell'utente (2026-10-14): «Limitatore sui 5 V, Limitare la corrente del comando».

1. **Un limite di corrente sul comando**: una resistenza o un fusibile ripristinabile nel ramo dei
   clamp, o sulla linea dei relè, perché il corto di un clamp non faccia passare ~1 A in un 2N7002.
   In alternativa un MOSFET che regga il limite di U503. Lo sceglie L45d2b, con le righe delle
   resistenze in corto.
2. **Un limitatore sulla linea a 5 V della logica**: uno zener o un TVS con un fusibile
   ripristinabile, così che U504 in corto non porti 12 V al micro.

## Perché

- **Sono parti oltre i limiti, quindi gravità 5**, e la priorità è alta qualunque sia la rarità
  (ADR-070).
- **Costano poche parti piccole**, sulla scheda dell'alimentatore, e non toccano il percorso del
  segnale.

## Alternative scartate

- **Un sorvegliante della sovratensione sulla linea regolata dei relè**: sarebbe un comparatore in
  più, e il limitatore sui 5 V protegge il micro direttamente. L'utente non l'ha scelto.
- **Accettarli**: avrebbe lasciato il micro e i MOSFET del comando a distruggersi al primo corto.

## Da riaprire se

- Il limite di corrente rallenta il comando dei relè (lo stacco del jack, Δ) oltre quanto chiede
  P9 (b): si torna all'utente coi tempi misurati.
- Il riesame del micro (L54) cambia il micro con uno che regge 12 V sull'alimentazione.
