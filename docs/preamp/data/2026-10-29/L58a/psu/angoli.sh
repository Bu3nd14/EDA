#!/bin/zsh
# angoli.sh <cartella mc> <an.csv> <prefisso uscita> - L54b3b: the worst corners of each criterion
# from the Monte Carlo (regressione.py), written as <cartella mc>/toll_<prefisso><nome>.json, and the
# fits in <cartella mc>/regressione.txt.
# [<intervalli.json>]: another set of ranges (a temperature, an X7R hypothesis): the signs are the
# fit's, the values that file's.
set -u
D=${0:A:h}
M=$1
A=$2
P=$3
I=${4:-$M/intervalli.json}
rm -f $M/regressione_$P.txt
for spec in buco20:dmus_ms:min:dmus spegnimento_l:d_perm_ms:min:dperm_sp guasto:d_perm_ms:min:dperm_gu \
            spegnimento_l:k_perm_ms:min:kperm_sp guasto:k_perm_ms:min:kperm_gu \
            accensione:arm_pg_ms:min:arm_acc fredda:arm_pg_ms:min:arm_fr fredda:bn_max:max:bn_fr \
            accensione:t_arm_ms:max:arm_tardi perdita:t_jack_ms:max:jack_tardi; do
    p=(${(s/:/)spec})
    /usr/bin/python3 -I $D/regressione.py $M/campioni.csv $I $A $p[1] $p[2] $p[3] \
        $M/toll_$P$p[4].json $M/regressione_$P.txt > /dev/null || echo "$spec: errore"
done
echo "fatto: $M/regressione_$P.txt"
