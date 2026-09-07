#!/bin/zsh
# setup.sh - one-shot environment setup for the EDA repo.
#
# Idempotent: safe to run any number of times. Each step checks
# whether its target already exists/is satisfied before doing
# anything, so a second run should be a fast no-op that only prints
# "already present" lines.
#
# Two-interpreter split (important, do not "simplify" away):
#   - SKIDL_PY  : the repo's own venv python (env/venv). Runs skidl,
#                 numpy, the circuit/testbench/report-generation code.
#   - KICAD_PY  : KiCad's bundled python3.9 framework interpreter.
#                 The ONLY python that can `import pcbnew` /
#                 kinet2pcb, because those bind against KiCad's own
#                 compiled swig module. Installing kinet2pcb into any
#                 other python3 is a no-op that silently can't import
#                 pcbnew later.
#
# Usage:
#   /bin/zsh /Users/roberto/EDA/scripts/setup.sh

set -u

ROOT=/Users/roberto/EDA
VENV_DIR="$ROOT/env/venv"
SKIDL_PY="$VENV_DIR/bin/python3"
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
TOOLS_DIR="$ROOT/scripts/tools"
FREEROUTING_JAR="$TOOLS_DIR/freerouting.jar"

# Prefer an explicit native-arm64 Homebrew python3.x for `venv` creation
# over the bare `python3` on PATH, which can resolve to Apple's
# universal /usr/bin/python3 stub or whatever shell rc last put first.
# Pin to whichever Homebrew python3.1x is actually installed.
BASE_PYTHON=$(ls /opt/homebrew/bin/python3.1[0-9] 2>/dev/null | sort -V | tail -1)
if [ -z "$BASE_PYTHON" ]; then
    BASE_PYTHON="python3"
fi

setup_status=0

echo "== setup.sh starting =="

# --- 0. repo directory scaffolding (idempotent: mkdir -p) ---
echo "-- 0. directory scaffolding --"
for d in circuits schematics spice models vendor testbenches pcb scripts \
         scripts/tools tests results fabrication docs smoke; do
    mkdir -p "$ROOT/$d"
done
echo "   directories present under $ROOT"

# --- 1. python venv for SKiDL / numpy / repo tooling ---
echo "-- 1. venv ($VENV_DIR) --"
if [ -x "$SKIDL_PY" ]; then
    echo "   venv already exists: $SKIDL_PY"
else
    echo "   creating venv with $BASE_PYTHON..."
    "$BASE_PYTHON" -m venv "$VENV_DIR" || { echo "   ERROR: venv creation failed" >&2; setup_status=1; }
fi

if [ -x "$SKIDL_PY" ]; then
    if "$SKIDL_PY" -m pip show skidl >/dev/null 2>&1; then
        ver=$("$SKIDL_PY" -m pip show skidl 2>/dev/null | awk '/^Version:/{print $2}')
        echo "   skidl already installed (version $ver)"
    else
        echo "   installing skidl + numpy into venv..."
        "$SKIDL_PY" -m pip install --quiet --upgrade pip
        "$SKIDL_PY" -m pip install --quiet skidl numpy || { echo "   ERROR: pip install skidl failed" >&2; setup_status=1; }
    fi
else
    echo "   SKIP: no venv interpreter at $SKIDL_PY" >&2
    setup_status=1
fi

# --- 2. kinet2pcb into KiCad's bundled python3.9 (netlist -> pcb bridge) ---
echo "-- 2. kinet2pcb (into KiCad bundled python3.9) --"
if [ -x "$KICAD_PY" ]; then
    if "$KICAD_PY" -m pip show kinet2pcb >/dev/null 2>&1; then
        ver=$("$KICAD_PY" -m pip show kinet2pcb 2>/dev/null | awk '/^Version:/{print $2}')
        echo "   kinet2pcb already installed (version $ver) in $KICAD_PY"
    else
        echo "   installing kinet2pcb into KiCad's python3.9..."
        "$KICAD_PY" -m pip install --user --quiet kinet2pcb || { echo "   ERROR: kinet2pcb install failed" >&2; setup_status=1; }
    fi
else
    echo "   ERROR: KiCad bundled python3.9 not found at $KICAD_PY" >&2
    setup_status=1
fi

# --- 3. freerouting.jar (autorouter, fetched once, cached under scripts/tools) ---
echo "-- 3. freerouting.jar --"
mkdir -p "$TOOLS_DIR"
if [ -s "$FREEROUTING_JAR" ]; then
    sz=$(stat -f%z "$FREEROUTING_JAR" 2>/dev/null || stat -c%s "$FREEROUTING_JAR")
    echo "   already present: $FREEROUTING_JAR ($sz bytes)"
else
    echo "   fetching latest freerouting release jar from GitHub..."
    latest_url=$(curl -s --max-time 15 https://api.github.com/repos/freerouting/freerouting/releases/latest \
        | python3 -c "import json,sys; d=json.load(sys.stdin); print(next(a['browser_download_url'] for a in d['assets'] if a['name'].endswith('.jar')))" 2>/dev/null)
    if [ -n "$latest_url" ]; then
        curl -L --max-time 120 -o "$FREEROUTING_JAR.part" "$latest_url" \
            && mv "$FREEROUTING_JAR.part" "$FREEROUTING_JAR" \
            && echo "   downloaded: $FREEROUTING_JAR" \
            || { echo "   ERROR: freerouting download failed" >&2; rm -f "$FREEROUTING_JAR.part"; setup_status=1; }
    else
        echo "   ERROR: could not resolve freerouting release jar URL (no network / API rate limit?)" >&2
        setup_status=1
    fi
fi

echo "== setup.sh done (exit $setup_status) =="
exit $setup_status
