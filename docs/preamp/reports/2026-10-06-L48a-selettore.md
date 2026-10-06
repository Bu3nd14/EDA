# L48a — il selettore d'ingresso coi condensatori per ingresso

Data: 2026-10-06 · Lotto: L48a · Decisioni: **ADR-064**. Dati: `data/2026-10-06/L48a/` (README).

## In breve

- **Il selettore esiste.** Quattro ingressi per canale; per ciascuno C_IN 1 µF in serie, R_SEL
  470 kΩ a massa dal lato del preamp, R_J 10 MΩ sul jack, e il NO di un relè G6K-2F-Y per ingresso
  (K13–K16, polo 1 sinistro, polo 2 destro). La manopola SW4 alimenta da `VRELAY` una sola bobina
  per posizione. Nessun firmware, nessun mute al cambio. Sorgente: `circuits/preamp/selector.py`
  (le bobine) e `preamp_audio.channel()` (il segnale).
- **NC-040 chiusa.** Cambio d'ingresso fra due sorgenti a continue diverse, sul banco
  (`spice/preamp/tb/tb_f1_selettore.cir`): fino a **100 mV** di continua il picco è **19,8 µV** al
  principale a +10 dB (~19 dB SPL contro una stanza silenziosa) e **6,3 µV** ai jack fissi, lo
  stesso di due sorgenti a 0 V. L'ingresso di prima, sullo stesso banco, dava **31,6 mV** al
  principale (~83 dB SPL) e 10,1 mV al fisso con 10 mV di continua.
- **Il limite, dichiarato in ADR-064**: con **1 V** di continua della sorgente il principale a
  +10 dB arriva a **140 µV** (~36 dB SPL; 63 µV a +3 dB, 44 µV al fisso), con la perdita del
  condensatore al minimo del poliestere. F1 regge fino a ~0,65 V.
- **E3 108,2 kΩ** (era 114,7; limite 100), uguale nelle tre posizioni del trim. **E5** invariato,
  5,496 µV. La rete perde 0,0027 dB a 20 Hz.
- **L'alimentatore**: +9,1 mA su `VRELAY`; la tenuta dopo una perdita di rete a −10 % scende da
  61,1 a **48,3 ms** (P9 ≥ 25 ms). NC-050 aggiornata.
- **NC-041, per L48b**: un calcolo a mano dice che il rimedio indicato (un condensatore
  all'ingresso del blocco B) **non toglie il gradino** di uno scatto del volume. Scritto nella voce;
  L48b lo misura prima di chiedere.
- `run_tests.sh` **13 / 0**; il 2e prova il selettore, **10 falsi su 10**; regressione **244 file
  su 248** uguali a L47c2b2, i 4 diversi sono E3 ed E5 dei due deck dell'ingresso.

## All'inizio, con l'utente

Le domande per nome, coi livelli in dB SPL e i numeri calcolati prima (non ancora simulati):

1. **Dividere?** — «Due parti»: L48a il selettore e i condensatori d'ingresso, L48b la continua
   attraverso trim e volume col banco di V2 e la regressione.
2. **Come togliere la continua della sorgente** — «Condensatore per ingresso». Nella domanda:
   il mute taglia in ~24 ms, ma la continua resta sui condensatori d'uscita (τ ~1 s sul principale,
   ~2,2 s sulle fisse), quindi un cambio sotto mute servirebbe ~10 s di silenzio. Il «superato» del
   prompt sul ~13 s di NC-040 non teneva conto di questo: il silenzio arriva in 24 ms, la continua
   no.
3. **I relè** — «Monostabili dalla manopola».

Un'aggiunta mia, non chiesta: **R_J 10 MΩ sul jack**. Col condensatore in serie un jack vuoto
resterebbe sospeso, e PR-14 dice «ogni ingresso sta a 0 V». Costa E3 da ~108,6 a 108,2 kΩ. Se
l'utente legge PR-14 solo sul lato del preamp, R_J si toglie senza altro da rifare.

## Il dimensionamento

