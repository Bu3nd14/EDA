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

## Hi-fi project team

The roster above is the *environment* team — the agents that built and validated the toolchain. The agents below are the *project* team that uses it to design audio hardware.

**The orchestrator is the main session, not a subagent.** It runs on Opus, defines requirements with the user, arbitrates between roles, and owns decisions that are not delegated (architecture, source-of-truth boundaries, gate outcomes). There is deliberately no `.claude/agents/` file for it — you do not delegate to your own orchestrator.

| Role | Agent | Model | Owns |
|---|---|---|---|
| Circuit design | `analog-topology-designer` | opus | `circuits/*.py` — the canonical topology, operating points, gain structure, predicted figures of merit. **Also owns the human-reviewable schematic drawing of its own circuit** (`docs/<project>/schematic/`) — the person who designed it draws it, because readability depends on knowing which structures matter |
| Gate review | `design-reviewer` | opus | Independent challenge at gates only. No write access by design |
| Measurement | `measurement-analyst` | sonnet | THD/THD+N, response, noise, PSRR, Zout, phase margin — verifies the designer's predictions |
| Power supply | `psu-engineer` | sonnet | Rails, ripple, regulation, thermal, **mains safety** |
| Layout | `pcb-automation-engineer` | sonnet | Placement, routing, **grounding/return paths/EMC**, DRC, fabrication export |
| Components | `bom-component-manager` | sonnet | Part selection, sourcing, vendor models + provenance |
| Regressions | `regression-runner` | haiku | Runs the verification scripts, reports exit codes verbatim. No judgment, no fixes |
| Documentation | `docs-writer` | sonnet | Project docs and measurement dossiers, from verified results only. Has **no execution tools by design**, so it never produces anything requiring a run — schematics and measurements come to it already verified |

`installer-verifier` and `toolchain-researcher` are kept on the bench — invoked only when adding or evaluating a tool, not as part of ongoing project work.

### Gates

`design-reviewer` is invoked at four points, not continuously:

- **G0 — First product review**: as soon as there is a dossier to judge,
  before the topology is frozen. Added 2026-09-09 (see below).
- **G1 — Topology freeze**: before layout begins.
- **G2 — Pre-layout**: schematic/netlist complete, before placement and routing.
- **G3 — Pre-fabrication**: before any fabrication export is treated as final.

#### G0 — la prima revisione del prodotto

Proposta dall'utente il 2026-09-09, con un argomento di costo: **gli errori
a catena costano moltissimo**, e i tre gate esistenti stanno tutti dopo il
punto in cui un errore ha già propagato. G1 congela la topologia; se la
topologia era sbagliata, G1 arriva tardi. G0 sta prima e chiede una cosa
sola: **quello che il progetto ha misurato finora dice che il circuito fa
quello che ha promesso?**

**Soggetto: il prodotto, non l'ambiente.** Questa riga è una correzione
esplicita dell'utente e va rispettata. G0 giudica il preamplificatore — il
circuito, il suo comportamento misurato, le decisioni che lo hanno prodotto
e i disegni che lo rappresentano. **Non** giudica i banchi di prova,
`run_simulation.sh`, il generatore del dossier o la toolchain: quella è
qualità dell'ambiente EDA, ed è un'altra conversazione. Se il revisore
inciampa in un difetto della catena lo annota a parte, sotto «osservazioni
fuori scope», e non apre una non conformità di prodotto.

**Le sette domande di G0.** Sono queste e vanno chiuse una per una, ognuna
con l'evidenza aperta o con l'ammissione che l'evidenza manca:

1. **La struttura di guadagno fa quello che ADR-001 promette?** È la
   diagnosi da cui nasce il progetto: il Technics SU-9070 richiede 46 dB di
   attenuazione, e quella è la causa misurabile del difetto lamentato. E1 e
   E2 sono misurati; l'attenuazione risultante all'ascolto (E3b) è quella
   prevista?
2. **I requisiti elettrici con evidenza sono soddisfatti, e dove non lo sono
   il rimedio dichiarato basta?** In particolare E4 con la sua tensione
   contro E8 a 20 Hz, e E6×E2, dove il margine misurato è stretto e il
   rimedio è il trim di ADR-011.
