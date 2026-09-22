#!/bin/zsh
# sabotaggi_2i.sh - il nuovo blocco 2i (scripts/check_no_placeholders.py) fatto
# cadere. Per ogni caso una copia di spice/ in una radice finta, un solo difetto,
# e l'exit code atteso. L39.
ROOT=${0:A:h:h:h:h:h:h:h}
S=$ROOT/docs/preamp/data/2026-09-22/L39/sabotaggi
CHK=$ROOT/scripts/check_no_placeholders.py
rm -rf $S/radici
mkdir -p $S/radici
: > $S/esiti.txt
caso() {   # nome, atteso, comando che guasta la copia (eseguito dentro la radice)
  local r=$S/radici/$1
  mkdir -p $r
  cp -R $ROOT/spice $r/spice
  ( cd $r && eval "$3" )
  /usr/bin/python3 $CHK $r > $S/$1.txt 2>&1
  local rc=$?
  local v="SBAGLIATO"; [ $rc -eq $2 ] && v="come atteso"
  print -r -- "$1: rc=$rc atteso=$2 $v - $(tail -1 $S/$1.txt)" >> $S/esiti.txt
}
caso c0_intatto 0 'true'
caso s1_include_nel_deck 1 'sed -i "" "s|^.include @REPO@/models/jfet/lsk489.lib$|.include @REPO@/spice/preamp/placeholder_devices.lib|" spice/preamp/tb/tb_op.cir'
caso s2_nome_nel_blocco 1 'sed -i "" "s| LSK489A$| LSK489X|" spice/preamp/gain_block_flat.inc'
caso s3_nome_nel_subckt 1 'sed -i "" "s| D1N914$| D1N4148|" spice/preamp/gain_block.subckt'
caso s4_riga_nel_deck 1 'print -r -- "QSONDA 1 2 3 NSS2N5551" >> spice/preamp/tb/tb_ac.cir'
caso s5_commento_non_conta 0 'print -r -- "* un tempo Q106 era NSS2N5551" >> spice/preamp/tb/tb_ac.cir'
caso s6_libreria_assente 2 'rm spice/preamp/placeholder_devices.lib'
caso s7_include_minuscolo 1 'print -r -- ".INCLUDE @REPO@/spice/preamp/placeholder_devices.lib" >> spice/preamp/tb/tb_trim.cir'
rm -rf $S/radici
cat $S/esiti.txt
