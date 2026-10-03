"""L47b2a: copia un deck sostituendo @REPO@ con la radice del repo (quella di questo file).

Usage: python3 risolvi_repo.py <deck.cir> <out.cir>
E' il `sed "s|@REPO@|<repo>|g"` dei README di L29b2/L29c, scritto su file perche' nel
worktree i comandi con redirezione attorno agli script sono rifiutati.
"""
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
src, dst = sys.argv[1:3]
os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
text = open(src).read().replace("@REPO@", REPO)
open(dst, "w").write(text)
print("%s -> %s (@REPO@ = %s)" % (src, dst, REPO))
