# L54a — avanzamento (sessione interrotta al limite d'uso, 2026-10-25)

Divisione decisa con l'utente all'inizio: **«Due parti»** — L54a i numeri, la scelta e l'ADR; L54b il
sorgente, se la scelta cambia il circuito. Piano approvato:
`/Users/roberto/.claude/plans/per-favore-esegui-il-parallel-hopper.md` (riassunto sotto).

## Fatto

- `psu/` copiato da `data/2026-10-22/L45d2b3b1/psu/`, `carico.txt` copiato (il carico di L45d2b3b1, senza
  il limitatore di L57b: ~1 mA per rail in più, da dichiarare).
- **Il caso noto**: `f_d530_corto_muss --n2n7002 ds` (`seq/controllo/`): deck uguale salvo i percorsi,
  `core_g1.csv` **byte-identico** a L45d2b3b1, punto fisso al giro 1.

## Il disegno in corso (opzione «a comparatori con lo standby»), tutto su V5, TLV1702/1704

- `PG` (100k su V5): quattro canali nuovi con le soglie del sorvegliante (rail +, rail −, `VRELAY_REG`,
  rete) — il sorvegliante su `MUTE_G` **non si tocca**.
- `PG_T`: 680k / 1 µF da V5, scarica veloce con uno Schottky su `PG`: ~0,47 s al rilascio.
- `mrq` (200k / 100n, 20 ms di debounce alla salita), tirato giù da: `PG_T` < VREF, SW3 in mute,
  Schottky su `ON`; un comparatore lo squadra in `MUTE_REQ` (pull-up 10k: Δ ≈ 17,7 ms).
  `PERMIT_REQ` non serve (PERMIT_T si carica già da `MUTE_REQ`).
- `ON` (pull-up 47k): comparatore sul frontale; è anche `VRELAY_EN`.
- `MAINS_T` (1M / 100n) caricato da `ON` e da `VR_G` con diodi: K501 cade ~84 ms dopo `PERMIT_CMD`.
- La ritenuta del guasto: `F` (100k / 47n, ~3 ms) alto solo se rail fuori ∧ rete presente ∧ armato
  (`ARM_T` 470k / 100n caricato da `PG_T` buono, scade ~26 ms dopo); una coppia NPN/PNP a tiristore
  alimentata da `ON`, azzerata dal frontale spento.
- Standby stimato: ~1,3 mA da V5 → ~16 mW in più dal secondario di T2 (~96 mW contro 80,5).
- Mancano ancora: il timeout dei 2 s all'accensione; l'opzione «senza standby» (K501 chiuso sul
  banco, T2 acceso con la rete; variante con `VRELAY` dal grezzo del rail +).

## La ricognizione: che cosa la FMEA chiede al firmware (agente di sola lettura)

Un temporizzatore analogico deve rifare, o la scelta deve dichiarare perso:
1. **stacca K501 dopo un guasto con la rete presente** (~80–100 ms): è l'unica cosa che limita
   l'energia in R550 / R551 (66–102 W, 4,7–8,8 J, NC-073) e in R552 (2,7 W per ~0,2 s, ADR-094);
2. la ritenuta fino al frontale (ADR-048 p. 5);
3. buco di rete contro guasto, rilascio dopo ≥ 500 ms (spec §4.5);
4. il timeout di 2 s all'accensione (ADR-091);
5. **la riserva del sorvegliante cieco** (ADR-073: il firmware muta in 2,2 ms leggendo l'ADC; «da
   riaprire se il firmware non legge più i rail (L54)»);
6. la diagnosi di L58 (ADR-076: il mute che non si inserisce, fino a 3,6 V / ~125 dB SPL; ADR-078).
Senza lo standby (niente K501) il punto 1 è perso: è un argomento contro l'opzione «senza standby».

## Prossimi passi

`genera_tb_psu.py --timer analogico` (e `diretto` per l'opzione senza standby), i casi di L41c alle tre
reti, standby e calore, la scelta all'utente, ADR-102, report; poi STATE.md, NEXT-SESSION.md,
`chunk_close.sh L54a`.
