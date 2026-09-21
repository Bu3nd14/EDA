# ldr_catena — il mute graduale a monte con due LDR, sulla catena intera (L29b, ADR-038)

**SIMULATO, scratch, non il deck versionato.** Modello comportamentale dal datasheet, con
estrapolazione dichiarata (`models/optocoupler/vtl5c4_comportamentale.lib`, curva B per
entrambe le celle). Gli altri modelli sono segnaposto (NC-017). Tono 2,7 V RMS a 1 kHz
(20 kHz solo per il relè), +10 dB, fase π/2, carichi da **100 kΩ** soltanto.

## I file

| File | Cosa fa |
|---|---|
| `build.py OUTDIR [TD] [v1\|v2\|v3]` | genera `ldr1k.cir` |
| `build20k.py OUTDIR [RS_CHIUSURA RS_APERTURA]` | il relè al jack a 20 kHz, con le LDR a stato fermo |
| `post.py DIR` | carico sulla sorgente, stati delle LDR agli istanti del relè, ripresa del livello |
| `c2curva.py`, `c2spettro.py` | C2(t) a intervalli di 0,1 s, e lo spettro di C2: diagnostica |
| `v1_td3/` … `v3_td6/`, `rele20k_v2_td3/`, `pavimento_v3_td4/` | `analisi.csv` di `v2_metodo.py analizza`, manifesto, `post.txt` |

**Il banco.**
- Il blocco CANALE di `tb_v2_mute_graduale.cir` è copiato senza toccarlo:
  `v2_metodo.py canale` dà OK, e le tolleranze sono `vntol=1e-6 abstol=1e-12`.
- Fuori dal blocco:
  - `RSRC` a 1 TΩ;
  - 1,5 Ω più la **LDR in serie** fra sorgente e selettore;
  - la **LDR verso massa** su `INA`, accanto a R_IN = 1 MΩ;
  - LED comandati da generatori ideali, con 10 MΩ dall'anodo a massa;
  - la profondità `d`, un'unica variabile reversibile che va da 0 a 1 in TD secondi;
  - il **relè al jack**, cioè il contatto netto `BJK*` del blocco, col rimbalzo.
- Le forme d'onda (~1,5 GB per profilo) non sono versionate. Si rigenerano con
  `build.py`, poi `ngspice -b` in circa 10–15 minuti.

## I profili

| | Serie | Derivazione | Relè |
|---|---|---|---|
| **v1** | 20 mA → 0 lineare su d ∈ [0, 0,1] | 0 fino a d = 0,35, poi 0,2 µA → 20 mA log | 50 ms dopo d = 1 |
| **v2** | 20 mA → 10 nA log su d ∈ [0, 0,45] | 10 nA → 20 mA log su d ∈ [0,5, 1] | 0,5 s dopo d = 1 |
| **v3** | 20 mA → 0,2 mA (d 0–0,1), **0,2 mA → 4,5 µA (d 0,1–0,45)**, → 10 nA (d 0,5) | come v2 | come v2 |

- **10 nA** è la corrente di riposo dei LED: sta sotto il ginocchio del buio (0,19 µA), e
  l'anodo non salta.
- **v3 è la scelta dell'utente** del 2026-09-21. Il tratto lento è quello in cui R_s va da
  10 kΩ a ~2 MΩ contro R_IN, e sta nella parte **estrapolata** della curva.

## Esito (principale / fisse)

