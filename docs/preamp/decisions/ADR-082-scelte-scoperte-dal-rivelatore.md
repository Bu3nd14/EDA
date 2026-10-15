# ADR-082 — Le scelte che il rivelatore copriva: il condensatore della Stax dopo il relè, due pin per i rail, il condensatore in corto accettato, il moltiplicatore in SOT-223

Data: 2026-10-15 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Supera ADR-072 nelle scelte 6, 8, 9 e 10** di `data/2026-10-14/L45d1/scelte_L45d2.pdf`, che
  affidava al rivelatore di continua; ADR-081 aveva tolto il rivelatore e lasciato queste quattro
  scelte senza rimedio.
- **Precisa ADR-081 punto 1**: il condensatore da 1 µF della fissa 2 sta fra il relè di mute e il
  jack, non fra la 47 Ω e il relè.
- **Precisa ADR-044** (la geometria del mute) sulla sola fissa 2, e **ADR-017** sul solo transistor
  del moltiplicatore di Vbe (come ADR-068 fece per il VAS e il suo carico).

## Contesto

L60a (`reports/2026-10-15-L60a-scelte-scoperte.md`), prima parte di L60, divisa dall'utente
all'inizio («Tre parti»). Il banco del canale di L45a / L45b senza rivelatore, con 1 µF sulla fissa
2 e i carichi montati (`data/2026-10-15/L60a/`, 30 corse; le tre di riferimento riproducono i numeri
noti: 44,2 ms, 552 ms contro ~0,56 s, 12 V fino alla fine; il blocco F2 al rail con 1 µF 117,5 ms
contro i 117 ms di ADR-081). Sulla fissa 2, col carico della Stax:

| Scelta | Il guasto | Sulla Stax | Principale / fissa 1 |
|---|---|---|---|
| 6 | isolamento bobina-contatti di **K3** (il mute della Stax, dopo il condensatore), 10 Ω / 1 kΩ, sul NO o sul comune | **12 V / 11,7 V per sempre** | — |
| 6 | lo stesso sul selettore K13 (a monte del blocco A), 10 Ω / 1 kΩ | 116 / 95 ms, picco 13,5–13,9 V | 510 / 258 ms; 127 / 105 ms |
| 6 | lo stesso su K7 (la cima di C_T) | 70 ms, 5,9 V | 95 ms; 77 ms |
| 6 | lo stesso su K2 e K4 | — | **12 V per sempre** (a valle) |
| 8 | il filo del rail positivo aperto fra le schede, a 0 e +10 dB | **388–421 ms**, picco 1,27–1,35 V | 932–957 ms (6,2–9,3 V); 410–433 ms |
| 8 | il filo del rail negativo aperto | 3,7 mV | ≤ 12 mV |
| 9 | il condensatore della fissa 2 in corto | 6,3 mV | — |
| 9 | lo stesso, poi il blocco A o F2 al rail | **14,4–15,0 V per sempre** | come senza |
| 10 | R126 in corto (A, F1, F2, B, B a +10 dB) | 37–38 ms | 32–47 ms; 29 ms |

Il calore della scelta 10: con R126 in corto **Q127, il transistor del moltiplicatore di Vbe, dissipa
0,49 W, ~231 °C** (SOT-23, 417 °C/W), per sempre: l'uscita torna a −0,22 V. **Il rivelatore non
scattava** su questo guasto (L45d2b1, `banco/guasti.csv`: scatto solo nel blocco B a +10 dB), e il
«106 ms» di NC-066 è un altro guasto (C145 in corto, il rail che cede). Toglierlo non cambia niente.

## Decisione

Parole dell'utente (2026-10-15), alle domande poste per nome coi numeri qui sopra:

