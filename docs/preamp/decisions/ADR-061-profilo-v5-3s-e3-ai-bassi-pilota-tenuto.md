# ADR-061 — Il profilo v5 del mute a 3 s con la cima di 7 mA; E3 nella sfumatura si giudica ai bassi; il pilota esponenziale resta; l'impronta propria della NSL-32SR3

Data: 2026-10-03 · Stato: accettata

**Rapporti con le decisioni precedenti.** Supera ADR-040 sul solo profilo (v4 → v5; il criterio di S
resta). Precisa ADR-039 (il profilo è simmetrico, 3 s per verso, come in ADR-059) ed E3 durante la
sfumatura (REQUIREMENTS, «Nota su E3 — durante la sfumatura del mute»). Conferma ADR-049 e ADR-050
sul pilota (la cima è di ADR-060). Lo `Stato:` di ADR-040 non è ancora aggiornato: si allinea con
l'utente alla rigenerazione del dossier, insieme a quelli già in elenco (NEXT-SESSION).

## Contesto

L47b2b doveva portare il mute sulla NSL-32SR3 (ADR-058, ADR-059) con la cima del LED di 7 mA
(ADR-060): il profilo a 3 s ricalibrato, il pilota, il firmware e le misure sul preamp intero.
All'inizio l'utente l'ha diviso: **«Due parti»**. **L47b2b1** (questo): il profilo, la scelta del
pilota, le misure sul preamp intero con un pilota ideale, e l'impronta del LED, per la quale ha
scelto **«Impronta propria nel repo»**. **L47b2b2**: il pilota vero in `psu.py`, il firmware,
`VRELAY`, le catene a valle.

Dati e come rifarli: `data/2026-10-03/L47b2b1/README.md`. Report:
`reports/2026-10-03-L47b2b1-profilo-v5.md`. Modello della cella: «comportamentale da dati
pubblicati, una sola cella misurata nella regione del mute»; la sua distorsione non è modellata.

### Due fatti trovati

1. **La NSL-32SR3 sopra 100 kΩ si spegne a ~0,24 decadi/s** (il modello di ADR-058: è il più
   lento compatibile con 25 MΩ a 10 s). Il v4 compresso a 3 s non sfuma: nei primi 2,2 s la
   serie si ferma a ~100 kΩ e il livello scende di 1,3 dB, poi la derivazione fa 70 dB in 0,9 s.
