# L63a — lo schematico completo dell'alimentatore (2026-10-21)

**Che cosa**: la richiesta dell'utente a fine L45d2b2c, «lo schematico, due pagine, ma complete
(anche fosse A3) una per la scheda audio e una per l'alimentatore, complete senza blocchi ripetuti».
Questo lotto fa la pagina dell'alimentatore e il controllo che la tiene onesta. La scheda audio è L63b.

**Il circuito non è stato toccato.** Nessuna ADR, nessuna non conformità aperta o chiusa.

## Le due scelte dell'utente, all'inizio

| Domanda | Risposta |
|---|---|
| Che cosa vuol dire «senza blocchi ripetuti» | **«Blocco una volta, un canale»**: il blocco di guadagno disegnato una volta, completo in ogni parte, con una tabella delle otto istanze, delle loro sigle e dei valori che cambiano; il canale sinistro disegnato e il destro nominato; tutto il resto completo. Circa 100 parti sulla pagina, A3. Vale per L63b |
| Come dividerlo | **«Prima l'alimentatore»**: L63a il controllo esteso alla netlist della scheda e la pagina dell'alimentatore, che non ha ripetizioni e lo collauda; L63b la scheda audio |

## La pagina

`docs/preamp/schematic/psu.pdf` (e `psu.svg`): A3 orizzontale, 1191 × 842 pt, una pagina. Si legge per pannelli:

1. **Rete e trasformatori**:
   - J510 dal modulo IEC;
   - F501 verso T2;
   - i due contatti di K501 verso T1;
   - i trasformatori fuori scheda, tratteggiati, sui loro morsetti.
2. **Rail audio ±15,3 V**:
   - ponte, serbatoi 4700 µF, R550 / R551;
   - U501 / U502 coi piedini tutti disegnati: gli ANY-OUT a massa, quelli liberi con la croce;
   - le due coppie di Schottky sui piedini, lo Schottky in serie, le tenute 2200 µF;
   - J1 verso la scheda audio, J2, il tie stellare NT501.
3. **VRELAY e i 5 V**:
   - T2, DF04M, 1N5819, serbatoio 4700 µF;
   - U503 12 V;
   - Q505 / Q506, l'interruttore di standby;
   - U504 e U512 in serie per V5.
4. **Riferimento, sorvegliante, rivelatore di rete**:
   - LM4040 e i partitori;
   - i quattro comparatori in OR su MUTE_G;
   - Q504 sulle semionde di RECT_V.
5. **Il micro**:
   - U509 con tutti i 20 piedini (i 6 liberi con la croce);
   - gli ingressi frontali con le loro reti RC;
   - J515 UPDI;
   - la legenda.
6. **I ritardi in hardware e i comandi dei relè**:
   - PERMIT_T e VR_T coi loro diodi, U508;
   - i tre sink 2N7002 con le catene di clamp verso VRELAY;
   - la bobina di K501 coi diodi di ricircolo, J4.

| | |
|---|---|
| Parti | **133 su 133** |
| Terminali | 349, tutti i piedini che la netlist collega |
| Piedini liberi | 14, ognuno con la croce (U501 3, U503 4, U509 6, U507 1) |
| Reti | 73, disegnate in 187 pezzi; 139 nomi (etichette, masse, rail) |
| Giunzioni | 105, messe dal disegno dove si incontrano tre fili |
| Testo | 5 pt (valori 4,5), le resistenze ~7 mm: si legge stampato in A3 |

Le cifre stampate sulla pagina sono **ricalcolate dai valori della netlist**, non scritte a mano:

- ANY-OUT: U501 15,3 V, U503 12,0 V; un'asserzione le confronta col valore della parte;
- FB di U502: 15,29 V;
- soglie del sorvegliante: VPLUS 13,55 V, VMINUS −13,50 V, VRELAY_REG 11,00 V;
- τ dei ritardi: 33,2 ms e 100,0 ms.

