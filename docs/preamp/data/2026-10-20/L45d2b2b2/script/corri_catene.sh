#!/bin/zsh
# corri_catene.sh - L45d2b2b2: the audio chain (catena_074.sh, 100 kOhm) on the cases that lose Delta
# today (D508 shorted, K501's coil shorted, three mains levels) and on K501's coil with option A2
set -u
S=${0:A:h}
/bin/zsh "$S/catena_074.sh" oggi 100k f_d508_corto_musm10 f_d508_corto_mus f_d508_corto_musp10 f_k501_bobina_musm10 f_k501_bobina_mus f_k501_bobina_musp10
/bin/zsh "$S/catena_074.sh" opz_a2 100k f_k501_bobina_musm10 f_k501_bobina_mus f_k501_bobina_musp10
echo "fatto"