`dimensionamento/`: C_IN 1 / 2,2 / 4,7 µF e R_SEL 470 kΩ / 1 MΩ. Il caso «oggi» ridà L47c2b2
(114,7 kΩ, 5,496 µV): il banco legge giusto.
- C_IN non decide niente in banda: la perdita a 20 Hz è 0,0027 dB con 1 µF, il rumore uguale alla
  quinta cifra. Più grande vuol dire più perdita di corrente continua (la costante d'isolamento
  è per µF), quindi 1 µF.
- R_SEL decide il gradino con le sorgenti a continua alta: la corrente di perdita del condensatore
  dell'ingresso non scelto, VB / 10 GΩ, scorre nel suo R_SEL. 470 kΩ: 140 µV a 1 V; 1 MΩ: 303 µV.
  E3: 470 kΩ dà 108,6 kΩ, 1 MΩ 112,5 kΩ. Scelto 470 kΩ.

## F1 sul banco

`tb_f1_selettore.cir` (canonico, passa il 2g e il 2h): due ingressi come nel sorgente, A a 0 V e
B a VB, il contatto di A che si apre a 50 ms e quello di B che si chiude 1 ms dopo (o 1 ms prima:
l'ordine di due monostabili non è garantito). Uscita fissa col suo buffer; principale con trim a
0 dB, attenuatore al massimo, blocco B a 0 / +3 / +10 dB. Tabella nel README dei dati.

Fino a 100 mV il residuo non dipende da VB: è il contatto che si muove (le capacità del contatto
e del selettore su un nodo tenuto da ~320 kΩ). Con la sovrapposizione è più piccolo, perché il
nodo non resta mai sospeso.

## Il sorgente e i controlli

- `selector.py` nuovo; `preamp_audio.py`: i quattro ingressi in `channel()`, i relè creati prima
  dei canali, il bilancio delle bobine (nove, 81,9 mA a 12 V; ~88 mA coi LED). Riferimenti
  espliciti (limitations #22). **Trovato nel lotto**: la manopola, chiamata SW3, collideva col
  deviatore del mute SW3 e SKiDL l'ha rinominata SW3_1 **senza errore**; ora è SW4.
- `check_relay_safe_state.py` (2e): il ruolo SEL, il SW_Rotary_3x4, e `check_input()` riscritto
  per intento. **10 falsi su 10** (`falsi/verdetti.txt`): la netlist di main, l'ingresso
  rimesso in continua, R_SEL tolta, R_J tolta, il NC sull'ingresso del blocco, il NO del relè
  sbagliato, la manopola che alimenta la bobina sbagliata, il diodo al contrario, un SEL
  bistabile, una bobina a GND.
- Il 2j passa senza modifiche: nessun pin del cablaggio fra le schede cambia.
- `preamp_blocks_draw.py` (2f): le asserzioni dell'ingresso riscritte sul selettore, il riquadro
  del selettore e la cornice degli ingressi aggiornati; SVG rigenerato.
- `tb_e3_e5.cir`, `tb_trim.cir`: la rete d'ingresso davanti al blocco A, E3 letta al jack.

## La regressione

21 deck contro `L47c2b2/regressione/dopo` (`regressione/confronto.txt`): 244 file su 248 uguali;
cambiano E3 (le colonne di |Zin|) ed E5 (≤ 1,7·10⁻⁵ relativo) di `tb_e3_e5` e `tb_trim`, come
atteso; nessun deck con rc ≠ 0. Il firmware non è stato toccato: il 2k passa, 19 falsi su 19.

## Non conformità

- **NC-040 chiusa** (bloccante per G1).
- **NC-041 aggiornata**: resta aperta e bloccante, è di L48b, col calcolo sul condensatore del
  blocco B.
- **NC-050 aggiornata**: tenuta 48,3 ms; resta aperta fino al carico congelato.
- **14 voci aperte, 3 bloccanti** (G1: NC-041, NC-048; G2: NC-044).

## Cosa resta fuori

- Il contratto (`PRB.md`, PR-14) dice ancora «il selettore è ancora da progettare» nei
  dettagli: cambiarlo vuole una ADR, da allineare con l'utente.
- Il dossier non descrive il selettore: si rigenera come lotto.
- La continua delle sorgenti vere dell'utente (il K11 non la pubblica): da misurare al prototipo,
  è la condizione «Da riaprire se» di ADR-064.
