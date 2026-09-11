# Preamplificatore — cosa manca per dirlo finito

**2026-09-11** · una pagina, in parole povere · il dettaglio sta in
`../NONCOMPLIANCE.md` e `../STATE.md`

---

## In una riga

Il progetto è **ancora sulla carta**: esiste uno schema completo e simulato,
non esiste ancora una scheda né un esemplare da ascoltare.

## Dove siamo

I requisiti sono congelati. Il circuito è scritto per intero in codice, e da
lì si generano schema e simulazioni senza passaggi manuali. Dodici banchi di
prova simulati producono dati veri, raccolti in un dossier. Ogni componente
attivo ha finalmente un modello fornito dal costruttore — **in libreria**;
nel circuito ci sono ancora i segnaposto.

Un registro tiene il conto di ciò che non va: **22 questioni aperte, 6
bloccanti**.

## Cosa manca, in ordine

**1. Sei punti bloccanti.** Finché restano aperti lo schema non si congela.

| | In parole povere |
|---|---|
| Il mute | com'è fatto oggi, a silenziamento inserito spinge lo stadio d'uscita fuori dal regime di funzionamento previsto |
| Stabilità (×2) | in due configurazioni il margine contro le oscillazioni è **sotto la soglia di 60°** che hai fissato il 10 settembre. Non è instabile: è sotto il margine di progetto |
| Rumore e distorsione | non hanno ancora numeri credibili, e non li avranno del tutto nemmeno con i modelli veri |
| Le due uscite fisse | non sono isolate fra loro: un apparecchio spento a valle si fa sentire sul resto |
| I componenti veri | sono entrati in libreria ma **non ancora nel circuito** |

**2. Rimettere i componenti veri nello schema e rifare le misure.** Tutte le
cifre attuali — stabilità, alimentazione, impedenze — vengono da modelli
provvisori e vanno rifatte. Si sa già di quanto sbagliano, e sbagliano in
direzioni opposte.

**3. Due funzioni chieste il 10 settembre e non ancora progettate**: il terzo
livello di guadagno (0 / +3 / +10 dB) e la regolazione fine dell'equilibrio
fra i canali, che deve funzionare solo a silenziamento inserito.

**4. L'alimentatore, e la sicurezza rete.** Non è ancora iniziato. Su un
apparecchio collegato alla presa, **senza un'analisi di sicurezza la
fabbricazione non si apre**: è una regola del progetto, non un'opinione.

**5. Poi, nell'ordine**: congelare lo schema → disegnare la scheda →
fabbricarla → montarla → ascoltarla. Ognuno di questi passaggi ha una
revisione che può rimandare indietro.

## Due cose da tenere presenti

**La simulazione non dirà mai come suona.** Copre in modo credibile
stabilità, rumore, risposta e impedenze. Non copre l'ascolto, e le cifre di
distorsione che si ottengono da modelli generici non sostituiscono una misura
su un prototipo reale.

**Non ci sono date.** Il lavoro procede a lotti piccoli, ognuno chiuso e
verificato prima del successivo: ne restano **undici** già identificati nella
tabella, più le fasi di cui sopra. Il vincolo non è tecnico — è quanto lavoro
entra in una sessione alla volta.

## Il segnale che le cose vanno nella direzione giusta

Le questioni bloccanti stanno **scendendo**: erano sette, ora sono sei. E
quasi tutte sono state trovate da controlli automatici o da riletture delle
fonti, non da un guasto scoperto tardi — che è esattamente lo scopo di tutta
questa impalcatura.
