#!/bin/zsh
# corri_seq.sh - one sequence case of L41b2, iterated to a fixed point
# (L47c2a: the firmware of the mute with the relays alone; no inversione; the
# ends of rilascio and spegnimento without the fade; the L41c cases kept for
# L47c2b).
# L47c2b2: copied from L47c2a's deck/; --angolo min passed again for the corner
# cases, *_min, as L41c's did (L47c2a's copy had dropped it, and the generator
# refuses a corner case without it).
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
# L45d2b2a: corri_seq.sh <caso> <etichetta> [opzioni di genera_tb_psu.py...]: the results go to
# seq/<etichetta>/<caso>, and the options (--ss, --cnr, --cap-audio, --bobine) reach every pass
# (L45d2b1: <caso> [max_giri]; max_giri is 8 here)
max=8
if [ "$caso" != "--solo-compila" ]; then
    etich=$2
    shift 2
    opz=("$@")
fi
D=${0:A:h}
ROOT=${0:A:h:h:h:h:h:h:h}
OUT=$D:h/seq/${etich:-x}/$caso
FW=$ROOT/firmware/preamp_timer
BIN=$ROOT/results/run_tests/firmware
mkdir -p "$BIN"
if [ "$caso" = "--solo-compila" ]; then
    /usr/bin/clang -std=c11 -Wall -Wextra -Werror -pedantic -O2 -o "$BIN/ponte" \
        "$FW/test/ponte.c" "$FW/test/mondo.c" "$FW/src/timer_core.c" -lm
    exit $?
fi
# a clean folder: a punto_fisso.txt or a core_g<n>.csv left by an earlier
# run would survive a failure of this one and be analysed as its result
rm -rf "$OUT"
mkdir -p "$OUT"
[ -x "$BIN/ponte" ] || { echo "manca $BIN/ponte: corri_seq.sh --solo-compila"; exit 1; }

typeset -A pre
pre=(accensione "" accensione_m10 "" rilascio muto spegnimento musica
     buco20 musica buco200 musica guasto musica
     spegnimento_l musica perdita musica perdita_min musica guasto_u501 musica
     guasto_u503 musica guasto_u503_min musica cf_nodelta musica corto_u503 musica)
typeset -A tf
# the deck's end (genera_tb_psu.py, CASI_SEQ: TE + tf)
tf=(accensione 4.5 accensione_m10 4.5 rilascio 2.5 spegnimento 2.4 buco20 3.3 buco200 3.6 guasto 3.0
    spegnimento_l 3.1 perdita 3.0 perdita_min 3.0 guasto_u501 3.0 guasto_u503 3.0
    guasto_u503_min 3.0 cf_nodelta 3.0 corto_u503 3.0)
# L45c1: the fault cases f_<ref>_<modo>_<evento> (modi.py) all start from MUSICA; the deck's
# end is the event's (spegn TE + 1.1 s, the others TE + 1.0 s)
case $caso in
    f_*_spegn) pre[$caso]=musica; tf[$caso]=3.1 ;;
    f_*_mus6) pre[$caso]=musica; tf[$caso]=8.0 ;;
    f_*) pre[$caso]=musica; tf[$caso]=3.0 ;;
esac
p=${pre[$caso]}
ang=nom
case $caso in *_min) ang=min ;; esac
cd "$OUT" || exit 1

# pass 0
if [ -z "$p" ]; then
    printf 't,mains_req,vrelay_en,mute_req,permit_req,stato\n0.000000,0,0,0,0,STANDBY\n' > core_g0.csv
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
        --uscite "$OUT/core_g$prev.csv" --giro $g --angolo $ang "${opz[@]}" > /dev/null || exit 1
    # L56: a ceiling of 150 s per pass (perl alarm; every sequence pass of L51b ran in ~12 s)
    /usr/bin/perl -e 'alarm shift; exec @ARGV' 150 /opt/homebrew/bin/ngspice -b "tb_psu_seq_${caso}_g$g.cir" -o "tb_psu_seq_${caso}_g$g.log" > /dev/null 2>&1
    rc_ng=$?
    # L56: ONE retry with the other integration method, for "Timestep too small" or the ceiling
    # ALONE. On L56's load guasto_u503_min fails pass 1 with gear (2.47 s, b.xu508b.bq, after a
    # long crawl) and pass 2 with trap + gmin 1e-8 (2.93 s, b.xu502.bi), each passing with the
    # other method (../sonda_u503/esiti_l56*.tsv); L51b's probe found the two methods give the
    # jack, the gain and V+ < 10.6 V at the same instants and the rails within 0.5 mV. The retry
    # is written to ripiego_g<g>.txt; any other error, or a second failure, is still refused.
    if [ $rc_ng -eq 142 ] || { grep -qi 'timestep too small' "tb_psu_seq_${caso}_g$g.log" && \
       ! grep -qiE 'singular|no such|non-increasing|transient op' "tb_psu_seq_${caso}_g$g.log"; }; then
        da=$(grep -oE 'method=[a-z]+ gmin=[0-9e.-]+' "tb_psu_seq_${caso}_g$g.cir")
        case $da in
            "method=gear gmin=1e-10") a="method=trap gmin=1e-8" ;;
            *) a="method=gear gmin=1e-10" ;;
        esac
        print -r -- "giro $g: $da -> $a (ngspice rc $rc_ng; 142 = tetto di 150 s; $(grep -i "timestep too small" "tb_psu_seq_${caso}_g$g.log" | head -1))" > "ripiego_g$g.txt"
        mv "tb_psu_seq_${caso}_g$g.log" "tb_psu_seq_${caso}_g${g}_primo.log"
        /usr/bin/sed -i '' "s/$da/$a/" "tb_psu_seq_${caso}_g$g.cir"
        /usr/bin/perl -e 'alarm shift; exec @ARGV' 300 /opt/homebrew/bin/ngspice -b "tb_psu_seq_${caso}_g$g.cir" -o "tb_psu_seq_${caso}_g$g.log" > /dev/null 2>&1
        if [ $? -eq 142 ]; then
            echo "$caso giro $g: anche il ripiego supera il tetto (300 s) - rifiutato"
            exit 1
        fi
        echo "$caso giro $g: ripiego $da -> $a"
    elif [ $rc_ng -ne 0 ] && ! grep -qiE 'error|singular|no such|non-increasing|transient op|timestep too small' "tb_psu_seq_${caso}_g$g.log"; then
        echo "$caso giro $g: ngspice rc $rc_ng senza un errore nel log - rifiutato"
        exit 1
    fi
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
