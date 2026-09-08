# ADR-008 — Buffer d'ingresso unico con resistenze di isolamento

Data: 2026-09-08 · Stato: accettata

## Contesto

Servono due uscite a livello fisso per gli amplificatori per cuffia
(Singxer SA-1 V2 e Stax SRM-T1). Entrambi hanno **il proprio controllo
di volume**, quindi vogliono il segnale a livello pieno: attenuarlo
prima significherebbe due volumi in serie, con il secondo sempre in
fondo alla corsa — esattamente il difetto che il progetto elimina.

La proposta iniziale era un **buffer dedicato per ciascuna** delle due
uscite.

## Decisione

**Un solo buffer d'ingresso**, che alimenta entrambe le uscite fisse
attraverso resistenze di isolamento da ~100 Ω, e in parallelo
l'attenuatore del ramo principale.

## Perché

- I carichi sono leggeri: Stax ~50 kΩ, Singxer di valore analogo. In
  parallelo restano ~25 kΩ, che sommati ai 10 kΩ dell'attenuatore fanno
  ~7 kΩ. A 2,7 V di picco sono 0,39 mA — contro una polarizzazione
  Classe A di ~15 mA. Il buffer non se ne accorge.
- Le resistenze in serie danno **quasi tutto l'isolamento reciproco** a
  costo zero: collegare o scollegare un apparecchio non tocca l'altro.
- Il costo di un blocco discreto in più non è il calore (~0,55 W) ma la
  **coppia di JFET** e la complessità.
- Con quattro telai interconnessi c'è un rischio concreto di **anelli di
  massa**: uscite separate con la propria resistenza di isolamento danno
  un punto in più dove intervenire se si presentano.

**Conseguenza architetturale importante**: il buffer d'ingresso è
obbligatorio per via delle uscite fisse — e una volta che esiste,
l'attenuatore non è più caricato dal cathode follower a ECC82 del phono.
Si può quindi scegliere l'attenuatore per le prestazioni (10 kΩ) invece
che per proteggere la valvola. **L'esigenza pratica dell'utente ha
risolto un vincolo elettrico.**

## Alternative scartate

- **Un buffer dedicato per ciascuna uscita fissa** (proposta iniziale):
  due blocchi discreti in più per canale, quindi due coppie di JFET in
  più, per un isolamento che le resistenze in serie danno quasi tutto.
- **Uscite fisse prelevate passivamente** dal selettore: caricherebbero
  il phono e si influenzerebbero a vicenda.

## Da riaprire se

Si aggiungono altre destinazioni a livello fisso, o una di esse risulta
avere impedenza d'ingresso bassa (< 5 kΩ).

---

## Aggiornamento 2026-09-08 — il valore scende a 47 Ω

Il testo sopra non è stato modificato. La Fase 2 ha rilevato che
**~100 Ω di resistenza di isolamento pone le uscite fisse *a* 100 Ω**,
cioè al limite di E4 e non sotto.

`analog-topology-designer` ha implementato ADR-008 come scritta e ha
sollevato il conflitto invece di correggerlo di propria iniziativa —
comportamento corretto.

**Valore adottato: 47 Ω.** Soddisfa E4 con margine e conserva
l'isolamento reciproco fra Singxer e Stax, che era lo scopo della
resistenza. Nessun'altra conseguenza.
