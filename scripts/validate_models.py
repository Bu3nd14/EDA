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

        rc, output = run_ngspice(cir_path)
        if rc != 0:
            results.append((f"{rel} [electrical]", "FAIL", f"ngspice exited {rc}: {output.strip().splitlines()[-1] if output.strip() else '(no output)'}"))
            any_fail = True
            continue

        if not os.path.isfile(csv_path) or os.path.getsize(csv_path) == 0:
            results.append((f"{rel} [electrical]", "FAIL", f"expected output file missing/empty: {csv_path}"))
            any_fail = True
            continue

        try:
            rows = read_wrdata(csv_path, ncols)
            ok, msg = check_fn(rows)
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
