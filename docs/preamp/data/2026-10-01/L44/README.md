# L44 — il rumore 1/f fuori dalla coppia d'ingresso (2026-10-01)

Report: `../../../reports/2026-10-01-L44-rumore-1f.md`. Decisione: **ADR-057**. Chiude **NC-004**.
**Cifre di modello, non misure.**

Il banco è il blocco di `main` dopo L46b (ADR-056), senza varianti di circuito: cambia solo il
flicker dei bipolari. Ogni variante dà a un **gruppo** di transistor una copia del suo modello
**rinominata** (`LS350_SPECCHIO`, `MMBT5401_VAS`, …) con KF/AF aggiunti, e ripunta le righe Q del
gruppo. Rinominare e non `altermod` per #29: un modello che non esiste fa fallire ngspice, e il
nome dice che il modello è alterato. Il controllo `ctrl` non tocca niente (i suoi `.inc` e
`.subckt` sono byte-identici ai sorgenti) e ridà L46b: `tb_e3_e5_ldr_e5.csv` byte-identico,
`tb_noise_breakdown` alla sesta cifra.

| Percorso | Cosa |
|---|---|
| `script/banco.py` | genera `inc/` e `deck/` per variante. Gruppi: `specchio` (Q121A/B), `cascode` (Q117/118), `vas` (Q122), `pozzi` (Q106, Q125), `vbe` (Q127), `finali` (Q132/133). Varianti: `ctrl`; `<gruppo>_fc<Hz>` e `tutti_fc<Hz>`, angolo 1/f con AF = 1 (KF = 2q·f_c), 100 Hz … 10 MHz; `dati` (KF 5·10⁻¹⁴, AF 1,4: il tipico delle curve), `tetto` (1·10⁻¹³: ADR-057, ora nei modelli), `tetto_x10` |
| `script/esegui.sh` | le corse, 8 in parallelo, in `run/<variante>/<deck>/` (copiato da L46b) |
| `script/sintesi.py` | `sintesi.csv` (E5 peggiore da `tb_e3_e5_ldr`, casi B e D di `tb_noise_breakdown`, dB SPL a 1 m con la formula di NC-028, margine sul tetto di 9,95 µV) e `dispositivi.csv` (densità per dispositivo al jack, nV/√Hz, a 20 / 100 / 1000 Hz, +10 dB, 430 Ω) |
| `deck/<variante>/rumore_dispositivi.cir` | deck nuovo: spettro per dispositivo, blocco B +10 dB, 430 e 2500 Ω, `wrdata` a nomi espliciti (#37) |
| `script/aggiungi_kf.py` | la riga `+ KF=1e-13 AF=1.4` in coda ai quattro modelli copiati byte per byte, e le loro intestazioni, **sui byte** (#39) |
| `script/provenienza_kf.py` | i `.provenance.json` dei cinque modelli |
| `script/commenti_kf.py` | i commenti dei 23 deck che dicevano «solo l'LSK489A ha KF» o «pavimento senza flicker» |
| `script/sabota_flicker.py` | i tre sabotaggi del controllo `[flicker]` di `validate_models.py`: modello senza la riga, MJE col `KF=0` del costruttore, KF raddoppiato. Tutti e tre FAIL, come devono |
| `script/regressione.sh`, `regressione/dopo/` | i 21 deck veloci coi modelli nuovi (copiato da L46b); il «prima» è `../L46b/regressione/dopo` |
| `script/confronta_regressione.py`, `regressione/confronto.csv` | confronto cella per cella: dei 249 CSV cambiano solo i 26 delle analisi di rumore |

Le fonti delle curve stanno in `vendor/` coi PROVENANCE: `bjt_pnp/motorola/2N5087/`,
`bjt_npn/motorola/2N5089/` (non usato per un numero), e
`bjt_pnp/linear_systems/LS350/PROVENANCE-L44-addendum.json` (il databook).

**Per rieseguire** (dalla radice del repo):

```
/usr/bin/python3 docs/preamp/data/2026-10-01/L44/script/banco.py tutte
/bin/zsh docs/preamp/data/2026-10-01/L44/script/esegui.sh <abs>/docs/preamp/data/2026-10-01/L44/deck/lista_cascode_fc100_e_altre_35.txt
/usr/bin/python3 docs/preamp/data/2026-10-01/L44/script/sintesi.py
/bin/zsh docs/preamp/data/2026-10-01/L44/script/regressione.sh dopo
/usr/bin/python3 docs/preamp/data/2026-10-01/L44/script/confronta_regressione.py
```

(Il nome della lista dipende dal numero di varianti: `banco.py` lo stampa.)

**Attenzione rieseguendo dopo L44.** Le corse di `run/` sono state fatte coi modelli di `models/`
**senza** flicker, prima che ADR-057 lo mettesse nei modelli. Rieseguite oggi, `ctrl` usa i modelli
col tetto e ridà `tetto` (E5 5,531 µV), non L46b. Le varianti di gruppo restano giuste per i loro
gruppi (`rinomina()` legge la scheda fino al primo commento, quindi non vede la riga KF in coda, e
scrive la propria), ma i gruppi **non** toccati ora portano il tetto invece di niente.
