#!/bin/zsh
# corri_an.sh - L54a: one sequence case with an analog timer (genera_tb_psu.py --timer
# comparatori | diretto). One pass: there is no firmware core to agree with, the circuit is the
# timer. The guards and the ONE retry with the other method are corri_seq.sh's (L56).
#
#   /bin/zsh corri_an.sh <caso> <etichetta> <timer> [opzioni di genera_tb_psu.py...]
#
# The results go to seq/<etichetta>/<caso>; ok.txt is written only when the log is clean.
set -u
caso=$1
etich=$2
timer=$3
shift 3
opz=("$@")
D=${0:A:h}
OUT=$D:h/seq/$etich/$caso
rm -rf "$OUT"
mkdir -p "$OUT"
ang=nom
case $caso in *_min) ang=min ;; esac
cd "$OUT" || exit 1
/usr/bin/python3 "$D/genera_tb_psu.py" --uscita "$OUT" --nome seq --caso "$caso" --giro 1 \
    --angolo $ang --timer "$timer" "${opz[@]}" > /dev/null || exit 1
cir=tb_psu_seq_${caso}_g1.cir
log=tb_psu_seq_${caso}_g1.log
/usr/bin/perl -e 'alarm shift; exec @ARGV' 300 /opt/homebrew/bin/ngspice -b "$cir" -o "$log" > /dev/null 2>&1
rc_ng=$?
if [ $rc_ng -eq 142 ] || { grep -qi 'timestep too small' "$log" && \
   ! grep -qiE 'singular|no such|non-increasing|transient op' "$log"; }; then
    da=$(grep -oE 'method=[a-z]+ gmin=[0-9e.-]+' "$cir")
    case $da in
        "method=gear gmin=1e-10") a="method=trap gmin=1e-8" ;;
        *) a="method=gear gmin=1e-10" ;;
    esac
    print -r -- "$da -> $a (ngspice rc $rc_ng; 142 = tetto di 300 s)" > ripiego.txt
    mv "$log" "${log:r}_primo.log"
    /usr/bin/sed -i '' "s/$da/$a/" "$cir"
    /usr/bin/perl -e 'alarm shift; exec @ARGV' 600 /opt/homebrew/bin/ngspice -b "$cir" -o "$log" > /dev/null 2>&1
    if [ $? -eq 142 ]; then
        echo "$caso: anche il ripiego supera il tetto (600 s) - rifiutato"
        exit 1
    fi
    echo "$caso: ripiego $da -> $a"
fi
if grep -qiE 'error|singular|no such|non-increasing|transient op|timestep too small' "$log"; then
    echo "$caso: il log ha un errore - rifiutato"
    grep -iE 'error|singular|no such|non-increasing|transient op|timestep too small' "$log" | head -3
    exit 1
fi
echo "$timer ${opz[*]}" > ok.txt
echo "$caso ($timer ${opz[*]}): fatto"
