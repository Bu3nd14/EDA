#!/bin/zsh
# corri_opzioni.sh - L45d2b2a: the power-up with the soft-start, for today's NR capacitors and the
# options put to the user (--cnr overrides the netlist; the source is not touched), at the nominal
# mains and at -10 %. Each run is corri_seq.sh to its fixed point; then misura_ss.py on all.
#   /bin/zsh corri_opzioni.sh
D=${0:A:h}
S=$D:h/seq
for caso in accensione accensione_m10; do
    /bin/zsh $D/corri_seq.sh $caso oggi > $S/oggi_$caso.txt 2>&1 &
    /bin/zsh $D/corri_seq.sh $caso n1u --cnr U502=1u > $S/n1u_$caso.txt 2>&1 &
    /bin/zsh $D/corri_seq.sh $caso p4u7_n470n --cnr U501=4.7u,U502=470n > $S/p4u7_n470n_$caso.txt 2>&1 &
    /bin/zsh $D/corri_seq.sh $caso p1u_n1u --cnr U501=1u,U502=1u > $S/p1u_n1u_$caso.txt 2>&1 &
done
wait
/usr/bin/python3 -I $D/misura_ss.py $D:h/accensione.csv $S/oggi/accensione $S/oggi/accensione_m10 \
    $S/n1u/accensione $S/n1u/accensione_m10 $S/p4u7_n470n/accensione $S/p4u7_n470n/accensione_m10 \
    $S/p1u_n1u/accensione $S/p1u_n1u/accensione_m10
print -r -- "fine opzioni"
