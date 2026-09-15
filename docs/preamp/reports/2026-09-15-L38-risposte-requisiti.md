# L38 — Le risposte del 2026-09-15 diventano requisiti (2026-09-15)

Lotto **L38**, di sola documentazione più un commento in `gain_block.py`. ADR
nuove: **ADR-032**, **ADR-033**, **ADR-034**. Aggiorna **NC-009** e **NC-019**.
**NC-028 sale a bloccante.**

**Nessun deck eseguito, nessun valore del circuito cambiato.** Le cifre marcate
«calcolato» vengono da `data/2026-09-15/L38/calcolo_v2.py` (solo stdlib): una
formula già scritta in NC-028 e un filtro digitale su forme d'onda ideali.
L'uscita è in `calcolo_v2.out.txt`.

## 1. La soglia letta contro i numeri del repo, prima di scriverla

La lezione di L37 era che un criterio del mandato può non distinguere niente.
Quattro letture.

| Lettura | Esito | Fonte |
|---|---|---|
| 100 µV in dB SPL di picco a 1 m, formula di NC-028 | **33,45 dB**, calcolato, limite superiore. Il diario diceva «circa 34» | `calcolo_v2.out.txt` §1; le righe di NC-028 si riproducono (53,45 / 76,37 / 86,51 / 93,79) |
| Il filtro 20 Hz–20 kHz su un gradino netto | 104 mV → **0,111 / 0,1109 / 0,1104 V** con passa-alto di ordine 1 / 2 / 4: **il filtro non lo ammorbidisce** | §2 |
| Lo stesso filtro su una rampa | 104 mV in 500 ms → **1,655 / 0,7547 / 0,3972 mV**; l'ordine pesa circa ×2 per passo, ma su nessuna cifra esistente cambia il verdetto | §2 |
| Il residuo a mute inserito | 4 mV picco-picco (NC-028), ≈ **59,47 dB SPL** calcolati. Letto alla lettera boccerebbe ogni mute a contatto singolo, e non è un bump | NC-028; §1 |

**Il contatto dei banchi non è il contatto vero.**
- `spice/preamp/tb/tb_mute_corto.cir:132` usa `RON=0.01`.
- Il datasheet G6K congelato (`vendor/relays/omron/G6K/en-g6k.pdf`,
  Characteristics) dà **100 mΩ massimi** e tempi d'intervento e di rilascio di
  **3 ms massimi**.
- I 3 ms sono un ritardo, non la durata del fronte. Per questo lo spike da 2,2 µs
  di NC-028 non si scrive come artefatto.

## 2. Le domande all'utente, e le risposte

La soglia alla lettera non separava i casi, quindi si è chiesto invece di
aggiustare.

| Domanda | Risposta dell'utente |
|---|---|
| Lo spegnimento rientra? | «si lo spegnimento rientra» |
| Ordine del passa-alto a 20 Hz | «indifferente» → 2° ordine, scelta di metodo del lotto |
| Cosa conta: A il bump, B la musica che filtra in mute, C il taglio netto della musica | «A, B e C» (dopo una spiegazione, perché la prima formulazione non era chiara) |
| Come si misura C | finestra di 10 ms, fra 10 ms, 50 ms e «la propone L29» |
| NC-019, il ponte che alla lettera è un corto | «Rame, forma da dimensionare» |

## 3. Cosa è stato scritto

- **ADR-032**:
  - la soglia, ≤ 100 µV di picco filtrato 20 Hz–20 kHz al jack delle tre uscite,
    per A, B e C, accensione e spegnimento compresi;
  - sotto 20 Hz nessun limite oltre il filtro;
  - il caso peggiore al posto dell'uso reale, anche nel criterio 3 di ADR-030;
  - conseguenza scritta e non decisa: la regola d'uso di ADR-030 non rende
    conforme V2.
- **`REQUIREMENTS.md`**:
  - V2 con soglia e **metodo di misura**: nodo, carichi, filtro, campionamento,
    contatti, la differenza da un riferimento per A, B sul mute tenuto, C col tono
    meno la ricostruzione su 10 ms, e il caso peggiore;
  - «Nota su F5» precisata;
  - Singxer **CHIUSO** in «Aperti»; il phono resta **RINVIATO**;
  - intestazione.