3. **È stabile, o è stabile nel caso comodo?** Il relè commuta la rete di
   controreazione, quindi il margine di fase è diverso nelle due modalità:
   V1 esiste per questo. Il revisore deve dire se i casi coperti sono i casi
   giusti, non solo se i numeri coperti sono buoni.
4. **Le ADR sono confermate o smentite dalle misure?** Alcune hanno una
   claim falsificabile e ora hanno i dati per verificarla; altre sono ancora
   solo ragionamento. Il revisore deve separare le due categorie.
5. **Dove il progetto dice «non lo so», lo dice davvero?** Rumore e
   distorsione non hanno cifre credibili finché i modelli sono segnaposto.
   Una cifra presentata come più solida di quanto sia è una non conformità,
   non una svista di stile.
6. **I disegni dicono la verità sul circuito?** Lo schema del blocco di
   guadagno e il diagramma a blocchi sono il prodotto tanto quanto la
   netlist: sono ciò su cui la revisione umana — precondizione dichiarata di
   G1 e G2 — viene esercitata. Un disegno che mente fa prendere decisioni
   sbagliate a chi lo guarda, ed è una non conformità di prodotto a tutti
   gli effetti.

7. **Che cosa il progetto presenta come normale, e nessuna sorgente del
   repo contraddice?** È la domanda che le prime sei non fanno. Le altre
   confrontano un'affermazione con una sorgente — un'etichetta contro un
   `.log`, una connessione contro la netlist — e trovano ciò che è
   **falso**. Questa cerca ciò che è **taciuto**: una condizione di lavoro
   che nessun banco esercita, un carico che nessuna misura copre, una
   scelta disegnata correttamente e mai giudicata. Il revisore deve
   nominare almeno un candidato, o dire esplicitamente di non averne
   trovati.

**Perché la settima esiste, e non è teoria.** A G0 era stato allestito un
**controllo cieco**: l'utente aveva trovato un errore nel diagramma a
blocchi e aveva chiesto che non fosse l'orchestratore a cercarlo. G0 non
l'ha trovato, pur avendo rasterizzato il disegno e confrontato riga per riga
con `preamp_audio.py`, e pur avendo trovato con lo stesso metodo
un'affermazione falsa sull'altro disegno (è diventata NC-001). L'errore era
che il Blocco A pilota **tre carichi in parallelo** senza isolamento
reciproco: il disegno lo mostra correttamente, nessuna etichetta è falsa,
e non c'era quindi niente da falsificare. Misurato e registrato in
`docs/preamp/reports/2026-09-09-revisione-utente-dossier.md`; l'omissione
è diventata NC-010, bloccante.

Conseguenza da tenere: **G0 vede le affermazioni false, non le omissioni di
giudizio.** La settima domanda è il rimedio parziale, e resta parziale — è
il motivo per cui la revisione umana dello schematico è una precondizione
di G1 e G2 e non un di più.

**Perché la sesta domanda ha un peso diverso.** `scripts/check_schematic.py`
confronta un disegno con la netlist nelle due direzioni, ma **copre solo i
disegni che hanno un manifesto**, e un diagramma a blocchi non ce l'ha
perché omette i dispositivi di proposito. La sua unica garanzia sono le
asserzioni dentro il proprio script di disegno. Struttura, collegamenti ed
etichette non sono verificati da niente: è il punto del progetto in cui un
errore può sopravvivere più a lungo.

E c'è un ostacolo pratico da conoscere: i due SVG sotto
`docs/preamp/schematic/` sono prodotti da matplotlib **con il testo
convertito in tracciati**, quindi non contengono un solo elemento `<text>` e
leggere il file non mostra nessuna etichetta. Per *guardarli* vanno
rasterizzati:

```sh
qlmanage -t -s 2400 -o <outdir> docs/preamp/schematic/preamp_blocks.svg
```

In alternativa si legge lo script che li genera, che è la loro vera fonte.
Un revisore che si limitasse a `cat` sull'SVG concluderebbe di non poter
giudicare il disegno, e sbaglierebbe.

