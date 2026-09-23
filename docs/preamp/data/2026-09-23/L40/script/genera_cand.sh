#!/bin/zsh
# genera_cand.sh : i costi dei candidati, sui deck flat (blocco B) che non sono
# d'anello: risposta e E2 (tb_ac), V3 (tb_v3_overload), headroom (tb_dc_headroom),
# rumore E5 (tb_noise_breakdown), Zout/PSRR (tb_zout_psrr_noise), punto di lavoro
# (tb_op). I candidati:
#   ctrl        nessuna alter: deve ridare L39/dopo
#   a_r169      strada (a): C124 1n
#   a_r133      strada (a): C124 1n, R128 1.33k (I_q 14,6 mA)
#   b0_r169     strada (b): +1,5 dB (RG0 7.87k, R138 6.49k), C_f 220p, C124 470p
#   b_r169      strada (b): +1,5 dB, C_f 220p, C124 560p
#   b_r133      strada (b): +1,5 dB, C_f 220p, C124 560p, R128 1.33k
S=${0:A:h}
mkdir -p $S/../candidati
: > $S/../candidati/lista.txt
B="+RG0L40 FB 0 7.87k"
for d in tb_ac tb_v3_overload tb_dc_headroom tb_noise_breakdown tb_zout_psrr_noise tb_op; do
  /usr/bin/python3 $S/varianti.py candidati $d ctrl --curve "alter r128 = 1.69k" >> $S/../candidati/lista.txt
  /usr/bin/python3 $S/varianti.py candidati $d a_r169 --curve "alter c124 = 1n" >> $S/../candidati/lista.txt
  /usr/bin/python3 $S/varianti.py candidati $d a_r133 --curve "alter c124 = 1n" "alter r128 = 1.33k" >> $S/../candidati/lista.txt
  /usr/bin/python3 $S/varianti.py candidati $d b0_r169 --curve "$B" "alter r138 = 6.49k" "alter c137 = 220p" >> $S/../candidati/lista.txt
  /usr/bin/python3 $S/varianti.py candidati $d b_r169 --curve "$B" "alter r138 = 6.49k" "alter c137 = 220p" "alter c124 = 560p" >> $S/../candidati/lista.txt
  /usr/bin/python3 $S/varianti.py candidati $d b_r133 --curve "$B" "alter r138 = 6.49k" "alter c137 = 220p" "alter c124 = 560p" "alter r128 = 1.33k" >> $S/../candidati/lista.txt
done
wc -l $S/../candidati/lista.txt
