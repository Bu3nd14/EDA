# ADR-034 — Il moltiplicatore di Vbe si accoppia al transistor d'uscita col rame del PCB, non con la fascetta

Data: 2026-09-15 · Stato: accettata

## Contesto

Il transistor del moltiplicatore di Vbe deve inseguire la temperatura del
**MJE15032**. `circuits/preamp/gain_block.py`, sezione 4, lo accoppiava al tab con
«thermal compound + cable tie». Ma **ADR-017** lo porta a un **MMBT5551 in
SOT-23**, e un SOT-23 non si fascetta a un TO-220: è **NC-019**.

## Decisione

1. **L'accoppiamento termico passa per il rame del PCB**, fra il SOT-23 del
   moltiplicatore e il MJE15032 dello stesso blocco. **T7 resta intatta**: la parte
   resta l'MMBT5551. L'utente, dopo L20: «ponte di rame sul PCB fra la piazzola
   del SOT-23 e quella del tab del TO-220». In L38, sentiti i due vincoli qui sotto:
   «Rame, forma da dimensionare».
2. **La forma la dimensiona e la dichiara `pcb-automation-engineer` prima di
   G2**: geometria, strato, isolamento e footprint del TO-220. Deve rispettare i
   due vincoli.

## Perché

**Due vincoli trovati in L38**, rileggendo il sorgente:
- **Il tab del MJE15032 è il collettore, su `VP`**, +15 V: in `gain_block.py` si
  legge `Q("npn", "MJE15032", "NMJE15032", VP, NBN, NEN, fp=FP_TO220)`, con la
  firma `Q(kind, val, model, c, b, e)`.
  - Il moltiplicatore sta su `NX`, `NBB` e `NY`, e nessuno dei suoi piedini è su
    `VP`.
  - Un ponte di rame **galvanico** fra una sua piazzola e il tab metterebbe in
    corto il rail. Il rame che porta calore va isolato elettricamente da almeno
    uno dei due lati.
- **Il footprint di oggi, `TO-220-3_Vertical`, ha solo le piazzole 1–3.** La
  piazzola del tab non c'è.
  - La libreria KiCad installata ha anche `TO-220-3_Horizontal_TabDown` e
    `_TabUp`.
  - La scelta non si fa qui.

**Perché conta.**
- Il moltiplicatore esiste per inseguire la V_BE d'uscita.
- Il suo 1,69 kΩ è **spazzato**: 50 Ω spostano I_q di 0,78 mA, come scrive
  `gain_block.py`.
- Senza accoppiamento, la classe A di ADR-003 dipende dalla temperatura.

**Oggi la parte non è ancora nel sorgente.** `gain_block.py` istanzia il 2N5551
col footprint TO-92: la sostituzione è di Fase 4 (NC-017). La regola vale per la
parte che ADR-017 ha scelto.

## Alternative scartate

- **Pasta termica e fascetta**: non si applica a un SOT-23.
- **Tenere il moltiplicatore a foro passante**, con la lacuna T7 dichiarata (la
  seconda strada di NC-019): l'utente vuole T7 intatta.
- **Un collegamento di rame galvanico diretto** fra la piazzola del SOT-23 e il
  tab: è un corto fra `VP` e un nodo di polarizzazione.

## Da riaprire se

- **`pcb-automation-engineer` non trova una geometria isolata** che accoppi
  abbastanza.
- **Il prototipo mostra una deriva di I_q** con la temperatura del MJE15032.
- **La Fase 4 ritara il moltiplicatore** coi modelli vendor e cambia la
  dissipazione.
- **Il transistor d'uscita cambia package**, o cambia il netto del suo tab.

Precisa **ADR-017** (costo di layout del SOT-23). Non ne supera nessuna.
