# L45d1 — il riporto delle tabelle dei guasti alla forma di ADR-070 (2026-10-14)

Prima parte di **L45d** (scelta dell'utente all'inizio del lotto, «Due parti»: L45d1 il riporto,
**L45d2** la decisione sui rimedi). Report `../../../reports/2026-10-14-L45d1-riporto-fmea.md`.
Nessuna corsa nuova, nessun cambiamento al circuito: ogni colonna viene dai CSV già pubblicati di
L45a, L45b e L45c1.

`<D>` = questa cartella, `<R>` = `docs/preamp/data`.

## I file

| File | Che cosa |
|---|---|
| `fmea_blocco_adr070.csv/.md` | L45a, il blocco di guadagno: 112 modi |
| `fmea_controlli_adr070.csv/.md` | L45b, i controlli: 78 righe, 64 classificate, 14 rimandi |
| `fmea_rail_adr070.csv/.md` | L45c1, i rail audio: 82 righe, 78 classificate, 4 riferimenti |
| `fmea_sintesi.csv/.md` | le quattro tabelle in una (L45c2 letta così com'è): il conteggio, i rimedi candidati, le righe ad alta e media priorità |
| `tassi/fonti.md` | i tipi nuovi e le loro fonti |

## Gli script (`script/`, solo stdlib, `/usr/bin/python3`)

| Script | Che cosa |
|---|---|
| `motore.py` | le regole di ADR-070 di `tabella_l45c2.py`, tolte da lì **senza cambiarle**; in più le istanze (`MOLT`) e le frazioni `a+b`, `a/N` |
| `verifica_l45c2.py` | **lo strumento su un caso noto**: ricalcola le colonne di ADR-070 di `L45c2/fmea_comando.csv` dalle sue stesse righe; tutte uguali, e con `--sabota` (l'obiettivo a 10 mV) 53 diverse |
| `tipi.py` | i tassi: quelli di L45c2 letti da lì, più i tipi nuovi |
| `classi_l45c1.py`, `riporto_l45c1.py` | L45c1: la tabella pubblicata, le colonne aggiunte; rifiuta se una colonna pubblicata cambia |
| `classi_l45a.py`, `riporto_l45a.py` | L45a: i picchi e il calore di `L45a/fmea_blocco.csv`, il verdetto P10 di `L45b/p10_blocco.csv`; rifiuta se i conti di L45b (544 / 257 / 58) o di L45a (112 modi, 26 col calore) non tornano |
| `classi_l45b.py`, `riporto_l45b.py` | L45b: i numeri riletti dal testo di `L45b/fmea_controlli.csv`; `--prova` controlla il lettore su 14 celle note |
| `sintesi.py` | la sintesi |

## Rifare

```sh
/usr/bin/python3 <D>/script/verifica_l45c2.py <R>/2026-10-14/L45c2              # tutte uguali
/usr/bin/python3 <D>/script/verifica_l45c2.py <R>/2026-10-14/L45c2 --sabota     # 53 diverse, exit 1
/usr/bin/python3 <D>/script/riporto_l45b.py --prova                             # 14 celle, 0 sbagliate
/usr/bin/python3 <D>/script/riporto_l45c1.py <R>/2026-10-13/L45c1 <D>
/usr/bin/python3 <D>/script/riporto_l45a.py <R>/2026-10-13 <D>
/usr/bin/python3 <D>/script/riporto_l45b.py <R>/2026-10-13/L45b <D>
/usr/bin/python3 <D>/script/sintesi.py <D> <R>/2026-10-14/L45c2
```
