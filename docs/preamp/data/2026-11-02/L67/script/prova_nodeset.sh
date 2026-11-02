#!/bin/zsh
# L67: prova dei nodeset su due deck (oggi e l56, 1 kHz, 0,2 V), in run/prova_nodeset/
L=${0:A:h:h}
R=${L:h:h:h:h:h}
for b in oggi l56; do
  /bin/zsh $R/scripts/run_simulation.sh $L/catena/deck/$b/catena_1k_lo.cir $L/run/prova_nodeset/$b > /dev/null 2>&1 &
done
wait
for b in oggi l56; do
  print -r -- "-- $b: $(grep -c 'source stepping failed' $L/run/prova_nodeset/$b/catena_1k_lo.log) op falliti, $(grep -c 'L53_CATENA' $L/run/prova_nodeset/$b/catena_1k_lo.log) casi"
  grep -h -A6 "Fourier analysis for v(bout)" $L/run/prova_nodeset/$b/catena_1k_lo.log | grep "^ *1 " | head -3
done
