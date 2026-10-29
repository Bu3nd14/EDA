# L54b3b — le tolleranze e la temperatura del temporizzatore (2026-10-28)

Seconda parte di **L54b3** (diviso dall'utente all'inizio di L54b3, «Due parti»; la prima, L54b3a, a
25 °C: la rete, i fronti veloci, i rimbalzi). Il punto 7 del prompt di L54b, le voci «le tolleranze» e
«la temperatura». Decisioni di riferimento **ADR-102**, **ADR-103**, **ADR-104**. `<L>` = questa
cartella. Python di analisi con `/usr/bin/python3 -I`. Le forme d'onda non stanno nel repository: si
rifanno.

## Il banco

`psu/` è il banco di L54b3a copiato, con `carico.txt`. **Senza opzioni nuove i deck di `buco20` e
`guasto` sono quelli di L54b3a riga per riga**, salvo il percorso di `cmpta.lib` (`psu/prova_inerte.sh`).
Le opzioni nuove (intestazione di `genera_tb_psu.py`, solo con `--timer sorgente`), ognuna che scrive
nell'intestazione del deck i valori che usa:

- `--temp <°C>`: `.options temp`. **La seguono** i modelli a giunzione: i BC847 / BC857 / BAT54 di
  Diodes Inc. (XTB, EG, XTI), il BAV199 che sta per il BAS416, l'1N4148, e i modelli generici del banco
  (ponte, Schottky, zener, transistor). **Non la seguono**: i regolatori e il riferimento
  comportamentali, i comparatori (`CMPTAV`), le R e le C. Per questi la temperatura entra dagli
  intervalli di `--toll` (sotto).
- `--toll <file.json>`: un fattore su ogni R / C nominata (il meccanismo di `ANGOLO`), la tensione
  dell'LM4040, e i **diciotto canali** dei comparatori (U513–U515 e U505 / U506 / U508) come `CMPTAV`
  (`psu/cmpta_v.lib`): `CMPTA` con lo scostamento per canale, una corrente d'ingresso su ogni ingresso,
  e l'alimentazione da cui l'uscita è viva (2,0 V `CMPTA`, 2,2 V `CMPTA22`). **Coi valori nominali
  (`psu/toll_nominale.json`) l'unico cambio è che U505 / U506 / U508 diventano tarati come U513–U515**
  (il `tarato18` di L54b2): il riferimento del Monte Carlo è quindi la corsa con `toll_nominale.json`,
  non la serie `n_`.
- `--perdita REF:A[,…]`: una corrente inversa A in parallelo al diodo, solo in inversa (`tanh` della
  tensione inversa su 50 mV), **in più** della perdita del modello: il massimo del datasheet alla
  temperatura, per eccesso (dichiarato).
- `--ritenuta costruttoreA | costruttoreC`: i gruppi di hFE A / C dei due transistor della ritenuta
  (`costruttore` resta il B).

`psu/campioni_mc.py` scrive i campioni (`toll_mcNNN.json` e `campioni.csv` coi parametri normalizzati in
[−1, 1]); `psu/analizza_mc.py` è `analizza_rob.py` coi margini in numeri.

### Le prove sul caso noto (`an_prova.csv`, `lista_prova.txt`)

| prova | atteso | misurato |
|---|---|---|
| `toll_nominale.json`, buco20 | la musica come la serie `n_` (559 ms dopo la rete) | **559,0 ms** |
| R571 × 1,10, buco20 | ~+10 % | 613,2 ms, **+9,7 %** |
| `--perdita D538:1e-6`, spegnimento_l | il permissivo più corto dopo il mute | 39,6 → **25,5 ms** |
| `--temp 60`, accensione | la corsa passa | musica a 1154,3 ms (1149,7 a 25 °C) |

## Le tolleranze (`psu/campioni_mc.py`), uniformi sull'intervallo

