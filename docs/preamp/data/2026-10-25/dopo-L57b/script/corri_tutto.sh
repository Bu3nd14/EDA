#!/bin/zsh
# dopo L57b: corri_tutto.sh - i gruppi del banco in fila (tre corse alla volta dentro ciascuno,
# limitations #75): il caso noto, le tre reti, il mute, il punto di lavoro vivo, il costo.
S=${0:A:h}
PY=/usr/bin/python3
for g in noto reti mute; do
  $PY $S/esegui.py $g || exit 1
done
$PY $S/nodeset.py || exit 1
$PY $S/esegui.py costo || exit 1
echo "corri_tutto: finito"
