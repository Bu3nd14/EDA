"""L47b2a: the nets of the four mute cells' pins, and the part, in a KiCad netlist.

Usage: python3 piedini_celle.py <preamp_audio.net> [...]
Prints, for U101/U301 (series string) and U102/U302 (shunt string), the
part and the net on each pin. Which pin is the anode is the SYMBOL's fact,
not the netlist's: Isolator:NSL-32 1 = A, 2 = K; Isolator:VTL5C 1 = K, 2 = A
(both read from KiCad 10's Isolator.kicad_sym in L47b2a). The script says
which LED pin each net reaches by that table.
"""
import re
import sys

REFS = ("U101", "U301", "U102", "U302")
LED = {"NSL-32": {"1": "A", "2": "K"}, "VTL5C": {"1": "K", "2": "A"}}


def main(paths):
    for path in paths:
        text = open(path).read()
        parts = dict(re.findall(
            r'\(ref "(U[13]0[12])"\).*?\(part "([^"]+)"\)', text, re.S))
        pins = {}
        for block in text.split("(net\n")[1:]:
            name = re.search(r'\(name "([^"]*)"\)', block).group(1)
            for ref, pin in re.findall(
                    r'\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
                if ref in REFS:
                    pins[(ref, pin)] = name
        print(path)
        for ref in REFS:
            part = parts.get(ref, "?")
            fn = LED.get(part, {})
            row = "  ".join(f"{p}({fn.get(p, 'cella' if p in '34' else '?')})"
                            f"={pins.get((ref, p), '?')}" for p in "1234")
            print(f"  {ref} {part:7s} {row}")


if __name__ == "__main__":
    main(sys.argv[1:])
