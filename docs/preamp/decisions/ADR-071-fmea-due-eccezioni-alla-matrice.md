# ADR-071 — Due eccezioni alla matrice dei guasti: i relè di mute come gli altri relè, i guasti silenziosi del blocco alla diagnosi

Data: 2026-10-14 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- È il terzo caso del «Da riaprire se» di ADR-070: la matrice mette nella stessa classe casi che
  l'utente vuole trattare in modo diverso. ADR-070 resta com'è; queste due eccezioni le si
  affiancano.
- Le due domande stanno in testa a `data/2026-10-14/L45d1/scelte_L45d2.pdf` («Due domande prima
  delle scelte»), prima delle dieci scelte.

## Contesto

La matrice di ADR-070 dà la priorità da gravità, probabilità e rilevabilità. Su due gruppi di righe
il risultato lo decide un solo fattore.
1. **L'isolamento fra bobina e contatti dei relè di mute** (K2–K4, K3 della Stax: 4 modi, 0,25–
   0,75 FIT). Se cede, 12 V di continua restano sul jack per sempre (~135 dB SPL a 1 m), anche a
   mute inserito. La riga è a gravità 4 e probabilità 1, quindi esce **media**. Lo stesso modo sui
   relè del selettore e del trim (K13–K16, K7/K8) ha probabilità 2 ed esce **alta**: lì i relè sono
   di più.
2. **28 guasti del blocco dentro P10** (scelta 13 del PDF). Il colpo resta sotto 0,87 V, o sopra
   per meno di 100 ms, poi il blocco lavora degradato e nessuno se ne accorge. Escono **media**
   (gravità 3, latenti) e nessuno ha un rimedio.

## Decisione

Parole dell'utente (2026-10-14), sulle due domande: «Insieme, ad alta»; «Mandarli alla diagnosi».

1. **I 4 modi d'isolamento dei relè di mute passano ad alta priorità** e stanno nella scelta 6
   insieme a selettore e trim. Il rimedio è quello della scelta 6 (ADR-072).
2. **I 28 guasti del blocco dentro P10 si accettano per il colpo**, che sta dentro il criterio. Il
   **degrado silenzioso** che lasciano dietro va al lotto della diagnosi (**L58**): sarà quel lotto
   a decidere se e come renderli visibili (test point, autodiagnosi). Restano a priorità media.

Conteggio dopo questa ADR (`data/2026-10-14/L45d2a/decisioni.md`): **100 righe alte e 56 medie**,
contro le 96 e 60 di L45d1.

## Perché

- **Lo stesso effetto vuole lo stesso trattamento.** Fra i relè di mute e quelli del selettore la
  differenza è la sola quantità di relè. Il colpo è lo stesso, ed è il peggiore che il progetto
  conosca: permanente, e a mute inserito, cioè proprio quando chi ascolta si crede al sicuro.
- **Per i 28 guasti del blocco il criterio è rispettato.** Quello che manca è sapere che il blocco
  è guasto, e questo è il mestiere della diagnosi, il lotto nuovo chiesto dall'utente dopo L45d1.
  Il rivelatore di continua della scelta 1 (ADR-072) potrebbe vederne qualcuno, quelli con più
  continua al jack (fino a ~0,98 V): L45d2b li riconta.

## Alternative scartate

- **I relè di mute a media, come vuole la matrice**: la rarità avrebbe deciso da sola, su un colpo
  permanente.
- **Accettare i 28 guasti come sono**: il degrado silenzioso resterebbe senza nessuno che lo guardi.
- **Ricontarli solo dopo il rivelatore**: avrebbe lasciato la domanda aperta fino a L45d2b, e la
  diagnosi serve comunque per quelli che il rivelatore non vede.

## Da riaprire se

- Il tasso dei relè di mute risulta più alto (dati di campo, o un relè diverso): allora la matrice
  li darebbe già alta, e l'eccezione non serve più.
- La diagnosi (L58) trova che un guasto dei 28 non si può vedere a un costo ragionevole: si torna
  all'utente con quel guasto, non lo si lascia in silenzio.
