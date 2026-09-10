#!/usr/bin/env python3
"""
validate_models.py - Health-check the /Users/roberto/EDA/models library.

For every model file we know how to test, this script:
  1. Confirms a provenance sidecar (<file>.provenance.json) exists and is
     well-formed (and, for vendor_derived files, that the referenced
     vendor/ original still exists and its sha256 matches what the
     provenance record says it was derived from).
  2. Builds a small, self-contained ngspice testbench that `.include`s
     the model file (never bare `.lib`) and instantiates the device.
  3. Actually runs `ngspice -b` on it and parses the numeric results out
     of the wrdata output file.
  4. Applies a pass/fail numeric predicate specific to that device class
     (not just "did ngspice exit 0" - checks the physics look sane).

Discovery: walks MODELS_DIR for *.lib files. Any discovered file with no
matching entry in TEST_REGISTRY (keyed by path relative to MODELS_DIR)
is reported as SKIPPED (coverage gap), not silently ignored.

Exit code: 0 if every check passed, 1 if anything failed or was
skipped due to a missing/broken provenance sidecar. Safe to re-run
(idempotent - overwrites its own scratch files under
results/model_validation/).

Usage:
    /usr/bin/python3 scripts/validate_models.py
    /usr/bin/python3 scripts/validate_models.py --check-provenance   # provenance-only, no ngspice runs
"""
import hashlib
import json
import os
import subprocess
import sys

# Derived from this file's own location, never hard-coded. Hard-coded it
# was, and run from an isolated copy of the repo it silently validated
# the MAIN checkout's models/ instead of the branch's: a green suite that
# had not looked at the work under test. Found in L6 by adding a model
# and watching it fail to appear in the report. Same family as ROOT in
# run_tests.sh, run_simulation.sh and freeze_vendor.sh.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT, "models")
VENDOR_DIR = os.path.join(ROOT, "vendor")
SCRATCH_DIR = os.path.join(ROOT, "results", "model_validation")
NGSPICE = "/opt/homebrew/bin/ngspice"

os.makedirs(SCRATCH_DIR, exist_ok=True)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def run_ngspice(cir_path):
    """Run ngspice -b on cir_path, return (returncode, stdout+stderr)."""
    proc = subprocess.run(
        [NGSPICE, "-b", cir_path],
        capture_output=True, text=True, timeout=60,
    )
    return proc.returncode, proc.stdout + proc.stderr


def read_wrdata(path, ncols_per_pair):
    """Read an ngspice wrdata file: rows of repeated (x,y) pairs.
    Returns list of dicts with 'x' and 'y0','y1',... per row."""
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            vals = [float(v) for v in line.replace(",", " ").split()]
            if len(vals) != 2 * ncols_per_pair:
                raise ValueError(f"unexpected column count in {path}: {line!r}")
            row = {"x": vals[0]}
            for i in range(ncols_per_pair):
                row[f"y{i}"] = vals[2 * i + 1]
            rows.append(row)
    return rows


# ---------------------------------------------------------------------
# Provenance checking
# ---------------------------------------------------------------------

REQUIRED_PROVENANCE_FIELDS = [
    "canonical_file", "device_class", "origin", "vendor_source_path",
    "vendor_source_sha256", "date_created", "author", "changes", "reason",
]


def check_provenance(lib_path):
    """Returns (ok: bool, message: str)."""
    sidecar = lib_path[:-4] + ".provenance.json" if lib_path.endswith(".lib") else lib_path + ".provenance.json"
    if not os.path.isfile(sidecar):
        return False, f"missing provenance sidecar: {os.path.relpath(sidecar, ROOT)}"
    try:
        with open(sidecar) as f:
            meta = json.load(f)
    except Exception as e:
        return False, f"provenance sidecar is not valid JSON: {e}"

    missing = [k for k in REQUIRED_PROVENANCE_FIELDS if k not in meta]
    if missing:
        return False, f"provenance sidecar missing fields: {missing}"

    if meta["origin"] not in ("authored", "vendor_derived"):
        return False, f"provenance 'origin' must be 'authored' or 'vendor_derived', got {meta['origin']!r}"

    if meta["origin"] == "authored":
        if meta["vendor_source_path"] is not None or meta["vendor_source_sha256"] is not None:
            return False, "origin=authored but vendor_source_path/sha256 are not null"
        return True, "authored, provenance OK"

    # vendor_derived
    vsp = meta["vendor_source_path"]
    vsh = meta["vendor_source_sha256"]
    if not vsp or not vsh:
        return False, "origin=vendor_derived but vendor_source_path/sha256 missing"
    abs_vendor_path = os.path.join(ROOT, vsp)
    if not os.path.isfile(abs_vendor_path):
        return False, f"referenced vendor source does not exist: {vsp}"
    actual_hash = sha256_of(abs_vendor_path)
    if actual_hash != vsh:
        return False, (
            f"vendor source hash MISMATCH for {vsp}: "
            f"provenance says {vsh}, file is currently {actual_hash} "
            f"(vendor file may have been modified - it should be frozen read-only)"
        )
    return True, f"vendor_derived, provenance OK (source hash verified: {vsp})"


# ---------------------------------------------------------------------
# Per-device-class testbench builders. Each returns (cir_text, csv_path,
# ncols_per_pair, check_fn(rows) -> (bool, str)).
# ---------------------------------------------------------------------

def close(a, b, rel=0.02, abs_=1e-12):
    return abs(a - b) <= max(abs_, rel * abs(b))


def tb_resistor(model_file):
    csv = os.path.join(SCRATCH_DIR, "resistors_generic_res.csv")
    cir = f"""* validate generic_res.lib
.include {model_file}
V1 in 0 DC 1
R1 in 0 1k RGEN
.control
dc TEMP 27 127 100
wrdata {csv} i(V1)
.endc
.end
"""
    def check(rows):
        if len(rows) != 2:
            return False, f"expected 2 rows (TEMP 27,127), got {len(rows)}"
        i27 = rows[0]["y0"]
        i127 = rows[1]["y0"]
        # R(27)=1000 -> I=-1mA ; R(127)=1000*(1+1e-3*100)=1100 -> I=-1/1100
        ok27 = close(i27, -1e-3, rel=0.01)
        ok127 = close(i127, -1.0 / 1100.0, rel=0.01)
        if ok27 and ok127:
            return True, f"I(27C)={i27:.6e} A (exp -1.000e-03), I(127C)={i127:.6e} A (exp -9.091e-04)"
        return False, f"I(27C)={i27:.6e}, I(127C)={i127:.6e} - TC1 temperature behavior not as expected"
    return cir, csv, 1, check


def tb_capacitor(model_file):
    csv = os.path.join(SCRATCH_DIR, "capacitors_generic_cap.csv")
    cir = f"""* validate generic_cap.lib
.include {model_file}
V1 in 0 PULSE(0 5 0 1n 1n 10m 20m)
R1 in out 1k
C1 out 0 CGEN C=1u
.control
tran 10u 5m
wrdata {csv} v(out)
.endc
.end
"""
    def check(rows):
        if len(rows) < 100:
            return False, f"too few rows ({len(rows)}) - transient may not have run"
        # find the row nearest t = 1 tau = R*C = 1ms
        target_t = 1e-3
        closest = min(rows, key=lambda r: abs(r["x"] - target_t))
        expected = 5.0 * (1 - 2.718281828 ** -1)  # ~3.1606V
        if close(closest["y0"], expected, rel=0.05):
            return True, f"v(out) at t~1tau(1ms)={closest['y0']:.4f}V (expected ~{expected:.4f}V, tau=R*C)"
        return False, f"v(out) at t~1tau={closest['y0']:.4f}V, expected ~{expected:.4f}V - RC time constant wrong"
    return cir, csv, 1, check


