#!/bin/zsh
# run_host_tests.sh - the timer firmware's host tests (L41b2, ADR-049; the mute
# with the relays alone since L47c2a, ADR-062).
#
#   /bin/zsh firmware/preamp_timer/test/run_host_tests.sh               the tests
#   /bin/zsh firmware/preamp_timer/test/run_host_tests.sh --falsi <out>  the tests, then
#        every fake build (FALSO_n in timer_core.c) must make ITS test fail; the
#        verdicts go to <out>
#   /bin/zsh firmware/preamp_timer/test/run_host_tests.sh --csv <dir>    also write each
#        sequence's outputs to <dir>/<test>.csv (the bridge to SPICE)
#
# Compiled with /usr/bin/clang (Apple clang), -std=c11 -Wall -Wextra -Werror
# -pedantic, into results/run_tests/firmware (gitignored). Exit 0 only if every
# check passes and, with --falsi, every fake fails where it must.
#
# L47c2a: test_legge (the LDR law, its calibration, the ADC budget of the
# string currents) is gone with the law (ADR-062), and with it fakes 2, 3, 8,
# 11, 12, 13, 14, 17, 19, 20, 21. Fakes 22-30 test the new sequences and the
# free pins; the ten that survive keep their numbers, so that L41b2's reports
# still read right. 19 fakes in all.
set -u

ROOT=${0:A:h:h:h:h}
T=${0:A:h}
SRC=${0:A:h:h}/src
OUT="$ROOT/results/run_tests/firmware"
mkdir -p "$OUT"
CC=/usr/bin/clang
CFLAGS=(-std=c11 -Wall -Wextra -Werror -pedantic -O1)

falsi_out=""
csv_dir=""
while [ $# -gt 0 ]; do
    case "$1" in
        --falsi) falsi_out="$2"; shift 2 ;;
        --csv) csv_dir="$2"; shift 2 ;;
        *) echo "argomento sconosciuto: $1" >&2; exit 2 ;;
    esac
done

build() {
    # $1 = suffix, $2 = extra flag (or empty)
    local extra=()
    [ -n "$2" ] && extra=("$2")
    $CC "${CFLAGS[@]}" "${extra[@]}" -o "$OUT/test_sequenze$1" \
        "$T/test_sequenze.c" "$T/mondo.c" "$SRC/timer_core.c" -lm || return 1
}

rc=0
echo "== firmware/preamp_timer: test sull'host =="
build "" "" || { echo "[FAIL] la compilazione"; exit 1; }
if [ -n "$csv_dir" ]; then
    mkdir -p "$csv_dir"
    "$OUT/test_sequenze" --root "$ROOT" --csv "$csv_dir"
else
    "$OUT/test_sequenze" --root "$ROOT"
fi
[ $? -ne 0 ] && rc=1

if [ -n "$falsi_out" ]; then
    # n -> the test that must fail with it (written before the runs)
    typeset -A attesi
    attesi=(1 accensione 4 inserzione 5 buco_classe1 6 buco_classe1 7 debounce
            9 spegnimento 10 buco_classe2 15 guasto 16 debounce 18 accensione
            22 inserzione 23 rilascio 24 rilascio 25 pin_liberi 26 pin_liberi
            27 pin_liberi 28 accensione 29 spegnimento 30 spegnimento)
    typeset -A cosa
    cosa=(1 "VRELAY_EN -> MUTE_REQ 5 ms (ADR-027: 13 ms)"
          4 "PERMIT_REQ insieme a MUTE_REQ, senza Delta"
          5 "buco di rete: PERMIT_REQ resta su"
          6 "MUTE_G_IN ignorato: solo ADC_MD"
          7 "debounce di 2 ms invece di 20"
          9 "spegnimento: rete staccata senza gli 80 ms"
          10 "buco di classe 2 trattato come classe 1"
          15 "nessuna ritenuta dopo il guasto"
          16 "SW3 letto al contrario: un filo rotto suona"
          18 "nessun limite di 2 s sui rail"
          22 "MUTE_REQ giu' 0,5 s dopo il tasto: la ritenuta della sfumatura rimasta"
          23 "rilascio: il rifiuto dell'hardware non guardato dopo i 10 ms"
          24 "rilascio: PERMIT_REQ 20 ms dopo MUTE_REQ"
          25 "PB4 dimenticato fra i pin liberi"
          26 "PC2 (MUTE_G_IN) nella lista al posto di PC3"
          27 "pin liberi col buffer d'ingresso acceso (ISC 0x0)"
          28 "VRELAY_EN al primo campione buono dei rail, senza i 100 ms"
          29 "spegnimento: MAINS_REQ 80 ms dopo VRELAY_EN"
          30 "spegnimento da MUSICA senza l'inserzione: niente Delta")
    : > "$falsi_out"
    echo "# L47c2a: i test sull'host contro i falsi di timer_core.c (FALSO_n)" >> "$falsi_out"
    echo "# ogni falso deve far FALLIRE il test indicato; gli altri possono passare" >> "$falsi_out"
    nf=0
    ntot=0
    for n in ${(onk)attesi}; do
        ntot=$((ntot + 1))
        build "_f$n" "-DFALSO=$n" || { echo "falso $n: non compila" >> "$falsi_out"; rc=1; continue; }
        o1=$("$OUT/test_sequenze_f$n" --root "$ROOT" 2>&1)
        t=${attesi[$n]}
        falliti=$(printf '%s\n' "$o1" | grep '^FALLISCE ' | sed 's/^FALLISCE //' | tr '\n' ' ')
        if printf '%s\n' "$o1" | grep -qx "FALLISCE $t"; then
            echo "falso $n (${cosa[$n]}): FALLISCE $t come deve  [falliti: $falliti]" >> "$falsi_out"
            nf=$((nf + 1))
        else
            echo "falso $n (${cosa[$n]}): $t NON fallisce  [falliti: ${falliti:-nessuno}]" >> "$falsi_out"
            rc=1
        fi
    done
    echo "== falsi: $nf su $ntot fanno fallire il loro test" | tee -a "$falsi_out"
fi

[ $rc -eq 0 ] && echo "[PASS] test sull'host del temporizzatore" || echo "[FAIL] test sull'host del temporizzatore"
exit $rc