| parte | intervallo | da dove |
|---|---|---|
| resistenze | ±1 %, ±100 ppm/°C × \|T − 25\| | a film spesso, dichiarato |
| condensatori C0G | ±5 % | ±30 ppm/°C: < 0,2 % fra 0 e 60 °C, dentro il 5 % |
| condensatori X7R | da 0,8 × (1 − polarizzazione) × 0,93 × 0,97 a 1,2 | ±20 % (il prompt); la polarizzazione a ≤ 5 V su un 1206 da 25 V: 1 µF −15 %, 330 nF −10 %, ≤ 100 nF −5 % (dalle curve dei costruttori, dichiarato); l'invecchiamento −7 % (10⁵ h a −2,5 %/decade); la temperatura −3 % a 0 / 60 °C |
| VREF (LM4040A) | 2,5 V ±0,1 %, ±100 ppm/°C × \|T − 25\| | il massimo del grado A |
| scostamento, per canale | ±3,5 mV + 20 µV/°C × \|T − 25\| | SBOS589D 7.6 (±3,5 mV a 2,2 V, il più largo; ±5,5 mV in tutta la temperatura) |
| corrente d'ingresso, una per tutti | ±15 nA a 25 °C, ±20 nA altrove | SBOS589D 7.6; il segno non è dato |

Le perdite massime dei diodi (`--perdita`), dai datasheet, interpolate in esponenziale fra le due
temperature date (dichiarato):

| diodo | 25 °C | 0 °C | 60 °C | da dove |
|---|---|---|---|---|
| D538 1N4148 (AT_PRT) | 25 nA | 5,5 nA | 210 nA | onsemi 1N914/D: 25 nA a 20 V, 50 µA a 150 °C |
| D535 / D536 / D541 BAS416 | 5 nA | 2,9 nA | 11 nA | Nexperia: 5 nA a 75 V, 80 nA a 150 °C |
| D533 / D534 / D537 BAT54 | 2 µA | 0,4 µA | 19 µA | DS11005: 2 µA a 25 V; ×9,5 da 25 a 60 °C dalla fig. 2 (`L54b3a/modelli.md`) |

## I criteri, scritti prima delle corse

Per ogni campione e ogni angolo: **niente scatto a vuoto** dell'accensione, del mute o della ritenuta,
e **lo scatto quando deve**. I tempi:

1. **Il permissivo ≥ 16,9 ms dopo il mute** (`d_perm_ms`, ADR-045 / C3): spegnimento_l, perdita, guasto.
2. **La musica ≥ 500 ms dopo la rete** dopo un buco di 20 ms (`dmus_ms`, buco20): il «Da riaprire se» di
   ADR-104.
3. **K501 ≥ 50 ms dopo il permissivo** allo spegnimento dal frontale (`k_perm_ms`, ADR-046).
4. **Il timeout e la ritenuta armata**: all'accensione (accensione, fredda) la ritenuta si arma **dopo**
   l'alimentazione buona (`arm_pg_ms` > 0) e non scatta (`ritenuta` 0, la base di Q513 ≤ 0,45 V,
   `bn_max`); con un rail morto all'accensione (accensione_u501) scatta e K501 si apre; con un rail che
   cade in musica (guasto) scatta e K501 si apre.
5. **L'accensione a freddo col frontale acceso** col tarato a 2,2 V (`tarato22` / `VON` 2,2): la base di
   Q513 ≤ 0,45 V anche a 60 °C e negli angoli (il «Da riaprire se» di ADR-103).
6. **La perdita di rete a −10 %**: il calo dei rail allo stacco del jack (`dvp_mv` / `dvm_mv`, L54b2:
   −21 / −49 mV, +4,4 dB SPL contro la soglia di V2 a ~33 dB SPL). Il colpo cresce come il calo:
   +4,4 + 20 log(calo / calo nominale) deve restare sotto 33 dB SPL; vicino al limite si rifà la catena
   al jack di L54b2.

Più: ogni verdetto (mute, musica, K501, ritenuta) come nel caso nominale del suo caso. Il caso peggiore
di ogni tempo si **dichiara**: l'angolo costruito dalla regressione del Monte Carlo, verificato con una
corsa.

Se una prova fallisce, il rimedio si porta all'utente coi numeri prima di cambiare il circuito.

## Gli esiti

Le cartelle sono `seq/<etichetta>/<caso>`; le forme d'onda cancellate dopo l'analisi. Nessuna corsa
finita in errore. **Il ripiego numerico**: a 25 e 60 °C nessuno; **a 0 °C 117 corse su 135** hanno
superato col metodo `gear` il tetto di 300 s di `corri_an.sh` e sono state rifatte col ripiego del banco
(`trap`, `gmin` 1e-8, L56; `ripiego.txt` nella cartella della corsa).

**Il ripiego, confrontato** (`lista_metodo.txt`, `an_metodo.csv`, 2026-10-29). Col metodo `gear` senza
tetto (`psu/num_t0.sh`) le due corse a 0 °C non finivano in 9 ore: fermate, nessun risultato. Il
confronto si è fatto dove `gear` finisce, forzando il ripiego (`--metodo trap8`) a 25 °C:

