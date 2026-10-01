import os
import shutil
import sys
sys.path.insert(0, "/Users/roberto/EDA/.claude/worktrees/L44/scripts")
import validate_models as vm

R = "/Users/roberto/EDA/.claude/worktrees/L44/"
T = "/Users/roberto/.claude/jobs/e965a52e/tmp/"
casi = {
    "senza_riga": (R + "vendor/bjt_npn/diodes_inc/MMBT5551/MMBT5551.spice.txt", "bjt_npn/mmbt5551.lib"),
    "mje_kf0": (R + "vendor/bjt_npn/onsemi/MJE15032/mje15032.lib", "bjt_npn/mje15032.lib"),
}
for nome, (src, rel) in casi.items():
    p = T + nome + ".lib"
    shutil.copy(src, p)
    print(nome, vm.run_recipe(rel, "_sab_%s.cir" % nome, lambda: vm.tb_flicker(p, rel)))
# KF raddoppiato
p = T + "kf2.lib"
open(p, "wb").write(open(R + "models/bjt_npn/mmbt5551.lib", "rb").read().replace(b"+ KF=1e-13 AF=1.4", b"+ KF=2e-13 AF=1.4"))
print("kf2", vm.run_recipe("bjt_npn/mmbt5551.lib", "_sab_kf2.cir", lambda: vm.tb_flicker(p, "bjt_npn/mmbt5551.lib")))
