#!/bin/zsh
# L70: the netlists of the variants (psu_<v>.py -> psu_<v>.net), and of the source as it is
# (psu_oggi.net, the control: it must equal circuits/preamp/psu.net but the date line).
set -u
Q=${0:A:h}
R=${Q:h:h:h:h:h:h}
cd "$Q" || exit 1
for v in s2 s1 s1s2 s1s2dc; do
    /usr/bin/env PSU_NET_OUT="$Q/psu_$v.net" /Users/roberto/EDA/env/venv/bin/python3 "$Q/psu_$v.py" > "$Q/psu_$v.out" 2>&1
    echo "$v: rc $?"
done
/usr/bin/env PSU_NET_OUT="$Q/psu_oggi.net" /Users/roberto/EDA/env/venv/bin/python3 "$R/circuits/preamp/psu.py" > "$Q/psu_oggi.out" 2>&1
echo "oggi: rc $?"
