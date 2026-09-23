# ADR-043 — Lo spegnimento è un requisito dell'alimentatore, e la protezione del jack non deve dipendere dall'alimentatore sano

Data: 2026-09-23 · Stato: accettata

## Contesto

L29c ha misurato V2 allo spegnimento col mute reale (`reports/2026-09-23-L29c-v2-caso-peggiore.md`,
dati `data/2026-09-23/L29c/matrice/veloci/`, 24 corse: rampe dei rail da 10 e 300 ms, simmetriche
e con un rail in ritardo di 50 ms, relè del jack chiuso da 0 a 100 ms dopo l'inizio della
discesa). Nessuna corsa regge i 100 µV di V2.

Il meccanismo è fisico, non numerico. Quando i rail scendono sotto circa **9,5–10,4 V**,
l'uscita del blocco B perde la regolazione: nella rampa da 10 ms scatta in 60 µs da −0,1 a
−9,1 V; in quella da 300 ms scivola a −3,6 V in ~10 ms. Il 4,7 µF porta il salto al jack:
- col relè ancora aperto, arriva intero: **8,9–17,5 V** con 5 ms o più di ritardo;
- col relè già chiuso, il jack ne vede la frazione 0,1 Ω / 47 Ω (il contatto contro la resistenza
  d'uscita, circa 1/470): **11 mV** nella rampa da 10 ms, **0,24 mV** in quella da 300 ms.

Quindi il solo relè in derivazione al jack, con qualunque ritardo, non porta lo spegnimento
sotto la soglia. Le corse con un rail in ritardo e con la discesa brusca sono anche la forma di un
**guasto** dell'alimentatore.

## Decisione

Parole dell'utente, il 2026-09-23: «(b), ma dobbiamo anche prevedere un failsafe mechanism in
cui l'alimentatore si rompa».

1. **Lo spegnimento normale è un requisito del lotto dell'alimentatore (L30).** I rail audio
   restano sopra la soglia a cui il blocco perde la regolazione (~10 V misurati, da rimisurare
   sul circuito di L30) finché il mute non è completo: mute graduale e relè al jack. Servono un
   supervisore che comandi il mute alla perdita di rete, e una tenuta dei rail che copra il
   mute più il margine. L30 lo verifica col metodo di V2, sul deck `tb_v2_casopeggiore.cir`
   (punto 5) o su un suo derivato.
2. **Un guasto dell'alimentatore non deve portare il salto al jack.** La protezione del jack non
   può dipendere dall'alimentatore sano: rail che cade di colpo, un rail solo, supervisore
   guasto. I numeri di L29c dicono che il relè in derivazione da solo non basta (~1/470). La
   forma del meccanismo la progetta **L30**, con l'utente. **Nessuna tecnica è scelta qui.**
3. **La soglia in caso di guasto resta aperta**: V2 per intero (100 µV), oppure una soglia di
   non-danno per il finale e i diffusori. Si chiede all'utente quando L30 la usa.

## Perché

- È la scelta dell'utente fra le tre proposte da L29c: (a) eccezione scritta di V2, (b) requisito
  all'alimentatore, (c) lotto sulla topologia dello stadio d'uscita o del mute al jack.
- Il salto nasce dai rail, non dal mute: sopra ~10 V lo stadio regola e il mute di L29c tiene.
- Il failsafe è la conseguenza diretta dei dati: le corse che simulano un guasto portano volt
  al jack se il relè ritarda, e decine di mV anche col relè immediato.

## Alternative scartate

- **(a) Eccezione scritta di V2 allo spegnimento**: non scelta dall'utente.
- **(c) Un lotto sulla topologia adesso**: non scelta; resta la strada se L30 non trova un
  alimentatore e un failsafe che reggano.
- **Solo un ritardo diverso del relè**: misurato, non basta (§ Contesto).

## Da riaprire se

- L30 non riesce a tenere i rail sopra la soglia per il tempo del mute con componenti ragionevoli.
- Il failsafe richiede un elemento in serie al segnale o un cambio dello stato sicuro di ADR-012.
  Allora è una modifica di topologia, e torna all'utente.
- La soglia di perdita della regolazione si sposta molto sul circuito definitivo.

Precisa **ADR-032** (V2 vale «accensione e spegnimento compresi») e **ADR-012** (lo stato sicuro
del mute); consegna a **L30** due requisiti.
