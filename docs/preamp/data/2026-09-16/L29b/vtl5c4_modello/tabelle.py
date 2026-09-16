"""Da pixel a valori: VTL5C4, datasheet Excelitas pag. 46, rasterizzata a 300 dpi.
Griglia letta da digit.py: resistenza, decadi a y = 76,5 (10k) 253 (1k) 429,5 (100) 606 (10);
corrente, decadi a x = 13,5 (0,1 mA) 321,5 (1) 629,5 (10) 937 (100).
Tempi: resistenza, decadi a y = 72,5 (100k) 231,5 (10k) 390,5 (1k) 549,5 (100);
tempo, x = 52,5 + 123,8 per unita' (1 ms in accensione, 100 ms in spegnimento)."""
import math

PXD_R, Y10K = 176.5, 76.5
PXD_I, X01 = 307.8, 13.5

# centri dei tratti delle curve per colonna (digit.py), griglia ed etichette escluse
col = {
    113: [81.5, 135.5],
    165: [80.0, 124.5, 171.5],
    234: [144.0, 180.5, 218.0],
    328: [190.5, 225.0, 251.5, 278.0],
    421: [271.5, 294.5, 313.5, 332.0],
    473: [305.0, 327.0, 344.0, 360.0],
    542: [342.5, 362.0, 380.0, 393.0],
    636: [385.5, 401.0, 415.0, 429.5],
    729: [419.5, 431.0, 441.5, 454.0],
    810: [444.5, 453.0, 461.0, 468.5],
}

def R_di(y):
    return 10 ** (4 - (y - Y10K) / PXD_R)

def I_di(x):
    return 0.1 * 10 ** ((x - X01) / PXD_I)

print("I_mA, R per curva dall'alta alla bassa resistenza (ohm)")
righe = []
for x in sorted(col):
    I = I_di(x)
    Rs = [R_di(y) for y in col[x]]
    righe.append((I, Rs))
    print("%.3f  " % I + "  ".join("%.0f" % r for r in Rs))

# tempi di spegnimento a 40 mA (curva continua) e a 10 mA (tratteggiata)
TX0, TPX = 52.5, 123.8
def Rt(y):
    return 10 ** (5 - (y - 72.5) / 159.0)
off40 = [(182, 360), (240, 326), (305, 295.5), (365, 270.5), (430, 244), (490, 222), (553, 199.5), (677, 159), (790, 123), (905, 87.5)]
off10 = [(182, 346.5), (240, 309), (305, 215.5 if False else 212.0), (365, 254.5), (490, 207), (553, 184.5), (677, 143), (790, 107)]
print("\nspegnimento a 40 mA: t_ms, R, log10R")
for x, y in off40:
    t = (x - TX0) / TPX * 100
    print("%.0f  %.0f  %.3f" % (t, Rt(y), math.log10(Rt(y))))
on40 = [(240, 467), (305, 488.5), (365, 502.5), (430, 515.5), (490, 525.5), (553, 535.5), (610, 542.5)]
on10 = [(305, 403), (365, 420), (430, 436), (490, 446.5), (610, 465.5), (677, 476.5), (740, 486.5), (790, 490.5), (905, 500)]
print("\naccensione a 40 mA: t_ms, R")
for x, y in on40:
    print("%.2f  %.0f" % ((x - TX0) / TPX, Rt(y)))
print("\naccensione a 10 mA: t_ms, R")
for x, y in on10:
    print("%.2f  %.0f" % ((x - TX0) / TPX, Rt(y)))
