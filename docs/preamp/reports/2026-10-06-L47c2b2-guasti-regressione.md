# L47c2b2 — il mute coi soli relè: i guasti e la regressione

Data: 2026-10-06 · Lotto: L47c2b2 · Decisioni: nessuna ADR nuova; esegue ADR-062 col banco di
ADR-063. Dati: `data/2026-10-06/L47c2b2/` (README).

## In breve

- **I guasti dell'alimentatore reggono col mute che taglia.** La catena di L41c (NC-036, chiusa in
  L41c) ricorsa sull'alimentatore e sul firmware di L47c2a e sulla scheda audio senza celle:
  - lato alimentatore **9 casi su 9** al punto fisso, criteri di L41c compresi; il controfattuale
    senza Δ fallisce come deve;
  - lato jack, il peggiore è **U502 spento, 0,89 mV** (~52,5 dB SPL di picco a 1 m; obiettivo 2 mV,
    L46b 0,90); U501 spento 0,55 mV; lo spegnimento morbido **15 nV**; la perdita di rete ≤ 0,09 µV;
    il corto della linea a 12 V dei relè 29,7 mV, sotto il tetto (ADR-051).
- **Lo spegnimento lungo dura 1,1 s**, scelta dell'utente: a quel punto i rail sono a +0,83 /
  −0,81 V, le stesse cifre di L41c a 7,6 s.
- **La regressione**: i 21 deck veloci **uguali a L47c1 su 248 file su 248**; il firmware
  sull'host 76 controlli, **19 falsi su 19**; `run_tests.sh` **13 passed / 0 failed**.
- **Trovati e corretti nel banco** (nessuno nel circuito):
  - L47c2a aveva perso il `--angolo min` dei casi d'angolo;
  - la finestra del ponte per lo spegnimento era quella della sfumatura;
  - due script di L41c e di L47c2b1 leggevano male le colonne o i rail di oggi;
  - i due casi di U503 spento non finivano col metodo gear.
- **Non conformità**: nessuna aperta o chiusa. NC-050 resta aperta fino al carico congelato (G2).
  15 voci aperte, 4 bloccanti.

## All'inizio, con l'utente

**Quanto dura lo spegnimento lungo**, cioè il frontale aperto mentre suona la musica.

- In L41c durava fino a TE + 7,6 s: la sfumatura teneva chiuso il relè di rete fino a TE + 6,63 s,
  e la corsa finiva circa un secondo dopo.
- Col mute che taglia il relè di rete apre a TE + 0,13 s, e TE + 1,1 s copre lo stesso secondo.

**Risposta: «1,1 s»** (la consigliata). Misurato dopo: a TE + 1,1 s i rail valgono +0,83 / −0,81 V,
le stesse cifre di L41c alla sua fine.

## Il primo tempo: l'alimentatore

Gli script di L47c2a copiati in `psu/`. I criteri di L41c, che L47c2a aveva lasciato fuori, sono
stati **riportati prima delle corse**:

- r41: il jack si apre (al più tardi) prima che il guadagno possa muoversi (al più presto);
- s41: il jack si apre prima che V+ scenda a 10,6 V.

In L41c si chiamavano r ed s; sono rinominati perché il rilascio di L47c2a ha già una r. Per
`cf_nodelta`, C3 e r41 **devono fallire**.

**Trovato**: la copia di L47c2a di `corri_seq.sh` aveva perso il `--angolo min` dei casi `_min`. Il
generatore li avrebbe rifiutati con un errore: nessun dato sbagliato, ma la catena non sarebbe
partita. Ripristinato.

**Trovato: i due casi di U503 spento non finivano** col metodo gear (oltre 45 minuti, contro i ~2
degli altri casi). La sonda (`sonda_u503/`):

- fino a TE + 0,5 s il deck corre in 17 s; fermato a TE + 0,55 s non finisce;
- lì la linea a 5 V del micro è scesa a ~0,9 V, e tutto il suo dominio galleggia;
- in L41c su quella linea c'erano i carichi del pilota delle LDR, tolti da ADR-062;
- tutto quello che i criteri e il ponte leggono succede prima: il jack a +18,7 ms, il guadagno a
  +35,9 ms, V+ sotto 10,6 V a +253 ms.

Il rimedio è numerico, non tocca il circuito:

- **trapezoidale con `gmin=1e-9`** per i soli due casi di U503;
- fino a TE + 0,5 s dà le forme d'onda del gear: stessi istanti al passo di 0,1 ms, rail entro
  0,54 mV, nominale e angolo minimo;
- il trapezoidale da solo finiva il caso nominale ma non quello d'angolo; gear con `rshunt` o con
  un passo di 5 µs non finiscono;
- 1 nS su una giunzione a 0,5 V fa 0,5 nA, e senza le stringhe LED la scheda non ha correnti così
  piccole.

