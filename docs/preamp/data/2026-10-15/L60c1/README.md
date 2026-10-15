# L60c1 — dove sta il condensatore da 1 µF della Stax rispetto al relè di mute (2026-10-15)

Prima parte di **L60c**, divisa dall'utente all'inizio («Prima la prova»): le misure sul banco,
**senza toccare il sorgente**. Report `../../../reports/2026-10-15-L60c1-stax-condensatore-prova.md`,
decisione **ADR-084** («Relè rinforzato»).

`<C>` = questa cartella. Gli script ricavano la radice del repo dalla propria posizione.

## Il banco

Quello di L60a: il canale di L45a e i controlli di L45b, importati e non copiati, coi carichi montati
e senza rivelatore. Cambia **solo l'uscita della fissa 2**: le sette righe di `genera_canale.uscita()`
per FIX2 si sostituiscono con la geometria in prova. Il deviatore K3 ha due comandi, MNO e MNC,
così le corse del mute hanno il trasferimento di 1 ms di ADR-044.

| Geometria | L'uscita della Stax |
|---|---|
| G0 | quella di oggi (ADR-044) con 1 µF: 47 Ω → C → comune · NO al jack, NC a massa; bleed 470 k sui due lati |
| G1 | ADR-082 punto 1: 47 Ω → NO · comune → 1 µF → jack, NC a massa; bleed 470 k sul comune e sul jack |
| G1b | G1 col bleed del jack a 220 k |
| G2 | 47 Ω → 10 µF → comune · NO → 1 µF → jack, NC a massa; bleed 470 k sui tre nodi |
| G2b | G2 col bleed del jack a 220 k |

I guasti di K3 vanno sul nodo del NO e su quello del comune di ciascuna geometria (`NODI_K3` nel
generatore). Il pin aperto è uno dei due rami da 20 mΩ di un rail (ADR-083).

**Limiti del banco.** Il contatto aperto non ha la sua capacità di 0,1 pF (ADR-044): G0 e G2
danno un gradino del mute nullo e non i µV di L29d2. Su G1 non cambia niente: il gradino è di
millivolt. I rail sono ideali. Dei guasti del blocco ci sono solo i due al rail, A e F2, i peggiori
di L45a: gli altri guasti di L45a che portano continua si rifanno in L60c2 sul circuito scelto.

## I file

| File | Cosa |
|---|---|
| `script/genera_L60c1.py` | i 187 deck in `deck/<gruppo>/` e `deck/lista.txt` |
| `script/uno.sh`, `script/corri.sh` | le corse con `run_simulation.sh`, 8 alla volta; esiti in `run/esiti.tsv` |
| `script/analizza_L60c1.py` | `v2.csv`, `caldo.csv`, `e9.csv` (funzioni di `scripts/v2_metodo.py`) |
| `p10.csv` | `analizza_p10.py` di L45b sulle corse `run/p10/*/` e quelle di riferimento |

## I risultati

**Il riferimento**: G0 col blocco F2 al rail dà 117,5 ms (L60a: 117,5); K3 sul NO dà 12 V per sempre
(L60a: 12 V per sempre). E9 di G0 a 1 µF è 0,161 dB (ADR-081, a calcolo: 0,162).

**V2 A, il gradino del mute sulla Stax** (`v2.csv`; inserimento e rilascio; continua del buffer
−5,7 mV, e ±20 mV sull'ingresso di F2):

| | nominale | VOSF2 +20 mV | VOSF2 −20 mV |
|---|---|---|---|
| G0, G2, G2b | 0 | 0 | 0 |
| G1, G1b | **5,97–6,09 mV** (76,5 dB SPL) | **26,8–27,3 mV** (89,7) | **14,8–15,1 mV** (84,6) |

**P10, sopra 0,87 V sulla Stax** (`p10.csv`; condensatori nominali / +5 %):

| | blocco A al rail | F2 al rail | K3, 10 Ω | K3, 1 kΩ | K3 in mute | un pin aperto |
|---|---|---|---|---|---|---|
| G0 | 118 / 124 | 117,5 / 123 | **per sempre** (NO e comune) | **per sempre** | NO: **per sempre**; comune: 0 | 0 |
| G1 | **129 / 135** | **129 / 135** | 110 / 115 | 0 (0,54 V) | 0 | 0 |
| G1b | 116 / 122 | 116 / 122 | 99 / 104 | 0 (0,54 V) | 0 | 0 |
| G2 | 108 / 113 | 108 / 113 | 119 / 125 | **131 / 138** | NO: 119–120 / 125–126 | 0 |
| G2b | 98 / 103 | 98 / 103 | 107 / 112 | 120 / **126** | NO: 107–108 / 112–114 | 0 |

**E9, 20 Hz contro 1 kHz sul jack della Stax** (`e9.csv`; nominale / −5 %): G0 0,161 / 0,178;
G1 0,135 / 0,149; G1b 0,165 / 0,182; G2 0,163 / 0,180; G2b 0,199 / **0,220** dB.

**L'inserimento a caldo** (`caldo.csv`): 0 su tutte le geometrie. Il jack fuori mute sta a 0 V sul
suo bleed.

## Rifare

```sh
/usr/bin/python3 -I <C>/script/genera_L60c1.py
/bin/zsh <C>/script/corri.sh <C>/deck/lista.txt          # ~3 min, 187 corse
/usr/bin/python3 -I <C>/script/analizza_L60c1.py
/usr/bin/python3 -I docs/preamp/data/2026-10-13/L45b/script/analizza_p10.py <C>/p10.csv <C>/run/p10/*/
```

Le forme d'onda (`run/**`) non stanno nel repository: si rifanno.
