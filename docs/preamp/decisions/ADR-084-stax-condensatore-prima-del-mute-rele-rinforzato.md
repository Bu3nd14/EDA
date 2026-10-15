# ADR-084 — Il condensatore della Stax resta prima del relè di mute, e il relè di mute della Stax diventa a isolamento rinforzato

Data: 2026-10-15 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Supera ADR-082 punto 1 nella prima parte** (il condensatore da 1 µF della fissa 2 fra il relè di
  mute K3 e il jack) e ne **attua la riserva**: le prove di L60c1 non passano, quindi il condensatore
  resta dov'è e K3 diventa un relè con isolamento rinforzato fra bobina e contatti.
- **Precisa ADR-081 punto 1**: il condensatore da 1 µF film della fissa 2 sta **fra la 47 Ω e K3**,
  nel posto del 4,7 µF di oggi.
- **Conferma ADR-044** (geometria iii) sulla fissa 2: comune al lato del condensatore, NC a massa, NO al
  jack, bleed da 470 k sui due lati.

## Contesto

L60c era la terza parte di L60. L'utente l'ha divisa all'inizio («Prima la prova»): prima le misure
sul banco, senza toccare il sorgente (**L60c1**), poi il sorgente e le prove complete (**L60c2**).
Il dubbio era stato visto leggendo ADR-044 e V2. Con i contatti a monte del condensatore, a mute
inserito la sua armatura d'ingresso va a massa e al rilascio risale alla continua del buffer F2, così
ogni mute porta quella continua alla Stax.

Il banco di L60a (`data/2026-10-15/L60c1/`, 187 corse, tutte col carico della Stax) confronta tre
geometrie sulla fissa 2. Le due corse di riferimento riproducono L60a: il blocco F2 al rail dà
117,5 ms, K3 sul NO dà 12 V per sempre.
- **G0**, la geometria di oggi con 1 µF.
- **G1**, la geometria di ADR-082: 47 Ω → K3 → 1 µF → jack; G1b è la stessa col bleed del jack a 220 k.
- **G2**, due condensatori: 10 µF prima di K3 e 1 µF dopo; G2b è la stessa col bleed del jack a 220 k.

| | Gradino del mute (soglia 100 µV) | Blocco al rail (≤ 125 ms) | K3 che cede, peggiore | 20 Hz a −5 % (≤ 0,2 dB) |
|---|---|---|---|---|
| G0 | 0 | 118–124 ms | **12 V per sempre** | 0,178 dB |
| G1 | **6,0–27,3 mV** (77–90 dB SPL all'orecchio) | **129–135 ms** | 110–115 ms | 0,149 dB |
| G1b | **6,0–27,3 mV** | 116–122 ms | 99–104 ms | 0,182 dB |
| G2 | 0 | 108–113 ms | **131–138 ms** (1 kΩ) | 0,180 dB |
| G2b | 0 | 98–103 ms | **120–126 ms** (1 kΩ) | **0,220 dB** |

I tempi vanno dal condensatore nominale al +5 %. Il gradino va dalla continua nominale del buffer
(−5,7 mV) a ±20 mV di dispersione sull'ingresso di F2. Il pin di un rail aperto sui due di J1 non
porta niente su nessuna geometria (≤ 0,2 µV). L'inserimento a caldo del jack della Stax è nullo su
tutte.

## Decisione

Le parole dell'utente (2026-10-15), alla domanda posta per nome coi numeri qui sopra: **«Relè
rinforzato»**.

1. **Il condensatore da 1 µF film della fissa 2 resta prima di K3**, al posto del 4,7 µF di oggi:
   `BUFFER F2 → 47 Ω → 1 µF → K3 → jack`, nella geometria iii di ADR-044.
2. **K3 diventa un relè con isolamento rinforzato fra bobina e contatti.** Con l'isolamento rinforzato
   il cedimento bobina-contatti non è più un guasto singolo credibile, e la riga della scelta 6 su K3
   esce da P10. Il relè si sceglie sul datasheet in L60c2, a parità di funzione: due deviatori, bobina a
   12 V, contatti per segnale, trasferimento e capacità del contatto aperto da confrontare coi valori
   di ADR-044. Il «Da riaprire se» di ADR-044 sul relè che cambia si applica.
3. **K2 e K4** (le altre uscite) **restano G6K**: contano sulla protezione a valle (ADR-081).

## Perché

- **G1 non regge il mute.** Il gradino è la continua del buffer F2 e passa il filtro di V2 quasi intero:
  60–270 volte la soglia, un colpo da 77–90 dB SPL all'orecchio a ogni mute. Il bleed del jack non lo
  cambia. Col bleed da 470 k, in più, il blocco al rail sta 4–10 ms sopra i 125 ms, perché il
  condensatore vede solo il bleed del jack e la Stax (45,2 kΩ), non più anche quello del lato
  condensatore.
- **G2 regge il mute ma non il relè che cede.** Il relè che cede con 1 kΩ carica anche il 10 µF, e il
  colpo dura 131–138 ms. Accorciare il bleed lo porta a 120–126 ms e fa uscire i 20 Hz al −5 %. Il
  margine è di pochi millisecondi e di pochi centesimi di dB, con un condensatore in più per canale.
- **G0 regge tutto tranne il relè che cede**, e quel guasto si toglie alla radice con un relè fatto
  per non averlo. Era la riserva già decisa in ADR-082.

## Alternative scartate

- **G1** (ADR-082 punto 1 alla lettera): fuori dal gradino del mute di 60–270 volte, e dal blocco al rail
  col bleed da 470 k.
- **G2 da rifinire**: un altro giro sul banco per qualche millisecondo, e un condensatore in più.
- **Accettare il gradino di G1** rivedendo V2: un colpo da 77–90 dB SPL a ogni mute, sulla cuffia che
  il progetto vuole proteggere.

## Conseguenze

- **L60c2**:
  - il sorgente: `preamp_audio.py` col condensatore della fissa 2 a 1 µF (il commento di ADR-007
    riscritto con ADR-081 e ADR-084) e il valore e il commento di K3. Oggi i tre relè di mute nascono
    nello stesso ciclo: K3 diventa diverso;
  - le netlist, i disegni, il generatore di `tb_v2_casopeggiore.cir` (il condensatore della Stax);
  - le prove sul circuito: E9, P10 coi guasti di L45a che portano continua sul banco della Stax, V2,
    l'inserimento a caldo, e il controllo 2e se legge il valore del relè.
- **La scelta 6 su K3 si chiude** col relè, quando la parte è nel sorgente.
- **NC-042 avanza.**

## Da riaprire se

- Non si trova un relè a isolamento rinforzato, a due deviatori per segnale, che stia nella scheda e
  regga i valori di ADR-044. Si torna all'utente con G2 rifinita.
- Il relè scelto cambia il gradino del mute misurato da V2 sulla fissa 2.
- Cambia la continua del buffer F2 di un ordine di grandezza (un servo, un condensatore all'ingresso):
  allora G1 va rimisurata.
