#!/bin/zsh
# L12 scratch: copies of three versioned decks with a remedy candidate applied
# by `alter` at the top of .control. Candidate 0 = today's values (control run).
set -e
WT=/Users/roberto/EDA/.claude/worktrees/L12-margine-fase
OUT=/Users/roberto/.claude/jobs/55979623/tmp/rimedi/costi
typeset -A CM CF RI
CM=(0 470p 1 1n   2 820p 3 680p)
CF=(0 22p  1 22p  2 47p  3 47p)
RI=(0 47   1 47   2 68   3 68)
for k in 0 1 2 3; do
  for deck in tb_v3_overload tb_ac tb_zout_psrr_noise; do
    d=$OUT/c$k/$deck
    mkdir -p $d
    ins="alter c124 = ${CM[$k]}\nalter c137 = ${CF[$k]}\nalter riso = ${RI[$k]}\necho \"L12 CANDIDATO c$k: C124=${CM[$k]} C137=${CF[$k]} RISO=${RI[$k]}\""
    awk -v ins="$ins" '{print} /^\.control/{gsub(/\\n/,"\n",ins); print ins}' $WT/spice/preamp/tb/$deck.cir > $d/$deck.cir
    n=$(grep -c "^alter c124" $d/$deck.cir)
    [[ $n == 1 ]] || { echo "insert count $n in $d/$deck.cir"; exit 1; }
  done
done
echo "generated 12 decks"
