# L45d2b3a — la retroazione dei regolatori dei rail: sul piedino o sul rail (2026-10-22)

Prima parte di **L45d2b3**, divisa all'inizio: l'utente ha riaperto il punto 2 di ADR-093 («facciamolo
in questo lotto»); i guasti rifatti e la sintesi sono L45d2b3b. Report
`../../../reports/2026-10-22-L45d2b3a-retroazione-regolatori.md`; decisione **ADR-096** («Sul
piedino»); il circuito non cambia.

`<A>` = questa cartella, `<R>` = la radice del repo.

## Il modello del costruttore di TPS7A4701

| File | Cosa |
|---|---|
| `script/patch_tps7a4701.py` | dal file congelato in `vendor/` al derivato in `<R>/models/ldo_regulator/tps7a4701_ngspice.lib`: 3 × `TC=0,0` tolti, 2 × `VSWITCH` → `SW` (coi suffissi SPICE letti: `ROFF=1G` è 1e9), 2 × `LIMIT` → `MIN(MAX(…))` |
| `prova/tb_limit.cir` | come ngspice legge `LIMIT` (`LIMIT(5, −1, 2)` = 0) e la riscrittura, nei due ordini (limitations #72) |
| `prova/tb_u501_op.cir` | 15,3 V con i piedini ANY-OUT di U501, 19 V, 51 Ω: **15,294 V** |
| `prova/tb_u501_gradino_ds.cir` | SBVS204G fig. 5-19 (5 V, 3,3 V, 10 → 845 mA, 10 µF): **3,37 mV**, fermo; la figura ~5 mV di picco e ~3 a regime, a occhio |

I due casi noti stanno anche in `validate_models.py` (`tb_tps7a4701`), con la DC in tre istanze.

**Che cosa è il modello.** L'uscita vale V(NR) × V(OUT) / V(SENSE) dietro 50 Ω / 32 nF e 4 mΩ. Con
SENSE sull'uscita il rapporto è 1: nessun anello (il gradino è la resistenza da 4 mΩ). Con SENSE
altrove l'anello è un integratore a ~94 kHz, con un termine locale perché il rapporto legge l'uscita
dopo i 4 mΩ. Il modello di TPS7A3301 (`vendor/`, usato com'è) ha la stessa forma senza il ritardo:
nessun anello.

## Il margine di fase

| File | Cosa |
|---|---|
| `script/anello.py` | un caso: il regolatore **generico** (integratore con banda fc, sorgente al piedino dietro `ro`), la rete del rail, il guadagno d'anello per iniezione di tensione sull'ingresso di misura, gli attraversamenti e il margine |
| `script/inviluppo.py` → `inviluppo.csv` | 1450 casi: i due rail × fc 10 k…1 MHz × ESR della tenuta 10…60 mΩ × ESR della scheda audio 0,05 / 0,2 Ω × cavo sì / no × carico 0,3 / 0,1 / 0,03 A × 0 / 25 / 60 °C (più la forma sul piedino per controllo) |
| `script/riassunto.py` → `riassunto.csv` | per rail e fc: il margine peggiore e il migliore, quanti sotto 60° e 45°, il caso peggiore |
| `script/anello_ti.py` | un caso col **modello di TI** di U501 (15,3 V sul piedino, 15,0 V sul rail), più un gradino di 50 mA sul rail |
| `script/inviluppo_ti.py` → `inviluppo_ti.csv` | 288 casi: la stessa griglia di rete, il + soltanto, le due forme |
| `script/zrail_ti.py` → `zrail.csv` | l'impedenza del rail nelle due forme, TI, caso nominale, da 10 Hz a 100 kHz |
| `script/confronta_t.py` | modulo e fase di due guadagni d'anello a confronto |
| `nominale.csv` | i controlli dello strumento e il caso nominale nei due modelli |

**La rete** (da `psu.py` e da `genera_tb_psu.py` di L45d2b2b1): C511 / C512 10 µF (5 mΩ) sul piedino;
l'SB340 `D(Is=8.7e-5 N=1.47 Rs=0.0136)`; C505 / C506 2200 µF a −20 % con l'ESR della tenuta; il cavo;
8 × (100 µF + 100 nF) sulla scheda audio, con le celle RC sul + (8000 µF dietro 1,25 Ω); il carico come
generatore di corrente (gli operazionali e il blocco tirano corrente quasi costante: nessuno
smorzamento, il caso prudente). Nel piccolo segnale il − è lo stesso circuito senza le celle.

**I controlli dello strumento**:
- un integratore senza rete: 10 kHz, **90,00°**;
- un polo RC (0,1 Ω, 1 mF) a fc 10 kHz: **3834 Hz, 22,54°** contro 3834 Hz e 22,55° a mano.

**I numeri** (dettaglio nel report):

| | Sul piedino | Sul rail |
|---|---|---|
| TI, carico di regime (48) | 90,1–90,9° | 51,0–108,8°, 9 sotto 60° |
| TI, tutti i carichi (144) | 88,8–90,9° | 20,6–108,8°, 82 sotto 60° |
| generico, regime, fc 10 k / 30 k / 100 k / 300 k / 1 M | 90° | il peggiore 22 / 24 / 32 / 43 / 59° |
| nominale TI / generico (fc 94 kHz) | 90,3° / 90° | 58,9° / 43,9° |

Il generico e il modello di TI coincidono sopra 30 kHz e si separano sotto: il rapporto del modello
di TI legge l'uscita dopo la sua resistenza da 4 mΩ (un anello locale che il generico non ha; con
`ro` = 4 mΩ il generico dà 43,6°, non 58,9°). Nessuno dei due è un limite: il regolatore vero ha
almeno un polo in più.

## Rifare

```sh
/usr/bin/python3 -I <A>/script/patch_tps7a4701.py <R>/vendor/ldo_regulator/ti/TPS7A4701/tps7a4701_trans.lib <R>/models/ldo_regulator/tps7a4701_ngspice.lib
/opt/homebrew/bin/ngspice -b <A>/prova/tb_limit.cir
/opt/homebrew/bin/ngspice -b <A>/prova/tb_u501_op.cir
/opt/homebrew/bin/ngspice -b <A>/prova/tb_u501_gradino_ds.cir
# lo strumento
/usr/bin/python3 -I <A>/script/anello.py <A>/strumento k_pin forma=pin fc=10e3 rete=rc:0.1:1m
/usr/bin/python3 -I <A>/script/anello.py <A>/strumento k_rc forma=rail fc=10e3 rete=rc:0.1:1m
# gli inviluppi (qualche minuto ciascuno)
/usr/bin/python3 -I <A>/script/inviluppo.py <A>/inviluppo <A>/inviluppo.csv
/usr/bin/python3 -I <A>/script/riassunto.py <A>/inviluppo.csv <A>/riassunto.csv
/usr/bin/python3 -I <A>/script/inviluppo_ti.py <A>/ti_griglia <A>/inviluppo_ti.csv
# il caso nominale e l'impedenza
/usr/bin/python3 -I <A>/script/anello_ti.py <A>/ti ti_pin forma=pin esr_hold=0.03 esr_audio=0.05 r_cavo=0 l_cavo=0 i=0.303373 temp=25
/usr/bin/python3 -I <A>/script/anello_ti.py <A>/ti ti_rail forma=rail esr_hold=0.03 esr_audio=0.05 r_cavo=0 l_cavo=0 i=0.303373 temp=25
/usr/bin/python3 -I <A>/script/anello.py <A>/strumento g_nom forma=rail fc=94360 esr_hold=0.03 esr_audio=0.05 r_cavo=0 l_cavo=0 i=0.303373 temp=25 celle=si
/usr/bin/python3 -I <A>/script/zrail_ti.py <A>/zrail <A>/zrail.csv 10 50 100 400 1000 3000 10000 100000
```

I deck generati, i log e le forme d'onda (`inviluppo/`, `ti_griglia/`, `ti/`, `strumento/`, `zrail/`,
~160 MB) non stanno nel repository: si rifanno coi comandi sopra.
