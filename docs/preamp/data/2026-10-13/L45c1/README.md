# L45c1 — i guasti singoli dell'alimentatore: i rail audio (2026-10-13)

Prima parte di **L45c** (scelta dell'utente all'inizio del lotto, «Due parti»: L45c1 i rail audio,
L45c2 la linea dei relè, i sorveglianti, il temporizzatore, i sink e il relè di rete). Report
`../../../reports/2026-10-13-L45c1-fmea-rail.md`. Nessun cambiamento al circuito.

`<A>` = questa cartella. È alla stessa profondità di `../../2026-10-12/L56-alimentatore/`, perché gli
script ricavano la radice del repo dalla propria posizione.

## Da dove viene

| Cosa | Da | Cambio |
|---|---|---|
| `psu/` (generatore, `corri_seq.sh`, analisi), `script/`, `carico.txt`, `ponte/estrai_ponte.py` | `../../2026-10-12/L56-alimentatore/` | il generatore e `corri_seq.sh` sanno fare i casi di guasto `f_*` (sotto); il resto com'era |
| `deck/genera_tb_v2_casopeggiore.py` | `../../2026-09-23/L29c/deck/` | `--casi` (la lista dei casi del ponte) e `--rl` (il carico dei tre jack); senza, il deck di L56 byte per byte |
| `deck/controlla_deck.py` | L56 | nessuno |

**Controlli della copia, prima di aggiungere i guasti**:
- `perdita` e `guasto_u501` corsi da qui danno il CSV del firmware e il JSON del ponte **identici
  byte per byte** a quelli di L56;
- il generatore audio copiato, senza le due opzioni, rifà il `deck/tb_v2_l41c.cir` di L56 **identico**;
- `script/misura_p10.py --prova`: l'esponenziale di L45b (1468,6 ms attesi, 1468,6 misurati), il seno a
  997 Hz (328,2 / 328,2) e lo stesso esponenziale scritto come file wrdata e riletto col lettore di
  `v2_metodo` (1468,65 / 1468,60 ms).

## I casi

`psu/modi.py` è la tabella dei modi; la sua intestazione dice le primitive. Un caso simulato si
chiama `f_<parte>_<modo>_<evento>`:

- **evento `mus`**: il guasto a TE = 2 s durante la musica, e niente altro, fino a TE + 1 s;
  `mus6` lo stesso fino a TE + 6 s (la presa centrale aperta, la cui deriva è lenta);
- **evento `perd`, `spegn`, `gu502`, `gu501`**: il guasto è **latente**, presente da t = 0, e a TE
  arriva l'evento (la perdita di rete, lo spegnimento dal frontale, U502 o U501 spenti, i casi di
  L41c).

Le primitive, applicate da `applica_guasto()` in `psu/genera_tb_psu.py` sulle righe delle parti
dell'alimentatore, ognuna con un `assert` su ciò che tocca (una riga o un nodo che il deck non ha
rifiuta il deck):

| Primitiva | Che cosa fa |
|---|---|
| `corto` | 10 S (0,1 Ω) fra due nodi dall'istante del guasto |
| `aperto` | il terminale spostato su un nodo nuovo, unito al vecchio da 1 kS prima e 1 nS dopo |
| `vset` | un gemello del regolatore comportamentale con un'altra tensione d'uscita prende il posto dell'originale all'istante del guasto (un pin ANY-OUT, il partitore di U502, SENSE) |
| `j1` | il filo di un rail fra le due schede si apre: regolatore, tenuta, sorvegliante dal lato dell'alimentatore (`vplus_psu`), il carico e i 100 µF della scheda audio (−20 %) dal suo |

I **NO saldati** di K2–K4 (`nosald_*`) non cambiano niente sull'alimentatore: `ponte/saldati.py`
copia il ponte del caso di base col contatto del jack che non si apre mai.

Il controllo delle primitive: `script/prova_generatore.py <cartella> <core.csv>` genera ogni deck e
stampa le righe che il guasto aggiunge o cambia rispetto al caso di base.

