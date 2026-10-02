# ADR-059 — Il JFET per il mute è provato e scartato sui numeri; la cella resta la NSL-32SR3, con un bersaglio di sfumatura di 3 s per verso

Data: 2026-10-02 · Stato: accettata — conferma ADR-058; precisa ADR-039 e ADR-040 sul tempo della sfumatura (bersaglio, non tetto del PRB)

## Contesto

Dopo L47a l'utente ha chiesto quali alternative ci fossero alla fotoresistenza (STATE, «Dopo
L47a»). Il mute sta a monte, davanti a 1 MΩ (ADR-038): lì i 50 Ω di un JFET non contano, e il
gate spegne con ~−9 V. Il JFET è entrato in prova contro la NSL-32SR3 di ADR-058, «sì, con una
prova prima», con la decisione dell'utente sui numeri. All'inizio di L47b l'utente ha diviso il
lotto: **L47b1** la prova e la decisione, **L47b2** il sorgente, il pilota, il firmware e le
catene a valle.

## La prova

Banco ridotto, lo stesso per le due celle: sorgente 1,5 Ω, la cella in serie e verso massa, R_IN
1 MΩ; tono di prova 2,7 V RMS; S col metodo di V2 (`scripts/v2_metodo.py`, importato). Dati e
come rifarli: `data/2026-10-02/L47b1/README.md`. Report: `reports/2026-10-02-L47b1-prova-mute.md`.

- **Il JFET**: MMBFJ112 di onsemi (DigiKey ~46 000 pz, Active, $0,30), modello del costruttore,
  angoli VGS(off) −1 / −1,68 / −5 V con copie rinominate verificate (22/22), il correttivo a
  metà Vds con due resistenze e il comando da 0 a −15 V attraverso una resistenza e un RC.
- **La NSL-32SR3**: il modello di L47a sulle curve A–E, il profilo v4 di ADR-040, con la cima del
  LED a 12 mA di ADR-050 (le prime corse a 20 mA, la cima del banco V2, sono nel report).

| | JFET | NSL-32SR3 (modello comportamentale, una sola cella misurata) |
|---|---|---|
| S, salto in 100 ms (≤ 20 dB) | **24–39 dB a 6 s**, 27–46 dB a 1 s: sfora sempre | 7–10 dB a 6 s; **3 s: 12,7–16,9 dB con la cima a 12 mA** (13,1–17,4 a 20 mA), A–E; 20–22 dB a 2 s |
| Distorsione nella sfumatura | **20–60 %** a 1 kHz su quasi tutta la discesa | non modellata (il modello è un resistore lineare) |
| Distorsione fuori mute | 4–33 % agli angoli tipico e −1 V; 0,005 % solo a −5 V | non modellata |
| B al jack, mute fermo | 124–186 µV (35–38 dB SPL) | cima 12 mA: 1 kHz 24–49 µV (21–27 dB SPL); 20 kHz 297–608 µV (42–49 dB SPL, dai 5 pF della VTL5C4) |
| \|Zin\| minimo (≥ 100 kΩ) | 49–84 kΩ a metà sfumatura all'angolo −5 V | 771 kΩ in gioco, 1,48 MΩ in mute |
| Rumore al jack | trascurabile (~0,4 µV calcolato) | trascurabile (~0,4 µV calcolato) |
| Costo per le 4 celle | ~$1,20 più ~12 resistenze e 4 condensatori | ~$16 |

**Il limite del JFET è fisico, non della geometria.** Un JFET è un resistore lineare solo finché
la tensione ai suoi capi resta piccola rispetto a Vgs − VGS(off). Una sfumatura, a metà strada,
mette ai capi dell'elemento che sfuma metà del segnale (1,9 V di picco) proprio dove la sua
resistenza vale quella del partitore, cioè a pochi mV dal pinch-off: il JFET limita la corrente
invece di resistere. Provato con il caso più favorevole possibile (`limite_jfet.py`): partitore
a L con 1, 10, 33 kΩ in serie e il JFET verso massa, gate da una sorgente **ideale** Vg = Vd/2 +
Vc. **THD 6–30 % fra −1 e −20 dB** a tutti gli angoli. La controprova: lo stesso deck con 50 mV
invece di 3,8 V dà 0,0002–0,0009 % su tutta la discesa. Il banco vede la distorsione bassa; quella
alta viene dai 2,7 V RMS del progetto in quel punto.

## Decisione

