#!/usr/bin/env python3
"""L58b: what each latent row SHOWS, from the waveforms of lista_l58b.txt (seq/<etichetta>/<caso>/).

Per case (TE = 3.0 s):
  standby at rest   the mean over a window with the front OFF: accensione 2.5 .. 3.0 s (before the
                    front goes on), spegnimento_l the last 0.2 s (TE + 0.9 .. TE + 1.1)
     vrelay_sb      VRELAY at the audio board (J1 pin 7): the front LEDs' supply (preamp_audio.py J5 /
                    J6 / J7 through 4.99 kOhm)
     k501_sb        K501's contact (k501_f > 0.5: the toroid ON)
     vplus_sb / vminus_sb   the audio rails
     mute_en_sb / permit_en_sb   the jack's / the permissive's coils energised (VRELAY - drain > 6 V)
     i_led_mA       the current of ONE front LED from VRELAY at standby, (VRELAY - 2.0 V) / 4.99 kOhm
                    (a red LED's ~2 V: an ASSUMPTION of the census, the panel LEDs are not chosen);
                    0 when VRELAY < 2 V
  after TE (accensione)
     t_coil_ms      the jack's coils energised for the first time after TE (Q501's rows: the jack
                    connected), in ms from TE
     t_rail_ms      V+ above 13.5 V and V- below -13.5 V for the first time after TE
     t_mus_ms       analizza_mc.py's (the last energising), for the base
  inserimento: mute_en_fine  the jack's coils still energised at the end (the mute did not insert)
Solo stdlib. /usr/bin/python3 -I censimento.py <out.csv> <seq_dir>/<etichetta>/<caso> [...]
"""
import csv
import os
import sys

TE = 3.0
R_LED, VF_LED = 4990.0, 2.0


def leggi(path):
    with open(path) as f:
        nomi = f.readline().split()
        righe = [list(map(float, r.split())) for r in f if r.strip()]
    return {n: [r[k] for r in righe] for k, n in enumerate(nomi)}


def media(t, y, a, b):
    v = [y[k] for k in range(len(t)) if a <= t[k] <= b]
    return sum(v) / len(v) if v else None


def primo(t, cond, da):
    for k in range(len(t)):
        if t[k] >= da and cond(k):
            return t[k]
    return None


def caso(d):
    nome = os.path.basename(d.rstrip("/"))
    out = [f for f in os.listdir(d) if f.endswith("_out.txt")]
    assert len(out) == 1, (d, out)
    w = leggi(os.path.join(d, out[0]))
    t = w["time"]
    vr, mc, pc = w["v(vrelay)"], w["v(mute_cmd)"], w["v(permit_cmd)"]
    if nome.startswith("spegnimento") or nome.endswith("_spls"):
        a, b = TE + 0.9, t[-1]
    else:
        a, b = 2.5, TE - 1e-4
    x = {"caso": os.path.basename(os.path.dirname(d.rstrip("/"))) + "/" + nome,
         "finestra_s": "%.2f-%.2f" % (a, b)}
    x["vrelay_sb"] = media(t, vr, a, b)
    x["k501_sb"] = media(t, w["v(k501_f)"], a, b)
    x["vplus_sb"] = media(t, w["v(vplus)"], a, b)
    x["vminus_sb"] = media(t, w["v(vminus)"], a, b)
    dm = [vr[k] - mc[k] for k in range(len(t))]
    dp = [vr[k] - pc[k] for k in range(len(t))]
    x["mute_en_sb"] = int(media(t, dm, a, b) > 6)
    x["permit_en_sb"] = int(media(t, dp, a, b) > 6)
    x["i_led_mA"] = max(0.0, (x["vrelay_sb"] - VF_LED) / R_LED * 1e3)
    if nome.startswith("accensione") or nome.endswith("_accs"):
        tc = primo(t, lambda k: dm[k] > 6, TE)
        tr = primo(t, lambda k: w["v(vplus)"][k] > 13.5 and w["v(vminus)"][k] < -13.5, TE)
        x["t_coil_ms"] = None if tc is None else round((tc - TE) * 1e3, 1)
        x["t_rail_ms"] = None if tr is None else round((tr - TE) * 1e3, 1)
        # the rails at the instant the jack's coils energise
        if tc is not None:
            k = t.index(tc)
            x["vplus_coil"], x["vminus_coil"] = w["v(vplus)"][k], w["v(vminus)"][k]
    if nome.startswith("inserimento") or nome.endswith("_inss"):
        x["mute_en_fine"] = int(dm[-1] > 6)
    for k, v in list(x.items()):
        if isinstance(v, float):
            x[k] = round(v, 4)
    return x


CAMPI = ["caso", "finestra_s", "vrelay_sb", "i_led_mA", "k501_sb", "vplus_sb", "vminus_sb", "mute_en_sb",
         "permit_en_sb", "t_coil_ms", "t_rail_ms", "vplus_coil", "vminus_coil", "mute_en_fine"]


def main():
    out, dirs = sys.argv[1], sys.argv[2:]
    rs = [caso(d) for d in dirs]
    with open(out, "w", newline="") as f:
        wr = csv.DictWriter(f, CAMPI)
        wr.writeheader()
        for r in rs:
            wr.writerow(r)
    for r in rs:
        print(",".join(str(r.get(c, "")) for c in CAMPI))


main()
