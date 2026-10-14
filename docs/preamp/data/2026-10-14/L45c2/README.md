# L45c2 — i guasti singoli della linea dei relè e del comando (2026-10-14)

Seconda parte di **L45c** (scelta dell'utente, 2026-10-13, «Due parti»), la prima nella forma di
**ADR-070** (gravità, probabilità, rilevabilità, priorità, rimedi candidati). Report
`../../../reports/2026-10-14-L45c2-fmea-comando.md`. Nessun cambiamento al circuito.

`<A>` = questa cartella, alla stessa profondità di `../../2026-10-13/L45c1/` (gli script ricavano la
radice del repo dalla propria posizione).

## Da dove viene

| Cosa | Da | Cambio |
|---|---|---|
| `psu/`, `script/`, `deck/`, `ponte/estrai_ponte.py`, `ponte/saldati.py`, `carico.txt` | `../../2026-10-13/L45c1/` | `genera_tb_psu.py`: le primitive `spento` e `niente`, l'evento `ins` (SW3 su mute) e `gu503` (U503 spento), una capacità facoltativa sull'apertura, la fine anticipata per caso (`modi.TF`). `modi.py` e `lista.py` sono di questo lotto |

**Controlli della copia, prima di ogni cambio**: `perdita` e `guasto_u501` corsi da qui danno il CSV
del firmware e il JSON del ponte **identici byte per byte** a quelli di L45c1. Dopo i cambi,
`script/prova_generatore.py` genera ogni deck di guasto e mostra che cambiano solo le righe della
sua primitiva (50 su 50); il caso di base `f_base_niente_ins` ha SW3 che si apre a TE e nient'altro.

## I casi

`psu/modi.py`: la tabella dei modi (la sua intestazione dice le primitive e gli eventi).
`script/classi_l45c2.py`: i tassi, la ripartizione dei modi, la rilevabilità, la gravità minima,
i rimedi (ADR-070); le fonti in `tassi/fonti.md`.

## Le corse

| Passo | Comando | Esito |
|---|---|---|
| alimentatore, al punto fisso col firmware | `psu/corri_lista.sh seq/lista.txt` | prima corsa 57 casi, 45 al punto fisso e 12 rifiutati (sotto); oggi 57 casi: 46 da soli, 2 accorciati, 9 accettati, la stella aperta tolta e R524 col mute aggiunta |
| i punti fissi che la regola del ponte non sa riconoscere | `psu/accetta.py seq/<caso>` | 9 accettati (sotto) |
| il lato alimentatore | `script/analizza_psu.py`, `script/analizza_rele.py` | `analisi_psu.csv`, `analisi_rele.csv` |
| la scheda audio | `script/catena_l45c2.sh` | `corse_100k/` e `corse_vuoto/`: 114 corse ciascuno, nessuna fallita |
| la tabella | `script/tabella_l45c2.py <A>` | `fmea_comando.csv`, `fmea_comando.md` |

**I punti fissi accettati (`accetta.py`).** La regola di `ponte.c` per `MUTE_G_IN` ricostruisce il
pin dai sorveglianti **supponendoli sani** dove l'uscita del core è cambiata rispetto a quella che ha
pilotato il circuito. Quando il guasto è proprio un sorvegliante, il riferimento o la catena di
`MUTE_G`, la ricostruzione contraddice il circuito, e `corri_seq.sh` rifiuta. `accetta.py` (con la
sua intestazione) accetta solo:
- **regola A**: le uscite del core uguali **byte per byte** fra gli ultimi due giri, e ogni
  sostituzione nel tick in cui il core cambia `MUTE_REQ` — `f_u505a_cieco_gu501`,
  `f_u505b_cieco_gu502`, `f_q501_gd_spegn`, `f_u506b_cieco_gu503`;
- **regola B**: nessun punto fisso del core, ma gli ultimi due giri danno alla scheda audio **le stesse
  cose** — i rail entro 2 mV a ogni campione, l'istante del jack e quello del guadagno entro 0,2 ms —
  `f_u504_spento_mus`, `f_u507_corto_mus`, `f_c528_corto_mus`, `f_q502_gd_mus`, `f_d522_corto_perd`.
  I rail differiscono al più di 0,18 mV.
Controllato prima dell'uso su un caso noto: una copia di `perdita` passa con la regola A e 0
sostituzioni; la stessa copia col giro 2 sostituito dalle forme d'onda di `guasto_u501` è rifiutata
(8,4 V di differenza sui rail, jack a 2,0174 contro 2,0118 s). Il ragionamento è scritto in
`seq/<caso>/accettato.txt`.

**Le corse accorciate (`modi.TF`).** Tre casi si fermano su «Timestep too small» con tutti e due i
metodi quando tutto è già spento: `f_c520_aperto_perd` a TE + 0,72 s, `f_u505a_cieco_gu501` a
TE + 0,95 s (i rail a +0,0004 / −0,73 V), `f_u507_aperto_mus` a TE + 0,96 s. Corrono fino a
TE + 0,6 / 0,9 / 0,9 s: in tutti il jack e il guadagno si muovono entro 32 ms dall'evento. Il banco
audio usa la durata del JSON del ponte.

**La stella aperta (NT501) non si simula.** Aperta la stella, il dominio del comando galleggia sulla
massa audio, e il banco legge i livelli logici rispetto alla massa: la corsa si ferma all'istante del
guasto, e con 1 nF dichiarato sull'apertura (la capacità fra gli avvolgimenti di T2) a TE + 30 ms
con tutti e due i metodi. È a calcolo (`modi.CALCOLO`); la cartella `seq/f_nt501_aperto_mus/`
resta come prova.

**Un artefatto noto.** Con V5 persa (`f_u504_spento_mus`), dopo ~20 ms il micro comportamentale con
V5 flottante porta i suoi pin a valori negativi a ogni semionda. A quel punto `MUTE_G` e `PERMIT_G`
sono già caduti (1,6 e 2,1 ms): gli istanti che vanno alla scheda audio sono fissati prima.

`script/guarda.py` stampa una forma d'onda a campioni (lo strumento usato per i casi sopra).

## Rifare

```sh
/bin/zsh <A>/psu/corri_seq.sh --solo-compila
/usr/bin/python3 <A>/psu/lista.py > <A>/seq/lista.txt
/bin/zsh <A>/psu/corri_lista.sh <A>/seq/lista.txt                 # ~6 min, 8 alla volta
/usr/bin/python3 <A>/psu/accetta.py <A>/seq/<caso>                # i 9 casi sopra
/usr/bin/python3 <A>/script/analizza_psu.py <A>/seq <A>/analisi_psu.csv @<A>/seq/lista.txt
/usr/bin/python3 <A>/script/analizza_rele.py <A>/seq <A>/analisi_rele.csv @<A>/seq/lista.txt
/bin/zsh <A>/script/catena_l45c2.sh                               # i due carichi
/usr/bin/python3 <A>/script/tabella_l45c2.py <A>
```

Le forme d'onda (`seq/**/*_out.txt`, `corse_*/*.dat`) e i deck che `dividi.py` rigenera sono in
`.gitignore`.
