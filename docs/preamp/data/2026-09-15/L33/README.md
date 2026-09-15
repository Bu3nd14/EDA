# Dati di L33 — le etichette di provenienza dell'LSK489 (2026-09-15)

Lotto **L33**, report `reports/2026-09-15-L33-provenienza-lsk489.md`. Chiude
**NC-031**. **Nessuna simulazione eseguita**: il lotto corregge frasi. Qui stanno
gli esiti del guardiano nuovo (blocco **2h**, `scripts/check_deck_provenance.py`)
e degli script che hanno contato, corretto e provato.

**La provenienza vera**, letta dagli `.include` dei deck:
- LSK489 = `LSK489X`, segnaposto con `KF = 0`
  (`spice/preamp/placeholder_devices.lib`);
- l'unico modello del costruttore è l'LS352 (`models/bjt_pnp/ls350.lib`), senza
  `KF`;
- nessun dispositivo simulato ha rumore 1/f.

## `prima/` — lo stato di `main`

| File | Cosa |
|---|---|
| `guardiano.txt` | 2h sui 17 deck di `main`: rc 1, 15 contraddizioni |
| `guardiano_6748fbc.txt` | 2h sui 16 deck di `6748fbc` (L12, prima di L27): rc 1, 14 |

## `dopo/` — i deck corretti

| File | Cosa |
|---|---|
| `guardiano.txt` | 2h sui 17 deck: rc 0 |
| `solo_commenti.txt` | 15 deck cambiati, ogni riga tolta o aggiunta è un commento `*`, righe di codice identiche a `main`: rc 0 |

## `esplorazione/`

| File | Cosa |
|---|---|
| `conta.py`, `conta.txt` | la baseline: 15 deck, 5 README espliciti e 2 impliciti, 1 copia datata fuori conto. `conta.txt` è girato **dopo** aver scritto il guardiano, la cui docstring cita la frase: è la riga `scripts/check_deck_provenance.py:11`, fuori conto |
| `correggi.py` | le sostituzioni esatte nei 15 deck; rifiuta se un testo non compare una volta sola |
| `solo_commenti.py` | la prova che il diff tocca solo commenti; fatta cadere su una copia con `VPP VPLUS 0 DC 16` (rc 1) |
| `annota.py` | le note in coda ai 7 README datati; rifiuta se la frase citata manca o la nota c'è già |
| `falsi/genera_e_verifica.py`, `falsi/esito.txt` | 11 sabotaggi del 2h, 11 su 11 come attesi |
| `falsi/c*.cir` | le copie sabotate, deck risolvibili con `@REPO@` |
