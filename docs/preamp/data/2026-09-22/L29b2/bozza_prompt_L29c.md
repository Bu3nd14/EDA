# BOZZA — prompt di L29c (scritta in L29b2, 2026-09-22; da rileggere dopo L39)

L'utente ha deciso di fare la Fase 4 (L39) **prima** di L29c. Questa bozza è il mandato
di L29c come stava a fine L29b2. Chi chiude L39 la riprende in `NEXT-SESSION.md` e la
aggiorna con i modelli del costruttore.

## Da dove si parte

- **Il criterio (ADR-040).** Il taglio con musica si giudica su **S, il salto di
  livello: ≤ 20 dB in 100 ms**, contato sopra −70 dB (il pseudo-mute del Technics).
  **C2 è diagnostica.** A e B restano a 100 µV, A senza segnale. Strumento:
  `scripts/v2_metodo.py`, righe `S_ins` e `S_rel`.
- **Il profilo del comando dei LED è la v4** (ADR-039, ADR-040). Serie: 20 mA → 0,2 mA
  (d 0–0,1) → 4,5 µA (0,45) → 0,19 µA (0,75) → 10 nA (0,8). Derivazione: 10 nA → 20 mA
  log-lineare su d 0,5–1. Td = 6 s, 10 nA di riposo, relè 0,5 s dopo d = 1.
- **Il guadagno si interblocca col mute come il trim** (ADR-041): solo a mute inserito,
  niente mute automatico, LED anche per il guadagno. L36 lo realizza.
- **Il deck versionato** `spice/preamp/tb/tb_v2_mute_ldr.cir` è **generato** da
  `data/2026-09-22/L29b2/deck/genera_tb_v2_mute_ldr.py`; si divide con
  `data/2026-09-22/L29b2/pavimento/dividi.py`.

## Il lavoro

Il caso peggiore di V2 col mute reale (LDR v4 più il relè al jack):
1. **I passaggi di guadagno** 0↔+3, +3↔+10, 0↔+10 dB nei due versi, **sotto mute**,
   seguiti dal rilascio: il **criterio 3 di ADR-030**, da cui dipende L36. A e S nei
   limiti.
2. **Il trim** nelle tre posizioni, con lo stesso schema.
3. **La dispersione dell'LSK489** fino a ±20 mV, in più posizioni dell'attenuatore.
4. **Mute breve e mute di almeno 2 s**. Il rilascio dopo un mute lungo parte dalla
   serie più buia.
5. **Accensione e spegnimento** con le rampe dei rail.
6. **Le curve A–D** del modello della LDR: la dispersione delle parti, per canale.

Esito: NC-028 si chiude se A, B e S reggono in tutta la matrice.

## Vincoli già pagati

- `set numdgt=15` prima di ogni `wrdata` (limitations #30); `pwl()` estrapola (#31).
- Le corse a 20 kHz con TMAX 0,5 µs valgono ore: vedi i tempi misurati in L29b2, nel
  report §8.
- Un LED senza percorso DC fa fallire l'op in silenzio (il 10 M del banco); i comandi
  dei LED sono log-lineari (col trapezio un gradino fa oscillare la cella); `analizza`
  accetta eventi solo per t > 0,3 s; `awk` col locale italiano non legge i `.dat`.
- `pkill -f` sul nome di uno script zsh prende anche i suoi subshell; `pgrep` con `\|`
  non vuol dire «oppure».
