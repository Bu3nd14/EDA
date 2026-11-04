# L70 — le due semplificazioni: i dati

Il report è `../../../reports/2026-11-04-L70-semplificazioni.md`; la decisione **ADR-119** («Tenere com'è»:
il circuito non cambia). Sotto, `<L>` è questa cartella e `<R>` la radice del repo. Python di sistema con
`-I`; al più tre simulazioni insieme, a priorità bassa.

## Il banco

Il banco di L69b (`../L69b/`) **copiato**, non rieseguito sul posto: `psu/`, `script/`, `deck/`, `termica/`,
`ponte/`, `lista_l64b.txt`, `carico.txt`, `lista_consumo.txt`. I cambi in questa copia:

| File | Che cosa |
|---|---|
| `psu/genera_tb_psu.py` | `--fusibile` (il modello del fusibile, sotto); i nodi delle parti tolte che le sonde leggono (`at_bn`, `at_f`, `at_t2s`, `at_md`, `md`, …) con 1 GΩ a massa, dichiarati nel deck (funzione `l70`); le sonde di Q504, il modello del costruttore di Q513 / Q514 e `alter rr512` saltati quando la parte non c'è. Sul circuito di oggi il deck è quello corso in L69b (`script/prova_gen.sh`: uguale a meno del percorso) |
| `script/catena_v.sh`, `script/ponte_v.sh` | `catena_audio.sh` / `ponte.sh` di L69b per una variante (cartelle `ponte/<v>_<rete>`, `corse/<v>_<rete>`, `tabella_<v>_<rete>.csv`) |

**Il fusibile** (`--fusibile I2T:ITH:RC`, o `REF=I2T:ITH:RC,...` uno per fusibile): resistenza a freddo RC e
un modello termico del primo ordine h' = i² − h/τ, τ = I2T / ITH², che fonde a h = I2T (l'I²t di fusione del
costruttore, adiabatico per gli impulsi brevi) e una corrente continua solo sopra ITH; fuso resta aperto.
ITH = 2,1 In nelle corse (il fusibile più lento, IEC 60127-2). Le cifre in `parti_fusibile.md`
(bom-component-manager, con le fonti). **Errore corretto**: la prima versione lasciava 1 Ω nel ramo (1 S
invece di 1e4 S); le corse fatte con quella sono state cancellate e rifatte.

## Le varianti (`varianti/`)

`fai_varianti.py` scrive `psu_<v>.py` (copie di `<R>/circuits/preamp/psu.py` con sostituzioni esatte, che
rifiutano se il sorgente si è mosso), `netlist.sh` le netlist (`PSU_NET_OUT`), `controlla.py` →
`controllo.txt` le parti e i piedini cambiati, e `psu_oggi.net` = `psu.net` del repo a meno della data.

| Variante | Parti | Che cosa |
|---|---|---|
| `s2` | 178 | senza il rivelatore di rete |
| `s1` | 176 | senza la ritenuta; F502 / F503 nei rami del secondario di T1 |
| `s1s2` | 167 | le due |
| `s1s2dc` | 169 | le due, e F504 / F505 sul lato continua (fra i serbatoi e R550 / R551) |

## Le corse (310, tutte con `ok.txt`, nessun ripiego)

| Lista | Etichette | Che cosa |
|---|---|---|
| `lista_s2_eventi.txt` | `s2[_m10/_p10]` | i 32 eventi (le righe non `f_` di `lista_l64b.txt`) |
| `lista_buchi_oggi.txt`, `lista_buchi_s2.txt` (`script/lista_buchi.py`) | `<v>_b<ms>[_m10/_p10]` | `buco200` con `--rete-forma buco:<ms>:zero`, 40–150 ms |
| `lista_corti_oggi.txt` (`script/lista_corti.py`) | `oggi` | i 38 guasti del lato grezzo (C501 / C502 / C509 / C510, D501 a–d, D510 / D511, D515 / D516) |
| `lista_coda2.txt` | `s1`, `s1s2` | gli eventi col fusibile neutro (1e9 A²s): la corrente nei rami |
| `lista_coda3.txt` | `s1s2_f125`, `s1s2_f160` | i 38 guasti con la 218 da 1,25 e da 1,6 A |
| `lista_coda5.txt` | `s1s2dc` | eventi e guasti, 1,6 A sul secondario e 1 A sul lato continua |

`script/corri_sequenze.sh 3 <lista>`; `script/mancanti.py` le righe senza `ok.txt`.

## Le analisi

| File | Script | Che cosa |
|---|---|---|
| `an_<v>.csv`, `confronto_<v>.txt` | `script/analizza_v.sh <v> confronta` (`psu/analizza_mc.py`, `script/confronta_eventi.py`) | gli eventi, e le colonne diverse da `../L69b/an_l64b.csv` |
| `an_buchi_<v>.csv` | `script/analizza_buchi.sh` | i buchi di rete |
| `fusibili_<etichetta>.csv` | `script/analizza_fus.sh` (`script/fusibili.py`) | per fusibile: picco, I²t, efficace a fine corsa, quando fonde; R550 / R551: picco, energia da TE, potenza a fine corsa |
| `tabella_s1s2_<rete>.csv`, `catena_s1s2_*.out` | `script/ponte_v.sh s1s2` | la catena al jack |
| `blocco/calore.csv` | `blocco/prepara.py`, `blocco/corri.sh`, `blocco/calore.py` | il blocco audio con un rail solo (deck di riferimento di L66 con un rail a 0 / ±0,6 V); il riferimento ridà L66 |
| `righe_toccate.csv` | `script/fmea_k501.py` | le righe della FMEA di oggi (L69) toccate da ciascuna variante |

## Le cifre

- S2 da sola: la ritenuta scatta a ogni perdita di rete e nei buchi di 60–200 ms (`confronto_s2.txt`,
  `an_buchi_s2.csv`); il buco di 20 ms senza mute.
- S1+S2: buco di 20 ms senza mute; 200 ms, la musica dopo 671–723 ms; al jack la perdita di rete 16,9–17,9
  dB SPL.
- I rami del secondario: 0,69 A efficaci, 24,5 A di picco, 3,0 A²s per accensione.
- C509 / C510 in corto: oggi R550 6,1 / 7,7 / 9,4 J; S1+S2 con 1,6 A nessun fusibile fonde, R550 34 / 43 /
  53 W di continuo; s1s2dc, F504 a — / 998 / 759 ms, R550 34–43 J.
- Il blocco con un rail solo: ≤ 75 °C con 60 °C d'aria.

## Come si rifà

```sh
/usr/bin/python3 -I <L>/varianti/fai_varianti.py ; /bin/zsh <L>/varianti/netlist.sh
/usr/bin/python3 -I <L>/varianti/controlla.py > <L>/varianti/controllo.txt
/bin/zsh <L>/script/prova_gen.sh buco20
/bin/zsh <L>/script/corri_sequenze.sh 3 <L>/lista_<...>.txt        # le liste sopra
/bin/zsh <L>/script/analizza_v.sh s2 confronta ; /bin/zsh <L>/script/analizza_buchi.sh oggi s2
/bin/zsh <L>/script/analizza_fus.sh <etichetta> [f]
/bin/zsh <L>/script/ponte_v.sh s1s2
/usr/bin/python3 -I <L>/blocco/prepara.py ; /bin/zsh <L>/blocco/corri.sh 1 ; /usr/bin/python3 -I <L>/blocco/calore.py
/usr/bin/python3 -I <L>/script/fmea_k501.py
```
