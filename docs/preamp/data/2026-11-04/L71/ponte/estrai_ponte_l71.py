#!/usr/bin/env python3
"""L71 (NC-083): the bridge of L69b (estrai_ponte.py, here beside it, unchanged) for the sequences
with the front switch moved, into the NINE SLOTS of the V2 deck (--matrice l41c reads nine JSONs by
the names of L41c's cases: the names are labels, the deck is the same for every slot).

    /usr/bin/python3 -I estrai_ponte_l71.py <seq_dir> <out_dir> <posto>=<caso> [...]

writes <out_dir>/<posto>.json and <out_dir>/posti.csv (slot, case, window). It reuses
estrai_ponte.py's functions (leggi, pwl_di, primo, thresholds, refusals); what changes is WHERE the
window sits and FROM WHERE the contacts are searched, because the V2 bench models one state only:
the jack closed (MUSICA) from the start, one opening of the jack contact (t_jack) and one drop of
the gain relays (t_gain), never a re-closure. So, per family:

  spl_riacceso_<ms>, spl_sw3_<ms> (from MUSICA, the front off at TE):
      the window of spegnimento_l: T0 = TE - 1 s, t_ins = TE - 10 ms; contacts searched from TE.
  acc_spento_<ms> (from standby, the front on at TE and off at TE + ms):
      only if the jack closed after TE (t_on: VRELAY - MUTE_CMD >= 9.6 V, the G6K's must-operate,
      the EARLIEST closure); otherwise REFUSED - there is no path to the jack, and the run's
      n_su = 0 in an_l71.csv says so. t_ins = min(TE + ms, t_on) - 10 ms; T0 = max(t_ins - 1 s,
      TE + 0.9 s) (the soft start puts the rails at ~0.6 s: before TE + 0.9 s the bench's own
      operating point would be on rising rails); contacts searched from max(TE + ms, t_on) for the
      jack and from max(TE + ms, the gain's closure) for the gain. HYPOTHESIS, declared: in the
      bench the jack is closed from T0, i.e. the board has been in MUSICA since T0, while in the
      run it closed at t_on. The music's arrival itself is the arrival of accensione (judged on the
      supply side, stato_finale.py); the bench reads what the front's opening adds after t_ins.
  END of the window, every family: the first of the data's end, the event + 1.1 s (spegnimento_l's
      1.1 s), and 1 ms before the jack or the gain closes again after its opening (the bench
      cannot close them again; what comes after is the music coming back, judged on the supply
      side). The reference is estrai_ponte.py's: the same points up to t_ins, then held.
  RIENTRO (<posto>=R:<caso>, any family): the music coming BACK (the jack's last closure after TE,
      t_close through 9.6 V, the earliest). The V2 bench cannot close the jack, so here it keeps
      it closed for the whole window and moves nothing: no t_jack, no t_gain. T0 = t_close - 1 s,
      t_ins = t_close (A_ins reads from the instant the jack can connect), the end t_close + 0.5 s.
      The REFERENCE is not estrai_ponte.py's: the rails held at their value at T0 for the whole
      window (the settled MUSICA before the sequence). So A_ins reads, after the jack connects,
      everything the rails' movement BEFORE and after it leaves at the outputs - against the music
      coming back on rails that never moved. The relay's own closure is V2's rilascio geometry.
Solo stdlib.
"""
import csv
import json
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
_argv = sys.argv
sys.argv = [_argv[0], "--passata-unica", "--te", "3.0"]
sys.path.insert(0, QUI)
import estrai_ponte as EP  # noqa: E402
sys.argv = _argv
TE = EP.TE
assert EP.UNICA and TE == 3.0


def ultimo_su(t, cond, da):
    """the first sample >= da where cond becomes true (after being false), or None"""
    for k in range(1, len(t)):
        if t[k] >= da and cond(k) and not cond(k - 1):
            return t[k]
    return None


