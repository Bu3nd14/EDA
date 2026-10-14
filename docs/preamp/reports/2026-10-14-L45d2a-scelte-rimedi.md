# L45d2a — le decisioni sui rimedi dei guasti singoli

Data: 2026-10-14 · Lotto: L45d2a (prima metà di L45d2) · Non conformità: NC-042 (avanza)

## In breve

L'utente ha diviso L45d2 in due parti: **«Prima decidere, poi costruire»**. Questa prima parte ha
preso tutte le decisioni: le due domande del «Da riaprire se» di ADR-070, le dieci scelte di
`data/2026-10-14/L45d1/scelte_L45d2.pdf` e le tre voci a bassa priorità della lista. Sono otto ADR,
**ADR-071…078**.

Il **circuito non cambia** e non c'è nessuna corsa nuova. Ogni riga alta e media della sintesi ha ora
una decisione e una destinazione (`data/2026-10-14/L45d2a/decisioni.csv`):

| Dove si realizza | righe alte e medie |
|---|---|
| **L45d2b**: il rivelatore, i diodi del grezzo, il comando | 88 |
| **L58**, la diagnosi | 38 |
| accettate | 24 |
| NC-062, il moltiplicatore di Vbe | 4 |
| G2, il pre-layout | 2 |

Dopo ADR-071 la sintesi conta **100 righe alte e 56 medie** (prima 96 e 60).

## Le domande e le risposte

Le domande sono state poste per nome, senza sigle. Le risposte dell'utente sono riportate tra
virgolette.

| Domanda | Risposta | ADR |
|---|---|---|
| Dividere il lotto? | «Prima decidere, poi costruire» | — |
| L'isolamento dei relè di mute (12 V permanenti, a media solo per la rarità): insieme a selettore e trim? | «Insieme, ad alta» | 071 |
| I 28 guasti del blocco dentro il criterio, a media solo per la latenza | «Mandarli alla diagnosi» | 071 |
| Scelta 1, il rivelatore di continua | «Sì, apre il mute e toglie la bobina» | 072 |
| Scelte 8 e 9, il filo del rail, il condensatore d'uscita in corto | «Coperte dal rivelatore» | 072 |
| Scelta 10 e le 21 righe col calore | «Togliere i rail al guasto» | 072 |
| Scelta 6, l'isolamento bobina-contatti | «Togliere la bobina al guasto» | 072 |
| Scelta 2, i sorveglianti ciechi | «Accettare la riserva del firmware» | 073 |
| Scelta 3, i corti del grezzo | «Rivedere i diodi e il regolatore» | 074 |
| Scelta 4, il comando e la logica | «Limitatore sui 5 V, Limitare la corrente del comando» | 075 |
| Scelta 5, il mute che non si inserisce | «Rivelarlo, alla diagnosi» | 076 |
| Scelta 7, il ritardo perso | «Accettarlo e basta» | 077 |
| Le sovratensioni dei rail | «Prima leggere i massimi» | 078 |
| Lo standby acceso, il tetto delle fisse | «Standby alla diagnosi» | 078 |

Le scelte 11 (il pre-layout) e 12 (il moltiplicatore di Vbe) non chiedevano una scelta.

## Le decisioni, per scelta

| Scelta | Decisione | ADR | Dove | alte | medie |
|---|---|---|---|---|---|
| 1 | il rivelatore apre il mute, toglie la linea dei relè, spegne i rail | 072 | L45d2b | 52 | 6 |
| 2 | accettata la riserva del firmware (2,2 ms) | 073 | accettata | 10 | 0 |
| 3 | rivedere D510 / D511, proteggere U502 | 074 | L45d2b | 9 | 1 |
| 4 | limite di corrente sul comando; limitatore sui 5 V | 075 | L45d2b | 8 | 0 |
| 5 | rivelato dal firmware | 076 | L58 | 8 | 2 |
| 6 | il rivelatore toglie la bobina | 072 | L45d2b | 7 | 0 |
| 7 | accettato come il corto della linea a 12 V | 077 | accettata | 0 | 10 |
| 8, 9 | coperti dal rivelatore, da verificare | 072 | L45d2b | 0 | 4 |
| 10 | il rivelatore spegne i rail | 072 | L45d2b | 1 | 0 |
| 11 | da verificare al pre-layout | — | G2 | 1 | 1 |
| 12 | nel suo lotto | — | NC-062 | 4 | 0 |
| 13 | 28 del blocco: accettati per il colpo, il degrado alla diagnosi; 4 invariati | 071 | L58 / accettata | 0 | 32 |

Le priorità sono quelle dopo ADR-071. Il dettaglio riga per riga è in `decisioni.csv`; il
riassunto generato è in `decisioni.md`.

**Basse, ADR-078**:
- 9 righe di sovratensione dei rail vanno a L45d2b: prima si leggono le tensioni massime delle
  parti, e il sorvegliante si aggiunge solo se serve;
- 8 righe di standby acceso vanno a L58;
- il tetto delle fisse resta a NC-046.

## Come è stato verificato

- `decisioni.py --prova` riconta la tabella del PDF dalla sintesi prima di decidere: **13 gruppi su
  13 uguali**, 156 righe.
- Dopo le decisioni, lo script verifica i conteggi attesi e si ferma se sono diversi: 100 alte e
  56 medie, 4 righe alzate, 28 guasti del blocco alla diagnosi, nessuna riga senza destinazione.
- Due numeri delle ADR sono stati riletti alla fonte:
  - il colpo di ADR-051 sul blocco di oggi è 6,44 mV (`reports/2026-10-14-L45c2-fmea-comando.md`);
  - Q505 è l'interruttore che porta `VRELAY` alla scheda audio, e U505 è il sorvegliante dei rail
    (`circuits/preamp/psu.py`).

## Che cosa resta

**A L45d2b** (la costruzione):
- il rivelatore di continua, cioè il mute, la linea dei relè e i rail, con la soglia contro la
  musica e la scarica dei rail misurata;
- D510 / D511 e la protezione di U502;
- il limite di corrente del comando e il limitatore sui 5 V;
- la lettura dei massimi per le sovratensioni;
- i guasti toccati rifatti, con le colonne dopo il rimedio di ADR-070;
- la chiusura di NC-042.

**A L58** (la diagnosi):
- il mute che non si inserisce;
- il degrado silenzioso dei 28 guasti del blocco;
- lo standby acceso per guasto;
- il rivelatore cieco (un guasto latente nuovo, ADR-072 «Da riaprire se»).