1. **Scelta 6** — «Condensatore dopo il relè e solo se non passano le misure nella terza parte allora
   Relè a isolamento rinforzato». **Sulla fissa 2 il condensatore da 1 µF va fra il relè di mute (K3)
   e il jack.** Tutti i contatti di K3 stanno allora a monte del condensatore, e i 12 V di una bobina
   che cede arrivano alla Stax solo come colpo che decade sul carico (a calcolo 41,2 ms ·
   ln(12 / 0,87) ≈ 108 ms, della classe del selettore). La geometria del mute su quell'uscita si riprogetta in L60c (dove va il contatto di
   riposo, i bleed) e si misura con le prove della fissa 2 (E9, P10 coi guasti di K3, V2,
   l'inserimento a caldo). **Se una di quelle prove non passa**, il condensatore torna dov'è oggi e
   **K3 diventa un relè con isolamento rinforzato fra bobina e contatti** (il G6K ha isolamento base,
   1500 V efficaci, `vendor/relays/omron/G6K/en-g6k.pdf`), da scegliere sul datasheet.
2. **Scelta 8** — «Due pin per il rail». **Il rail positivo e il negativo passano fra le due schede
   su due pin e due fili ciascuno**, in parallelo: un pin o un filo che si apre non toglie più il
   rail. Resta il guasto doppio. Nessun circuito nuovo.
3. **Scelta 9** — «Accettarlo, è doppio». Il condensatore in corto, da solo, è un colpo di 6 mV;
   la Stax esposta per sempre richiede un secondo guasto del blocco. PR-30 parla di **un**
   componente che si rompe: il caso sta fuori, scritto come guasto doppio. Il film di
   polipropilene si guasta di norma aperto.
4. **Scelta 10** — «Package grande». **Q127 diventa DZT5551 in SOT-223**, lo stesso die e lo stesso
   modello del MMBT5551 (come ADR-068): a 0,49 W e 125 °C/W sulla piazzola minima ~88 °C con 27 °C
   d'aria (~121 °C con i 60 °C d'aria, sotto i 125 °C di P7). La linguetta è il
   collettore, NX: non è sul rail positivo, quindi l'accoppiamento termico col finale MJE15032 in
   rame senza contatto galvanico (ADR-034) resta possibile, e la linguetta lo facilita.

## Perché

- **Scelta 6**: il relè di mute della Stax sta dopo il condensatore, e nessuna protezione a valle lo
  copre; spostare il condensatore usa la parte che c'è già e porta il guasto nella stessa classe del
  selettore (116 ms, dentro i 125). Il relè rinforzato resta la riserva se la geometria nuova non
  regge le prove. Raro: ~0,5 guasti per 10⁹ h su K3 (`scelte_L45d2.pdf`, scelta 6).
- **Scelta 8**: fuori da PR-30 sulla Stax per un fattore ~3 (388–421 ms contro 125), perché il rail
  scende piano e la deriva lenta passa il condensatore. Due pin costano un connettore più largo e
  nessuna parte attiva; il filo di ritorno del sensore richiedeva una misura in più e un pin lo
  stesso. 0,3 guasti per 10⁹ h.
- **Scelta 9**: doppio guasto; ~0,8 guasti per 10⁹ h per il corto, moltiplicati per un guasto del
  blocco dopo.
- **Scelta 10**: 0,2 guasti per 10⁹ h, ma il transistor a 231 °C si rompe e il guasto che segue è
  un altro, non previsto. La parte nuova costa un'impronta, non un circuito.

## Alternative scartate

- **Scelta 6**: accettarlo (12 V per sempre sulla Stax, 23 dB sopra il tetto); il relè rinforzato
  subito (resta la riserva).
- **Scelta 8**: il sorvegliante che legge il rail dal lato della scheda audio (un pin in più e una
  durata ancora da misurare); accettarlo come eccezione a PR-30.
- **Scelta 9**: due condensatori in serie (2 × 2,2 µF: uno in corto lascia 2,2 µF, ~250 ms sopra il
  tetto); mandarlo alla diagnosi (L58).
- **Scelta 10**: lasciarlo a NC-062, che rivede il moltiplicatore per un altro motivo (il calore dei
  finali); accettarlo.

## Conseguenze

- **L60b** (togliere il rivelatore) fa anche i due pin per rail su J1 (`psu.py`,
  `preamp_audio.py`, `check_psu_harness.py`, i disegni) e Q127 in SOT-223 (`gain_block.py`, il
  commento di ADR-017 / ADR-034 aggiornato), con le netlist rigenerate una volta sola.
- **L60c** sposta il condensatore della fissa 2 dopo K3 a 1 µF, riprogetta la geometria del mute su
  quell'uscita e la misura; le prove di P10 col carico della Stax comprendono i guasti di K3
  (isolamento sul NO e sul comune, 10 Ω e 1 kΩ) e il filo del rail con un solo pin dei due aperto.
- **NC-066**: il «106 ms» è il caso C145 / R144, non la scelta 10; la voce si chiude comunque col
  rivelatore.
- Se NC-062 cambia il moltiplicatore, il package di questa ADR vale per il transistor che lo
  sostituisce.

## Da riaprire se

- Le prove di L60c sulla geometria nuova non passano: si passa al relè rinforzato (questa ADR lo
  prevede già) e, se nessun relè adatto si trova, si torna all'utente.
- Il connettore fra le schede non ha pin per raddoppiare i due rail: si torna all'utente con le due
  alternative scartate della scelta 8.
- L'accoppiamento termico col finale (G2) non si riesce a fare con la linguetta del SOT-223 sul
  collettore.
