# L26 — Tre requisiti nuovi dell'utente diventano ADR-019

Data: 2026-09-10 · Lotto: **L26** · Decisione: **ADR-019**
Chiude: **NC-012** · Apre: **NC-021** (bloccante), **NC-022**, **NC-023**
Alza a bloccante: **NC-002**

---

## Il risultato in quattro righe

1. **Il margine di fase minimo è 60°, ovunque.** Chiude NC-012, che quella
   soglia la chiedeva — e con essa **due voci diventano decidibili, in
   negativo**: NC-002 (blocco A, 41,98°) sale a bloccante, e nasce NC-021
   (blocco B a 0 dB con cavo, 56,46°).
2. **Il trim funziona solo a mute inserito, con interlock elettrico.** Due
   comandi, il mute abilita il trim. È l'unica delle tre forme proposte che un
   banco possa provare.
3. **I livelli di guadagno diventano tre — 0, +3, +10 dB** — e a relè
   diseccitati il guadagno resta **0 dB**.
4. **Nessuna riga di topologia è stata scritta.** Questo lotto registra e
   apre lavoro; non ne esegue.

---

## 1. Perché è un lotto e non una nota

I tre requisiti sono arrivati in conversazione. Lasciarli lì significa
perderli: è la stessa ragione per cui `STATE.md` esiste, e il precedente è
**L8b**, dove due regole dell'utente diventarono ADR-016 e i requisiti T7/T8.

Il costo di non farlo si vede bene proprio su questi tre: **due invalidano
misure già pubblicate** e uno cambia la matrice di verifica. Un requisito che
vive solo in una chat non fa fallire niente — ed è il modo in cui un progetto
scopre a valle di aver misurato la cosa sbagliata.

## 2. Le tre domande poste prima di scrivere, e perché

Nessuno dei tre requisiti era ambiguo nell'intento. Due lo erano
nell'**estensione**, e in un caso l'estensione decide se il progetto è
conforme o no.

### Il margine di fase: a quale carico?

È la domanda che **NC-012 aveva già posto** senza risposta: «una soglia senza
il carico a cui si riferisce non è un requisito migliore». I 60° cadono in
posti molto diversi a seconda di dove li si applica:

| Se la soglia vale… | Il progetto oggi |
|---|---|
| al carico nominale | **conforme** (63,02° a vuoto) |
| anche al caso peggiore da 4,7 nF | **non conforme** (56,46°) |
| ovunque, blocco A compreso | **non conforme due volte** (56,46° e 41,98°) |

Risposta: **ovunque**. È la lettura più severa, ed è stata scelta
esplicitamente sapendo cosa comporta.

### Il trim: che forma ha l'interlock?

Tre forme possibili, di costo crescente: un vincolo di pannello (procedurale),
un mute che si inserisce da sé durante la regolazione, o un permissivo
elettrico sui relè del trim.

Risposta: **elettrico**. È l'unica **falsificabile**: si applica il comando
del trim a mute rilasciato e si verifica che non succeda nulla. Un vincolo di
pannello non si può provare, e il mute automatico avrebbe richiesto
temporizzazione, che ADR-009 (nessun microcontrollore) rende sgradevole.

### Il terzo livello: cosa succede a relè diseccitati?

Risposta: **0 dB**. Il principio di sicurezza di ADR-001/ADR-004 si conserva —
nessun guasto di bobina, e nessuno stato di accensione, può portare a un
guadagno più alto del minimo. Il valore esatto del gradino e il numero di relè
escono dal dimensionamento.

## 3. Cosa i tre requisiti costano al progetto

Dichiarato qui perché nessuna delle tre righe di `REQUIREMENTS.md` lo lascia
intuire.

### Il margine di fase: 18° sul blocco A non sono un ritocco

| Configurazione | Margine | Contro 60° |
|---|---|---|
| Blocco B, 0 dB, a vuoto | 63,02° | conforme |
| Blocco B, +10 dB, a vuoto | 86,09° | conforme |
| **Blocco B, 0 dB, 4,7 nF** | **56,46°** | **−3,5°** → NC-021 |
| **Blocco A, carico canonico, 4,7 nF** | **41,98°** | **−18°** → NC-002 |

I due numeri **esistevano già**: il primo rimisurato in L22, il secondo è
l'evidenza di NC-002 dal gate G0. Il requisito non ha scoperto niente di
nuovo — ha reso decidibile ciò che era già sul tavolo. È precisamente ciò che
NC-012 prevedeva.

