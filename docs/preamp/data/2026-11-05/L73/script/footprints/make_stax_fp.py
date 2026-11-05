#!/usr/bin/env python3
"""
L73: the trial footprint of the Stax output capacitor (C165 / C365), NC-080.

A copy of KiCad's C_Rect_L26.5mm_W7.0mm_P22.50mm_MKS4 (the WIMA MKP 4 1 uF,
the biggest part of the Stax window in the admitted list, REQUIREMENTS P6,
ADR-121 / ADR-122) with a silkscreen marking inside the outline.

Why it is distinct from the Singxer's (C162 / C362): the Singxer output takes
4.7-10 uF, 31.5 x 15 mm at pitch 27.5 up to 41.5 x 19 at pitch 37.5. A 4.7 uF
film cap (pitch 27.5) does not go into 22.5 mm holes, and the marking says the
only value allowed. The 4.7 uF on the Stax gives 538 ms above 0.87 V (E8).

A TRIAL footprint (scratch of L73): the source takes it only by decision, G2.

  /usr/bin/python3 make_stax_fp.py <out .pretty dir>
"""
import os
import sys

SRC = ("/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints/"
       "Capacitor_THT.pretty/C_Rect_L26.5mm_W7.0mm_P22.50mm_MKS4.kicad_mod")
NAME = "C_Rect_L26.5mm_W7.0mm_P22.50mm_STAX_1uF"
MARK = """	(fp_text user "STAX 1uF 5% ONLY"
		(at 11.25 0 0)
		(layer "F.SilkS")
		(effects
			(font
				(size 1.2 1.2)
				(thickness 0.18)
			)
		)
	)
"""


def main():
    out = sys.argv[1]
    t = open(SRC).read()
    t = t.replace('(footprint "C_Rect_L26.5mm_W7.0mm_P22.50mm_MKS4"', f'(footprint "{NAME}"', 1)
    t = t.replace('(generator "kicad-footprint-generator")', '(generator "L73 make_stax_fp.py")', 1)
    t = t.replace('(property "Value" "C_Rect_L26.5mm_W7.0mm_P22.50mm_MKS4"',
                  f'(property "Value" "{NAME}"', 1)
    t = t.replace('length*width=26.5*7mm^2, Capacitor,',
                  'length*width=26.5*7mm^2, Stax output 1 uF +/-5 % only (ADR-121, NC-080, L73 trial),', 1)
    # The Fab reference moves off the centre, the marking takes it.
    t = t.replace('(fp_text user "${REFERENCE}"\n\t\t(at 11.25 0 0)',
                  '(fp_text user "${REFERENCE}"\n\t\t(at 11.25 2 0)', 1)
    t = t.replace("\t(pad \"1\"", MARK + "\t(pad \"1\"", 1)
    assert NAME in t and "STAX 1uF" in t
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, NAME + ".kicad_mod")
    open(path, "w").write(t)
    print("written:", path)


if __name__ == "__main__":
    main()
