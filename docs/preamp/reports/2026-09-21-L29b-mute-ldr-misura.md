# L29b — il mute graduale a monte con LDR: il modello verificato e la misura sulla catena (2026-09-21)

Lotto **L29b**, cominciato il 2026-09-16 e ripreso il 2026-09-21. **Diviso due volte**:
- il caso peggiore di V2 è **L29c** (2026-09-16);
- il sorgente, il deck versionato ed E3/E5/P7 sono **L29b2** (scelta dell'utente del
  2026-09-21).

Questo lotto chiude la **misura**. **NC-028 resta aperta e bloccante.**

Dati:
- `data/2026-09-16/L29b/` per la prima parte;
- `data/2026-09-21/L29b/ldr_catena/` per questa.

**Provenienza dei modelli.** Il modello della LDR è **comportamentale dal datasheet, con
estrapolazione dichiarata**, e ogni cifra qui sotto lo porta. Del costruttore c'è solo
l'LS352. Il resto è segnaposto (NC-017), LSK489 compreso.

## 1. Il modello VTL5C4: prima verificato, poi corretto

`vtl5c4_modello/` del 2026-09-16 (README lì). Il modello **non riproduceva la sua
fonte**. È stato corretto nel generatore, non nel `.lib`.

| | Prima | Dopo | Tolleranza |
|---|---|---|---|
| Statica, 38 punti delle curve A–D | già corretta | entro lo 0,02 % | 0,5 % |
| Spegnimento da 40 mA, 10 punti | 567 contro 1555 Ω a 105 ms | entro l'1,4 % | 3,5 % |
| A 10 s | — | 396,9 MΩ (minimo del datasheet: 400 MΩ) | 3,5 % |
| Accensione dal buio, 16 punti | 6,8 ms per 330 Ω, il datasheet 1,51 ms | entro il 3,16 % | **3,5 %, allentata** |

**La tolleranza d'accensione, allentata e dichiarata.**
- Il 3 % è diventato 3,5 % per un solo punto (10 mA, 4,50 ms, −3,16 %).
- Quel punto dista −3,5 % anche dalla retta dei minimi quadrati della sua stessa curva:
  è dispersione della lettura a pixel.

**Sabotaggi.** Tre, tutti rilevati.

**Tre trappole trovate, tutte silenziose:**
1. `alter` + `op` in sequenza non convergono e stampano cifre sbagliate, a 40 mA perfino di
   segno opposto.
2. Col trapezio, un gradino sul LED fa oscillare la corrente della cella di ±180 %.
3. Una divisione per `V(tau)`: il nodo parte da 0 V nel Newton del punto di lavoro, e la
   cella **in serie a 1 MΩ** (dove sta in ADR-038) non convergeva mai. Oggi è protetta, e
   la ricetta di `validate_models.py` ha il caso: senza protezione cade, provato.

**`validate_models.py`: 48 su 48.** I cinque modelli di L29b erano SKIP.
- **MMBFJ112**: la rDS(on) del modello del costruttore vale 59,7 Ω, contro un massimo di
  50 Ω nel suo stesso datasheet. È registrato, e non incide: è un candidato scartato.

## 2. La catena col metodo di V2

Scratch `ldr_catena/`.
- Il blocco CANALE è quello dei deck di V2, senza modifiche.
- Due LDR per canale all'ingresso del blocco A, con la profondità unica di ADR-038 e il
  relè al jack.
- Tono a 1 kHz, 100 kΩ. Il relè anche a 20 kHz.

Tre profili del comando dei LED:
- **v1** e **v2** sono miei;
- **v3** è una scelta dell'utente, fatta sulle cifre di v2.

| Principale / fisse | v1 Td 3 | v2 Td 3 | v2 Td 5 | v3 Td 4 | **v3 Td 6** | Soglia |
|---|---|---|---|---|---|---|
| **C2 inserzione** | 5,56 / 1,57 mV | 5,37 / 1,50 | 5,35 / 1,50 | 3,60 / 0,97 | **2,56 / 0,62** | 1 mV |
| C2 rilascio | 1,25 V | 5,07 / 1,46 ¹ | 7,70 / 2,44 ¹ | ≈ 2,9 mV prima della coda | **non decidibile** | 1 mV |
| C2 relè, 1 kHz | 1,05 / 0,33 mV | 0,70 / 0,22 | 0,13 / 0,04 | 0,28 / 0,09 | 0,07 / 0,02 | 1 mV |
| A senza segnale | 4,8 mV | 0,20 µV | 0,03 µV | 0,05 µV | 0,03 µV | 100 µV |
| B2 | 3,0 µV | 3,6 µV | 0,5 µV | 1,2 µV | 0,29 µV | 100 µV |
| Carico minimo sulla sorgente | 252 kΩ | 278 kΩ | 588 kΩ | 423 kΩ | **714 kΩ** | E3 ≥ 100 kΩ |

¹ Cifre di `analizza`, per le quali **il pavimento con le LDR non è misurato** (§3).

**Il relè al jack a 20 kHz** (v2 Td 3):
- **chiusura 0,56 / 0,18 mV**, **apertura 0,34 / 0,11 mV**;
- il pavimento è 0,1 µV, quindi la cella è decidibile;
- la stima di ADR-038 era **0,57 mV**.

