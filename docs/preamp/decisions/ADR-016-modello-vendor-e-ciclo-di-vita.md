# ADR-016 — Nessun componente a fine vita, nessun dispositivo attivo senza modello vendor

Data: 2026-09-10 · Stato: accettata

## Contesto

Il lotto L8 (`reports/2026-09-10-L8-parti-nuove.md`) ha verificato alla
fonte le quattro parti nuove del progetto e ne ha trovate due in stato
inaccettabile:

- il **THAT320**, array PNP dello specchio di corrente d'ingresso, è
  **fine vita dal 2026-09-01**, con last-time buy che chiude il
  **2026-09-30**;
- **2N5401** e **2N5551** — VAS, cascode, generatori di corrente,
  moltiplicatore di Vbe: **cinque istanze per blocco** — non hanno alcun
  modello SPICE del costruttore raggiungibile, e nemmeno un PDF vendor
  contenente testo `.MODEL`.

L'utente ha risposto il 2026-09-10 che **l'approvvigionamento entro il
30 settembre non è possibile**, e ha posto due regole.

## Decisione

**Due regole di progetto, non due verdetti su tre parti.**

1. **Nessun componente a fine vita entra in questo progetto.** Un
   annuncio di EOL già pubblicato squalifica la parte, anche se esiste
   una finestra di last-time buy.
2. **Ogni dispositivo attivo del percorso di segnale deve avere un
   modello SPICE del costruttore.** Vale per **tutti** i dispositivi
   attivi, non solo per quelli che L8 ha esaminato.

Diventano i requisiti **T7** e **T8** in `REQUIREMENTS.md`.

**Conseguenze immediate**, che questa ADR registra e non discute:

| Dispositivo | Stato | Esito |
|---|---|---|
| LSK489 | modello vendor **sì** (PDF, trascritto in L6, validato in L7) | **resta** |
| THAT320 | fine vita | **sostituire** |
| 2N5551, 2N5401 | nessun modello vendor | **sostituire** |
| MJE15032, MJE15033 | modello **non confermato** (Fase 1: «pagina models esiste, file finale non confermato») | **verificare, e sostituire se manca** |
| 1N4148 | mai verificato | **verificare, e sostituire se manca** |

## Perché

**Sulla regola 1.** Un last-time buy risolve l'approvvigionamento e non
risolve il progetto. Ciò che si compra il 30 settembre è uno stock
finito e non riacquistabile: la prima riparazione fuori garanzia, la
seconda coppia di schede, o una revisione futura ripropongono lo stesso
problema in un momento peggiore, quando il pezzo non è più ordinabile da
nessuno. Un progetto che ADR-006 costruisce apposta perché sia **un solo
blocco riusato quattro volte** amplifica il difetto per quattro.

Vale la pena notare che ADR-013 aveva già scritto la clausola di riapertura
giusta — *«oppure l'LSK489 esce di produzione»* — ma solo per il JFET.
Nessuno l'ha applicata all'array. Il memo THAT era pubblico dal 1°
settembre e ADR-013 è dell'8: **la regola c'era, mancava il controllo**.
La regola 1 esiste perché quel controllo diventi obbligatorio invece che
implicito.

**Sulla regola 2, e qui i numeri ci sono.** Oggi **sei dispositivi attivi
su sette** nel percorso di segnale sono modellati da segnaposto scritti a
mano (`spice/preamp/placeholder_devices.lib`), il cui stesso file
dichiara: nessuna cifra di THD ricavata da lì ha significato, e `KF = 0`
ovunque, quindi non esiste rumore 1/f. È la ragione per cui **NC-004** è
bloccante.

E i segnaposto non sbagliano tutti nello stesso verso, il che è peggio
che sbagliare molto:

| Dispositivo | Segnaposto dichiara | Datasheet |
|---|---|---|
| `PTHAT320` | `TF = 1,5 ns`, «f_T ~ 100 MHz» | **325 MHz** tip. → ~3× **lento** |
| `NSS2N5551` | `TF = 0,5 ns`, «f_T ~ 300 MHz» | **100 MHz min**, misurato a 10 mA mentre il circuito lavora a 2-6 mA → ~3× **veloce** |

Un margine di fase calcolato con entrambi **non è conservativo in modo
noto**: non si sa nemmeno da che parte sbagli. Sono le cifre di NC-002 e
NC-012.

