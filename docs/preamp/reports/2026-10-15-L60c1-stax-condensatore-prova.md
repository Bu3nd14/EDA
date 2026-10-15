# L60c1 — Il condensatore della Stax dopo il relè di mute: la prova prima del sorgente (2026-10-15)

Prima parte di **L60c** («la Stax ha il suo condensatore»). All'inizio della sessione l'utente ha
diviso il lotto: «Prima la prova».
- **L60c1**: le misure sul banco, senza toccare il sorgente, e la scelta;
- **L60c2**: il sorgente e le prove complete sulla scelta.

**Il risultato.** Il condensatore da 1 µF **dopo** il relè di mute K3, come lo voleva ADR-082 punto 1,
non regge. A ogni mute la Stax riceve la continua del buffer F2, un colpo da 77–90 dB SPL
all'orecchio, e col bleed di oggi il blocco al rail passa i 125 ms. L'utente ha scelto la riserva
che ADR-082 prevedeva: **«Relè rinforzato»** → **ADR-084**. Il condensatore da 1 µF resta prima di K3,
nella geometria di oggi; K3 diventa un relè con isolamento rinforzato fra bobina e contatti, da
scegliere sul datasheet in L60c2. Il circuito non cambia in L60c1.

## 1. Perché la prova prima

Leggendo ADR-044 (la geometria del mute) e il metodo di V2, prima di toccare il sorgente: con tutti i
contatti di K3 a monte del condensatore, a mute inserito la sua armatura d'ingresso va a massa. Al
rilascio risale alla continua del buffer, che il blocco A gli passa (−6,6 mV nominali, fino a ±30 mV
con la dispersione). Il banco del mute, inoltre, legge la geometria dalla netlist e rifiuta tutto
ciò che non è la geometria iii: cambiare il sorgente si portava dietro il generatore e il controllo
della suite. L'utente ha scelto di misurare prima, sul banco.

## 2. Il banco

`data/2026-10-15/L60c1/` (README): il banco di L60a importato, con l'uscita della Stax sostituita da
cinque geometrie. Ognuna ha il deviatore K3 con due comandi e il trasferimento di 1 ms di ADR-044. Le
prove: il gradino del mute col metodo di V2, i guasti di P10, i 20 Hz di E9 e l'inserimento a caldo.
In tutto 187 corse, tutte terminate.

**Il controllo prima dei numeri nuovi**:
- G0, cioè la geometria di oggi con 1 µF, col blocco F2 al rail dà **117,5 ms**, come L60a;
- K3 sul NO dà **12 V per sempre**, come L60a;
- E9 su G0 dà **0,161 dB**, contro gli 0,162 calcolati in ADR-081.

**Due correzioni dello strumento, fatte prima di leggere i numeri.**
- Nell'analisi AC l'interruttore con isteresi di ngspice restava aperto nel punto di lavoro. Il jack
  della Stax era a −147 dB su tutte le geometrie, e la differenza fra 20 Hz e 1 kHz veniva 0,004 dB
  (il solo C_IN). Il flag `ON` sull'istanza non è bastato. Nei deck di E9, che descrivono lo stato
  fuori mute, il NO è scritto come la sua resistenza da 0,1 Ω e il NC, aperto, non c'è.
- La prima tabella di P10 contava anche i file `.stdout` come corse. Si rifà sulle sole cartelle.

## 3. I numeri

| Geometria | Gradino del mute (soglia 100 µV) | Blocco al rail (≤ 125 ms) | K3 che cede, peggiore | 20 Hz al −5 % (≤ 0,2 dB) |
|---|---|---|---|---|
| **G0** oggi, 1 µF prima di K3 | 0 | 118–124 ms | **12 V per sempre** | 0,178 dB |
| **G1** ADR-082: 1 µF dopo K3 | **6,0–27,3 mV**, 77–90 dB SPL | **129–135 ms** | 110–115 ms | 0,149 dB |
| G1b, bleed del jack 220 k | **6,0–27,3 mV** | 116–122 ms | 99–104 ms | 0,182 dB |
| **G2** 10 µF prima, 1 µF dopo | 0 | 108–113 ms | **131–138 ms** (1 kΩ) | 0,180 dB |
| G2b, bleed del jack 220 k | 0 | 98–103 ms | 120–**126** ms (1 kΩ) | **0,220 dB** |

Gli intervalli dei tempi vanno dal condensatore nominale al +5 %. Il gradino va dalla continua
nominale del buffer (−5,7 mV) a ±20 mV sull'ingresso di F2. I dB SPL sono all'orecchio, con la
catena di NC-046: la soglia di 100 µV vale 41 dB SPL. Su tutte le geometrie:
- **un pin aperto** dei due di un rail (ADR-083) porta al jack meno di 0,2 µV;
- **l'inserimento a caldo** del jack della Stax è nullo: fuori mute il jack sta a 0 V sul suo bleed.

**Che cosa dicono.**
- **G1**:
  - il gradino è la continua del buffer, e passa il filtro di V2 quasi intero: il bleed non lo cambia;
  - col bleed da 470 k il condensatore vede solo il jack e la Stax (45,2 kΩ invece di 41,2): τ più
    lungo, e il blocco al rail esce di 4–10 ms;
  - K3 che cede passa (110–115 ms): era il guasto per cui la si voleva.
- **G2** tiene la continua nel 10 µF e il mute torna a zero. Però K3 che cede con 1 kΩ carica anche il
  10 µF, e il colpo dura di più. Ogni modo di accorciarlo tocca i 20 Hz.
- **G0** regge tutto, tranne K3 che cede.

## 4. La decisione

Domanda posta per nome, coi numeri della tabella. Tre possibilità:
- il relè rinforzato;
- i due condensatori, da rifinire;
- accettare il gradino, rivedendo il requisito dei transitori di commutazione.

L'utente: **«Relè rinforzato»** → **ADR-084**:
1. il condensatore da 1 µF film della fissa 2 resta prima di K3, al posto del 4,7 µF di oggi, nella
   geometria iii;
2. K3 diventa un relè con isolamento rinforzato fra bobina e contatti. Il cedimento bobina-contatti
   esce dai guasti singoli credibili;
3. K2 e K4 restano G6K.

## 5. Che cosa resta: L60c2

- **Il relè**, scelto sul datasheet: due deviatori per segnale, bobina a 12 V, isolamento rinforzato
  fra bobina e contatti. La capacità del contatto aperto e il trasferimento si confrontano coi valori
  di ADR-044.
- **Il sorgente**, `preamp_audio.py`: il condensatore della fissa 2 a 1 µF col commento di ADR-007
  riscritto; K3 come parte diversa da K2 e K4, che oggi nascono nello stesso ciclo.
- **Le netlist, i disegni e il generatore di `tb_v2_casopeggiore.cir`.**
- **Le prove sul circuito**:
  - E9;
  - P10 coi guasti di L45a che portano continua: qui ci sono solo i due blocchi al rail;
  - V2 sulla fissa 2 con 1 µF: qui G0 dà 0, ma senza la capacità di 0,1 pF del contatto aperto;
  - l'inserimento a caldo;
  - `run_tests.sh`.

**NC-042 avanza**; nessuna voce aperta o chiusa.
