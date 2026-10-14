#!/bin/zsh
# After L45d1: print the HTML of pdf_scelte.py to an A4 PDF with Chrome headless.
#   stampa_pdf.sh <in.html> <out.pdf>
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$2" "file://$1" 2>/dev/null
[[ -s "$2" ]] || { echo "PDF non scritto: $2" >&2; exit 1; }
echo "scritto $2"
