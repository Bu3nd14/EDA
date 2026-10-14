# ADR-072 — Un rivelatore di continua sulle uscite dei blocchi: apre il mute, toglie la linea dei relè alla scheda audio e spegne i rail audio

Data: 2026-10-14 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- È il rimedio di P10 (ADR-069) per i guasti del blocco. ADR-069 lo aveva indicato come candidato e
  ne aveva lasciato la scelta a L45d.
- Copre cinque scelte di `data/2026-10-14/L45d1/scelte_L45d2.pdf`: la **1**, la **6**, la **8**, la
  **9** e la **10**. Una sola ADR perché il meccanismo è uno solo. Le sezioni qui sotto seguono il
  numero della scelta.
- Il progetto del circuito, la soglia e la prova sono di **L45d2b**. Il dispositivo d'uscita resta
  a L55 e il moltiplicatore di Vbe a NC-062.

## Contesto

Un guasto del blocco di guadagno porta il blocco al rail: ~14,9 V al jack (~137 dB SPL a 1 m),
sopra il tetto di 0,87 V per 0,56–3,1 s, contro i 100 ms di P10. Nessun mute può abbassare il
picco, che arriva al jack insieme al guasto (L45a). Il tempo invece sì: col rivelatore ideale di
L45b scende a 0,2–10,1 ms. In 21 di quelle righe c'è anche un secondo guasto per calore (in cima
C145 in corto, con R144 a 22,5 W), e il mute da solo non lo toglie.

## Decisione

Parole dell'utente (2026-10-14): «Sì, apre il mute e toglie la bobina» (scelta 1); «Coperte dal
rivelatore» (scelte 8 e 9); «Togliere i rail al guasto» (scelta 10); «Togliere la bobina al guasto»
(scelta 6).

**Un rivelatore di continua sulle uscite dei blocchi, in hardware.** Quando un'uscita ha continua:
1. **apre il mute**, cioè stacca i jack (scelta 1);
2. **toglie la linea dei relè (`VRELAY`) alla scheda audio**: nessuna bobina resta alimentata, e
   un isolamento bobina-contatti che cede non ha più 12 V da portare sul segnale (scelta 6, e i
   relè di mute di ADR-071);
3. **spegne i rail audio**: il ramo che scalda resta senza corrente, e il secondo guasto per calore
   dura quanto il rivelatore più la scarica dei rail (scelta 10 e le 21 righe col calore della
   scelta 1).

**Scelte 8 e 9, coperte.** Il filo del rail positivo che si apre fra le due schede porta il blocco
al rail, e il rivelatore lo vede anche se il sorvegliante legge il rail dal lato
dell'alimentatore. Il condensatore d'uscita in corto lascia l'uscita accoppiata in continua: un
guasto del blocco che arriva dopo ora viene visto e mutato invece di non decadere più. L45d2b
verifica entrambi i casi sul banco, senza aggiungere parti per loro.

## Perché

- **È l'unico rimedio che porta i guasti del blocco dentro P10**: 52 righe alte e 6 medie. Il
  tempo sopra il tetto passa da secondi a millisecondi; il picco resta, e P10 lo dichiara senza
  soglia.
- **Un solo segnale chiude tre problemi.** La continua su un'uscita è il sintomo comune del blocco
  guasto, del rail che manca e dell'isolamento che cede. Toglierle sia il jack sia le bobine sia i
  rail costa un rivelatore, non tre.
- **In hardware, come vuole PR-24**: la sicurezza non dipende dal firmware.

## Vincoli per L45d2b

- **La musica non deve farlo scattare.** Col volume al massimo la musica supera 0,87 V (ADR-069):
  il rivelatore deve distinguere la continua dal basso più profondo. La soglia e la costante di
  tempo si scelgono sul banco, contro i 100 ms di P10.
- **I rail non si spengono di colpo.** La tenuta dopo i regolatori (≥ 1500 µF effettivi per rail,
  P9 (b)) li tiene su per un tempo che va misurato. Il calore del secondo guasto si giudica su quel
  tempo, contro i limiti di PR-22 / P7. Un candidato è la strada che esiste già: dopo un guasto con
  la rete presente il temporizzatore stacca il toroidale (P9 (b)).
- Dopo lo scatto l'apparecchio resta spento fino a un comando dal frontale, come dopo un guasto
  dell'alimentatore.
- **I guasti toccati si rifanno**, con le colonne dopo il rimedio di ADR-070: le scelte 1, 6, 8, 9 e
  10, e i 28 guasti di ADR-071 che il rivelatore potrebbe vedere.

## Alternative scartate

- **Il rivelatore che apre solo il mute**: lascia la bobina a 12 V sui relè di mute, e lascia il
  calore.
- **Relè a isolamento rinforzato** (scelta 6): il circuito non cambierebbe, ma il datasheet va
  verificato relè per relè, e il problema delle bobine a 12 V resterebbe sui relè di mute.
- **Limitare la corrente nei rami che scaldano** (scelta 10): una parte per ramo, e il dispositivo
  d'uscita è comunque di L55.
- **Un filo di ritorno del sensore del rail** (scelta 8): un pin in più fra le schede per un caso
  che il rivelatore vede già.
- **Accettare**: i guasti del blocco resterebbero fuori da P10 per secondi.

## Da riaprire se

- In L45d2b nessuna soglia separa la continua di un guasto dalla musica più bassa entro i 100 ms:
  si torna all'utente con i numeri (ADR-069, «Da riaprire se»).
- I rail scendono troppo piano perché lo spegnimento tenga il calore dentro i limiti: per la scelta
  10 si torna alla corrente limitata nel ramo.
- Il rivelatore stesso ha un guasto che lo rende cieco: è un guasto latente, e va alla diagnosi
  (L58).
