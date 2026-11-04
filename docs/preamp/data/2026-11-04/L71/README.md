# L71 — il frontale mosso durante una sequenza (NC-083): i dati

Il report è `reports/2026-11-04-L71-frontale-mosso.md`; la decisione ADR-120. Il circuito non cambia
(`circuits/preamp/psu.net` di `main` dopo L70bis). Sotto, `<L>` è questa cartella.

## Che cosa c'è

| Percorso | Che cos'è |
|---|---|
| `psu/`, `script/` (salvo i file nuovi sotto), `ponte/estrai_ponte.py`, `deck/controlla_deck.py`, `termica/`, `carico.txt` | Il banco di L69b, **copiato** (L69b non si riesegue sul posto) |
| `psu/genera_tb_psu.py` | Quello di L69b con le **cinque famiglie di L71** in `CASI_SEQ` (`acc_spento_`, `spl_riacceso_`, `spl_sw3_`, `ins_ritorno_`, `ril_ritorno_`; gli istanti in `L71_*`) e la lettura di `psu/casi_extra.txt` (gli istanti degli angoli). Sui casi che c'erano i deck sono quelli di L69b riga per riga: `script/prova_gen.sh`, 0 righe diverse a meno dei percorsi |
| `psu/toll_c0g_t{0,25,60}_dperm_sp.json` | Gli angoli peggiori di Δ di L54b3b (ADR-105), copiati |
| `lista_l71.txt` (135), `lista_rif.txt` (12), `lista_l71b.txt` (21), `lista_l71c.txt` (8), `lista_l71d.txt` (6), `lista_angoli_1.txt` (6), `lista_angoli_2.txt` (42) | Le liste **come sono state corse**, nell'ordine. `script/lista_l71.py` e `script/lista_l71b.py` leggono gli istanti dal generatore, che dopo la prima lista ne ha di più: rieseguiti oggi darebbero liste più lunghe. `lista_l71c/d` sono state scritte a mano dagli istanti fitti, `lista_angoli_*` da `script/lista_angoli_l71.py` |
| `an_l71.csv` | `psu/analizza_mc.py` su tutte le 230 corse |
| `stato_l71.csv` | `script/stato_finale.py`: le chiusure del jack, l'anticipo del permissivo (ADR-045, 3), il margine fisico a ogni distacco (`r41_min_ms`, il criterio di ADR-120), la musica più breve, lo stato finale contro quello atteso **scritto prima delle corse** |
| `sintesi_l71.txt` | `script/sintesi.py`: le cifre del report |
| `ponte/estrai_ponte_l71.py`, `ponte/<gruppo>/` | Il ponte di L71 nei nove posti del deck V2 (`posti.csv` dice quale corsa è in quale posto) e il modo «rientro» (`R:`). Gruppi in `gruppi.txt`: tre per rete, `rientro`, `brevi` |
| `script/catena_l71.sh`, `script/catene.sh`, `script/tabella_l71.py`, `tabella_<gruppo>.csv`, `catena_<gruppo>.out`, `deck/tb_v2_l41c_<gruppo>.cir` | La catena al jack: il criterio di V2 dello spegnimento, ≤ 100 µV, scritto prima delle corse |
| `script/calo.py`, `script/delta_nodi.py`, `script/mostra.py` | V+ / V− attorno alla musica che torna; i nodi di Δ; una tabella leggibile da un CSV |

Le forme d'onda (~45 MB l'una, 19 GB in tutto) e le corse grezze non stanno nel repository (`.gitignore`).

## Le corse

Il 2026-11-04: le 135 sequenze (3 alla volta), poi i riferimenti (3), le catene (2 alla volta) insieme alle
liste aggiunte (1 alla volta), gli angoli (3). **230 sequenze rc 0, tutte con `ok.txt`**; 16 col ripiego
numerico (`trap`, gmin 1e-8), tutte agli angoli a 0 °C, come in L54b3b. **11 catene, 198 corse audio rc 0**,
0 rifiutate dalle guardie, 0 partite dal punto sbagliato.

## Il ponte di L71, in breve

Il banco V2 (`--matrice l41c`) parte con il jack chiuso e modella **un** distacco del jack e **una** caduta del
guadagno, mai una richiusura. Per le famiglie dallo stato di musica la finestra è quella dello spegnimento
(T0 = TE − 1 s); per il frontale rispento all'accensione si apre 10 ms prima del primo fra lo spegnimento e
la musica, con T0 non prima di TE + 0,9 s (i rail della partenza morbida a ~0,6 s), e **solo** se il jack si è
chiuso (altrimenti nessun percorso al jack: `an_l71.csv`, `n_su` = 0). La finestra finisce 1 ms prima che il
jack o il guadagno si richiudano. Il **rientro** tiene il jack chiuso per tutta la finestra (aperta sulla
chiusura del jack) e confronta col riferimento a rail **fermi** al valore di T0: legge tutto quello che il
movimento dei rail, prima e dopo, lascia all'uscita quando la musica torna. **Ipotesi dichiarata**: per il
frontale rispento all'accensione il banco ha il jack chiuso da T0, cioè la scheda in musica da prima; la
chiusura del jack in sé è quella dell'accensione.

## Come si rifà

```sh
/bin/zsh <L>/script/prova_gen.sh                                  # i deck di L69b sui casi che c'erano
/bin/zsh <L>/script/corri_sequenze.sh 3 <L>/lista_l71.txt          # e lista_rif, lista_l71b/c/d, lista_angoli_1
/usr/bin/python3 -I <L>/script/lista_angoli_l71.py --da <L>/an_l71.csv   # dopo lista_angoli_1: scrive psu/casi_extra.txt
/bin/zsh <L>/script/corri_sequenze.sh 3 <L>/lista_angoli_2.txt
/bin/zsh <L>/script/analizza_l71.sh                                # an_l71.csv, stato_l71.csv
/usr/bin/python3 -I <L>/script/ponte_l71.py                        # i gruppi per rete e il rientro
/usr/bin/python3 -I <L>/ponte/estrai_ponte_l71.py <L>/seq <L>/ponte/brevi \
    spegnimento_l=l71_m10/acc_spento_1202p35 perdita=l71_m10/acc_spento_1202p4 perdita_min=l71_m10/acc_spento_1202p6 \
    guasto=l71_m10/acc_spento_1202p8 guasto_u501=l71_m10/acc_spento_1203 guasto_u503=l71_m10/acc_spento_1204 \
    guasto_u503_min=l71_ang_t0_m10/acc_spento_1164p4 cf_nodelta=l71_ang_t25_m10/acc_spento_1170p1 \
    corto_u503=l71_ang_t60_m10/acc_spento_1176p3
/bin/zsh <L>/script/catene.sh                                      # ogni riga di gruppi.txt
/usr/bin/python3 -I <L>/script/sintesi.py > <L>/sintesi_l71.txt
```
