#!/bin/zsh
# v2_cella.sh <fase> : una cella di V2 - 1 kHz, 100 kOhm, le tre uscite in ogni
# wrdata - dal deck versionato spice/preamp/tb/tb_v2_mute_ldr.cir, con la procedura
# di L29b2 (dividi.py, una corsa per processo, v2_metodo.py analizza). Si corrono
# solo le corse *_1k_100k e le tre A senza segnale a 100 kOhm (lz*_100k). L39, portato a L40, poi a L29c (primo controllo).
ROOT=${0:A:h:h:h:h:h:h:h}
DIR=$ROOT/docs/preamp/data/2026-09-23/L29c/$1/v2_1k_100k
mkdir -p $DIR
# Secondo argomento facoltativo: il deck da correre (per "prima", la copia del
# deck versionato di L29b2, sui segnaposto, salvata in <fase>/tb_v2_mute_ldr_L29b2.cir).
DECK=${2:-$ROOT/spice/preamp/tb/tb_v2_mute_ldr.cir}
sed "s|@REPO@|$ROOT|g" $DECK > $DIR/ldr.cir
/usr/bin/python3 $ROOT/docs/preamp/data/2026-09-22/L29b2/pavimento/dividi.py $DIR/ldr.cir
# Le righe del manifesto non sono corse: "rele" rilegge i dati di "ev", le "pav_*"
# quelli di "evp"/"invp". Si filtra e si corre per la colonna file (L39: la prima
# versione filtrava per cella, e ha lanciato una corsa inesistente).
head -1 $DIR/manifest.csv > $DIR/manifest_cella.csv
grep -E ',([a-z]+_1k_100k|lz[a-z]+_100k)\.dat,' $DIR/manifest.csv >> $DIR/manifest_cella.csv
cd $DIR
touch tempi.txt
corri() {
  local c=$1 t0=$SECONDS
  /opt/homebrew/bin/ngspice -b corsa_$c.cir > corsa_$c.log 2>&1
  print -r -- "$c rc=$? $((SECONDS-t0))s" >> tempi.txt
}
for c in ${(fu)"$(tail -n +2 manifest_cella.csv | cut -d, -f2 | sed 's/\.dat$//')"}; do
  [ -s $c.dat ] && { echo "$c: gia' corsa"; continue; }
  corri $c &
done
wait
cat tempi.txt
echo "log con righe Error:"
grep -c -E 'Error' corsa_*.log | grep -v ':0$'
/usr/bin/python3 $ROOT/scripts/v2_metodo.py analizza $DIR/manifest_cella.csv $DIR $DIR/analisi.csv | tail -30
