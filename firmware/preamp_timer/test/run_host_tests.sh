#!/bin/zsh
# run_host_tests.sh - the timer firmware's host tests (L41b2, ADR-049).
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
    $CC "${CFLAGS[@]}" "${extra[@]}" -o "$OUT/test_legge$1" \
        "$T/test_legge.c" "$T/mondo.c" "$SRC/timer_core.c" -lm || return 1
}

rc=0
echo "== firmware/preamp_timer: test sull'host =="
build "" "" || { echo "[FAIL] la compilazione"; exit 1; }
if [ -n "$csv_dir" ]; then
    mkdir -p "$csv_dir"
    "$OUT/test_sequenze" --csv "$csv_dir"
else
    "$OUT/test_sequenze"
fi
r1=$?
"$OUT/test_legge" "$ROOT"
r2=$?
[ $r1 -ne 0 ] && rc=1
[ $r2 -ne 0 ] && rc=1

if [ -n "$falsi_out" ]; then
    # n -> the test that must fail with it (written before the runs)
    typeset -A attesi
    attesi=(1 accensione 2 rilascio 3 inserzione 4 inserzione 5 buco_classe1
            6 buco_classe1 7 debounce 8 inversione 9 spegnimento 10 buco_classe2
            11 tabella 12 tabella 13 cal_l41b1 14 accensione 15 guasto
            16 debounce 17 inserzione 18 accensione 19 bilancio 20 accensione)
    typeset -A cosa
    cosa=(1 "VRELAY_EN -> MUTE_REQ 5 ms (ADR-027: 13 ms)"
          2 "d si muove col rele' ancora aperto"
          3 "MUTE_REQ 0,1 s dopo d = 1 invece di 0,5"
          4 "PERMIT_REQ insieme a MUTE_REQ, senza Delta"
          5 "buco di rete: PERMIT_REQ resta su"
          6 "MUTE_G_IN ignorato: solo ADC_MD"
          7 "debounce di 2 ms invece di 20"
          8 "inserzione non reversibile"
          9 "spegnimento: rete staccata senza i 50 ms"
          10 "buco di classe 2 trattato come classe 1"
          11 "nessuna compensazione di Vt"
          12 "la cima a 20 mA (NC-038)"
          13 "correzione della calibrazione col segno sbagliato"
          14 "nessuna calibrazione all'accensione"
          15 "nessuna ritenuta dopo il guasto"
          16 "SW3 letto al contrario: un filo rotto suona"
          17 "Td = 3 s invece di 6"
          18 "nessun limite di 2 s sui rail"
          19 "lo zero dell'ADC non sottratto"
          20 "VRELAY_EN subito dopo il fit, la cima corretta non assestata")
    : > "$falsi_out"
    echo "# L41b2: i test sull'host contro i falsi di timer_core.c (FALSO_n)" >> "$falsi_out"
    echo "# ogni falso deve far FALLIRE il test indicato; gli altri possono passare" >> "$falsi_out"
    nf=0
    for n in {1..20}; do
        build "_f$n" "-DFALSO=$n" || { echo "falso $n: non compila" >> "$falsi_out"; rc=1; continue; }
        o1=$("$OUT/test_sequenze_f$n" 2>&1)
        o2=$("$OUT/test_legge_f$n" "$ROOT" 2>&1)
        t=${attesi[$n]}
        falliti=$(printf '%s\n%s\n' "$o1" "$o2" | grep '^FALLISCE ' | sed 's/^FALLISCE //' | tr '\n' ' ')
        if printf '%s\n%s\n' "$o1" "$o2" | grep -qx "FALLISCE $t"; then
            echo "falso $n (${cosa[$n]}): FALLISCE $t come deve  [falliti: $falliti]" >> "$falsi_out"
            nf=$((nf + 1))
        else
            echo "falso $n (${cosa[$n]}): $t NON fallisce  [falliti: ${falliti:-nessuno}]" >> "$falsi_out"
            rc=1
        fi
    done
    echo "== falsi: $nf su 20 fanno fallire il loro test" | tee -a "$falsi_out"
fi

[ $rc -eq 0 ] && echo "[PASS] test sull'host del temporizzatore" || echo "[FAIL] test sull'host del temporizzatore"
exit $rc
