#!/bin/zsh
# analizza_tutto.sh - L45d2b2b2: analizza_075.py and riassunto_075.py on every label of the lot
set -u
S=${0:A:h}
L=$S:h
A=(/usr/bin/python3 -I "$S/analizza_075.py")
R=(/usr/bin/python3 -I "$S/riassunto_075.py")
$A "$L/seq/oggi" "$L/analisi_oggi.csv" @"$L/lista_075.txt"
$R "$L/analisi_oggi.csv" "$L/riassunto_oggi.csv" > "$L/riassunto_oggi.txt"
$A "$L/seq/oggi_ds" "$L/analisi_oggi_ds.csv" @"$L/lista_comando.txt"
$R "$L/analisi_oggi_ds.csv" "$L/riassunto_oggi_ds.csv" > "$L/riassunto_oggi_ds.txt"
$A "$L/seq/opz_a" "$L/analisi_opz_a.csv" @"$L/lista_comando.txt"
$R "$L/analisi_opz_a.csv" "$L/riassunto_opz_a.csv" mos=Q503:DMN6075S > "$L/riassunto_opz_a.txt"
$A "$L/seq/opz_b" "$L/analisi_opz_b.csv" @"$L/lista_comando.txt"
$R "$L/analisi_opz_b.csv" "$L/riassunto_opz_b.csv" mos=Q501:DMN6075S,Q502:DMN6075S,Q503:DMN6075S > "$L/riassunto_opz_b.txt"
$A "$L/seq/opz_r" "$L/analisi_opz_r.csv" @"$L/lista_resistenze.txt"
$R "$L/analisi_opz_r.csv" "$L/riassunto_opz_r.csv" > "$L/riassunto_opz_r.txt"
$A "$L/seq/opz_5v" "$L/analisi_opz_5v.csv" @"$L/lista_5v.txt"
$R "$L/analisi_opz_5v.csv" "$L/riassunto_opz_5v.csv" > "$L/riassunto_opz_5v.txt"
echo fatto
