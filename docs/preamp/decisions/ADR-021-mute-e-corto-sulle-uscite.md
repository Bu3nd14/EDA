# ADR-021 — Mute tenibile a tempo indefinito, e ogni uscita regge un corto

Data: 2026-09-14 · Stato: accettata — precisata da ADR-023 (classe A su ogni percorso ascoltabile: la classe B resta nei soli stadi che servono un'uscita mutata, in corto o con un apparecchio a bassa Zin)

## Contesto

ADR-012 metteva il mute «per qualche secondo». Ma ADR-019 ne ha fatto il
**permissivo del trim**, e chi regola il trim lo tiene inserito quanto vuole.
A mute inserito i contatti NC mettono a massa i jack a valle di 47 Ω e
4,7 µF, e lo stadio d'uscita va in classe B (**NC-001**). Un corto esterno al
connettore fa lo stesso sullo stesso nodo (**NC-010**), e il progetto non può
escluderlo.

Le decisioni sono dell'utente (2026-09-13, parole esatte in NC-001):
- il mute deve potersi tenere «a tempo indefinito a costo di cambiare la
  topologia»;
- «la classe B può essere accettata in mute, ma il mute non deve mettere a
  rischio la termica»;
- «non possiamo essere certi che le uscite non vengano messe in corto»;
- il requisito non deve escludere «la possibilità di staccare o mutare le
  uscite in maniera attiva».

I due numeri che mancavano li ha dati l'utente il 2026-09-14: **60 °C** di
ambiente nel telaio chiuso, **Tj ≤ 125 °C**.

## Decisione

**1. Il mute si tiene a tempo indefinito.** Supera la durata «qualche secondo»
di ADR-012. Il resto di ADR-012 resta: un relè di mute su tutte le uscite, a
riposo verso il silenzio.

**2. Ogni uscita regge un corto, e il requisito descrive l'esito, non la
tecnica.** Si considerano due condizioni:
- il **mute inserito**, come è cablato: oggi tutti e tre i jack a massa
  insieme;
- un **corto franco** (≤ 0,01 Ω) al connettore di **una qualsiasi** delle tre
  uscite.

In ciascuna, a tempo indefinito e con segnale presente, **nessun componente
esce dai propri limiti termici e di area di lavoro sicura**. Il dominio del
segnale è sinusoidale fra 20 Hz e 20 kHz, di ampiezza qualsiasi fino a E6
all'ingresso, con ogni posizione dell'attenuatore e ogni modalità di guadagno.
Il verbo, per ogni componente e ogni punto del dominio:

| | Criterio |
|---|---|
| a regime | **60 °C + P_media · RθJA ≤ 125 °C** (dispositivi attivi) |
| SOA | ogni punto istantaneo (V_CE, I_C) sta dentro la curva SOA pubblicata per la sua durata; oltre la curva più lunga pubblicata vale il criterio a regime |
| transitorio | fra l'inizio del corto (o l'inserzione del mute) e l'intervento di un'eventuale protezione, **Tj di picco ≤ 125 °C**, calcolata con la Zθ(t) del datasheet |
| resistenze | potenza ≤ quella nominale **a 60 °C** secondo il declassamento della parte scelta. Finché la parte non è scelta (L9), la verifica consegna la potenza richiesta come vincolo di distinta |
| contatti di relè | corrente RMS ≤ corrente nominale di conduzione (G6K-2F-Y: **2 A**) |

I numeri di oggi, senza dissipatore, letti dai datasheet in `vendor/`:

| Parte | RθJA | P_media massima |
|---|---|---|
| MJE15032/33, TO-220 | 62,5 °C/W | **1,04 W** |
| MMBT5401, SOT-23 | 403 °C/W (pad minimo; 357 su 15×15 mm) | **161 mW** |
| MMBT5551, SOT-23 | 417 °C/W | **156 mW** |
| LS352 (serie LS350), SOIC-8 | 435 °C/W per lato, ricavato dal declassamento di 2,3 mW/°C | **149 mW** per lato, 280 mW in tutto |
| LSK489, SOIC-8 | 417 °C/W per lato, ricavato da 2,4 mW/°C | **156 mW** per lato, 260 mW in tutto |

Con un dissipatore il verbo non cambia, cambia la catena termica:
RθJC + RθCS + RθSA al posto di RθJA.

**3. La classe B è ammessa in queste due condizioni, e solo in queste.** È
un'eccezione dichiarata a **T1**/ADR-003: con un corto al connettore è
inevitabile. Con i carichi normali di V1 la classe A resta richiesta. Un
apparecchio spento a valle con Zin bassa **non è un corto** e resta NC-010.

**4. La tecnica è libera:** limitazione di corrente, distacco attivo, mute
attivo, anche con i componenti ammessi da ADR-022. **Un mute in derivazione
non conta come protezione**: durante un corto ne aggiunge un secondo invece di
togliere il primo.

## Perché

- **Una verifica su una durata finita non chiude niente.** ADR-019 rende il
  mute tenibile per ore. Il criterio a regime è l'unico onesto, e comprende
  anche ogni temporizzatore.
- **Il mute è un caso particolare del corto:** stesso nodo, stessa fisica.
  Scriverli in un'unica decisione impedisce di chiudere una via sola, che è
  l'avvertimento di NC-010.
- **60 °C** è la stanza a 35 °C più ~25 °C di aumento in un telaio chiuso
  dentro una libreria (ADR-010). **125 °C** lascia 25 °C sotto i 150 °C
  assoluti di tutte le parti. È una scelta dell'utente con un ragionamento
  dietro, non un numero del datasheet.
- **Le resistenze e i contatti ci sono** perché l'utente ha chiesto di non
  mettere a rischio la termica, e una resistenza da 0,25 W con 1 W dentro è
  un rischio termico tanto quanto un transistor.
- **Il requisito resta neutro sulla tecnica** perché il distacco attivo e il
  mute in serie non vanno esclusi prima di avere i numeri.

## Alternative scartate

- **Classe B accettata «per la durata del temporizzatore»** (il mandato di
  L18): contraddiceva ADR-019.
- **Un'impedenza minima ammessa a valle** (NC-010, strada 2): è proprio il
  corto che il requisito chiede di reggere.
- **Prescrivere una resistenza in serie al contatto:** chiude la via del mute e
  non quella del corto esterno, e costa contro E4.
- **Tj ≤ 150 °C:** nessun margine. **110 °C:** avrebbe imposto un rimedio
  prima di sapere se serve.

## Da riaprire se

- La temperatura misurata nel telaio del prototipo **supera i 60 °C**.
- Cambiano i dispositivi d'uscita, il loro montaggio (un dissipatore) o il
  numero di uscite (i buffer di L17 sono un'uscita nuova da verificare).
- Entra una modalità di guadagno o un'ampiezza fuori dal dominio (L27 porta il
  +3 dB: dentro il dominio, ma va verificato).
