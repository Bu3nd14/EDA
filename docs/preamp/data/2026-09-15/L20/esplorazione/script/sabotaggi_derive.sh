#!/bin/zsh
# sabotaggi_derive.sh - L20: make scripts/derive_jfet_variant.py fall, on copies.
#
# Each case builds a scratch tree that mirrors the two paths the script reads
# (spice/preamp/gain_block_flat.inc and spice/preamp/derived/...), breaks one
# thing, and runs the script. Expected rc and expected message are printed next
# to what came out: a control that falls for another reason does not count.
#
# Usage: /bin/zsh sabotaggi_derive.sh <repo> <scratch-dir>

set -u
REPO="$1"
S="$2"
PY=/usr/bin/python3
DER="$REPO/scripts/derive_jfet_variant.py"
SRC="$REPO/spice/preamp/gain_block_flat.inc"
OUT="$REPO/spice/preamp/derived/gain_block_flat_lsk489a.inc"

case_tree() {
    rm -rf "$S/$1"
    mkdir -p "$S/$1/spice/preamp/derived"
    cp "$SRC" "$S/$1/spice/preamp/gain_block_flat.inc"
    cp "$OUT" "$S/$1/spice/preamp/derived/gain_block_flat_lsk489a.inc"
}

run() {   # name, expected rc, expected text, args...
    local name="$1" exp_rc="$2" exp_txt="$3"
    shift 3
    local out rc
    out=$("$PY" "$DER" "$@" 2>&1)
    rc=$?
    local verdict="AS EXPECTED"
    if [ "$rc" != "$exp_rc" ] || ! print -r -- "$out" | grep -q -- "$exp_txt"; then
        verdict="NOT AS EXPECTED"
    fi
    echo "--- $name: rc $rc (expected $exp_rc, text '$exp_txt') -> $verdict"
    print -r -- "$out" | sed 's/^/    /'
}

# 0. the intact tree passes
case_tree s0_intatto
run "s0 intact copy, --check" 0 "is the current derivation" "$S/s0_intatto" --check

# 1. the derived file edited by hand (a value in the copy, R136 1.50k -> 1.51k)
case_tree s1_derivato_ritoccato
sed -i '' 's/^R136 OUT FB 1.50k$/R136 OUT FB 1.51k/' "$S/s1_derivato_ritoccato/spice/preamp/derived/gain_block_flat_lsk489a.inc"
run "s1 derived file edited by hand, --check" 1 "STALE" "$S/s1_derivato_ritoccato" --check

# 2. the generated block changed and the derived file not regenerated
case_tree s2_sorgente_cambiata
sed -i '' 's/^C137 OUT FB 330p$/C137 OUT FB 220p/' "$S/s2_sorgente_cambiata/spice/preamp/gain_block_flat.inc"
run "s2 generated block changed, derived stale, --check" 1 "STALE" "$S/s2_sorgente_cambiata" --check

# 3. a source with ONE JFET line on LSK489X
case_tree s3_una_riga
sed -i '' 's/^JQ110B D2N G2 S2 LSK489X$/JQ110B D2N G2 S2 LSK489Y/' "$S/s3_una_riga/spice/preamp/gain_block_flat.inc"
run "s3 source with one LSK489X line" 2 "1 JFET lines on LSK489X" "$S/s3_una_riga" --out -

# 4. a source with THREE JFET lines on LSK489X
case_tree s4_tre_righe
echo "JQ110C D2N G2 S2 LSK489X" >> "$S/s4_tre_righe/spice/preamp/gain_block_flat.inc"
run "s4 source with three LSK489X lines" 2 "3 JFET lines on LSK489X" "$S/s4_tre_righe" --out -

# 5. LSK489X on a line that is not a JFET
case_tree s5_non_jfet
echo "Q999 NX NHI NVE LSK489X" >> "$S/s5_non_jfet/spice/preamp/gain_block_flat.inc"
run "s5 LSK489X on a BJT line" 2 "not a JFET" "$S/s5_non_jfet" --out -

# 6. the positive control: --model LSK489X gives the source back, header aside
case_tree s6_identita
"$PY" "$DER" "$S/s6_identita" --model LSK489X --out spice/preamp/derived/identita.inc > /dev/null
tail -n +6 "$S/s6_identita/spice/preamp/derived/identita.inc" | cmp - "$S/s6_identita/spice/preamp/gain_block_flat.inc"
echo "--- s6 --model LSK489X, header aside, identical to the source: cmp rc $? (expected 0)"
