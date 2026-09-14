# L12 — Ogni istanza del blocco sopra i 60° (2026-09-14)

Lotto **L12**. Chiude **NC-002** e **NC-021** (bloccanti). Registra **ADR-024** e
**ADR-025**. Dati: `data/2026-09-14/L12/` (vedi il suo `README.md`).

## 1. La baseline, verificata prima di chiedere

I tre deck d'anello rieseguiti sui valori di L17:
- `tb_loop_blockA.cir` e `tb_loop_bufferfissa.cir`: tabelle e 24 curve
  **byte-identiche** a `data/2026-09-14/L17/`;
- `tb_loop.cir` (blocco B, sonda al jack): 56,46° a 4,7 nF riprodotti. **Nessun
  file dati LS352 esisteva**: `data/2026-09-09/tb_loop_*` è del THAT320.

**La cella che mancava.** Il blocco B non era mai stato misurato sul nodo.
`tb_loop.cir` ha preso una seconda sonda (`CNODE` su `OUT`) e la griglia a 8
punti. **Fatto fallire**: con `alter cnode` tolto, le 16 righe sul nodo restano a
63,0161° e 86,0157°, contro i 36,26° del deck vero. Le curve al jack differiscono
dalla baseline di ≤ 2,8·10⁻⁵ dB e 0,0006°, per il CNODE da 1 fF.

## 2. La domanda, e la decisione dell'utente (ADR-024)