2. **Il v4 compresso a 7 mA viola E3 al rilascio**: |Zin| a 20 kHz al connettore **88,7–94,0 kΩ**
   su tutte le curve (`tran` ngspice). Al rilascio la serie si riaccende mentre la derivazione
   striscia ancora sopra 100 kΩ. Il controllo «lungo la sequenza» di L29b guardava il solo ramo
   della cella (≥ 170 kΩ qui) e non lo vedeva (limitations #43).

### I numeri portati all'utente (banco ridotto di L47b1, curve A–E, `tran` ngspice)

Il banco ridotto è stato rifatto anche in Python (`banco/rapido.py`), verificato contro ngspice
entro 0,03 dB su S, e usato per cercare il profilo su famiglie di centinaia di profili.

| Strada | Inserimento / rilascio | S peggiore (≤ 20 dB) | E3 a 20 kHz nella sfumatura | Mute a d = 1 |
|---|---|---|---|---|
| v4 compresso (oggi) | 3 / 3 s | 16,4 dB | **88,7 kΩ** | −70,7…−79,0 dB |
| E3 ai bassi, tabella per verso | 3 / 3 s | 10,8 dB | 80,5 kΩ | −72,6…−80,3 dB |
| E3 ≥ 100 kΩ a ogni frequenza | 3 / 5 s | 12,2 dB | ≥ 102,2 kΩ | −77…−84 dB |
| E3 ≥ 100 kΩ a ogni frequenza | 3 / 4 s | 16,9 dB (rapido) | ≥ 102 kΩ | — |

Con il rilascio in 3 s **nessun profilo** tiene E3 ≥ 100 kΩ anche a 20 kHz (588 profili: il
migliore 99,7 kΩ con S oltre 20 dB).

Il pilota semplificato (NC-045), agli angoli (15–60 °C, Vbe ±18 mV, RC ±10 %), curve A–E:

| Pilota | Parti per le due stringhe | S peggiore | Mute | Note |
|---|---|---|---|---|
| Di oggi (ADR-049/050): DAC, convertitori esponenziali appaiati, calibrazione | ~30 | quello del profilo (10,9 dB col v5) | −72,6…−80,3 dB | qualunque tabella |
| P1 «un RC più un generatore di corrente» | — | **44,5 dB** (anche col criterio largo) | — | escluso dalla fisica: la corrente sale come 1 − e^(−t/τ) e attraversa le prime decadi in millisecondi |
| P2 un RC e un NPN con RE, senza calibrazione | ~12 | **17,8 dB** | **−68 dB** (minimo −70) | in basso la corrente varia di ~250× sugli angoli; E3 a 20 kHz 73,6 kΩ |

## Decisione

**Dell'utente**, il 2026-10-03, alle due domande coi numeri sopra:
- sulla sfumatura: **«3 s e 3 s, impedenza ai bassi»**;
- sul pilota: **«Tenere il pilota di oggi»**.
Prima, all'inizio del lotto: **«Due parti»** e **«Impronta propria nel repo»**.

1. **Il profilo v5**, simmetrico (la stessa tabella nei due versi), 3 s per verso, cima 7 mA,
   riposo 10 nA, interpolazione in log come il v4:
   - **serie**: 7 mA a d = 0 → 10 nA a d = 0,6, log-lineare; poi 10 nA;
   - **derivazione**: 10 nA fino a d = 0,155 → 7 mA a d = 1, log-lineare (sotto ~0,3 µA è ancora
     buia: agisce da d ≈ 0,3).
   Viene dalla famiglia a quattro parametri (serie fino a d = 0,6; derivazione da 0,1 µA a
   d = 0,3 alla cima, che sta sulla stessa retta). Una tabella per verso avrebbe dato 10,1 dB
   invece di 10,2 nel modello rapido, e un salto di corrente in un'inversione a metà corsa:
   scartata.
2. **E3 durante la sfumatura si giudica ai bassi**: |Zin| a 20 Hz ≥ 100 kΩ al connettore in ogni
   istante, in ogni posizione del trim e con ogni capacità del selettore; il minimo a 20 kHz si
   misura e si dichiara. Negli stati fermi E3 non cambia. PR-6 del PRB non cambia: «non carica il
   phono a valvole» riguarda il condensatore d'uscita del phono, cioè i bassi.
3. **Il pilota resta quello di ADR-049 e ADR-050**, con la cima di 7 mA (ADR-060) e la tabella
   v5. La semplificazione di NC-045 è scartata coi numeri. Lo realizza L47b2b2 (`psu.py`, il
   firmware, la calibrazione).
4. **L'impronta della NSL-32SR3 è del repo**: `library/preamp.pretty/NSL-32SR3_LED3.30`
   (`preamp:NSL-32SR3_LED3.30` in `preamp_audio.py`), dall'impronta KiCad coi terminali del LED a
   3,30 mm (Silonex 104058 Rev 07: 3,30 ± 0,13; KiCad 3,81) e la cella a 2,54 mm, centrata come
   l'originale. La prima libreria di impronte del repo: la pipeline del PCB (L49) dovrà
   nominarla nella sua tabella delle librerie.

## Le cifre del v5

**Banco ridotto, `tran` ngspice** (`banco/run/v5/`, `banco/tabelle/sfumatura_v5.csv`), curve A–E:

| | A | B | C | D | E |
|---|---|---|---|---|---|
| S inserimento (dB) | 8,97 | 9,36 | 9,22 | **10,21** | 8,04 |
| S rilascio (dB) | **10,88** | 10,52 | 10,53 | 10,53 | **10,88** |
| Mute a d = 1 (dB) | −79,7 | −74,3 | −73,2 | −80,3 | −72,6 |

**E3 lungo la sfumatura**, con l'AC del deck E3 negli istanti peggiori (`e3/e3_sequenza.csv`; trim
0/6/12, selettore 1 fF/22 pF/68 pF): **a 20 Hz ≥ 154,9 kΩ** (curva A, al rilascio, t ≈ 6,5 s); su
tutta la banda il minimo è a 20 kHz, **88,1 kΩ** (curva A, 68 pF), per circa 2 s per verso.

