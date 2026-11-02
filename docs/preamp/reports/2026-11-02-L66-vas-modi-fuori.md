# L66 — Il VAS a 126 °C e i modi fuori dai quindici (2026-11-02)

Chiude **NC-076** (maggiore, prima di G1). Decisione **ADR-111**. Dati `data/2026-11-02/L66/` (README,
con la sezione «Rifare»).

## Il banco e i casi noti

Il banco del calore di L45d2b3b2b2, caricato per percorso come in L58b. Prima di leggere un numero
nuovo:
- il calore: 20 righe di `calore_sorg.csv` di L58b e 5 di `calore_fmje.csv` di L55, **775 celle, 0
  diverse**;
- la Stax: Q132_ce e Q133_ce alla cifra di L45d2b3b2b2;
- V4 a caldo: la base dà 2,7 dB, 0,000726 % e −131,7 dB, come L45d2b3b2b2;
- dopo la modifica, il sorgente nuovo ridà la variante misurata: 40 righe, 600 celle di potenza, 0
  diverse.

## 1. Il meccanismo (`meccanismo.csv`)

| | sano | Q132 in corto base-emettitore |
|---|---|---|
| uscita del blocco | −2,9 mV | **−13,6 V** |
| VAS Q122 | 10,7 mA, 0,142 W | **19,8 mA, 0,528 W** |
| limitatore Q193 | spento | 6,0 mA (al limite) |
| finale PNP Q133 | 20,6 mA | 25,5 mA, saturo |
| carico del VAS Q125 | 10,6 mA | saturo (NY a −14,75 V) |
| specchio d'ingresso | 2,2 mA | spento |

Senza la base-emettitore di Q132 il VAS pilota l'uscita direttamente attraverso R130 + R134 (32 Ω), e
tutta la tensione del moltiplicatore (2,0 V) cade sul finale PNP. Per tenere l'uscita a zero il VAS
dovrebbe fornire ~(2,0 − 0,6 − 0,6) / 22 Ω ≈ 35 mA. Il limitatore di ADR-099 ne concede ~20: l'anello
perde, l'uscita va al rail e il VAS resta al limite con ~27 V ai capi.

Nel blocco di prima di ADR-099 il VAS forniva quei ~30 mA e l'uscita restava a ~0: era il «degrado
silenzioso, 115 °C» della FMEA. **È il limitatore a fare del guasto un'uscita al rail.** D158 (il diodo
di ADR-095 sulla stessa giunzione) in corto è lo stesso guasto.

## 2. I modi fuori dai quindici (`confronto.csv`)

I 145 modi del blocco meno i quindici di ADR-099, le 11 delle parti nuove e i 28 di L58b, cioè 91,
rifatti sul sorgente contro la riga della FMEA (che portava il calore del blocco di prima di
ADR-097 / ADR-099):
- **fuori da P7 solo D158 in corto, 126 °C**;
- quasi tutti si scaldano meno: i finali da 87 a 79 °C col dissipatore, Q122 e Q146 in corto
  collettore-emettitore da 107 a 95 °C, Q125 aperto e R126 aperta da 91 a 79 °C;
- i picchi al jack uguali alla FMEA entro 0,1 dB, salvo D158 in corto (da 87,9 a 136,6 dB SPL alla
  principale: va al rail).

**R120 in corto** (limitations #75): l'avevo lasciato nella lista lunga a 2,3 s. Le cinque corse si
sono fermate a oltre un'ora di CPU ciascuna e le ho fermate a mano, sotto 1 GB, senza danni. È un errore
mio: la #75 dice di correrle da sole e corte. Sono state rifatte a 0,6 s (~25–35 min l'una, sotto 1 GB). Sul
sorgente nuovo: 80–84 °C sul VAS, 127,8 dB SPL alla principale (la FMEA: 86 °C, 127,3).

## 3. La Stax (`p10_stax.csv`)

Q132_be e D158_cc: **114,3 ms** sopra 0,87 V, 120,0 col condensatore d'uscita a +5 %, contro i 150 di
P10. Sono i numeri dei corti dei finali (114,1 / 119,8). Alla principale ~137 dB SPL, sulla protezione
a valle (ADR-081), come gli altri guasti del blocco al rail.

## 4. Le opzioni, coi numeri

VAS sulla piazzola minima (125 °C/W), 60 °C d'aria. Il blocco vede i rail regolati, quindi i numeri
valgono a rete −10 / 0 / +10 %.

| | sorgente (33 + 22 Ω) | 34,0 + 21,0 Ω | **36,5 + 18,7 Ω** |
|---|---|---|---|
| Q132_be / D158_cc | 126 / 126 °C | 124 / 125 | **120 / 121** |
| i quattro di ADR-099 | 123–124 | 118–123 | **118–119** |
| Q132_be, dispositivi a 60 °C | 121 | 119 | 115 |
| margine di fase minimo | 43,33° | 43,34 | 43,26 |
| limitatore a riposo, 27 / 60 / 90 °C | 0,06 / 0,9 / 7,5 µA | 0,09 / 1,3 / 10,4 | 0,25 / 3,3 / **23** |
| V4 a caldo (aria 57 °C): THD 20 kHz, fuori | 0,000726 %, 0 / 12 | 0,000726 %, 0 / 12 | 0,000725 %, 0 / 12 |
| IMD CCIF a caldo | −131,7 dB | −131,6 | −131,0 |

Il rame sotto il VAS (≤ 123 °C/W, nessun cambio del circuito) non si verifica oggi: il datasheet non dà
cifre tra la piazzola minima e i 50 × 50 mm, e quel rame sta sul nodo del polo dominante.

**La scelta dell'utente: «Limitatore 36,5 + 18,7 Ω»** (ADR-111).

## 5. Il sorgente

- R123 36,5 Ω, R192 18,7 Ω nelle otto istanze (`circuits/preamp/gain_block.py`, coi commenti che
  rimandano ad ADR-111). `spice/preamp/gain_block*` sono uguali a `varianti/lim365/`.
- Le netlist: 396 / 44 reti con gli stessi piedini. Una si è rinominata, AL_OUT → F2L_IN (limitations
  #74): `audio_draw.py` ammette ora più sinonimi per nome, ma sempre uno solo presente.
- I disegni rigenerati; il deck del corto in mute con la potenza di R123 scritta come i² × 36,5.
- `run_tests.sh` **14 / 0**.
- Le righe del blocco di `fmea_l58b.csv` (il «Da riaprire se» di ADR-110): le procedure col tester di
  `DIAGNOSI.md` leggono la continua al test point e il riposo dei finali, che il cambio non tocca (a riposo
  il VAS, i finali e la continua d'uscita restano alla cifra, `op_caldo.csv`). Q132_be, che lì rimandava a
  NC-076, ha la sua riga nuova in `fmea_l66.csv`.

## 6. La FMEA (`fmea_l66.csv`)

Le **145 righe del blocco** rifatte sul sorgente dopo ADR-111, coi finali col dissipatore. **Nessuna
oltre P7** (la più calda: Q132_be e D158_cc, 121 °C sul VAS; poi i cinque del limitatore a 118–119, tutto
il resto ≤ 95), **nessuna oltre P10**. Priorità: 95 basse, 49 medie, 1 alta (C145 in corto, a NC-075).
La tabella datata di L45d2b3b3 non si riscrive.

## Errori di questo lotto

- R120 in corto nella lista lunga (sopra).
- Le corse grezze della regressione (~260 MB, comprese le forme d'onda) committate e pushate sul ramo,
  contro il vincolo. Tolte dall'indice nel commit dopo. Il merge è uno squash, quindi `main` non le riceve.
