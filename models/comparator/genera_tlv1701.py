#!/usr/bin/python3
"""L54b2: the ngspice derivative of TI's TLV1701 transient model (the TLV1704's die, one channel).

Reads the frozen vendor file and writes the derivative; nothing is edited by hand. The patches,
each counted against the vendor file (a different count refuses, so a new vendor file is read
again instead of patched blind):
  1. CRLF -> LF (limitations #39).
  2. "TC=0,0" on R and C: PSpice's positional tempco, all 0 -> dropped, a no-op.
  3. ".MODEL x VSWITCH Roff Ron Voff Von" and its "S_x" instances -> the XSPICE "aswitch" with
     the same four values (the instance "A_x %vd(control) %gd(switched) x"): PSpice's switch
     moves smoothly between Voff and Von, in either order, and so does aswitch. ngspice's SW
     has a hysteresis instead: the translation of L41a (VT = (Von + Voff) / 2, VH = (Von - Voff)
     / 2) makes it as wide as the control swing, and with Von < Voff (four of the five here) it
     does not invert the switch at all (data/2026-10-28/L54b2/prova/tb_sw.cir); with VH = 0 and
     RON / ROFF swapped the sense is right but the output chatters on a slow input
     (prova/tb_tlv1701_solo.cir), which the compatibility mode psa does not do.
  4. IF(c, a, b) -> ((c) ? (a) : (b)); nested IFs are rewritten from the outside in.
  5. "&" and "|" in the expressions -> "&&" and "||".
  6. "2.5V" (a unit suffix in an expression of IS_SET, never instantiated) -> 2.5.
  7. A named variant TLV1701_OC appended beside the faithful TLV1701 (see the comment there).

usage: genera_tlv1701.py <vendor tlv1701.lib> <out .lib>
"""
import re
import sys

src, out = sys.argv[1], sys.argv[2]
raw = open(src, newline="").read()
text = raw.replace("\r\n", "\n").replace("\r", "\n")

COUNTS = {}


def count(name, n, expected):
    COUNTS[name] = n
    if n != expected:
        raise SystemExit("RIFIUTATO: %s: %d nel file del costruttore, attesi %d" % (name, n, expected))


text, n = re.subn(r"\s+TC=0,0", "", text)
count("TC=0,0", n, 16)

SUFFIX = {"T": 1e12, "G": 1e9, "MEG": 1e6, "K": 1e3, "M": 1e-3, "U": 1e-6, "N": 1e-9, "P": 1e-12,
          "F": 1e-15, "": 1.0}


def spice_value(s):
    m = re.fullmatch(r"([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)(MEG|[TGKMUNPF]?)", s.upper())
    if m is None:
        raise SystemExit("RIFIUTATO: valore non letto %r" % s)
    return float(m.group(1)) * SUFFIX[m.group(2)]


INVERTED = []


def vswitch(m):
    name, body = m.group(1), m.group(2)
    kv = dict((k.upper(), spice_value(v)) for k, v in re.findall(r"(\w+)\s*=\s*([-+0-9.eE]+[A-Za-z]*)", body))
    if kv["VON"] < kv["VOFF"]:
        INVERTED.append(name)
    # XSPICE aswitch: the resistance moves smoothly (log) from r_off at cntl_off to r_on at
    # cntl_on, in either order, as PSpice's VSWITCH does
    return (".MODEL %s aswitch(cntl_off=%g cntl_on=%g r_off=%g r_on=%g log=TRUE)"
            % (name, kv["VOFF"], kv["VON"], kv["ROFF"], kv["RON"]))


text, n = re.subn(r"\.MODEL\s+(\S+)\s+VSWITCH\s*\(?([^)\n]*)\)?", vswitch, text)
count("VSWITCH", n, 5)
count("VSWITCH invertiti", len(INVERTED), 4)

# the instances: "S_x n+ n- nc+ nc- model" -> "A_x %vd(nc+ nc-) %gd(n+ n-) model"
text, n = re.subn(r"(?m)^S_(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$",
                  r"A_\1 %vd(\4 \5) %gd(\2 \3) \6", text)
count("istanze S", n, 5)


