# L54b3a — la robustezza del temporizzatore al banco: la rete sporca, i fronti veloci, i rimbalzi (2026-10-28)

Prima parte di **L54b3** (diviso dall'utente all'inizio, «Due parti»: questa la rete, i fronti veloci
contro la ritenuta, i rimbalzi, a 25 °C; la seconda le tolleranze e la temperatura). Il punto 7 del
prompt di L54b. Decisioni di riferimento **ADR-102**, **ADR-103**. `<L>` = questa cartella. Python di
analisi con `/usr/bin/python3 -I`. Le forme d'onda non stanno nel repository: si rifanno.

## Il banco

`psu/` è il banco di L54b2 copiato, con `carico.txt`. Col solo copiato e senza opzioni nuove i deck di
`guasto` e `buco20` (`--timer sorgente --n2n7002 ds --tss 3.0 --comparatore tarato`) sono quelli di
L54b2 riga per riga, salvo il percorso di `cmpta.lib`; con le opzioni nuove aggiunte e assenti, lo
stesso (provato). Le opzioni (intestazione di `genera_tb_psu.py`, tutte solo con `--timer sorgente`):

- `--rete-forma calo:<f>:<t0>:<durata>:<rampa> | buco:<ms>:<zero|cresta> | sovra:<f>:<t0>:<durata>`:
  l'inviluppo della rete al posto di quello del caso, poi per `--rete`. **Provata**: `buco:20:zero` su
  `buco20` dà il deck di L54b2 salvo l'intestazione.
- `--disturbo <REF>:<V>:<fronte>:<larghezza>:<t0>`: un impulso trapezoidale in serie all'uscita del
  regolatore REF (U512 → V5, U503 → `VRELAY_REG`). I regolatori del banco sono ideali (nessuna banda):
  un gradino di carico non fa fronti, quindi il fronte si inietta.
- `--rimbalzo <front|sw3>:<ms>:<seme>`: la transizione dell'interruttore a TE diventa un treno di
  aperture e chiusure lungo `<ms>`, intervalli uniformi fra 20 µs e 1 ms, col seme dichiarato.
- `--durata`, `--passo-max` (il passo massimo del transitorio, 20 µs di L41b2), `--sonde-piu` (la base e
  il collettore della ritenuta, V5, i grezzi, e tre `.meas` sui punti del transitorio: la base prima e
  dopo TE, il minimo di VRELAY_EN), `--ritenuta costruttore`, `--bat54 costruttore`.

`psu/analizza_rob.py`: le colonne di `analizza_an.py` di L54a, calcolate allo stesso modo, più i
conteggi di mute e di K501 dopo TE, il ritorno della rete (`t_rit_ms`), la musica dopo il ritorno
(`dmus_ms`), la ritenuta tenuta alla fine, le tre `.meas`, i grezzi e V5.

## I criteri, scritti prima delle corse

Per ogni caso: **niente scatto a vuoto** dell'accensione, del mute o della ritenuta, e **lo scatto
quando deve**. Dal caso `buco20` (in musica a TE = 3,0 s, frontale acceso), alle tre reti:

1. **Se i rail restano in regolazione** (V+ mai sotto 10,6 V): nessun mute (`n_giu` 0), musica alla
   fine, la ritenuta no.
2. **Se escono**: il mute prima (`s41`, `r41`, `C2`, `C3`), poi la musica che torna **≥ 500 ms dopo il
   ritorno della rete** (`dmus_ms`), una sola volta (`n_su` 1); **la ritenuta mai**: un calo o un buco
   di rete non è un guasto della scheda (ADR-102 la vuole per un rail o `VRELAY_REG` fuori con la rete
   presente, e la rete «presente» qui è una rete bassa). K501 alla fine chiuso.
3. **La sovratensione** (+15 % per 0,5 s): nessun cambio; e il grezzo massimo contro la tensione
   d'ingresso massima dei regolatori (TPS7A4701 36 V, TPS7A3301 −36 V, SBVS204G / SBVS190), alle tre
   reti.
4. **Durante l'accensione** (calo a −20 / −30 % 0,3 s dopo il frontale): l'accensione si completa,
   senza ritenuta.

**I fronti veloci** (`--disturbo` su V5 e su `VRELAY_REG`, in musica e in mute): la ritenuta non scatta
(`bn_max` sotto 0,45 V, la soglia di T6b). Si cerca l'ampiezza a cui scatta, coi fronti 10 ns / 100 ns /
1 µs e coi condensatori base-emettitore (C554 / C555) a 0, 100 pF, 330 pF, 1 nF, 2,2 nF, coi transistor
del costruttore (i generici non hanno capacità: non possono scattare per un dv/dt); il margine si dà
in dB contro il fronte più grande che i datasheet dei regolatori danno per i gradini di carico della
scheda (K501, i relè della scheda audio).

