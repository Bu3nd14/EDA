# ADR-036 — A si giudica senza segnale; il mute è graduale e in serie, con rampa da 3 s, accettato con C fuori soglia sulla principale

Data: 2026-09-16 · Stato: accettata

## Contesto

L29a ha misurato col metodo di V2 (ADR-032, precisato da ADR-035) sette varianti
di mute a contatto e quattro posizioni di un mute graduale ideale, con rampe da
20 ms, 200 ms, 1 s e 3 s. Dati: `data/2026-09-16/L29a/corse/`. Report:
`reports/2026-09-16-L29a-metodo-v2-e-varianti.md`. Due cose sono emerse.

**1. A con musica non misura un gradino.** Col riferimento che tiene dall'inizio
lo stato finale, nell'istante della commutazione la corsa con l'evento suona e il
riferimento no, o il contrario: la differenza contiene la musica stessa. Misurato:
A con musica vale **12,7 V sulla principale e 4,03 V sulle fisse per ogni
variante e ogni rampa**, da un contatto netto a una dissolvenza di **3 s**, e
12,8 V a 20 Hz. Una dissolvenza di 3 s non può lasciare un gradino di 12,7 V: è il
picco del segnale al jack (12,07 V) passato dal filtro. È lo stesso difetto che
ADR-035 ha corretto per C.

**2. Nessuna variante rispetta A, B e C insieme.** È il caso del «Da riaprire se»
di ADR-032: «la scelta torna all'utente, con i numeri». La migliore è il mute
graduale **in serie** con rampa da **3 s** (tabella sotto). Portate all'utente il
2026-09-16, con due strade per ciascuna domanda.

## Decisione

1. **A si giudica solo senza segnale.** Con la musica presente decide **C**
   (C2, ADR-035). A con musica resta nelle tabelle come diagnostica, col nome
   `A_musica`, e non entra nel verdetto (`v2_metodo.py`, `base_di`). Parola
   dell'utente: «Come misurare seguo il tuo consiglio».
2. **Il mute di progetto è graduale e in serie, con rampa da 3 s**, accettato
   **con C fuori soglia sull'uscita principale**: 2,93–3,05 mV contro 1 mV.
   Parola dell'utente: «per ora usiamo (ii), accettiamo la serie da 3s».
3. **«Per ora»**: la decisione sceglie la direzione di L29b, non chiude NC-028.
   Il rimedio esiste solo in un deck, con un elemento graduale **ideale**.

## Perché

- **A senza segnale misura davvero il gradino** — il gradino d'offset, la
  ragione per cui ADR-012 ha voluto il mute — con una risoluzione fino ai
  picovolt. Con musica non si perde niente: il gradino della carica del
  condensatore (i 5,37 V di NC-028) è un termine lento che il fit, senza termine
  continuo, non ricostruisce, quindi finisce nel residuo di C2 e lo boccia già
  (8,9 V sulla variante di oggi). Il prezzo è che con musica il limite effettivo
  diventa quello di C, 1 mV invece di 100 µV. Non si poteva fare meglio: il
  pavimento di una misura per differenza con musica a 1 kHz sulla principale sta
  a 0,57–0,80 mV, e a 100 µV non darebbe mai un verdetto.
- **La serie è l'unica posizione in cui una rampa più lenta aiuta.** Le posizioni
  in derivazione (al jack, prima del condensatore, con o senza offset annullato)
  restano ferme a 0,32–0,42 V di C qualunque sia la rampa, e lasciano ~20 mV di
  residuo a mute inserito. In serie C scende circa come 1/T.

### La variante accettata, misurata

Deck `tb_v2_mute_graduale.cir`, posizione `g4`, celle `bm3s` / `lz3s` e i loro
riferimenti. Estratto versionato: `data/2026-09-16/L29a/corse/serie_3s.csv`.
**SIMULATO**, modelli segnaposto (NC-017), elemento graduale ideale.

| Grandezza | Principale 100 k / 10 k | Fisse 100 k / 10 k | Soglia | Esito |
|---|---|---|---|---|
| A senza segnale | 16 / 13 pV | 13 / 4 pV | 100 µV | ✓ |
| B1, residuo a mute inserito | 1,65 µV / 0,23 µV | 0,63 / 0,075 µV | 100 µV | ✓ |
| B2 | 1,65 µV / 0,23 µV | 0,63 / 0,075 µV | 100 µV | ✓ |
| **C2 a 1 kHz** | **2,93–3,02 / 2,93–3,05 mV** | 0,84–0,87 / 0,83–0,86 mV | 1 mV | **✗ principale**, ✓ fisse |
| C2 a 20 Hz, **solo rampa 1 s**, 100 k | 62 mV | 20 mV | 1 mV | ✗ — rampa da 3 s non misurata |
| C2 a 20 kHz | — | — | 1 mV | **non misurato**: il deck non ha celle a 20 kHz |
| A con musica (diagnostica) | 12,7 V | 4,03 V | — | non è un verdetto |

Il C2 della principale sta **3,7–5,4 volte sopra il suo pavimento** (0,57–0,80 mV):
è una misura, non rumore. Seguendo 1/T, per scendere sotto 1 mV servirebbero
circa **9 s** di rampa: **calcolato, non misurato**.

## Cosa aspettarsi all'ascolto

Stime **calcolate**, non misure. La cifra in dB SPL usa la formula di NC-028
(finale ×21,1, Heresy 96 dB/1 W/1 m): 96 + 20·log(21,1·ΔV / 2,83) dB SPL di picco
a 1 m. **È un limite superiore grossolano**: tratta il picco come un tono
continuo, e un evento breve si sente meno.

