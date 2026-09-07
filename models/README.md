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
  diodes/             generic .model D, plus one vendor-derived demo
  bjt_npn/            generic .model NPN
  bjt_pnp/            generic .model PNP
  mosfet_n/           generic .model NMOS (LEVEL=1)
  mosfet_p/           generic .model PMOS (LEVEL=1)
  jfet/               generic .model NJF
  opamp/              generic single-pole macro-model .subckt
  subckt_generic/     generic multi-terminal .subckt (coupled-inductor
                       transformer) demonstrating a non-2-terminal part
```

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
