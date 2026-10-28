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
