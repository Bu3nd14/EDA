"""genera_impronta.py - L47b2b1: l'impronta propria della NSL-32SR3, coi terminali del LED a 3,30 mm.

Scelta dell'utente (L47b2b1, alla domanda sull'impronta): «Impronta propria nel repo».

Parte dall'impronta KiCad OptoDevice:Luna_NSL-32 (KiCad 10.0.6, SharedSupport/footprints) e ne
cambia solo le quote che il disegno del costruttore contraddice:
  - LED (piazzole 1 e 2): 3,81 -> 3,30 mm (Silonex 104058 Rev 07: 3,30 +/- 0,13; Advanced Photonix
    3,3). Piazzola 1 (anodo, rettangolare) resta in (0, 0); la 2 va in (0, -3,30);
  - cella (3 e 4): 2,53 -> 2,54 mm (Silonex 2,54 +/- 0,13), centrata come il LED;
  - tutto il resto (corpo, serigrafia, fab, cortile, testi) traslato di +0,255 mm in y, cosi' che
    corpo e cella restino centrati sulla coppia del LED come nell'originale (centro -1,905 -> -1,65);
  - le due righe Fab dei terminali del LED seguono le piazzole.
Fori 0,81 mm invariati: accolgono il LED Silonex (0,25 x 0,64, diagonale ~0,69) e la cella (0,4).
Il modello 3D resta quello di KiCad (passo dei terminali del LED 3,81: solo l'aspetto).

    /usr/bin/python3 genera_impronta.py <uscita.kicad_mod>
"""
import re
import sys

SORGENTE = ("/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints/"
            "OptoDevice.pretty/Luna_NSL-32.kicad_mod")
NOME = "NSL-32SR3_LED3.30"
LED, CELLA = 3.30, 2.54
CENTRO_VECCHIO, CENTRO = -3.81 / 2, -LED / 2
DY = CENTRO - CENTRO_VECCHIO                      # +0,255


def fmt(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def main():
    t = open(SORGENTE).read()
    assert t.count('(pad "') == 4, "impronta sorgente inattesa"
    # 1. le piazzole, per numero
    pos = {"1": (0.0, 0.0), "2": (0.0, -LED),
           "3": (10.16, CENTRO - CELLA / 2), "4": (10.16, CENTRO + CELLA / 2)}

    def pad(m):
        n = m.group(1)
        x, y = pos[n]
        return '(pad "%s"%s(at %s %s)' % (n, m.group(2), fmt(x), fmt(y))
    t, k = re.subn(r'\(pad "(\d)"([^(]*)\(at [-0-9.]+ [-0-9.]+\)', pad, t)
    assert k == 4
    # 2. le righe Fab dei terminali del LED (y = 0 e y = -3,8): seguono le piazzole, non si traslano
    t = t.replace("(start 0.03 -3.8)\n\t\t(end 1.98 -3.8)", "(start 0.03 -3.3)\n\t\t(end 1.98 -3.3)")
    t = t.replace("(start 1.46 -3.8)\n\t\t(end 1.87 -3.8)", "(start 1.46 -3.3)\n\t\t(end 1.87 -3.3)")
    fisse = {"(start -0.02 0)", "(end 1.98 0)", "(start 1.46 0)", "(end 1.87 0)",
             "(start 0.03 -3.3)", "(end 1.98 -3.3)", "(start 1.46 -3.3)", "(end 1.87 -3.3)"}

    # 3. ogni altra coordinata di linee e testi: +DY in y
    def sposta(m):
        tutto = m.group(0)
        if tutto in fisse:
            return tutto
        x, y, resto = m.group(2), float(m.group(3)), m.group(4) or ""
        return "(%s %s %s%s)" % (m.group(1), x, fmt(y + DY), resto)
    t = re.sub(r"\((start|end|at) ([-0-9.]+) ([-0-9.]+)( [-0-9.]+)?\)",
               lambda m: sposta(m) if not m.group(0).startswith("(at 0 0 0)") else m.group(0), t)
    # le piazzole sono gia' al posto giusto: rimetterle (lo spostamento sopra le ha toccate)
    t, k = re.subn(r'\(pad "(\d)"([^(]*)\(at [-0-9.]+ [-0-9.]+\)', pad, t)
    assert k == 4
    t = t.replace('(footprint "Luna_NSL-32"', '(footprint "%s"' % NOME, 1)
    t = t.replace('(property "Value" "Luna_NSL-32"', '(property "Value" "%s"' % NOME, 1)
    t = t.replace('(descr "Optoisolator with LED and photoresistor")',
                  '(descr "NSL-32SR3 (Advanced Photonix): LED lead pitch 3.30 mm, cell 2.54 mm, per '
                  'Silonex 104058 Rev 07 (+/-0.13). Derived from KiCad OptoDevice:Luna_NSL-32 '
                  '(LED at 3.81 mm). EDA repo, L47b2b1, docs/preamp/data/2026-10-03/L47b2b1/impronta/")', 1)
    open(sys.argv[1], "w").write(t)
    for n, (x, y) in sorted(pos.items()):
        print("piazzola %s: (%s, %s)" % (n, fmt(x), fmt(y)))
    print("LED %.2f mm, cella %.2f mm, centri %.3f / %.3f" % (
        LED, CELLA, (pos["1"][1] + pos["2"][1]) / 2, (pos["3"][1] + pos["4"][1]) / 2))


if __name__ == "__main__":
    main()