**L'ideale di ADR-036** (serie graduale da 3 s) valeva **2,93–3,05 / 0,83–0,87 mV**.

### 2.1 Cosa hanno detto i profili

- **v1**:
  - al rilascio la serie tornava in 0,1 s, e il livello saltava di 31 dB (C2 1,25 V);
  - il gradino 0 → 0,2 µA sul LED della derivazione faceva saltare l'anodo di ~1,4 V
    dentro un nodo a 1 MΩ, attraverso 0,5 pF (A 4,8 mV).
- **v2**:
  - 10 nA di riposo e rampe log-lineari risolvono A e il rilascio;
  - **l'inserzione resta a 5,35 mV con qualunque durata** (3 s o 5 s). Il picco cade
    quando la serie va da ~1 k a ~80 k, e lì la cella si spegne alla sua velocità, non a
    quella del LED.
- **v3**:
  - il tratto della serie da 10 k a ~2 M va più lento dello spegnimento naturale;
  - l'inserzione scende a **2,56 mV** sulla principale, **sotto l'ideale di ADR-036**, e a
    **0,62 mV sulle fisse, sotto soglia**;
  - quel tratto sta nella parte **estrapolata** della curva.

### 2.2 Cose che l'ideale non mostrava

- **Il carico sulla sorgente** non scende mai sotto 252 kΩ. Con v3 Td 6 il minimo è
  714 kΩ, contro l'ipotesi ≥ 10 kΩ di ADR-038 e contro E3 ≥ 100 kΩ.
- **La ripresa del livello dopo il rilascio non è lenta.** Con la serie a 88 Ω, la
  derivazione ancora a ~300 kΩ costa 0,002 dB.
- **Il relè a 1 kHz dipende da quanto è buia la serie** alla chiusura.
  - ADR-038 la supponeva al buio, e dava ≈ 30 µV.
  - Con 50 ms di ritardo la serie vale 576 kΩ, e C2 1,05 mV.
  - Con 0,5 s scende sotto 1 mV. È il motivo del ritardo di 0,5 s nei profili v2 e v3.

## 3. Il pavimento di C2 con le LDR: il rilascio non è ancora decidibile

Dopo il rilascio, C2 resta **stazionario a ~6,5 mV** sulla principale, col livello già
pieno.
- Contro la stessa corsa senza relè, che dopo 10 s è nello stato fisico identico, resta a
  6,4–7,1 mV: **è numerico**.
- Lo spettro è piatto, e le armoniche delle due corse coincidono.

La stessa corsa (v3 Td 4) con TMAX 7 µs contro 10 µs misura il pavimento lungo la
sequenza:

| Finestra | Principale | Fisse |
|---|---|---|
| inserzione | ≤ 0,68 mV | ≤ 0,22 mV |
| risalita del rilascio | ≤ 0,58 mV | ≤ 0,21 mV |
| **coda: serie accesa, derivazione che si fa buia** | **4,6–7,2 mV** | **1,9–2,3 mV** |

La finestra di C2 di `analizza` arriva a `t_rel + t_grad + 0,2 s`, dentro la coda.
**I C2 di rilascio che `analizza` riporta per v3 (6,8–6,9 mV) sono pavimento, non evento.** Per v2 (5,07 e 7,70 mV) il picco cade durante la rampa della serie, ma il pavimento di quelle corse non è misurato: non si sa.
- Per v3 Td 4, prima della coda: ≈ 2,9 mV.
- Per v3 Td 6 non c'è una corsa di pavimento.
- Il pavimento di C2 dei deck di L29a (0,51–0,59 mV) **non copre le corse con LDR
  attive**.
- Il meccanismo non è attribuito.

## 4. Verdetto

- **Si porta avanti il profilo v3 con Td = 6 s**, candidato di progetto per L29b2.
  - A, B, il relè (1 e 20 kHz) ed E3 sono nei limiti.
  - L'inserzione è sotto l'ideale di ADR-036 sulla principale e sotto soglia sulle fisse.
  - Resta **C2 d'inserzione a 2,56 mV sulla principale, fuori soglia**: è la stessa
    condizione che ADR-036 aveva accettato «per ora» per l'ideale (2,93 mV).
- **Il rilascio e l'inversione non sono decidibili** finché il pavimento numerico con le
  LDR non è capito o abbassato. È il primo compito di L29b2.
- **NC-028 resta aperta e bloccante.** Mancano:
  - il rilascio decidibile;
  - 20 Hz e 20 kHz sulla dissolvenza, e 10 kΩ;
  - il sorgente e il deck versionato;
  - E3, E5 e P7 (L29b2);
  - il caso peggiore (L29c).

## 5. Cosa non è stato fatto, e perché

- **Il sorgente** (`circuits/preamp/preamp_audio.py`), **il deck versionato**, **E3 ed E5
  con la LDR in serie**, **P7 riletto**: tutto in L29b2, per la divisione decisa
  dall'utente.
- Questo lotto non ha scritto **nessuna ADR**. Il profilo v3 è una scelta di comando dentro
  ADR-038, e diventa decisione di progetto quando va nel sorgente, in L29b2.
