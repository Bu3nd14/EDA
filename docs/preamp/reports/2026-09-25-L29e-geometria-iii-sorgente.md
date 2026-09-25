# L29e — la geometria iii nel sorgente (2026-09-25)

**La geometria iii di ADR-044 è in `circuits/`, e il sorgente riproduce le celle peggiori di L29d2
esattamente: 18 righe di verdetto su 18 uguali al banco, scarto 0 alla quarta cifra, 0 fuori.
La parte del mute di NC-028 è confermata sul sorgente.** Nessuna ADR nuova: il cablaggio è
quello che ADR-044 descrive.

- **Dati**: `data/2026-09-25/L29e/`, con README.
- **Il sorgente**: `circuits/preamp/preamp_audio.py`, la netlist rigenerata.

## 1. La decisione dell'utente

La sola scelta che il mandato lasciava aperta: il bleed dal lato del condensatore. Nel deviatore
conta solo nel ms del trasferimento, e nessuna corsa l'aveva misurato senza. Domanda posta il
2026-09-25, con le due strade (tenerlo, o toglierlo dopo una prova). Risposta: **«Tenerlo»**.
Nel sorgente:
- 470 k sulle fisse: `R167`, `R168`, `R367`, `R368`;
- 220 k sulla principale: `R264`, `R464`.

## 2. La piedinatura, letta

`vendor/relays/omron/G6K/en-g6k.pdf`, **pagina 6 del PDF** (il mandato diceva 7, che è quella
del bistabile G6KU). Riquadro «G6K-2F-Y, Terminal Arrangement/Internal Connections (TOP VIEW)»,
reso a 600 dpi, stato diseccitato:

| Polo | Perno (COM) | Appoggio (NC) | Aperto (NO) |
|---|---|---|---|
| 1, riga bassa | 3 | 2 | 4 |
| 2, riga alta | 6 | 7 | 5 |

Coincide con l'unica copia della mappa, `preamp_audio.py` righe 120–122 (letta in L21). Ogni polo
ha i tre capi separati: il deviatore si fa, e il «Da riaprire se» di ADR-044 sulla piedinatura non
scatta.

## 3. Il cablaggio

Per ciascuna uscita, e su entrambi i canali:

| Capo | Net | Prima di L29e |
|---|---|---|
| COM (3 / 6) | il lato del condensatore, `*_FIXCk` / `*_MAINC` (nuovo nodo) | il jack |
| NC (2 / 7) | GND | GND |
| NO (4 / 5) | il jack, unito al connettore | libero |

- **Il bleed del jack** resta sul jack: `R163`, `R166`, `R263`, e gli omologhi del canale R. È lo
  stato sicuro di ADR-044 punto 2.
