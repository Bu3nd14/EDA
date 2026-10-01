# L46b — il PSRR del rail positivo (2026-10-01)

Report: `../../../reports/2026-10-01-L46b-psrr-rail-positivo.md`. Decisione: **ADR-056**. **Cifre
di modello, non misure**: conta il trend fra varianti sullo stesso banco.

Il banco è quello di L46a (`script/` copiato da `../L46a/script/`, la cartella base si ricava dalla
posizione dello script: la variabile si chiama ancora `L46A`). Le varianti partono da
`base/gain_block_flat_adr054.inc`, il blocco generato su `main` prima di L46b (c9078f65): il
sorgente ora contiene la cella, e le varianti non devono partire da lì.

| Percorso | Cosa |
|---|---|
| `script/varianti.py` | le varianti (dizionario `VARIANTI`, docstring col meccanismo): `ctrl` (nessuna modifica, deve ridare `vas56_cm470p` di L46a), `sv_*` cella su specchio e VAS, `s_*` solo specchio, `v_*` solo VAS, `svc_*` anche il cascode, `sv_molt_*` moltiplicatore di capacità, `*_esr0` condensatore ideale come nel sorgente, `sv_r10_esr0_r120_*` lo spazzamento di R120, `adr056_esr005` il blocco scelto con l'ESR prudente (la fonte della tabella di ADR-020) |
| `script/genera.py` | come in L46a, più la famiglia `clip` (`tb_dc_headroom`, `tb_v3_overload`) |
| `script/psrr_tab.py` | PSRR± minimo sui tre modi a 50 / 100 Hz, 1 / 10 / 20 kHz → `psrr.csv` |
| `script/quota_adr020.py` | il verbo di ADR-020 su uno spettro dei rail **limitato per eccesso** dai datasheet dei regolatori (ipotesi nella docstring) → `quota_adr020.csv` |
| `script/clip.py` | clip in continua a +10 dB e clip/recupero di V3 → `clip.csv` (venv) |
| `script/celle_netlist.py` | le otto celle lette da `preamp_audio.net` |
| `run/<variante>/` | le corse; `sintesi.csv`, `idss.csv`, `run/punto_di_lavoro.csv` |
| `regressione/prima`, `dopo` | i 21 deck veloci sul blocco di ADR-054 e su quello di ADR-056; `confronto_grezzo.csv`; `regressione/script/` gli script di L46a copiati senza modifiche |
| `l41c/` | la catena di L41c (solo il terzo tempo: deck della scheda audio coi ponti di L41c) ricorsa sul blocco di ADR-056: `deck/` (byte-identico a quello di L41c: il blocco entra da `gain_block.subckt`), `corse/`, `tabella.csv` |
| `l41c/var/` | la stessa catena sui sottocircuiti varianti: `adr054` (senza cella, il controllo che ha trovato la causa), `c470u`, `c220u`, `r4p7` (i due casi stretti), `r120_226` (tutti e nove) |

I `.dat` delle corse di `l41c/` e i deck che `dividi.py` rigenera sono in `.gitignore` (~6,3 GB).

**Per rieseguire** (dalla radice del repo):

```
/usr/bin/python3 docs/preamp/data/2026-10-01/L46b/script/varianti.py adr056_esr005
/usr/bin/python3 docs/preamp/data/2026-10-01/L46b/script/genera.py op,psrr,v1,clip,thd,imd,slew adr056_esr005
/bin/zsh docs/preamp/data/2026-10-01/L46b/script/esegui.sh <abs>/docs/preamp/data/2026-10-01/L46b/deck/lista_oppsrrv1clipthdimdslew.txt
/usr/bin/python3 docs/preamp/data/2026-10-01/L46b/script/psrr_tab.py ctrl adr056_esr005
/usr/bin/python3 docs/preamp/data/2026-10-01/L46b/script/quota_adr020.py ctrl adr056_esr005
/usr/bin/python3 docs/preamp/data/2026-09-23/L40/script/limiti_psrr.py docs/preamp/data/2026-10-01/L46b/run/adr056_esr005/tb_zout_psrr_noise tb_zout_psrr_noise 0db 3db 10db
/bin/zsh docs/preamp/data/2026-10-01/L46b/script/regressione.sh dopo
```

La catena di L41c, come nel README di L41c (passi 3-…), con `--ponte` sui JSON di
`../../2026-09-26/L41c/ponte/` e `--uscita` in `l41c/deck/`; il controfattuale si legge con
`../../2026-09-26/L41c/script/cf_fino_all_aborto.py`.
