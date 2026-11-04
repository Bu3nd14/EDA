#!/bin/zsh
# L70: the generator of this folder on today's netlist must give L69b's deck of the same case (but the
# paths in the header and the includes); on each variant it must generate without a refusal.
#   /bin/zsh script/prova_gen.sh <caso> [opzioni in piu']
set -u
L=${0:A:h:h}
R=${L:h:h:h:h:h}
T=/Users/roberto/.claude/jobs/79aaa85d/tmp/prova_gen
caso=$1
shift
BASE=(--n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore --bat54 costruttore --sonde-piu)
rm -rf $T
mkdir -p $T/oggi $T/s1 $T/s2 $T/s1s2
/usr/bin/python3 $L/psu/genera_tb_psu.py --uscita $T/oggi --nome seq --caso $caso --giro 1 --angolo nom --timer sorgente $BASE "$@" > /dev/null
echo "oggi: rc $?"
for v in s1 s2 s1s2; do
    /usr/bin/python3 $L/psu/genera_tb_psu.py --net $L/varianti/psu_$v.net --uscita $T/$v --nome seq --caso $caso --giro 1 --angolo nom --timer sorgente $BASE --fusibile 1:1:0.1 "$@" > /dev/null
    echo "$v: rc $?"
done
/usr/bin/sed -e "s|$L|X|g" -e "s|${L:h}/L69b|X|g" $T/oggi/tb_psu_seq_${caso}_g1.cir > $T/a.cir
/usr/bin/sed -e "s|${L:h}/L69b|X|g" $L:h/L69b/seq/oggi/$caso/tb_psu_seq_${caso}_g1.cir > $T/b.cir
if /usr/bin/cmp -s $T/a.cir $T/b.cir; then echo "oggi = L69b"; else echo "oggi DIVERSO da L69b"; /usr/bin/diff $T/a.cir $T/b.cir | head -8; fi
