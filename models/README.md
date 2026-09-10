# models/ — canonical, curated SPICE models

This is the ONLY tree that circuit netlists should `.include`. Everything
here is either:

- **authored** — written from scratch for this project (generic/trivial
  parts, no vendor IP involved), or
- **vendor_derived** — copied from `vendor/<...>/` and then converted,
  patched, trimmed, or renamed for our use.

Every file in this tree (except `README.md`/`PROVENANCE_CONVENTION.md`
themselves) MUST have a matching sidecar `<filename>.provenance.json`.
The validator (`scripts/validate_models.py --check-provenance`) enforces
this and fails if a sidecar is missing or malformed.

## Directory layout (by device class)

```
models/
  resistors/        generic .model R  (linear resistor w/ tempco)
  capacitors/        generic .model C  (linear capacitor w/ tempco)
  inductors/          generic .model L  (linear inductor w/ tempco)
  diodes/             generic .model D, one vendor-derived demo, and the
                       1N4148 bias diode (onsemi)
  bjt_npn/            generic .model NPN, plus MMBT5551 (Diodes Inc.) and
                       MJE15032 (onsemi)
  bjt_pnp/            generic .model PNP, plus MMBT5401 (Diodes Inc.),
                       MJE15033 (onsemi) and LS350/LS352 (Linear Systems)
  mosfet_n/           generic .model NMOS (LEVEL=1)
  mosfet_p/           generic .model PMOS (LEVEL=1)
  jfet/               generic .model NJF, plus LSK489 (Linear Systems)
  opamp/              generic single-pole macro-model .subckt
  subckt_generic/     generic multi-terminal .subckt (coupled-inductor
                       transformer) demonstrating a non-2-terminal part
```

## The vendor models, and what they are worth

Seven of the files here are **vendor models**, and they are the reason
requirement **T7** (`docs/preamp/decisions/ADR-016-*.md`) can be met at
all: every active device in the preamp's signal path now has a model
published by the manufacturer that makes it. Each one carries its verdict
against its own datasheet **in its own header**, and none of the verdicts
is decoration:

| File | Part | Verdict against its own datasheet |
|---|---|---|
| `jfet/lsk489.lib` | LSK489 (Linear Systems) | mixed — V_GS(off) outside, **NC-013** |
| `bjt_pnp/ls350.lib` | LS352 (Linear Systems) | mixed — f_T 35% low, **NC-020** |
| `bjt_pnp/mmbt5401.lib` | MMBT5401 (Diodes Inc.) | **three of three inside** |
| `bjt_npn/mmbt5551.lib` | MMBT5551 (Diodes Inc.) | **three of three inside** |
| `bjt_npn/mje15032.lib` | MJE15032 (onsemi) | h_FE **and** f_T outside — **NC-024**, **NC-025** |
| `bjt_pnp/mje15033.lib` | MJE15033 (onsemi) | h_FE inside, f_T outside — **NC-025** |
| `diodes/1n4148.lib` | 1N4148 (onsemi) | both published limits inside |

Two properties they share, and both belong next to any number computed
with them:

1. **Only `jfet/lsk489.lib` has `KF`/`AF`.** None of the other six has
   flicker noise, so a simulated noise figure that leans on them is a
   **floor without 1/f**, which is exactly where the analysis says the
   noise is dominant. That is why **NC-004** does not close merely
   because the real models arrived.
2. **Where a deviation exists it runs pessimistic** — less gain, less
   speed than the guaranteed part. That is the safe direction, but it is
   not a *known amount*.

Each of them is locked by a recipe in `scripts/validate_models.py` that
re-measures it at its datasheet's own conditions (`set temp = 25`, never
ngspice's default 27 °C) and fails if a digit moves. The recipes assert
the deviations **as deviations**: none of them claims a conformance that
is not there.

## How to use these in a netlist

Always use `.include <absolute-or-relative-path>`, never bare `.lib
<file>` unless the file itself contains `.lib <name>` / `.endl` section
markers (ours don't — confirmed in Step 3 that ngspice 47's `.lib
<file>` with no section name fails with "unknown subckt", while
`.include` works for plain `.model`/`.subckt` files).

Each model file's header comment documents the exact instantiation
syntax to use, including ngspice-specific quirks discovered while
building this library, e.g.:

- `R` supports **both** `Rxxx n1 n2 <value> <model>` (positional) and
  `Rxxx n1 n2 <model> R=<value>`.
- `C` and `L` do **NOT** support the positional `<value> <model>` form —
  ngspice errors with `unknown parameter (<modelname>)`. You must write
  `Cxxx n1 n2 <model> C=<value>` / `Lxxx n1 n2 <model>
  inductance=<value>` (model name immediately after the nodes, then the
  value as a named parameter). Verified against ngspice 47's own
  `devhelp capacitor` / `devhelp inductor` output.

## Provenance convention

See `PROVENANCE_CONVENTION.md`. Short version: every model file has a
sidecar JSON recording origin, vendor source (if any), what was changed,
why, and by whom/when.

## Validating the library

```
/usr/bin/python3 /Users/roberto/EDA/scripts/validate_models.py
```

Runs every model through a minimal auto-generated ngspice testbench and
checks the result is electrically sane. Nonzero exit code on any
failure — safe to wire into CI.
