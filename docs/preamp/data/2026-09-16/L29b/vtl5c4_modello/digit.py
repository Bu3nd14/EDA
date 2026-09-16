"""Digitalizzazione a pixel delle curve VTL5C4 (datasheet Excelitas pag. 46, 300 dpi).
Legge un BMP senza librerie, trova le righe e le colonne di griglia (linee lunghe),
poi per colonne scelte elenca i tratti scuri che non sono griglia (le curve, spesse)."""
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
        img.append([sum(b[base + x * step: base + x * step + 3]) < 300 for x in range(w)])
    return img, w, h

img, w, h = leggi_bmp(sys.argv[1])
# righe di griglia: righe con > 60% di pixel scuri
righe = [y for y in range(h) if sum(img[y]) > 0.6 * w]
col = [x for x in range(w) if sum(img[y][x] for y in range(h)) > 0.6 * h]
print("righe scure lunghe:", righe)
print("colonne scure lunghe:", col)
xs = [int(v) for v in sys.argv[2].split(",")]
for x in xs:
    tratti, y = [], 0
    while y < h:
        if img[y][x] and y not in righe:
            y0 = y
            while y < h and img[y][x]:
                y += 1
            tratti.append((y0, y - 1))
        y += 1
    print("x=%d tratti:" % x, tratti)
