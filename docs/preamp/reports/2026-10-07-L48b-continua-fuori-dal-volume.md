# L48b — la continua fuori dal volume: C_T fra trim e volume, R_G, il potenziometro col bilanciamento

Data: 2026-10-07 · Lotto: L48b · Decisioni: **ADR-065** (con PR-10, PR-16, PR-19, PR-20 firmati).
Dati: `data/2026-10-07/L48b/` (README).

## In breve

- **Il gradino del volume non c'è più.** Fra il COM del trim e la cima del volume c'è C_T, 10 µF in
  polipropilene (C265 / C465). Ogni scatto del volume, a ogni guadagno e con la continua del blocco
  A da −30 a +30 mV, resta **sotto 0,05 µV** al jack. Prima: in cima alla corsa a +10 dB **4,3 mV
  (~66 dB SPL)**, **19,5 mV (~79 dB SPL)** col caso peggiore.
- **Il rimedio indicato da NC-041 non funzionava**: col condensatore all'ingresso del blocco B lo
  scatto dà 4,29 mV, come prima. Il calcolo di L48a è confermato dalla misura.
- **Il volume diventa un potenziometro col bilanciamento** (scelta dell'utente: il commutatore a
  scatti cortocircuitante è «troppo caro»): ALPS RK27 10 kΩ log, e davanti un bilanciamento doppio
  a curva MN da 50 kΩ con lo scatto al centro, dove non attenua. **R_G 1 MΩ** dal cursore a massa
  (R265 / R465). I canali: **≤ 1 dB** col volume, col bilanciamento regolato (~2,5° d'immagine).
- **Le misure sul circuito nuovo**: E5 5,496 µV al centro del bilanciamento e 5,60 µV girato di
  3 dB; V1 ≥ **64,42°** con la sorgente del bilanciamento (5,6 kΩ); E9 −0,045 dB a 20 Hz; E3
  108,2 kΩ; il trim −6,08 / −12,00 dB.
- **V2 col volume** (gruppo 6 nuovo): sotto a ogni guadagno. La matrice intera: vedi sotto.
- **Trovati nel banco**, due trappole nuove: un `SW` resta aperto in `ac` (**limitations #48**), e
  `gmin` inventa corrente di gate su un gate sospeso (**#49**). In più: R113 del sottocircuito, che il
  blocco B vero non aveva (ora sì, R_G), e VOSB del banco V2 (#44) che spinge 20 nA nel volume.
- Il 2e ha `check_volume()`, il 2f le asserzioni nuove: **8 falsi su 8**.

## All'inizio: le strade misurate prima delle domande

Banco dedicato (`scatti/`): la catena di `tb_trim.cir`, la continua del blocco A imposta davanti al
gate (−6,6 mV nominale da `tb_op`, ±30 mV), il volume come scala da 10 kΩ col cursore fra due punti,
cortocircuitante e non. Lo scatto in cima alla corsa a +10 dB:

| Strada | nominale | peggiore | 20 Hz (100 k) | E5 |
|---|---|---|---|---|
| oggi | 4,30 mV · 66 dB SPL | 19,5 mV · 79 | −0,005 dB | 5,496 µV |
| 1 µF + 1 MΩ all'ingresso del blocco B | 4,29 mV · 66 | 19,4 mV · 79 | −0,006 | 5,496 |
| 47 / 68 / 100 µF prima del trim | ≤ 0,002 µV | ≤ 0,002 µV | −0,060 / −0,031 / −0,017 | 5,496 |
| 10 µF fra trim e volume | ≤ 0,002 µV | ≤ 0,002 µV | −0,033 | 5,496 |

A metà corsa, oggi, 39 / 52 dB SPL. Fra trim e volume il trim porta ancora la continua: senza mute
il cambio 0→−6 dB darebbe 73 / 86 dB SPL, ma il trim si muove solo in mute.

**Tre difetti del banco, trovati dalla sonda prima delle cifre** (README):
1. R113 nel sottocircuito del blocco B (il circuito di allora non l'aveva): col cursore aperto
   decideva il gate. Il generatore scrive un sottocircuito senza R113.
2. `gmin` (1e-12 S sul gate-drain a ~14 V, ~14 pA) faceva derivare il gate col cursore aperto:
   289 µV al jack, 0,48 µV con `gmin=1e-15` (**limitations #49**).
3. In `ac` gli interruttori `SW` restavano aperti: E5 era il rumore del solo blocco B (**#48**).

**Il rilievo nuovo, per ogni strada**: col contatto del volume che si apre per un attimo il gate
del blocco B resta senza ritorno. Con la corrente di gate del datasheet dell'LSK489 (−2 pA tipica,
−25 pA massima a 25 °C), 1 ms aperto su 100 pF dà 29 dB SPL tipici e 51 dB SPL massimi a +10 dB.

## Le domande e le risposte

Per nome e in dB SPL, coi numeri sopra:

1. **Dividere?** «Tutto in questa sessione».
2. **Il volume continuo?** L'utente: «se invece di un volume a scatti mettiamo un volume
   continuo?». Risposta: la continua nel cursore di un potenziometro crepita (ESP: «DC should not
   be allowed to flow through any pot»); il gradino nasce dalla continua, non dagli scatti.
3. **La letteratura?** «non mi ricordo nessun pre che abbia click udibili». Risposta, con le fonti:
   un condensatore davanti al volume (e spesso il ritorno del gate dopo), oppure operazionali con
   decimi di mV di offset, oppure un servo.
4. **68 µF?** «non ho mai sentito parlare di 68 µF sul segnale». Risposta: lo decide l'impedenza
   dopo il condensatore; 0,68 µF su 1,5 kΩ perderebbero ~18 dB a 20 Hz; Self raccomanda 47 µF su
   10 kΩ. **«Fra trim e volume, film 10 µF».**
5. **Il commutatore cortocircuitante** (Elma 04, Seiden, ~140–180 €): «troppo caro, da solo costa
   come 1/4 della scheda audio, dobbiamo usare un buon potenziometro non a scatti e se la precisione
   tra i canali può risultare udibile a 4 m […] dovremo introdurre un balance».
6. **R_G**: «Sì, 1 MΩ». **La soglia**: «1 dB» (Sengpiel: ~2,5° per dB al centro; Mills: ~1°
   d'angolo minimo). **Il potenziometro**: «ALPS RK27 + bilanciamento» (≤ 2 dB dichiarati; il TKD
   CP-2500 ≤ 3 dB). **Il bilanciamento**: «Curva MN, 0 dB al centro» (Alpha RV16 MN 50 kΩ con lo
   scatto al centro; il lineare in serie perdeva 1,9 dB al centro, contro E1).
7. **Il contratto**: PR-10, PR-16, PR-19, PR-20 riscritti e **firmati**: «Firmo così».

## Il sorgente

`preamp_audio.py`: C_T (C265 / C465, `C_Rect_L31.5mm_W17.0mm_P27.50mm_MKS4`) fra la rete nuova
`<ch>_TRIM_OUT` (il COM di K7) e `<ch>_ATT_TOP`; R_G (R265 / R465) dal cursore a massa, fuori dal
blocco per non rinumerarlo (#22); il connettore del volume `VOL_<ch> 10k`. Netlist confrontata per
connettività (`sorgente/confronto_netlist.txt`): quattro parti nuove, due valori di connettore, le
due reti spezzate; nient'altro. ERC di SKiDL 65 avvisi / 0 errori, nessuno sulle parti nuove. Schema
a blocchi rigenerato (pannello 2: «dal TRIM → 10 µF → VOLUME + bilanciamento MN → R_G → BLOCCO B»).

**I controlli.** 2e: `check_volume()` prova per intento che il pin alto del volume si raggiunge dal
COM del trim **solo** attraverso un condensatore, e che il cursore ha una e una sola 1 MΩ a massa;
riconosce NC-041 anche sulla netlist di prima, dove il connettore si chiamava `ATT_`. 2f: le stesse
cose sullo schema a blocchi. **8 falsi su 8** (`falsi/verdetti.txt`): la netlist di prima, C_T
cortocircuitato a sinistra e a destra, C_T scavalcato da una resistenza, R_G staccata da massa, R_G
100k, R_G tolta dal cursore, il connettore rinominato (solo il 2e); la netlist vera passa.

## Le misure sul circuito nuovo

| Grandezza | L48a | L48b | limite |
|---|---|---|---|
| E5 peggiore (+10 dB, 430 Ω), bilanciamento al centro | 5,496 µV | 5,496 µV | 9,95 |
| E5 peggiore, bilanciamento girato di 3 dB | — | **5,60 µV** | 9,95 |
| V1 blocco B, sorgente fino a 2,611 kΩ | 65,16° | 65,16° | 60 |
| V1 blocco B, sorgente 5,6 kΩ (bilanciamento) | — | **64,42°** | 60 |
| E9, 20 Hz, cj 100 kΩ | −0,005 dB | **−0,045 dB** | ±0,2 |
| E9, 20 Hz, finale futuro 10 kΩ | −0,135 dB | −0,175 dB | (ADR-007) |
| E3 | 108,2 kΩ | 108,2 kΩ | 100 |
| trim −6 / −12 dB | −6,003 / −11,939 | −6,076 / −11,997 | ±0,1 |
| scatto del volume, ogni guadagno e continua | 4,3 mV (nominale) | ≤ 0,05 µV | 100 µV |
| cursore che si stacca, con R_G, +10 dB | — | 9,5 / 31 / ~50 dB SPL (tipica / max 25 °C / max 55 °C stimata) | |

## V2 col volume

Il generatore (`data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py`) ha ora C_T, il
bilanciamento al centro e il volume come due contatti (`KVH`, `KVL`) che portano il partitore da 0
a −2 dB in cima alla corsa; R_G è R113 del blocco. Il controfattuale li scavalca. 155 corse.

- **Gruppo 6, lo scatto del volume** (dispersione peggiore, senza mute, A_ins): al principale
  **6,2 / 8,9 / 19,6 µV** a 0 / +3 / +10 dB (fino a ~19 dB SPL), alle fisse ~0,6 nV. Scalano
  esattamente col guadagno: è VOSB del banco, che spinge 20 nA nel volume attraverso R113 (#44,
  lasciato perché prudente). Con VOSB = 0 lo stesso scatto a +10 dB dà **9,2 nV** (`v2/sonda_vosb/`).
- **Diagnostica: il trim cambiato in mute e il mute rilasciato 0,5 s dopo** (V2 vuole 2 s):
  3,6 / 5,3 µV al principale (0→−6 / 0→−12 dB).
- **La matrice intera** (`v2/matrice/verdetto.csv`): **0 verdetti fuori su 250**. I peggiori:
  senza segnale A ≤ **5,4 µV** (accensione; L47c2b1 7,3), il guadagno 0,04 µV, il trim 0,10 µV,
  la dispersione 0,41 µV; con la musica il jack grezzo ≤ **43,5 µV** (L47c2b1 55,0) e il sempre in
  mute ≤ **16,9 µV** (20 kHz, come L47c2b1); il volume 19,6 µV. Le corse: 154 su 155 passano la
  guardia; `off_r10m_d20_iii` abortisce (uno spegnimento brusco di L29c, escluso dal verdetto da
  L29d2, come in L47c2b1). Le ultime sei righe, il clic a 20 kHz, sono state analizzate a parte
  (`manifest_20k.csv`) e unite (`unisci_analisi.py`).
- **Il clic del taglio** (`v2/matrice/clic.csv`, dichiarato, senza soglia): le stesse cifre di
  L47c2b1. Al rilascio a 1 kHz +4,65 dB sul taglio ideale al principale e +5,19 dB alle fisse; a
  20 kHz +0,35…+0,66 dB; a 20 Hz al rilascio 23,7 / 25,7 dB sotto il taglio ideale.
- **Il controfattuale** (C_T scavalcato, il bilanciamento tolto): ridà la cella del taglio di
  L47c2b1, C2 e A con la musica entro lo **0,02 %**, A senza segnale e B al pavimento numerico.
- Le corse a 20 kHz hanno richiesto quasi due giorni di orologio e ~2,5 ore di CPU: il Mac era in
  sospensione. La seconda volta la matrice si corre con `caffeinate`.

## Regressione

I 21 deck veloci (`script/regressione.sh`, `confronta.py`): **245 file su 248 uguali a L48a**,
nessun deck con rc ≠ 0. Cambiano i tre attesi: E5 di `tb_e3_e5` e `tb_trim` (al più 0,23 %,
C_T e il bilanciamento nella catena) e l'attenuazione del trim in `tb_trim_e3.csv` (il carico di
8,33 kΩ al posto di 10 kΩ, −6,076 / −11,997 dB). Gli altri deck modellano il blocco B col solo
attenuatore, senza C_T: in banda sono il circuito di oggi (R113 del sottocircuito è R_G), mentre in
continua il loro blocco B vede ancora la continua del blocco A attraverso il volume (−6,6 mV
nominali, non misurato quanto sposti le loro cifre). Misurano anelli, rumore e impedenze, non
gradini; i gradini sono di V2, che ha C_T.

## Non conformità

**NC-041 chiusa** (ADR-065): la continua del blocco A non attraversa più il volume, misurato sul
circuito nuovo; il volume è fra gli eventi di V2, sotto a ogni guadagno. La frase falsa del dossier
si corregge quando lo si rigenera (NEXT-SESSION). Restano **13 aperte, 2 bloccanti** (NC-048 per
G1, NC-044 per G2).

## Cosa resta, e per chi

- Il potenziometro montato si misura al prototipo (E10: ≤ 1 dB col bilanciamento regolato).
- Il dossier non descrive né il selettore né il volume nuovo; le righe `Stato:` di ADR-009 e
  ADR-053 non nominano ADR-065 (con l'utente, quando si rigenera il dossier).
- L49: gli ingombri nuovi (C_T 31,5 × 17 mm per canale) e il bilanciamento sul pannello.
