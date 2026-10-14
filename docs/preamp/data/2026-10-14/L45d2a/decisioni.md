# Le decisioni sui rimedi, riga per riga (L45d2a)

Dalla sintesi di L45d1 (`../L45d1/fmea_sintesi.csv`, non riscritta) e dalle scelte di `../L45d1/scelte_L45d2.pdf`, coi numeri del PDF. Generato da `script/decisioni.py`.

**Righe alte e medie: 156.** Dopo ADR-071: **100 alte, 56 medie** (i 4 modi d'isolamento dei relè di mute passano ad alta). I 28 guasti del blocco dentro il criterio vanno alla diagnosi.

| Dove si realizza | righe |
|---|---|
| G2 | 2 |
| L45d2b | 88 |
| L58 | 38 |
| NC-062 | 4 |
| accettata | 24 |

| Scelta | Decisione | ADR | Dove | alte | medie (dopo ADR-071) |
|---|---|---|---|---|---|
| 1 | il rivelatore di continua apre il mute, toglie la linea dei rele' alla scheda audio e spegne i rail audio | ADR-072 | L45d2b | 31 | 6 |
|  | il rivelatore di continua apre il mute, toglie la linea dei rele' alla scheda audio e spegne i rail audio; col calore: i rail spenti tolgono anche il secondo guasto (scelta 10) | ADR-072 | L45d2b | 21 | 0 |
| 2 | accettata la riserva del firmware (muta in 2,2 ms invece di 1 ms) | ADR-073 | accettata | 10 | 0 |
| 3 | rivedere D510 / D511 e proteggere U502 dall'uscita sopra l'ingresso; il fusibile di rete resta a G2 | ADR-074 | L45d2b | 9 | 1 |
| 4 | limitare la corrente sul comando | ADR-075 | L45d2b | 7 | 0 |
|  | un limitatore sulla linea a 5 V della logica | ADR-075 | L45d2b | 1 | 0 |
| 5 | rivelato dal firmware (legge il comando del mute e stacca la linea dei rele' alla scheda audio) | ADR-076 | L58 | 8 | 2 |
| 6 | il rivelatore toglie la linea dei rele' alla scheda audio: la bobina non porta piu' 12 V sul segnale | ADR-072 | L45d2b | 7 | 0 |
| 7 | accettato come il corto della linea a 12 V (ADR-051) | ADR-077 | accettata | 0 | 10 |
| 8 | coperto dal rivelatore di continua, da verificare | ADR-072 | L45d2b | 0 | 2 |
| 9 | coperto dal rivelatore di continua, da verificare | ADR-072 | L45d2b | 0 | 2 |
| 10 | il rivelatore spegne i rail audio: il calore dura quanto il suo ritardo | ADR-072 | L45d2b | 1 | 0 |
| 11 | niente da scegliere: si verifica al pre-layout | — | G2 | 1 | 1 |
| 12 | nel lotto del moltiplicatore di Vbe | — | NC-062 | 4 | 0 |
| 13 | accettato per il colpo (dentro i 100 ms); il degrado silenzioso va alla diagnosi | ADR-071 | L58 | 0 | 28 |
|  | invariato: nessuno nel circuito: si vede e si ripara | — | accettata | 0 | 1 |
|  | invariato: nessuno: P9 (c), il corto di un rail, accettato | — | accettata | 0 | 2 |
|  | invariato: nessuno: il guasto non ha effetto, o il circuito lo mette gia' in sicurezza | — | accettata | 0 | 1 |

Le righe a bassa priorità decise da ADR-078: 9 sovratensioni dei rail (L45d2b, prima i massimi) e 8 standby acceso per guasto (L58). Il dettaglio riga per riga è nel CSV.
