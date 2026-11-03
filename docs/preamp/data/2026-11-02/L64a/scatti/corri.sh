#!/bin/zsh
# L48b: corre i deck tb_l48b_scatti_v*.cir di una cartella in parallelo, un log per deck.
# Uso: corri.sh <cartella>. Svuota prima i CSV e le onde (limitations #35).
dir=$1
rm -f $dir/scatti_v*.csv(N) $dir/onde_v*.txt(N) $dir/v*.log(N)
for d in $dir/tb_l48b_scatti_v*.cir; do
  n=${d:t:r}
  /opt/homebrew/bin/timeout 3000 /opt/homebrew/bin/ngspice -b $d -o $dir/${n#tb_l48b_scatti_}.log > /dev/null 2>&1 &
done
wait
for l in $dir/v*.log; do
  print -- "$l: $(grep -c -E 'Transient op started|Timestep too small|aborted|^Error|too many args|no such device' $l) righe sospette"
done
