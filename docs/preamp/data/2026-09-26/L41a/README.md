# L41a — l'alimentatore: potenza, `VRELAY`, relè di rete, sorvegliante (2026-09-26)

Dati del lotto L41a (NC-036, P9). Decisione: **ADR-048**. Report:
`docs/preamp/reports/2026-09-26-L41a-alimentatore-potenza-sorvegliante.md`. Sorgente:
`circuits/preamp/psu.py` → `circuits/preamp/psu.net`. Le forme d'onda (`*.txt`, ~100 MB a
corsa) **non si committano**: si rifanno correndo i deck.

## Le cartelle

| Cartella | Cosa |
|---|---|
| `scelte/` | i numeri portati all'utente **prima** di decidere: `raddrizzatore.py` (toroidale ipotetico 2×12…15 V, 30/50 VA, rete ±10 % → `raddrizzatore.csv`) e `stima_telaio_l41a.py` (il calore di L30 rifatto con l'architettura decisa) |
| `deck/` | `genera_tb_psu.py` (il banco generato da `psu.net`, con i modelli dichiarati nell'intestazione) e `analizza.py` |
| `rete/` | il deck finale: regime e perdita di rete a rete −10 % / nominale / +10 % |
| `guasti/` | il deck finale: regolatore +, − e di `VRELAY` che cedono con la rete presente; la perdita di rete col rivelatore disattivato |
| `varianti/` | la tenuta di `VRELAY`: 12 V AC + 2200 µF (la partenza, fuori), 12 V AC + 4700 µF (scelta), 15 V AC + 2200 µF |
| `falsi/` | `check_psu_harness.py` fatto fallire: 8 falsi su 8, `esito.txt` |

## Come si rifà

```sh
env/venv/bin/python3 circuits/preamp/psu.py
/usr/bin/python3 docs/preamp/data/2026-09-26/L41a/deck/genera_tb_psu.py --uscita <abs>/rete --nome rete
/usr/bin/python3 docs/preamp/data/2026-09-26/L41a/deck/genera_tb_psu.py --uscita <abs>/guasti --nome guasti
cd <abs>/rete   ; /opt/homebrew/bin/ngspice -b tb_psu_rete.cir   > tb_psu_rete.log 2>&1
cd <abs>/guasti ; /opt/homebrew/bin/ngspice -b tb_psu_guasti.cir > tb_psu_guasti.log 2>&1
/usr/bin/python3 docs/preamp/data/2026-09-26/L41a/deck/analizza.py <abs>/rete
/usr/bin/python3 docs/preamp/data/2026-09-26/L41a/deck/analizza.py <abs>/guasti
/usr/bin/python3 docs/preamp/data/2026-09-26/L41a/falsi/falsi.py circuits/preamp/preamp_audio.net circuits/preamp/psu.net
```

Le varianti: `genera_tb_psu.py ... --t2 15` (secondario di T2 in V AC) e `--cvr 4700u`
(C520 al posto del valore di netlist). Ogni deck gira in pochi minuti.

**Le guardie**:
- ogni log deve avere 0 righe `Error`, `singular`, `Transient op`, `no such`;
- ogni caso rimette **tutte** le alterazioni a valore di netlist (limitations #34). Il log stampa
  `@rr512[resistance]` per caso: 2,2e5 nei guasti dei regolatori, 1e15 solo nelle perdite
  «senza rivelatore».

## I modelli (dichiarati, non del costruttore salvo dove detto)

- **Regolatori**: comportamentali (transconduttanza verso la tensione impostata, limite di
  corrente, dropout, nessuna corrente inversa). **Niente PSRR né rumore**: la quota di ADR-020
  **non** è verificata qui. Il modello TI del TPS7A3301 (SBVM665) funziona in ngspice ed è in
  `vendor/`; quello del TPS7A4701 (SBVM364) carica ma dà un punto di lavoro sbagliato.
- **Comparatore**: comportamentale open-drain, 1 µs, alta impedenza sotto 2 V
  d'alimentazione. Il modello TI del TLV1701 (SBOM859C) non commuta in ngspice.
- **LM4040**: shunt comportamentale a 2,500 V.
- **Trasformatori**: Thevenin del secondario. T1 2×15 V 50 VA, regolazione 8 %; T2 12 V AC
  5 VA, regolazione 20 %. Ipotesi dichiarate, da confermare sui pezzi.
- **Carico**: 265 mA per rail (ADR-042); le bobine a 12 V della scheda audio come resistenze,
  senza induttanza (il datasheet del G6K non la dà, L36).

## Le cifre (analisi.csv)

| Caso | `MUTE_CMD` rilasciato | Rail al rilascio | Tenuta rail 13,5→10,6 V | `VRELAY` dopo lo scatto |
|---|---|---|---|---|
| perdita di rete −10 / nom / +10 % | 14,2 / 14,3 / 14,4 ms (rivelatore) | +15,00 / −15,05 V | 60,3 ms | ≥ 11,4 V per 62,8 / 144,9 / 227,3 ms |
| U501 (+) cede | 9,56 ms | scatto a 13,56 V | 19,35 ms | rete presente |
| U502 (−) cede | 10,14 ms | scatto a −13,52 V | 19,36 ms | rete presente |
| U503 (`VRELAY`) cede aperto | 15,83 ms | scatto a `VRELAY` 11,0 V | — | ≥ 9,6 V (80 %) per 32,9 ms |
| rivelatore guasto + perdita di rete | 72,5–136 ms | 13,56 V | 60 ms | −10 %: 0 ms (doppio guasto, dichiarato) |
