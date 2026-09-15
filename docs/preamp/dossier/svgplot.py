"""Grafici SVG minimi per il dossier, senza dipendenze.

SVG e' il formato primario deciso con l'utente: e' testo, quindi si
versiona e si confronta con `git diff`, e si apre in qualunque browser.
Niente matplotlib - non e' installato e non serve: qui servono assi
logaritmici, qualche curva e delle annotazioni.

Nessun numero di questo modulo finisce sul disegno: le annotazioni
arrivano gia' calcolate da build_dossier.py, che le legge dai CSV.
"""

import math

# Palette: distinguibile anche in scala di grigi (le tre modalita' di
# guadagno differiscono per tinta, le varianti per luminosita' e tratteggio).
# L32 (ADR-026): il +3 dB prende il verde, a luminosita' intermedia fra
# il blu del 0 dB e il rosso del +10 dB.
C_0DB = "#1f5c99"
C_0DB_ALT = "#7fb3e0"
C_3DB = "#2e7d4f"
C_3DB_ALT = "#86c29c"
C_10DB = "#a8452a"
C_10DB_ALT = "#e09880"
C_REQ = "#888888"
C_AXIS = "#333333"
C_GRID = "#e0e0e0"
C_GRID_MINOR = "#f2f2f2"


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


class Axes:
    """Un pannello. Due Axes che condividono x impilano un diagramma di Bode."""

    def __init__(self, x0, y0, w, h, xlim, ylim, xlog=True, ylog=False,
                 xlabel="", ylabel="", title="", xticks=None):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.xlim, self.ylim = xlim, ylim
        self.xlog, self.ylog = xlog, ylog
        self.xlabel, self.ylabel, self.title = xlabel, ylabel, title
        self.xticks = xticks  # [(valore, etichetta)] per un asse categorico
        self.bars = []        # (x, y0, y1, color, larghezza)
        self.series = []      # (xs, ys, color, label, dash, width)
        self.annots = []      # (x, y, testo, dx, dy)
        self.hlines = []      # (y, color, label, dash)
        self.vlines = []      # (x, color, dash)

    # -- trasformazioni --------------------------------------------------
    def tx(self, x):
        a, b = self.xlim
        if self.xlog:
            if x <= 0:
                x = a
            f = (math.log10(x) - math.log10(a)) / (math.log10(b) - math.log10(a))
        else:
            f = (x - a) / (b - a)
        return self.x0 + f * self.w

    def ty(self, y):
        a, b = self.ylim
        if self.ylog:
            if y <= 0:
                y = a
            f = (math.log10(y) - math.log10(a)) / (math.log10(b) - math.log10(a))
        else:
            f = (y - a) / (b - a)
        return self.y0 + self.h - f * self.h

    # -- contenuto -------------------------------------------------------
    def line(self, xs, ys, color, label=None, dash=None, width=1.6):
        self.series.append((xs, ys, color, label, dash, width))

    def hline(self, y, color=C_REQ, label=None, dash="6,4", left=False):
        """`left=True` porta l'etichetta a sinistra: serve quando due linee
        orizzontali sono cosi' vicine che le etichette si sovrappongono."""
        self.hlines.append((y, color, label, dash, left))

    def vline(self, x, color=C_REQ, dash="3,3"):
        self.vlines.append((x, color, dash))

    def annot(self, x, y, text, dx=6, dy=-6):
        self.annots.append((x, y, text, dx, dy))

    # -- resa ------------------------------------------------------------
    def bar(self, x, y0, y1, color, width=26):
        self.bars.append((x, y0, y1, color, width))

    def _xticks(self):
        a, b = self.xlim
        if self.xticks is not None:
            return list(self.xticks), []
        if not self.xlog:
            n = 8
            step = (b - a) / n
            return [(a + i * step, _fmt_lin(a + i * step)) for i in range(n + 1)], []
        major, minor = [], []
        d0, d1 = int(math.floor(math.log10(a))), int(math.ceil(math.log10(b)))
        for d in range(d0, d1 + 1):
            v = 10.0 ** d
            if a <= v <= b:
                major.append((v, _fmt_hz(v)))
            for m in range(2, 10):
                vv = m * v
                if a <= vv <= b:
                    minor.append(vv)
        return major, minor

    def _yticks(self):
        a, b = self.ylim
        if self.ylog:
            out = []
            d0, d1 = int(math.floor(math.log10(a))), int(math.ceil(math.log10(b)))
            for d in range(d0, d1 + 1):
                v = 10.0 ** d
                if a <= v <= b:
                    out.append((v, _fmt_lin(v)))
            return out
        n = 6
        step = (b - a) / n
        return [(a + i * step, _fmt_lin(a + i * step)) for i in range(n + 1)]

    def render(self, show_xlabels=True):
        p = []
        X0, Y0, W, H = self.x0, self.y0, self.w, self.h
        major, minor = self._xticks()

        p.append(f'<rect x="{X0}" y="{Y0}" width="{W}" height="{H}" '
                 f'fill="#ffffff" stroke="none"/>')
        for v in minor:
            x = self.tx(v)
            p.append(f'<line x1="{x:.1f}" y1="{Y0}" x2="{x:.1f}" y2="{Y0+H}" '
                     f'stroke="{C_GRID_MINOR}" stroke-width="1"/>')
        for v, _ in major:
            x = self.tx(v)
            p.append(f'<line x1="{x:.1f}" y1="{Y0}" x2="{x:.1f}" y2="{Y0+H}" '
                     f'stroke="{C_GRID}" stroke-width="1"/>')
        for v, _ in self._yticks():
            y = self.ty(v)
            p.append(f'<line x1="{X0}" y1="{y:.1f}" x2="{X0+W}" y2="{y:.1f}" '
                     f'stroke="{C_GRID}" stroke-width="1"/>')

        for xv, color, dash in self.vlines:
            if not (self.xlim[0] <= xv <= self.xlim[1]):
                continue
            x = self.tx(xv)
            p.append(f'<line x1="{x:.1f}" y1="{Y0}" x2="{x:.1f}" y2="{Y0+H}" '
                     f'stroke="{color}" stroke-width="1.2" stroke-dasharray="{dash}"/>')

        for yv, color, label, dash, left in self.hlines:
            if not (min(self.ylim) <= yv <= max(self.ylim)):
                continue
            y = self.ty(yv)
            p.append(f'<line x1="{X0}" y1="{y:.1f}" x2="{X0+W}" y2="{y:.1f}" '
                     f'stroke="{color}" stroke-width="1.4" stroke-dasharray="{dash}"/>')
            if label:
                tx = X0 + 4 if left else X0 + W - 4
                anchor = "start" if left else "end"
                p.append(f'<text x="{tx}" y="{y-5:.1f}" text-anchor="{anchor}" '
                         f'font-size="11" fill="{color}">{_esc(label)}</text>')

        for bx, by0, by1, bcolor, bw in self.bars:
            x = self.tx(bx)
            ya, yb = self.ty(by0), self.ty(by1)
            top, hgt = min(ya, yb), abs(yb - ya)
            p.append(f'<rect x="{x-bw/2:.1f}" y="{top:.1f}" width="{bw}" '
                     f'height="{max(hgt,1.2):.1f}" fill="{bcolor}" '
                     f'fill-opacity="0.85" stroke="{bcolor}" stroke-width="1"/>')

        for xs, ys, color, label, dash, width in self.series:
            pts = []
            for x, y in zip(xs, ys):
                if not (self.xlim[0] <= x <= self.xlim[1]):
                    continue
                yy = min(max(y, min(self.ylim)), max(self.ylim))
                pts.append(f"{self.tx(x):.1f},{self.ty(yy):.1f}")
            if not pts:
                continue
            da = f' stroke-dasharray="{dash}"' if dash else ""
            p.append(f'<polyline points="{" ".join(pts)}" fill="none" '
                     f'stroke="{color}" stroke-width="{width}"{da} '
                     f'stroke-linejoin="round"/>')

        for x, y, text, dx, dy in self.annots:
            cx, cy = self.tx(x), self.ty(y)
            p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.2" '
                     f'fill="#ffffff" stroke="{C_AXIS}" stroke-width="1.4"/>')
            anchor = "start" if dx >= 0 else "end"
            p.append(f'<text x="{cx+dx:.1f}" y="{cy+dy:.1f}" text-anchor="{anchor}" '
                     f'font-size="11" fill="{C_AXIS}">{_esc(text)}</text>')

        p.append(f'<rect x="{X0}" y="{Y0}" width="{W}" height="{H}" '
                 f'fill="none" stroke="{C_AXIS}" stroke-width="1.2"/>')
        for v, lab in major:
            x = self.tx(v)
            p.append(f'<line x1="{x:.1f}" y1="{Y0+H}" x2="{x:.1f}" y2="{Y0+H+5}" '
                     f'stroke="{C_AXIS}" stroke-width="1.2"/>')
            if show_xlabels:
                p.append(f'<text x="{x:.1f}" y="{Y0+H+18}" text-anchor="middle" '
                         f'font-size="11" fill="{C_AXIS}">{_esc(lab)}</text>')
        for v, lab in self._yticks():
            y = self.ty(v)
            p.append(f'<line x1="{X0-5}" y1="{y:.1f}" x2="{X0}" y2="{y:.1f}" '
                     f'stroke="{C_AXIS}" stroke-width="1.2"/>')
            p.append(f'<text x="{X0-9}" y="{y+4:.1f}" text-anchor="end" '
                     f'font-size="11" fill="{C_AXIS}">{_esc(lab)}</text>')

        if self.ylabel:
            p.append(f'<text x="{X0-48}" y="{Y0+H/2:.1f}" text-anchor="middle" '
                     f'font-size="12" fill="{C_AXIS}" '
                     f'transform="rotate(-90 {X0-48} {Y0+H/2:.1f})">{_esc(self.ylabel)}</text>')
        if self.xlabel and show_xlabels:
            p.append(f'<text x="{X0+W/2:.1f}" y="{Y0+H+36}" text-anchor="middle" '
                     f'font-size="12" fill="{C_AXIS}">{_esc(self.xlabel)}</text>')
        if self.title:
            p.append(f'<text x="{X0}" y="{Y0-10}" font-size="13" '
                     f'font-weight="600" fill="{C_AXIS}">{_esc(self.title)}</text>')
        return "\n".join(p)

    def legend(self, x, y, cols=1, colw=200):
        p = []
        items = [(lab, col, dash) for _, _, col, lab, dash, _ in self.series if lab]
        rows = math.ceil(len(items) / cols) if items else 0
        for i, (lab, col, dash) in enumerate(items):
            cx = x + (i // rows) * colw
            cy = y + (i % rows) * 17
            da = f' stroke-dasharray="{dash}"' if dash else ""
            p.append(f'<line x1="{cx}" y1="{cy-4}" x2="{cx+22}" y2="{cy-4}" '
                     f'stroke="{col}" stroke-width="2.2"{da}/>')
            p.append(f'<text x="{cx+28}" y="{cy}" font-size="11" '
                     f'fill="{C_AXIS}">{_esc(lab)}</text>')
        return "\n".join(p)


def _fmt_hz(v):
    if v >= 1e6:
        return f"{v/1e6:g}M"
    if v >= 1e3:
        return f"{v/1e3:g}k"
    return f"{v:g}"


def _fmt_lin(v):
    if abs(v) < 1e-9:
        return "0"
    if abs(v) >= 1000:
        return f"{v:.0f}"
    return f"{v:.4g}"


def document(width, height, body, caption=None):
    cap = ""
    if caption:
        cap = (f'<text x="12" y="{height-10}" font-size="11" fill="#666666">'
               f'{_esc(caption)}</text>')
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" '
            f'font-family="Helvetica, Arial, sans-serif">\n'
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>\n'
            f'{body}\n{cap}\n</svg>\n')
