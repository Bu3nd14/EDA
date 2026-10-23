# L45d2b3b2b2 — il calore sul blocco del sorgente (2026-10-23)

Seconda parte di **L45d2b3b2b** (divisa dall'utente in L45d2b3b2b1, «Due parti»: b1 il sorgente, **b2 il
calore**). Report `../../../reports/2026-10-23-L45d2b3b2b2-calore-sorgente.md`. Verifica **ADR-099** sul
blocco generato da `circuits/preamp/gain_block.py`; NC-042 avanza. **Il circuito non cambia.** `<L>` =
questa cartella. Python con `/usr/bin/python3 -I`.

## Le sigle (limitations #22)

| banco di L45d2b3b2a (rv2) | R161 | R162 | R167 | Q168 | R169 |
|---|---|---|---|---|---|
| sorgente (base + 90) | R190 | R191 | R192 | Q193 | R194 |

`confronta_rv2.py` e `nuove_max.py` hanno la mappa. Le colonne `P_r161_W` / `P_r162_W` di `calore_*.csv`
sono una lista fissa di `analizza_calore.py` (le parti del limitatore di L62b): su rv2 erano le due parti
nuove del banco, sul sorgente restano vuote, e si mettono da parte (dichiarato in `confronta_rv2.py`).

## Il calore dei quindici e delle parti nuove (`sintesi_sorg.csv`, `sintesi_sorgt60.csv`)

`script/genera.py` importa `genera.py` di L45d2b3b2a e aggiunge la variante **`sorg`**: il blocco di
`spice/preamp/` byte per byte (rifiutato altrimenti), le copie guaste rifiutate senza R150…R153, R160 e
le cinque parti nuove. rif + i quindici + gli 11 modi delle parti nuove nelle cinque posizioni: 135 deck,
135 rc 0.

| Verifica | Esito |
|---|---|
| contro rv2 (`confronta_rv2.py`) | **il calore: 4320 celle, 0 diverse** oltre 1e-3; il jack: 211 livelli sopra 0 dB SPL con scarto 0,0 dB, 485 ampiezze sopra 1 µV entro lo 0,25 %, 140 tempi del massimo (sopra 1 mV) entro 0,1 ms; 1189 celle sotto le soglie (il residuo numerico: a riposo il jack a −62 contro −105 dB SPL, 1,8 nV contro 13 pV) |
| oltre i limiti | **2 su 15**, i corti dei finali (160 / 149 °C nudi); il VAS **123 °C** (D102 / D103 aperti, Q125 in corto), **124 °C** con R126 in corto; i modi delle parti nuove al più 87 °C |
| coi dispositivi a 60 °C (`caldo.py`, 35 deck) | il VAS **119 °C** nei quattro guasti; contro `rv2t60`: 1120 celle, 0 diverse |
| le parti nuove (`nuove_max.py`) | uguali al banco: R194 **0,236 W** (R107 in corto: ≥ 0,5 W in distinta), R190 0,089 W, R191 0,054 W, R192 0,009 W, Q193 0,021 W e 69 °C |
| il dissipatore (`dissipatore.py`) | uguale al banco: i corti dei finali **99 / 95 °C** col WA-T220-101E (160 / 149 nudi), riposo 67 °C, P7 69 / 70 °C |

## La Stax dei casi oltre 100 ms (`stax_lunghi.csv`, `p10_stax_lunghi.csv`)

`script/genera_stax_lunghi.py`: gli stessi 121 casi di L45d2b3b1 con le loro impostazioni (gear e durata;
il caso che L45d2b3b1 aveva rifatto in gear parte in gear), le copie guaste rifiutate senza R160 e le
cinque parti nuove. 121 rc 0, tutti `ok`.

- **Nessuno oltre 150 ms, nessuno oltre 125 ms**; il più lungo 124,5 ms (JQ110B, A, C +5 %).
- **D102 / D103 aperti 145,8 → 91,5 ms** (C nominale 141,7 → 86,4): il limite del VAS, come ADR-098
  prevedeva («un rimedio per il loro calore può accorciare anche la Stax»).
- 19 casi più corti di oltre 1 ms (Q121A, R119: ~102–124 → 0 ms; Q106 in corto 102–124 → 86–90 ms), 6 più
  lunghi: il finale PNP in corto +6,6…6,9 ms (al più 119,4 ms), R107 in corto sulla fissa 2 +9,3…9,8 ms
  (al più 119,6 ms); gli altri 96 entro 1 ms.

## Il riposo e V4 a caldo (`riposo.csv`, `tj/`, `sintesi_caldo.csv`)

