# L54b2 — il temporizzatore sul sorgente: i comparatori, l'innesco della ritenuta, lo standby, la catena al jack (2026-10-28)

**Mandato**: la seconda delle tre parti di L54b (diviso dall'utente, «Tre parti»): i comparatori col
modello del costruttore contro il comportamentale sui casi della sicurezza; i pull-up delle uscite
tenute basse in standby (NC-037); la catena al jack dello spegnimento dal frontale e della perdita
di rete, in dB SPL. Dati `data/2026-10-28/L54b2/` (README). Decisione **ADR-103**.

## Sintesi

- **Il modello di TI del TLV1701** (`models/comparator/tlv1701_ngspice.lib`, generato da
  `genera_tlv1701.py`, ricetta `tb_tlv1701`): da solo torna col datasheet — soglia allo scostamento
  di 0,4 mV, **tpLH 574 / tpHL 460 ns** (SBOS589D 560 / 460), 75 mV a 0,5 mA, 55 µA — e col file di TI
  non toccato nel modo `psa`. Il «DO NOT USE» di L41a aveva una causa: la traduzione degli
  interruttori di PSpice, che con Von < Voff non li inverte (limitations #77).
- **Sul banco dell'alimentatore il modello di TI non passa l'accensione**: fermo a 2,19 V di V5, e
  la variante coi ritocchi numerici dichiarati ancora a 0,21 s dopo sette ritocchi. La scelta
  dell'utente: **«Comportamentale tarato»** — `CMPTA`, il comparatore del banco coi numeri del
  modello di TI.
- **Il tarato contro il comportamentale**, 31 corse con dodici e con diciotto canali: **tutti i
  verdetti uguali**; gli istanti fino a +0,3 ms (il guadagno), +0,8 ms (un jack coi diciotto canali),
  −4,1 ms (la musica dopo un buco), oltre il limite scritto prima: metà dalla resistenza d'uscita
  (150 Ω contro 50, provato), il resto entro un campione.
- **Una ritenuta che scattava all'accensione** (scoperta, non chiesta): con le uscite aperte sotto
  la loro alimentazione minima, all'accensione a freddo col frontale acceso l'apparecchio restava
  spento. Il comportamentale la nascondeva con 0,1 V di margine (limitations #78). La scelta
  dell'utente: **«Resistenza verso il ritorno»**, **R585 33 kΩ** nel sorgente; la base a 0,30 V nel
  caso peggiore; la ritenuta 2,7 ms più tarda, R550 +1,9 %.
- **Lo standby**: la strada che regge (5 V da acceso, tenuti finché K501 è chiuso, quattro parti)
  **71,5 / 80,5 / 89,7 mW** contro 116,1 / 130,1 / 144,2; la scelta dell'utente: **«Lasciare
  com'è»**. NC-037 resta aperta.
- **La catena al jack**: lo spegnimento dal frontale **−55,2 dB SPL** e la perdita di rete **−55,3**
  a rete 0 %; a rete **−10 %** la perdita **+4,4 dB SPL** (i regolatori escono di regolazione 2,4 ms
  prima dello stacco). Tutto sotto la soglia di V2 (~33 dB SPL) e sotto una stanza silenziosa. Le
  cifre del dossier (33,9 / 39,2 nV) erano già superate da L56.
- `run_tests.sh` **14 passed / 0 failed**; `validate_models.py` **69 / 69** (+2: il TLV1701, la
  ricetta e la provenienza).

## 1. Il modello del costruttore

| | TLV1701 (TI, tradotto) | `psa` sul file di TI | `CMPTA` (tarato) | SBOS589D |
|---|---|---|---|---|
| soglia, salita / discesa | −0,32 / −0,46 mV | −0,32 / −0,46 mV | −0,24 / −0,50 mV | ±0,3 tip., ±2,5 max |
| tpLH / tpHL (5 ns) | 574 / 460 ns | — | 581 / 457 ns | 560 / 460 |
| uscita bassa a 0,5 mA | 75 mV | 75 mV | 74 mV | — |
| corrente | 55,0 µA | 55,0 µA | 55,0 µA | — |

Il derivato fedele traduce gli interruttori come `aswitch` di XSPICE (continui come in PSpice, in
tutti e due gli ordini), gli `IF` e gli operatori logici. Nel circuito in cui sta (V5 dietro 1 Ω, il
pull-up da 10 k), con V5 che sale da zero, si ferma a 2,19 V: la finestra d'alimentazione è un `IF`
netto e l'uscita che assorbe la riattraversa. La variante nominata `TLV1701_OC` (provenance) passa la
rampa da sola; sul banco si ferma a 42,8 ms, poi a 0,21 s. Domanda all'utente coi numeri: «Comportamentale
tarato».

Il vendor in `vendor/comparator/ti/TLV1702/` è 0644 benché `PROVENANCE.json` dica 0444: segnalato, non
toccato.

## 2. I casi della sicurezza

Criteri scritti prima (README §2). Sul sorgente di L54b2, tarato contro comportamentale:

- verdetti (`C2`, `C3`, `r41`, `s41`, `musica_TE`, `mus_end`, `k501_end`, `esito`): **31 / 31 uguali**
  coi dodici canali, 31 / 31 coi diciotto; `cf_nodelta` fallisce;
- istanti: fuori dal limite max(0,1 ms; 0,5 %) fino a 1,5× (dodici canali) e 2,1× (diciotto). Il
  guadagno +0,3 ms in `perdita`, `buco20`, `buco200` alle tre reti; il jack +0,2 ms nei sorveglianti
  ciechi e in `guasto`, +0,5–0,8 ms coi diciotto canali nei guasti di K501 e C509; la musica dopo
  `buco20` 537,2 invece di 541,3 ms (la specifica ≥ 500 ms);
- la causa provata: `CMPTA` a 50 Ω riporta il guadagno di `perdita` da 55,7 a 55,6 ms (comportamentale
  55,5). Metà dello scarto è la resistenza d'uscita che scarica i condensatori del temporizzatore;
  l'altra metà è entro il campione da 0,1 ms. Il limite era stato scritto per lo scostamento e il
  ritardo, non per la resistenza d'uscita: non lo si allarga ora, lo si dichiara.

## 3. L'innesco della ritenuta all'accensione

Il datasheet non dice che cosa fanno le uscite sotto 2,2 V. Aperte, AT_F (R581 100 kΩ da V5, C553
330 nF) segue V5 e attraverso R582 porta la base di Q513 oltre la soglia prima che i comparatori si
sveglino: la ritenuta scatta e tiene l'apparecchio spento finché non si spegne il frontale.

| la base di Q513 al massimo, V5 < 2,3 V | |
|---|---|
| comportamentale | 0,50 V (passa per 0,1 V a 25 °C, niente a 60 °C) |
| tarato, uscite vive a 2,2 V | scatta |
| + C554 470 nF | 0,61 V |
| + **R585 33 kΩ** | **0,30 V** |

Con R585 la ritenuta scatta e tiene in ogni guasto provato; K501 +2,7 ms nel guasto del rail −; R550
7,80 / 9,52 J (+1,9 %), R552 0,48 / 0,55 J. Nel sorgente: `psu.py` (il commento verso ADR-103),
`psu.net` (`nomi_reti.txt`: 0 reti cambiate), lo schematico (167 / 167), il caso noto strutturale
48 / 48 (la netlist di prima fallisce), il controllo dei relè con la regola **T6b** (la base ≤ 0,45 V
con V5 a 2,2 V e ogni uscita aperta: 0,32 V; la netlist di prima 0,89 V, fallisce).

## 4. Lo standby

Il consumo da T2 viene soprattutto da R573, R575, R576 (0,5 mA ciascuna a 5 V), R579 (0,23 mA) e da
R524, R537 (0,5 mA). Alimentarle da VRELAY_EN non va (il nodo acceso, diviso dalle uscite basse,
scende sotto il riferimento). Le opzioni sul banco: README §3. Quella che regge, i 5 V da acceso
tenuti finché K501 è chiuso, dà **71,5 / 80,5 / 89,7 mW** con ogni sequenza uguale; l'utente ha scelto
di lasciare lo standby com'è (**116,1 / 130,1 / 144,2 mW**, invariati sul sorgente con R585). Il
criterio di NC-037 resta ≤ 0,35 W di perdita a vuoto di T2 a rete +10 %.

## 5. La catena al jack

Il ponte di L41c accetta ora una corsa sola del temporizzatore a comparatori (`--passata-unica`).
Il jack principale, picco a 1 m:

| | −10 % | 0 % | +10 % | L56 | dossier |
|---|---|---|---|---|---|
| spegnimento dal frontale | −55,2 dB SPL | −55,2 | −55,2 | −58,5 | −35,9 (33,9 nV) |
| perdita di rete | **+4,4** (3,52 µV) | −55,3 (3,63 nV) | −55,2 | −46,7 | −34,7 (39,2 nV) |
| perdita, Δ minimo | +4,4 | −55,4 | −55,2 | −43,0 | −35,0 |

Contro la soglia di V2 (100 µV, ~33 dB SPL) e una stanza silenziosa (25–35 dB(A); un picco contro un
livello pesato A): tutto sotto, il peggiore 29 dB sotto la soglia. **A −10 %** i regolatori escono di
regolazione 2,4 ms prima dello stacco (il rail + −21 mV, il − −49 mV): la frase di ADR-102 «il rail
resta in regolazione fino allo stacco in ogni caso» non vale a −10 %, di qualche decina di mV. Il
dossier va rigenerato (L64): le sue cifre sono di L51b.

## 6. Cosa resta fuori, e dove va

- **L54b3**: la robustezza al banco, il punto 7 del prompt di L54b (sotto, parola per parola), col
  comparatore tarato (`--comparatore tarato`, `tarato22` per il caso peggiore dell'accensione) e con
  la base di Q513 all'accensione fra le cose da tenere sotto 0,45 V a 60 °C (il «Da riaprire se» di
  ADR-103).
- **L58**: la riga della FMEA di R585 (aperta: la ritenuta all'accensione torna; in corto: AT_F a
  terra, la ritenuta non scatta più per un guasto del rail).
- **L64**: il dossier rigenerato, con la catena al jack di questo lotto.

## Per L54b3

Il punto 7 del prompt di L54b (richiesta dell'utente dopo L54a, 2026-10-26), parola per parola:

> 7. **La robustezza del temporizzatore, al banco e non al prototipo** (richiesta dell'utente dopo L54a,
>    2026-10-26: «il prototipo è molto costoso, dobbiamo cercare di accorgerci al banco delle simulazioni
>    dei problemi, il primo prototipo deve essere usabile»; ADR-102 lasciava al prototipo l'immunità ai
>    disturbi). I criteri si scrivono prima delle corse; per ognuno: niente scatto a vuoto
>    dell'accensione, del mute o della ritenuta, e lo scatto quando deve:
>    - **la rete**: cali lenti (brown-out) a −15 / −20 / −30 % per 0,1–2 s; buchi di ½, 1, 3, 10 periodi;
>      una sovratensione +15 %; la rete che torna mentre i rail scendono; tutto alle tre reti;
>    - **i disturbi veloci**: fronti ripidi su `VRELAY_REG` e su V5 (K501 che chiude, i relè della scheda
>      audio che commutano, il carico di `VRELAY` a gradino): la ritenuta a due transistor non si innesca
>      da sola; il suo 1 nF base-emettitore dimensionato coi numeri, non a sentimento;
>    - **i rimbalzi** del frontale e di SW3 con forme di rimbalzo vere (treni di 1–5 ms);
>    - **le tolleranze**: un Monte Carlo sugli RC dei ritardi (resistenze ±1 %, condensatori secondo il
>      dielettrico, ±5 % C0G / ±20 % X7R con la tensione) e sulle soglie e gli offset dei comparatori:
>      ogni tempo nei suoi limiti (il permissivo ≥ 16,9 ms dopo il mute, la musica ≥ 500 ms dopo la
>      rete, K501 ≥ 50 ms dopo il permissivo, il timeout ~2 s, la ritenuta armata), col caso peggiore
>      dichiarato;
>    - **la temperatura** a 0 e 60 °C, coi transistor della ritenuta e i comparatori del costruttore;
>    - al prototipo resta solo ciò che non si simula (i disturbi irradiati, il layout), detto per nome.
>    Se una prova fallisce, il rimedio si porta all'utente coi numeri prima di cambiare il circuito.

Nel sorgente i due 1 nF base-emettitore della ritenuta sono C554 (Q513) e C555 (Q514). «I comparatori
del costruttore» sono, per ADR-103, il tarato `CMPTA`.
