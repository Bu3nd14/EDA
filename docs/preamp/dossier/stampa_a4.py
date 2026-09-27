#!/usr/bin/env python3
"""Il dossier in un PDF A4 stampabile, FUORI dal repo.

    /usr/bin/python3 docs/preamp/dossier/stampa_a4.py <file.pdf>

La fonte di verita' e' la pagina che build_dossier.py genera; il PDF ne e' una
stampa usa-e-getta e **non si versiona**: lo script rifiuta un percorso
d'uscita dentro il repository. Due copie versionate dello stesso dossier
diventerebbero due fonti di verita' (decisione dell'utente, 2026-09-27).

Cosa fa:
  1. build_dossier.py --standalone in una cartella temporanea: la pagina con
     le figure incorporate, generata sul momento coi suoi controlli (se il
     generatore rifiuta, non si stampa niente);
  2. un foglio di stile di stampa: A4, tema chiaro, piè di pagina numerato,
     tabelle e figure non spezzate, celle che vanno a capo agli spazi. Senza
     quest'ultima regola una tabella larga esce dal margine e Chrome
     rimpicciolisce TUTTO il documento per farcela stare;
  3. Chrome headless, --print-to-pdf.

Solo stdlib; serve Google Chrome in /Applications.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BUILD = os.path.join(HERE, "build_dossier.py")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PRINT_CSS = r"""
<style media="print">
@page {
  size: A4;
  margin: 15mm 14mm 17mm 14mm;
  @bottom-center {
    content: "Dossier del preamplificatore di linea · " counter(page) " / " counter(pages);
    font: 8pt "IBM Plex Sans", Helvetica, Arial, sans-serif; color: #666;
  }
}
html, body { background: #fff !important; }
body { font-size: 10pt; line-height: 1.42; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.wrap { max-width: none !important; padding: 0 !important; margin: 0 !important; }
p, ul, .col, .lede, .note, .meta { max-width: none !important; }
h1 { font-size: 22pt; margin-top: 0; }
h2 { break-after: avoid; page-break-after: avoid; margin-top: 18pt; }
h3 { break-after: avoid; page-break-after: avoid; }
h2#s1, h2#s13, h2#spsu { break-before: page; page-break-before: always; }
p.prov { break-after: avoid; }
.tablewrap { overflow: visible !important; margin: 8pt 0; }
table { font-size: 7.9pt; width: 100%; table-layout: auto; }
th, td { padding: 3pt 4pt !important; white-space: normal !important;
         overflow-wrap: normal; word-break: normal; hyphens: none; }
code { white-space: normal !important; }
pre { white-space: pre-wrap !important; }
tr, td, th { break-inside: avoid; page-break-inside: avoid; }
thead { display: table-header-group; }
.plate { overflow: visible !important; break-inside: avoid; page-break-inside: avoid;
         padding: 4pt; margin: 10pt 0; }
.plate svg, .plate img { max-width: 100% !important; max-height: 235mm; height: auto; }
.synopsis div, .note { break-inside: avoid; page-break-inside: avoid; }
nav.toc { break-after: page; page-break-after: always; }
a { color: inherit; text-decoration: none; }
</style>
"""


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".pdf"):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    out = os.path.abspath(sys.argv[1])
    if os.path.commonpath([out, REPO]) == REPO:
        print(f"RIFIUTATO: {out} sta dentro il repository. Il PDF e' una stampa, non una "
              "seconda fonte di verita': scrivilo altrove.", file=sys.stderr)
        return 1
    if not os.path.exists(CHROME):
        print(f"RIFIUTATO: manca {CHROME}", file=sys.stderr)
        return 1
    tmp = tempfile.mkdtemp(prefix="dossier_a4_")
    page = os.path.join(tmp, "dossier.html")
    r = subprocess.run([sys.executable, BUILD, "--standalone", page], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr, file=sys.stderr)
        print("RIFIUTATO: build_dossier.py non passa, niente da stampare.", file=sys.stderr)
        return 1
    text = open(page, encoding="utf-8").read()
    if '<meta charset="utf-8">' not in text:
        print("RIFIUTATO: la pagina non ha l'intestazione attesa", file=sys.stderr)
        return 1
    # il tema chiaro, qualunque cosa dica il sistema
    text = '<html data-theme="light">\n' + text.replace(
        '<meta charset="utf-8">', '<meta charset="utf-8">' + PRINT_CSS, 1)
    printable = os.path.join(tmp, "dossier_stampa.html")
    with open(printable, "w", encoding="utf-8") as f:
        f.write(text)
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--run-all-compositor-stages-before-draw", "--virtual-time-budget=15000",
                        f"--print-to-pdf={out}", "file://" + printable],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not os.path.exists(out) or os.path.getsize(out) == 0:
        print(r.stderr[-600:], file=sys.stderr)
        print("RIFIUTATO: Chrome non ha scritto il PDF", file=sys.stderr)
        return 1
    print(f"scritto {out} ({os.path.getsize(out)} byte), dalla pagina generata ora")
    return 0


if __name__ == "__main__":
    sys.exit(main())
