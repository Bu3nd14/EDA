# L56 — i guasti dell'alimentatore col blocco di ADR-067 (2026-10-12)

La catena di L51b (`../../2026-10-09/L51b/`, il suo README dice come è fatta), ricorsa perché L56 ha
cambiato la corrente e la continua d'uscita del blocco di guadagno (ADR-067: +1,27 mA per rail per
blocco; continua −6,6 → −2,9 mV). Report `../../../reports/2026-10-12-L56-specchio.md`, §6.
`<A>` = questa cartella, alla stessa profondità di L51b perché gli script ricavano la radice dalla
posizione. Gli script sono quelli di L51b salvo le tre differenze sotto; le uscite di L51b che qui
non si rifanno (il confronto con `L51b-prima`, la termica, i falsi del firmware, i sabotaggi del
dossier) sono state tolte dalla copia.

## Le differenze da L51b

| File | Cambio |
|---|---|
| `carico.txt` | rail **303,76 / 311,928 mA** (8 × `tb_op` del blocco di ADR-067, `../L56/regressione/dopo/tb_op/`), contro 293,62 / 301,7864; il resto di `VRELAY` invariato |
| `psu/corri_seq.sh` | **un tetto di 150 s per passo e un solo ripiego**: se un passo cade per «Timestep too small» o supera il tetto, si rifà una volta con l'altro metodo d'integrazione (gear ↔ trap + `gmin` 1e-8), scritto in `seq/<caso>/ripiego_g<N>.txt`; ogni altro errore, o un secondo fallimento, resta rifiutato |
| `psu/genera_tb_psu.py` | accetta una chiave facoltativa `metodo_u503_min` (oggi non usata: il ripiego la rende inutile) |
| `sonda_u503/prepara_l56.py`, `corri_l56.sh` | la sonda della numerica di `guasto_u503_min`, sul passo 1 (`esiti_l56.tsv`) e sul passo 2 (`esiti_l56_g2.tsv`) |

**Perché il ripiego.** Col carico di L56 `guasto_u503_min` cade al passo 1 con gear (dopo un lungo
avanzare a passi minimi, «Timestep too small» a 2,47 s su `b.xu508b.bq`) e al passo 2 con trap +
`gmin` 1e-8 (2,93 s, `b.xu502.bi`); ogni passo finisce con l'altro metodo (`esiti_l56*.tsv`). Anche
`perdita_min` cadeva al passo 1 con gear (2,86 s). È lo stesso caso al limite della numerica di
L47c2b2 e L51b: L51b ha mostrato che i due metodi danno il jack, il guadagno e V+ < 10,6 V agli
stessi istanti e i rail entro 0,5 mV. Ripieghi effettivi: `perdita_min` giro 1, `guasto_u503_min`
giro 1 (`ripiego_g1.txt` in ciascuno).

## Le cifre

- **I banchi** (`rete/`, `guasti/`, `timer/`): tenuta di VRELAY_REG ≥ 11,4 V a rete −10 % 48,3 ms
  (L51b 48,3; P9 ≥ 25); rail + a 13,5 V dopo la perdita 62,9 ms (65,5); valle del grezzo − 17,84 V
  (17,89); VRELAY a J1 < 9,6 V dopo PERMIT con U503 spento 35,9 ms (35,9); il temporizzatore passa,
  nominale e all'angolo minimo (i due «errori» `t_permit out of interval` sono quelli attesi di L47c2a).
- **Le 14 sequenze** (`seq/analisi_seq.txt`): **VERDETTO: PASSA**; il controfattuale senza Δ fallisce
  come deve.
- **La scheda audio** (`tabella.csv`), picco al jack principale: U502 spento **14 µV** (16,4 dB SPL;
  L51b 0,815 mV, 51,7), U501 spento 0,136 mV (36,1; L51b 0,517 mV, 47,7), corto della linea a 12 V
  **6,4 mV** (69,6 dB SPL; L51b 14,9 mV, 76,9), controfattuale senza Δ 6,4 mV (fallisce come deve).
  Tutti sotto i tetti. La continua più piccola del blocco porta meno salto al jack quando i relè del
  guadagno cadono prima di quello del jack.

## Rifare

```sh
/bin/zsh <A>/psu/genera_tutti.sh
/bin/zsh <A>/psu/corri_tutti.sh            # due «errori» attesi: t_permit out of interval (L47c2a)
/usr/bin/python3 <A>/psu/analizza.py <A>/rete
/usr/bin/python3 <A>/psu/analizza.py <A>/guasti
/usr/bin/python3 <A>/script/analizza_timer_in.py <A>
/bin/zsh <A>/psu/tutti_seq.sh              # ~15 min col tetto e i ripieghi
/bin/zsh <A>/script/catena_audio.sh        # ~2 min
/usr/bin/python3 <A>/sonda_u503/prepara_l56.py ; /bin/zsh <A>/sonda_u503/corri_l56.sh      # la sonda, passo 1
/usr/bin/python3 <A>/sonda_u503/prepara_l56.py 2 ; /bin/zsh <A>/sonda_u503/corri_l56.sh 2  # passo 2
```

Nella prima corsa di `tutti_seq.sh` (prima del ripiego) `perdita_min` e `guasto_u503_min` erano
cadute; sono state rifatte una per una con `corri_seq.sh <caso> 10`, poi `analizza_seq.py` su tutte.
Le forme d'onda sono in `.gitignore`.
