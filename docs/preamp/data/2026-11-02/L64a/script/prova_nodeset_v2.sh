#!/bin/zsh
# L64a: prova dei .nodeset del blocco (nodeset_v2.py) su celle della matrice di V2 gia' corse oggi
# con rc=0 senza: i due .dat (onde e stati) devono restare uguali byte per byte. Una alla volta, a
# priorita' bassa. Uso: prova_nodeset_v2.sh <cartella delle corse> <cella> [...]
D=$1
shift
OUT=${0:A:h:h}/prova_nodeset
mkdir -p $OUT
cd $D
for c in $@; do
  cp $c.dat $OUT/${c}_senza.dat
  cp ${c}_stati.dat $OUT/${c}_stati_senza.dat
  nice -n 15 /opt/homebrew/bin/ngspice -b corsa_${c}_nb.cir > $OUT/${c}_nb.log 2>&1
  rc=$?
  esito=DIVERSI
  if cmp -s $c.dat $OUT/${c}_senza.dat && cmp -s ${c}_stati.dat $OUT/${c}_stati_senza.dat; then
    esito="uguali byte per byte"
  fi
  print -r -- "$c: rc=$rc transient_op=$(grep -c 'Transient op started' $OUT/${c}_nb.log); i due .dat coi nodeset e senza: $esito" | tee -a $OUT/esito.txt
  # i .dat coi nodeset restano accanto (<cella>_nb.dat) per scarto_nodeset_v2.py; quelli della
  # matrice restano quelli della corsa senza nodeset
  cp $c.dat ${c}_nb.dat
  cp ${c}_stati.dat ${c}_stati_nb.dat
  cp $OUT/${c}_senza.dat $c.dat
  cp $OUT/${c}_stati_senza.dat ${c}_stati.dat
done
