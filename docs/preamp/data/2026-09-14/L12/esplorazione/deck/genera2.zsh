#!/bin/zsh
# L12 scratch: copies of four versioned decks with a candidate applied by `alter`
# at the top of .control. g0 = today's values (control), g3 = 470p / 330p / 56.
set -e
WT=/Users/roberto/EDA/.claude/worktrees/L12-margine-fase
OUT=/Users/roberto/.claude/jobs/55979623/tmp/rimedi/costi2
typeset -A CM CF RI
CM=(0 470p 3 470p)
CF=(0 22p  3 330p)
RI=(0 47   3 56)
for k in 0 3; do
  for deck in tb_v3_overload tb_ac tb_zout_psrr_noise tb_switch_v2; do
    d=$OUT/g$k/$deck
    mkdir -p $d
    ins="alter c124 = ${CM[$k]}\nalter c137 = ${CF[$k]}\nalter riso = ${RI[$k]}\necho \"L12 CANDIDATO g$k: C124=${CM[$k]} C137=${CF[$k]} RISO=${RI[$k]}\""
    awk -v ins="$ins" '{print} /^\.control/{gsub(/\\n/,"\n",ins); print ins}' $WT/spice/preamp/tb/$deck.cir > $d/$deck.cir
    n=$(grep -c "^alter c137" $d/$deck.cir)
    [[ $n == 1 ]] || { echo "insert count $n in $d/$deck.cir"; exit 1; }
  done
done
echo "generated 8 decks"
