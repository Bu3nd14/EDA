# Prompt per la sessione successiva — L6

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L6,
e si ferma. Non iniziarne un secondo.

Leggi PRIMA, in quest'ordine, e non saltare:

  1. `CLAUDE.md` — ambiente, percorsi assoluti, trappole che falliscono
     in silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. `docs/preamp/STATE.md` — la sezione "Come si lavora da qui", la
     tabella dei lotti (ora con L16-L19), la sezione **L5e** e "Prossimo
     passo concreto"
  3. `docs/preamp/NONCOMPLIANCE.md` — **dodici voci aperte, 3 bloccanti**
  4. `docs/preamp/decisions/ADR-013-jfet-ingresso-lsk489.md` — è il
     mandato di questo lotto, passi 1-3
  5. `docs/limitations.md` **#13** — la trappola che morde proprio
     mentre si trascrive un modello

## IL LOTTO: L6 — LSK489, i passi 1-3 di ADR-013

È il lotto che rende credibili le cifre che oggi non lo sono, ed è il
rimedio alla non conformità bloccante **NC-004**: rumore e distorsione non
hanno evidenza finché i modelli sono segnaposto, e i contributori dominanti
previsti stanno nello **specchio di corrente**, cioè nella topologia. Non è
un dettaglio di componente.

  1. **Congela il datasheet** in `vendor/`, che oggi non contiene nessun
     PDF (13 sottodirectory, zero datasheet). `vendor/` è di sola lettura
     (`scripts/freeze_vendor.sh`, mode 0444).
  2. **Trascrivi il modello** in `models/jfet/`, che oggi ha solo
     `generic_njf.lib`.
  3. **Registra la provenance** nel sidecar `<file>.provenance.json` —
     convenzione in `models/PROVENANCE_CONVENTION.md`.

Poi `/usr/bin/python3 scripts/validate_models.py --check-provenance`.

## Quello che L5e ha già accertato su questo lotto, eseguendolo

Non riscoprirlo: è stato verificato il 2026-09-09 e ti fa risparmiare
mezza sessione. Ma **riverificalo prima di fidartene**, che è la regola.

**Le due sorgenti vendor esistono e si scaricano** (HTTP 200,
`application/pdf`), dalla pagina prodotto ufficiale
`linearsystems.com/jfet-amplifiers-duals/lsk489-series`:

| Cosa | URL | Nome dichiarato | Byte |
|---|---|---|---|
| Datasheet | `https://www.linearsystems.com/_files/ugd/7e8069_0e97881584d2424baa3f3ad67a624446.pdf` | `LSK489DSRevA38.pdf` | 530 957 |
| Modello SPICE | `https://www.linearsystems.com/_files/ugd/7e8069_668879111342422cbdbc172d1d2d9d75.pdf` | `Copy_LSK489A NJF.pdf` | 27 178 |

Nota: Mouser serve una revisione **più recente** del datasheet (RevA40,
04/12/2022) di quella servita dal produttore (RevA38). Va registrato nella
provenance, e **L7 deve confermare** che i limiti I_DSS/V_P non siano
cambiati fra le due revisioni.

**Il modello è una riga sola**, letta rasterizzando il PDF:

```
.model LSK489A NJF(Beta=2.2m Betatce=-.5 Rd=11 Rs=30 Lambda=4.3m Vto=-1.13
Vtotc=-2.5m Is=3f Isr=0 N=1 Xti=0 Alpha=30u VK=120 Cgd=3.19p Mj=0.32 Pb=0.8 Fc=0.5
Cgs=2.92p Kf=0.0009f Af=1 Gdsnoi=2.15 Nlev=3 Mfg=Linear_Systems)
```

**Verbatim ngspice la rifiuta in modo fatale**: `Mfg=Linear_Systems` viene
interpretato come espressione → `Undefined parameter [linear_systems]`,
`ERROR: fatal error in ngspice`. Rumoroso, non silenzioso.

**Tolto `Mfg`, ngspice accetta la riga ma ignora quattro parametri** con un
warning: `isr`, `alpha`, `vk`, `mj`. Sono raffinamenti PSpice/LTspice della
giunzione di gate e della corrente di saturazione. **Vanno dichiarati nella
provenance**, non ingoiati. I parametri di rumore che servono a NC-004 —
`Kf`, `Af`, `Nlev`, `Gdsnoi` — sono invece **accettati**, ed è il punto:
questo modello ha il 1/f che i segnaposto non hanno.

**Nel repo non c'è nessuno strumento PDF**: né `pdftotext`, né `pdftoppm`,
né `mutool`, `qpdf`, `gs`; niente `pypdf` nel venv. Funzionano `sips` e
`qlmanage`, ma **solo sulla prima pagina** — basta per il modello (una
pagina sola), **non basta per L7**, che deve leggere la tabella I_DSS/V_P a
pagina 2+ del datasheet. Se serve, `brew install poppler` va deciso con
l'utente, non fatto di iniziativa.