Il metodo di L56 (`script/v4caldo.py`, copia di `caldo.py` di L60d1, con `genera_imd.py` = `genera.py` di
L46b): ogni giunzione alla sua Tj, iterata fino al passo 4, aria 27 / 57 °C. Le spec: `sorg--sot223` (la
base, il modello termico di L60d1), `--diss` (i finali a 24,5 °C/W: 2,5 + 2 d'interfaccia, ipotesi, + 20),
`--molt` (il moltiplicatore Q127 al case del finale NPN: l'accoppiamento in rame **perfetto** di ADR-034,
un limite superiore), e tutti e due. La VAS sul rame o sulla piazzola minima dà lo stesso numero: `--sot223`
fissa il VAS e il suo carico a 125 °C/W.

**Un ostacolo della convergenza**: il passo 2 di `diss--molt` (aria 27) falliva gmin e source stepping,
e il transient op cadeva sul punto spento (VPF 0,07 V), rifiutato da `leggi_op`; `option gminsteps=40`
non bastava. Ogni `op` dal passo 2 parte ora dal punto del passo prima (`.nodeset`), su tutte le spec;
nessun log con «Transient op started».

| I_q dei finali, mA (ADR-042: ~20,3) | nudi | dissipatore | nudi + accoppiati | dissipatore + accoppiati |
|---|---|---|---|---|
| uniforme 27 °C | 20,51 | 20,51 | 20,51 | 20,51 |
| aria 27 °C | 22,71 | 21,06 (−7,3 %) | 21,84 (−3,8 %) | 21,19 (−6,7 %) |
| aria 57 °C | 24,23 (+19,4 % su 20,3) | 22,48 (+10,7 %) | 23,20 | 22,52 (+10,9 %) |

- A riposo uniforme 27 °C il VAS 10,715 mA, i finali 20,45 / 20,56 mA, la continua d'uscita −2,88 mV:
  quelli di ADR-099 (il «Da riaprire se» di ADR-097 non scatta).
- Il limitatore Q193 a riposo: 0,06 / 0,7 / 1,3 µA (uniforme 27, 57, aria 57) contro ~83 µA di base del VAS.
- **V4 a caldo** (`sintesi_caldo.csv`, 40 deck rc 0): in tutte e quattro le spec **0 casi su 12 fuori** a
  20 kHz, margine peggiore **2,7 dB** (aria 57 °C; 3,0 dB a 27), THD al più 0,000726 % a 0,2 V e 0,00735 %
  a 2 V; IMD CCIF **−131,7 dB** (margine 21,7 dB); il gradino della coda oltre la scansione (> +23,6 %).
  Contro `l60d1--sot223` (L60d1, `sintesi_caldo.csv`, prima di ADR-097 e ADR-099): margine 2,7 / 2,7 dB a
  57 °C (3,1 → 3,0 a 27), THD 0,000722 → 0,000725 %, IMD −131,8 → −131,7 dB. Il dissipatore e
  l'accoppiamento non cambiano V4 di più di 0,000001 %.

## Rifare

```sh
/usr/bin/python3 -I <L>/script/genera.py sorg
/bin/zsh <L>/script/corri.sh <L>/deck/lista_sorg.txt 6
/usr/bin/python3 -I <L>/script/analizza.py sorg
/usr/bin/python3 -I <L>/script/sintesi.py sorg
/usr/bin/python3 -I <L>/script/confronta_rv2.py
/usr/bin/python3 -I <L>/script/nuove_max.py sorg
/usr/bin/python3 -I <L>/script/caldo.py sorg 60 D102_ap D103_ap Q125_ce R126_cc Q133_ce Q132_ce
/bin/zsh <L>/script/corri.sh <L>/deck/lista_sorgt60.txt 6
/usr/bin/python3 -I <L>/script/analizza.py sorgt60
/usr/bin/python3 -I <L>/script/sintesi.py sorgt60
/usr/bin/python3 -I <L>/script/confronta_rv2.py sorgt60 rv2t60
/usr/bin/python3 -I <L>/script/dissipatore.py
/usr/bin/python3 -I <L>/script/genera_stax_lunghi.py
/bin/zsh <L>/script/corri.sh <L>/deck/lista_stax_lunghi.txt 3
/usr/bin/python3 -I docs/preamp/data/2026-10-13/L45b/script/analizza_p10.py <L>/p10_stax_lunghi.csv <L>/run/stax_lunghi/*/
/usr/bin/python3 -I <L>/script/confronta_lunghi.py
/usr/bin/python3 -I <L>/script/v4caldo.py op sorg--sot223 sorg--sot223--diss sorg--sot223--molt sorg--sot223--diss--molt
/bin/zsh <L>/script/esegui.sh <L>/deck/lista_op.txt        # poi p2, p3, p4 allo stesso modo, poi deck4
/usr/bin/python3 -I <L>/script/riposo.py sorg--sot223 sorg--sot223--diss sorg--sot223--molt sorg--sot223--diss--molt
/usr/bin/python3 -I <L>/script/leggi_four.py sorg--sot223 sorg--sot223--diss sorg--sot223--molt sorg--sot223--diss--molt
/usr/bin/python3 -I <L>/script/sintesi_caldo.py sorg--sot223 sorg--sot223--diss sorg--sot223--molt sorg--sot223--diss--molt
```

`run/` (le corse) non sta nel repository (`.gitignore`): si rifà.