Coi numeri delle due posizioni, e tre fatti: per il blocco A nodo e cavo
coincidono (va dritto al cablaggio dell'attenuatore, `preamp_audio.py:142-149`);
al jack il minimo non cade a 4,7 nF; ADR-019 mescolava già le due posizioni.

L'utente ha chiesto cosa fosse la sonda — «per me é il cavo di collegamento tra
il pre e il finale oppure tra il pre e gli ampli cuffia» — e, spiegato, ha
deciso: **«ogni cavo fino a 4,7 nF, blocco A con capacità realistica»**.

Il valore «realistico» per il blocco A è dell'orchestratore, dichiarato
all'utente: **≤ 1 nF**, dieci volte la stima di ≤ 50 cm a 100-150 pF/m. Il repo
non ha misure del telaio.

## 3. Il caso peggiore vero

Col criterio nuovo, e le celle di V1 che i deck non coprivano (sorgente
dell'attenuatore per il blocco B, sorgente phono per il blocco A):

| Istanza, valori di L17 | Minimo | Dove |
|---|---|---|
| Blocco B 0 dB | **54,97°** | attenuatore a metà corsa (2,5 kΩ), 2,7 nF |
| Blocco A, cablaggio ≤ 1 nF | 63,32° | phono 430 Ω, 1 nF |
| Buffer, al jack | 61,51° | Stax, 2,7 nF |

Solo il blocco B era sotto soglia, e peggio dei 56,46° che NC-021 citava.

## 4. La scelta del rimedio

Esplorazione in scratch con `alter`, tabelle in `data/…/L12/esplorazione/`.

**Più Miller o isolamento** (griglia fitta, minimo del blocco B a 0 dB):

| C124 / C137 / R_iso | Minimo | T a 20 kHz | Slew in discesa |
|---|---|---|---|
| 470p / 22p / 47 (L17) | 54,97° | 33,7 dB | 3,73 V/µs |
| 1n / 22p / 47 | 61,74° | 27,2 dB | 1,79 V/µs |
| 820p / 47p / 68 | 62,49° | 28,9 dB | 2,17 V/µs |
| 680p / 47p / 68 | 61,25° | 30,5 dB | 2,61 V/µs |

**Lo slew rate decide.** A +10 dB, 20 kHz e fondo scala (12 V pk, pendenza ideale
1,511 V/µs), tutti e tre i candidati con più Miller **vanno in slew** in discesa:
1,374 / 1,419 / 1,450 V/µs, con +0,38 / +0,20 / +0,09 V di continua in uscita.
Lo slew in salita coincide con I_coda/C124 (4,37 mA: 9,05 contro 9,3 V/µs a
470 pF), e questo valida la misura. I costi via `alter` sui deck versionati:
PSRR del rail + a 10 kHz −6,5 / −4,8 / −3,2 dB, E4 a 82 Ω a 20 Hz coi 68 Ω.

**Il C_f** (C137, in parallelo a R_f) non tocca né il polo dominante né lo slew:

| C124 / C137 / R_iso | Minimo | Agli spigoli (C ±5 %, R ±1 %) |
|---|---|---|
| 470p / 220p / 47 | 60,79° | — |
| **470p / 330p / 47** | **61,21°** | **60,73°** |
| 470p / 220p / 56 | 61,87° | 61,43° |
| 470p / 330p / 56 | 62,27° | 61,84° |

**Scelto: C137 = 330 pF, 47 Ω invariati (ADR-025).** È il cambiamento minimo
che passa anche agli spigoli, e non tocca reti d'uscita né deck. Il 330p con
56 Ω dava più guardia al prezzo di tre reti d'uscita, dei loro deck e di E4 da
61 a 70 Ω: resta scritto in ADR-025 come alternativa.

## 5. La consegna

- `circuits/preamp/gain_block.py`: `C("330p", OUT, FB)`, commento verso
  ADR-024/025; riepilogo LOOP e RESPONSE coi numeri nuovi.
- Rigenerati `gain_block.net`, `.subckt`, `_flat.inc`: una riga ciascuno,
  `C137 OUT FB 22p → 330p`; diff normalizzato del `.net`: solo il valore.
- `preamp_audio.net` rigenerato, ERC 0 errori. **Confronto semantico**: 357
  componenti, **8 valori cambiati** (C137, C236, C337, C436, C536, C636, C736,
  C836), 232 net e 862 nodi **identici come partizione**. La prima versione
  del confronto aveva letto 0 componenti — il parser non reggeva gli a capo del
  formato KiCad — e diceva «identiche: True»: scartata prima di fidarsene.
- `gain_block.svg` e manifesto rigenerati (44 dispositivi, 100/100 terminali).
- Deck: `tb_loop.cir` (sonda al jack e sul nodo, sorgenti 1 mΩ / 1 k / 2,5 k,
  griglia a 11 punti), `tb_loop_blockA.cir` (sorgente 430 Ω, criterio ≤ 1 nF
  nell'intestazione), `tb_loop_bufferfissa.cir` (1,5 / 2,7 / 3,3 nF in più).

## 6. I verdetti, sul circuito nuovo

`data/2026-09-14/L12/dopo/`, criterio ADR-024:

| Istanza | Minimo | Dove |
|---|---|---|
| Blocco B 0 dB | **61,21°** | 2,5 kΩ, 3,3 nF |
| Blocco B +10 dB | 102,96° | 2,5 kΩ, 4,7 nF |
| Blocco A | **63,36°** | 430 Ω, 1 nF |
| Buffer delle fisse | **61,63°** | Stax, 2,7 nF |

**Il buffer ha mostrato perché la griglia conta.** Sulla griglia a 8 punti di
L17 il minimo era 61,85° (2,2 nF); aggiunti 2,7 e 3,3 nF, 61,63°. Il deck è
stato esteso prima di registrare il numero.

Agli spigoli di tolleranza: blocco B 60,73°, blocco A 62,69°, buffer 61,16°.
Sul nodo, come informazione: blocco B 42,20°, blocco A 40,91° a 4,7 nF, buffer
40,97°.

## 7. Non regressione

| Controllo | Esito |
|---|---|
| `tb_op` | 79 valori identici a `data/2026-09-10/tb_op-LS352.log` (cambiano solo i nomi, rinumerati in L10) |
| `tb_blockA_carichi` | 108 righe, stato di classe A identico in ogni riga; blocco A a 14,356 mA, buffer F2 a 14,509 mA |
| `tb_mute_corto` | 440 righe, **0** con lo stato di classe A cambiato; MJE peggiore per blocco A/F/B 214,0 / 298,0 / 348,0 mW, come L17 |
| `tb_uscite_fisse` | E4 invariata; E5 1,666 µV (430 Ω) |
| `tb_zout_psrr_noise` | PSRR rail + a 10 kHz 39,78 / 29,83 dB (L18: 39,8 / 29,82); rumore peggiore 4,225 µV |
| `tb_noise_breakdown` | peggiore 4,2246 µV |
| `tb_switch_v2` | picchi +1,5202 / −1,6246 V, come prima |
| `tb_v3_overload` | recupero entro 1 µs, clipping +13,26 / −13,78 V |
| `tb_ac` | 0 dB: −0,007 dB a 20 kHz, −3 dB a 2,20 MHz; +10 dB: −0,053 dB a 20 kHz rispetto a 1 kHz, −3 dB a **183 kHz** (era 333) |

I limiti per tono di **ADR-020** restano validi: la PSRR non si è mossa.

## 8. Una trappola nuova

Il primo deck di slew (`tran` con `tstart`, poi `meas`) ha lasciato **vuote** le
colonne d'ampiezza con ngspice a rc 0: «ft_polyfit failed», «no such variable».
Visto contando le celle vuote, non dall'exit code. → **limitazione #26**.

## 9. Non conformità

- **NC-002 chiusa**, **NC-021 chiusa**.
- **17 voci aperte, 2 bloccanti** (NC-004, NC-017).

## 10. Visto e non toccato

- **Il riepilogo in fondo a `gain_block.py`** porta ancora cifre del THAT320 su
  rumore e punto di lavoro in altre righe: aggiornate solo LOOP e RESPONSE.
- **Il dossier** legge ancora `data/2026-09-09`.
- **La modalità +3 dB** non esiste (NC-022, L27): è l'unica riga di stabilità di
  V1 senza misura oltre al trim, e la rete di controreazione che L27 cambia è
  quella su cui lavora il C_f.
- **`CLAUDE.md`** parla di «18 limitazioni»: sono 26.
