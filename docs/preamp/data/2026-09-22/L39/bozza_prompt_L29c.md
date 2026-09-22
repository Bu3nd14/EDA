# BOZZA — prompt di L29c (L29b2, aggiornata in L39 il 2026-09-22; da rileggere dopo L40)

La bozza di L29b2 (`data/2026-09-22/L29b2/bozza_prompt_L29c.md`) resta com'era. Questa è
la stessa, portata ai modelli del costruttore di L39. **L29c viene dopo L40**: V1 cade coi
modelli veri (NC-034), e L40 cambia la compensazione o il guadagno minimo. Misurare il caso
peggiore di V2 prima vorrebbe dire rifarlo. Chi chiude L40 riprende questa bozza in
`NEXT-SESSION.md` con i valori che L40 avrà scelto.

## Da dove si parte

- **I modelli (L39).** Ogni dispositivo attivo è il modello del costruttore di `models/`
  (LSK489A, MMBT5551, MMBT5401, LS350, Qmje15032, Qmje15033, D1N914). Solo l'LSK489A ha
  KF; nessun modello porta la dispersione. Le cifre di V2 portano quell'etichetta.
- **Cosa è cambiato per V2 in L39** (1 kHz, 100 k, principale, `data/2026-09-22/L39/`):
  - S 7,163 / 5,32 dB, come prima: lo decide il profilo delle LDR;
  - A senza segnale ≤ 3,75 µV, B2 0,33 µV;
  - il **fondo di distorsione della catena** (C_pav) scende da 0,96 a **0,27 mV**;
  - l'offset del blocco B da −16,58 a **−15,45 mV** (per il criterio 3 di ADR-030).
  L40 cambierà di nuovo questi numeri: rimisurare la cella di riferimento prima della
  matrice.
- **Il criterio (ADR-040).** Il taglio con musica si giudica su **S, il salto di
  livello: ≤ 20 dB in 100 ms**, contato sopra −70 dB. **C2 è diagnostica.** A e B restano
  a 100 µV, A senza segnale. Strumento: `scripts/v2_metodo.py`, righe `S_ins` e `S_rel`.
- **Il profilo del comando dei LED è la v4** (ADR-039, ADR-040). Td = 6 s, 10 nA di
  riposo, relè 0,5 s dopo d = 1.
- **Il guadagno si interblocca col mute come il trim** (ADR-041). L36 lo realizza.
- **Il deck versionato** `spice/preamp/tb/tb_v2_mute_ldr.cir` è **generato** da
  `data/2026-09-22/L29b2/deck/genera_tb_v2_mute_ldr.py` (che da L39 prende gli include del
  costruttore da `tb_v2_mute_graduale.cir`); si divide con
  `data/2026-09-22/L29b2/pavimento/dividi.py`. Per correre una sola cella c'è
  `data/2026-09-22/L39/script/v2_cella.sh`.

## Il lavoro

Il caso peggiore di V2 col mute reale (LDR v4 più il relè al jack):
1. **I passaggi di guadagno** 0↔+3, +3↔+10, 0↔+10 dB nei due versi, **sotto mute**,
   seguiti dal rilascio: il **criterio 3 di ADR-030**, da cui dipende L36. A e S nei
   limiti. Se L40 alza il guadagno minimo, i livelli da passare sono i suoi.
2. **Il trim** nelle tre posizioni, con lo stesso schema.
3. **La dispersione dell'LSK489** fino a ±20 mV, in più posizioni dell'attenuatore. Col
   gruppo B via `altermod` e sonda (limitations #29), come `tb_idss_*.cir`.
4. **Mute breve e mute di almeno 2 s.**
5. **Accensione e spegnimento** con le rampe dei rail.
6. **Le curve A–D** del modello della LDR: la dispersione delle parti, per canale.

Esito: NC-028 si chiude se A, B e S reggono in tutta la matrice.

## Vincoli già pagati

- `set numdgt=15` prima di ogni `wrdata` (limitations #30); `pwl()` estrapola (#31).
- Le corse a 20 kHz con TMAX 0,5 µs valgono ore (L29b2, report §8). In L39 le corse a
  1 kHz coi modelli veri sono durate 3–9 minuti l'una, circa 1,5–3 volte quelle sui
  segnaposto, con 11 in parallelo su 10 core.
- **Il manifesto non è l'elenco delle corse** (L39): `rele_*` rilegge i dati di `ev`,
  `pav_*` quelli di `evp`/`invp`. Una cella si estrae dalla colonna `file`.
- Un LED senza percorso DC fa fallire l'op in silenzio; i comandi dei LED sono
  log-lineari; `analizza` accetta eventi solo per t > 0,3 s; `awk` col locale italiano
  non legge i `.dat`. `v2_metodo.py analizza` su 11 corse a 1 kHz impiega minuti.
- `pkill -f` sul nome di uno script zsh prende anche i suoi subshell; `pgrep` con `\|`
  non vuol dire «oppure».