**I rimbalzi** (treni di 1, 3, 5 ms, tre semi) all'accensione, allo spegnimento, al rilascio del mute e
al suo inserimento: lo stesso esito della transizione pulita (`n_giu`, `n_su`, `n_k501`, la ritenuta);
gli istanti al più più tardi della lunghezza del treno.

**Il controllo numerico**: un caso per famiglia rifatto col passo massimo 5 µs, gli stessi verdetti e
gli istanti entro un campione (0,1 ms).

Se una prova fallisce, il rimedio si porta all'utente coi numeri prima di cambiare il circuito.

## Gli esiti

Tutte le corse pulite (nessun ripiego numerico). Le cartelle sono in `seq/<etichetta>/<caso>`.

### I modelli del costruttore

`modelli.md` (il subagente dei componenti): BC847A/B/C, BC857A/B/C, BAT54 di **Diodes Inc.** (Nexperia
rifiuta lo scaricamento); `validate_models.py` 83 / 83, `--check-provenance` 39 / 39. Da sapere: il
BC847B ha VBE 708 mV a 2 mA (il massimo del datasheet è 700); la perdita del BAT54 è ~3,4 volte la curva
tipica, dentro il massimo (2 µA a 25 V).

- **I transistor da soli** (`cq`) ridanno L54b2 identico (musica a 1107,2 ms all'accensione, 537,2 dopo il
  buco di 20 ms).
- **Il BAT54 da solo** (`prova_solo_d`): **la ritenuta scatta a ogni accensione**. D535 e D541, in inversa
  verso AT_T2S (2,7 MΩ / 1 µF), aggiungono ~1,3 µA ai ~1,2 µA di carica: AT_T2S passa VREF a 1,07 s invece
  che a ~1,9 s, con V+ a 7,3 V (i rail ancora nella partenza morbida) e la rete presente. Limitations #79.

### La rete sporca (`an_rete.csv`, 60 corse, prima di ADR-104, coi modelli generici)

- **I buchi** da ½ a 15 periodi, alle due fasi, alle tre reti, e la rete che torna dopo 30–300 ms: tutti
  passano. ½ periodo non fa niente; da 1 periodo il mute prima (`s41`, `r41`, `C2`, `C3`), la musica che
  torna 513,6–675 ms dopo la rete, una volta, la ritenuta mai.
- **La sovratensione** +15 % per 0,5 s: niente. Il grezzo al massimo 26,7 V (rete +10 % × 1,15) contro i
  36 V dei TPS7A4701 / TPS7A3301; il grezzo dei relè 20,3 V.
- **I cali durante l'accensione** (−20 / −30 % a 0,3 s): l'accensione si completa, la ritenuta no.
- **I cali lenti: falliscono 14 su 27.** Se i regolatori escono di regolazione con la rete presente, la
  ritenuta scatta e la musica non torna: −30 % a ogni rete (salvo 0,1 s a +10 %), −20 % e −15 % a rete
  −10 %, già per 0,1 s. Il regolatore + esce con la valle del grezzo a 16,2 V (`grezzi.py`); a rete −10 %
  stabile è 17,88 V; quello dei relè esce per primo (12,37 contro 13,07 V).

**I rimedi provati sul banco** (`--qualifica`, solo sul banco): tre canali di comparatore che svuotano
l'innesco se un grezzo è sotto soglia. Sui tre grezzi (17 / 17 / 12,7 V, `an_q_*`, `confronta_q_*`): 12
cali su 14 si riprendono, ma **col corto davanti al regolatore + (`f_c509_corto_mus`) la ritenuta non
scatta più** e K501 resta chiuso: scartato. Sul solo grezzo dei relè (12,7 V, `an_qv*`, `confronta_qv_*`):
i 31 casi della sicurezza come L54b2, 12 su 14 si riprendono (la musica 549–684 ms dopo la rete); a −30 %
per 2 s (rete −10 % e 0 %) scatta ancora, dal timeout dell'accensione, con K501 che si apre e chiude 2–4
volte. **La scelta dell'utente: «Lasciare com'è»** (ADR-104).

### I diodi dei nodi da megaohm (ADR-104)

`--bassa-perdita` (il modello BAV199 di Diodes Inc. su D535 / D541 / D536), coi modelli del costruttore
(`an_bp_prova.csv`, `an_lp.csv`): con R571 820 kΩ la musica dopo il buco di 20 ms torna a 469 ms (solo
D535 / D541) o 461 ms (anche D536), sotto i 500; con R571 1 MΩ a 559 ms, l'accensione a 1149,7 ms, il
timeout e la ritenuta nel guasto giusti. **La scelta dell'utente: «Diodi a bassa perdita, R571 1 MΩ»**:
D535 / D536 / D541 BAS416 nel sorgente, R571 1M. Sul banco il BAS416 è il modello BAV199 (dichiarato).