**Il gesto.** Premere mute, o rilasciarlo, non è istantaneo: la musica scende, o
risale, in una dissolvenza. La rampa dura 3 s, ma la conduttanza cambia in modo
log-lineare e l'ampiezza al jack cambia quasi tutta mentre attraversa i ~3
decenni attorno a 1/47 S: la dissolvenza **udibile** dura circa 3/13 della rampa,
**~0,7 s**. Si sente come un abbassamento rapido del volume, non come un taglio.
Vale anche per l'accensione, se il mute d'accensione (ADR-012, ADR-027 §5) usa lo
stesso elemento.

**Senza musica, e a mute inserito: silenzio.** Il gradino d'offset all'inserzione
e al rilascio vale picovolt; il residuo a mute inserito microvolt o meno. Niente
«tump», su nessuna uscita.

**Il botto di oggi sparisce.** I 5,37 V al rilascio di NC-028 venivano dal
condensatore d'uscita caricato dalla musica attraverso il contatto verso massa.
In serie il condensatore non vede quella corrente.

**Durante la dissolvenza, sulla principale: 2,93–3,05 mV di C.** Non è un clic.
È la parte della dissolvenza che la ricostruzione del tono su 10 ms non segue:
accompagna la musica mentre sale o scende, non compare nel silenzio.
- **Al livello della prova** — manopola al massimo, +10 dB, sorgente a 2,7 V RMS,
  12 V di picco al jack, un livello che nessuno ascolta — vale al massimo
  **≈ 63 dB SPL** di picco a 1 m (62,8–63,1).
- **A un livello d'ascolto normale** — qualche centinaio di mV al jack (NC-028),
  30–40 volte meno della prova — il residuo scala con la musica e scende a circa
  **73–102 µV, ≈ 31–34 dB SPL**. Stima calcolata sulla linearità del residuo
  col livello, non misurata.
- **È mascherato dalla musica stessa**, che nello stesso istante sta cambiando di
  volume di decine di dB.

**Uscite fisse (Singxer SA-1, Stax SRM-T1): 0,83–0,87 mV, sotto soglia.** La
cifra in dB SPL non si calcola: il guadagno di quegli apparecchi non è noto.

**Le incognite, che l'ascolto del prototipo deve sciogliere.**
- **I bassi.** A 20 Hz, con la rampa da **1 s**, C vale 62 mV sulla principale:
  ≈ 89 dB SPL con la stessa formula. La rampa da 3 s a 20 Hz **non è stata
  misurata**. Attenuano due cose non quantificate qui: l'orecchio a 20 Hz è molto
  meno sensibile, e le Heresy a 20 Hz riproducono poco. Se qualcosa si sente, è
  più probabile un «respiro» nei bassi durante la dissolvenza che un clic.
- **I 20 kHz** non sono misurati per il mute graduale.
- **L'elemento reale.** Il deck usa una conduttanza ideale. Un JFET, un
  fotoaccoppiatore o un altro elemento vero avrà distorsione propria durante la
  rampa, resistenza residua e dipendenza dalla temperatura: può fare meglio o
  peggio.
- **I modelli** sono segnaposto (NC-017): il pavimento di C e parte delle cifre
  dipendono da loro.

## Conseguenze, scritte e non decise

- **NC-028 resta aperta e bloccante.** Si chiude quando il mute graduale in serie
  è un circuito reale nel sorgente, misurato col metodo — L29b.
- **Il caso peggiore di V2 non è coperto da questo confronto**: cambi di
  guadagno, trim, dispersione dell'LSK489, accensione e spegnimento. Anche questo
  è L29b, insieme a P7 per la posizione in serie e al criterio 3 di ADR-030.
- **Il mute in serie cambia lo stato sicuro** di ADR-012: a contatto aperto il
  jack non è più tenuto a massa dal relè. `check_relay_safe_state.py` e ADR-012
  vanno riletti in L29b; una modifica sarà un'ADR nuova.
- **La dissolvenza da ~0,7 s** allunga ogni operazione che passa dal mute: il
  trim (F8) e l'eventuale interblocco del guadagno (ADR-030).

## Alternative scartate

- **A con musica misurata come C2** (differenza dei residui): il pavimento a
  1 kHz sulla principale sta a 0,57–0,80 mV, sopra i 100 µV: non darebbe mai un
  verdetto.
- **Misurare la serie con rampe più lunghe prima di scegliere** (~9 s calcolati):
  rinviata; resta la prima strada se l'ascolto boccia la rampa da 3 s.
- **Chiudere L29a col solo confronto e rinviare la scelta**: l'utente ha scelto.
- **Le varianti a contatto netto** (dopo, prima, entrambi, prima con offset
  annullato, serie, serie più jack, sequenza): C2 fra 6,9 e 10,4 V con musica, in
  ogni caso.
- **Il mute graduale in derivazione**: C fermo a 0,32–0,42 V anche con rampa da
  3 s, e ~20 mV di residuo a mute inserito.

## Da riaprire se

- **L'ascolto del prototipo** sente la dissolvenza, un «respiro» nei bassi o
  qualunque cosa durante il mute.
- **L'elemento reale** misurato non tiene le cifre dell'elemento ideale.
- **Una rampa più lunga** risulta accettabile all'uso: C sulla principale può
  scendere sotto 1 mV (circa 9 s calcolati).
- **I modelli del costruttore** (NC-017 chiusa) cambiano il pavimento o le cifre.
- **La rampa da 3 s a 20 Hz, o una misura a 20 kHz,** esce molto peggio di quanto
  qui stimato.

Precisa **ADR-032** (A: con musica non è un verdetto) e **ADR-035**. Non supera
nessuna ADR. ADR-012 e ADR-021 non si toccano: la loro rilettura per il mute in
serie è di L29b.