Coincidono con quelle di `psu_blocks_draw.py`.

Una cosa la pagina la mostra e non la risolve: il valore di F501 nella netlist è
«T2 primary (T, from T2 datasheet)». È scritto per intero in una nota del pannello 1. Il fusibile non
ha ancora una corrente: si fissa col datasheet di T2.

## Come è tenuta onesta

**Il controllo**, `scripts/check_schematic.py`:

- legge anche le netlist KiCad (le riconosce da `(export`);
- prende i piedini per numero; un piedino che nessuna rete elenca è libero;
- il percorso SPICE del blocco di guadagno è invariato: 61 su 61.

**Il kit**, `docs/preamp/schematic/sheet_kit.py`, per le pagine di una scheda intera:

- **le reti** di ogni piedino vengono da `psu.net`; i nomi dei piedini dai simboli di KiCad
  (limitations #70);
- **i rifiuti**, ognuno un errore e non un avviso:
  - un filo fra due reti diverse;
  - due reti sullo stesso punto, un nodo su un filo di un'altra rete, due fili di reti diverse
    sovrapposti;
  - un filo sopra una resistenza, un diodo, un condensatore, o dentro il riquadro di un integrato o il
    triangolo di un comparatore;
  - una rete disegnata in più pezzi senza un nome su **ogni** pezzo;
  - un'etichetta col nome di un'altra rete;
  - una parte o un piedino collegato non disegnati, un piedino libero disegnato come collegato;
  - un piedino del simbolo di un integrato né disegnato né segnato libero;
  - un testo sopra un altro testo, sopra un filo o sopra una parte;
- **le giunzioni** le mette il kit;
- **il manifesto** esce dal disegno: ogni terminale col nome del suo pezzo di rete.

**Nella suite**:

- **2d** confronta `psu.manifest.json` con `psu.net` nei due sensi, come per il blocco;
- **2f** ridisegna la pagina (i rifiuti del kit) e vuole il manifesto generato **uguale** a quello
  versionato. Senza questo, il 2d potrebbe passare su un file che il disegno non scrive più.

**I sabotaggi**: 14 su 14 presi, 6 sul controllo e 8 sul kit (`data/2026-10-21/L63a/script/sabotaggi.py`,
README accanto).

## Che cosa si è trovato strada facendo

- **Il controllo dei testi diceva «0 sovrapposti» su una pagina che ne aveva 170.** Misurava la
  figura di default di matplotlib (6,4 × 4,8 pollici), perché schemdraw la porta alla dimensione vera
  solo al salvataggio. Corretto, ha trovato 170 sovrapposizioni; il disegno le ha tolte tutte, e ora il
  controllo è uno dei rifiuti. Registrato come **limitations #70**, con la regola di provare ogni
  controllo nuovo su un caso che deve fallire.
- **Il primo controllo guardava solo fili contro fili.** Un filo che attraversa una resistenza
  sarebbe passato. Aggiunto il controllo sui corpi delle parti, provato da un sabotaggio.

## Resta

- **L63b**, la scheda audio, col kit di questo lotto (prompt in `NEXT-SESSION.md`). Le otto istanze del
  blocco non hanno le stesse sigle relative: per esempio la 1xx ha R142, la 5xx R541. La tabella delle
  istanze va ricavata dalla numerazione di `gain_block()` e verificata, non ricopiata.
- Il valore di F501, da fissare col datasheet di T2 (già noto, non nuovo).

## Verifica

- `check_schematic.py psu.manifest.json psu.net` → exit 0, 133 su 133.
- `check_schematic.py gain_block.manifest.json gain_block_flat.inc` → exit 0, 61 su 61.
- `sabotaggi.py` → 14 / 14.
- `pdfinfo psu.pdf` → 1191,14 × 842,48 pt (A3), 1 pagina.
- `run_tests.sh` → **14 passed / 0 failed**.
- La pagina guardata a 300 dpi pannello per pannello, prima di consegnarla.
