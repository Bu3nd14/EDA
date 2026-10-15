#!/usr/bin/env python3
"""Leg 3 of the IM pin-map reading: the vector coordinates of the terminal
assignment drawing (108-98001 Rev. K p. 5, non-latching, top view).

Prints every straight segment of the drawing (page coordinates in pt) inside
the region of the non-latching terminal drawing, then, for each diagonal
segment (the armatures), its distance at its free end from the vertical
contact lines nearby.

L60c2, run as:
  /opt/homebrew/bin/pdftocairo -svg -f 5 -l 5 \
      vendor/relays/te/IM/ENG_DS_108-98001_K.pdf p5.svg
  /usr/bin/python3 im_pinmap_svg.py p5.svg 28 144 715 805
The drawing's lines are filled outlines, so the contacts show up as thin
horizontal rectangles at the tip height (y ~ 723.4-724.2 pt for the top row,
~ 794.3-795.0 pt for the bottom row): the 2 / 7 contact spans x = 96.2-104.0
pt, the 4 / 5 contact 110.7-116.1 pt. The armature of pole 2 runs from
(106.1, 733.2) to (99.6, 721.5): at y = 723.8 it is at x = 100.9 pt, INSIDE
the 7 contact and 9.8 pt short of the 5 one; pole 1 mirrors it (x = 100.8 pt
at y = 794.6). Pin 7 / 2 sit at x ~ 96.6 pt, 6 / 3 at ~ 106.2, 5 / 4 at
~ 115.7 (the pad outlines). So: COM 3 / 6 rest on 2 / 7 (NC), 4 / 5 are NO."""
import re
import sys
import xml.etree.ElementTree as ET

svg, x0, x1, y0, y1 = sys.argv[1], *map(float, sys.argv[2:6])
NS = "{http://www.w3.org/2000/svg}"
tree = ET.parse(svg)


def mat(t):
    if not t:
        return (1, 0, 0, 1, 0, 0)
    m = re.match(r"matrix\(([^)]*)\)", t)
    if m:
        return tuple(float(v) for v in re.split(r"[ ,]+", m.group(1).strip()))
    return (1, 0, 0, 1, 0, 0)


def mul(a, b):
    return (a[0]*b[0] + a[2]*b[1], a[1]*b[0] + a[3]*b[1],
            a[0]*b[2] + a[2]*b[3], a[1]*b[2] + a[3]*b[3],
            a[0]*b[4] + a[2]*b[5] + a[4], a[1]*b[4] + a[3]*b[5] + a[5])


def ap(m, x, y):
    return (m[0]*x + m[2]*y + m[4], m[1]*x + m[3]*y + m[5])


segs = []


def walk(el, m):
    if el.tag == NS + "defs":
        return
    m = mul(m, mat(el.get("transform")))
    if el.tag == NS + "path":
        toks = re.findall(r"[MLCZHVmlczhv]|-?[\d.]+(?:e-?\d+)?", el.get("d", ""))
        cur = None
        start = None
        i = 0
        cmd = None
        while i < len(toks):
            t = toks[i]
            if t.isalpha():
                cmd = t
                i += 1
                if cmd in "Zz":
                    if cur and start:
                        segs.append((cur, start))
                    cur = start
                continue
            if cmd == "M":
                cur = start = (float(toks[i]), float(toks[i+1])); i += 2; cmd = "L"
            elif cmd == "L":
                p = (float(toks[i]), float(toks[i+1])); i += 2
                segs.append((cur, p)); cur = p
            elif cmd == "C":
                p = (float(toks[i+4]), float(toks[i+5])); i += 6; cur = p
            else:
                i += 1
        # transform the segments just added
        pass
    for c in el:
        walk(c, m)
    if el.tag == NS + "path":
        pass


# simpler: collect with transforms applied
def walk2(el, m, out):
    if el.tag == NS + "defs":
        return
    m = mul(m, mat(el.get("transform")))
    if el.tag == NS + "path":
        before = len(segs)
        walk(el, (1, 0, 0, 1, 0, 0))
        for s in segs[before:]:
            out.append((ap(m, *s[0]), ap(m, *s[1])))
        del segs[before:]
        return
    for c in el:
        walk2(c, m, out)


out = []
walk2(tree.getroot(), (1, 0, 0, 1, 0, 0), out)
inreg = [s for s in out
         if all(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in s)
         and abs(s[0][0]-s[1][0]) + abs(s[0][1]-s[1][1]) > 0.5]
verts = []
for a, b in inreg:
    kind = "V" if abs(a[0]-b[0]) < 0.05 else ("H" if abs(a[1]-b[1]) < 0.05 else "D")
    print(f"{kind} ({a[0]:8.3f},{a[1]:8.3f}) -> ({b[0]:8.3f},{b[1]:8.3f})")
    if kind == "V":
        verts.append((a[0], min(a[1], b[1]), max(a[1], b[1])))
print()
for a, b in inreg:
    if abs(a[0]-b[0]) < 0.05 or abs(a[1]-b[1]) < 0.05:
        continue
    for tip, other in ((a, b), (b, a)):
        near = sorted((abs(v[0]-tip[0]), v[0]) for v in verts
                      if v[1]-1 <= tip[1] <= v[2]+1)
        print(f"diagonal end ({tip[0]:.3f},{tip[1]:.3f}): vertical lines at "
              + ", ".join(f"x={x:.3f} (dist {d:.2f} pt)" for d, x in near[:3]))
