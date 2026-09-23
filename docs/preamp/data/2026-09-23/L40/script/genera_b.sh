#!/bin/zsh
# genera_b.sh : strada (b), guadagno minimo sopra 0 dB. Una gamba fissa
# RG0L40 da FB a massa su OGNI istanza oggi a guadagno 1 (blocco A, blocco B nel
# modo basso, buffer), e R138 (R_G3) ricalcolata perche' +3 e +10 dB restino
# +3,05 / +9,97 dB (R_G10 866 non cambia: la differenza di conduttanza fra +10
# e +3 e' la stessa). E96:
#   g05  +0,5 dB  RG0 25.5k  R138 4.12k
#   g10  +1,0 dB  RG0 12.4k  R138 4.99k
#   g15  +1,5 dB  RG0 7.87k  R138 6.49k
# per C124 470p/560p/680p e R128 1.69k/1.33k. Deck in strada_b/, lista in
# strada_b/lista.txt.
S=${0:A:h}
mkdir -p $S/../strada_b
: > $S/../strada_b/lista.txt
for g in g05:25.5k:4.12k g10:12.4k:4.99k g15:7.87k:6.49k; do
  parts=(${(s.:.)g})
  for cm in 470p 560p 680p; do
    for r in 1.69k 1.33k; do
      e=${parts[1]}_cm${cm}_r${r}
      /usr/bin/python3 $S/varianti.py strada_b tb_loop $e "+RG0L40 FB 0 ${parts[2]}" "alter r138 = ${parts[3]}" "alter c124 = $cm" "alter r128 = $r" >> $S/../strada_b/lista.txt
      for d in tb_loop_blockA tb_loop_bufferfissa; do
        /usr/bin/python3 $S/varianti.py strada_b $d $e "+RG0L40 FB 0 ${parts[2]}" "alter c124 = $cm" "alter r128 = $r" >> $S/../strada_b/lista.txt
      done
    done
  done
done
wc -l $S/../strada_b/lista.txt
