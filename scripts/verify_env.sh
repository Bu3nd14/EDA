#!/bin/zsh
# verify_env.sh - "is my environment sane" check.
#
# Verifies that ngspice, kicad-cli, the repo venv python, KiCad's
# bundled python3.9, java and the freerouting jar are all present,
# prints their exact versions, and confirms every native binary is
# arm64 (not running under Rosetta / x86_64-only).
#
# Exit code: 0 if everything required is present and arm64-capable,
# nonzero (count of failed checks) otherwise.
#
# Usage:
#   /bin/zsh /Users/roberto/EDA/scripts/verify_env.sh

set -u

NGSPICE=/opt/homebrew/bin/ngspice
KICAD_CLI=/Users/roberto/Applications/KiCad.app/Contents/MacOS/kicad-cli
SKIDL_PY=/Users/roberto/EDA/env/venv/bin/python3
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
JAVA=/opt/homebrew/opt/openjdk/bin/java
FREEROUTING_JAR=/Users/roberto/EDA/scripts/tools/freerouting.jar

fail=0

check_arch() {
    # $1 = path to binary. Prints PASS/FAIL and returns nonzero on fail.
    local bin_path="$1"
    local archs
    archs=$(file "$bin_path" 2>/dev/null)
    if echo "$archs" | grep -q "arm64"; then
        echo "   arch: OK (arm64 present) - $archs"
        return 0
    else
        echo "   arch: FAIL (no arm64 slice found) - $archs"
        return 1
    fi
}

echo "== verify_env.sh: EDA toolchain environment check =="
echo "host arch (uname -m): $(uname -m)"
echo

echo "-- ngspice --"
if [ -x "$NGSPICE" ]; then
    ver=$("$NGSPICE" -v 2>&1 | head -2 | tail -1)
    echo "   path:    $NGSPICE"
    echo "   version: $ver"
    check_arch "$NGSPICE" || fail=$((fail + 1))
else
    echo "   MISSING: $NGSPICE not found or not executable" >&2
    fail=$((fail + 1))
fi
echo

echo "-- kicad-cli --"
if [ -x "$KICAD_CLI" ]; then
    ver=$("$KICAD_CLI" version 2>&1)
    echo "   path:    $KICAD_CLI"
    echo "   version: $ver"
    check_arch "$KICAD_CLI" || fail=$((fail + 1))
else
    echo "   MISSING: $KICAD_CLI not found or not executable" >&2
    fail=$((fail + 1))
fi
echo

echo "-- python3 (repo venv, for SKiDL/numpy) --"
if [ -x "$SKIDL_PY" ]; then
    ver=$("$SKIDL_PY" --version 2>&1)
    skidl_ver=$("$SKIDL_PY" -m pip show skidl 2>/dev/null | awk '/^Version:/{print $2}')
    echo "   path:    $SKIDL_PY"
    echo "   version: $ver (skidl ${skidl_ver:-NOT INSTALLED})"
    if [ -z "$skidl_ver" ]; then
        echo "   MISSING: skidl not installed in venv (run scripts/setup.sh)" >&2
        fail=$((fail + 1))
    fi
    check_arch "$SKIDL_PY" || fail=$((fail + 1))
else
    echo "   MISSING: $SKIDL_PY not found (run scripts/setup.sh)" >&2
    fail=$((fail + 1))
fi
echo

echo "-- python3.9 (KiCad bundled, for pcbnew/kinet2pcb) --"
if [ -x "$KICAD_PY" ]; then
    ver=$("$KICAD_PY" --version 2>&1)
    k2p_ver=$("$KICAD_PY" -m pip show kinet2pcb 2>/dev/null | awk '/^Version:/{print $2}')
    echo "   path:    $KICAD_PY"
    echo "   version: $ver (kinet2pcb ${k2p_ver:-NOT INSTALLED})"
    if [ -z "$k2p_ver" ]; then
        echo "   MISSING: kinet2pcb not installed in KiCad python (run scripts/setup.sh)" >&2
        fail=$((fail + 1))
    fi
    check_arch "$KICAD_PY" || fail=$((fail + 1))
else
    echo "   MISSING: $KICAD_PY not found" >&2
    fail=$((fail + 1))
fi
echo

echo "-- java (for freerouting) --"
if [ -x "$JAVA" ]; then
    ver=$("$JAVA" -version 2>&1 | head -1)
    echo "   path:    $JAVA"
    echo "   version: $ver"
    check_arch "$JAVA" || fail=$((fail + 1))
else
    echo "   MISSING: $JAVA not found or not executable" >&2
    fail=$((fail + 1))
fi
echo

echo "-- freerouting.jar --"
if [ -s "$FREEROUTING_JAR" ]; then
    sz=$(stat -f%z "$FREEROUTING_JAR" 2>/dev/null || stat -c%s "$FREEROUTING_JAR")
    main_class=$(unzip -p "$FREEROUTING_JAR" META-INF/MANIFEST.MF 2>/dev/null | awk -F': ' '/^Main-Class/{print $2}' | tr -d '\r')
    echo "   path:    $FREEROUTING_JAR ($sz bytes)"
    echo "   main-class: ${main_class:-unknown}"
else
    echo "   MISSING: $FREEROUTING_JAR not found (run scripts/setup.sh)" >&2
    fail=$((fail + 1))
fi
echo

if [ "$fail" -eq 0 ]; then
    echo "== RESULT: all required tools present and arm64-verified (0 failures) =="
else
    echo "== RESULT: $fail check(s) FAILED - environment is not sane ==" >&2
fi
exit $fail