Le parole dell'utente, alla domanda con la tabella: **«NSL-32SR3»**; e sul tempo della
sfumatura: **«proviamo target a 3s»**.

1. **La cella del mute resta la NSL-32SR3** (ADR-058 confermata). Il JFET è registrato come
   provato e scartato, coi numeri sopra.
2. **Il bersaglio di sfumatura è 3 s per verso.** È un **bersaglio di progetto**, non un tetto del
   PRB: l'utente ha detto «proviamo». Sul banco ridotto, col profilo v4 compresso a 3 s e la cima
   a 12 mA, S vale 12,7–16,9 dB sulle cinque curve (il caso peggiore la curva D, 3,1 dB di
   margine). Un tetto
   scritto nel PRB, se l'utente lo vorrà dopo la misura sul preamp intero, vuole un'ADR (ADR-053).
3. **L47b2** porta la NSL-32SR3 nel sorgente col profilo a 3 s, decide la cima del LED, e misura
   sul preamp intero.

## Perché

- Il JFET sfora S a ogni tempo provato e distorce del 20–60 % nella sfumatura. Rimediarlo vuole
  un'altra architettura: resistenze fisse in serie (che portano rumore ed E3 in mute), più stadi
  a L per arrivare al residuo di B, gli interruttori in serie col gate isolato da un diodo. Sono 4–6
  JFET per canale, e la distorsione a sfumatura poco profonda **resta**, per il limite sopra.
- La NSL-32SR3 passa S su tutto l'inviluppo A–E a 3 s, con le cifre da modello che lo dicono.
- 3 s invece di 6 s: è la direzione che l'utente aveva già accettato per NC-045 («sono disposto a
  cambiare e a ridurre il tempo di mute»), e il banco dice che regge.

## Cosa precisa, e cosa si deve ancora verificare

- **Conferma ADR-058**; **precisa ADR-039** (Td = 6 s) **e ADR-040** (il profilo v4): il tempo
  passa a un bersaglio di 3 s per verso, da verificare sul preamp intero. Il profilo v4 è stato
  compresso, non ricalibrato sull'inviluppo della NSL-32SR3: lo fa L47b2.
- **Da misurare in L47b2, col banco V2 sul preamp intero:**
  - S col profilo a 3 s e il pilota vero (NC-049);
  - **B a 20 kHz prima che chiuda il relè**: 42–49 dB SPL al jack sul banco ridotto, dai 5 pF di
    cella che il modello prende dalla VTL5C4 (un'ipotesi di L47a). ADR-038 contava già sul relè
    al jack (≈ 0,57 mV a 20 kHz calcolati); va visto quanto dura prima della chiusura;
  - E3 ed E5 sul circuito vero.
- **La cima del LED** (ADR-050, 12 mA): il declassamento della NSL-32SR3 non è pubblicato. Ipotesi
  dichiarata o domanda al costruttore (techsupport@advancedphotonix.com), in L47b2.
- **Le cifre della NSL-32SR3 non portano distorsione né rumore**: il modello non li ha. La
  letteratura (ESP, «Muting Circuits», citata in ADR-038) parla di «very low distortion during the
  transition». Nessun agente giudica come suona: il giudizio resta dell'utente e del prototipo.

## Alternative scartate

- **Il JFET nella geometria di ADR-038** (serie + derivazione, correttivo resistivo, comando RC):
  sopra.
- **Il JFET col correttivo ideale in un partitore a L**: distorce lo stesso (6–30 % fra −1 e
  −20 dB). È il limite fisico, non un difetto della realizzazione.
- **Un JFET a più stadi** (resistenze in serie, interruttori isolati da diodi, due derivazioni):
  4–6 JFET per canale, rumore e E3 peggiori, e la distorsione resta. Non simulato oltre il limite
  sopra: il limite basta a escluderlo.
- **Un tetto di 4 o 6 s nel PRB**: l'utente ha preferito un bersaglio di 3 s da provare.
- Relè a gradini, MOSFET contrapposti, VCA e integrati di volume: già scartati con l'utente prima
  di L47b (STATE, «Dopo L47a»).

## Da riaprire se

- Sul preamp intero S a 3 s sfora 20 dB su una curva dell'inviluppo A–E.
- B a 20 kHz prima del relè risulta udibile, e il relè al jack non lo copre.
- Un prototipo della NSL-32SR3 mostra distorsione nella sfumatura che l'utente giudica udibile.
- Il mute si sposta in un punto del circuito dove il segnale è sotto ~50 mV: lì il JFET torna
  pulito (controprova di L47b1).
