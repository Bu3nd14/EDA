"""prova_p2.py - il controllo di Esponenziale (pilota_semplice.P2): la cima agli angoli e la
corrente a qualche frazione di Vb, per vedere lo spostamento con temperatura e dispersione."""
import pilota_semplice as P

RE = 100.0
vb = P.vb_top_per(P.ION, RE)
print("Vb di cima (7 mA a 60 C, Vbe -18 mV): %.4f V" % vb)
for tc in (15.0, 37.5, 60.0):
    for dv in (-18e-3, 0.0, 18e-3):
        e = P.Esponenziale(vb, RE, tc, dv)
        print("T %4.1f C  dVbe %+5.0f mV:  cima %.3f mA   v=0.6 %.3g A   v=0.45 %.3g A   v=0.35 %.3g A" % (
            tc, dv * 1e3, e.i(vb) * 1e3, e.i(0.6 * vb), e.i(0.45 * vb), e.i(0.35 * vb)))