def tb_inductor(model_file):
    csv = os.path.join(SCRATCH_DIR, "inductors_generic_ind.csv")
    cir = f"""* validate generic_ind.lib
.include {model_file}
V1 in 0 PULSE(0 5 0 1n 1n 10m 20m)
R1 in mid 1k
L1 mid 0 LGEN inductance=1m
.control
tran 10u 5m
wrdata {csv} v(mid)
.endc
.end
"""
    def check(rows):
        if len(rows) < 10:
            return False, f"too few rows ({len(rows)})"
        first_after_edge = next(r for r in rows if r["x"] >= 1e-9)
        last = rows[-1]
        ok_edge = first_after_edge["y0"] > 4.5   # near-full step across L right after edge
        ok_final = abs(last["y0"]) < 0.01         # near 0V across L at steady state
        if ok_edge and ok_final:
            return True, f"v(L) right after edge={first_after_edge['y0']:.3f}V (~5V expected), v(L) at t=5ms={last['y0']:.2e}V (~0V expected)"
        return False, f"v(L) right after edge={first_after_edge['y0']:.3f}V, v(L) final={last['y0']:.3e}V - RL step response wrong"
    return cir, csv, 1, check


def tb_diode(model_file, name, subckt=None):
    csv = os.path.join(SCRATCH_DIR, f"diodes_{name}.csv")
    if subckt:
        device_line = f"X1 a 0 {subckt}"
    else:
        device_line = "D1 a 0 DGEN"
    cir = f"""* validate {name}
.include {model_file}
V1 in 0 DC 0.7
R1 in a 100
{device_line}
.control
dc V1 -1 0.8 0.05
wrdata {csv} v(a) i(V1)
.endc
.end
"""
    def check(rows):
        if len(rows) < 10:
            return False, f"too few rows ({len(rows)})"
        rev = next(r for r in rows if abs(r["x"] - (-1.0)) < 1e-6)
        fwd = next(r for r in rows if abs(r["x"] - 0.7) < 1e-6)
        rev_i = abs(rev["y1"])
        fwd_i = abs(fwd["y1"])
        ok = rev_i < 1e-6 and fwd_i > 1e-4 and fwd_i > 1000 * rev_i
        if ok:
            return True, f"reverse I(-1V)={rev_i:.3e}A (blocking), forward I(0.7V)={fwd_i:.3e}A (conducting)"
        return False, f"reverse I={rev_i:.3e}A, forward I={fwd_i:.3e}A - diode not behaving as expected"
    return cir, csv, 2, check


def tb_bjt(model_file, name, model_name, kind):
    csv = os.path.join(SCRATCH_DIR, f"bjt_{name}.csv")
    if kind == "npn":
        cir = f"""* validate {name} (NPN common-emitter)
.include {model_file}
Vcc vcc 0 DC 5
Vbb vbb 0 DC 1.7
Rb vbb b 10k
Rc vcc c 1k
Q1 c b 0 {model_name}
.control
op
wrdata {csv} i(Vbb) i(Vcc)
.endc
.end
"""
    else:  # pnp
        cir = f"""* validate {name} (PNP common-emitter)
.include {model_file}
Vcc vcc 0 DC -5
Vbb vbb 0 DC -1.7
Rb vbb b 10k
Rc vcc c 1k
Q1 c b 0 {model_name}
.control
op
wrdata {csv} i(Vbb) i(Vcc)
.endc
.end
"""
    def check(rows):
        if len(rows) != 1:
            return False, f"expected 1 op-point row, got {len(rows)}"
        ib = abs(rows[0]["y0"])
        ic = abs(rows[0]["y1"])
        if ib < 1e-9:
            return False, f"base current too small ({ib:.3e}A) - device may not be conducting"
        hfe = ic / ib
        ok = ic > 1e-6 and 20 <= hfe <= 500
        if ok:
            return True, f"Ib={ib:.3e}A, Ic={ic:.3e}A, hFE(computed)={hfe:.1f} (plausible range 20-500)"
        return False, f"Ib={ib:.3e}A, Ic={ic:.3e}A, hFE={hfe:.1f} - out of plausible range"
    return cir, csv, 2, check


def tb_mosfet(model_file, name, model_name, kind):
    csv = os.path.join(SCRATCH_DIR, f"mosfet_{name}.csv")
    if kind == "n":
        # two separate M-instances at Vgs=0 (should be off) and Vgs=5 (should be on)
        cir = f"""* validate {name} (NMOS on/off)
.include {model_file}
Vdd d1 0 DC 5
Vg1 g1 0 DC 0
M1 d1 g1 0 0 {model_name} W=100u L=10u
Vdd2 d2 0 DC 5
Vg2 g2 0 DC 5
M2 d2 g2 0 0 {model_name} W=100u L=10u
.control
op
wrdata {csv} i(Vdd) i(Vdd2)
.endc
.end
"""
    else:  # p
        cir = f"""* validate {name} (PMOS on/off)
.include {model_file}
Vdd d1 0 DC -5
Vg1 g1 0 DC 0
M1 d1 g1 0 0 {model_name} W=100u L=10u
Vdd2 d2 0 DC -5
Vg2 g2 0 DC -5
M2 d2 g2 0 0 {model_name} W=100u L=10u
.control
op
wrdata {csv} i(Vdd) i(Vdd2)
.endc
.end
"""
    def check(rows):
        if len(rows) != 1:
            return False, f"expected 1 op-point row, got {len(rows)}"
        i_off = abs(rows[0]["y0"])
        i_on = abs(rows[0]["y1"])
        ok = i_off < 1e-6 and i_on > 1e-4 and i_on > 100 * i_off
        if ok:
            return True, f"I(Vgs=0, off)={i_off:.3e}A, I(Vgs=+/-5V, on)={i_on:.3e}A"
        return False, f"I_off={i_off:.3e}A, I_on={i_on:.3e}A - MOSFET on/off behavior not as expected"
    return cir, csv, 2, check


def tb_jfet(model_file):
    csv = os.path.join(SCRATCH_DIR, "jfet_generic_njf.csv")
    cir = f"""* validate generic_njf.lib (JFET on/off)
.include {model_file}
Vdd d1 0 DC 5
Vgs1 g1 0 DC 0
J1 d1 g1 0 JNGEN
Vdd2 d2 0 DC 5
Vgs2 g2 0 DC -3
J2 d2 g2 0 JNGEN
.control
op
wrdata {csv} i(Vdd) i(Vdd2)
.endc
.end
"""
    def check(rows):
        if len(rows) != 1:
            return False, f"expected 1 op-point row, got {len(rows)}"
        i_on = abs(rows[0]["y0"])   # Vgs=0, above pinch-off (Vto=-2) -> on
        i_off = abs(rows[0]["y1"])  # Vgs=-3, below pinch-off -> off
        ok = i_off < 1e-6 and i_on > 1e-4 and i_on > 100 * i_off
        if ok:
            return True, f"I(Vgs=0, on)={i_on:.3e}A, I(Vgs=-3V, pinched off)={i_off:.3e}A"
        return False, f"I_on={i_on:.3e}A, I_off={i_off:.3e}A - JFET pinch-off behavior not as expected"
    return cir, csv, 2, check


