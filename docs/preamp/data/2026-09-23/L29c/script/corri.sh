#!/bin/zsh
# corri.sh <dir> <deck> <regex> <npar> : corre le corse di un deck di V2 generato (L29c), quelle
# la cui colonna FILE del manifesto soddisfa <regex> (grep -E sul nome del .dat, senza .dat), con
# al piu' <npar> ngspice insieme. Procedura di L29b2: sed @REPO@, dividi.py, una corsa per
# processo. Il manifesto filtrato (manifest_sel.csv) contiene le righe le cui corse sono
# richieste; i riferimenti che nominano vanno selezionati anche loro dal regex.
# Una corsa gia' fatta (.dat non vuoto e riga rc=0 in tempi.txt) non si ripete.
ROOT=${0:A:h:h:h:h:h:h:h}
DIR=$1
DECK=$2
RE=$3
NPAR=${4:-10}
mkdir -p $DIR
sed "s|@REPO@|$ROOT|g" $DECK > $DIR/deck.cir
/usr/bin/python3 $ROOT/docs/preamp/data/2026-09-22/L29b2/pavimento/dividi.py $DIR/deck.cir > $DIR/dividi.txt
/usr/bin/python3 $ROOT/docs/preamp/data/2026-09-23/L29c/script/seleziona.py $DIR/manifest.csv "$RE" $DIR/manifest_sel.csv $DIR/corse_sel.txt
cd $DIR
touch tempi.txt
corri() {
  local c=$1 t0=$SECONDS
  /opt/homebrew/bin/ngspice -b corsa_$c.cir > corsa_$c.log 2>&1
  print -r -- "$c rc=$? $((SECONDS-t0))s $(date +%H:%M:%S)" >> tempi.txt
}
for c in $(cat corse_sel.txt); do
  if [ -s $c.dat ] && grep -q "^$c rc=0 " tempi.txt; then
    echo "$c: gia' corsa"
    continue
  fi
  while [ $(jobs -r | wc -l) -ge $NPAR ]; do
    sleep 5
  done
  corri $c &
done
wait
echo "fatto: $(wc -l < corse_sel.txt) corse selezionate"
