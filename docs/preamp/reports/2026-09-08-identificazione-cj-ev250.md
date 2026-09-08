# Identificazione del finale: cj Evolution 250 = MV50 in triodo

Data: 2026-09-08 · Tipo: report (datato)

Aggiorna la sezione "Dati non verificati" di
`2026-09-08-analisi-catena.md`, dove le specifiche del finale erano
segnalate come **prese da annunci d'asta e non dal costruttore**.

## La fonte

L'utente aveva scritto all'assistenza clienti **conrad-johnson** nel
febbraio 2025 e conserva lo scambio di email. Due informazioni, dal
costruttore:

1. **«The EVO250 began life as the MV50. The only difference is that the
   EVO250 is configured for triode operation.»**
2. **«The EV250 is rated at 30 watts.»**

*(Provenienza registrata come "email dell'assistenza clienti
conrad-johnson, febbraio 2025". I dati personali dello scambio non sono
riportati nel repository.)*

Questo cambia lo stato della fonte da "annuncio d'asta" a **costruttore**,
e apre l'accesso al manuale ufficiale dell'MV50, che esiste ed è
pubblicato da conrad-johnson.

## Specifiche MV50 (manuale ufficiale)

| Parametro | Valore |
|---|---|
| Potenza | 45 W/ch RMS su 4/8/16 Ω, 30 Hz–15 kHz, ≤1% THD/IMD |
| **Sensibilità** | **750 mV** a piena potenza |
| **Impedenza d'ingresso** | **100 kΩ** |
| Valvole finali | EL34 / 6CA7 |
| Fase | Non invertente |
| Risposta | 20 Hz – 20 kHz +0 / −0,5 dB |
| Distorsione a piccolo segnale | < 0,1% a centro banda |

## Cosa vale per l'EV250

**Confermato**: l'impedenza d'ingresso di **100 kΩ**. Il telaio e lo
stadio d'ingresso non cambiano nella conversione a triodo — cambia la
connessione dello stadio finale. Il requisito E4 del preamplificatore
(Zout costante e bassa) resta dimensionato correttamente.

**Confermato**: **30 W**, non i 25 W trovati online.

**Non pubblicata**: la sensibilità dell'EV250. La conversione a triodo
riduce il guadagno dello stadio finale, quindi il dato dell'MV50 non si
trasferisce tal quale. Si può però **delimitare** fra due ipotesi
estreme, ed è sufficiente.

### Ipotesi (a) — rete di controreazione invariata

Se cj ha toccato solo la connessione dello stadio finale, il guadagno ad
anello chiuso resta quello dell'MV50:

- MV50: √(45 × 8) = 18,97 V da 750 mV → guadagno **25,3×**
- EV250 a 30 W: √(30 × 8) = 15,49 V → sensibilità **612 mV**

### Ipotesi (b) — sensibilità invariata

- Sensibilità 750 mV, 30 W → guadagno **20,7×**

### Intervallo risultante

**Guadagno di tensione del finale: 20,7× – 25,3×**, cioè
**26,3 – 28,1 dB**. Uno scarto di soli **1,8 dB**.

## Verifica: la diagnosi regge?

Sì, e meglio di prima. Ricalcolando l'attenuazione che il Technics
doveva applicare per un ascolto normale (0,5 W = 2,0 V ai morsetti,
partendo dai suoi 18,0 V d'uscita):

| Ipotesi | Guadagno finale | V richiesta all'ingresso | Attenuazione |
|---|---|---|---|
| (a) | 25,3× | 79,1 mV | **47,1 dB** |
| (b) | 20,7× | 96,8 mV | **45,4 dB** |

**La manopola dell'utente indicava 46 dB — cioè esattamente in mezzo ai
due estremi.**

Il conto precedente (45,6 dB, basato su 25 W / 670 mV da fonti non
verificate) cadeva anch'esso nell'intervallo. **La diagnosi di ADR-001 è
robusta su tutto il campo plausibile**: non dipende da quale delle due
ipotesi sia vera.

## Conseguenze per il progetto

**Nessuna modifica alla topologia.** Con il preamplificatore a guadagno
unitario, l'attenuazione richiesta all'ascolto normale diventa:

| Ipotesi | Attenuazione con il nuovo preamp |
|---|---|
| (a) | 30,7 dB |
| (b) | 28,9 dB |

Cioè **~29–31 dB**, contro i ~29 dB stimati in precedenza. L'attenuatore
a scatti da 10 kΩ lavora a metà corsa in entrambi i casi: invariato.

**Headroom**: 30 W su Klipsch Heresy da 96 dB/1W/1m danno **110,8 dB a un
metro**. Ancora più margine di prima. La potenza non è un problema.

## Resta aperto

La sensibilità esatta dell'EV250 non è pubblicata e non è stata chiesta
al costruttore. **Non è necessaria**: l'intervallo di 1,8 dB è troppo
stretto per cambiare qualsiasi decisione presa finora. Se un giorno
servisse (per esempio per dimensionare esattamente il +10 dB di ADR-004),
si può chiedere all'assistenza cj, che si è già dimostrata disponibile.

## Fonti

- Assistenza clienti conrad-johnson, email di febbraio 2025 (in possesso
  dell'utente).
- [Manuale ufficiale MV50, conrad-johnson](https://conradjohnson.com/owners-manuals/mv50man.pdf)
- [MV50, HiFi Engine](https://www.hifiengine.com/manual_library/conrad-johnson/mv50.shtml)
- [conrad-johnson, prodotti vintage](https://conradjohnson.com/vintage-conrad-johnson-products/)