def tb_lsk489(model_file):
    """REGRESSION LOCK on the L7 datasheet cross-check (ADR-013 step 4).

    Until L7 this was a declared SMOKE test: it asked only whether the
    part conducts at Vgs = 0 and is pinched off at -3 V, and it said so.
    L7 measured the transcribed model against the datasheet's own limits
    AT THE DATASHEET'S OWN TEST CONDITIONS, and the verdict was MIXED.
    This recipe asserts exactly that verdict and nothing more:

      I_DSS      2.593 mA  at VDG = 15 V, VGS = 0, 25 C
                 -> INSIDE the LSK489A window 2.5 / 5.5 / 8.5 mA, but
                    3.7% above the minimum and 53% below typical.

      V_GS(off)  -1.1244 V at VDS = 15 V, I_D = 1 nA, 25 C
                 -> OUTSIDE the published window (min -1.5 V, max -3.5 V),
                    0.376 V short of the minimum magnitude.

      V_GS       -0.6502 V at VDS = 15 V, I_D = 500 uA, 25 C
                 -> INSIDE the window -0.5 / -3.5 V.

    So this check does NOT claim datasheet conformance, because for
    V_GS(off) there is none. What it does is LOCK the numbers L7
    measured, so that a silent edit of models/jfet/lsk489.lib - exactly
    the "correction" a later reader might make after reading
    docs/limitations.md #13 - turns the suite red instead of passing
    unnoticed. The deviation itself is NC-013 in
    docs/preamp/NONCOMPLIANCE.md; the measurement, its three independent
    legs and the reasoning are in
    docs/preamp/reports/2026-09-09-L7-controllo-incrociato-lsk489.md.

    The conditions are the datasheet's, not ngspice's defaults, and that
    is not cosmetic: the datasheet is specified @ 25 C while ngspice runs
    at 27 C, and this model carries Vtotc = -2.5m, so the two differ by
    exactly 5.0 mV on V_P. And VDG = 15 V with VGS = 0 means VDS = 15 V
    AT THE TERMINALS - Rd=11 and Rs=30 are internal to the model.

    One sweep answers all three: I_DSS is its last point (VGS = 0) and
    the two voltages are threshold crossings on the way there.

    ngspice emits four "unrecognized parameter ... ignored" warnings for
    isr/alpha/vk/mj on every run. They are expected - see the header of
    models/jfet/lsk489.lib - and do not affect the exit code.
    """
    csv = os.path.join(SCRATCH_DIR, "jfet_lsk489.csv")
    cir = f"""* validate lsk489.lib - LSK489A at the datasheet's own test conditions
.include {model_file}
Vdd d 0 DC 15
Vgg g 0 DC 0
J1 d g 0 LSK489A
.control
set temp = 25
dc Vgg -1.30 0 50u
wrdata {csv} i(Vdd)
.endc
.end
"""
    # Datasheet LSK489A, RevA40 page 2 (Electrical Characteristics), and
    # the values L7 measured against it.
    IDSS_MIN, IDSS_MAX = 2.5e-3, 8.5e-3
    VGS_OP_MIN, VGS_OP_MAX = -3.5, -0.5
    VP_DATASHEET_MIN = -1.5
    VP_MEASURED = -1.124355   # V, at I_D = 1 nA, VDS = 15 V, 25 C
    VP_TOL = 1e-3

    def check(rows):
        if len(rows) < 20000:
            return False, f"expected the full Vgs sweep, got {len(rows)} rows"
        pts = [(r["x"], abs(r["y0"])) for r in rows]
        idss = pts[-1][1]   # the sweep ends at VGS = 0, which is the I_DSS point

        def crossing(target):
            prev = None
            for v, i in pts:
                if prev is not None and prev[1] < target <= i:
                    v0, i0 = prev
                    return v0 + (target - i0) / (i - i0) * (v - v0)
                prev = (v, i)
            return None

        vp = crossing(1e-9)          # datasheet definition of V_GS(off)
        vgs_op = crossing(500e-6)    # datasheet definition of V_GS
        if vp is None or vgs_op is None:
            return False, ("I_D never crossed 1 nA and/or 500 uA in the swept "
                           "range - the model's threshold has moved")

        problems = []
        if not (IDSS_MIN <= idss <= IDSS_MAX):
            problems.append(
                f"I_DSS={idss:.4e}A is outside the LSK489A window "
                f"[{IDSS_MIN:.1e}, {IDSS_MAX:.1e}]A")
        if abs(vp - VP_MEASURED) > VP_TOL:
            problems.append(
                f"V_P={vp:.6f}V has moved from the value L7 measured "
                f"({VP_MEASURED:.6f}V) by more than {VP_TOL * 1e3:.1f}mV - "
                f"the model line changed")
        if not (VGS_OP_MIN <= vgs_op <= VGS_OP_MAX):
            problems.append(
                f"V_GS@500uA={vgs_op:.6f}V is outside the window "
                f"[{VGS_OP_MIN}, {VGS_OP_MAX}]V")
        if problems:
            return False, "; ".join(problems)

        short_by = abs(VP_DATASHEET_MIN) - abs(vp)
        return True, (
            f"I_DSS={idss * 1e3:.3f}mA in [2.5, 8.5]mA; "
            f"V_GS@500uA={vgs_op:.4f}V in [-0.5, -3.5]V; "
            f"V_P={vp:.4f}V locked to L7 - still {short_by:.3f}V short of the "
            f"datasheet -1.5V minimum, which is NC-013, not a regression")
    return cir, csv, 1, check


