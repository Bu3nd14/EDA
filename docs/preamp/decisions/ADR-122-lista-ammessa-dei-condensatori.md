# ADR-122 — La lista ammessa dei condensatori di segnale

Data: 2026-11-05 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Esegue P6** (L42c, ADR-053: «le prove si fanno coi tipi di una lista ammessa, che il giro della
  distinta scrive qui accanto») e **PR-12 come riscritta da ADR-118** (dopo il prototipo si cambiano i
  condensatori di accoppiamento dissaldandoli, coi tipi della lista; niente zoccoli).
- **Conferma ADR-007** sul dielettrico (polipropilene) e ne completa i valori con le finestre; la Stax ha
  la sua, ADR-121.
- Chiude la parte di **NC-082** da fare prima di G1 (le finestre e i tipi, che sono requisiti). Le impronte
  sui pezzi più grandi restano per G2, e la prova di spazio è NC-048 (L73).

## Contesto

La revisione dell'architetto avversariale di L65 (rilievo **R2**): la lista non esisteva, e le impronte di
oggi sono quelle del poliestere (`…MKT`, `…MKS4`). Senza la lista, la promessa di PR-12 non è costruibile:
non si sa che cosa si può montare né quanto spazio serve.

## Decisione

La lista è la tabella sotto P6 in `REQUIREMENTS.md`: per ogni posizione la finestra di valore, il vincolo
che la fissa, i tipi in **film di polipropilene ±5 %** coi codici letti e il pezzo più grande. Stesso tipo e
valore nei due canali. La Stax ha un solo valore ammesso, **1,0 µF ±5 %**: non è una variabile d'ascolto.

## Perché

- **Le finestre** (`data/2026-11-05/L72/script/finestre.py`): con ogni condensatore della catena al basso
  della sua finestra a −5 %, a 20 Hz principale 0,128 dB, fissa 1 0,150, fissa 2 0,179, contro i 0,2 dB di E9.
  Lo scarto fra i canali dovuto ai ±5 % è al più 0,032 dB (in E10). I limiti alti: l'ingresso da PR-14 (la
  perdita del film: R_isolamento ≥ 10 GΩ, il poliestere peggiore a 1 µF di ADR-064), C_T dal valore
  verificato, la Stax da P10 (ADR-121); principale e Singxer non hanno un requisito che li limiti in alto.
- **E12**: con 0,1 V ai capi bastano 26–235 s di τ_IR; i tipi dichiarano 10 000–30 000 s.
- **I tipi** (`data/2026-11-05/L72/distinta/README.md`, `bom-component-manager`, DigiKey e datasheet
  scaricati il 2026-11-05; due codici riletti a campione dall'orchestratore: WIMA MKP4D046806F00JSSD e
  Vishay CMF55845R00BEEB, conformi). Il Panasonic ECW-FE a 2,2 µF (τ 10 000 s, 4,5 GΩ) **non** passa la
  perdita dell'ingresso ed è escluso; i KEMET R76 sono solo ±10 %. Per C_T un solo costruttore con ±5 % e
  codice letto (WIMA MKP 4).
- **I pezzi più grandi**: 26,5 × 7 × 16,5 mm (1 µF), 31,5 × 15 × 26 mm (4,7 µF), 41,5 × 19 × 32 mm a passo
  37,5 (10 µF / 250 V). Le impronte di oggi (16,5 × 7 mm a passo 15 per C162 / C362) non li accolgono.

## Alternative scartate

- **Zoccoli o passi multipli con torrette**: l'utente, 2026-11-04, «solo per la lista ammessa e non per lo
  zoccolo (dissalderemo)».
- **Ammettere il poliestere** per le prove: il 19 % del segnale cade sul condensatore della Stax a 20 Hz, e
  ADR-007 chiede il polipropilene.

## Da riaprire se

- Un tipo della lista va fuori produzione, o la sua τ_IR letta sul datasheet scende sotto il vincolo.
- L'utente vuole provare un tipo fuori lista: si verifica contro le stesse finestre e si aggiunge qui.
- La prova di spazio di L73 non accoglie il pezzo più grande di una posizione: si restringe la finestra.
