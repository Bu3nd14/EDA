#!/usr/bin/env python3
"""One-shot: insert tb_bav199_fit (text in argv[2]) into scripts/validate_models.py (argv[1])
before tb_opamp and register it.  Refuses to run twice."""
import sys

path, snippet = sys.argv[1], sys.argv[2]
s = open(path).read()
assert "tb_bav199_fit" not in s, "already inserted"
anchor = "def tb_opamp(model_file):"
assert s.count(anchor) == 1
s = s.replace(anchor, open(snippet).read() + anchor)
reg_anchor = '    reg["opamp/generic_opamp.lib"] = lambda p: tb_opamp(p)\n'
assert s.count(reg_anchor) == 1
s = s.replace(reg_anchor,
              '    # L57b - BAV199 ESTIMATE from the datasheet, not the manufacturer\'s model.\n'
              '    reg["diodes/bav199_fit.lib"] = lambda p: tb_bav199_fit(p)\n'
              + reg_anchor)
open(path, "w").write(s)
