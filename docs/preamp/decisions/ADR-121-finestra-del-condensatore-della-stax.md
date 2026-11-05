# ADR-121 — Il condensatore della Stax: 1 µF ±5 %, capacità reale 0,895–1,265 µF; E8 e T5 riscritti

Data: 2026-11-05 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Precisa ADR-081** (punto 1, C165 / C365 da 1 µF ±5 %) dandogli la finestra ammessa, e **completa ADR-007**:
  «4,7 µF su tutte e tre le uscite» resta vero per la principale e la fissa 1, non per la Stax.
- Riscrive **E8** e **T5** (`REQUIREMENTS.md`), che dicevano ancora 4,7 µF su ogni uscita, e la frase della
  sezione 6 del dossier (`dossier/build_dossier.py`) che attribuiva il polo del banco `tb_ac` al
  «condensatore d'uscita da 4,7 µF (E8)». Chiude la parte di **NC-080** da fare prima di G1.

## Contesto

La revisione dell'architetto avversariale di L65 (`reports/2026-11-04-L65-architetto-avversariale.md`,
rilievo **R3**): C165 / C365 sono vincolati a ~0,97–1,2 µF (sotto cade E9, sopra cade PR-30), ma E8 e T5
dicono 4,7 µF. Chi segue E8 monta un condensatore che tiene la Stax sopra 0,87 V per ~538 ms.

## Decisione

Sulla fissa 2 il condensatore d'uscita è **1 µF ±5 %** in polipropilene, e la sua **capacità reale deve
stare in 0,895–1,265 µF**. Sono ammessi i valori nominali **1,0 µF e 1,1 µF a ±5 %**; non 1,2 µF ±5 %, non
un ±10 %. E8 e T5 lo dicono.

## Perché

Calcolo e corse in `data/2026-11-05/L72/` (`script/stax_finestra.py`, `stax/stax_limite_alto.csv`):

- **Il limite basso viene da E9** (±0,2 dB a 20 Hz) col carico della Stax: 50 kΩ ∥ 470 kΩ ∥ 470 kΩ =
  41,2 kΩ, più il polo d'ingresso (C_IN 1 µF su 470 kΩ ∥ 1 MΩ, 0,0027 dB). Il budget lascia 0,1973 dB al
  condensatore d'uscita: **C ≥ 0,895 µF**. Il modello a due poli ridà la simulazione del netlist di L60c2
  (0,147 / 0,161 / 0,178 dB a +5 % / nominale / −5 %) entro 0,001 dB.
- **Il limite alto viene da P10** (al più 150 ms sopra 0,87 V col carico della Stax, ADR-086, ADR-117). Il
  guasto peggiore è 124,5 ms a 1,05 µF (un JFET d'ingresso, L45d2b3b2b2); la durata di una scarica RC sopra
  una soglia è lineare in C, quindi **C ≤ 1,265 µF**. **Non assunto: simulato.** I cinque casi più lunghi (i
  tre JFET / Q146 di L45d2b3b2b2, i due di L66 sul blocco di oggi) rifatti a 1,05 µF ridanno le cifre versionate
  entro 0,1 ms, e a 1,265 µF danno **149,5 / 149,7 / 149,5 / 144,5 / 144,5 ms**, entro 0,4 ms dalla scala
  lineare. Il margine è nullo per costruzione: 1,265 µF è il limite.
- **Sul nominale**, con la tolleranza della parte: a ±5 % 0,942–1,205 µF, quindi 1,0 e 1,1 µF (1,1 µF: E9
  0,148 dB al −5 %, P10 137 ms al +5 %); a ±10 % 0,995–1,150 µF, e nessun valore della serie ci sta.
- La differenza dal «~0,97» dell'architetto: lui dava una cifra a occhio fra le righe della sua tabella
  (0,95 µF fa 0,176 dB); il limite esatto sulla capacità reale è 0,895 µF.

## Alternative scartate

- **Lasciare E8 com'era e scrivere l'eccezione solo in ADR-081**: E8 è il testo che si consulta montando la
  scheda; è lì che il valore sbagliato rompe PR-30.
- **Allargare la finestra con un ±10 %**: non ci sta nessun valore.

## Da riaprire se

- Cambia il carico della fissa 2 (un apparecchio diverso dall'SRM-T1, PR-30) o i bleed da 470 kΩ.
- Un guasto del blocco più lungo di 124,5 ms a 1,05 µF (il limite alto scende in proporzione).
- Il tetto di P10 cambia (ADR-117, «Da riaprire se»).
- Prima di G2: l'impronta di C165 / C365 deve essere distinta da quella di C162 / C362 (o la serigrafia
  marcata) — la parte di NC-080 che resta aperta.
