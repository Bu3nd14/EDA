# ADR-070 — La FMEA ha la forma standard: gravità, probabilità dai tassi normati, rilevabilità, priorità e rimedi candidati

Data: 2026-10-14 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- Non cambia nessun criterio: PR-23 / P9 (b), P9 (c) e PR-30 / P10 (ADR-069) restano il verdetto di
  ogni riga. Cambia la **forma** dell'analisi che chiude NC-042.
- Vale da **L45c2**. Le tabelle di L45a, L45b e L45c1 si riportano a questa forma **in L45d**, come
  primo passo, prima della decisione sui rimedi.

## Contesto

Le tabelle di L45a, L45b e L45c1 danno per ogni modo l'effetto misurato al jack e il verdetto contro
il requisito, e nient'altro. Mancano tre colonne che una FMEA ha di norma (IEC 60812): la gravità su
una scala, la probabilità del modo e la rilevabilità. Un condensatore che si apre e un relè di rete
che si salda oggi pesano uguale, e un guasto latente non si distingue da uno che il sorvegliante
vede. Manca anche la colonna dei rimedi: L45d dovrebbe scegliere su ~400 righe senza un ordine.

## Decisione

Da L45c2 ogni riga della FMEA ha queste colonne: **parte, funzione, modo, effetto** (misurato, al
jack principale e alle fisse, in V e in dB SPL), **verdetto** (il criterio di oggi), **gravità**,
**tasso** (FIT, con la fonte), **probabilità**, **rilevabilità**, **priorità**, **rimedi
candidati**. Parole dell'utente (2026-10-14): «di solito l'output di una FMEA si struttura almeno in:
Failure mode, effect, severity, occurrence (risk), mitigation»; e sulle tre scelte, «ok, tassi
normati, retrofit in L45d, scrivi l'ADR».

**Gravità**, ancorata alle soglie già firmate (dB SPL di picco a 1 m, al jack):

| Gravità | Che cosa succede |
|---|---|
| **1** | niente di percepibile: ≤ 100 µV (~33 dB SPL, la soglia di V2, sotto una stanza silenziosa) |
| **2** | una funzione persa o degradata senza colpo (non si accende, un comando non risponde, un LED sbagliato), o un colpo ≤ 2 mV (~60 dB, l'obiettivo di ADR-046) |
| **3** | un colpo udibile ma dentro il criterio: fino a 0,87 V (~112 dB), o sopra per non più di 100 ms |
| **4** | il criterio non è rispettato (P9 (b) o P10): danno possibile alla catena a valle |
| **5** | sicurezza: un componente oltre i suoi limiti termici (PR-22, P7, NC-062), la rete, il fuoco |

**Probabilità**, dal tasso di guasto del modo: il tasso della parte da **SN 29500** o **IEC 61709**,
portato alla temperatura della parte nel telaio caldo (60 °C d'aria, ADR-021) col modello di stress
della norma, e ripartito fra i modi con **FMD-2016**. Le classi (10 FIT ≈ un apparecchio su ~1100 in
dieci anni sempre acceso):

| Probabilità | FIT del modo |
|---|---|
| **1** | < 1 |
| **2** | 1–10 |
| **3** | 10–100 |
| **4** | > 100 |

**Rilevabilità**: **1** il circuito lo vede e mette in sicuro (il sorvegliante, Δ, il mute);
**2** lo vede subito chi ascolta (non suona, non si accende, un LED); **3** latente, non si vede
finché non arriva un secondo evento (lo spegnimento, la perdita di rete, un altro guasto).

**Priorità**, da una matrice e non da un prodotto:

| gravità ↓ · probabilità → | 1 | 2 | 3–4 | latente (rilevabilità 3), qualunque probabilità |
|---|---|---|---|---|
| **5** | alta | alta | alta | alta |
| **4** | media | alta | alta | alta |
| **3** | bassa | bassa | media | media |
| **1–2** | bassa | bassa | bassa | bassa |

**Rimedi candidati**: le opzioni, ciascuna col suo costo in parti quando si conosce. La scelta
resta all'utente in L45d, che aggiunge la gravità, la probabilità e la priorità **dopo** il rimedio.

La priorità ordina il lavoro di L45d e sostiene un'eventuale accettazione dichiarata. **Non
sostituisce il verdetto**: una riga fuori da P9 (b) o P10 resta fuori, qualunque sia la sua
probabilità.

## Perché

- **La probabilità separa casi che oggi sono uguali.** Una resistenza a film si apre a ~0,1–1 FIT,
  un elettrolitico al caldo a decine, un relè secondo le manovre. Senza dati di campo, i tassi
  normati sono il riferimento più difendibile, e la fonte si scrive riga per riga.
- **La rilevabilità è il punto debole di questo progetto.** I casi peggiori di L45c1 sono latenti:
  il NO di mute saldato e Q501 in corto restano invisibili fino allo spegnimento (3,4 V e 2,8 V al
  jack se poi si spegne U501). In un prodotto senza manutenzione un guasto latente aspetta il
  secondo evento.
- **Una matrice, non il prodotto gravità × probabilità × rilevabilità.** Il prodotto rende uguali
  casi che non lo sono (una gravità 5 rara e una gravità 1 frequente possono avere lo stesso numero), ed è il motivo
  per cui AIAG-VDA (2019) lo ha sostituito con una priorità d'azione a tabella.
- **Quattro o cinque classi, non dieci.** Senza dati di campo una scala da 1 a 10 dà una precisione
  che i tassi non hanno.
- **Il riporto delle tabelle vecchie va in L45d** perché è lì che servono tutte insieme: rifarle
  prima non cambia nessun numero misurato (la gravità viene dagli effetti già misurati, la probabilità
  dalle tabelle, la rilevabilità dal meccanismo).

## Alternative scartate

- **Probabilità a stima qualitativa** (frequente / rara): più veloce, ma non si difende davanti a un
  revisore e non si confronta fra lotti. Scelta dell'utente: tassi normati.
- **Il prodotto dei tre numeri** (RPN): vedi sopra.
- **Riportare L45a–L45c1 subito, prima di L45c2**: un lotto in più senza numeri nuovi. Scelta
  dell'utente: in L45d.
- **Lasciare la forma di oggi**: L45d sceglierebbe i rimedi senza sapere quali guasti sono rari,
  quali latenti e quali già visti dal circuito.

## Da riaprire se

- Per una classe di parti nessuna delle tre fonti dà un tasso o una ripartizione dei modi: si
  dichiara l'ipotesi riga per riga, e se le righe così diventano molte si torna all'utente.
- Il prototipo, o dati di campo, danno tassi diversi da quelli delle tabelle di una classe intera.
- In L45d la matrice mette nella stessa classe casi che l'utente vuole trattare in modo diverso.