def tb_ls350(model_file):
    """REGRESSION LOCK on the L22 datasheet cross-check of the LS352.

    Same shape as tb_lsk489, and for the same reason: the model is a HAND
    TRANSCRIPTION from a vendor PDF, so the failure mode to guard against
    is a silent edit of a digit. What this asserts is the verdict L22
    measured at the datasheet's own conditions, 25 C, no more:

      hFE @ IC = 1 mA, VCE = 5 V     490.6   -> INSIDE the LS352 window
                                                (200 MIN), and locked
      hFE @ IC = 100 uA              483.2   -> INSIDE [200, 600]
      hFE @ IC = 10 uA               441.2   -> INSIDE [200, 600]

    It does NOT assert datasheet conformance overall, because for fT
    there is none: the model gives 129.5 MHz at IC = 1 mA against a
    200 MHz MINIMUM, 35% low. That deviation is NC-020, not a regression,
    and it is deliberately NOT re-measured here - an fT sweep costs an .ac
    run per point and the suite is a lock, not a lab. The measurement and
    its three agreeing legs are in the L22 report.

    The conditions are the datasheet's and not ngspice's: the datasheet is
    @ 25 C, ngspice defaults to 27, and XTB = 1.5 makes hFE temperature
    dependent, so running at the default would shift every number here.

    ngspice prints "warning, model type mismatch in line" on every run,
    because the vendor writes the device type inside the parentheses. It
    is expected output - see the header of models/bjt_pnp/ls350.lib, where
    it is shown to change no number - and does not affect the exit code.
    """
    csv = os.path.join(SCRATCH_DIR, "bjt_pnp_ls350.csv")
    cir = f"""* validate ls350.lib - LS352 grade at the datasheet's own conditions
.include {model_file}
Q1 c b 0 LS350
Vb b 0 DC -0.6
Vc c 0 DC -5
.control
set temp = 25
save @q1[ic] @q1[ib]
dc Vb -0.45 -0.95 -0.0002
wrdata {csv} @q1[ic] @q1[ib]
.endc
.end
"""
    # Datasheet LS350SeriesDSRevA5.pdf, ELECTRICAL CHARACTERISTICS @ 25 C,
    # LS352 column, and the values L22 measured against it.
    HFE_MIN, HFE_MAX = 200.0, 600.0
    MEASURED = {1e-3: 490.6, 100e-6: 483.2, 10e-6: 441.2}
    TOL_PCT = 0.5   # a transcription slip moves these by far more than 0.5%

    def check(rows):
        if len(rows) < 2000:
            return False, f"expected the full Vb sweep, got {len(rows)} rows"
        pts = [(abs(r["y0"]), abs(r["y1"])) for r in rows]   # (|ic|, |ib|)
        problems, report = [], []
        for target, expected in sorted(MEASURED.items(), reverse=True):
            prev = None
            hfe = None
            for ic, ib in pts:
                if prev is not None and prev[0] < target <= ic and ib > 0:
                    # Interpolate IB at the crossing, the way ngspice's own
                    # `meas ... when` does. Taking the bracketing sample
                    # instead reads 438.2 where meas reads 441.2 - a 0.7%
                    # error that is the sweep step, not the model, and it
                    # would make this lock fail for the wrong reason.
                    ic0, ib0 = prev
                    f = (target - ic0) / (ic - ic0)
                    hfe = target / (ib0 + f * (ib - ib0))
                    break
                prev = (ic, ib)
            if hfe is None:
                problems.append(f"IC never crossed {target:g} A in the sweep")
                continue
            if not (HFE_MIN <= hfe <= HFE_MAX):
                problems.append(
                    f"hFE={hfe:.1f} at IC={target:g}A is outside the LS352 "
                    f"window [{HFE_MIN:.0f}, {HFE_MAX:.0f}]")
            if abs(hfe - expected) / expected * 100 > TOL_PCT:
                problems.append(
                    f"hFE={hfe:.1f} at IC={target:g}A has moved from the "
                    f"value L22 measured ({expected}) by more than "
                    f"{TOL_PCT}% - the model line changed")
            report.append(f"hFE@{target:g}A={hfe:.1f}")
        if problems:
            return False, "; ".join(problems)
        return True, (", ".join(report) + " - all inside [200, 600]; fT is "
                      "35% below the datasheet minimum, which is NC-020, "
                      "not a regression")
    return cir, csv, 2, check


# ---------------------------------------------------------------------
# L25: the five vendor models promoted out of vendor/ into models/.
#
# These are the first recipes that need MORE THAN ONE output file, and
# the reason is physical, not stylistic: fT and C_obo (and the diode's
# C_T) are AC quantities, the hFE and V_F points are DC, and `wrdata`
# writes one plot at a time. So a builder here returns a LIST of output
# paths and a LIST of column counts, and its check_fn receives the list
# of row-sets in the same order. main() handles both shapes; the fourteen
# single-output recipes above were not touched.
#
# Two things that every one of these decks does, and that are worth
# copying rather than rediscovering:
#
#   * `destroy all` between analyses. Each analysis makes a NEW numbered
#     plot, and without this the next wrdata can silently write the
#     previous one - docs/limitations.md #10, the defect that was worth a
#     factor of 3.4 in L5.
#   * `save` lists the internal device vectors AND the branch currents.
#     @q1[ic] is not recorded unless it is saved, and once there is an
#     explicit save list, i(Vc) has to be on it too.
# ---------------------------------------------------------------------

def _interp_hfe(rows, target):
    """hFE at a target IC, interpolating IB the way ngspice's own
    `meas ... when` does. Reading the bracketing sample instead is worth
    the sweep step - 0.7% on the LS350 in L22 - which would fail these
    locks for the wrong reason. Returns None if IC never reaches target."""
    prev = None
    for r in rows:
        ic, ib = abs(r["y0"]), abs(r["y1"])
        if prev is not None and prev[0] < target <= ic and ib > 0:
            ic0, ib0 = prev
            f = (target - ic0) / (ic - ic0)
            return target / (ib0 + f * (ib - ib0))
        prev = (ic, ib)
    return None


def _row_at(rows, freq):
    """The AC row nearest a frequency. The sweeps below are chosen so that
    the datasheet's own test frequency is hit exactly."""
    return min(rows, key=lambda r: abs(r["x"] - freq))


def _cap_from(row, re_key, im_key):
    """Capacitance from the current a 1 V AC source pushes into a reverse
    biased junction: C = |Im(I)| / (2 pi f). The real part is returned too,
    because it is what says whether the reading is capacitive at all."""
    import math
    c = abs(row[im_key]) / (2.0 * math.pi * row["x"])
    return c, abs(row[re_key] / row[im_key])