| Caso | MUTE_CMD | jack (tardi) | guadagno (presto) | V+ < 10,6 V |
|---|---|---|---|---|
| spegnimento lungo | 21,2 ms dopo il pin | +31,3 ms | +68,1 ms | +313 ms |
| perdita di rete (nominale, angolo) | 14,4 ms | +17,4 ms | +34,7 / +33,4 ms | +183 ms |
| U502 spento | 10,7 ms | — | — | — |
| U501 spento | 10,1 ms | +13,1 ms | +30,4 ms | +34,8 ms |
| U503 spento (nominale, angolo) | 15,7 / 15,3 ms | +18,7 / +18,3 ms | +35,9 / +34,3 ms | +253 ms |
| controfattuale senza Δ | 14,4 ms | +17,4 ms | **+14,4 ms** (fallisce, come deve) | +183 ms |
| corto della linea a 12 V (senza verdetto) | 0,1 ms | +3,1 ms | +0,1 ms | +183 ms |

## Il ponte e la scheda audio

**Il ponte** (`ponte/estrai_ponte.py`, da L41c) ha perso le correnti delle stringhe LED.

**Trovato: la finestra del ponte per lo spegnimento era quella della sfumatura**: partiva a
TE + 5,4 s. Con la fine a TE + 1,1 s sarebbe partita dopo i dati. Lo spegnimento ora prende la
finestra dei guasti, che parte 10 ms prima che il frontale si apra.

**La scheda audio**: `--matrice l41c` senza celle e col contatto in serie di ADR-063, 18 corse.
Tutte e 18 passano la guardia, partono dal punto giusto e contengono il loro evento: dopo il cambio
di guadagno l'uscita del blocco si sposta di ≥ 0,09 V in ogni caso. Due script ereditati non
erano adatti ai dati di oggi:

- **`verifica_eventi.py` di L41c** cercava le colonne delle celle. Sui file di oggi avrebbe saltato
  ogni riga e stampato 0 per ogni caso, cioè cifre piccole senza nessun evento dentro, in silenzio.
  Corretto; ora rifiuta un file senza righe della forma attesa.
- **`verifica_partenza.py` di L47c2b1** chiede 15 V tondi sul rail. Rifiutava tutte e 18 le corse,
  i cui rail vengono dal regolatore vero (+14,9997 / −15,0525 V). Ora confronta il rail col primo
  punto del ponte.

| Caso | L41c | L46b | **L47c2b2** | dB SPL di picco a 1 m | criterio |
|---|---|---|---|---|---|
| spegnimento morbido | 30,1 nV | 12,8 nV | **15,0 nV** | −43,0 | ≤ 100 µV |
| perdita di rete / angolo | 0,12 / 0,18 µV | 0,08 / 0,09 µV | **0,05 / 0,09 µV** | −27,3 | ≤ 2 mV |
| U502 spento | 1,37 mV | 0,90 mV | **0,89 mV** | 52,5 | ≤ 2 mV |
| U501 spento | 1,03 mV | 0,56 mV | **0,55 mV** | 48,3 | ≤ 2 mV |
| U503 spento / angolo | 75 / 75 nV | 75 / 75 nV | **52 / 15 nV** | −32,3 | ≤ 2 mV |
| controfattuale senza Δ | ≥ 66,5 mV | 29,7 mV | **29,7 mV** | 82,9 | deve superare 2 mV: **fallisce, come deve** |
| corto della linea a 12 V | 69,4 mV | 29,7 mV | **29,7 mV** | 82,9 | sotto il tetto di 0,87 V (ADR-051) |

**Rispetto a L46b**, l'ultima ricorsa, sono cambiate tre cose insieme:

- l'alimentatore, senza il pilota, e il firmware di L47c2a;
- la scheda audio, senza celle;
- il contatto in serie del banco, col fronte di 4,55 µs (ADR-063 vale anche per questo banco).

I due guasti che contano, U502 e U501 spenti, restano entro l'1,5 % di L46b. Sono la continua del
blocco che arriva al jack quando il guadagno cade prima del jack (L46b). Gli altri casi restano
ai nanovolt.

## La regressione

- **I 21 deck veloci** (`script/regressione.sh`, copiato da L47c1): rc 0 su 21. Confrontati con
  `L47c1/regressione/dopo`: **248 file su 248 uguali**. Era l'atteso: da L47c1 il circuito audio e
  i deck sono cambiati solo nei commenti.
- **Il firmware sull'host**: 76 controlli, 0 falliti, 9 test su 9; **19 falsi su 19**.
- **`run_tests.sh`**: **13 passed / 0 failed** (dal worktree, coi due commenti del sorgente
  aggiornati).

## Il sorgente

Solo due commenti, per la tracciabilità:

- in `gain_block.py`, il blocco «SUPPLY FAULTS AT THE JACK» ora cita L47c2b2 invece di L46b;
- in `preamp_audio.py`, lo spegnimento al jack punta ai dati di L47c2b2.

Nessun valore è cambiato. Nessuna modifica al PRB, ai requisiti, ai modelli, al firmware o al
dossier.