def caso(seq, out, posto, nome):
    rientro = nome.startswith("R:")
    nome = nome[2:] if rientro else nome
    d = os.path.join(seq, nome)
    if not os.path.exists(os.path.join(d, "ok.txt")):
        raise SystemExit("%s: nessun ok.txt di corri_an.sh - rifiutato" % nome)
    cir = os.path.join(d, "tb_psu_seq_%s_g1.cir" % os.path.basename(nome))
    if "--timer sorgente" not in open(cir).readline():
        raise SystemExit("%s: il deck non e' --timer sorgente - rifiutato" % nome)
    log = open(os.path.join(d, "tb_psu_seq_%s_g1.log" % os.path.basename(nome))).read().lower()
    bad = [w for w in EP.MALE if w in log]
    if bad:
        raise SystemExit("%s: il log ha %s - rifiutato" % (nome, bad))
    S = EP.leggi(os.path.join(d, "tb_psu_seq_%s_g1_out.txt" % os.path.basename(nome)))
    t, vr, mc, pc = S["time"], S["v(vrelay)"], S["v(mute_cmd)"], S["v(permit_cmd)"]
    jack_aperto = lambda k: vr[k] - mc[k] < EP.V_RIL            # noqa: E731
    jack_chiuso = lambda k: vr[k] - mc[k] >= EP.V_OP            # noqa: E731
    gain_giu = lambda k: vr[k] - pc[k] < EP.V_OP or vr[k] < EP.V_OP   # noqa: E731
    gain_su = lambda k: not gain_giu(k)                          # noqa: E731
    m = re.match(r"(spl_riacceso|spl_sw3|acc_spento|ins_ritorno|ril_ritorno)_([0-9p]+)$", os.path.basename(nome))
    if rientro and m:
        ch = [t[k] for k in range(1, len(t)) if t[k] >= TE and jack_chiuso(k) and not jack_chiuso(k - 1)]
        if not ch:
            raise SystemExit("%s: nessuna chiusura del jack dopo TE - nessun rientro (rifiutato)" % nome)
        t_ev, t_on = ch[-1], ch[-1]
        t0, t_ins = t_ev - EP.T_EVENTO_AUDIO, t_ev
        jack = gain = None
        fine_psu = min(t[-1], t_ev + 0.5)
    elif not m or m.group(1) in ("ins_ritorno", "ril_ritorno"):
        raise SystemExit("%s: famiglia non prevista dal ponte di L71 - rifiutato" % nome)
    ms = float(m.group(2).replace("p", ".")) * 1e-3
    if rientro:
        pass
    elif m.group(1) == "acc_spento":
        t_ev = TE + ms
        t_on = ultimo_su(t, jack_chiuso, TE)
        if t_on is None:
            raise SystemExit("%s: il jack non si chiude mai dopo TE - nessun percorso al jack, "
                             "nessun ponte (rifiutato)" % nome)
        g_on = ultimo_su(t, gain_su, TE)
        t_ins = min(t_ev, t_on) - 0.010
        t0 = max(t_ins - EP.T_EVENTO_AUDIO, TE + 0.9)
        da_j, da_g = max(t_ev, t_on), max(t_ev, g_on if g_on is not None else t_ev)
    else:
        t_ev, t_on = TE, None
        t_ins, t0 = TE - 0.010, TE - EP.T_EVENTO_AUDIO
        da_j = da_g = TE
    if not rientro:
        jack = EP.primo(t, jack_aperto, da_j)
        gain = EP.primo(t, gain_giu, da_g)
        fine_psu = min(t[-1], t_ev + 1.1)
    for x, cond in (() if rientro else ((jack, jack_chiuso), (gain, gain_su))):
        if x is not None:
            r = ultimo_su(t, cond, x)
            if r is not None:
                fine_psu = min(fine_psu, r - 0.001)
    jack = None if jack is None else jack + EP.T_RIL
    if jack is not None and jack > fine_psu:
        raise SystemExit("%s: il jack si apre dopo la fine della finestra" % nome)
    k0 = next(k for k in range(len(t)) if t[k] >= t0)
    k1 = max(k for k in range(len(t)) if t[k] <= fine_psu)
    tt = [x - t0 for x in t[k0:k1 + 1]]
    fine = tt[-1]
    res = {"caso": ("R:" if rientro else "") + nome, "posto": posto, "giro": 1, "sorgente": os.path.relpath(d, out), "T0_psu": t0,
           "t_ins": t_ins - t0, "t_fine": fine, "t_jack": None if jack is None else jack - t0,
           "t_gain": None if gain is None else gain - t0,
           "t_evento_psu": t_ev, "t_on_psu": t_on,
           "soglie": {"V_op": EP.V_OP, "V_ril": EP.V_RIL, "T_ril": EP.T_RIL}}
    for chiave, col in (("vpp", "v(vplus)"), ("vmm", "v(vminus)")):
        y = S[col][k0:k1 + 1]
        pts, tol, worst = EP.pwl_di(tt, y, "rail")
        res[chiave] = {"punti": pts, "tolleranza": tol, "scarto_max": worst, "n": len(pts)}
        ti = res["t_ins"]
        a = max(k for k in range(len(pts)) if pts[k][0] <= ti)
        (ta, ya), (tb, yb) = pts[a], pts[min(a + 1, len(pts) - 1)]
        yi = ya if tb == ta else ya + (yb - ya) * (ti - ta) / (tb - ta)
        pts_r = pts[:a + 1] + ([(ti, yi)] if ti > ta else []) + [(fine, yi)]
        if rientro:
            pts_r = [(0.0, pts[0][1]), (fine, pts[0][1])]
        res[chiave + "_rif"] = {"punti": pts_r, "n": len(pts_r)}
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, posto + ".json"), "w"), indent=1)
    print("%-16s <- %-18s T0 %.4f  t_ins %.4f  jack %s  guadagno %s  fine %.3f" % (
        posto, nome, t0, res["t_ins"], "-" if res["t_jack"] is None else "%.5f" % res["t_jack"],
        "-" if res["t_gain"] is None else "%.5f" % res["t_gain"], fine))
    return [posto, res["caso"], "%.6f" % t0, "%.6f" % res["t_ins"], "%.6f" % fine,
            "" if res["t_jack"] is None else "%.6f" % res["t_jack"],
            "" if res["t_gain"] is None else "%.6f" % res["t_gain"]]


if __name__ == "__main__":
    seq, out = sys.argv[1], sys.argv[2]
    righe = [caso(seq, out, *x.split("=")) for x in sys.argv[3:]]
    with open(os.path.join(out, "posti.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["posto", "caso", "T0_psu", "t_ins", "t_fine", "t_jack", "t_gain"])
        w.writerows(righe)