def _tb_diodes_bjt(model_file, model_name, csv_base, sign, ib_ft,
                   hfe_window, hfe_locked, ft_locked, cobo_locked, cobo_max):
    """Shared body of tb_mmbt5401() and tb_mmbt5551() - the two Diodes
    Incorporated models are the same die polarity-mirrored, are specified
    at mirrored conditions, and differ only in numbers. `sign` is +1 for
    the NPN and -1 for the PNP.

    Three devices in one deck, because the datasheet specifies the three
    quantities at three DIFFERENT operating points and one instance cannot
    be at all of them:

      Q1  hFE   at |VCE| = 5 V,  swept base voltage
      Q2  fT    at |VCE| = 10 V, FIXED base current
      Q3  C_obo at |VCB| = 10 V, EMITTER OPEN (1 T-ohm to ground, which is
          the DC path the solver needs and 5 orders below the junction's
          own admittance at 1 MHz)

    THE fT BIAS IS A HARD-CODED BASE CURRENT, and the first output file
    exists to keep that honest: it records Q2's collector current from an
    op, and the check refuses if it is not the datasheet's 10 mA. That is
    not ceremony - it is the exact thing that went wrong in L24, whose
    169.5 MHz for the MMBT5401 came from a round IB = 100 uA that this
    model turns into IC = 12.68 mA, 27% above the specified test current.

    fT IS THE DATASHEET'S DEFINITION, NOT THE UNITY-GAIN CROSSING: the
    Diodes tables specify fT at "f = 100MHz", i.e. the gain-bandwidth
    product measured there, and the 100 MHz minimum is written against
    that. On the MMBT5401 the two definitions agree to 0.02%; on the
    MMBT5551 they differ by 1.8%, so the choice is not cosmetic. The AC
    sweep is `dec 2` from 1 MHz to 100 MHz, which lands exactly on both
    the C_obo test frequency and the fT test frequency.

    Conditions are the datasheet's and not ngspice's: set temp = 25,
    because the tables are @ 25 C, ngspice defaults to 27, and XTB makes
    hFE temperature dependent.
    """
    op_csv = os.path.join(SCRATCH_DIR, csv_base + "_op.csv")
    hfe_csv = os.path.join(SCRATCH_DIR, csv_base + "_hfe.csv")
    ac_csv = os.path.join(SCRATCH_DIR, csv_base + "_ac.csv")
    v5, v10 = 5.0 * sign, 10.0 * sign
    vb_start, vb_stop, vb_step = 0.45 * sign, 1.05 * sign, 0.0002 * sign
    # PNP base current leaves the base, NPN base current enters it.
    ib_nodes = "b2 0" if sign < 0 else "0 b2"
    cir = f"""* validate {csv_base}.lib - {model_name} at the datasheet's own conditions
.include {model_file}
Q1 c1 b1 0 {model_name}
Vc1 c1 0 DC {v5}
Vb1 b1 0 DC {0.6 * sign}
Q2 c2 b2 0 {model_name}
Vc2 c2 0 DC {v10}
Ib2 {ib_nodes} DC {ib_ft:.9g} AC 1
Q3 c3 0 e3 {model_name}
Re3 e3 0 1T
Vc3 c3 0 DC {v10} AC 1
.control
set temp = 25
save @q1[ic] @q1[ib] @q2[ic] i(Vc2) i(Vc3)
op
wrdata {op_csv} @q2[ic]
destroy all
dc Vb1 {vb_start} {vb_stop} {vb_step}
wrdata {hfe_csv} @q1[ic] @q1[ib]
destroy all
ac dec 2 1meg 100meg
let hfe = mag(i(Vc2))
let cre = real(i(Vc3))
let cim = imag(i(Vc3))
wrdata {ac_csv} hfe cre cim
destroy all
.endc
.end
"""
    HFE_MIN, HFE_MAX = hfe_window
    FT_MIN = 100e6
    TOL_PCT = 0.5   # a changed digit moves these by far more than 0.5%

    def check(sets):
        op_rows, hfe_rows, ac_rows = sets
        problems, report = [], []

        if len(op_rows) != 1:
            return False, f"expected one op row, got {len(op_rows)}"
        ic_ft = abs(op_rows[0]["y0"])
        if abs(ic_ft - 10e-3) / 10e-3 > 0.001:
            problems.append(
                f"the fT bias is off: IC = {ic_ft * 1e3:.4f} mA where the "
                f"datasheet specifies 10 mA. The hard-coded base current no "
                f"longer produces the test current, so the fT below would be "
                f"measured at the wrong operating point")

        if len(hfe_rows) < 2000:
            return False, f"expected the full Vb sweep, got {len(hfe_rows)} rows"
        hfe = _interp_hfe(hfe_rows, 10e-3)
        if hfe is None:
            problems.append("IC never reached 10 mA in the sweep")
        else:
            if not (HFE_MIN <= hfe <= HFE_MAX):
                problems.append(
                    f"hFE={hfe:.3f} at IC=10mA is outside the datasheet window "
                    f"[{HFE_MIN:.0f}, {HFE_MAX:.0f}]")
            if abs(hfe - hfe_locked) / hfe_locked * 100 > TOL_PCT:
                problems.append(
                    f"hFE={hfe:.3f} has moved from the value L25 measured "
                    f"({hfe_locked}) by more than {TOL_PCT}% - the model changed")
            report.append(f"hFE@10mA={hfe:.1f}")

        if len(ac_rows) < 3:
            return False, f"expected the AC sweep, got {len(ac_rows)} rows"
        r100 = _row_at(ac_rows, 100e6)
        ft = r100["x"] * r100["y0"]
        if ft < FT_MIN:
            problems.append(
                f"fT={ft / 1e6:.3f}MHz is below the datasheet minimum "
                f"{FT_MIN / 1e6:.0f}MHz")
        if abs(ft - ft_locked) / ft_locked * 100 > TOL_PCT:
            problems.append(
                f"fT={ft / 1e6:.3f}MHz has moved from the value L25 measured "
                f"({ft_locked / 1e6:.3f}MHz) by more than {TOL_PCT}%")
        report.append(f"fT={ft / 1e6:.1f}MHz")

        r1 = _row_at(ac_rows, 1e6)
        cobo, ratio = _cap_from(r1, "y1", "y2")
        if ratio > 0.05:
            problems.append(
                f"the C_obo reading is not capacitive: |Re/Im| = {ratio:.3g}")
        if cobo > cobo_max:
            problems.append(
                f"C_obo={cobo * 1e12:.4f}pF exceeds the datasheet maximum "
                f"{cobo_max * 1e12:.0f}pF")
        if abs(cobo - cobo_locked) / cobo_locked * 100 > TOL_PCT:
            problems.append(
                f"C_obo={cobo * 1e12:.4f}pF has moved from the value L25 "
                f"measured ({cobo_locked * 1e12:.4f}pF) by more than {TOL_PCT}%")
        report.append(f"C_obo={cobo * 1e12:.3f}pF")

        if problems:
            return False, "; ".join(problems)
        return True, (", ".join(report) + " - three of three inside the "
                      "datasheet windows, at IC verified to 10.000 mA")
    return cir, [op_csv, hfe_csv, ac_csv], [1, 2, 3], check


def tb_mmbt5401(model_file):
    """REGRESSION LOCK on the L25 cross-check of the MMBT5401 (the VAS).

    Datasheet DS30057 Rev. 12-2, (c) 2024. Three quantities, three of
    three inside the manufacturer's own windows - with the MMBT5551 the
    only model in this repo with no mixed verdict:

      hFE   @ IC = -10 mA, VCE = -5 V              124.917  (60 .. 240)
      fT    @ IC = -10 mA, VCE = -10 V, 100 MHz    160.116 MHz  (100 min)
      C_obo @ VCB = -10 V, 1 MHz, IE = 0           3.7063 pF    (6 max)

    THE fT VALUE IS NOT L24's. L24 and ADR-017 record 169.5 MHz; that
    number is reproduced exactly by a round IB = 100 uA, which this model
    turns into IC = 12.68 mA. Re-measured at the datasheet's own IC =
    10.000 mA it is 160.1 MHz on three agreeing legs. The verdict does not
    change, the number moves by -5.5%, and it is the number the dominant
    pole discussion rests on. See _tb_diodes_bjt() and the file header.

    The base current below is what produces IC = 10.000 mA with the model
    AS FROZEN; the op check in the recipe refuses if that stops being
    true, so the lock cannot quietly drift onto another operating point.
    """
    return _tb_diodes_bjt(
        model_file, "MMBT5401", "bjt_pnp_mmbt5401", -1,
        ib_ft=78.9569265e-6, hfe_window=(60.0, 240.0), hfe_locked=124.917,
        ft_locked=160.116e6, cobo_locked=3.7063e-12, cobo_max=6e-12)


