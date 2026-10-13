# L45b — i guasti dei controlli della scheda audio, e P10 (2026-10-13)

Dati del report `docs/preamp/reports/2026-10-13-L45b-fmea-controlli.md` (NC-042). Seconda parte
di L45: i controlli (relè, piloti, commutatori, LED, condensatori d'uscita, firmware), e i guasti del
blocco di L45a rimisurati contro **P10** (ADR-069): il tempo sopra 0,87 V al jack **senza filtro** e
**a vuoto**. Il circuito non cambia.

## Il banco

Il canale di L45a (`../L45a/script/genera_canale.py`, **importato**, non copiato) senza blocchi
guasti; il guasto è in **un** controllo, con lo stesso interruttore di L45a (`CTL`, 0 → 1 a 0,3 s in
10 µs; `SWFC` chiude un corto da 10 mΩ, `SWFO` stacca un terminale). **A vuoto** = le tre righe
`RLD*` (cj 100 k, Singxer 10 k, Stax 50 k) tolte: restano i bleed sul lato del condensatore e sul jack.

| Famiglia | Cosa |
|---|---|
| `ctl` | i guasti dei controlli, a vuoto (`genera_controlli.py controlli`): condensatori d'uscita, C_T, C_IN, bleed, i contatti del mute, del guadagno (i rami di K1/K5 sul blocco B), del trim (la presa della scala), del selettore, l'isolamento fra bobina e contatti (12 V di `VRELAY` sul nodo del contatto, con 10 Ω o 1 kΩ), la 47 Ω in corto col cavo, i latenti del mute (spegnimento e accensione col jack collegato) |
| `ctl_carico` | gli stessi coi carichi di oggi (`--carico`) |
| `lunghe` | i casi che sulle fisse durano più della corsa, fino a 6 s (`genera_controlli.py lunghe`) |
| `vuoto_tr_*` | **ogni** deck di L45a con le tre righe `RLD*` tolte (`genera_controlli.py vuoto FAMIGLIA`), stesse impostazioni (accorciate, gear, il rivelatore ideale `taglio*`) |
| `verifica_carico` | un deck di L45a copiato **così com'è** (`tr_B/Q132_ce`): ridà i numeri di L45a |

## Gli script (`script/`)

- `genera_controlli.py` — i deck (sopra). La tabella `MODI` dice per ogni modo quale riga del canale
  cambia.
- `analizza_p10.py` — `analizza_tr.py` di L45a più **la durata di P10**: per ogni jack `sopra_ms`
  (tempo con |v| > 0,87 V dal guasto, senza filtro), `ultimo_ms`, e la colonna `p10`
  (`entro` / `FUORI` / `FUORI, ancora sopra alla fine`). `--prova` controlla lo strumento su un
  esponenziale (14,9 V, τ 0,517 s: 1468,6 ms attesi e misurati) e su un seno a 997 Hz (328,2 ms).
- `analizza_vuoto.sh` — tutte le analisi di `vuoto_tr_*`, poi `sintesi_p10.py` → `p10_blocco.csv/.md`.
- `tabella_controlli.py` — `fmea_controlli.csv/.md`: un modo di guasto per riga, coi numeri delle
  corse (`analisi_ctl*.csv`, `analisi_rs.csv`, `analisi_latenti.csv`, `analisi_lunghe.csv`) o col
  ragionamento a calcolo.
- `squillo.py` — la 47 Ω in corto col cavo: sovraelongazione e residuo sul `.dat` grezzo.
- `lista_vuoto.py` — la lista unica delle corse di L45a a vuoto (`deck/lista_giro2.txt`), senza i
  modi che in L45a si erano bloccati (corrono nelle loro varianti accorciate o gear).
- `corri.sh`, `uno.sh` — quelli di L45a (xargs -P 8, limitations #58), copiati perché scrivono in
  `run/` accanto a sé.
- `stampa.py` — stampa compatta di un `analisi_*.csv`.

## Rifare

```sh
/usr/bin/python3 <L45b>/script/analizza_p10.py --prova
/usr/bin/python3 <L45b>/script/genera_controlli.py controlli            # e --carico
/usr/bin/python3 <L45b>/script/genera_controlli.py vuoto tr_A tr_F1 ...  # le famiglie di L45a
/usr/bin/python3 <L45b>/script/lista_vuoto.py
/bin/zsh <L45b>/script/corri.sh <L45b>/deck/lista_ctl.txt                # 8 alla volta
/bin/zsh <L45b>/script/corri.sh <L45b>/deck/lista_giro2.txt              # ~560 corse, ~45 min
/bin/zsh <L45b>/script/analizza_vuoto.sh
/usr/bin/python3 <L45b>/script/tabella_controlli.py
```

Gli elenchi `deck/lista_*.txt` portano i percorsi assoluti del worktree di L45b: si rigenerano coi
comandi sopra. `genera_controlli.py controlli MODO...` riscrive `lista_ctl.txt` coi soli modi dati.
Le forme d'onda (`run/**/*.dat`, ~decine di GB) non sono nel repo (`.gitignore`).
