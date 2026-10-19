# L60d2 — i guasti sulla Stax e V2 con la media (2026-10-19)

Seconda parte di L60d. Decisioni: **ADR-088** e **ADR-089** (nuove); applica ADR-086 e ADR-087. Dati:
`data/2026-10-19/L60d2/` (README lì). Cifre di modello, ngspice 47, i modelli di `models/`.

## Le decisioni dell'utente

- All'inizio, sulla media che attenua i 20 kHz di 0,63 dB: **«Correggere»** → ADR-088.
- Sui 17 guasti più lunghi che in L60c2, tutti sotto 150 ms: **«Accetta, sotto il tetto»** → ADR-089.

## 1. V2 con la media su ogni campione (ADR-087, ADR-088)

`scripts/v2_metodo.py`: ogni campione a 96 kHz è la media del segnale di ngspice, lineare a tratti e
senza diradamento, sull'intervallo centrato sul campione (`media_campioni()`, come `b1_confronto.py`
di L60d1); poi la correzione `[−a, 1+2a, −a]`, a = 0,0507. **La scelta che ADR-087 non aveva fatto**:
la media ha guadagno sin(x)/x, −0,63 dB a 20 kHz (28 corse della matrice su 155). Con la correzione:
0,000 dB a 20 kHz, +0,0003 dB a 1 kHz, al più +0,032 dB a 14 kHz. Il metodo di prima resta come
colonna `picco_puntuale_V` per A e B (`campiona(..., "puntuale")`).

- **Autotest** 27 controlli su 27; **sabotaggi** 15 su 15 presi (`sabotaggi_v2.txt`). Nuovi:
  - T16, un treno di impulsi da 134 ns a fase fissa: con la media B1 **3,28 µV** contro i 3,13 µV
    dell'area ideale; il metodo di prima **2,72 V**. Il sabotaggio `senza_media` lo fa cadere.
  - T17, toni da 12 V sulla griglia di ngspice: −0,0016 dB a 1 kHz, −0,0019 dB a 20 kHz; il
    sabotaggio `senza_correzione` lo fa cadere a −0,63 dB.
  - `lineare` e `senza_diradamento` mordono ancora (T7 controlla il metodo di prima, che resta).
- **Su corse vere** (`prova_metodo.txt`): sui riferimenti «sempre in mute» a 1 kHz e 20 Hz la media
  corretta, la media pura e il metodo di prima danno la stessa cifra alla quarta cifra.
- La suite non esegue `v2_metodo.py` (il 2k è il firmware): `run_tests.sh` non cambia.

## 2. I guasti sulla Stax (NC-069)

**Il banco.** Quello di L60c2 importato (`script/genera_L60d2.py`): i 107 modi di L60c2 più i 20
delle parti nuove (R150, R151, R152, R153 aperte e in corto; R112 e R144 in corto), sulle posizioni A
e F2, condensatore della Stax nominale e +5 %: 275 corse.

