# ADR-089 — I guasti del blocco sulla Stax col limite all'inseguitore: più lunghi, accettati sotto il tetto

Data: 2026-10-19 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Applica ADR-086** (la ridondanza nel blocco, il tetto della Stax a 150 ms) e **ADR-087** (R153,
  4,7 kΩ sul collettore dell'inseguitore davanti al VAS): li prova sui guasti della Stax.
- Il tetto di 150 ms di ADR-086 resta; non si apre niente.

## Contesto

L60d2 ha rifatto P10 sulla Stax (`data/2026-10-19/L60d2/`, `p10_stax.csv`) sul blocco di oggi: i 107
guasti del blocco di L60c2 più i 20 delle parti nuove (R150–R153, R112 / R144 in corto), sulle
posizioni A e F2, condensatore nominale e +5 %.

- **La tabella di ADR-086 è risolta**: R109 aperta da 0,4–1,2 s a **0 ms**; R112 aperta e R144 aperta
  da 117–149 a **0 ms**; Q133 in corto da 127–135 a **19–21 ms**; la source di JQ110B aperta da
  140–149 a 110–124 ms. Le parti nuove, aperte e in corto: 0 ms.
- **Nessun guasto oltre 150 ms** (il peggiore 128,5 ms).
- **17 guasti durano di più che in L60c2** (34 corse, quasi tutte sul blocco A): D102 / D103 aperti
  da 98 a **128,5 ms**, JQ110A in corto da 78 a 124 ms, Q106 in corto, R107 in corto, Q121A, R119,
  Q146 in corto; su F2 gli stessi, al più 116 ms.
- **La causa** (`script/diagnosi_peggio.py`): le stesse corse col blocco di L45a e col blocco di oggi
  con R153 a 1 Ω danno le stesse cifre, quelle di L60c2 (D102 aperto 94,9 ms, JQ110A in corto
  74,9 ms). Senza il limite, l'inseguitore del blocco guasto assorbe fino a 0,26 A dai rail e tiene
  l'uscita a ~6 V; col limite l'uscita va a 12,6 V e la Stax resta sopra 0,87 V più a lungo. È lo
  stesso scambio di ADR-087 visto da un guasto: il limite toglie il calore (Q146 da 0,41 W a 0,027 W
  in P7) e lascia l'uscita più vicina al rail.
- Il prompt del lotto chiedeva che «il resto dei modi di A e F2 non peggiori».

## Decisione

La domanda all'utente (2026-10-19), coi numeri qui sopra; la risposta: **«Accetta, sotto il tetto»**.

- I 17 guasti più lunghi sono accettati: tutti entro i 150 ms di ADR-086, col margine minimo di
  21,5 ms (D102 / D103 aperti, blocco A, condensatore +5 %).
- NC-069 si chiude.

## Perché

- Il criterio per la Stax è il tetto, non il confronto con la versione precedente.
- Il rimedio alternativo (un limite diverso sull'inseguitore) cambia il blocco con tutta la sua
  regressione, per guasti che sono già sotto il tetto.

## Alternative scartate

- **Fermarsi e cercare un rimedio**: un altro valore di R153 riapre ADR-087 (10 kΩ non converge in
  parti della matrice d'anello; meno di 4,7 kΩ limita meno il calore).

## Conseguenze

- Il registro di NC-069 e il report di L60d2 riportano le durate.
- L45d2b3 (i guasti nella forma di ADR-070) parte da queste durate, non da quelle di L60c2.

## Da riaprire se

- Un guasto del blocco sulla Stax, misurato sul prototipo o in una simulazione futura, supera i 150 ms.
- R153 cambia valore.
