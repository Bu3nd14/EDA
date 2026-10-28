# ADR-103 — I comparatori del temporizzatore tarati sul costruttore, l'innesco della ritenuta tenuto basso all'accensione, lo standby com'è

Data: 2026-10-28 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Completa ADR-102** al punto 2 (la ritenuta): il nodo d'innesco ha una resistenza verso il ritorno
  (R585). Non cambia il resto di ADR-102: le funzioni, gli RC, la coppia a tiristore.
- **NC-037** resta aperta, con la cifra di oggi; il primo «Da riaprire se» di ADR-102 (lo standby
  oltre 0,5 W alla presa col pezzo di T2 scelto) trova qui la strada già misurata.
- **Il verdetto «DO NOT USE»** sul modello di TI del TLV1701 (`vendor/comparator/ti/TLV1702/
  PROVENANCE.json`, L41a) aveva una causa: la traduzione degli interruttori di PSpice (limitations
  #77). Il modello tradotto gira da solo; sul banco dell'alimentatore no.

## Contesto

L54b2 (`data/2026-10-28/L54b2/`, README; report `reports/2026-10-28-L54b2-…`). Il prompt chiedeva i
casi della sicurezza col modello del costruttore dei comparatori contro il comportamentale, e i
pull-up delle uscite tenute basse in standby alimentati solo da acceso.

## Decisione

Parole dell'utente (2026-10-28), alle tre domande coi numeri:

1. **«Comportamentale tarato»**. Il modello di TI tradotto per ngspice (`models/comparator/
   tlv1701_ngspice.lib`, `TLV1701`) torna col datasheet da solo (soglia allo scostamento di 0,4 mV,
   tpLH 574 / tpHL 460 ns contro 560 / 460, 75 mV a 0,5 mA, 55 µA), ma il banco non passa
   l'accensione: ngspice si ferma a 2,19 V di V5, e la variante coi ritocchi numerici dichiarati
   (`TLV1701_OC`) si ferma lo stesso, dopo sette ritocchi, a 0,21 s nello stadio d'uscita. Sul banco
   i comparatori sono il comportamentale coi numeri misurati sul modello di TI (`psu/cmpta.lib`,
   `CMPTA`): dichiarato come taratura, non come il modello del costruttore.
2. **«Resistenza verso il ritorno»**: **R585, 33 kΩ** dal nodo d'innesco della ritenuta (AT_F) al
   ritorno. Sotto la loro alimentazione minima (2,2 V) le uscite dei comparatori possono restare
   aperte (il datasheet non lo dice): AT_F seguiva V5 attraverso R581 e la ritenuta scattava
   all'accensione a freddo col frontale acceso.
3. **«Lasciare com'è»** per lo standby: i pull-up restano sui 5 V sempre presenti.

## Perché

| L'innesco della ritenuta all'accensione a freddo col frontale acceso | la base di Q513 al massimo, V5 < 2,3 V |
|---|---|
| comportamentale (L54b1) | 0,50 V: passa, 0,1 V sotto i ~0,6 V di un BC847 a 25 °C, niente a 60 °C |
| tarato, le uscite vive a 2,0 V / a 2,2 V | la ritenuta scatta: l'apparecchio resta spento finché non si spegne il frontale |
| tarato a 2,2 V con C554 a 470 nF | 0,61 V: sulla soglia già a 25 °C |
| **tarato a 2,2 V con R585 33 kΩ** | **0,30 V** |

- **La ritenuta scatta e tiene** con R585 in ogni caso di guasto provato (`guasto`, `guasto_u503`,
  `ritenuta_frontale`, i sorveglianti ciechi), col comportamentale e col tarato.
- **Il prezzo**: alto, AT_F tende a 1,24 V invece di 5 V, e la ritenuta scatta ~2,7 ms più tardi
  (K501 a 131,8 invece di 129,1 ms nel guasto del rail −). Il corto davanti al regolatore +: R550
  **7,80 / 9,52 J** invece di 7,65 / 9,35 J (rete 0 / +10 %, +1,9 %); la bobina di K501 in corto,
  R552 0,48 / 0,55 J invece di 0,47 / 0,54 J. Una parte in più.
- **Il controllo dei relè** lo tiene: la regola T6b vuole la base dell'NPN della ritenuta ≤ 0,45 V con
  V5 a 2,2 V e ogni uscita aperta (0,32 V con R585; la netlist di prima 0,89 V, fallisce).

**Lo standby**, dal secondario di T2 a rete −10 / 0 / +10 %:

| | standby | le sequenze |
|---|---|---|
| oggi (scelto) | 116,1 / 130,1 / 144,2 mW | — |
| 5 V da acceso, tenuto da K501 (un AO3401A, un 2N7002 sul comando di K501, un BAT54, 100 kΩ) | 71,5 / 80,5 / 89,7 mW | tutte uguali a oggi |
| 5 V dal solo frontale | 67,5 / 76,0 / 84,7 mW | allo spegnimento cadono tutte le richieste insieme: K501 a 19,4 invece di 123,1 ms |
| i pull-up dieci volte più alti | 80,3 / 90,3 / 100,4 mW | l'apparecchio non si accende |

## Alternative scartate

- **Il modello di TI coi ritocchi**: esito incerto, e ogni ritocco lo allontana dal modello del
  costruttore.
- **C554 a 470 nF** (nessuna parte in più): la base sulla soglia già a 25 °C, R550 +5,8 %.
- **Lasciare l'innesco com'è**: l'accensione con la rete che torna dipende da un comportamento del
  comparatore che il datasheet non garantisce.
- **Il 5 V da acceso** (quattro parti, −45 / −50 / −55 mW): non scelto ora; è la strada se lo
  standby supera il limite.

## Da riaprire se

- Il pezzo di T2 scelto porta lo standby oltre 0,5 W alla presa: prima il 5 V da acceso, tenuto da
  K501 (la riga sopra), poi si torna all'utente.
- Il prototipo mostra che le uscite del TLV1704 sotto 2,2 V assorbono, o che R585 ritarda la ritenuta
  oltre quello che i guasti del rail reggono.
- L54b3 (la temperatura, il Monte Carlo) porta la base di Q513 all'accensione oltre 0,45 V.
