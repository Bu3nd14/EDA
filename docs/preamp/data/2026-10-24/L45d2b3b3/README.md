# L45d2b3b3 — la sintesi della FMEA della scheda audio dopo i rimedi (2026-10-24)

L'ultima parte di **L45d2b3** (NC-042). Report `../../../reports/2026-10-24-L45d2b3b3-sintesi-fmea.md`.
Decisione **ADR-100**; **NC-042 chiusa**; NC-072 avanza. Il circuito non cambia. `<L>` = questa
cartella, `<R>` = `docs/preamp/data`. Python con `/usr/bin/python3 -I`, solo stdlib.

## I file

| File | Che cosa |
|---|---|
| **`fmea_dopo.csv`** | **la FMEA dopo i rimedi**: 539 righe — le 469 delle quattro tabelle di L45 (`<R>/2026-10-14/L45d1/fmea_sintesi.csv`) con la decisione di L45d2a, e 70 righe nuove delle parti aggiunte dopo L45 —, le colonne prima e dopo di ADR-070, lo stato (dove va la riga) e la fonte di ogni cifra |
| `fmea_dopo.md` | la stessa, leggibile: i conteggi prima / dopo, le destinazioni, le righe alte e medie |
| `p10_stax_nuove.csv` | la Stax sui modi delle cinque parti di ADR-099 (R190, R191, R192, Q193, R194), A e F2, C nominale e +5 %: 44 corse |
| `p10_stax_controllo.csv` | il caso noto della Stax: tre casi di `<R>/2026-10-23/L45d2b3b2b2/stax_lunghi.csv` |

## Gli script (`script/`)

| Script | Che cosa |
|---|---|
| `regole.py` | le regole di ADR-070 / ADR-071 per le colonne dopo il rimedio; la matrice, le classi e i tassi sono quelli di `<R>/2026-10-14/L45d1/script/` (`motore.py`, `tipi.py`), importati |
| `verifica.py` | **le regole sul caso noto, prima dei numeri nuovi**: dalle righe pubblicate ridanno la priorità delle 469 righe di L45d1, la priorità dopo ADR-071 delle 173 di L45d2a, la gravità delle 112 del blocco e FIT e probabilità delle quattro tabelle; `--sabota` (matrice, obiettivo a 10 mV, tassi × 3) le deve far cambiare |
| `genera_stax_nuove.py` | i deck della Stax: il banco di `genera_stax_lunghi.py` di L45d2b3b2b2 (e con lui L45d2b3b1, L60d2, L60c2, L60c1, L45a); prima tre deck del caso noto, poi i 44 dei modi nuovi; rifiuta un blocco o una copia guasta senza R160 e le parti di ADR-099 |
| `corri.sh`, `uno.sh` | copiati da L45d2b3b2b2 |
| `dopo.py` | le colonne dopo il rimedio, riga per riga (le regole nella sua intestazione); rifiuta se un conteggio noto non torna (469, 173, 97, 112, 15 + 11, 121, 44) |
| `sintesi_dopo.py` | `fmea_dopo.md` |

## Le regole, in breve (l'intestazione di `dopo.py` le ha tutte)

- **Il blocco** (le righe di L45a e le parti nuove del blocco): il calore e il jack dall'ultimo banco
  che ha corso il modo — il sorgente con ADR-099 (`sintesi_sorg.csv`, il VAS anche `sintesi_sorgt60.csv`,
  i corti dei finali `dissipatore.csv`), poi il blocco di ADR-097, poi quello di L45d2b3b1 —; la Stax
  dall'ultima corsa del caso. Gravità 5 se una parte resta oltre i limiti, 4 se la Stax supera 150 ms,
  poi le soglie di ADR-070 sul picco. Sulla principale e sulla fissa 1 P10 non ha durata (ADR-081): un
  blocco al rail è gravità 3, «conta sulla protezione a valle», scritto nella riga.
- **P e R** invariate per le righe che c'erano (stessa parte, stesse istanze, stesso meccanismo), salvo
  J1 a un pin (ADR-083: latente). Per le righe nuove P dai tassi di `tipi.py` (8 istanze nel blocco), R
  dal jack (blocco: > 0,87 V → 2, altrimenti 3; `verifica.py` la trova uguale alla regola di L45a su 106
  delle 112 righe) o da ciò che il banco mostra (alimentatore).
- **Le righe non rifatte** (accettate, alla diagnosi, a G2, le basse di L45b / L45c che nessun rimedio
  tocca: 275 «invariata») tengono le colonne di prima, con la ragione nello stato.
- **A calcolo** (9 righe, `CALCOLO` nell'effetto): i modi dell'alimentatore che nessun banco ha corso
  (R550 / R551, C507 / C508 aperti e in corto, R552 in corto, C536 aperto, D513 / D514 aperti).

## Gli esiti

- **Il caso noto**: tutte le righe uguali al pubblicato; col sabotaggio 506 diverse. La Stax: i tre casi
  di L45d2b3b2b2 ridanno 86,4 / 124,5 / 113,7 ms, e deck e copia guasta sono quelli di allora salvo il
  titolo e il percorso.
- **La Stax delle parti di ADR-099**: Q193 in corto C-E, R192 aperta, R194 aperta portano il blocco al
  rail, **115,5–124,0 ms** (C +5 %); gli altri otto modi 0 ms.
- **La FMEA**: 539 righe, **26 alte** (100 prima, sulle tabelle), **71 medie**, 441 basse, 1 esclusa
  (K3, ADR-085). Le alte: 11 accettate (ADR-073, 10; ADR-097, 1), 8 alla diagnosi (il mute che non si
  inserisce, ADR-076), 4 alla scelta della parte (NC-073: C509, C510, la bobina di K501; NC-075: C145),
  1 a G2 (F501), 2 nuove (R550 / R551 in corto, calcolo: il regolatore a 135,9 / 137,2 °C a rete +10 %)
  → NC-072 (ADR-100).

## Rifare

```sh
/usr/bin/python3 -I <L>/script/verifica.py                       # tutte uguali
/usr/bin/python3 -I <L>/script/verifica.py --sabota              # 506 diverse, exit 1
/usr/bin/python3 -I <L>/script/genera_stax_nuove.py
/bin/zsh <L>/script/corri.sh <L>/deck/lista_stax_controllo.txt 3
/usr/bin/python3 -I <R>/2026-10-13/L45b/script/analizza_p10.py <L>/p10_stax_controllo.csv <L>/run/stax_controllo/*/
/bin/zsh <L>/script/corri.sh <L>/deck/lista_stax_nuove.txt 3
/usr/bin/python3 -I <R>/2026-10-13/L45b/script/analizza_p10.py <L>/p10_stax_nuove.csv <L>/run/stax_nuove/*/
/usr/bin/python3 -I <L>/script/dopo.py
/usr/bin/python3 -I <L>/script/sintesi_dopo.py
```

`run/` (le corse, ~1,8 GB) non sta nel repository: si rifà, ~3 s a corsa.
