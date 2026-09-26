#!/bin/zsh
# corri_seq.sh - one sequence case of L41b2, iterated to a fixed point.
#
#   /bin/zsh corri_seq.sh <caso> [max_giri]
#
# Pass g: genera_tb_psu.py --nome seq builds the deck from the core's outputs
# of pass g-1 (core_g<g-1>.csv), ngspice runs it and writes what the micro's
# pins see (tb_psu_seq_<caso>_g<g>_out.txt, gitignored), ponte.c runs the
# core on that and writes core_g<g>.csv. When core_g<g>.csv equals
# core_g<g-1>.csv - the same rows, the same values, every time within 0.2 ms,
# two samples of the 100 us grid (confronta.py) - and no pin had to be
# rebuilt, the circuit and the firmware agree: the last deck is the case.
# Pass 0 is the micro held in its preamble state (sano.py + ponte.c), or all
# outputs at 0 for a power-up from standby.
#
# Guards (limitations #33, L41b1's README): a log with Error, singular,
# "no such", non-increasing, "Transient op" or "Timestep too small" refuses
# the pass.
set -u
caso=$1
max=${2:-8}
D=${0:A:h}
ROOT=${0:A:h:h:h:h:h:h:h}
OUT=$D:h/seq/$caso
FW=$ROOT/firmware/preamp_timer
BIN=$ROOT/results/run_tests/firmware
mkdir -p "$BIN"
if [ "$caso" = "--solo-compila" ]; then
    /usr/bin/clang -std=c11 -Wall -Wextra -Werror -pedantic -O2 -o "$BIN/ponte" \
        "$FW/test/ponte.c" "$FW/test/mondo.c" "$FW/src/timer_core.c" -lm
    exit $?
fi
mkdir -p "$OUT"
[ -x "$BIN/ponte" ] || { echo "manca $BIN/ponte: corri_seq.sh --solo-compila"; exit 1; }

typeset -A pre
pre=(accensione "" rilascio muto inversione musica spegnimento musica
     buco20 musica buco200 musica guasto musica)
typeset -A tf
tf=(accensione 3.3 rilascio 9.6 inversione 8.3 spegnimento 8.65 buco20 3.3 buco200 3.6 guasto 3.0)
p=${pre[$caso]}
cd "$OUT" || exit 1

# pass 0
if [ -z "$p" ]; then
    printf 't,mains_req,vrelay_en,mute_req,permit_req,dac_on,code_s,code_p,stato,d\n0.000000,0,0,0,0,0,0,0,STANDBY,1.000000\n' > core_g0.csv
else
    if [ "$p" = "muto" ]; then
        /usr/bin/python3 "$D/sano.py" sano_out.txt ${tf[$caso]} --muto
    else
        /usr/bin/python3 "$D/sano.py" sano_out.txt ${tf[$caso]}
    fi
    "$BIN/ponte" sano_out.txt core_g0.csv --da 2 --preambolo "$p" || exit 1
fi

g=1
while [ $g -le $max ]; do
    prev=$((g - 1))
    /usr/bin/python3 "$D/genera_tb_psu.py" --uscita "$OUT" --nome seq --caso "$caso" \
        --uscite "$OUT/core_g$prev.csv" --giro $g > /dev/null || exit 1
    /opt/homebrew/bin/ngspice -b "tb_psu_seq_${caso}_g$g.cir" -o "tb_psu_seq_${caso}_g$g.log" > /dev/null 2>&1
    if grep -qiE 'error|singular|no such|non-increasing|transient op|timestep too small' "tb_psu_seq_${caso}_g$g.log"; then
        echo "$caso giro $g: il log ha un errore - rifiutato"
        grep -iE 'error|singular|no such|non-increasing|transient op|timestep too small' "tb_psu_seq_${caso}_g$g.log" | head -3
        exit 1
    fi
    if [ -z "$p" ]; then
        "$BIN/ponte" "tb_psu_seq_${caso}_g${g}_out.txt" "core_g$g.csv" --da 2 \
            --pilota "core_g$prev.csv" > "ponte_g$g.txt" || exit 1
    else
        "$BIN/ponte" "tb_psu_seq_${caso}_g${g}_out.txt" "core_g$g.csv" --da 2 --preambolo "$p" \
            --pilota "core_g$prev.csv" > "ponte_g$g.txt" || exit 1
    fi
    cat "ponte_g$g.txt"
    if /usr/bin/python3 "$D/confronta.py" "core_g$g.csv" "core_g$prev.csv" > "confronto_g$g.txt"; then
        if ! grep -q "sostituzioni di MUTE_G_IN 0$" "ponte_g$g.txt"; then
            echo "$caso: uscite uguali ma con sostituzioni di MUTE_G_IN: non e' un punto fisso"
            exit 1
        fi
        echo "$caso: punto fisso al giro $g (core_g$g.csv = core_g$prev.csv entro 0,2 ms, 0 sostituzioni)"
        echo "$g" > punto_fisso.txt
        exit 0
    fi
    echo "$caso giro $g: le uscite del core sono cambiate, si rifa'"
    g=$((g + 1))
done
echo "$caso: NESSUN punto fisso in $max giri"
exit 1
