"""L47b2a: a fake netlist with ONE LED reversed (U301, the series string's R).

Usage: python3 rovescia_un_led.py <in.net> <out.net>
Swaps pin "1" and pin "2" of U301 in every net's node list. The result is a
series string whose two LEDs meet anode to anode: it never lights, and it
generates and ERCs like the good one. check_relay_safe_state.py must refuse it.
"""
import re
import sys


def main(src, dst):
    text = open(src).read()
    pat = re.compile(r'(\(ref "U301"\)\s+\(pin ")([12])(")')
    n = len(pat.findall(text))
    if n != 2:
        sys.exit(f"expected U301 pins 1 and 2 once each, found {n}")
    out = pat.sub(lambda m: m.group(1) + {"1": "2", "2": "1"}[m.group(2)]
                  + m.group(3), text)
    open(dst, "w").write(out)
    print(f"{dst}: U301 pin 1 <-> 2")


if __name__ == "__main__":
    main(*sys.argv[1:3])