## Le corse

| Passo | Comando | Esito |
|---|---|---|
| alimentatore, al punto fisso col firmware | `psu/corri_lista.sh seq/lista.txt` (xargs -P 8) | 44 casi su 44 al punto fisso; un ripiego (`f_j513ct_aperto_mus`, gear → trap a TE + 3 ms, «Timestep too small» su `b.xu504.bi`) |
| il lato alimentatore | `script/analizza_psu.py seq analisi_psu.csv @seq/lista.txt` | `analisi_psu.csv` |
| la scheda audio | `script/catena_l45c1.sh` (ponte, saldati, due deck, corse, guardie, ripiego gear, analisi, lettura fino ai rimbalzi) | `corse_100k/` 94 corse su 96 passano la guardia, `corse_vuoto/` 95 su 96 (sotto) |
| la tabella | `script/tabella_l45c1.py <A>` | `fmea_rail.csv`, `fmea_rail.md` |

**Le corse audio che si fermano.** Il corto del rail + (`f_vplus_massa_mus`, ai due carichi) e il
corto di C501 (`f_c501_corto_mus`, a 100 k) si fermano su «Timestep too small» nel JFET d'ingresso
del blocco A, a +4,10 / +4,35 ms, coi tre tentativi di `corri.sh` e anche col metodo gear
(`script/rifai_gear.sh`, il primo log resta come `corsa_<c>_trap.log`). `script/fino_all_aborto.py`
le legge **fino alla fine dei rimbalzi del jack** (t_jack + 0,521 ms, il contatto di
`tb_v2_mute_graduale.cir`), che cade prima dell'aborto (lo script lo verifica): da lì il contatto è
aperto e, coi 1e-18 F di cavo del banco, il jack non tiene niente. **Non fino all'aborto**: nel
corto di C501 a 100 k il risolutore resta fermo su un istante (4,2007 ms) con il jack a 0,84 V per
molte righe prima di fermarsi — una corsa che sta per abortire, non una tensione; lo stesso caso a
vuoto, che finisce, ha al più 8,9 mV, e la lettura fino ai rimbalzi a 100 k dà 9,0 mV. Il picco è
grezzo, e la tabella lo usa al posto del filtrato dicendolo (`aborto.csv`).

**Un errore della prima corsa, corretto.** Il primo `catena_l45c1.sh` aveva la lista dei carichi
scritta male (`${@:-100k vuoto}` diventa un solo elemento): ha corso solo il carico 100 k, in una
cartella `corse_100k vuoto`. I dati sono quelli giusti del 100 k; la cartella e il deck sono stati
rinominati (`corse_100k/`, `deck/tb_v2_100k.cir`), lo script corretto, e il carico a vuoto corso a
parte con `catena_l45c1.sh vuoto`.

`corse_100k/` è il carico di L41c / L56 (100 kΩ sui tre jack) per il picco filtrato di PR-23 / P9 (b)
(`analisi.csv`, A_ins); `corse_vuoto/` è P10, a vuoto (1e12, restano i bleed): `p10.csv`, il picco
grezzo e il tempo sopra 0,87 V.

## Rifare

```sh
/bin/zsh <A>/psu/corri_seq.sh --solo-compila
/usr/bin/python3 <A>/psu/lista.py > <A>/seq/lista.txt
/bin/zsh <A>/psu/corri_lista.sh <A>/seq/lista.txt                 # ~12 min, 8 alla volta
/usr/bin/python3 <A>/script/analizza_psu.py <A>/seq <A>/analisi_psu.csv @<A>/seq/lista.txt
/bin/zsh <A>/script/catena_l45c1.sh                               # i due carichi
/usr/bin/python3 <A>/script/tabella_l45c1.py <A>
```

Le forme d'onda (`seq/**/*_out.txt`, `corse_*/*.dat`) e i deck che `dividi.py` rigenera sono in
`.gitignore`.