def args_at(s, i):
    # s[i] is the "(" after IF: return (end index past ")", [top-level arguments])
    depth, start, parts = 0, i + 1, []
    for j in range(i, len(s)):
        c = s[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                parts.append(s[start:j])
                return j + 1, parts
        elif c == "," and depth == 1:
            parts.append(s[start:j])
            start = j + 1
    raise SystemExit("RIFIUTATO: IF senza parentesi chiusa")


# only in expressions: a "{ ... }" that is not on a comment line
def in_braces(fn):
    def sub(line):
        if line.startswith("*"):
            return line
        return re.sub(r"\{[^{}]*\}", lambda m: fn(m.group(0)), line)
    return "\n".join(sub(x) for x in text.split("\n"))


n_if = [0]


def ternary(expr):
    while True:
        m = re.search(r"\bIF\s*\(", expr)
        if m is None:
            return expr
        end, parts = args_at(expr, m.end() - 1)
        if len(parts) != 3:
            raise SystemExit("RIFIUTATO: IF con %d argomenti" % len(parts))
        c, a, b = (p.strip() for p in parts)
        expr = expr[:m.start()] + "((%s) ? (%s) : (%s))" % (c, a, b) + expr[end:]
        n_if[0] += 1


text = in_braces(ternary)
count("IF", n_if[0], 23)

n_and = [0]
n_or = [0]


def logic(expr):
    expr, a = re.subn(r"(?<!&)&(?!&)", "&&", expr)
    expr, o = re.subn(r"(?<!\|)\|(?!\|)", "||", expr)
    n_and[0] += a
    n_or[0] += o
    return expr


text = in_braces(logic)
count("&", n_and[0], 5)
count("|", n_or[0], 3)

text, n = re.subn(r"\b2\.5V\b", "2.5", text)
count("2.5V", n, 1)

# 7. A second, NAMED variant beside the faithful TLV1701 (which stays as the vendor wrote it):
#    TLV1701_OC, two changes, both from the datasheet and not from the model:
#    a. the input-range check (INPUTRANGE) no longer floats the output: SBOS589D §8.3.1 and
#       fig. 18, "designed to prevent phase inversion when the input pins exceed the supply
#       voltage" - the part keeps comparing (its inputs are diode-clamped to the rails, fn. 2 of
#       the absolute maxima, not modelled here or in CMPOD);
#    b. out of the supply window (2.19-37.1 V) the output is OPEN, not "floating at mid supply"
#       through 1 ohm from an ideal source: an open-collector output cannot source current, and
#       the datasheet does not say what it does below 2.2 V. Open is what the bench's CMPOD does
#       below 2 V. With the faithful model the bench cannot get V5 through 2.19 V
#       (prova/tb_tlv1701_rampa.cir: stuck at 2.196 ms, 1.4 GB and growing).
def block(name):
    m = re.search(r"(?ms)^\.SUBCKT %s .*?^\.ENDS\s*$" % re.escape(name), text)
    if m is None:
        raise SystemExit("RIFIUTATO: sottocircuito %s non trovato" % name)
    return m.group(0)


#    c. the supply window itself (Supply_Enable: a hard IF at 2.19 V, no hysteresis) is not used:
#       with the output open below it the loop "enabled -> the output sinks 0.5 mA -> V5 drops
#       through its source resistance -> disabled" has no fixed point and ngspice stops at
#       2.1907 ms all the same (prova/tb_tlv1701_rampa_oc.cir, 1.5 GB). In its place CMPOD's own
#       supply behaviour, smooth: the output behind a conductance of 1 S above ~2.1 V of supply
#       and ~0 below ~1.9 V (CMPOD's tanh at 2 V, 0.1 V wide). Written as a B source: an XSPICE
#       aswitch in the same place put the step at ~10 ns whenever the output was open (422 277
#       points in 10 ms against 2 269, prova/tb_tlv1701_solo_oc.cir);
#    d. the 55 uA of I_IS only with the supply up, as CMPOD (> 1 V), not from a dead V5
#       (limitations #73).
#    So the comparison with CMPOD on the bench is of what the model adds - the thresholds and the
#    offset, the delays, the output stage, Iq - with the same behaviour where the datasheet says
#    nothing. The ports are renamed in the variant (INP INN VP VM OUT): "V(V+,V-)" is not an
#    expression ngspice reads.
top, stage = block("TLV1701"), block("Output_Stage")
top_oc, n1 = re.subn(r"^\.SUBCKT TLV1701 IN\+ IN- V\+ V- OUT", ".SUBCKT TLV1701_OC INP INN VP VM OUT",
                     top, flags=re.M)
REN = {"IN+": "INP", "IN-": "INN", "V+": "VP", "V-": "VM"}
top_oc = "\n".join(" ".join(REN.get(t, t) for t in x.split()) if not x.startswith(".SUBCKT") else x
                   for x in top_oc.split("\n"))
top_oc, n2 = re.subn(r"(?m)^X_U5 N21237 INRANGE 0 (.*) OUT Output_Stage$",
                     r"X_U5 N21237 0 0 \1 OUTI Output_Stage_OC", top_oc)
top_oc, n3 = re.subn(r"(?m)^X_U7 N21237 0 V\+_BUFFER V-_BUFFER Supply_Enable$",
                     "V_ENOC N21237 0 0\n"
                     "B_UVOC OUTI OUT I = V(OUTI,OUT)*(1e-12 + 0.5*(1+tanh((V(VP,VM)-2)/0.1)))",
                     top_oc)
top_oc, n4 = re.subn(r"(?m)^I_IS N843683 VM DC 55u$",
                     "B_ISOC N843683 VM I = 55u*0.5*(1+tanh((V(VP,VM)-1)/0.05))", top_oc)
stage_oc, n5 = re.subn(r"^\.SUBCKT Output_Stage ", ".SUBCKT Output_Stage_OC ", stage, flags=re.M)
stage_oc, n6 = re.subn(r"(?m)^X_SMID .*\n", "", stage_oc)
#    e. the input decision (HPA_COMPHYS: EOUT = IF(INP > INN, VDD, VSS)) is a step: on the bench,
#       with an input moving slowly through the reference while the timer powers up, ngspice stops
#       on it ("Timestep too small ... xu515d.x1.x_u3.eout", 42.8 ms into perdita,
#       seq/costruttore/perdita). In the variant it is a tanh 0.1 mV wide - a finite gain, under
#       the model's own 0.4 mV of offset and ten times sharper than CMPOD's 1 mV. VH is 0 in this
#       model (VHYS on node 0), so INNNEW is INN either way.
comp = block("HPA_COMPHYS")
comp_oc, n7 = re.subn(r"^\.SUBCKT HPA_COMPHYS ", ".SUBCKT HPA_COMPHYS_OC ", comp, flags=re.M)
comp_oc, n8 = re.subn(r"(?m)^EOUT OUT 0 VALUE = .*$",
                      "EOUT OUT 0 VALUE = { V(VSS) + (V(VDD)-V(VSS))*0.5*(1+tanh((V(INP)-V(INNNEW))/1e-4)) }",
                      comp_oc)
top_oc, n9 = re.subn(r"(?m)^(X_U3 .* 0) HPA_COMPHYS$", r"\1 HPA_COMPHYS_OC", top_oc)
#    f. the decision held at VSS while the supply is under ~1.5 V (tanh at 1.5 V, 0.1 V wide; 1
#       above 2.1 V, where (c) lets the output act): with the tanh of (e) alone ngspice still
#       stopped 42.757 ms into perdita, U515D flipping with V5 at ~1 mV, every node of the model
#       at the level of the noise (prova/diag: V5 86 uV -> 0.54 mV, IN- crossing IN+ at 0.37 mV).
#       Nothing the circuit sees depends on it: the output is open there. A 10 ns pole on the
#       decision (C1 10 nF) did not help and is not used.
comp_oc, n10 = re.subn(r"\*0\.5\*\(1\+tanh\(\(V\(INP\)-V\(INNNEW\)\)/1e-4\)\) \}",
                       "*0.5*(1+tanh((V(INP)-V(INNNEW))/1e-4))*0.5*(1+tanh((V(VDD,VSS)-1.5)/0.1)) }",
                       comp_oc)
#    g. the output stage's level shifter (DIGLEVSHIFT: IF(V(1) < 1, V+ - 1, V+), the control of
#       the output switch) as a tanh 50 mV wide around the same 1 V: with (f) ngspice stopped next
#       at 0.21 s of perdita on its branch (V_V1)
shift = block("DIGLEVSHIFT")
shift_oc, n11 = re.subn(r"^\.SUBCKT DIGLEVSHIFT ", ".SUBCKT DIGLEVSHIFT_OC ", shift, flags=re.M)
shift_oc, n12 = re.subn(r"(?m)^E1 3 0 VALUE = \{ \(\(V\(1\) < 1\) \? \(V\(VSS_NEW\)\) : \(V\(VDD_NEW\)\)\) \}$",
                        "E1 3 0 VALUE = { V(VSS_NEW) + (V(VDD_NEW)-V(VSS_NEW))*0.5*(1+tanh((V(1)-1)/0.05)) }",
                        shift_oc)
stage_oc, n13 = re.subn(r"(?m)^(X_U3 .*) DIGLEVSHIFT$", r"\1 DIGLEVSHIFT_OC", stage_oc)
count("variante OC", n1 + n2 + n3 + n4 + n5 + n6 + n7 + n8 + n9 + n10 + n11 + n12 + n13, 13)
stage_oc = stage_oc + "\n*$\n" + comp_oc + "\n*$\n" + shift_oc
variant = ("\n*$\n* --- TLV1701_OC: the named variant of genera_tlv1701.py, patch 7 (not TI's) ---\n"
           + top_oc + "\n*$\n" + stage_oc + "\n")

head = ("* ngspice derivative of TI's TLV1701 model, generated by models/comparator/genera_tlv1701.py\n"
        "* (L54b2) from vendor/comparator/ti/TLV1702/tlv1701.lib; do not edit, regenerate.\n")
open(out, "w").write(head + text + variant)
print("scritto %s: %s; invertiti %s" % (out, ", ".join("%s %d" % kv for kv in COUNTS.items()),
                                        " ".join(INVERTED)))
