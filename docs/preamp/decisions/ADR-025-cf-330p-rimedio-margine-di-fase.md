# ADR-025 — C_f da 22 a 330 pF: il rimedio del margine di fase, uguale in tutte le istanze

Data: 2026-09-14 · Stato: accettata

## Contesto

Col criterio di **ADR-024** e i valori di L17, una sola istanza stava sotto i 60°
di **ADR-019**: il **blocco B a 0 dB**, **54,97°** con l'attenuatore a metà corsa
e 2,7 nF al jack (NC-021). Il blocco A, col cablaggio ≤ 1 nF, dava 63,32°; i
buffer, al jack, 61,51°. Il blocco è uno solo (T3, ADR-006): ogni valore di
`gain_block.py` cambia otto istanze.

## Decisione

**C137, il C_f in parallelo a R_f, passa da 22 pF a 330 pF, dielettrico C0G.**
Miller (C124, 470 pF) e resistenze d'uscita (47 Ω) restano come sono. Il valore
è lo stesso in tutte le otto istanze.

## Perché

**Il margine**, deck versionati in `data/2026-09-14/L12/dopo/`:

| Istanza, criterio ADR-024 | C_f 22 pF | C_f 330 pF | agli spigoli (C ±5 %, R ±1 %) |
|---|---|---|---|
| Blocco B 0 dB, cavo al jack, ogni sorgente | 54,97° | **61,21°** | 60,73° |
| Blocco B +10 dB | 80,26° | 102,96° | — |
| Blocco A, cablaggio ≤ 1 nF | 63,32° | **63,36°** | 62,69° |
| Buffer delle fisse, cavo al jack | 61,51° | **61,63°** | 61,16° |

**Cosa non cambia**, rimisurato:
- guadagno d'anello a 20 kHz (33,7 dB) e **slew rate** (3,73 V/µs in discesa):
  il C_f non tocca il polo dominante;
- **PSRR**: rail + a 10 kHz 29,83 contro 29,82 dB, quindi i limiti di ADR-020
  restano validi;
- **E5**: caso peggiore 4,225 µV contro 4,231; fisse 1,666 µV;
- **punto di lavoro**: 79 valori su 79 identici;
- **classe A e P7**: `tb_mute_corto` e `tb_blockA_carichi` senza nessuna riga che
  cambi stato; la MJE peggiore resta a 348,0 mW;
- **V2** (picchi del relè) e **V3** (recupero < 1 µs), **E4** (1,067 Ω al nodo).

**Il costo**: a +10 dB la banda chiusa passa da 333 a **183 kHz**, e la
risposta a 20 kHz scende di 0,053 dB rispetto a 1 kHz (era 0,016). A 0 dB c'è
+0,03 dB a 100 kHz. Nessun requisito fissa una banda.

## Alternative scartate

- **Più Miller** (C124 a 1 nF): 61,74°, ma lo slew in discesa scende a
  1,79 V/µs. A 20 kHz e fondo scala, +10 dB, la sinusoide va in slew: +0,38 V di
  continua, pendenza 1,374 contro 1,511 V/µs richiesti. Toglie anche 6,5 dB di
  guadagno d'anello e di PSRR del rail + a 10 kHz.
- **Miller più isolamento a 68 Ω** (680 pF, 47 pF, 68 Ω): 61,25°, ancora in slew
  (1,450 V/µs), Re(Zout) a 20 Hz 82 Ω, −3,2 dB di PSRR.
- **C_f 330 pF più 56 Ω su tutte le uscite**: 62,27°, 61,84° agli spigoli.
  Più guardia, ma cambia tre reti d'uscita e i deck che le descrivono, ed E4
  sale da 61 a 70 Ω a 20 Hz. Resta la prima strada se serve più margine.
- **Meno guadagno d'anello per degenerazione**: non esplorata, perché il C_f
  raggiungeva la soglia senza costi sulle grandezze misurate.

Numeri delle alternative: `data/2026-09-14/L12/esplorazione/`.

## Da riaprire se

- **La Fase 4** (NC-017, NC-020, NC-025) cambia i modelli: la guardia agli
  spigoli sul blocco B è 0,7°.
- **L27** aggiunge il secondo ramo di R_g: la rete di controreazione cambia e la
  modalità +3 dB va misurata con questo C_f.
- **Entra un requisito di banda** a +10 dB o di risposta a 20 kHz.
