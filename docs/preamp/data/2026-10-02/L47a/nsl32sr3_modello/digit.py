"""Lettura a pixel del grafico «Photocell Resistance vs. LED Current» della NSL-32SR3
(datasheet Silonex 104058 Rev 07, pag. 1, rasterizzata a 300 dpi con pdftoppm e ritagliata;
vedi README). Legge un BMP senza librerie, come il digit.py di L29b.

Trova le righe e le colonne di griglia (linee nere lunghe dentro il grafico) e i centri dei
cinque rombi blu dei punti marcati. Stampa i pixel e i valori (griglia log-log)."""
import struct, sys


def leggi_bmp(p):
    b = open(p, "rb").read()
    off = struct.unpack_from("<I", b, 10)[0]
    w, h = struct.unpack_from("<ii", b, 18)
    bpp = struct.unpack_from("<H", b, 28)[0]
    step = bpp // 8
    row = (w * step + 3) & ~3
    flip = h > 0
    h = abs(h)
    img = []
    for y in range(h):
        yy = (h - 1 - y) if flip else y
        base = off + yy * row
        img.append([tuple(b[base + x * step: base + x * step + 3]) for x in range(w)])   # B, G, R
    return img, w, h


img, w, h = leggi_bmp(sys.argv[1])
nero = lambda p: sum(p) < 200
blu = lambda p: p[0] > 90 and p[2] < 60 and p[1] < 60

# righe e colonne di griglia: almeno 500 pixel neri in fila (il riquadro esterno e' piu' lungo
# e sta fuori dal grafico; si tengono le linee interne fra le etichette)
righe = [y for y in range(h) if sum(nero(img[y][x]) for x in range(w)) > 500]
colonne = [x for x in range(w) if sum(nero(img[y][x]) for y in range(h)) > 250]


def gruppi(v):
    out, cur = [], [v[0]]
    for a in v[1:]:
        if a - cur[-1] <= 2:
            cur.append(a)
        else:
            out.append(cur)
            cur = [a]
    out.append(cur)
    return [sum(c) / len(c) for c in out]


print("righe nere lunghe:", gruppi(righe))
print("colonne nere lunghe:", gruppi(colonne))

# pixel blu: i rombi sono le macchie piu' larghe della linea della curva (spessa ~3 px)
pix = [(x, y) for y in range(h) for x in range(w) if blu(img[y][x])]
macchie = []
for x, y in pix:
    for m in macchie:
        if abs(m["x"] - x) <= 12 and abs(m["y"] - y) <= 12:
            m["p"].append((x, y))
            break
    else:
        macchie.append({"x": x, "y": y, "p": [(x, y)]})
rombi = []
for m in macchie:
    xs = [p[0] for p in m["p"]]
    ys = [p[1] for p in m["p"]]
    if max(xs) - min(xs) >= 8 and max(ys) - min(ys) >= 8:
        rombi.append(((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, len(m["p"])))
print("rombi (x, y, pixel):")
for r in sorted(rombi):
    print("  %.1f %.1f %d" % r)
