# ADR-077 — Il ritardo fra mute e permesso che si perde: accettato come il corto della linea a 12 V

Data: 2026-10-14 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- È la **scelta 7** di `data/2026-10-14/L45d1/scelte_L45d2.pdf` (10 righe medie, L45c2).
- Estende ADR-051 a un'altra classe di guasti con lo stesso effetto. ADR-051 resta com'è.

## Contesto

Δ è il ritardo fra lo stacco dei jack e il rilascio dei relè di guadagno (ADR-045, ADR-046). Alcuni
guasti lo fanno perdere: U504 spento (la linea a 5 V persa), C523 o C528 aperti seguiti da U503
spento o dalla perdita di rete, D520 o D522 in corto, R524 aperta. Così i relè di guadagno cadono
fino a 4,3 ms prima che il jack si apra. Al jack arrivano **6,44 mV** (~70 dB SPL a 1 m), lo stesso
colpo già accettato per il corto della linea a 12 V (ADR-051). Due di questi guasti, D520 in corto
e R524 aperta, lo fanno perdere **a ogni mute**, senza nessun segno.

## Decisione

Parole dell'utente (2026-10-14): «Accettarlo e basta».

**La perdita di Δ per un guasto singolo è accettata**, come il corto della linea a 12 V: vale il
solo tetto di non-danno (0,87 V, ~112 dB). Non si aggiunge nessun controllo e il circuito non
cambia.

## Perché

- **Il colpo è lo stesso di ADR-051**, ~42 dB sotto il tetto. Una regola diversa per lo stesso
  colpo non si difenderebbe.
- **Anche ripetuto a ogni mute resta un click**: ~70 dB SPL di picco a 1 m, sopra l'obiettivo di
  2 mV (~60 dB) ma lontano da ogni danno. Chi ascolta lo sentirebbe, e questo è già un segno.

## Alternative scartate

- **Un controllo di Δ a ogni mute** (il firmware legge il permesso e il jack), dalla diagnosi:
  scartato dall'utente.
- **Una tenuta locale per il relè del trim e i relè di guadagno**, indipendente dalla linea dei relè
  e dal comando del mute: è la stessa alternativa che ADR-051 aveva scartato. Toglie Δ dalla linea
  comune, ma costa un pin fra le schede e rifà i banchi.

## Da riaprire se

- Una misura sul prototipo mostra un colpo di Δ perso sopra ~2 mV per ragioni che il banco non
  vedeva.
- La diagnosi (L58) trova di poter controllare Δ senza parti nuove: allora si porta all'utente come
  un'aggiunta gratuita.
