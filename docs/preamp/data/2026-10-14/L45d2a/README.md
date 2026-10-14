# L45d2a — le decisioni sui rimedi dei guasti, riga per riga

Prima metà di L45d2, divisa dall'utente il 2026-10-14 («Prima decidere, poi costruire»). Il
circuito non cambia, e non ci sono corse nuove. Report: `reports/2026-10-14-L45d2a-scelte-rimedi.md`.

| File | Che cosa |
|---|---|
| `decisioni.csv` | 173 righe: le 156 alte e medie della sintesi di L45d1, ciascuna con la scelta del PDF (1–13), la decisione, l'ADR, dove si realizza (L45d2b, L58, accettata, G2, NC-062) e la priorità dopo ADR-071; più le 17 righe basse che decide ADR-078 (`scelta = bassa`) |
| `decisioni.md` | il riassunto per scelta e per destinazione |
| `script/decisioni.py` | lo script (solo stdlib) |

L'ingresso è `../L45d1/fmea_sintesi.csv`, che non viene riscritto. I numeri delle scelte sono quelli
di `../L45d1/scelte_L45d2.pdf`. Il raggruppamento è lo stesso di `../L45d1/script/pdf_scelte.py`:
il prefisso del testo dei rimedi, nello stesso ordine.

## Il controllo

Prima di decidere qualunque cosa lo script riconta la tabella del PDF, scelta per scelta, e si
ferma se un conteggio è diverso (52/6, 10/0, 9/1, 8/0, 8/2, 3/4, 0/10, 0/2, 0/2, 1/0, 1/1, 4/0, 0/32;
156 righe). Poi verifica i conteggi attesi delle decisioni:
- dopo ADR-071, 100 righe alte e 56 medie;
- 4 righe alzate (l'isolamento dei relè di mute);
- 28 guasti del blocco alla diagnosi;
- ogni riga ha una destinazione.

## Rifare

```sh
/usr/bin/python3 -I <D>/script/decisioni.py <D>/../L45d1/fmea_sintesi.csv --prova   # i conteggi del PDF
/usr/bin/python3 -I <D>/script/decisioni.py <D>/../L45d1/fmea_sintesi.csv <D>
```

con `<D>` = `docs/preamp/data/2026-10-14/L45d2a` (percorso assoluto).