- **I ref**: nessuno si rinumera. Le 6 resistenze nuove hanno ref esplicite (limitations #22),
  verificato sul diff dei ref prima e dopo.
- **L'ERC di SKiDL** passa da 48 a 42 avvisi. Spariscono i 6 «Unconnected pin» degli NO di
  K2–K4; nessun avviso nuovo. Le fusioni di net sono le stesse, e cambia solo il nome che SKiDL
  sceglie, come già in L17.
- **Il diagramma a blocchi** (2f) è ridisegnato: condensatore → scarico lato C → deviatore in
  serie → scarico al jack. L'asserzione nuova è sui valori dei bleed lato C.

### P7, riletto
Col mute inserito va a massa il **lato del condensatore**, attraverso il contatto NC. Prima ci
andava il **jack**, dall'altra parte dello stesso condensatore. Lo stadio vede lo stesso carico
nei due casi: 47 Ω più 4,7 µF verso massa.
- `tb_mute_corto.cir` (L17) mette a massa il lato jack con 0,01 Ω, che resta il caso peggiore
  contro gli 0,1 Ω del contatto. Le cifre P7 di L17 valgono anche per la iii.
- I casi di corto al connettore (2–4) sono a mute rilasciato: la serie chiusa aggiunge 0,1 Ω ai
  47, e il deck, senza, resta il caso peggiore.

La nota è nel sorgente e nell'intestazione del deck, che per il resto è invariato. **In più**: a
mute inserito, un corto esterno sul jack è ora isolato dal suo stadio. Non diventa per questo una
protezione dai corti.

## 4. Il 2e

`check_relay_safe_state.py` verificava per il mute solo «NC a massa», che passava sia sulla
derivazione al jack sia sulla iii. Ora asserisce la geometria **per intento**, non per pin:
- COM su una net con un condensatore e nessun connettore;
- NO su una net col pin di segnale di un connettore e nessun condensatore;
- un resistore a massa su entrambe;
- nessun altro contatto di mute sul jack.

Fatto fallire (`data/2026-09-25/L29e/falsi/`, `genera_falsi.py`, `esito.csv`):

| Variante | rc atteso | rc | Cosa dice |
|---|---|---|---|
| netlist di oggi | 0 | 0 | 6 jack su NO |
| netlist di `main` (derivazione al jack) | 1 | 1 | COM sul jack, NO scollegato, su 6 poli |
| NC↔NO del polo 2 di K2 (NC-014) | 1 | 1 | NC non a massa, NO a massa, poli diversi |
| COM↔NO del polo 1 di K4 | 1 | 1 | COM sul jack, NO sul lato C |
| senza `R167` (bleed lato C) | 1 | 1 | lato C senza resistore a massa |
| senza `R263` (bleed del jack) | 1 | 1 | jack senza resistore a massa |

## 5. Il deck versionato, generato dalla netlist

Il blocco CANALE **non cambia**: è la rete d'uscita universale del banco, e i quattro deck
`tb_v2_mute_*.cir` ne dipendono per identità. Cambia la configurazione del deck versionato.
`genera_tb_v2_casopeggiore.py` ha una matrice nuova, `sorgente`, che diventa il default:
- legge `circuits/preamp/preamp_audio.net` col parser e col controllo del 2e, importati: una
  sola definizione;
- rifiuta se la netlist non è la iii. Provato sulla netlist di `main`: rifiuta, e non scrive
  nulla;
- ricava i bleed lato C, uguali sui due canali;
- rifiuta se il bleed del jack non è `RBLx` del blocco.

Dal banco restano:
- il contatto aperto a 0,1 pF (datasheet, L29d2);
- il trasferimento di 1 ms (ipotesi);
- 0 pF di cavo e 100 kΩ di carico (il caso peggiore).

**La differenza dichiarata**:

| Controllo | Esito |
|---|---|
| `--matrice l29c` contro il deck versionato di `main` | byte-identico |
| `--matrice l29d2` contro `L29d2/deck/tb_v2_l29d2.cir` | byte-identico |
| `L29d2/script/identici.sh` (8 deck di L29c e L29d), prima di riscrivere il deck versionato | 8 su 8 identici |
| `script/confronto_deck.py`, deck dal sorgente contro L29d2 | netlist identica (210 righe), 135 corse su 135 identiche, 183 righe di manifesto su 183 presenti; nel banco in più solo `c100`, `r10k`, `k5` (135 ciascuna) e il controfattuale N (8) |

Da L29e, `identici.sh` di L29d2 non vale più per il deck versionato (il default è cambiato). Si
confronta con `--matrice l29c` scritto in un file temporaneo.

## 6. Le celle peggiori sul sorgente

Dal deck versionato rigenerato, con gli script di L29c: 17 corse (le 5 celle e i loro
riferimenti), 8 in parallelo.
- **17 rc=0**, nessun «Transient op» (#33);
- `@cks*[capacitance]` = 1e-13 (#29);
- 14 min la più lunga, non i 36 attesi.

Criterio, dichiarato prima di leggere: stesso esito e scarto ≤ 1 % sopra 1 nV (0,01 dB per S).
Fonte: `tabella_sorgente.csv`.

| Cella | Grandezza | Sorgente | Banco L29d2 | Scarto |
|---|---|---|---|---|
| `gm0x10_lz_c` (cambio a relè chiuso) | A_ins | 0,1704 µV | 0,1704 µV | 0 |
| `x01000_dpmaxmax_c` (dispersione) | A_ins / A_rel | 0,491 / 69,69 µV | 0,491 / 69,69 µV | 0 |
| `x01000_dpmaxmax_i` | A_ins | 8,914 µV | 8,914 µV | 0 |
| `on_r300p` (accensione) | A_ins | 4,416 µV | 4,416 µV | 0 |
| `mh01_1k` (musica) | S_ins / S_rel | 7,163 / 5,445 dB | 7,163 / 5,445 dB | 0 |
| `mh01_20` (musica) | B2 / S_ins | 8,715 µV / 7,158 dB | 8,715 µV / 7,158 dB | 0 |

**18 righe su 18 uguali, 0 fuori** (`verdetto.py`: «NON REGGE: 0 su 18»). È l'esito atteso: il
deck dal sorgente è, corsa per corsa, quello di L29d2. Il valore di questo passo è un altro.
- **La catena è chiusa**: la configurazione che il banco simula è quella che la netlist dice, e
  il generatore lo verifica a ogni rigenerazione. La misura su cui l'utente ha chiuso la parte
  del mute di NC-028 è la misura del circuito che sta in `circuits/`.
- **I limiti restano quelli di L29d2**: il contatto a 0,1 pF e il trasferimento di 1 ms non vengono
  dalla netlist, e il vincolo di layout (G2, ≤ ~2,4 pF fra lato C e jack) resta aperto.

## 7. Cosa resta

- **NC-028**: la parte del mute è confermata sul sorgente. Resta aperta e bloccante per lo
  spegnimento (L30).
- **L36**, il prossimo: il guadagno interbloccato dal mute (ADR-041). «Col jack a massa» di
  ADR-038 punto 4 si legge «col lato del condensatore a massa e il jack staccato».
