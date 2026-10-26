# Prompt per la sessione successiva — L54b2, il temporizzatore sul sorgente: il modello del costruttore, lo standby, la catena al jack

Nome della sessione: **hi-fi preamp L54b2** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura della prima parte di L54b (2026-10-26). L54b è stato diviso dall'utente
> all'inizio, «Tre parti»: la prima (il sorgente, i guardiani, i disegni, il banco sul sorgente col
> suo caso noto) è fatta; questa è la seconda; la terza (**L54b3**) è la robustezza al banco. L'ordine
> deciso con l'utente: L54 → **L54b2** → L54b3 → L55 → L58 → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L54b2**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Dove siamo

Il temporizzatore di ADR-102 è nel sorgente: `circuits/preamp/psu.py`, U513–U515 (TLV1704 sul
simbolo LM339), C545–C555, R569–R584, D533–D541, Q513 / Q514 (la ritenuta); il micro, il firmware e
il loro test non ci sono più. Il banco dell'alimentatore legge il temporizzatore dalla netlist:
`data/2026-10-26/L54b1/psu/genera_tb_psu.py --timer sorgente` (README della cartella). I casi di L54a
coi comparatori — sequenza, guasti, consumo — sono già stati rifatti sul sorgente come caso noto
(`an_sorgente.csv`, `an_fmea_sorgente.csv`, il confronto in `confronta_noto.txt`): **non vanno rifatti
qui**, si parte da quei numeri.

## Che cosa fare

1. **I comparatori col modello del costruttore** (`vendor/comparator/ti/TLV1702/tlv1701.lib`, il
   TLV1701: canale singolo, lo stesso dado del TLV1704; la provenienza in `PROVENANCE.json`). Prima
   il modello da solo, nel circuito in cui sta (limitations #76: alimentato da V5 dietro i suoi
   pull-up, non da una sorgente ideale) e con la modalità di compatibilità giusta (#72); poi un
   `--comparatore costruttore` del banco che mette il sottocircuito al posto di `CMPOD` sui dodici
   canali del temporizzatore (e, se il deck regge, sui sei di U505–U508), e i casi della sicurezza
   contro il comportamentale: `perdita` / `_min`, `guasto`, `guasto_u501`, `guasto_u503` / `_min`,
   `cf_nodelta`, i tre sorveglianti ciechi, `ritenuta_frontale`, `accensione_u501`, `buco20` /
   `buco200`, alle tre reti dove la rete conta. Un deck che cambia si confronta coi numeri, non col
   codice d'uscita (#76).
2. **Lo standby** (NC-037): i pull-up delle uscite tenute basse in standby (R573 `MUTE_REQ`, R575
   `PERMIT_REQ`, R579 `MAINS_REQ`, R576 il nodo «acceso» e quelli che lo seguono) alimentati solo da
   acceso, nel sorgente con le loro ragioni; la cifra dal secondario di T2 alle tre reti contro
   **116,1 / 130,1 / 144,2 mW** (rete −10 / 0 / +10 %, sul sorgente: `consumo_sorgente*`; le cifre
   ±10 % stampate da L54a e in ADR-102, 116,7 / 145,1, non si rifanno: report di L54b1 §4). Se la scelta di come alimentarli ha più di
   una strada ragionevole, si porta all'utente coi numeri prima di cambiare il circuito. Con il
   sorgente che cambia: il controllo dei relè, i disegni, il caso noto strutturale da riallineare.
3. **La catena al jack** dello spegnimento dal frontale e della perdita di rete (il ponte di L41c),
   contro 33,9 / 39,2 nV del dossier, in dB SPL (memoria «Bump in dB SPL»).

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#72**, **#73–#76**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di L54b1.
- **ADR-102**; il report `reports/2026-10-26-L54b1-temporizzatore-sorgente.md`; i README di
  `data/2026-10-26/L54b1/` e `data/2026-10-25/L54a/`.

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti, le pipe o i `;` attorno a comandi che eseguono
  script; `cd … && script`; le variabili di shell nei percorsi e nei cicli; `xargs` sulla riga di
  comando; `awk` con programmi, heredoc, `python3 -c`, script lunghi sulla riga di comando (scriverli
  su file); `sed` con valori calcolati; un titolo di PR con l'apostrofo (il corpo su file,
  `--body-file`); un `git` con `-C` dentro un comando composto. Comandi semplici, **percorsi
  assoluti**, script scritti con Write, Edit per i testi.
- Il generatore di L54a senza `--net` legge la netlist nuova: per rifare L54a serve `--net
  data/2026-10-26/L54b1/psu_prima.net` (README di L54b1).
- Le corse: la memoria (limitations #75) decide il parallelo; commit e push prima di una lista lunga;
  le forme d'onda grandi non si committano.
- Le domande all'utente si fanno per nome, senza sigle (al più fra parentesi); i colpi al jack in dB
  SPL; ogni opzione con la sua cifra contro il limite della parte, alle tre reti dove la rete conta.

## NON fa parte di questo lotto

- **La robustezza al banco** (la rete sporca, i fronti veloci, i rimbalzi, il Monte Carlo, la
  temperatura): **L54b3**, col prompt che questa sessione scrive alla chiusura (il punto 7 del
  prompt di L54b, parola per parola nel report della prima parte, §«Per L54b3»).
- Le righe della FMEA delle parti nuove e la diagnosi in hardware (ADR-076, ADR-078): L58.
- Il dispositivo d'uscita (L55), il dossier (L64), la revisione (L65), G1.
- Le decisioni prese non si riaprono, salvo che un «Da riaprire se» della loro ADR scatti.

## CHIUSURA

1. `STATE.md` con L54b2 **fatto** nella tabella dei lotti, e il prossimo (L54b3).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per L54b3 col punto 7 del prompt di L54b intero (dal report
   della prima parte, §«Per L54b3»), con la riga
   «Nome della sessione: hi-fi preamp L54b3» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L54b2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
