#!/bin/zsh
# L29d2: il generatore esteso deve ridare BYTE PER BYTE i deck versionati di L29c e della sonda
# L29d. Rigenera in una cartella di lavoro e confronta con cmp. Esce col numero di differenze.
# Uso: identici.sh <cartella_di_lavoro>
ROOT=${0:A:h:h:h:h:h:h:h}
T=$1
mkdir -p $T
G=$ROOT/docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py
D=$ROOT/docs/preamp/data/2026-09-23/L29c
bad=0
prova() {
  # prova <file versionato> <argomenti del generatore...>
  local ref=$1; shift
  local out=$T/${ref:t}
  /usr/bin/python3 $G "$@" --uscita $out > /dev/null
  if cmp -s $ref $out; then
    print "identico  ${ref#$ROOT/}"
  else
    print "DIVERSO   ${ref#$ROOT/}"
    bad=$((bad+1))
  fi
}
prova $ROOT/spice/preamp/tb/tb_v2_casopeggiore.cir --matrice l29c
prova $D/controfattuale/cf.cir --matrice controfattuale
prova $D/caldo/tb_v2_caldo.cir --matrice caldo
for c in AA AD DA DD; do
  prova $D/curve/tb_v2_curve_$c.cir --matrice curve --curve ${c[1]} ${c[2]}
done
prova $ROOT/docs/preamp/data/2026-09-25/L29d/deck/tb_v2_sonda_serie.cir --matrice sonda_l29d
print "differenze: $bad"
exit $bad
