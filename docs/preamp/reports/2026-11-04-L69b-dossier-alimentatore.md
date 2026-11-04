# L69b — l'evidenza dell'alimentatore e il dossier sul sorgente nuovo

Data: 2026-11-04 · Lotto: L69b · Decisioni: nessuna ADR. Dati: `data/2026-11-04/L69b/` (README). Nessuna
non conformità aperta o chiusa; NC-050 invariata (il dato di oggi è quello di L64b). Il circuito non
cambia: è quello di ADR-116 (L69).

## In breve

- **Il primo giro** (`rifiuti_primo_giro.txt`): **124 rifiuti**, tutti l'evidenza di L64b sul circuito di
  prima: 120 sequenze e i deck dei banchi `rete` e `guasti` (il deck rigenerato ha le due metà dei pull-up,
  quello corso la resistenza unica), e `parti_schede.csv` (118 / 189, R588 / R589 in più).
- **Le corse**, sul banco di L64b copiato, 09:04–09:32: **117 sequenze**, lo standby, i banchi della rete e
  dei guasti, il calore, il ponte e la catena al jack alle tre reti; **tutte rc 0**, ogni `ok.txt` con la sua
  riga. Al più tre simulazioni insieme, a priorità bassa.
- **La seconda strada contro L64b** (`confronta_l64b.py`, nuovo): **7578 celle, 386 diverse**, ognuna
  spiegata nel README. Le cifre del dossier alla cifra stampata sono quelle di L64b: `VRELAY_REG` **50,3 /
  109,6 / 169,1 ms** (P9 ≥ 25), il permissivo **39,6 ms**, la musica **612,8 ms** dopo un buco di 20 ms,
  K501 **75,6 ms** dopo il permissivo, al jack U501 spento **32,2 dB SPL**, a rete −10 % **+4,3 dB SPL**, il
  calore **17,68 / 15,42 / 19,98 W** (57,7 °C a 3 cm nel caso peggiore, come L64b); lo standby **115,9 /
  129,8 / 143,9 mW** (+0,02).
- **La seconda strada contro i lotti** (`confronta.py`): **4255 celle, 0 fuori**, i 107 deck di L58b uguali
  a quelli di oggi a meno del carico e delle due metà; per arrivarci, uno scarto dichiarato su tre colonne
  (sotto).
- **Il dossier**: «OK: tutti i controlli incrociati sono passati»; **sabotaggi 67 su 67** (i 61 di L68 sui
  file di oggi, più sei nuovi).

## Trovato

- **L'armo della ritenuta arriva 0,6–0,7 ms prima** (`t_arm_ms`, `arm_pg_ms`; e la base della ritenuta,
  `bn_max`, 0,3 mV): sono le colonne che leggono AT_ON, e contro L58b uscivano dalla tolleranza di un'unità
  della cifra (68 celle). Il meccanismo l'ho misurato, non supposto (`armo.py` → `armo.txt`): AT_ON alto
  4,471 V, 51 µA nel pull-up, 20 Ω in meno (9,98 kΩ invece di 10 kΩ, ADR-116) lo alzano di 1,02 mV; AT_T2S
  si carica da AT_ON con 2,7 MΩ / 1 µF fino a VREF (2,47 V), e 1 mV in più anticipa l'armo di **0,76 ms**.
  In `confronta.py` lo scarto di ADR-116 vale solo per quelle tre colonne (1 ms, 0,5 mV). Il criterio
  (l'armo dopo l'alimentazione buona, `arm_pg_ms` > 0) resta largo: 1625,8 ms.
- **L58b non è più «lo stesso circuito»**: la pagina lo diceva in due punti; ora dice L58b col `psu.py` di
  prima dei pull-up in due metà, e le due metà lette come la resistenza unica nel controllo dei deck (che
  rifiuta se le due righe non ci sono una volta).
- **`PSU_DA` al 2026-11-04**: ogni dato di L64b sulla prima strada viene ora rifiutato dal generatore; L64b
  si legge solo da `vecchio()`, come seconda strada (provato con un sabotaggio).

- **Due sabotaggi di L68 passavano** sul `main` di L69: toccavano le righe di R572 / R576 in corto di
  `fmea_l68.csv` (NC-079), che L69 ha sostituito con le sue e che non entrano più nella FMEA di oggi. Non
  è un buco del generatore (una riga sostituita non arriva in pagina), ma il sabotaggio non provava più
  niente: riportati su una riga di L68 ancora viva, e cadono.

## Errori

- Il primo `armo.py` leggeva la forma d'onda come coppie tempo / valore (il formato di `wrdata` senza
  scala unica): zero punti; il file ha una sola colonna del tempo. Corretto prima di usarne il numero.
- I comandi composti dal worktree (`git` con altro, `cd` + `git add`) rifiutati o partiti dalla cartella
  sbagliata: rifatti uno per uno con `git -C`.