def tb_mmbt5551(model_file):
    """REGRESSION LOCK on the L25 cross-check of the MMBT5551 (tail sink,
    both cascodes, VAS load, Vbe multiplier - five instances per block).

    Datasheet DS30061 Rev. 15-2, (c) 2025:

      hFE   @ IC = 10 mA, VCE = 5 V               107.218  (80 .. 250)
      fT    @ IC = 10 mA, VCE = 10 V, 100 MHz     175.683 MHz  (100 min)
      C_obo @ VCB = 10 V, 1 MHz                   2.2207 pF    (6 max)

    ON THIS DEVICE THE fT DEFINITION MATTERS. The datasheet's own - the
    gain-bandwidth product at ftest = 100 MHz - gives 175.683 MHz, which
    is what is locked because it is what the 100 MHz minimum is written
    against. The |hfe| = 1 crossing gives 172.579 MHz, 1.8% lower, because
    the roll-off is not a clean -20 dB/dec to unity: GBW peaks at 176.9
    MHz near 30 MHz and is down to 105 MHz by 1 GHz. On the MMBT5401 the
    same two definitions agree to 0.02%, which is why the difference is a
    property of this model rather than of the method.
    """
    return _tb_diodes_bjt(
        model_file, "MMBT5551", "bjt_npn_mmbt5551", +1,
        ib_ft=91.6805512e-6, hfe_window=(80.0, 250.0), hfe_locked=107.218,
        ft_locked=175.683e6, cobo_locked=2.2207e-12, cobo_max=6e-12)


def _tb_mje(model_file, model_name, csv_base, sign, ib_ft, hfe_points,
            ft_locked):
    """Shared body of tb_mje15032() and tb_mje15033(), the two halves of
    the output stage. One datasheet covers both (MJE15032/D, December 2024
    Rev. 7), specifying hFE at 0.5 / 1.0 / 2.0 A with VCE = 5 V and fT at
    IC = 500 mA, VCE = 10 V.

    fT HERE IS NOT THE UNITY-GAIN CROSSING EITHER, AND ON THESE TWO IT
    CHANGES A VERDICT RATHER THAN A DIGIT. Note 2 of the datasheet says
    "fT = hfe ftest" and the test row gives ftest = 1.0 MHz, so fT is the
    gain-bandwidth product measured AT 1 MHz. At 1 MHz these devices are
    only ~2.6 octaves above their own beta pole, so that reading is
    materially lower than the asymptote: 27.667 MHz for the NPN and 29.286
    MHz for the PNP, against a 30 MHz minimum, where the crossings (30.713
    and 30.719 MHz) would both clear it. The minimum is written against
    the 1 MHz test, so the 1 MHz reading is the comparison that means
    something - and made that way NEITHER MODEL REACHES ITS OWN MINIMUM.
    That is NC-025, opened by L25; L24 had recorded 31.04 / 31.38 MHz and
    read them as inside.

    So this recipe locks two published deviations and does NOT claim
    conformance: NC-024 (the NPN's hFE at 0.5 A) and NC-025 (fT on both).
    A recipe that declared conformance where there is none would be worse
    than no recipe.

    As in the Diodes recipes the fT bias is a hard-coded base current and
    the first output file records the collector current it actually
    produces, so the lock cannot drift onto another operating point.
    """
    op_csv = os.path.join(SCRATCH_DIR, csv_base + "_op.csv")
    hfe_csv = os.path.join(SCRATCH_DIR, csv_base + "_hfe.csv")
    ac_csv = os.path.join(SCRATCH_DIR, csv_base + "_ac.csv")
    ib_nodes = "b2 0" if sign < 0 else "0 b2"
    cir = f"""* validate {csv_base}.lib - {model_name} at the datasheet's own conditions
.include {model_file}
Q1 c1 b1 0 {model_name}
Vc1 c1 0 DC {5.0 * sign}
Vb1 b1 0 DC {0.8 * sign}
Q2 c2 b2 0 {model_name}
Vc2 c2 0 DC {10.0 * sign}
Ib2 {ib_nodes} DC {ib_ft:.9g} AC 1
.control
set temp = 25
save @q1[ic] @q1[ib] @q2[ic] i(Vc2)
op
wrdata {op_csv} @q2[ic]
destroy all
dc Vb1 {0.5 * sign} {1.6 * sign} {0.0002 * sign}
wrdata {hfe_csv} @q1[ic] @q1[ib]
destroy all
ac lin 1 1meg 1meg
let hfe = mag(i(Vc2))
wrdata {ac_csv} hfe
destroy all
.endc
.end
"""
    FT_MIN = 30e6
    TOL_PCT = 0.5

    def check(sets):
        op_rows, hfe_rows, ac_rows = sets
        problems, report = [], []

        if len(op_rows) != 1:
            return False, f"expected one op row, got {len(op_rows)}"
        ic_ft = abs(op_rows[0]["y0"])
        if abs(ic_ft - 0.5) / 0.5 > 0.001:
            problems.append(
                f"the fT bias is off: IC = {ic_ft * 1e3:.2f} mA where the "
                f"datasheet specifies 500 mA")

        if len(hfe_rows) < 4000:
            return False, f"expected the full Vb sweep, got {len(hfe_rows)} rows"
        for target, locked, minimum in hfe_points:
            hfe = _interp_hfe(hfe_rows, target)
            if hfe is None:
                problems.append(f"IC never reached {target:g} A in the sweep")
                continue
            if abs(hfe - locked) / locked * 100 > TOL_PCT:
                problems.append(
                    f"hFE={hfe:.3f} at IC={target:g}A has moved from the value "
                    f"L25 measured ({locked}) by more than {TOL_PCT}%")
            mark = "" if hfe >= minimum else f" BELOW its {minimum:g} minimum"
            report.append(f"hFE@{target:g}A={hfe:.1f}{mark}")

        if len(ac_rows) != 1:
            return False, f"expected one AC row, got {len(ac_rows)}"
        ft = ac_rows[0]["x"] * ac_rows[0]["y0"]
        if abs(ft - ft_locked) / ft_locked * 100 > TOL_PCT:
            problems.append(
                f"fT={ft / 1e6:.3f}MHz has moved from the value L25 measured "
                f"({ft_locked / 1e6:.3f}MHz) by more than {TOL_PCT}%")
        short = (FT_MIN - ft) / FT_MIN * 100
        report.append(f"fT={ft / 1e6:.3f}MHz ({short:.1f}% below its 30MHz "
                      f"minimum - NC-025)")

        if problems:
            return False, "; ".join(problems)
        return True, ", ".join(report)
    return cir, [op_csv, hfe_csv, ac_csv], [1, 2, 1], check


def tb_mje15032(model_file):
    """REGRESSION LOCK on the L25 cross-check of the MJE15032, the NPN
    output device. TWO of its four checked points are OUTSIDE the
    manufacturer's own datasheet, and this recipe asserts exactly that:

      hFE @ IC = 0.5 A   66.389    70 MIN.       OUTSIDE by 5.1%  (NC-024)
      hFE @ IC = 1.0 A   61.335    50 MIN.       inside
      hFE @ IC = 2.0 A   53.488    10 MIN.       inside
      fT  @ 500 mA       27.667 MHz  30 MHz MIN. OUTSIDE by 7.8%  (NC-025)

    The 2.0 A point corrects L24, which recorded it as "not reached" -
    that was the extent of its base sweep, not a property of the model,
    which reaches IC = 6.8 A smoothly.

    Both deviations run pessimistic: less gain and less speed than the
    guaranteed part. That is the safe direction, but it is not a known
    amount, and the model does not describe a conforming device.
    """
    return _tb_mje(
        model_file, "Qmje15032", "bjt_npn_mje15032", +1,
        ib_ft=6.22718707e-3,
        hfe_points=[(0.5, 66.389, 70.0), (1.0, 61.335, 50.0),
                    (2.0, 53.488, 10.0)],
        ft_locked=27.667e6)