**Trovato per strada, e prima di tutto** (limitations #62): i deck di guasto di L45a non guastano il
blocco al volo, includono `L45a/inc/<modo>.subckt`, una copia scritta il 2026-10-13: **il blocco senza
ridondanza**. La prima corsa del banco provava R109 aperta senza R150. Se ne sono accorte solo le
corse dei modi nuovi, la cui copia non esisteva (ngspice cade in 0 s). Fermata, il generatore ora
riscrive le copie dal blocco di oggi in `inc/` e rifiuta una copia senza R150–R153. In L60c2 era giusto
così: il blocco era ancora quello di L45a.

**P10 sulla Stax** (`p10_stax.csv`, tetto 150 ms di ADR-086):

| Modo (la tabella di ADR-086) | L60c2 | **L60d2** |
|---|---|---|
| R109 aperta, A / F2 | 396–1217 ms | **0 ms** |
| R112 aperta | 140–149 ms | **0 ms** |
| R144 aperta | 117–130 ms | **0 ms** |
| Q133 in corto | 127–135 ms | **19–21 ms** |
| La source di JQ110B aperta | 140–149 ms | 110–124 ms |

- Le parti nuove, aperte e in corto: **0 ms**.
- **Nessun guasto oltre 150 ms**; il peggiore D102 / D103 aperti in A, **128,5 ms** (+5 %).
- JQ110B aperta in A, condensatore nominale, si ferma a 0,304 s («Timestep too small» su JQ110A),
  anche col gear, con `rshunt` e col fronte del guasto in 100 µs; con `reltol=3e-4` finisce: **118,5
  ms** (`p10_diagnosi.csv`), come la stessa corsa a +5 % (124,4).
- R120 in corto finisce a 0,6 s, come in L45b e L60c2 (22–26 ms).

**I guasti più lunghi.** 17 modi (34 corse), quasi tutti sul blocco A, durano di più che in L60c2:
D102 / D103 aperti da 98 a 128,5 ms, JQ110A in corto da 78 a 124, Q106 in corto, R107 in corto, Q121A,
R119, Q146 in corto; su F2 gli stessi, al più 116 ms. **La causa è R153**
(`script/diagnosi_peggio.py`):

| Blocco A, C nominale | blocco di L45a | oggi | oggi con R153 a 1 Ω |
|---|---|---|---|
| D102 aperto | 94,9 ms | 125,1 ms | 94,9 ms |
| JQ110A in corto | 74,9 ms | 118,5 ms | 74,9 ms |
| Q122 in corto | 118,0 ms | 118,0 ms | si ferma |

Senza il limite l'inseguitore del blocco guasto assorbe fino a 0,26 A dai rail e tiene l'uscita a
~6 V; col limite l'uscita va a 12,6 V. Q122 in corto non è peggiorato: in L60c2 la corsa si fermava a
6 ms (era segnata come limite inferiore). Il prompt chiedeva «non peggiorare»; l'utente: **«Accetta,
sotto il tetto»** (ADR-089). **NC-069 chiusa.**

## 3. P7

- **R123 e R126 a 56 Ω** in `spice/preamp/tb/tb_mute_corto.cir` (il deck le calcolava con 91 Ω, il
  valore di prima di ADR-054, in tutti e quattro i blocchi; il prompt citava solo R123): R123 da 14,3
  a **8,8 mW**, R126 da 10,4 a **6,4 mW**; ogni altra cifra uguale (`p7/p7.txt`). Il commento del
  sorgente su R123 («0.123 W», da P7 di L56 col 91 e senza R153) è aggiornato; il vincolo ≥ 0,13 W
  per la distinta resta.
- **R153 in corto** (`p7_r153cc.txt`): l'inseguitore torna senza limite, **Q146 0,41 W medi, 2,0 W di
  picco** (blocco B, +10 dB, mute o principale in corto), contro i 0,31 W del SOT-23 — le cifre di
  NC-071. Il resto di P7 resta nei limiti (Q125 0,19 W in SOT-223, i finali 0,39 W). È un guasto
  singolo con una conseguenza termica: **va a L45d2b3 dentro NC-042**, non è deciso qui.
  - Con R153 a 1 mΩ dieci celle (+10 dB, ingresso massimo, attenuatore 0,79) finiscono in un punto di
    lavoro sbagliato: i rail a 48 W, le correnti di ogni blocco divise per dieci, anche dei tre sani.
    Con 1 Ω le stesse celle tornano a 4,6–6,6 W, come L60d1 senza R153 (limitations #59). La cifra
    è quella con 1 Ω.

## 4. La matrice di V2 (NC-070)

Dal deck versionato (rigenerato, uguale), sul blocco di L60d1, 7 corse alla volta, ~6 h. **154 corse
su 155 passano la guardia**, come L48b: `off_r10m_d20_iii` si ferma anche col gear, ed è uno
spegnimento brusco escluso dal verdetto da L29d2 (in L60c2 le corse ferme erano sei).

- `verdetto.py`: **0 su 250 fuori** (L60c2: 16).
- **Uscita per uscita** da `analisi.csv` (`v2/peggiore_per_uscita.txt`), sulle grandezze col tetto:

  | | Principale | Singxer | Stax |
  |---|---|---|---|
  | B1 (sempre in mute) | **15,1 µV** (L60c2 174,6; L48b 16,9) | 5,9 µV | 58,2 µV |
  | B2g (jack grezzo in mute) | **28,4 µV** (L60c2 499; L48b 30,0) | 9,1 µV | **82,4 µV** |
  | A senza segnale | 19,2 µV | 2,2 µV | 12,7 µV |
  | Righe sopra 100 µV | **0** (L60c2 10) | 0 | 0 |

- **Col metodo di prima, sulle stesse corse, la principale sarebbe ancora fuori**: B1 104,1 µV, B2g
  240,4 µV. NC-070 si chiude per R153 *e* per la media di ADR-087 insieme; sulle fisse i due metodi
  coincidono entro pochi µV. Il «Da riaprire se» di ADR-087 (la principale fuori col metodo nuovo)
  non scatta. **NC-070 chiusa.**
- **La Stax a 20 kHz**: 82,4 µV, a 1,7 dB dal tetto (`mev_20k_iii`, la musica a 20 kHz a mute
  inserito). Non è nuova: L60c2 aveva 84,1 µV sulla stessa cella, ma il verdetto tiene solo l'uscita
  peggiore di ogni cella e la principale (173 µV) la copriva — la cifra «Stax, il peggiore 14,7 µV»
  di L60c2 non la vedeva (limitations #63). L48b, col condensatore da 4,7 µF e un contatto da 0,1 pF:
  11,1 µV. La differenza è il contatto aperto di K3 IM06TS, 1 pF.

## 5. Suite

`run_tests.sh` **13 passed / 0 failed** (2026-10-19, dal worktree): il circuito non cambia (solo due
commenti di `gain_block.py`), il deck di V2 rigenerato uguale, `tb_mute_corto.cir` corretto (fuori
dalla suite); firmware 19 falsi su 19.

## Cose trovate per strada

- **limitations #62**: i deck di guasto di L45a includono una copia del blocco scritta una volta.
- **limitations #63**: il verdetto di V2 tiene solo l'uscita peggiore di ogni cella.
- **limitations #60** aggiornata: `b1_confronto.py` di L60d1 importa `v2_metodo.py`, e da oggi la sua
  riga «v2» legge la media corretta.
- `G0_CTRL_F2` compariva due volte nella lista di L60c2 (due gruppi di L60c1 con lo stesso nome): una
  corsa sola in L60d2.

## Che cosa resta

- **L45d2b2** (il prompt in `NEXT-SESSION.md`), poi **L45d2b3**: lì R153 in corto (Q146 a 0,41 W) e le
  durate di P10 di questo lotto come punto di partenza.
- Sul prototipo: il jack della Stax a 20 kHz col mute inserito, che qui sta a 1,7 dB dal tetto.
