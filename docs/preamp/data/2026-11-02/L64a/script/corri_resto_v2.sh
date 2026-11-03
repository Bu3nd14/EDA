#!/bin/zsh
# L64a: il resto della matrice di V2, senza caricare la macchina (l'utente, 2026-11-02: «cerca di
# non caricare al massimo la CPU»). Uso: corri_resto_v2.sh <npar> <cella in corsa> ...
#  1. le corse non ancora finite con rc=0, tranne quelle ancora in corsa (gli argomenti) e le
#     celle della dispersione che non trovano l'op (rc=OPT): corri.sh di L29c, <npar> alla volta,
#     a priorita' bassa;
#  2. le celle rc=OPT coi .nodeset del blocco da solo (nodeset_v2.py, limitations #86), con la
#     guardia di L29c, <npar> alla volta; esito in tempi.txt con la nota «nodeset_blocco»;
#  3. manifest_sel.csv e corse_sel.txt di nuovo su tutta la matrice ('.*'), per l'analisi.
L=${0:A:h:h}
ROOT=${L:h:h:h:h:h}
C=$ROOT/docs/preamp/data/2026-09-23/L29c
D=$L/run/v2
NPAR=$1
shift
RE=$(/usr/bin/python3 -I $L/script/resto_v2.py $D $@)
print -r -- "resto: ${RE[1,200]}..."
if [[ -n $RE ]]; then
  nice -n 10 /bin/zsh $C/script/corri.sh $D $ROOT/spice/preamp/tb/tb_v2_casopeggiore.cir "$RE" $NPAR
fi
OPT=($(grep " rc=OPT " $D/tempi.txt | awk '{print $1}' | sort -u))
/usr/bin/python3 -I $L/script/nodeset_v2.py $D $OPT
cd $D
uno_nb() {
  local c=$1 t0=$SECONDS
  nice -n 10 /opt/homebrew/bin/ngspice -b corsa_${c}_nb.cir > corsa_${c}_nb.log 2>&1
  local rc=$?
  if grep -q 'Transient op started' corsa_${c}_nb.log; then
    rc=OPT
  fi
  print -r -- "$c rc=$rc $((SECONDS-t0))s $(date +%H:%M:%S) nodeset_blocco" >> tempi.txt
}
for c in $OPT; do
  while (( ${#jobstates} >= NPAR )); do
    sleep 5
  done
  uno_nb $c &
done
wait
/usr/bin/python3 $C/script/seleziona.py $D/manifest.csv '.*' $D/manifest_sel.csv $D/corse_sel.txt
print -r -- "fine: $(grep -c ' rc=0 ' $D/tempi.txt) righe rc=0 in tempi.txt"