def tb_mje15033(model_file):
    """REGRESSION LOCK on the L25 cross-check of the MJE15033, the PNP
    output device. hFE is clean at all three published points, fT is not:

      hFE @ IC = 0.5 A   88.218    70 MIN.       inside (by 26%)
      hFE @ IC = 1.0 A   66.917    50 MIN.       inside
      hFE @ IC = 2.0 A   42.766    10 MIN.       inside
      fT  @ 500 mA       29.286 MHz  30 MHz MIN. OUTSIDE by 2.4%  (NC-025)

    Worth reading next to its NPN complement: hFE 129.4 here against 75.7
    there at the project's actual 15 mA working point is a 1.7x IMBALANCE
    inside a complementary follower, which the hand-written placeholders
    could not show because they were symmetric by construction. That is
    Fase 4 material, not a regression, and is not asserted here.
    """
    return _tb_mje(
        model_file, "Qmje15033", "bjt_pnp_mje15033", -1,
        ib_ft=3.54936812e-3,
        hfe_points=[(0.5, 88.218, 70.0), (1.0, 66.917, 50.0),
                    (2.0, 42.766, 10.0)],
        ft_locked=29.286e6)


def tb_1n4148(model_file):
    """REGRESSION LOCK on the L25 cross-check of the 1N4148 bias diode.

    Datasheet 1N914/D, September 2024 Rev. 6 - the 1N4148 row, which is
    not the 914B row. Both published limits are inside:

      V_F @ I_F = 10 mA        0.766187 V   1.0 V MAX.   (23% margin)
      C_T @ V_R = 0, 1 MHz     0.8687 pF    4.0 pF MAX.

    THE MODEL NAME IS D1N914 AND THE FILE IT CAME FROM IS 1n914.lib, while
    this file is named for the part. All three are correct and none should
    be "corrected": onsemi files the 1N4148 under the 1N914 document, and
    the file that DOES carry the part's name - 1n4148.lib on the same
    server - contains .SUBCKT 1N4148WT, the SOD-323 variant, which ngspice
    would load without a word. docs/limitations.md #20.

    C_T is measured as the current a 1 V AC source pushes into the
    unbiased junction, C = |Im(I)| / (2 pi f); the check also refuses if
    the reading is not dominated by its imaginary part, because that is
    what says the number is a capacitance at all.

    Two devices in the deck because V_F needs a forward current source and
    C_T needs zero bias - one instance cannot be at both.
    """
    vf_csv = os.path.join(SCRATCH_DIR, "diodes_1n4148_vf.csv")
    ct_csv = os.path.join(SCRATCH_DIR, "diodes_1n4148_ct.csv")
    cir = f"""* validate 1n4148.lib - onsemi D1N914 at the datasheet's own conditions
.include {model_file}
If 0 a DC 0.01
D1 a 0 D1N914
Vc k 0 DC 0 AC 1
D2 k 0 D1N914
.control
set temp = 25
save v(a) i(Vc)
dc If 0.0005 0.02 0.00001
wrdata {vf_csv} v(a)
destroy all
ac lin 1 1meg 1meg
let cre = real(i(Vc))
let cim = imag(i(Vc))
wrdata {ct_csv} cre cim
destroy all
.endc
.end
"""
    VF_MAX = 1.0
    CT_MAX = 4e-12
    VF_LOCKED = 0.766187      # V, at IF = 10 mA, 25 C
    VF_TOL = 1e-3
    CT_LOCKED = 0.8687e-12
    TOL_PCT = 0.5

    def check(sets):
        vf_rows, ct_rows = sets
        problems, report = [], []

        if len(vf_rows) < 1000:
            return False, f"expected the full IF sweep, got {len(vf_rows)} rows"
        prev, vf = None, None
        for r in vf_rows:
            i, v = r["x"], r["y0"]
            if prev is not None and prev[0] < 10e-3 <= i:
                i0, v0 = prev
                vf = v0 + (10e-3 - i0) / (i - i0) * (v - v0)
                break
            prev = (i, v)
        if vf is None:
            problems.append("IF never reached 10 mA in the sweep")
        else:
            if vf > VF_MAX:
                problems.append(
                    f"V_F={vf:.6f}V exceeds the datasheet maximum {VF_MAX}V")
            if abs(vf - VF_LOCKED) > VF_TOL:
                problems.append(
                    f"V_F={vf:.6f}V has moved from the value L25 measured "
                    f"({VF_LOCKED:.6f}V) by more than {VF_TOL * 1e3:.0f}mV")
            report.append(f"V_F@10mA={vf:.4f}V")

        if len(ct_rows) != 1:
            return False, f"expected one AC row, got {len(ct_rows)}"
        ct, ratio = _cap_from(ct_rows[0], "y0", "y1")
        if ratio > 0.05:
            problems.append(
                f"the C_T reading is not capacitive: |Re/Im| = {ratio:.3g}")
        if ct > CT_MAX:
            problems.append(
                f"C_T={ct * 1e12:.4f}pF exceeds the datasheet maximum "
                f"{CT_MAX * 1e12:.0f}pF")
        if abs(ct - CT_LOCKED) / CT_LOCKED * 100 > TOL_PCT:
            problems.append(
                f"C_T={ct * 1e12:.4f}pF has moved from the value L25 measured "
                f"({CT_LOCKED * 1e12:.4f}pF) by more than {TOL_PCT}%")
        report.append(f"C_T@VR=0={ct * 1e12:.4f}pF")

        if problems:
            return False, "; ".join(problems)
        return True, (", ".join(report) + " - both published limits inside "
                      "(C_T sits 4.6x below its ceiling, so the model is a "
                      "typical specimen, not the datasheet's worst case)")
    return cir, [vf_csv, ct_csv], [1, 2], check


def tb_opamp(model_file):
    csv = os.path.join(SCRATCH_DIR, "opamp_generic.csv")
    cir = f"""* validate generic_opamp.lib (unity-gain buffer)
.include {model_file}
Vcc vcc 0 DC 15
Vee vee 0 DC -15
Vin vin 0 DC 1
X1 vin out vcc vee out OPAMP_GENERIC
.control
op
wrdata {csv} v(vin) v(out)
.endc
.end
"""
    def check(rows):
        if len(rows) != 1:
            return False, f"expected 1 op-point row, got {len(rows)}"
        vin = rows[0]["y0"]
        vout = rows[0]["y1"]
        ok = close(vout, vin, rel=0.001)
        if ok:
            return True, f"unity-buffer: Vin={vin:.6f}V, Vout={vout:.6f}V (diff={abs(vin-vout):.2e}V)"
        return False, f"Vin={vin:.6f}V, Vout={vout:.6f}V - feedback buffer not tracking input"
    return cir, csv, 2, check