**Il sorgente nuovo** (`n_`, la lista della sicurezza di L54b2 coi modelli del costruttore,
`confronta_n_*.txt`): **nessun verdetto cambia** in 31 righe; la musica +42 ms più tarda (R571), dopo un
buco sempre ≥ 559 ms dalla rete; il guadagno ~1 ms e K501 ~3 ms prima nei guasti (i transistor del
costruttore). Netlist: cambiano solo i valori e il simbolo delle quattro parti; lo schematico 167 / 167, il
manifesto uguale.

### I rimbalzi (`an_rimbalzi.csv`, 40 corse, sorgente nuovo)

Accensione, spegnimento, rilascio e inserimento del mute, treni di 1 / 3 / 5 ms, tre semi: **tutti come la
transizione pulita** (un solo mute o una sola musica, la ritenuta no); gli istanti al più +4,7 ms con un
treno di 5 ms; all'accensione e al rilascio identici (il debounce di AT_MRQ).

### I fronti veloci (`an_fronti.csv`, sorgente nuovo, transistor e BAT54 del costruttore)

**La prima forma non arriva al nodo** (`f_*`): in serie all'uscita del regolatore i condensatori di bulk
tengono il nodo e il regolatore del banco eroga soltanto; V5 non si muove. Quelle corse non valgono
(limitations #80). **La forma giusta** (`g_*`, `--disturbo nodo:`): l'impulso in serie ai terminali delle
parti sul nodo, oltre il disaccoppiamento; le `.meas` `x_max` / `x_min` provano che arriva.

| la base di Q513 al massimo (l'innesco ~0,45 V), impulso 10 µs su V5 a tutte le pull-up | +1 V | +5 V | −5 V |
|---|---|---|---|
| C554 = C555 = 0 | 52,7 mV | 130,5 mV | 47,4 mV |
| 100 pF | 15,3 | 31,1 | 13,6 |
| 330 pF | 8,8 | 14,5 | 6,9 |
| **1 nF (com'è)** | 6,4 | 8,4 | 5,3 |
| 2,2 nF | 5,8 | 6,7 | 5,2 |

(fronti 10 ns; con fronti di 1 µs all'1 nF lo stesso. A riposo la base è a 5,2 mV.) **La ritenuta non scatta
in nessun caso**, nemmeno senza i condensatori. Contro il fronte che i datasheet danno per i gradini della
scheda (TPS7A4701 figura 5-19: ~10 mV per 835 mA; i gradini della scheda sono decine di mA) il margine è
oltre 54 dB (5 V provati senza scatto). L'1 nF resta: con l'1 nF l'impulso di 5 V muove la base di 3,2 mV
invece di 125 mV; e senza di esso il banco di L54a si fermava sullo scatto (L54a).

Su `VRELAY_REG` (R522, la bobina di K501, R540, C531): la base non si muove; −5 V per 10 µs rilasciano
MUTE_CMD per un campione (≤ 0,1 ms, il sorvegliante dei relè sotto 11 V: lo scatto quando deve), e la musica
torna allo stesso istante (C3 tiene); −1 V niente.

### Il controllo numerico (`an_numerico.csv`)

Il calo, il rimbalzo e il fronte rifatti col passo massimo 5 µs: **identici** alle corse a 20 µs.

## Al prototipo resta (detto per nome)

I disturbi irradiati e quelli condotti dalla rete sopra le decine di kHz (il banco non ha il filtro di rete
né le capacità del trasformatore); il layout: le capacità parassite e le perdite superficiali della
scheda sui nodi da megaohm (AT_T2S 2,7 MΩ, AT_PRT 4,7 MΩ, AT_PGT 1 MΩ), i ritorni di massa fra RLY_RET e
GND; l'inrush vero del toroide alla chiusura di K501 (il modello del trasformatore è lineare).

## Rifare

```sh
/usr/bin/python3 -I <L>/psu/lista_nuovo.py <L>/../L54b2/lista_finale.txt > <L>/lista_nuovo.txt
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_nuovo.txt 6        # ~0,45 GB per corsa
/bin/zsh <L>/psu/confronta_serie.sh n_
/usr/bin/python3 -I <L>/psu/analizza_rob.py --te=3.0 <out.csv> <L>/seq/<etichetta>/<caso> ...
```
Le liste: `lista_rete.txt`, `lista_qualifica.txt`, `lista_varianti.txt`, `lista_bp_prova.txt` (prima di
ADR-104), `lista_nuovo.txt`, `lista_fronti.txt` (dopo). Prima di ADR-104 il sorgente si rifà con la
netlist del commit precedente a ADR-104 di questo ramo.