| | `gear` | ripiego |
|---|---|---|
| la musica dopo il buco, l'angolo peggiore | 566,9 ms | **560,9 ms** |
| l'accensione nominale: la musica / l'armamento | 1209,3 / 2173 ms | 1202,3 / **2008,7 ms** |
| il guasto: il jack, V+ < 10,6 V, il guadagno, K501 | 15,6 / 428,5 / 52,9 / 129,1 ms | 15,6 / 428,5 / 51,7 / 127,0 ms |

e a 0 °C l'angolo della musica col passo di 5 µs: **537,7 ms come a 20 µs**. **Il ripiego accorcia i
ritardi dei nodi da megaohm**: `gmin` 1e-8 mette 100 MΩ su ogni giunzione, una perdita in più su AT_T2S
(2,7 MΩ) e AT_PGT (1,1 MΩ). Le cifre a 0 °C stanno quindi per difetto nel verso dei limiti (la musica
dopo il buco ~6 ms più tarda col metodo normale); l'armamento anticipa, ma il suo margine sull'
alimentazione buona a 0 °C resta ≥ 723 ms. Nessun verdetto del lotto cambia (limitations #81).

### Il Monte Carlo a 25 °C (`an_mc25.csv`, `mc25/`, 700 corse; prima di ADR-105)

100 campioni (seme 54, i dieci condensatori in C0G) su accensione, spegnimento_l, buco20, perdita,
guasto, accensione_u501, fredda, più il nominale: **nessun verdetto diverso dal nominale**.

| margine | nominale | il campione peggiore | limite |
|---|---|---|---|
| il permissivo dopo il mute | 39,6 ms | 37,6 ms | ≥ 16,9 |
| la musica dopo un buco di 20 ms | 559 ms | 532 ms | ≥ 500 |
| K501 dopo il permissivo | 75,8 ms | 71,4 ms | ≥ 50 |
| l'armamento dopo l'alimentazione buona, accensione / a freddo | 1626 / 1047 ms | 1497 / 926 ms | > 0 |
| la base di Q513, a freddo col frontale acceso | 0,282 V | 0,287 V | ≤ 0,45 |

**La regressione** (`psu/regressione.py`, `mc25/regressione.txt`): lineare sui 53 parametri normalizzati,
residui da 3·10⁻⁵ V a 0,75 ms. I pesi maggiori: la musica dopo il buco C548 (+26 ms per il suo ±5 %),
R571, la corrente d'ingresso; il permissivo C550, C528; K501 C551, C529; l'armamento C552 (+109 ms),
la corrente d'ingresso (+47 ms), R580. **Gli angoli** (`psu/angoli.sh`, `psu/prepara_angoli.sh`): ogni
parametro all'estremo che peggiora il margine, coi valori degli intervalli della temperatura e del
dielettrico (`angoli/`).

### Gli angoli e la temperatura prima di ADR-105 (`an_angoli.csv`, `an_temp.csv`, `an_diag.csv`)

`psu/verdetti_angoli.py`: 48 corse su 138 falliscono.

- **A 60 °C la ritenuta scatta all'accensione a freddo col frontale acceso**, anche coi valori nominali
  (la lista della sicurezza a 60 °C: la base a 0,88 V prima dell'evento in ogni caso). La diagnosi
  (`lista_diag.txt`): senza perdite aggiunte 0,372 V; con quella di D538 e dei BAS416 0,372 V; con la
  perdita massima dei tre BAT54 **0,883 V**; le perdite di 60 °C a 25 °C 0,538 V senza scatto; coi BAT54
  generici 0,293 V. È D534: dal rivelatore di rete (AT_MD, 100 kΩ a V5) nel nodo d'innesco (AT_F).
- **A 0 °C** la musica dopo il buco nell'angolo 491 ms (C0G), 477 ms (X7R sui piccoli).
- **In X7R sui piccoli** K501 42,9–48,3 ms dopo il permissivo.

**Le prove dei rimedi** (`lista_rimedio_prova*.txt`, sul banco con `--bassa-perdita` e `--valore`): i
tre BAT54 in BAS416 tolgono lo scatto (0,27 V) ma la musica dopo il buco va a 461 ms a 60 °C (D533 lascia
AT_PG più alto); il solo D534 in BAS416: 0,271 V, 0,309 V nell'angolo col comparatore da 2,2 V, la musica
574,5 ms a 60 °C; R571 1,1 MΩ: l'angolo a 0 °C 537,7 ms, la musica all'accensione 1209,3 contro 1149,7 ms.
**Le scelte dell'utente**: «Solo D534 a bassa perdita», «R571 a 1,1 MΩ», «Tutti C0G» (ADR-105).

### Sul sorgente di ADR-105 (`an_v_*.csv`, `confronta_v_*.txt`)

- **I 69 angoli** a 0 / 25 / 60 °C, alle tre reti, col comparatore da 2,0 e 2,2 V: **tutti passano**.
  Il minimo di ogni margine: la musica dopo il buco **537,1 ms** (0 °C, +10 %), il permissivo 31,4 ms
  (60 °C), K501 63,8 ms (0 °C), l'armamento 723,1 ms dopo l'alimentazione buona (a freddo, 0 °C), la
  base 0,311 V (0 °C, 2,2 V); col rail morto all'accensione la ritenuta e K501 aperto, l'armamento fino
  a 2514,7 ms (60 °C). La perdita di rete a −10 % nell'angolo del jack più tardo: il rail − cala di
  ≤ 17,3 mV allo stacco (contro 14,8 a 25 °C nello stesso angolo): il colpo resta nell'ordine dei
  +4,4 dB SPL di L54b2, lontano dalla soglia di V2 (~33 dB SPL).
- **La lista della sicurezza a 25 °C** contro la serie `n_` di L54b3a: i verdetti e gli istanti di
  sicurezza identici (i guasti entro 0,12 del limite), la sola musica +54–60 ms (R571).
- **A 0 e 60 °C** la stessa lista: **gli stessi verdetti** in tutti i 31 casi; gli istanti si spostano di
  qualche ms (a 60 °C il guadagno ~5 ms prima, il jack fino a +4,3 ms in un guasto). **A 60 °C la musica
  dopo il rilascio del tasto del mute a 7,7 ms invece di 18,1**: la perdita massima di D537 carica il
  filtro dei rimbalzi su AT_MRQ; i treni di rimbalzo veri (1–5 ms, L54b3a) restano coperti.
- **I gruppi di hFE A e C** dei due transistor della ritenuta, a 25 e 60 °C: come il B (nessuno scatto
  all'accensione, la base ≤ 0,30 V col comparatore da 2,2 V; lo scatto nel guasto, con la ritenuta dal
  frontale, col rail morto all'accensione).
- **Il controllo numerico**: l'angolo della musica a 60 °C col passo di 5 µs identico (579,4 ms).

## Al prototipo resta (detto per nome)

Come L54b3a: i disturbi irradiati e quelli condotti sopra le decine di kHz; il layout, cioè le perdite
superficiali della scheda sui nodi da megaohm e ora anche su AT_F / AT_MD (la causa del guasto di
questo lotto, a 60 °C, era una perdita di 19 µA); l'inrush del toroide. In più: la perdita vera dei
pezzi comprati (il banco ha usato il massimo del datasheet, per eccesso, sommato a quella del modello).

## Rifare

```sh
/usr/bin/python3 -I <L>/psu/campioni_mc.py --n 100 --seme 54 --uscita <L>/mc25
/usr/bin/python3 -I <L>/psu/lista_mc.py m25_ accensione,spegnimento_l,buco20,perdita,guasto,accensione_u501,fredda "<opzioni>" <L>/mc25/toll_mc0*.json <L>/psu/toll_nominale.json > <L>/lista_mc25.txt
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_mc25.txt 6      # ~45 min per 350 corse
/usr/bin/python3 -I <L>/psu/analizza_mc.py --te=3.0 <L>/an_mc25.csv <L>/seq/m25_*/*
/usr/bin/python3 -I <L>/psu/riassunto_mc.py <L>/an_mc25.csv m25_
/bin/zsh <L>/psu/prepara_angoli.sh
/usr/bin/python3 -I <L>/psu/lista_angoli.py <L>/mc25 c0g 0,25,60 v_ > <L>/lista_v_angoli.txt
/usr/bin/python3 -I <L>/psu/verdetti_angoli.py <L>/an_v_angoli.csv
/bin/zsh <L>/psu/confronta_serie.sh v_          # e v_t0_, v_t60_
```
Le liste prima di ADR-105 (`lista_seconda.txt`, `lista_diag.txt`, `lista_rimedio_prova*.txt`) si rifanno
con la netlist del commit precedente a ADR-105 di questo ramo; quelle dopo sono `lista_verifica.txt`.
