# L41b2 — il temporizzatore dell'alimentatore, il firmware (2026-09-26)

Dati del lotto L41b2 (NC-036, NC-038). Decisione: **ADR-050**. Report:
`docs/preamp/reports/2026-09-26-L41b2-temporizzatore-firmware.md`. Firmware:
`firmware/preamp_timer/` (`src/timer_core.c`, `test/`). Specifica:
`firmware/preamp_timer/spec/timer_spec.md`. Sorgente dell'hardware, **non toccato**:
`circuits/preamp/psu.py` → `psu.net`.

Le forme d'onda (`*_out.txt`, ~45 MB l'una) sono in `.gitignore`: si rifanno coi comandi sotto.
Si versionano i deck, i log, le uscite del core di ogni giro e le analisi.

## Le cartelle

| Cartella | Cosa |
|---|---|
| `deck/` | `genera_tb_psu.py` (copiato da L41b1, che resta com'era, ed esteso con `--nome seq` e `--cima`); `corri_seq.sh` (un caso fino al punto fisso), `tutti_seq.sh` (i sette in parallelo, poi l'analisi), `confronta.py` (due giri uguali?), `sano.py` (i pin di un alimentatore sano, per il giro 0), `analizza_seq.py` (i criteri, scritti prima delle corse), `analizza_ldr.py` |
| `ldr/` | il banco in continua delle LDR con la cima a 12 mA (ADR-050), senza calibrazione e calibrato (`cal_cima12mA.json`), anche coi LED al massimo e V5 a 4,90 V |
| `e3_e5/` | E3 ed E5 rifatti a 12 mA: `copia_12mA.py` copia il deck di L29b2 cambiando solo le correnti dei LED e le resistenze della cella in serie |
| `seq/` | le sette sequenze sul circuito col core come micro: una cartella per caso, coi deck, i log, `core_g<n>.csv` e `ponte_g<n>.txt` di ogni giro; `corri_<caso>.txt`; `analisi_seq.txt`, il verdetto |
| `falsi/` | `esito.txt`: i 21 falsi del core contro i test sull'host; `seq_falso6_guasto.txt` e `seq_falso9_spegnimento.txt`: due falsi fatti fallire anche sul circuito |

## Come si rifà

Dalla radice del repo:

```sh
/bin/zsh firmware/preamp_timer/test/run_host_tests.sh --falsi docs/preamp/data/2026-09-26/L41b2/falsi/esito.txt
/bin/zsh docs/preamp/data/2026-09-26/L41b2/deck/tutti_seq.sh       # ~10 min, sette ngspice in parallelo
```

`tutti_seq.sh` compila `test/ponte.c` col core (`corri_seq.sh --solo-compila`), poi per ogni
caso `corri_seq.sh <caso> 10`, che **svuota la cartella del caso** e itera:
1. `genera_tb_psu.py --nome seq` scrive il deck dalle uscite del core del giro prima
   (`core_g<n-1>.csv`): le PWL `set_` delle quattro richieste, `den_` e `dset_` del DAC, la
   corrente del micro;
2. ngspice lo fa girare e scrive quello che vedono i pin del micro (griglia di 100 µs);
3. il log si legge **prima** dei dati: `Error`, `singular`, `no such`, `non-increasing`,
   `Transient op`, `Timestep too small` rifiutano il giro (limitations #33, **#35**);
4. `ponte` fa girare il core su quei pin (un passo ogni 1 ms, più l'interruzione su ogni fronte
   di discesa di `MUTE_G_IN`) e scrive `core_g<n>.csv`;
5. se `core_g<n>.csv` è uguale a `core_g<n-1>.csv` (stesse righe, tempi entro 0,2 ms) e il ponte
   non ha dovuto ricostruire `MUTE_G_IN` nemmeno una volta, circuito e firmware concordano: è il
   punto fisso, e il deck di quel giro è il caso.

Il giro 0 è il core fermo nel suo stato di partenza: tutto a 0 per l'accensione dallo standby,
oppure MUTO o MUSICA raggiunti nel mondo dell'host (`mondo.c`) con l'errore del banco a 25 °C.

I casi (`corri_seq.sh`): `accensione` (dallo standby), `rilascio` (da MUTO), `inversione`
(un'inserzione invertita a metà), `spegnimento` (il frontale aperto in MUSICA), `buco20` e
`buco200` (rete assente 20 e 200 ms), `guasto` (U502 spento con la rete presente).

**Un falso sul circuito**: si compila il ponte con `-DFALSO=<n>` al posto di `--solo-compila`
(il comando è in `corri_seq.sh`), si fa girare `corri_seq.sh <caso>` e `analizza_seq.py`, poi si
rifà `tutti_seq.sh`, che ricompila il ponte vero e riscrive tutte le cartelle.

## Il banco (le differenze da L41b1)

Quelle dichiarate nell'intestazione di `genera_tb_psu.py` (il carico dei rail resistivo, il
contatto di K501 dietro un RC di 5 ms, i due interruttori come conduttanze), più tre correzioni
di L41b2, ciascuna col suo commento nel codice:
- **il codice del DAC in shutdown tiene l'ultimo valore**: il DAC spento è la sola sua 500 kΩ, e
  il codice non entra nella corrente. Col codice a 0 nello stesso µs dello shutdown la `tran` si
  fermava a 8,629 s nello spegnimento; con un fronte di 100 µs anche;
- **`gmin=1e-10`** (il default è 1e-12): con un core che spegneva a un altro istante (il falso 6
  nel guasto), la `tran` si fermava all'apertura di K501. `rshunt`, `maxord=2`, `trtol=1` e un
  modello liscio del MCP6004 non bastavano. 100 pS su una giunzione a 0,5 V sono 50 pA: lo 0,5 %
  dei 10 nA di riposo;
- **il ponte**: all'interruzione il pin `MUTE_G_IN` vale basso per definizione, senza
  ricostruzione. Letto per interpolazione proprio sulla soglia, valeva 2,5 V ± l'arrotondamento:
  il guasto alternava due giri senza punto fisso, e il buco di 200 ms chiudeva con una
  sostituzione.

## Le cifre

In `seq/analisi_seq.txt` (i criteri sono nell'intestazione di `analizza_seq.py`) e nel report.
