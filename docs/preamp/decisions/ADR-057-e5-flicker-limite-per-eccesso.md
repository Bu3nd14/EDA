# ADR-057 — E5 si verifica col flicker dei bipolari a un tetto dichiarato, ricavato dalle curve pubblicate

Data: 2026-10-01 · Stato: accettata

## Contesto

NC-004 (bloccante per G1): da L39 tutti i dispositivi simulati sono modelli del costruttore, ma
solo l'LSK489A porta il rumore 1/f. Specchio (LS352, modello LS350), cascode, VAS, pozzi,
moltiplicatore di Vbe e finali ne erano senza, e E5 (5,08 µV contro 9,95) era un **pavimento**,
non una cifra. Il mandato di L44 lasciava all'utente il modo di dare il flicker a quei
dispositivi; l'utente ha scelto **cercare dati veri**, ricadendo su un limite per eccesso dove
mancano.

## Decisione

**E5 si verifica coi bipolari a KF = 1·10⁻¹³, AF = 1,4 (forma di ngspice
i² = 2qIb + KF·Ib^AF/f): un tetto per la classe dei bipolari a piccolo segnale, due volte il valore
tipico letto sulle curve pubblicate, applicato per scelta dichiarata anche ai piccoli NPN e ai
finali, che non hanno curve.** Il tetto sta nei cinque modelli di `models/` (LS350, MMBT5401,
MMBT5551, MJE15032, MJE15033), e `validate_models.py` lo rilegge dal rumore a ogni corsa. Con
questo, e coi tetti di distorsione di ADR-055, **NC-004 si chiude** (decisione dell'utente,
2026-10-01).

## Perché

- **Le curve trovate** (L44, ricerca di `bom-component-manager`; PDF e letture in `vendor/` coi
  PROVENANCE):
  - **2N5087, Motorola**, Fig. 2 a pag. 3, rumore di corrente a 10 µA … 1 mA: AF = 1,35 coerente
    sulle cinque correnti, KF ~2·10⁻¹⁴ a 10 Hz e ~5·10⁻¹⁴ a 300 Hz. Rilette dall'orchestratore
    sull'immagine della pagina: coincidono;
  - **databook Linear Systems**, nota «Solving the Noise Puzzle», Fig. 3 a pag. 329, famiglia
    LS310/LS350 a 10 e 300 µA (la didascalia non dice quale dei due): AF ~1,46, KF ~6·10⁻¹⁴; il
    caso peggiore a 10 µA è ~2× il tipico.
- **Il tetto copre tutte le letture**, all'eccesso a 1 Hz: LS35x a 300 µA 4·10⁻²² contro 1·10⁻²²
  letto, a 10 µA 3,4·10⁻²⁴ contro 7·10⁻²⁵; 2N5087 a 1 mA 2,6·10⁻²¹ contro ~1·10⁻²¹.
- **E5 regge**, caso peggiore (`tb_e3_e5_ldr.cir`, curva D, +10 dB, 430 Ω), dB SPL a 1 m con la
  formula di NC-028:

  | Flicker dei bipolari | E5 | dB SPL | Margine sul tetto di E5 |
  |---|---|---|---|
  | nessuno (L46b) | 5,083 µV | 7,6 | 5,83 dB |
  | tipico della classe, KF 5·10⁻¹⁴ | 5,312 µV | 8,0 | 5,45 dB |
  | **il tetto, KF 1·10⁻¹³** | **5,531 µV** | **8,3** | **5,10 dB** |
  | 10× il tetto | 8,568 µV | 12,1 | 1,30 dB |

  Una stanza silenziosa sta a 25–35 dB(A).
- **Quanto flicker romperebbe E5.** L'eccesso al quadrato cresce linearmente con KF (10× il
  tetto dà 10,0× l'eccesso): E5 tocca 9,95 µV a **~15 volte il tetto**, ~31 volte il tipico. In
  angolo 1/f con AF = 1: tutti i bipolari insieme a ~84 kHz, il solo VAS a ~157 kHz, il solo
  specchio a ~412 kHz. Le curve pubblicate mettono l'angolo fra qualche decina di Hz e qualche
  kHz.
- **Chi domina col flicker**: il VAS (Q122), poi il lato d'uscita dello specchio (Q121B) e i
  cascode; pozzi, moltiplicatore di Vbe e finali spostano E5 di meno di 0,001 µV anche con un
  angolo di 100 kHz. Per questo il tetto dato **per scelta** ai finali e al MMBT5551 non pesa.
- **Il circuito non cambia.** Nessuna leva da misurare: il mandato le chiedeva solo se E5 non
  reggeva.

## Alternative scartate

- **Lasciare NC-004 aperta fino alla misura sul prototipo**: G1 bloccato da un rischio che il
  banco mostra a 15× di distanza.
- **Chiudere solo la metà del rumore**: la distorsione ha già tetti decidibili (ADR-055) e cifre
  dei modelli del costruttore dentro di essi; il tetto di THD+N e l'ascolto restano comunque al
  prototipo per ADR-055 e P6.
- **Il valore tipico (5·10⁻¹⁴) invece del tetto**: le curve non sono dei pezzi esatti e lo
  specchio è attribuito alla famiglia; il caso peggiore dichiarato da Linear Systems è ~2× il
  tipico.
- **Riscrivere la scheda del costruttore** nei quattro modelli copiati byte per byte: si
  perde la verifica col `diff` delle righe non di commento. La riga KF/AF va in coda al file,
  fuori dal blocco del costruttore (ngspice la unisce alla scheda, e sui MJE sovrascrive il
  `KF=0 AF=1` del costruttore: misurato).

## Da riaprire se

- Il prototipo misura un rumore in uscita sopra quello previsto col tetto, in particolare sotto
  1 kHz: il tetto era ottimista, e il margine (15×) va rifatto con la misura.
- Si trova una curva di rumore del LS352, del MMBT5401/2N5401 o del MMBT5551/2N5551 più alta del
  tetto.
- Il blocco cambia dove il flicker pesa (VAS, specchio, cascode): la scansione per gruppo di L44
  va ricorsa (`data/2026-10-01/L44/script/banco.py`).