**Sul preamp intero** (il banco V2, `tb_v2_casopeggiore.cir` rigenerato col v5, pilota ideale;
`data/2026-10-03/L47b2b1/v2/`, metodo di V2): la matrice del deck versionato (111 corse; le 24 di
spegnimento escluse come in L29d2) e la matrice «curve» per A, C, D, E (18 corse ciascuna).
- **S regge ovunque**: ≤ 9,36 / 13,52 dB (inserimento / rilascio) sulle curve B, ≤ 10,21 / 12,29 dB
  sulle altre (limite 20).
- **A e B senza segnale reggono** col banco corretto (A ≤ 5,4 µV, all'accensione; B ≤ 0,004 µV).
- **B con musica a 20 Hz subito dopo il relè non regge**: 100,5–241,2 µV (curve D…E). È la musica
  che la NSL-32SR3 lascia passare nei 0,5 s fra d = 1 e il relè (1,4–3,4 mV di picco a 20 Hz,
  ~60–64 dB SPL col tono di prova a piena scala), che il passa-alto del metodo porta dentro la
  finestra di B2. Il rimedio noto, il relè ≥ 2,5 s dopo d = 1 (B2 previsto ≤ 81 µV), l'utente non
  l'ha preso: **«0,5 s com'è»**. Aperta **NC-053**.
- **Il banco è stato corretto** (scelta dell'utente: «Sì, correggere il banco»): l'offset del primo
  stadio faceva passare 20 nA nelle celle, e dava un click di 211 µV a metà sfumatura che il
  circuito non ha (0,38 µV corretto; limitations #44).
- Le corse a 20 Hz delle curve C ed E corrono con `option trtol=1` (E anche `rshunt=1e12`):
  limitations #42, spostamenti dichiarati ≤ 0,14 e ≤ 4,6 µV.

**Il relè resta a 0,5 s dopo d = 1** (ADR-039, il contratto di J3): scelta dell'utente.

## Cosa costa

- **A 20 kHz** l'ingresso scende a ~88 kΩ per circa 2 s in ogni verso, con la musica già
  attenuata. Ai bassi resta sopra 150 kΩ.
- **Il pilota** resta il più complesso dei tre: ~30 parti e la calibrazione nel firmware.
- **Nessuna parte nuova** per il profilo: solo la tabella (firmware, L47b2b2) e i banchi.

## Alternative scartate

- **Il v4 compresso**: S 16,4 dB e E3 88,7 kΩ a 20 kHz al rilascio.
- **Rilascio in 5 s** (E3 ≥ 100 kΩ a ogni frequenza, S 12,2 dB) e **in 4 s** (S 16,9 dB): l'utente
  ha preferito 3 s per verso e il giudizio ai bassi.
- **Una tabella per verso**: nessun guadagno (10,1 contro 10,2 dB), e un salto di corrente in
  un'inversione a metà corsa.
- **P1** e **P2**: sopra.

## Da riaprire se

- Sul preamp intero S sfora 20 dB su una curva dell'inviluppo, o un'inversione a metà corsa del v5
  lo fa (matrice V2).
- Il prototipo misura la cella più lenta o più veloce di 0,24 decadi/s oltre 100 kΩ: il profilo e
  E3 dipendono da quel tasso, che è un'ipotesi dichiarata del modello.
- Un phono reale si dimostra sensibile al carico a 20 kHz durante la sfumatura.
- Il pilota di L47b2b2 non riesce a seguire la tabella v5 entro la tolleranza della calibrazione.