| | v1 Td 3 | v2 Td 3 | v2 Td 5 | v3 Td 4 | **v3 Td 6** | Soglia |
|---|---|---|---|---|---|---|
| **C2 inserzione** | 5,56 / 1,57 mV | 5,37 / 1,50 | 5,35 / 1,50 | 3,60 / 0,97 | **2,56 / 0,62** | 1 mV |
| C2 rilascio (`analizza`) | 1,25 V / 0,40 V | 5,07 / 1,46 | 7,70 / 2,44 | 6,79 / 2,15 | 6,89 / 2,19 | 1 mV |
| C2 inversione a metà | 7,9 / 2,4 mV | 11,5 / 3,6 | 7,0 / 2,1 | 9,4 / 2,8 | 7,4 / 2,2 | 1 mV |
| C2 relè 1 kHz, chiusura | 1,05 / 0,33 mV | 0,70 / 0,22 | 0,13 / 0,04 | 0,28 / 0,09 | 0,07 / 0,02 | 1 mV |
| A senza segnale | 4,8 mV / 1,3 mV | 0,20 / 0,06 µV | 0,03 µV | 0,05 µV | 0,03 µV | 100 µV |
| B2 | 3,0 µV | 3,6 µV | 0,5 µV | 1,2 µV | 0,29 µV | 100 µV |
| Carico minimo sulla sorgente | 252 kΩ | 278 kΩ | 588 kΩ | 423 kΩ | 714 kΩ | E3 ≥ 100 kΩ |

Sulla principale:
- il pavimento di C2 misurato con celle a TMAX diverso, senza LDR attive, vale
  0,51–0,59 mV;
- quello con le LDR attive (`pavimento_v3_td4/`) è nella tabella qui sotto.

L'ideale di ADR-036 (serie graduale da 3 s) valeva **2,93–3,05 / 0,83–0,87 mV**.

**Il relè a 20 kHz** (v2 Td 3, LDR allo stato di chiusura 871 kΩ e di apertura 2,17 MΩ):
- **chiusura 0,56 / 0,18 mV**, apertura **0,34 / 0,11 mV**;
- pavimento 0,1 µV: decidibile, perché a mute LDR il tono al jack vale ~1 mV;
- ADR-038 aveva stimato 0,57 mV.

## Il pavimento numerico con le LDR (la scoperta di questa corsa)

Dopo il rilascio, C2 non torna al pavimento: resta **stazionario a ~6,5 mV** sulla
principale, a livello già pieno (−0,000 dB), con le LDR ferme.

1. **Contro la stessa corsa senza relè** (`norele`, stato fisico identico dopo 10 s) resta
   a 6,4–7,1 mV. Quindi **non è fisico**.
2. Non è un tono:
   - lo spettro è piatto, con rms 1,6 mV e picco 6,7 mV;
   - le armoniche delle due corse coincidono (h2 876 contro 886 µV).
3. **La stessa corsa con TMAX 7 µs contro 10 µs** dà la curva del pavimento lungo tutta la
   sequenza (v3 Td 4):

| Finestra | Pavimento principale | Pavimento fisse |
|---|---|---|
| inserzione, 1–4 s | ≤ 0,68 mV | ≤ 0,22 mV |
| mute, 4,3–8,6 s | < 20 µV | < 20 µV |
| risalita, 8,6–9,9 s | 0,07–0,58 mV | 0,01–0,21 mV |
| **dopo 10 s: serie accesa, derivazione che si fa buia** | **4,6–7,2 mV** | **1,9–2,3 mV** |

**Cosa ne segue.**
- **L'inserzione è decidibile.** Per v3 Td 6 il C2 vale 2,56 mV contro 0,68 mV di pavimento.
- **Il rilascio no.** La finestra di C2 di `analizza` arriva a `t_rel + t_grad + 0,2 s`, e
  il suo picco cade nella coda, dove il pavimento sale: è il pavimento, non l'evento.
  - Per v3 Td 4, prima della coda: ≈ **2,9 mV** principale, contro 0,58 mV di pavimento.
  - Per v3 Td 6 non c'è una corsa di pavimento: il rilascio è **non decidibile**.
- **L'inversione** ha la stessa riserva.
- **Il meccanismo non è attribuito.** Il pavimento sale quando la cella verso massa sta
  facendosi buia a livello pieno, e la sensibilità del livello a R_p lì vale solo
  ~1,6e-4 per e-fold. È il primo compito di L29b2.