**Il metodo di trascrizione**, che è la parte che ADR-013 chiama il costo
accettato: **due letture indipendenti che devono coincidere**. Una visiva
(`qlmanage -t -s 2000` sul PDF congelato, poi si guarda l'immagine) e una
meccanica (script stdlib che decomprime con `zlib` i content stream del PDF
ed estrae i codici glifo dagli operatori `Tj`; su questo PDF i codici sono
GID con offset costante `+0x1D` rispetto a WinAnsi). Si confrontano
carattere per carattere. Se divergono, il lotto si ferma e lo dice.

**Attenzione a `docs/limitations.md` #13**: `"1M"` in KiCad è 1 MΩ, in
SPICE è 1 mΩ. Qui **non morde** — `2.2m`, `4.3m`, `-2.5m` sono milli in
entrambe le convenzioni, `3f`/`0.0009f` femto, `3.19p`/`2.92p` pico — e
proprio per questo va scritto: è il punto in cui qualcuno "correggerebbe"
un valore giusto.

## Una cosa che L6 deve fare e che non è nei tre passi

**Aggiungere la ricetta di test in `scripts/validate_models.py`.** Lo
script scopre i `.lib` da solo e marca `SKIP` quelli senza ricetta, **e uno
SKIP fa uscire 1** (righe 475-478 e 527): senza la ricetta `run_tests.sh`
diventa rosso e `chunk_close.sh` rifiuta. Modello da copiare: `tb_jfet()`,
righe 339-364, più la voce in `build_registry()`.

**Livello L6: fumo, non datasheet.** Due istanze, `Vgs=0` conduce e
`Vgs=-3` è interdetto, come fa il generico. Il confronto coi limiti
I_DSS/V_P del datasheet è **L7**, ed è il passo 4 di ADR-013: mescolarlo
qui cancellerebbe la ragione per cui i due lotti sono separati.

Conseguenza: la libreria passa da **24 a 26 check**. Aggiorna le citazioni
in `CLAUDE.md` (riga 124) e `README.md` (righe 140 e 298). **Non** i report
in `docs/preamp/reports/`: sono datati e immutabili.

## E una trappola che L6 attiva

`scripts/freeze_vendor.sh` ha `VENDOR_DIR` **cablato** su
`/Users/roberto/EDA/vendor` (riga 7). Eseguito da un worktree
congelerebbe il checkout principale e **non i file nuovi**, in silenzio. È
la stessa famiglia di `export_fab.sh` e `setup.sh`, che `STATE.md` dice di
sistemare «quando uno dei due verrà toccato» — e L6 lo tocca. È `/bin/sh`,
quindi niente `${0:A:h:h}`:

```sh
VENDOR_DIR="$(cd "$(dirname "$0")/.." && pwd)/vendor"
```

Poi eseguilo e **guarda** che i file nuovi siano 0444 nel worktree.

## NON fa parte di L6

**Correggere le non conformità.** Hanno i loro lotti — L11-L19 nella
tabella di `STATE.md`. In particolare le due bloccanti che non sono NC-004:

- **NC-001**, il mute che porta lo stadio d'uscita fuori dalla Classe A
  (L11);
- **NC-010**, aperta in L5e: le **uscite fisse non isolate** portano il
  Blocco A in Classe B se un apparecchio a valle si spegne (L17). È
  l'errore del diagramma a blocchi che l'utente aveva visto e che G0 non
  aveva trovato. Le due voci hanno la stessa fisica ma **non lo stesso
  rimedio**: chi chiuderà NC-001 con una resistenza in serie al contatto
  del mute non chiude anche NC-010.

**Non toccare `circuits/` né `spice/preamp/`**: il segnaposto `LSK489X`
resta dov'è, la sostituzione nella topologia è Fase 4. Nessun numero del
dossier deve cambiare in L6, ed è una proprietà da verificare
(`git diff --stat` non deve nominare `circuits/` né `docs/preamp/data/`).

## COME LAVORIAMO

  - Verifica invece di fidarti. Se un subagente riporta dei numeri,
    rieseguili tu prima di riferirmeli. È già servito tre volte.
  - **Cerca se qualcuno ha già deciso, prima di aprire una voce.** In L5e
    NC-009 stava per essere aperta come «serve una decisione di progetto»:
    ADR-015 l'aveva presa il giorno prima. La voce è diventata un'altra —
    più piccola e vera.
  - Niente cifre non eseguite. Una simulazione descritta e non lanciata
    non è evidenza.
  - Un lotto per volta, mai due agenti in parallelo: il vincolo è il cap
    di token del piano.
  - Lavora in un worktree. I commit non pushati dentro
    `.claude/worktrees/` spariscono col worktree, ed è già successo.
  - CHIUSURA. Non è una lista da ricordare, è uno script che rifiuta.
    Nell'ordine:
      1. aggiorna `docs/preamp/STATE.md` segnando **L6 fatto** e il lotto
         successivo come prossimo (la tabella deve dire `**fatto**`)
      2. riscrivi QUESTO file per il lotto successivo — se il titolo
         nomina ancora L6, lo script rifiuta, ed è il controllo che
         esiste apposta
      3. committa, pusha, apri la PR
      4. `/bin/zsh scripts/chunk_close.sh L6`
         Verifica tutto, merghia, riallinea il checkout dell'utente e
         **rilegge da lì** per provare il riallineo. Se rifiuta, ha
         ragione: sistema e rilancia.
      5. rimuovi il worktree con i due comandi che lo script stampa
      6. fermati. Non iniziare il lotto dopo.
