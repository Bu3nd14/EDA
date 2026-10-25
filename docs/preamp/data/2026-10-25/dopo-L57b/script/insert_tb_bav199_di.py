#!/usr/bin/env python3
"""Dopo L57b, una volta: inserisce tb_bav199 (testo in argv[2]) in scripts/validate_models.py (argv[1])
prima di tb_bav199_fit e lo registra per diodes/bav199.lib. Rifiuta di girare due volte."""
import sys

path, snippet = sys.argv[1], sys.argv[2]
s = open(path).read()
assert "def tb_bav199(" not in s, "gia' inserito"
anchor = "def tb_bav199_fit(model_file):"
assert s.count(anchor) == 1
s = s.replace(anchor, open(snippet).read() + anchor)
reg_anchor = "    # L57b - BAV199 ESTIMATE from the datasheet, not the manufacturer's model.\n"
assert s.count(reg_anchor) == 1
s = s.replace(reg_anchor,
              "    # Dopo L57b - BAV199, Diodes Incorporated's model (the user's file).\n"
              '    reg["diodes/bav199.lib"] = lambda p: tb_bav199(p)\n'
              + reg_anchor)
open(path, "w").write(s)
print("inserito")
