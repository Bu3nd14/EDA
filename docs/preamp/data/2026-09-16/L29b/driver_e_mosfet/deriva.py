src = open("/Users/roberto/.claude/jobs/c42646c7/tmp/vom/VOM1271.lib", newline="").read().replace("\r\n", "\n")
a = "D2 +Iout -Iout PD n=13"
b = "D2 +Iout -Iout PD13"
assert src.count(a) == 1
src = src.replace(a, b)
m = ".model PD D(IS=8.377E-12 N=1.7321 RS=16 IKF=9)"
assert src.count(m) == 1
src = src.replace(m, m + "\n* L29b (ngspice): 13 celle in serie di PD = un diodo con N x 13 e RS x 13\n.model PD13 D(IS=8.377E-12 N=22.5173 RS=208 IKF=9)")
head = """* vom1271.lib - Vishay VOM1271, driver fotovoltaico per MOSFET con spegnimento rapido.
* VENDOR_DERIVED: copia di VOM1271.lib dentro
*   vendor/optocoupler/vishay/VOM1271/spicemodelvom1271.zip (zip intatto)
* con UNA modifica per ngspice, e nient'altro: vedi vom1271.provenance.json.
*   originale:  D2 +Iout -Iout PD n=13
*   qui:        D2 +Iout -Iout PD13, .model PD13 = PD con N x 13 e RS x 13
* In LTspice `n` sull'istanza del diodo e' un moltiplicatore SERIE; ngspice
* non lo accetta ("unknown parameter (n)"). Controllo della lettura: Voc =
* 13 * N * Vt * ln(Isc/IS) = 13 * 1,7321 * 25,85 mV * ln(15e-6/8,377e-12)
* = 8,38 V, contro 8,4 V tipici del datasheet a IF = 10 mA.
*
"""
open("/Users/roberto/EDA/.claude/worktrees/L29b/models/optocoupler/vom1271.lib", "w").write(head + src)
p = "/Users/roberto/EDA/.claude/worktrees/L29b/models/optocoupler/vom1271.lib"
s = open(p).read()
assert s.count("\n.backanno\n") == 1
s = s.replace("\n.backanno\n", "\n* .backanno   (L29b: direttiva di sola annotazione LTspice, ngspice la rifiuta)\n")
s = s.replace("* con UNA modifica per ngspice, e nient'altro", "* con DUE modifiche per ngspice, e nient'altro")
s = s.replace("*   qui:        D2 +Iout -Iout PD13, .model PD13 = PD con N x 13 e RS x 13\n",
              "*   qui:        D2 +Iout -Iout PD13, .model PD13 = PD con N x 13 e RS x 13\n*   e `.backanno` (annotazione LTspice, nessun effetto elettrico) commentata\n")
open(p, "w").write(s)
