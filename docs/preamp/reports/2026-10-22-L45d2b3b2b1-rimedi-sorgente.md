# L45d2b3b2b1 — i rimedi del calore nel sorgente (2026-10-22)

Lotto di **NC-042** (prima di G1). Prima parte di L45d2b3b2b, divisa dall'utente all'inizio: **«Due
parti»** (qui il sorgente, l'impronta, le netlist, i disegni, la regressione, V1 e P7; il calore dei
guasti, la Stax e il riposo a caldo in **L45d2b3b2b2**). Applica **ADR-099**, nessuna decisione nuova.
Dati: `data/2026-10-22/L45d2b3b2b1/` (README).

## Che cosa è entrato nel circuito

Nelle otto istanze di `gain_block()`:

- l'aiuto dello specchio (Q148) va al rail negativo attraverso **R190, 10 kΩ**;
- il riferimento è **R101 + R191, due 3,40 kΩ** in serie;
- il VAS ha **R123 33 Ω + R192 22 Ω** e il limitatore **Q193** (MMBT5401) sul 33 Ω;
- la sorgente di coda (Q106) va al nodo dei source attraverso **R194, 1 kΩ, ≥ 0,5 W a 60 °C**;
- i sedici finali hanno il **dissipatore Ohmite WA-T220-101E**, in un'impronta nuova.

**Il blocco generato è la variante misurata in L45d2b3b2a (rv2) riga per riga**, a meno delle sigle:
le cifre del banco del calore valgono per lui. Le rimisura comunque L45d2b3b2b2, come chiede ADR-099.

## Due cose trovate per strada

**Le sigle nuove sulle parti del canale.** Col contatore del blocco le cinque parti avrebbero portato il
blocco A fino a 163 e il B fino a 264, dove il canale ha già le sue: R161 la 47 Ω dell'uscita fissa, R261
quella dell'uscita principale. SKiDL ha rinominato i doppioni (`R161_1`) **senza un errore**: se ne è
accorto il confronto delle parti fra le due netlist. Le parti nuove ora partono da base + 90 su ogni
istanza (R190…R194, R290…, R590…), un intervallo libero ovunque; il disegno della scheda lo sa.

**I piedini dei transistor e le piazzole.** Il simbolo dei transistor che usa tutto il progetto chiama i
piedini «B», «C», «E»; le impronte KiCad dei transistor hanno piazzole «1», «2», «3». Così come sono, al
layout nessun transistor si collegherebbe alle sue piazzole. Non tocca la simulazione né i disegni, e non
è di questo lotto: va risolto prima del layout (G2). L'impronta nuova del finale ha già le piazzole
chiamate B / C / E, e i due piedini del dissipatore sono «C»: al potenziale del collettore per
costruzione.

## Le verifiche

| | Esito |
|---|---|
| La netlist | 578 → **618 parti**; cambia solo il voluto; due reti hanno cambiato nome a parità di piedini (`L_ATT_W` → `BL_IN`, `BR_IN` → `R_ATT_W`), dichiarate nei disegni |
| I tre disegni | rigenerati, ognuno uguale alla sua netlist in entrambe le direzioni |
| La regressione (21 deck) | 21 su 21 a buon fine; contro la variante misurata, 17 deck su 18 entro un millesimo, P7 entro lo 0,12 % sulle potenze |
| **V1**, il margine di fase minimo | 43,11 → **43,64°** (blocco A), 47,18 → 47,57° (blocco B), invariato o meglio ovunque |
| **P7** (60 °C d'aria) | nessuna parte fuori. Il finale PNP 0,52 → 0,40 W: **85 °C senza dissipatore, 70 °C con**; l'aiuto dello specchio 63 °C; le parti nuove al più 0,024 W |
| `run_tests.sh` | **15 / 0** |

Due deck canonici corretti: P7 calcolava la potenza di R123 con 56 Ω scritto a mano (ora 33, e misura
anche le parti nuove); un deck del punto di lavoro leggeva la tensione della coda sul nodo dei source,
che ora sta dopo la 1 kΩ.

## Per la seconda parte (L45d2b3b2b2)

Il calore dei quindici e dei modi delle parti nuove sul blocco del sorgente (deve ridare
`sintesi_rv2.csv` di L45d2b3b2a); la Stax dei casi oltre 100 ms (ADR-098); la corrente di riposo e V4 a
caldo col metodo di L56, ora che il finale accoppiato al moltiplicatore ha un dissipatore; i «Da riaprire
se» di ADR-099 e ADR-097. Le sigle del banco cambiano: R161 → R190, R162 → R191, R167 → R192, Q168 →
Q193, R169 → R194.
