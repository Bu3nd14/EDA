# Smoke test: trivial RC low-pass end-to-end pipeline

Fixture: single resistor (1k) + capacitor (100n) RC low-pass, driven by a
`Simulation_SPICE` VPULSE source. Defined in `smoke/rc_circuit.py`
(SKiDL), driven end-to-end by `smoke/run_pipeline.sh`.

Result: **11 stages PASSED, 3 PARTIAL, 0 FAILED.**

## Stage-by-stage verdict

| # | Stage | Verdict | Evidence |
|---|---|---|---|
| 1 | Circuit definition | PASSED | `smoke/rc_circuit.py` runs, defines R1/C1/V1 and nets VIN/OUT/GND |
| 2 | Schematic generation | **PARTIAL** | `smoke/rc_circuit.kicad_sch` produced and machine-valid (parses, renders to SVG), but visually unusable (overlapping components — Limitations #5) |
| 3 | SPICE netlist generation | **PARTIAL** | SKiDL's native `generate_netlist(tool="spice")` fails on KiCad-library parts (Limitations #2); working path uses `kicad-cli sch export netlist --format spice` → `smoke/rc_circuit_kicad_spice.cir` |
| 4 | KiCad netlist generation | PASSED | `smoke/rc_circuit.net` (SKiDL `tool="kicad10"`) |
| 5 | Simulation | PASSED | `ngspice -b` on `smoke/rc_tran.cir` and `smoke/rc_ac.cir`; see accuracy below |
| 6 | Result extraction | PASSED | `smoke/rc_tran_out.txt`, `smoke/rc_ac_out.txt`, `smoke/rc_sim_summary.json` |
| 7 | ERC | **PARTIAL** | `smoke/rc_circuit_erc.json`: 1 `error` (`power_pin_not_driven` on GND), 3 `warning` (`lib_symbol_mismatch` on R, C, VPULSE) — see Limitations #4 |
| 8 | PCB creation | PASSED | `kinet2pcb` on bundled python3.9 → `smoke/rc_circuit.kicad_pcb` |
| 9 | Footprint assignment | PASSED | R_0805, C_0805, 2-pin header footprints placed from netlist |
| 10 | Placement | PASSED | `smoke/place_components.py` |
| 11 | Routing | PASSED | `ExportSpecctraDSN` → Freerouting 2.4.1 → `ImportSpecctraSES` → `smoke/rc_circuit_routed.kicad_pcb` |
| 12 | DRC | PASSED | `smoke/rc_circuit_drc.json`: `"violations": []`, `"unconnected_items": []` |
| 13 | Gerber export | PASSED | `smoke/gerbers/*.gtl,.gbl,...` — RS-274X content inspected, not just exit code |
| 14 | Drill export | PASSED | `smoke/gerbers/rc_circuit_routed.drl` — Excellon content inspected |

## Simulation accuracy (from `smoke/rc_sim_summary.json`)

- R = 1000 Ω, C = 100 nF → theoretical τ = 1.0e-4 s, theoretical fc = 1591.5494 Hz
- Simulated fc = 1587.6200 Hz → **error 0.2469%**
- Transient step checks (simulated vs. theoretical V_out) at t ≈ τ, 2τ, 3τ, 5τ:
  all within ~1.2e-4 V absolute error, well under 1%.
- ngspice version confirmed in the run: 47.

## ERC detail (`smoke/rc_circuit_erc.json`)

- `error`: `power_pin_not_driven` — Symbol `#PWR001` Pin 1 (GND power input
  not driven by any output power pin).
- `warning` x3: `lib_symbol_mismatch` on R1 (`R`), C1 (`C`), V1 (`VPULSE`) —
  "doesn't match copy in library" for `Device`/`Simulation_SPICE`.
- KiCad version recorded in the report: 10.0.6.

## DRC detail (`smoke/rc_circuit_drc.json`)

- `"violations": []`, `"unconnected_items": []`, `"schematic_parity": []` —
  clean, after the Freerouting round-trip.
- KiCad version recorded in the report: 10.0.6.

## Reproducing

```sh
zsh /Users/roberto/EDA/smoke/run_pipeline.sh
```

This regenerates every artifact referenced above under `smoke/`. Note
`smoke/` is scratch, not canonical (see `AGENTS.md` operating rule #8).
