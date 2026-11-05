# 2026-11-05 — L72, i testi e le parti

Quattro rilievi dell'architetto avversariale di L65 (R2, R3, R6, R7), quattro non conformità (NC-080,
NC-081, NC-082, NC-084). Dati e script in `data/2026-11-05/L72/`; ADR-121…ADR-124. **Chiuse NC-081 e
NC-084**; NC-080 e NC-082 restano aperte **per G2 soltanto** (le impronte). Il circuito cambia solo nel
campo di tolleranza di dodici resistenze; nessun valore, nessuna rete.

## 1. Il condensatore della Stax (NC-080, ADR-121)

`script/stax_finestra.py` (il calcolo di L61 copiato ed esteso) prima ridà i numeri noti: il carico 41,2 kΩ,
le perdite a 20 Hz simulate in L60c2 (0,147 / 0,161 / 0,178 dB) entro 0,001 dB, i 115 ms dell'architetto.

- **Limite basso, E9**: con 0,0027 dB del polo d'ingresso, al condensatore restano 0,1973 dB: **≥ 0,895 µF**
  reali. Il «~0,97» dell'architetto era una lettura a occhio della sua tabella.
- **Limite alto, P10**: 124,5 ms a 1,05 µF, scalato a 150 ms: **≤ 1,265 µF**. Verificato sulle corse:
  `script/genera_stax.py` copia i cinque casi più lunghi (tre di L45d2b3b2b2, due di L66 sul blocco di oggi)
  cambiando solo CFIX2; 10 corse, rc 0, ~5 s l'una, 3 alla volta a `nice 10`.

  | caso | versionato a 1,05 µF | ricorso a 1,05 µF | a 1,265 µF | scala lineare |
  |---|---|---|---|---|
  | JFET d'ingresso, D-S (blocco A) | 124,5 | 124,4 | **149,6** | 150,0 |
  | JFET d'ingresso, lato retroazione | 124,4 | 124,5 | **149,7** | 149,9 |
  | Q146 C-E | 124,2 | 124,2 | **149,5** | 149,6 |
  | D158 in corto (buffer della Stax) | 120,0 | 120,0 | 144,5 | 144,6 |
  | Q132 B-E (buffer della Stax) | 120,0 | 120,0 | 144,5 | 144,6 |

  (`stax/stax_limite_alto.csv`, ms sopra 0,87 V.)
- **Sul nominale** a ±5 %: 0,942–1,205 µF. **Ammesso solo 1,0 µF ±5 %** (1,1 µF non si trova); 1,2 µF ±5 % e
  1,0 µF ±10 % stanno dentro per 5 nF, senza margine, e non si ammettono.
- **E8 e T5** riscritti; la frase della sezione 6 del dossier che chiamava «condensatore d'uscita da 4,7 µF
  (E8)» il polo del banco `tb_ac` ora dice che è il banco, e dà le cifre della Stax.

## 2. La lista ammessa (NC-082, ADR-122)

`script/finestre.py`: finestre per posizione, E9 a 20 Hz con ogni condensatore della catena al basso a −5 %
(principale 0,128 dB, fissa 1 0,150, fissa 2 0,179), lo scarto fra i canali a 20 Hz dai ±5 % (≤ 0,032 dB),
E12 con 0,1 V ai capi (τ_IR ≥ 52 / 235 / 26 s). La ricerca dei tipi: `bom-component-manager`,
`distinta/README.md`, solo DigiKey e datasheet (Mouser, TME, Farnell, RS, LCSC non raggiungibili).
Riletti a campione dall'orchestratore: WIMA MKP4D046806F00JSSD (6,8 µF / 100 V, PP, ±5 %, 31,5 × 15 × 26,
648 pz) e Vishay CMF55845R00BEEB (0,1 %, 25 ppm/K; la potenza è data come 0,6 W e come 1/2 W sulla
stessa pagina, entrambe sopra 0,25 W): conformi.

| Posizione | Finestra | Raccomandato | Il più grande |
|---|---|---|---|
| ingresso, C171–C174 / C371–C374 | 1,0–2,2 µF, R_isol ≥ 10 GΩ | TDK B32672L2105J003 | 26,5 × 7 × 16,5 (1 µF); 26,5 × 11 × 21 (2,2 µF) |
| C_T, C265 / C465 | 6,8–10 µF | WIMA MKP4D046806F00JSSD | 41,5 × 19 × 32, passo 37,5 |
| principale, C262 / C462 | 2,2–10 µF | Panasonic ECW-FD2W475J | 31,5 × 15 × 26, passo 27,5 |
| fissa 1, C162 / C362 | 4,7–10 µF | Panasonic ECW-FD2W475J | 41,5 × 19 × 32 (col 10 µF) |
| fissa 2, C165 / C365 | solo 1,0 µF ±5 % | TDK B32672L2105J003 | 26,5 × 7 × 16,5 |

Esclusi: Panasonic ECW-FE a 2,2 µF (4,5 GΩ, sotto i 10 GΩ dell'ingresso), KEMET R76 (solo ±10 %). Per C_T
un solo costruttore con ±5 % e codice letto.

## 3. Le resistenze allo 0,1 % (NC-081, ADR-123)

`script/e10_caso_peggiore.py` ridà le cifre dell'architetto all'1 % (0,237 / 0,257 / **0,494 dB**); allo 0,1 %
il peggiore è **0,049 dB** (+10 dB col trim a −12 dB). Sorgente: `gain_block.TOL_GAIN` sui tre resistori del
blocco commutato, `trim.TOL_TRIM` sulla scala, come campo `Tolerance`. Netlist rigenerati
(`script/rigenera.sh`): `confronta_netlist.py` li trova uguali a main salvo il campo, sulle dodici parti
attese (653 parti, 396 reti). `run_tests.sh` **14 passed / 0 failed**. Distinta: TE/Neohm YR1B (845 e 464 Ω
non in scorta) o Vishay CMF55 …BEEB (scorta zero, 26 settimane): nessuna serie 0,1 % ha i cinque valori in
scorta a DigiKey.

## 4. La principale e le Heresy (NC-084, ADR-124)

`script/principale_potenza.py` (la convenzione di NC-028, che ridà 136,6 / 140,1 dB SPL della FMEA): il
finale satura a 21,9 V di picco, **113,8 dB SPL** di picco; al diffusore al più 30 W col seno, 60 W in onda
quadra. Klipsch pubblica 100 W continui / 400 W di picco per Heresy III e IV; della Heresy I nessun
documento Klipsch raggiungibile (le copie del manuale rispondono 403; fonti secondarie 100–105 W, un
proprietario 25 W per una coppia del 1966).

**Le scelte dell'utente**: «100 W, ipotesi dichiarata»; sul testo di PR-30 «Firmo così». P10 riscritta; la
tabella della FMEA nel dossier scrive «il finale in clipping» sopra 113,8 dB SPL, con la cifra lineare.

## Non fatto qui

- Il dossier non è rigenerato (è L74): le correzioni a `build_dossier.py` si vedranno lì.
- Le impronte (C165 / C365 distinta, i pezzi più grandi della lista): G2; la prova di spazio è L73.
- La potenza della Heresy I letta sul pezzo: ipotesi dichiarata, «Da riaprire se» di ADR-124.
