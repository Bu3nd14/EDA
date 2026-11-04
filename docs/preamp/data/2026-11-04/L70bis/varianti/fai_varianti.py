#!/usr/bin/env python3
"""L70: the three variants of circuits/preamp/psu.py, as COPIES next to this script (the source is
not touched while they are studied):

  s2   - the mains detector out (R510, R554, R511, Q504, R512, R555, C518, U506 channel A; its timer
         copy U513 channel D with R569, D533, D534, D535). The rail supervisor (U505) and the
         VRELAY_REG supervisor (U506 channel B) stay.
  s1   - the latch after a rail fault out (U515 channels C and D, R580, C552, D541, R581, C553, R585,
         R582, Q513, R583, C554, Q514, R584, C555; D534 and D535, which only fed AT_F / AT_T2S from
         the detector), and one fuse per leg of T1's secondary: F502 in T1_SEC_A, F503 in T1_SEC_B,
         between the harness J513 and the bridge D501.
  s1s2 - both.

An unused comparator channel gets + on VREF and - on RET: its open-drain output stays off. Its
output goes to a net of its own (NC_<ref>_<ch>), nothing else on it.
Every edit is an exact string replacement that must match ONCE: a source that moved refuses.

    /usr/bin/python3 -I fai_varianti.py
writes psu_<v>.py here; the netlists come from netlist.sh (the venv's SKiDL).
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = QUI
for _ in range(6):
    REPO = os.path.dirname(REPO)
SRC = os.path.join(REPO, "circuits", "preamp", "psu.py")


def via(testo, vecchio, nuovo=""):
    n = testo.count(vecchio)
    if n != 1:
        raise SystemExit("RIFIUTATO: %r compare %d volte" % (vecchio[:70], n))
    return testo.replace(vecchio, nuovo)


def righe_via(testo, *frammenti):
    """Removes each whole line that contains the fragment (exactly one line each)."""
    for f in frammenti:
        r = [ln for ln in testo.split("\n") if f in ln]
        if len(r) != 1:
            raise SystemExit("RIFIUTATO: %r in %d righe" % (f, len(r)))
        testo = testo.replace(r[0] + "\n", "", 1)
    return testo


def s2(t):
    t = via(t, '''    MB, MD = Net("MD_B"), Net("MD")
''')
    t = righe_via(t, 'MB_R = Net("MD_B_R")', 'res("11k", "R510"', 'res("11k", "R554"',
                  'res("4.7k", "R511"', 'qd = part("Transistor_BJT", "BC847", "BC847", "Q504"',
                  'qd[1] += MB', 'qd[2] += RET', 'qd[3] += MD', 'MD_R = Net("MD_R")',
                  'res(R_MD_HALF, "R512"', 'res(R_MD_HALF, "R555"', 'cap(C_MD, "C518"')
    t = via(t, '''    cmp2["3"] += VREF      # A +
    cmp2["2"] += MD        # A -: out LOW when MD > VREF (no mains)
    cmp2["1"] += MUTE_G
''', '''    # L70 (S2): channel A unused - the mains detector is out
    cmp2["3"] += VREF      # A +
    cmp2["2"] += RET       # A -
    cmp2["1"] += Net("NC_U506_A")
''')
    t = via(t, "                  (VREF, MD, AT_MD)))         # no half-wave for ~15 ms",
            '                  (VREF, RET, Net("NC_U513_D"))))   # L70 (S2): unused')
    t = righe_via(t, 'res("100k", "R569", V5, AT_MD)', 'diode("BAT54", "D533", AT_PG, AT_MD)')
    t = righe_via(t, 'diode("BAS416", "D534", AT_F, AT_MD)', 'diode("BAS416", "D535", AT_T2S, AT_MD)')
    return t


def s1(t):
    if 'diode("BAS416", "D534", AT_F, AT_MD)' in t:
        t = righe_via(t, 'diode("BAS416", "D534", AT_F, AT_MD)', 'diode("BAS416", "D535", AT_T2S, AT_MD)')
    t = via(t, '''                  (AT_T2S, VREF, AT_F),       # not armed
                  (VREF, AT_PG, AT_F)))       # power good
''', '''                  (VREF, RET, Net("NC_U515_C")),   # L70 (S1): unused
                  (VREF, RET, Net("NC_U515_D")))) # L70 (S1): unused
''')
    t = righe_via(t, 'res("2.7M", "R580", AT_ON, AT_T2S)', 'cap("1u", "C552", AT_T2S, RET',
                  'diode("BAS416", "D541", AT_T2S, AT_ON)', 'res("100k", "R581", V5, AT_F)',
                  'cap("330n", "C553", AT_F, RET', 'res("33k", "R585", AT_F, RET)',
                  'res("47k", "R582", AT_F, AT_BN)')
    t = via(t, '''    q = part("Transistor_BJT", "BC847", "BC847", "Q513", FP_SOT23)
    q[1] += AT_BN                  # B
    q[2] += RET                    # E
    q[3] += AT_BP                  # C
    res("100k", "R583", AT_BN, RET)
    cap("1n", "C554", AT_BN, RET)
    q = part("Transistor_BJT", "BC857", "BC857", "Q514", FP_SOT23)
    q[1] += AT_BP                  # B
    q[2] += AT_ON                  # E
    q[3] += AT_BN                  # C
    res("100k", "R584", AT_ON, AT_BP)
    cap("1n", "C555", AT_ON, AT_BP)
''', "    # L70 (S1): the latch is out\n")
    t = via(t, '''    br[2] += T1A
    br[3] += T1B
''', '''    # L70 (S1): one fuse per leg of T1's secondary, between the harness and the bridge
    T1AF, T1BF = Net("T1_SEC_AF"), Net("T1_SEC_BF")
    for fref, a, b in (("F502", T1A, T1AF), ("F503", T1B, T1BF)):
        f = part("Device", "Fuse", "T1 secondary (T, L70)", fref, FP_FUSE)
        f[1] += a
        f[2] += b
    br[2] += T1AF
    br[3] += T1BF
''')
    return t


def dc(t):
    """s1s2dc (added in L70 after the first runs: the fuses of T1's secondary do not open with the
    regulator's pin shorted, 2.9-3.6 A in the leg): also one fuse per rail on the DC side, F504 between
    the reservoir C501 (RAW_P) and R550, F505 between R551 and the reservoir C502 (RAW_M)."""
    t = via(t, '''    r = part("Device", "R", "4.7", "R550", FP_R_2W)
    r[1] += RAW_P
''', '''    # L70 (s1s2dc): F504, the + rail's DC fuse, between the reservoir and R550
    RAW_PF = Net("RAW_PF")
    f = part("Device", "Fuse", "+ rail DC (T, L70)", "F504", FP_FUSE)
    f[1] += RAW_P
    f[2] += RAW_PF
    r = part("Device", "R", "4.7", "R550", FP_R_2W)
    r[1] += RAW_PF
''')
    t = via(t, '''    r = part("Device", "R", "4.7", "R551", FP_R_2W)
    r[1] += RAW_MR
    r[2] += RAW_M
''', '''    # L70 (s1s2dc): F505, the - rail's DC fuse, between R551 and the reservoir
    RAW_MF = Net("RAW_MF")
    r = part("Device", "R", "4.7", "R551", FP_R_2W)
    r[1] += RAW_MR
    r[2] += RAW_MF
    f = part("Device", "Fuse", "- rail DC (T, L70)", "F505", FP_FUSE)
    f[1] += RAW_MF
    f[2] += RAW_M
''')
    return t


def main():
    base = open(SRC).read()
    # the copy lives 6 levels below the repo: REPO from the copy would be wrong
    base = via(base, "REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
               "REPO = %r  # L70: the copy's REPO, written by fai_varianti.py" % REPO)
    base = via(base, "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))",
               "sys.path.insert(0, %r)" % os.path.join(REPO, "circuits", "preamp"))
    for nome, f in (("s2", s2), ("s1", s1), ("s1s2", lambda t: s1(s2(t))),
                    ("s1s2dc", lambda t: dc(s1(s2(t))))):
        with open(os.path.join(QUI, "psu_%s.py" % nome), "w") as fh:
            fh.write(f(base))
        print("psu_%s.py" % nome)


main()