**Cosa blocca una non conformità bloccante a G0**: l'accesso a G1. La
topologia non si congela finché la voce non è chiusa, o da una modifica del
circuito o da una ADR che accetti lo scostamento **consapevolmente e per
iscritto**. Non blocca invece i lotti che procurano i modelli vendor
(L6-L7): quelli sono il rimedio naturale a metà delle voci prevedibili, non
un avanzamento di fase.

**G0 è anche la risposta alla domanda sul «revisore avversariale».** Non
serve un agente nuovo: serve `design-reviewer` con questo mandato. Ha già le
proprietà che contano — nessun accesso in scrittura per costruzione, e
l'obbligo di rieseguire le verifiche invece di fidarsi dei resoconti — e G0
le punta sul prodotto invece che sul processo.

**A gate is triggered by test results, not by a pull request** (decided
2026-09-09). A diff is the wrong artefact to judge an analog design on: the
changed lines of `gain_block.py` say nothing about phase margin, and at the
moment a PR is open the measurements that would answer the gate's question do
not exist yet. Tying the two coupled every chunk to gate-weight it had no data
for, and kept the repository disaligned while it waited.

So a gate runs **offline, after the merge**, on `main`, against the dossier and
the measured data. `design-reviewer` re-runs the verification itself rather than
trusting reports - it already has that mandate - which is why the decks and
`scripts/run_simulation.sh` must be reproducible from a clean checkout.

**What a gate produces is non-compliances, not a merge veto.** A dated report in
`docs/preamp/reports/` opens them; each one names the requirement it is against
(E-number / V-number), the evidence behind it (which data file, which
measurement), a severity, and a status. The living register is
`docs/preamp/NONCOMPLIANCE.md`, and open items feed the lotti table in
`docs/preamp/STATE.md` - so a gate produces work rather than stopping it.

**BLOCK has not gone away, it has moved.** A non-compliance of **blocking**
severity does not block a merge; it blocks **phase advancement** - no layout, no
fabrication - which is what that rule always meant. On a mains-connected design,
a missing safety analysis is an automatic blocking non-compliance at G3.

Severities:

| Severità | Significato | Effetto |
|---|---|---|
| **bloccante** | un requisito non è soddisfatto, o manca l'evidenza per dirlo | la fase successiva non si apre |
| **maggiore** | scostamento reale, con margine residuo o rimedio noto | va chiusa prima del gate successivo |
| **minore** | osservazione da registrare, nessun rimedio richiesto ora | resta aperta e visibile |

**A human-reviewable schematic is a precondition for G1 and G2.** A design
nobody can look at has not been reviewed, however many numbers agree. Simulation
verifies the figures; it does not verify whether the signal path is short, where
the ground return runs, or whether a bias choice convinces someone who knows the
domain — and that judgement belongs to the user, not to any agent here.

Readable analog schematics cannot be auto-placed (researched and tested — see
`docs/limitations.md` #16), so they are drawn by hand in code and checked
mechanically against the netlist by `scripts/check_schematic.py`. The gate
requirement is not "a drawing exists" but "a drawing exists **and**
`scripts/run_tests.sh` confirms it matches the circuit". See
`docs/architecture.md`.

### What the team does not do

No agent judges how a circuit *sounds*. Subjective evaluation belongs to the user, on real hardware. Simulation covers stability, noise, response, PSRR and impedance credibly; it does not cover listening, and distortion figures from generic macro-models are not trustworthy substitutes for measurement on a prototype.

### Project roadmap

Preamplifier first, then a phono stage, then a power amplifier. A DAC is possible but not committed. Agent mandates are written to be reusable across all of these rather than tuned to any one — but note the emphasis shifts: a phono stage is dominated by noise and RIAA equalisation accuracy, while a power amplifier is dominated by thermal design and mains safety.

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
   sources of truth. **Dossier data is neither**: measurements the dossier
   cites are versioned under `docs/preamp/data/<YYYY-MM-DD>/`, because a
   gate that runs offline on `main` needs numbers it can actually open, and
   `results/` is gitignored. Curated, not raw - what the dossier plots, not
   every run. A measurement is true of one version of the circuit, so the
   date is part of the path, exactly as for `reports/`.
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