- **ADR-033**: i LED del trim restano su K9 e K10. Il guasto di un solo relè è
  noto e accettato, anche per i LED di ADR-030.
- **ADR-034**: accoppiamento termico col rame del PCB, T7 intatta, e due vincoli
  (sezione 4).
- **Indice delle ADR**: 017, 027 e 030 segnate come precisate, sul modello di
  ADR-013 e ADR-031. **I file delle ADR esistenti non sono stati toccati.**

## 4. NC-019: il ponte alla lettera era un corto

- **Il sorgente.** `Q(kind, val, model, c, b, e)`: il MJE15032 è
  `Q("npn", "MJE15032", "NMJE15032", VP, NBN, NEN, fp=FP_TO220)`. Il tab, cioè il
  collettore, sta su **`VP`**. Il moltiplicatore è
  `Q("npn", "2N5551", "NSS2N5551", NX, NBB, NY)`, e nessun piedino è su `VP`.
- **Il footprint.** `TO-220-3_Vertical.kicad_mod` ha solo `pad "1"`, `"2"` e
  `"3"`: nessuna piazzola del tab. La libreria ha anche le varianti
  `Horizontal_TabDown` e `Horizontal_TabUp`.
- **Il riferimento di NC-019 era deriva di righe.** Diceva `gain_block.py:350`,
  ma la regola stava a 459–461.
- **La consegna a `pcb-automation-engineer` non esiste come documento.** Era solo
  la riga «Handed to pcb-automation-engineer as a placement rule». Da L38 è il
  commento che punta ad ADR-034, e lo dice.
- **Il controllo sul commento.**
  - Si esporta HEAD con `git show`, poi si confronta `ast.dump` con quello del
    worktree: **identico**, rc 0.
  - Su una copia con `R("1.69k", NX, NBB)` portato a `1.70k` lo stesso controllo
    rifiuta: rc 1.

## 5. NC-028 sale a bloccante

Il paragrafo «Perché maggiore e non bloccante» della voce diceva che V2 non aveva
una soglia. Ora ce l'ha.

La misura di L11 è versionata: `data/2026-09-14/tb_mute_corto_transitorio.csv`,
`vjm_max_rel` 17,3886 V contro `vjm_pk_prima` 11,9907 V a +10 dB. Porta sul jack
un gradino di volt, circa 54 000 volte la soglia. Nessuna scelta di metodo lo
porta sotto: un gradino netto passa il filtro quasi intero (§1).

È lo stesso passaggio che L26 fece con NC-002. Il mandato si aspettava 13 voci e
2 bloccanti; i file dicono **13 e 3**.

## 6. NC-009, punto 3

L'utente ha deciso la sede: il manuale d'uso. **Il manuale non esiste**, e nessun
lotto della tabella lo produce. Il punto 3 si sposta e non si chiude, quindi la
voce resta aperta, maggiore.

## 7. Verifiche

- `run_tests.sh` eseguito dal worktree: **10 passed, 0 failed**. Il 2i passa,
  perché il blocco non è stato rigenerato.
- **Nessun file ADR esistente modificato.** In `decisions/` cambia solo
  `README.md`, cioè l'indice.
- **Le condizioni di `chunk_close.sh`** su `STATE.md` (L38 **fatto**) e su
  `NEXT-SESSION.md` (titolo «… — L29») sono verificate con grep prima del commit.

## 8. Da dire all'utente

- **NC-028 è bloccante.** Non cambia l'ordine dei lotti: L29 era già sul cammino
  critico.
- **A + B + C fanno crescere L29.**
  - C, con la musica presente, difficilmente sta sotto soglia con un contatto
    netto: probabilmente serve un mute graduale.
  - B va misurato con contatti a 100 mΩ.
  - La riga di L29 passa da M a **M/L**.
- **Il manuale d'uso** (NC-009) non ha un lotto.
- **Il selettore d'ingresso**: V2 lo elenca fra le commutazioni, e nessun lotto lo
  misura.
