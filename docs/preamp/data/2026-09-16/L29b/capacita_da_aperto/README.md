# L29b, passo 1 — la capacità da aperto dell'elemento in serie

**Verifica di un calcolo, non una misura di V2.** Analisi AC di piccolo segnale,
senza filtro e senza transitorio, sul blocco `* >>> CANALE` di
`spice/preamp/tb/tb_v2_mute_graduale.cir` così com'è su `main` a 2471bab.
SIMULATO, modelli segnaposto (NC-017).

## Perché

L'elemento graduale ideale di L29a (posizione `g4`) è una conduttanza pura da
1e-12 S, senza capacità, e a mute inserito il jack non va a massa. Un elemento
reale ha una capacità da aperto. Il calcolo diceva: 1 pF vale ≈ 8 MΩ a 20 kHz, e
contro i 100 k ‖ 220 k della principale lascia passare ≈ 100 mV, contro i 100 µV
di B.

## Come

- `build.py` legge le prime 181 righe del deck (fino a `* <<< CANALE`).
- Sostituisce la sorgente del tono con una sorgente AC unitaria, e mette l'elemento
  in serie nello stato «mute inserito»: SSER = 1, `RBY*` = 1e12, bleeder lato
  condensatore 220 k / 470 k, come `g4`.
- Aggiunge:
  - `CF*`, la capacità da aperto in parallelo all'elemento: 1 fF, 0,5, 2, 10 pF;
  - `RSH*`, una derivazione jack–massa: assente (1e12) o contatto chiuso (0,1 Ω).
- Guadagno +10 dB. Carichi 100 k e 10 k su tutte le uscite. 20 Hz, 1 kHz, 20 kHz.
- `coff.csv`: modulo di V(jack) per 1 V alla sorgente. Per il tono di prova si
  moltiplica per 3,818 V di picco.

Rigenerare: `/usr/bin/python3 build.py` (scrive `coff.cir` in un percorso assoluto
dello scratch del job: correggerlo), poi `/opt/homebrew/bin/ngspice -b coff.cir`.
Il CSV viene scritto nella directory corrente.

Controllo di coerenza: con 1 fF la principale a 100 k e 1 kHz dà 5,4 µV di picco
non filtrati. L'elemento ideale senza capacità ne darebbe ≈ 0,8 µV calcolati, e
L29a ha misurato B = 1,65 µV filtrato. Stesso ordine: il banco non è rotto.

## Esito, al tono di prova (× 3,818 V), di picco, non filtrato

| Caso | Principale 100 k 1 kHz | Principale 100 k 20 kHz | Fissa 100 k 1 kHz | Fissa 100 k 20 kHz |
|---|---|---|---|---|
| solo serie, 0,5 pF | 2,60 mV | 51,6 mV | 0,99 mV | 19,8 mV |
| solo serie, 2 pF | 10,4 mV | 206 mV | 3,95 mV | 79,1 mV |
| solo serie, 10 pF | 51,9 mV | 1,03 V | 19,8 mV | 394 mV |
| serie 10 pF + 0,1 Ω al jack | 75 nV | 1,50 µV | 24 nV | 0,48 µV |

A 10 k le cifre della sola serie sono circa 7 volte più basse, e restano sopra i
100 µV di B a 1 kHz e a 20 kHz già da 0,5 pF (principale a 10 k, 0,5 pF, 1 kHz:
361 µV). A 20 Hz la sola serie da 0,5 pF sta sotto: 52 µV sulla principale a 100 k.

**Conclusioni** (limite superiore, prima del filtro, che a 20 kHz toglie circa 3 dB):
1. **Un elemento solo in serie non rispetta B** con nessuna capacità fisica. A
   20 kHz sulla principale a 100 k servirebbero ≲ 1,4 fF.
2. **Con una derivazione al jack B cade a µV o meno.**
3. **La derivazione non può essere un contatto netto aperto con la musica.**
   Aprendosi scopre di colpo il residuo della riga «solo serie», cioè mV a
   1 kHz, contro 1 mV di C. Quindi anche la derivazione dev'essere graduale,
   oppure commutare solo quando la serie è ancora chiusa.
