# ADR-030 — Il cambio di guadagno interbloccato dal mute: monostabili con autoritenuta, solo se la misura lo giustifica

Data: 2026-09-15 · Stato: accettata

## Contesto

F6 e ADR-012 mettono il mute sulla commutazione del guadagno, ma **come regola
d'uso**: nessun interblocco elettrico lo impone, a differenza del trim (F8,
ADR-027). Commutare a caldo è sicuro, perché l'anello non si apre mai (ADR-004,
V2 verificata in L27). Ma senza servo (ADR-007) l'offset del blocco B è
moltiplicato dal guadagno: l'uscita principale salta di (G₂ − G₁)·Vos_in, e il
4,7 µF porta il salto al jack. L'utente, 2026-09-15: «vorrei evitare bump sulle
casse».

## Decisione

1. **Se il guadagno si interblocca, lo si fa con la strada B.** Parole
   dell'utente: «mettiamo il cambio guadagno condizionato al mute, prendiamo la
   strada B». K1 e K5 restano **monostabili**, e ciascuno ha un **relè
   ausiliario** con la bobina in parallelo:
   - a mute inserito le bobine seguono la manopola;
   - fuori mute si tengono attraverso un contatto dell'ausiliario, e la
     manopola non muove nulla.
2. **Tre LED dello stato vero del guadagno** (0 / +3 / +10 dB), letti dai poli
   liberi degli ausiliari, a pannello e cablati (ADR-028). Parole dell'utente:
   «ovviamente servono i LED anche per il guadagno ora», «anche i led guadagno
   sono a pannello».
3. **Si realizza solo se una misura lo giustifica.** Parole dell'utente: «si
   serve una misura perchè altrimenti rischiamo di aggiungere relè e LED senza
   motivo, introducendo un bump per togliere un bump». La misura la fa **L29**:
   per la variante di mute che L29 sceglie, il gradino al jack del **cambio
   sotto mute seguito dal rilascio** deve risultare minore di quello del
   **cambio a caldo**, nell'uso reale. Altrimenti niente interblocco, e la
   regola d'uso si scrive sul pannello o nella documentazione d'uso.
4. **Il trim resta com'è**, a bistabili (ADR-027). Parole dell'utente: «seguo il
   tuo consiglio».

## Perché

**Il bump a caldo è calcolato, non misurato.** Vos_in viene da NC-028: −14,2 mV
coi modelli MJE/MMBT del costruttore, −16,6 mV coi segnaposto, −33 mV coi
segnaposto a sorgente 1,5 Ω, più fino a ±20 mV di dispersione LSK489. Stima SPL
con la formula di NC-028 (finale ×21,1, Heresy 96 dB), un limite superiore:

| Passaggio | G₂ − G₁ | Gradino al jack | ≈ dB SPL di picco a 1 m |
|---|---|---|---|
| 0 ↔ +3 dB | 0,420 | ~6 mV, fino a ~14 | ~69–76 |
| +3 ↔ +10 dB | 1,732 | ~25 mV, fino a ~59 | ~81–89 |
| 0 ↔ +10 dB | 2,152 | ~31 mV, fino a ~74 (2,5 kΩ) / ~114 (1,5 Ω) | ~83–95 |

Decade con τ = 4,7 µF × (220 kΩ ∥ 100 kΩ) ≈ 0,32 s. Riguarda solo l'uscita
principale: le fisse restano sempre a guadagno 1.

**Perché prima la misura.** Il rilascio del mute con musica porta al jack
**5,37 V** a +10 dB e 1,79 V a 0 dB (simulazioni scratch, NC-028); senza musica,
picovolt. Il gate vince solo rilasciando a musica ferma o a volume basso. E con
il contatto prima del condensatore, una delle strade di L29, il cambio sotto
mute rimette al rilascio proprio un gradino d'offset.

**Perché B e non i bistabili.** La strada A (K1/K5 bistabili col ponte H del
trim) usa il permissivo K6 e non aggiunge relè per il gate. Ma una bobina
interrotta lascia il guadagno dov'era, anche a +10 dB: contro F5, «nessun
guasto di bobina … può portare a un guadagno più alto». Con B una bobina guasta
torna a 0 dB. La caduta di `VRELAY` non distingue le due strade: diseccita
K2–K4 e inserisce il mute in entrambi i casi. Entrambe costano due relè (A due
spia per i LED, B due ausiliari).

**Perché non anche il trim.** B sul trim è possibile a parità di relè, col
commutatore a 2 poli e senza il rischio termico dei bistabili pilotati a lungo in
mute (ADR-027). Ma consuma fuori mute (circa 42 mA a 5 V), estende al trim la
corsa al rilascio, va cablato «diseccitato = −12 dB» e rifà L16. È quasi un
pareggio: si tiene il lavoro verificato.

**Cosa costa B, calcolato.** Bobine fuori mute a +10 dB: 8 × 21,1 mA ≈
**169 mA** a 5 V, contro 126,6 mA oggi. Il rischio da provare è la **corsa al
rilascio**: quando K6 commuta, per un istante né il comando né la tenuta
alimentano le bobine. Il circuito lo progetta L36.

## Alternative scartate

- **A — K1/K5 bistabili**: contro F5 sul guasto di bobina.
- **Regola d'uso senza interblocco**: resta la via se la misura non giustifica
  B (decisione 3).
- **Mute automatico al movimento della manopola**: vuole temporizzazione,
  scartato per il trim in ADR-019 per la stessa ragione.
- **Interblocco senza LED**: fuori mute la manopola può non dire il guadagno
  vero, come per il trim (F9).

## Da riaprire se

- **L29 mostra** che il cambio sotto mute non riduce il gradino rispetto al
  cambio a caldo: l'interblocco non si fa.
- **La corsa al rilascio** non si chiude senza componenti che accumulano carica,
  o senza un permissivo in più.
- **La bobina di K6 si interrompe**: trim e guadagno diventerebbero comandabili
  a caldo (già in ADR-027); con B il guadagno torna al comportamento di oggi.
- **Il budget delle bobine** supera quanto l'alimentazione di `VRELAY` fornisce
  (L30 e lotto dell'alimentatore).
- **La corsa è chiusa sul guadagno**: allora B va rivalutata anche per il trim,
  per avere un solo meccanismo.

Precisa **ADR-012** e **ADR-019**: il mute diventa permissivo anche del
guadagno. **Estende ADR-026** senza superarla: F5 resta com'è.
