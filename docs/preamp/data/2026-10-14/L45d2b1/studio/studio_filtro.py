"""Numeric study: n-pole critically damped low-pass (n equal RC poles, tau each),
|y| against a threshold. For each (n, tau, vth): detection time of a DC step of
amplitude Vx, and peak |y| for the music test set at amplitude A."""
import math

DT = 1e-4


def run(n, tau, sig, T):
    y = [0.0] * n
    a = DT / tau
    pk = 0.0
    t = 0.0
    trace = []
    while t < T:
        x = sig(t)
        for i in range(n):
            y[i] += a * ((x if i == 0 else y[i - 1]) - y[i])
        pk = max(pk, abs(y[-1]))
        trace.append(y[-1])
        t += DT
    return pk, trace


def t_det(n, tau, vth, vx, T=0.5):
    _, tr = run(n, tau, lambda t: vx, T)
    for i, v in enumerate(tr):
        if abs(v) >= vth:
            return i * DT
    return float("inf")


def clip(v, c):
    return max(-c, min(c, v))


def music(A, kind, f=20.0):
    w = 2 * math.pi * f
    if kind == "sin":
        return lambda t: A * math.sin(w * t)
    if kind == "cos":
        return lambda t: A * math.cos(w * t)
    if kind == "quadra":          # sine driven 3x into a clip at A
        return lambda t: clip(3 * A * math.sin(w * t), A)
    if kind == "burst1":          # one full cycle, then silence
        return lambda t: A * math.sin(w * t) if t < 1 / f else 0.0
    if kind == "mezzo":           # one half cycle only (worst, unphysical after HP)
        return lambda t: A * math.sin(w * t) if t < 0.5 / f else 0.0
    raise ValueError(kind)


if __name__ == "__main__":
    kinds = ["sin", "cos", "quadra", "burst1", "mezzo"]
    print("n tau_ms vth | t_det(0.95) t_det(1.5) t_det(14.9) ms | peak B(14V) 20Hz: " + " ".join(kinds) + " | peak F(3.82V) sin/quadra/burst1")
    for n in (1, 2, 3, 4):
        for tau in (0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.07):
            for vth in (0.4, 0.5, 0.6):
                td = [t_det(n, tau, vth, vx) * 1e3 for vx in (0.95, 1.5, 14.9)]
                if td[0] > 95:
                    continue
                pB = [run(n, tau, music(14.0, k), 0.6)[0] for k in kinds]
                pF = [run(n, tau, music(3.82, k), 0.6)[0] for k in ("sin", "quadra", "burst1")]
                print("%d %4.0f %.2f | %5.1f %5.1f %5.1f | %s | %s" % (
                    n, tau * 1e3, vth, td[0], td[1], td[2],
                    " ".join("%5.2f" % p for p in pB), " ".join("%5.2f" % p for p in pF)))
