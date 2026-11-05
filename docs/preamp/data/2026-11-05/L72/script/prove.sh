#!/bin/zsh
# prove.sh <file di uscita> : run_tests.sh dal worktree, a nice 10.
L=${0:A:h:h}
ROOT=${L:h:h:h:h:h}
cd $ROOT || exit 1
nice -n 10 /bin/zsh $ROOT/scripts/run_tests.sh > $1 2>&1
rc=$?
print -r -- "run_tests rc=$rc"
tail -6 $1
