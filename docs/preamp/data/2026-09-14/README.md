# Dati del 2026-09-14 — mute tenuto e corto sulle uscite

Prodotti dal lotto **L11**. Decisioni: **ADR-021** e **ADR-022**. Report:
`../../reports/2026-09-14-L11-mute-e-corto.md`.

**Topologia**: quella di L10 (LSK489 fuso in una Part, specchio LS352 a
220 Ω). Ogni altro dispositivo è ancora un segnaposto
(`spice/preamp/placeholder_devices.lib`, NC-017), tranne nel file di
sensibilità. **Nessuna protezione dal corto**: è la baseline.

## I file

| File | Deck | Cosa |
|---|---|---|
| `tb_mute_corto_regime.csv` | `tb_mute_corto.cir` | 148 righe: 74 corse × 2 blocchi. Potenza media di ogni dispositivo, picchi di corrente, potenza nelle resistenze |
| `tb_mute_corto_transitorio.csv` | `tb_mute_corto.cir` | 4 righe: inserzione e rilascio del mute, con segnale e senza, a 0 e +10 dB |
| `tb_mute_corto_trans_0.csv`, `_10.csv` | `tb_mute_corto.cir` | forma d'onda del transitorio con segnale, 0 e +10 dB |
| `tb_mute_corto.log` | `tb_mute_corto.cir` | log completo di ngspice |
| `tb_mute_corto_regime-CONTROLLO-senza-contatti-di-mute.csv` | copia del deck senza le tre righe `SMUTE` | **la prova che il deck distingue il mute**: le 36 righe di mute sono identiche a quelle normali (0 su 36 differiscono), contro 32 su 36 nella baseline |
| `tb_mute_corto_regime-SENSIBILITA-modelli-vendor.csv` | copia del deck con i modelli vendor di MJE15032/33 e MMBT5401/5551 al posto dei segnaposto | **non di record**: dice in che verso si muovono le cifre (NC-024, NC-025) |
| `tb_blockA_carichi_*.csv`, `tb_blockA_carichi.log` | `tb_blockA_carichi.cir` | rieseguito sulla topologia di oggi: i dati del 2026-09-09 erano col THAT320 |

## Colonne di `tb_mute_corto_regime.csv`

Hanno un'intestazione vera, scritta dal deck con `echo`, e non `colN`.

- `blk`: A (buffer e due fisse) o B (uscita principale).
- `modo_db`: 0 o 10. `f_hz`: 1000 o 20000. `vin_pk`: picco della sorgente, in V.
- `k_att`: rapporto dell'attenuatore (1 = manopola al massimo).
- `caso`: **0** normale · **1** mute (tre jack a massa insieme) · **2** corto
  franco al connettore FIX1 · **3** corto FIX2 · **4** corto MAIN.
- `p_<dispositivo>`: potenza media in W, finestra 4-8 ms dopo 4 ms di
  assestamento. I nomi sono quelli di `spice/preamp/gain_block.subckt`:
  - `q132` / `q133`: MJE15032 / MJE15033;
  - `q122`: VAS;
  - `q125`: carico del VAS;
  - `q127`: moltiplicatore di Vbe;
  - `q106`: coda;
  - `q117` / `q118`: cascode;
  - `q121a` / `b`: LS352;
  - `jq110a` / `b`: LSK489.
- `icmax_*` / `icmin_*`: picchi di I_C in A. **Classe A ⇔ `icmin_q132 > 0` e
  `icmax_q133 < 0`.**
- `p_r134` / `p_r135`: 22 Ω d'emettitore. `p_r130` / `p_r131`: 10 Ω di base.
  `p_r123` / `p_r126`: 91 Ω del VAS e del suo carico.
- `p_rsep`, `p_rsep2`, `irms_*`: le 47 Ω d'uscita e la loro corrente RMS,
  che a mute inserito è quella del contatto. Nel blocco A sono le due fisse;
  nel blocco B `p_rsep` è la 47 Ω dell'uscita principale e `p_rsep2` vale 0.
- `p_q132_w1` / `_w2`: le due metà della finestra, per la stazionarietà.
  Scarto massimo **1,39 %**.
- `voutpk`: picco positivo sul nodo OUT del blocco.

## Colonne dei transitori

**`tb_mute_corto_transitorio.csv`.** Inserzione a 10 ms, rilascio a 30 ms. Le
colonne sono picchi di potenza istantanea in W:
- `ppk_b132_ins`: nei 2 ms dopo l'inserzione;
- `_mute`: a mute tenuto;
- `_rel`: nei 2 ms dopo il rilascio.

Poi i picchi di tensione sul jack principale (`vjm`) e sul jack FIX1 (`vj1`),
prima e dopo il rilascio.

**`tb_mute_corto_trans_<modo>.csv`.** Colonne dispari:
- col1 p(XB.Q132), col3 p(XB.Q133);
- col5 p(XA.Q132), col7 p(XA.Q133);
- col9 p(XB.Q122);
- col11 v(JM), col13 v(J1);
- col15 comando del mute.

## Numeri chiave

Verificati rileggendo questi CSV.

- **Tutti i dispositivi passano ADR-021**, con TA 60 °C, Tj ≤ 125 °C e senza
  dissipatore:
  - MJE peggiore: 484 mW, Tj 90,2 °C (blocco A, mute);
  - dispositivo più caldo: Q125, Tj 96,5 °C.
- **Resistenze**, vincoli di distinta:
  - la 47 Ω dell'uscita principale arriva a **1,10 W** (corto MAIN, +10 dB,
    20 kHz);
  - le 22 Ω del blocco B a 0,27 W;
  - le 47 Ω delle fisse a 0,155 W.
- **Controprova indipendente** della potenza, da (Vc−Ve)·Ic + (Vb−Ve)·Ib, sul
  caso corto MAIN, +10 dB, 20 kHz:
  - Q132: 253,8 contro 253,2 mW;
  - VAS: 52,66 contro 52,57 mW;
  - la 47 Ω: 1,0970 W dalla corrente, 1,0969 W dalla tensione.
- **Riposo**: I_C delle MJE **14,556-14,557 mA**, contro i 14,557 di
  `../2026-09-10/tb_op-LS352.log`.
- **`tb_blockA_carichi`** sulla topologia di oggi coincide coi dati del
  2026-09-09 a quattro cifre. Col corto da 0,01 Ω: I_C(Q132) massima
  **65,456 mA**, minima −0,34 µA.

## Nota di L33 (2026-09-15) — la provenienza dell'LSK489

Il testo sopra resta com'era: è l'output di un'esecuzione datata. **Una sua frase non è vera**: «(LSK489 fuso in una Part, specchio LS352 a 220 Ω). Ogni altro dispositivo è ancora un segnaposto», che si legge come se l'LSK489 non fosse un segnaposto. Lo è.

- L'LSK489 simulato è **`LSK489X`**, il segnaposto scritto a mano di
  `spice/preamp/placeholder_devices.lib`, con `KF = 0`. Il modello del
  costruttore, `models/jfet/lsk489.lib` (`LSK489A`), non l'ha mai incluso
  nessun deck, né oggi né alla data di questi dati:
  `git log -S "jfet/lsk489.lib" -- spice circuits` è vuoto.
- L'unico modello del costruttore simulato è l'**LS352**
  (`models/bjt_pnp/ls350.lib`), che non ha `KF`. Quindi **nessun dispositivo
  simulato ha rumore 1/f**.
- **Nessun numero cambia**, cambia cosa se ne crede: ogni cifra di rumore qui è
  un pavimento senza flicker, JFET compresi (NC-004, NC-031).
