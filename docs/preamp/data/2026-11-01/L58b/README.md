# L58b — l'autodiagnosi (2026-11-01)

Le righe latenti mandate alla diagnosi (ADR-071, ADR-076, ADR-078, ADR-100; ADR-109), misurate per
vedere **che cosa mostrano**; la coppia in serie a Q501 misurata e messa nel sorgente. Decisione
**ADR-110**; report `../../../reports/2026-11-01-L58b-autodiagnosi.md`; procedura
`../../../DIAGNOSI.md`. `<L>` = questa cartella; Python con `/usr/bin/python3 -I`.

## I banchi e i casi noti

| Banco | Copiato da | Caso noto |
|---|---|---|
| `psu/` (il temporizzatore, `corri_lista_an.sh`) | `data/2026-10-29/L58a/psu/` | `l58b_base/accensione` e `spegnimento_l` riga per riga uguali a `l58a_base` (`an_l58b.csv` contro `an_l58a.csv`) |
| `script/genera.py` (i guasti del blocco sul sorgente) | il banco del calore di L45d2b3b2b2, caricato per percorso | `rif`, `Q132_ce`, `R126_cc` nelle cinque posizioni: 15 righe di `calore_sorg.csv` e `analisi_jack_sorg.csv` uguali |
| `v2/` (V2 all'accensione con le rampe vere) | `data/2026-10-29/L58a/v2/` | `l58_base_acc` uguale a L58a2 (7,7 nV alla fissa 1) |

## Le aggiunte al banco dell'alimentatore

- `modi.py`: `RIGHE_L58B` (i sette modi dello standby, K501 saldato = Q503 in corto; Q501 D-S / G-D),
  `RIGHE_SERIE` (i quattro modi della coppia), `RIGHE_SERIE_R` (R586 / R587 aperte), l'evento `inss`
  (l'inserimento del mute dal frontale).
- `genera_tb_psu.py --q501serie <R_sopra>:<R_sotto>`: Q501 + Q509 al posto di Q501 sul sorgente di
  prima. Sul sorgente nuovo **non va usata** (la coppia c'è già): `psu/sorgente_uguale.py` prova che il
  deck del sorgente nuovo è il deck della variante (`1e6:10000`), salvo il titolo.
- `psu/censimento.py`: lo standby a regime (VRELAY alla scheda audio, K501, i rail), l'istante in cui
  le bobine del mute si eccitano all'accensione, il mute che resta eccitato dopo l'inserimento.
- `psu/confronta_serie.py`: la coppia contro la base e i guasti contro la coppia sana.

## Le cifre

- **Lo standby** (`censimento_psu.csv`):
  - Q505 / Q506 in corto e R540 aperta: VRELAY 12,0 V alla scheda audio a frontale spento (i LED);
  - R536 aperta dal primo spegnimento; R537 in corto e U508 B cieco anche a freddo, col toroidale acceso;
  - Q503 in corto: toroidale acceso, VRELAY 0, la musica a 17,4 ms invece di 1209,3.
- **Q501** (`v2/analisi.csv`): le bobine eccitate 2,5 ms dopo il frontale, rail a 0,012 V; il jack
  principale 70,1 mV, fisse 0,642 / 0,657 V; rete −10 / +10 % uguale (`lista_rete.txt`).
- **Il blocco** (`censimento_blocco.csv`, posizioni A, B, B a +10 dB, F1, F2): la continua al test
  point e il riposo dei finali contro `rif`.
- **La coppia**:
  - `lista_serie.txt` (10 kΩ / 10 kΩ, `an_serie.csv`): Q501 G-D, il jack a 50,4 / 49,9 ms contro 10,3,
    dopo il guadagno (C3, r41 a 0);
  - `lista_s1m.txt` / `lista_s1m2.txt` (1 MΩ / 10 kΩ, `an_s1m.csv`, `cens_s1m.csv`, `an_s1m_rete.csv`):
    tutto come la coppia sana salvo Q509 G-D (muto);
  - `lista_sorg.txt` (`an_sorg.csv`): gli otto eventi sul sorgente nuovo uguali alla variante (0,1 ms,
    0,1 mV).
- **I falsi** (`falsi/`): i 24 di L54b1 e 5 della coppia, 29 su 29 come attesi (`verdetti.txt`).
- **La FMEA** (`fmea_l58b.csv`, `script/fmea_l58b.py`): 60 righe, 5 alte (K2–K4 accettate, R585
  accettata), 25 medie, 30 basse.

## Rifare

```sh
/usr/bin/python3 -I <L>/psu/lista_l58b.py > <L>/lista_l58b.txt
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_l58b.txt 4
/usr/bin/python3 -I <L>/psu/analizza_mc.py --te=3.0 <L>/an_l58b.csv <L>/seq/l58b_base/* <L>/seq/l58b/*
/usr/bin/python3 -I <L>/psu/censimento.py <L>/censimento_psu.csv <L>/seq/l58b_base/* <L>/seq/l58b/*
/usr/bin/python3 -I <L>/script/genera.py sorg
/bin/zsh <L>/script/corri.sh <L>/deck/lista_sorg.txt 6
/usr/bin/python3 -I <L>/script/analizza.py sorg
/usr/bin/python3 -I <L>/script/censimento_blocco.py
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_rete.txt 6
/usr/bin/python3 -I <L>/v2/genera_v2_l58b.py
/bin/zsh <L>/v2/corri_v2.sh
# la coppia (sul sorgente di PRIMA, --q501serie): lista_serie.txt, lista_s1m.txt, lista_s1m2.txt
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_s1m.txt 6      # da <L>
/usr/bin/python3 -I <L>/psu/confronta_serie.py an_s1m.csv cens_s1m.csv l58b_s1m      # da <L>
# il sorgente nuovo
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_sorg.txt 8
/usr/bin/python3 -I <L>/falsi/falsi.py circuits/preamp/preamp_audio.net circuits/preamp/psu.net
/usr/bin/python3 -I <L>/script/fmea_l58b.py
```

Le forme d'onda (`*_out.txt`), `run/` e `v2/run/` non stanno nel repository (`.gitignore`).
