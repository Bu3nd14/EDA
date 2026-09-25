# ADR-045 — Il permissivo K6 ha un comando proprio, e all'inserimento del mute rilascia dopo i relè del jack

Data: 2026-09-25 · Stato: accettata

## Contesto

Il residuo di L36 (`reports/2026-09-25-L36-guadagno-interbloccato.md`, sezione 7; NC-028) è
questo: la manopola del guadagno viene girata **fuori** mute, e poi si inserisce il mute. A quel
punto il guadagno va alla manopola:
- all'apertura del NO di K6, più il tempo di rilascio di K1, se scende;
- alla chiusura dell'NC di K6, più il tempo di operate di K1, se sale.

Il trim ha la stessa forma, al tempo di set dei bistabili (ADR-027).

K6 ha la bobina su `MUTE_CMD`, come i relè del jack K2–K4 (ADR-019 §2, ADR-027). Rilasciano
insieme, e l'ordine «prima si staccano i jack, poi cambiano guadagno e trim» dipende dallo scarto
fra esemplari della stessa parte. Il datasheet non lo dà.

Se l'ordine si rovescia, il gradino d'offset del blocco B arriva al jack. È dello stesso ordine
del cambio a caldo: fino a **~90 dB SPL di picco a 1 m**, un limite superiore calcolato con la
formula di NC-028. La soglia V2 è ~33 dB, e una stanza silenziosa ha un fondo di ~25–35 dB(A).
L'utente, il 2026-09-25: «non possiamo accettare il comportamento». La regola d'uso non rende
comunque conforme V2 (ADR-032).

## Decisione

Parole dell'utente, il 2026-09-25: «sono d'accordo con lo sfasamento e metti una nota per il
failsafe».

1. **K6 ha un comando proprio, `PERMIT_CMD`**, distinto da `MUTE_CMD`. Lo dà il temporizzatore
   del mute, fuori dal percorso del segnale (ADR-022).
2. **All'inserimento del mute**: prima rilascia `MUTE_CMD` (K2–K4: jack staccati, lato del
   condensatore a massa, ADR-044), poi, **dopo Δ**, `PERMIT_CMD` (K6).
   - Guadagno e trim si possono muovere solo dopo il rilascio di K6, quindi a jack già staccati.
   - Δ deve superare il rilascio massimo dei relè del jack, **3 ms** (en-g6k.pdf p. 3), più il
     margine. Si propone **~20 ms**; il valore lo fissano L35 e il lotto dell'alimentatore.
3. **Al rilascio del mute**: `PERMIT_CMD` si eccita **non dopo** `MUTE_CMD`.
   - Il guadagno non cambia, perché il polo ponte di L36 lo tiene indipendentemente da K6.
   - Il trim non cambia, perché i bistabili tengono lo stato.
   - Resta fermo il vincolo di ADR-027: il mute si rilascia non prima di 10 + 3 ms da quando
     `VRELAY` è valida.
4. **Il 2e cambia**: oggi asserisce che la bobina di K6 sta sulle net dei relè di mute. Dovrà
   asserire che sta su `PERMIT_CMD`. La prova d'interblocco deve continuare a trattare K6 come «il
   mute» (eccitato fuori mute). Il sabotaggio da far fallire: K6 di nuovo su `MUTE_CMD`.
5. **Lo realizza L35**, come primo punto, prima del pannello: cambia i fili del comando del mute
   che L35 porta comunque al connettore.

## Perché

- **L'ordine diventa una cifra del costruttore.** Oggi dipende dallo scarto fra due rilasci che il
  datasheet non limita dal basso. Con lo sfasamento dipende da Δ contro il rilascio massimo,
  3 ms, che il datasheet dà.
- **In dB**: il caso che L36 lasciava aperto, fino a ~90 dB di picco possibili, torna a quello di
  un cambio sotto mute. È 0,17 µV misurati in L29d2/L29e sulla geometria iii, cioè **~−22 dB**:
  circa 55 dB sotto la soglia V2 e circa 50 dB sotto il fondo della stanza.
- **Chiude anche il trim**, che ha la stessa forma e nessuno aveva ancora messo in dB.
- **Non aggiunge relè** né componenti che accumulano carica: non si realizza nessun «Da riaprire
  se» di ADR-030. Aggiunge un filo di comando e una seconda uscita sfasata nel temporizzatore.

## Alternative scartate

- **Accettarlo e misurarlo al prototipo**: rifiutato dall'utente.
- **La regola d'uso «prima il mute, poi la manopola»**: rifiutata dall'utente, e comunque non
  rende conforme V2 (ADR-032).
- **Un permissivo in più, o relè di mute con più poli per leggere lo stato vero dei jack**:
  riaprono ADR-030 e costano parti. Non danno una garanzia migliore di Δ contro 3 ms.
- **Rallentare K1/K5 con un condensatore**: accumula carica, cioè un «Da riaprire se» di ADR-030.
  E il trim non ne beneficia.

## La nota per il failsafe (ADR-043, L30)

**Lo sfasamento vale solo con `VRELAY` presente.** Se `VRELAY` crolla (rete persa, alimentatore
guasto), tutte le bobine cadono insieme, e cadono insieme anche K2–K4, K6, K1/K5 e K11/K12:
- **K1 e K5 tornano a 0 dB (F5) nello stesso istante in cui si staccano i jack.** Si ripresenta
  la corsa di questa ADR: un gradino d'offset fino a ~90 dB di picco, se il guadagno scende
  prima che il NO del jack si apra.
- I bistabili del trim non si muovono senza corrente.

**Quindi il failsafe di L30 deve coprire anche questo.** Alla perdita di rete o di `VRELAY`:
- deve rilasciare `MUTE_CMD` per primo;
- deve tenere alimentate le bobine di K6, K1/K5 e K11/K12 per almeno Δ dopo;
- oppure deve dimostrare con un altro meccanismo che il guadagno non cambia prima dello stacco
  dei jack.

Si aggiunge ai due requisiti che ADR-043 consegna a L30 (lo spegnimento normale e il guasto
dell'alimentatore), e si verifica col metodo di V2.

## Da riaprire se

- Il temporizzatore non può dare due uscite sfasate senza logica nel percorso del segnale.
- Δ non ci sta nel tempo di tenuta di `VRELAY` che L30 riesce a garantire, nel caso del failsafe.
- Un catalogo successivo del G6K cambia il rilascio massimo di 3 ms.

Precisa **ADR-019 §2** e **ADR-027** (la bobina di K6 non è più su `MUTE_CMD`) e **ADR-041**
(chiude il residuo di L36). Aggiunge un requisito al failsafe di **ADR-043**.
