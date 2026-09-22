# ADR-040 — V2: il taglio con musica si giudica sul salto di livello, ≤ 20 dB in 100 ms; C2 diventa diagnostica, e il profilo del mute a LDR è la v4

Data: 2026-09-22 · Stato: accettata

## Contesto

ADR-035 aveva dato a C, il taglio della musica, una soglia di **1 mV**, misurata come
differenza dei residui del fit su una finestra di 10 ms. ADR-038 aveva tenuto quella
soglia invece di allentarla. L29b2 ha reso misurabile il mute a LDR (il pavimento era
un arrotondamento di `wrdata`, `docs/limitations.md` #30) e ha trovato tre cose.
1. **A 20 Hz C non si soddisfa con nessuna dissolvenza ragionevole.** La finestra di
   10 ms copre un quinto di periodo, e C2 misura la pendenza dell'inviluppo. Una
   dissolvenza a coseno **ideale** sulla principale (calcolo sul metodo,
   `data/2026-09-22/L29b2/transizione/`):
   - a 20 Hz vale 2,26 mV in 6 s e 1,36 mV in 10 s: sotto 1 mV serve oltre ~14 s;
   - a 1 kHz vale 0,25 mV in 6 s.
2. **Sulla principale la distorsione della catena da sola vale 0,65–0,96 mV di C2.**
   Il contenuto armonico cambia col livello, e il riferimento non lo cancella. È la
   distorsione dei modelli segnaposto (NC-017).
3. **Il comando dei LED non può produrre un inviluppo a coseno in 6 s.** Sopra ~80 kΩ
   la cella si spegne al massimo a 0,4 decadi/s, secondo l'ipotesi pessimistica del
   modello. Una ricerca su profili a 21 nodi con accelerazione limitata è rimasta a
   6,7 volte il coseno ideale.

L'utente ha dato un **dato d'uso**. Il Technics che il preamp sostituisce ha un
pseudo-mute che cala di **20 dB di colpo**, con la musica attiva, e parole
dell'utente: «non mi ha mai dato fastidio all'inserzione con la musica attiva,
quindi 20 dB di salto li considero accettabili». Un gradino così, a livello pieno,
varrebbe C ≈ 10 V: diecimila volte la soglia di ADR-035.

## Decisione

Scelta dell'utente il 2026-09-22, «Criterio in dB + v4» fra tre strade:

**1. V2 ha una grandezza nuova, S — il salto di livello**, ed è il verdetto del
taglio con musica:
- il **livello** del tono al jack è l'ampiezza del fit seno + coseno a frequenza
  nota. La finestra è di max(10 ms, un periodo), quindi a 20 Hz 50 ms. Si esprime in
  dB sotto il livello pieno della corsa di riferimento del rilascio, al 95°
  percentile;
- sotto **−70 dB** il livello si tiene a −70 dB: lì la musica non conta, e la scala
  in dB esplode;
- **S** è la variazione massima del livello in **100 ms**, nella stessa finestra di
  C (da t_evento − 20 ms a t_evento + t_grad + 0,2 s);
- **soglia: S ≤ 20 dB**, a ogni uscita, a 10 e 100 kΩ, a 20 Hz, 1 kHz e 20 kHz.

**Di chi è cosa**: i 20 dB sono dell'utente. I 100 ms e i −70 dB sono una proposta
di L29b2, dichiarata qui e riapribile. Il gradino del Technics è istantaneo, quindi
sta dentro «20 dB in 100 ms» comunque si scelga la finestra.

**2. C2 diventa diagnostica**, come C1: si calcola, si riporta col suo pavimento,
non decide. Un taglio netto a livello pieno resta respinto da S: 0 → −70 dB in un
istante fa 70 dB.

**3. A e B restano come sono** (ADR-032, ADR-036): 100 µV, A senza segnale.

**4. Il profilo del comando dei LED è la v4**, al posto della v3 di L29b. ADR-039, dello
stesso lotto, porta il contratto già scritto così:
- serie: 20 mA a d = 0, 0,2 mA a 0,1, 4,5 µA a 0,45, **0,19 µA a 0,75**, 10 nA a 0,8
  e oltre;
- derivazione: 10 nA fino a d = 0,5, poi log-lineare fino a 20 mA a d = 1;
- 10 nA di riposo, Td = 6 s, relè 0,5 s dopo d = 1: come ADR-039.

## Perché

- **La soglia viene dall'ascolto dell'utente**, non da un calcolo. Il gradino del
  Technics è un'esperienza d'uso ripetuta, sullo stesso impianto.
- **Un criterio in dB segue l'orecchio**, che sente in logaritmo. C2 lavora in
  ampiezza lineare e pesa i cambi ad alto livello: a 20 Hz misura la pendenza, non
  un difetto udibile. Una dissolvenza lenta di un 20 Hz è un tono pulito.
- **La v4 sta largamente dentro.** Dagli stati ngspice (1 kHz, 100 kΩ), come salto
  in 100 ms sopra −70 dB:

  | | Inserzione | Rilascio | Inversione |
  |---|---|---|---|
  | v3 | 7 dB | **30 dB** (−56 → −26) | 7 dB |
  | v4 | 7 dB | 4 dB | 3 dB |

  La v3 sfora al rilascio. La misura sul deck versionato, col metodo di questa ADR, è
  nel report di L29b2.

## Alternative scartate

- **Tenere C ≤ 1 mV** (ADR-035, ADR-038). A 20 Hz richiede dissolvenze oltre ~14 s
  anche con un inviluppo ideale. Sulla principale il fondo della distorsione della
  catena lascia ~0,05–0,35 mV alla transizione.
- **Il criterio in dB solo per accettare, e C2 a guidare il progetto.** È stata la
  seconda strada proposta. L'utente ha scelto di non allungare Td né di continuare a
  ottimizzare C2.
- **Allungare Td a 8–10 s** per avvicinare il coseno: stima di L29b2, non misurata.

## Cosa precisa

- **Precisa ADR-035**: C2 resta come metodo di diagnostica, e la soglia di 1 mV
  resta come riferimento. Il verdetto del taglio passa a S.
- **Precisa ADR-032**: le grandezze del verdetto di V2 sono A, B e S.
- **Precisa ADR-038**: «l'utente ha scelto di tenere la soglia» di C è superato da
  questa decisione, su un dato nuovo.
- **ADR-039** (stesso lotto) scrive il contratto del comando con la v4.

## Da riaprire se

- Sul prototipo il salto della v4 si sente, o un altro evento sotto 20 dB dà
  fastidio all'ascolto.
- I modelli veri (NC-017) cambiano l'inviluppo al jack: il salto si rimisura.
- La cella reale si spegne più in fretta dell'ipotesi pessimistica (0,4 decadi/s
  sopra 80 kΩ): l'inviluppo cambia forma, e S si rimisura.
- L'utente vuole un margine sotto i 20 dB. La v4 ne ha, e la finestra o il pavimento
  si possono stringere senza toccare il circuito.