def tb_transformer(model_file):
    csv = os.path.join(SCRATCH_DIR, "subckt_generic_transformer.csv")
    cir = f"""* validate generic_transformer.lib (N=5 turns ratio, open-circuit secondary)
.include {model_file}
V1 vsrc 0 AC 1
Rs vsrc pri_p 1
Rload sec_p 0 1MEG
X1 pri_p 0 sec_p 0 XFMR_GENERIC PARAMS: N=5 LPRI=1m
.control
ac dec 5 10k 100k
wrdata {csv} vdb(pri_p) vdb(sec_p)
.endc
.end
"""
    def check(rows):
        if len(rows) < 3:
            return False, f"too few rows ({len(rows)})"
        last = rows[-1]
        diff_db = last["y1"] - last["y0"]
        import math
        expected_db = 20 * math.log10(5 * 0.999)
        ok = close(diff_db, expected_db, rel=0.05, abs_=0.5)
        if ok:
            return True, f"sec/pri ratio at {last['x']:.0f}Hz = {diff_db:.2f}dB (expected ~{expected_db:.2f}dB for N=5, K=0.999)"
        return False, f"sec/pri ratio = {diff_db:.2f}dB, expected ~{expected_db:.2f}dB - transformer ratio wrong"
    return cir, csv, 2, check


# ---------------------------------------------------------------------
# Registry: relative path (from MODELS_DIR) -> builder function
# ---------------------------------------------------------------------

def build_registry():
    reg = {}
    reg["resistors/generic_res.lib"] = lambda p: tb_resistor(p)
    reg["capacitors/generic_cap.lib"] = lambda p: tb_capacitor(p)
    reg["inductors/generic_ind.lib"] = lambda p: tb_inductor(p)
    reg["diodes/generic_diode.lib"] = lambda p: tb_diode(p, "generic_diode")
    reg["diodes/generic_diode_from_vendor.lib"] = lambda p: tb_diode(p, "generic_diode_from_vendor", subckt="VENDOR_1N4148_GENERIC")
    reg["bjt_npn/generic_npn.lib"] = lambda p: tb_bjt(p, "generic_npn", "QNGEN", "npn")
    reg["bjt_pnp/generic_pnp.lib"] = lambda p: tb_bjt(p, "generic_pnp", "QPGEN", "pnp")
    reg["mosfet_n/generic_nmos.lib"] = lambda p: tb_mosfet(p, "generic_nmos", "MNGEN", "n")
    reg["mosfet_p/generic_pmos.lib"] = lambda p: tb_mosfet(p, "generic_pmos", "MPGEN", "p")
    reg["jfet/generic_njf.lib"] = lambda p: tb_jfet(p)
    reg["jfet/lsk489.lib"] = lambda p: tb_lsk489(p)
    reg["bjt_pnp/ls350.lib"] = lambda p: tb_ls350(p)
    # L25 - the five vendor models promoted out of vendor/ (NC-017).
    reg["bjt_pnp/mmbt5401.lib"] = lambda p: tb_mmbt5401(p)
    reg["bjt_npn/mmbt5551.lib"] = lambda p: tb_mmbt5551(p)
    reg["bjt_npn/mje15032.lib"] = lambda p: tb_mje15032(p)
    reg["bjt_pnp/mje15033.lib"] = lambda p: tb_mje15033(p)
    reg["diodes/1n4148.lib"] = lambda p: tb_1n4148(p)
    reg["opamp/generic_opamp.lib"] = lambda p: tb_opamp(p)
    reg["subckt_generic/generic_transformer.lib"] = lambda p: tb_transformer(p)
    return reg


def discover_lib_files():
    found = []
    for dirpath, _, filenames in os.walk(MODELS_DIR):
        for fn in filenames:
            if fn.endswith(".lib"):
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, MODELS_DIR)
                found.append(rel)
    return sorted(found)


def main():
    check_provenance_only = "--check-provenance" in sys.argv

    registry = build_registry()
    lib_files = discover_lib_files()

    results = []  # (name, status, message)
    any_fail = False

    for rel in lib_files:
        abs_path = os.path.join(MODELS_DIR, rel)

        # 1. provenance check (always)
        prov_ok, prov_msg = check_provenance(abs_path)
        results.append((f"{rel} [provenance]", "PASS" if prov_ok else "FAIL", prov_msg))
        if not prov_ok:
            any_fail = True

        if check_provenance_only:
            continue

        # 2. electrical test
        if rel not in registry:
            results.append((f"{rel} [electrical]", "SKIP", "no test recipe registered for this file"))
            any_fail = True
            continue

        try:
            cir_text, csv_path, ncols, check_fn = registry[rel](abs_path)
        except Exception as e:
            results.append((f"{rel} [electrical]", "FAIL", f"error building testbench: {e}"))
            any_fail = True
            continue

        cir_path = os.path.join(SCRATCH_DIR, os.path.basename(rel).replace(".lib", "") + "_tb.cir")
        with open(cir_path, "w") as f:
            f.write(cir_text)

        # A recipe may write MORE THAN ONE output file: fT, C_obo and C_T
        # are AC quantities while hFE and V_F are DC, and wrdata writes one
        # plot at a time. When csv_path is a list, ncols is a list of the
        # same length and check_fn receives the list of row-sets in the same
        # order. Single-output recipes are unaffected.
        multi = isinstance(csv_path, (list, tuple))
        csv_paths = list(csv_path) if multi else [csv_path]
        ncols_list = list(ncols) if multi else [ncols]

        # Delete the outputs before running. Otherwise a deck that fails to
        # write one of them leaves the PREVIOUS run's file on disk and the
        # check reads stale numbers - a green result for a run that did not
        # happen. Same family as the marker file run_simulation.sh uses.
        for p in csv_paths:
            if os.path.isfile(p):
                os.remove(p)

        rc, output = run_ngspice(cir_path)
        if rc != 0:
            results.append((f"{rel} [electrical]", "FAIL", f"ngspice exited {rc}: {output.strip().splitlines()[-1] if output.strip() else '(no output)'}"))
            any_fail = True
            continue

        missing = [p for p in csv_paths
                   if not os.path.isfile(p) or os.path.getsize(p) == 0]
        if missing:
            results.append((f"{rel} [electrical]", "FAIL", f"expected output file(s) missing/empty: {', '.join(missing)}"))
            any_fail = True
            continue

        try:
            sets = [read_wrdata(p, n) for p, n in zip(csv_paths, ncols_list)]
            ok, msg = check_fn(sets if multi else sets[0])
        except Exception as e:
            results.append((f"{rel} [electrical]", "FAIL", f"error parsing/checking results: {e}"))
            any_fail = True
            continue

        results.append((f"{rel} [electrical]", "PASS" if ok else "FAIL", msg))
        if not ok:
            any_fail = True

    # print report
    print()
    print(f"{'MODEL / CHECK':55s} {'STATUS':6s} DETAIL")
    print("-" * 110)
    for name, status, msg in results:
        print(f"{name:55s} {status:6s} {msg}")
    print("-" * 110)
    n_pass = sum(1 for _, s, _ in results if s == "PASS")
    n_fail = sum(1 for _, s, _ in results if s == "FAIL")
    n_skip = sum(1 for _, s, _ in results if s == "SKIP")
    print(f"TOTAL: {n_pass} PASS, {n_fail} FAIL, {n_skip} SKIP  (out of {len(results)} checks)")
    print()

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
