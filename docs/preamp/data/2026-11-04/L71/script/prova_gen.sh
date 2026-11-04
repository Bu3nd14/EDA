#!/bin/zsh
# L71: the copied generator gives L69b's decks on the existing cases (the paths aside), and writes
# one deck of each new family. Out in $L/prova_gen/ (deleted at the start).
#   /bin/zsh script/prova_gen.sh
set -eu
L=${0:A:h:h}
B=$L:h/L69b
O=$L/prova_gen
rm -rf $O
mkdir -p $O
BASE=(--n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore --bat54 costruttore --sonde-piu)
for spec in "spegnimento_l oggi" "accensione oggi_m10:0.9" "inserimento oggi" "rilascio oggi"; do
    caso=${spec%% *}
    et=${spec##* }
    rete=()
    case $et in *:*) rete=(--rete ${et##*:}); et=${et%%:*} ;; esac
    mkdir -p $O/$et/$caso
    /usr/bin/python3 $L/psu/genera_tb_psu.py --uscita $O/$et/$caso --nome seq --caso $caso --giro 1 \
        --angolo nom --timer sorgente $BASE $rete > /dev/null
    a=$B/seq/$et/$caso/tb_psu_seq_${caso}_g1.cir
    b=$O/$et/$caso/tb_psu_seq_${caso}_g1.cir
    n=$(/usr/bin/diff <(/usr/bin/sed -e 's#/Users/roberto/EDA/.claude/worktrees/[^/]*##g' -e 's#data/2026-11-04/L[0-9a-z]*/#X/#g' $a) \
                      <(/usr/bin/sed -e 's#/Users/roberto/EDA/.claude/worktrees/[^/]*##g' -e 's#data/2026-11-04/L[0-9a-z]*/#X/#g' $b) | /usr/bin/grep -c '^[<>]' || true)
    echo "$et/$caso: righe diverse da L69b (percorsi a parte): $n"
done
for caso in acc_spento_1209 spl_riacceso_120 ins_ritorno_30 ril_ritorno_12 spl_sw3_15; do
    mkdir -p $O/nuovi/$caso
    /usr/bin/python3 $L/psu/genera_tb_psu.py --uscita $O/nuovi/$caso --nome seq --caso $caso --giro 1 \
        --angolo nom --timer sorgente $BASE > /dev/null
    echo "$caso:"
    /usr/bin/grep -E '^VG(FRONT|SW3) |^\.tran|tran ' $O/nuovi/$caso/tb_psu_seq_${caso}_g1.cir | /usr/bin/cut -c1-200
done
