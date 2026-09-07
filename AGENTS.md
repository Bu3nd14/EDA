# AGENTS.md — Subagent Roster and Operating Rules

This file describes the subagents defined under `.claude/agents/` and how an
orchestrator should delegate to them, plus the operating rules that apply to
all work in this repository regardless of which agent performs it. It is
kept in sync with the actual agent definition files — if you change a role
in `.claude/agents/`, update this file to match.

## Roster

| Agent | File | Tools | Use when | Returns |
|---|---|---|---|---|
| `toolchain-researcher` | `.claude/agents/toolchain-researcher.md` | Read, Grep, Glob, Bash, WebSearch, WebFetch | You need a structured, evidence-based comparison of EDA tools (KiCad, LibrePCB, ngspice, SKiDL, Qucs-S, etc.) against supplied criteria. | A comparison table/notes with each claim tagged "observed" (tested) or "reported" (docs/community only). Does **not** make the final architecture decision. |
| `installer-verifier` | `.claude/agents/installer-verifier.md` | Bash, Read | A tool needs to be actually installed and verified (native ARM64 confirmed, exact version + path recorded). | Install method, exact command, executable path(s), raw architecture-verification output (`file`/`lipo`), version string. Does **not** decide which tool to install. |
| `spice-engineer` | `.claude/agents/spice-engineer.md` | Bash, Read, Write, Edit | ngspice (or chosen SPICE tool) needs to be driven through batch simulations (`.op`, `.dc`, `.ac`, `.tran`, `.noise`, sweeps) with results extracted to CSV/JSON. | Working netlist(s), exact invocation, real simulation output/errors, path to extracted results. Reports failures/suspicious results plainly, does not silently retry and hide failed attempts. |
| `pcb-automation-engineer` | `.claude/agents/pcb-automation-engineer.md` | Bash, Read, Write, Edit | The selected PCB tool's programmatic capabilities need testing: board creation, footprint placement, net assignment, track/zone creation, DRC, fab export. | What actually worked vs. failed, with evidence (real output, inspected artifacts — not just exit codes). Flags GUI-only/non-scriptable capabilities explicitly. Does **not** choose the PCB tool. |
| `smoke-test-runner` | `.claude/agents/smoke-test-runner.md` | Bash, Read, Write, Edit | A trivial end-to-end pipeline validation is needed: schematic → netlist → simulation → PCB → placement → routing → ERC/DRC → gerber/drill export. | Per-stage verdict (succeeded / partially succeeded / failed) with evidence, and explicit flags on any non-scriptable manual workaround. |
| `docs-writer` (this role) | `.claude/agents/docs-writer.md` | Read, Write, Edit, Grep, Glob | README.md, AGENTS.md, or report sections need drafting from findings already gathered by other agents. | Markdown reflecting only verified findings; explicit `TODO: unverified` placeholders where information is missing; never invents capabilities/versions/results. |

## Delegation guidance for the orchestrator

- Tool selection is a two-step handoff: `toolchain-researcher` gathers
  evidence and comparison data; the **orchestrator** (not the researcher)
  makes the final architecture call.
- Installation is a separate step from research: `installer-verifier` only
  installs/verifies what has already been decided, and reports raw
  evidence (not opinions).
- Capability testing is tool-specific and stage-specific:
  `spice-engineer` owns simulation-side capability testing;
  `pcb-automation-engineer` owns PCB-side capability testing. Neither one
  chooses the underlying tool.
- `smoke-test-runner` is the integration check — used after individual
  capabilities are believed to work, to confirm the pipeline works
  end-to-end as a whole, not just in isolation. Any stage it cannot
  complete is reported as failed/blocked, never silently skipped.
- `docs-writer` is downstream of all of the above — it only writes up
  findings that already exist (in conversation or on disk), and never
  performs new research, installation, or testing itself.

## Operating rules (apply to all agents and all work in this repo)

1. **Vendor files are read-only.** Never silently modify original vendor
   models; `vendor/` is read-only (mode 0444, enforced by
   `scripts/freeze_vendor.sh`). Converted/patched copies go in `models/`
   with provenance recorded in a `<file>.provenance.json` sidecar (see
   `models/PROVENANCE_CONVENTION.md`).
2. **Preserve source-of-truth consistency.** Topology changes go in
   `circuits/*.py` (SKiDL), never by hand-editing generated
   schematics/netlists. Layout lives in the `.kicad_pcb` file — it is not a
   topology source. The netlist sync is one-way: code → KiCad.
3. **Validate after changes.** Run `scripts/validate_models.py` after any
   model change; run `scripts/run_tests.sh` broadly after other changes.
4. **ERC/DRC gate fabrication.** Always run ERC and DRC before any
   fabrication export. Never export fab files from a board that fails DRC
   (`scripts/export_fab.sh` is expected to refuse in that case).
5. **Fabrication outputs are generated, not edited.** Never manually modify
   generated fabrication files (gerbers/drill).
6. **No unverified capability claims.** Do not claim a capability works
   without having executed it. This environment was built on that rule —
   every capability documented here was actually run and its output
   inspected, not assumed from documentation.
7. **Prefer deterministic scripts over undocumented GUI procedures.**
   If something is only reachable through the GUI, say so explicitly rather
   than implying it is automatable.
8. **Keep scratch separate from canonical.** `smoke/` and `results/` are
   scratch/experimental; `circuits/`, `models/`, `vendor/` are canonical
   sources of truth.
9. **Two-interpreter split.** Always use absolute interpreter paths when
   touching both SKiDL (venv Python 3.13) and `pcbnew`/`kinet2pcb` (KiCad's
   bundled Python 3.9) — they are not interchangeable and there is no
   single interpreter that has both.
10. **`Simulation_SPICE` symbols need manual fields.** When using SKiDL
    `Simulation_SPICE` library parts, always set `Sim.Type` and `Sim.Device`
    manually in addition to `Sim.Params` — SKiDL does not carry the first
    two through into the generated schematic, which otherwise produces a
    silently invalid SPICE line.

## Keeping this file in sync

If a new agent file appears under `.claude/agents/`, or an existing one's
`description`/tools/rules change, update the roster table above by reading
the actual file — do not rely on memory of what was requested.
