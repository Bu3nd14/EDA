# ADR-024 — La sonda capacitiva di V1 è il cavo: al jack, ogni cavo fino a 4,7 nF; il blocco A col suo cablaggio

Data: 2026-09-14 · Stato: accettata

## Contesto

**ADR-019** fissa 60° «ovunque, caso peggiore capacitivo da 4,7 nF compreso», ma
non dice **dove** si applica la sonda. Il repo misurava in due posizioni diverse:
il blocco B al jack (`tb_loop.cir`), il blocco A sul nodo d'uscita (NC-002).

L12 ha misurato tutte e due le posizioni, coi valori di L17
(`data/2026-09-14/L12/prima/`, esplorazione nel report):

| Istanza | Sonda sul nodo, 4,7 nF | Al jack, minimo della spazzata fino a 4,7 nF |
|---|---|---|
| Blocco A | 40,96° | nessun jack |
| Buffer delle fisse | 40,89° | 61,51° (Stax, 2,7 nF) |
| Blocco B a 0 dB | 36,26° | **54,97°** (attenuatore a metà corsa, 2,7 nF) |

Al jack il margine **non è monotono**: tocca il minimo fra 2,2 e 3,3 nF e poi
risale. A 4,7 nF il blocco B dava 56,46°, non il suo caso peggiore.

## Decisione

Parole dell'utente, 2026-09-14: la sonda «per me é il cavo di collegamento tra il
pre e il finale oppure tra il pre e gli ampli cuffia», e poi «ogni cavo fino a
4,7 nF, blocco A con capacità realistica».

1. **La sonda è il cavo d'interconnessione**, e sta **al jack**: dopo i 47 Ω e il
   4,7 µF, sul blocco B e sui buffer delle fisse.
2. **Il verdetto è il minimo sulla spazzata fino a 4,7 nF**, non il valore a
   4,7 nF: un cavo più corto deve passare come uno lungo.
3. **Il blocco A** non pilota un cavo verso un apparecchio: pilota il cablaggio
   interno fino all'attenuatore sul pannello. Si giudica con una **capacità
   realistica** di quel cablaggio, presa **≤ 1 nF**. Il repo non ha misure del
   telaio; 1 nF è circa dieci volte la stima di ≤ 50 cm a 100-150 pF/m. Il
   valore è dell'orchestratore ed è stato dichiarato all'utente.
4. **La sonda sul nodo resta nei deck** come informazione, e come controllo che il
   deck sappia fallire.

## Perché

- **Sul nodo non c'è nessun cavo vero.** È una prova più severa della realtà, e
  con essa fallivano tutte e otto le istanze.
- **Il minimo della spazzata** è l'unica lettura che copre i cavi reali. Letto a
  4,7 nF il blocco B sembrava 1,5° migliore di quanto sia.
- **Il blocco A** con 4,7 nF sul cablaggio simulerebbe decine di metri di filo
  dentro un telaio.

## Alternative scartate

- **Sonda sul nodo**: 8 istanze su 8 sotto soglia, blocco B a 36,26°, senza un
  cavo che lo giustifichi.
- **Sonda al jack letta solo a 4,7 nF**: salta il minimo fra 2,2 e 3,3 nF.
- **4,7 nF anche sul cablaggio del blocco A**: scartata dall'utente.

## Da riaprire se

- **Il telaio** dà un cablaggio verso l'attenuatore con più di 1 nF, o l'attenuatore
  lascia il pannello per un cavo lungo.
- **Si aggiunge un'uscita senza resistenza in serie**: lì jack e nodo coincidono.
- **Si prevede un cavo oltre 4,7 nF** (qualche decina di metri).

Precisa **ADR-019** e il testo di **V1**, senza riscriverli.