Le strade per recuperarli costano tutte a un altro requisito: più
compensazione costa banda e slew rate; meno guadagno d'anello costa
distorsione, che è metà della ragione per cui ADR-003 ha scelto i discreti;
una rete d'isolamento diversa dai 47 Ω tocca E4 e ADR-008. **Va scelta coi
numeri di ciascuna**, ed è il lotto **L12**, che cambia natura: non più
«misura il blocco A coi valori veri» ma «portalo sopra soglia».

Una nota di onestà che appartiene al report e non al requisito: **41,98° non è
un circuito instabile**. La soglia a 60° è un margine di progetto — copre la
dispersione dei componenti, la capacità dei cavi che nessuno ha misurato, e i
modelli che non sono ancora tutti veri.

E va letta insieme a **NC-020**: il modello LS352 è più *lento* della parte
che il datasheet garantisce, quindi questi margini sono **pessimistici** — ma
di quantità ignota, quindi non si può concluderne che la parte reale passi.

### Il terzo guadagno: la matrice cresce, e con essa dodici deck

Il salto 0 → +10 dB è grosso, e il gradino intermedio serve. Ma:

- **la matrice V1 passa da tre a quattro configurazioni di blocco**, e si
  moltiplica per posizione dell'attenuatore, carico e sorgente;
- **i dodici deck spazzano due modalità**: ogni `foreach` che fa `0db / 10db`
  ne vuole tre, e chi li tocca incontra `limitations.md` #10 — un `$var` in un
  nome `wrdata` non si chiude da solo e fallisce **in silenzio**;
- **servono più relè o più poli**, quindi cambia il budget di corrente delle
  bobine per `psu-engineer` e cambia il pannello;
- **il diagramma a blocchi calcola il guadagno da R_f/R_g e lo asserisce**:
  `scripts/check_schematic.py` va esteso, non aggirato;
- **le cifre pubblicate a +10 dB restano valide** — quel livello non cambia —
  ma nessuna copre il livello nuovo.

**Il principio di ADR-004 non cambia e non deve**: si commuta R_g verso massa,
mai R_f, quindi l'anello non passa per il relè e non si apre mai. Con due rami
verso massa il principio si conserva per costruzione, e «riposo = 0 dB» lo
rende esplicito.

### L'interlock: il dettaglio su cui il progetto ha già sbagliato una volta

Il trim di ADR-011 **non esiste ancora** — è L16 — quindi l'interlock è tutto
da fare. Il punto delicato non è il permissivo in sé: è **quale contatto**.
I relè di mute sono a riposo in mute (ADR-012), quindi l'alimentazione delle
bobine del trim va presa dal contatto chiuso **in** mute, non da quello chiuso
a riposo.

È esattamente il tipo di errore che **NC-014** ha già prodotto sullo stesso
relè: il polo 2 invertito nel codice, perché le due lame pendono dalla stessa
parte ma le righe sono numerate in verso opposto. Per questo NC-023 prescrive
la verifica **sulla netlist**, come L21 farà per NC-014: un interlock che non
è stato provato a fallire non è un interlock.

## 4. Cosa questo lotto NON ha fatto

- **Non ha scritto una riga di topologia.** `circuits/preamp/` non è stata
  toccata: il diff non la nomina.
- **Non ha rimisurato nulla.** Tutti i numeri citati vengono da misure già nel
  repo — L22 per il blocco B, il gate G0 per il blocco A.
- **Non ha deciso come si recuperano i 18°.** Registra che vanno recuperati e
  che la scelta costa a qualcos'altro.
- **Non ha dimensionato il gradino a +3 dB** né scelto il numero di relè.
- **Non ha toccato il dossier**, che pubblica ancora 56,945° come caso
  peggiore, cioè un numero della topologia col THAT320. Il dossier va
  rigenerato **una volta**, dopo la Fase 4, e nel frattempo le sue cifre sono
  tracciabili alla directory dati da cui vengono.

## 5. Lo stato dopo questo lotto

**20 voci aperte, 7 bloccanti** — due in più di prima, e non perché il
progetto sia peggiorato: perché ora due misure che esistevano hanno un
confine contro cui essere giudicate.

| Voce | Stato | Lotto |
|---|---|---|
| NC-001 | bloccante | L11 |
| **NC-002** | **bloccante** (alzata qui) | L12 |
| NC-004 | bloccante | L6-L7 + riesecuzione |
| NC-010 | bloccante | L17 |
| NC-014 | bloccante | L21 |
| NC-017 | bloccante | L25 + Fase 4 |
| **NC-021** | **bloccante** (nuova) | L12 |
| **NC-022** | maggiore (nuova) | **L27** |
| **NC-023** | maggiore (nuova) | L16 |
| ~~NC-012~~ | **chiusa** | — |