**Perché la regola vale anche per MJE15032/33 e 1N4148**, che L8 non
aveva nel mandato: sono i **dispositivi d'uscita** e il riferimento di
polarizzazione del rail negativo. Un modello d'uscita sbagliato è
esattamente ciò che rende priva di significato una cifra di distorsione,
perché lo stadio d'uscita è dove la non linearità di incrocio vive. Una
regola che si ferma alle parti già esaminate non è una regola, è
l'elenco di ciò che si è guardato.

**Cosa costa questa decisione, dichiarato e non nascosto.** Non è una
sostituzione di righe di BOM:

- lo specchio di corrente d'ingresso va **riprogettato**, non
  ri-approvvigionato: cambia il punto di lavoro dello stadio d'ingresso e
  cambiano le cifre di rumore, perché il THAT320 portava appaiamento
  monolitico e rbb = 25 Ω;
- se i due MJE cadono, **lo stadio d'uscita è una modifica di topologia**,
  non un cambio di package;
- **tutte le cifre attuali di polarizzazione, margine di fase, PSRR e
  Z_out sono da rifare** dopo la sostituzione. Erano già provvisorie —
  vengono da segnaposto — ma smettono di essere anche solo indicative.

Il guadagno che paga il costo è che **NC-004 diventa chiudibile davvero**:
con modelli veri su tutto il percorso, le cifre di rumore e distorsione
smettono di essere un pavimento dichiarato tale.

## Cosa questa ADR supera, e cosa no

**Non supera ADR-013**, che riguarda il JFET d'ingresso: l'LSK489 ha un
modello del costruttore e non è a fine vita, quindi soddisfa entrambe le
regole e resta. **NC-013** — il modello descrive un esemplare d'angolo a
bassa I_DSS — resta aperta e non c'entra con questa decisione.

**Il THAT320 non era oggetto di una decisione.** ADR-013 lo nomina una
volta sola, di passaggio, dentro la discussione di un'alternativa
scartata: «lo specchio si fa meglio con PNP appaiati o con l'array
THAT320, che ha la migliore provenienza SPICE di tutto il giro». È
entrato nella topologia come **scelta implementativa** in
`circuits/preamp/gain_block.py` che citava quella parentesi. Non c'è
quindi una decisione da superare: c'è una scelta implementativa da
rifare, e questa ADR è la prima a trattarla come una decisione.

Vale come nota di metodo: **una parte che entra citando una parentesi non
ha mai avuto un'istruttoria.** È il motivo per cui il suo stato di ciclo
di vita non era stato controllato da nessuno.

## Alternative scartate

**Last-time buy del THAT320 entro il 2026-09-30.** Scartata dall'utente
per due ragioni: l'approvvigionamento entro la finestra non è
praticabile, e un componente a fine vita non entra in un progetto nuovo.
Era la strada più economica sul breve — nessuna riprogettazione, nessuna
cifra da rifare — e la meno sostenibile sul lungo.

**Tenere 2N5401/2N5551 con un modello generico dichiarato tale.** È lo
stato attuale, e ha il pregio dell'onestà: il file dei segnaposto dichiara
per esteso cosa non si può affermare con essi. Scartata perché lascia
NC-004 aperta per sempre: nessuna cifra di distorsione del progetto
diventerebbe mai credibile, e la distorsione è metà del motivo per cui
ADR-003 ha scelto i discreti.

**Usare un modello di terze parti** (i mirror GitHub di modelli attribuiti
a Central Semiconductor). Scartata perché **un mirror non è provenienza**:
è precisamente la regola che ADR-013 impone per l'LSK489 — si congela ciò
che il **costruttore** ha servito, con il suo URL e il suo hash. Accettarlo
qui svuoterebbe la procedura là.

**Limitare la regola alle parti già esaminate.** Scartata: vedi sopra —
sarebbe l'elenco di ciò che si è guardato, non una regola.

## Da riaprire se

Nessun candidato soddisfa entrambe le regole per una funzione necessaria
— cioè se per lo specchio, per il VAS o per lo stadio d'uscita non esiste
alcuna parte in produzione con modello del costruttore. In quel caso la
scelta è fra rilassare la regola 2 per quella singola funzione, **con la
lacuna dichiarata accanto a ogni numero che ne dipende**, e cambiare
topologia per non aver bisogno di quel dispositivo.

Si riapre anche se una parte scelta sotto queste regole viene dichiarata
fine vita più tardi: allora non è la regola a sbagliare, è il momento in
cui il controllo va rifatto — e va rifatto **a ogni gate**, non una volta
sola.
