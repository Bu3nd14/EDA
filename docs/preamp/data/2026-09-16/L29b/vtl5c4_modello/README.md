# vtl5c4_modello — il modello comportamentale della LDR del mute (L29b, ADR-038)

Generato il 2026-09-16, **verificato e corretto il 2026-09-21** (ripresa di L29b).
Ogni cifra ricavata da `models/optocoupler/vtl5c4_comportamentale.lib` porta l'etichetta
«modello comportamentale dal datasheet, con estrapolazione dichiarata».

| File | Cosa fa |
|---|---|
| `digit.py` | legge a pixel la pag. 46 del datasheet, rasterizzata a 300 dpi |
| `tabelle.py` | converte i pixel in valori (curve statiche, spegnimento, accensione) |
| `genera_modello.py` | scrive il `.lib`. **Il `.lib` non si edita a mano**: si corregge qui |
| `verifica_statica.py` | R(I_LED) sulle quattro curve, un processo ngspice per punto |
| `verifica_dinamica.py` | spegnimento da 40 mA e accensione dal buio a 40 e 10 mA, curva B |

```sh
/usr/bin/python3 genera_modello.py        # rigenera il .lib
/usr/bin/python3 verifica_statica.py      # esce col numero di punti fuori tolleranza
/usr/bin/python3 verifica_dinamica.py
```

## Esito (2026-09-21)

- **Statica: 38 punti su 38 entro lo 0,02 %.** Le quattro curve A–D sono un inviluppo: il
  datasheet non permette di dire quale condizione sia quale. L'estrapolazione arriva a
  400 MΩ al buio, come dichiarato.
- **Spegnimento da 40 mA:**
  - 10 punti letti su 10, entro l'1,4 %;
  - a 10 s, 396,9 MΩ contro il minimo di 400 MΩ del datasheet: il bersaglio al buio è
    400 MΩ esatti, e ci si arriva in modo asintotico.
- **Accensione dal buio: 16 punti su 16 entro il 3,16 %**, con tolleranza **3,5 %**.
  - È allentata dal 3 % per un solo punto: 10 mA a 4,50 ms, −3,16 %.
  - Quel punto dista −3,5 % anche dalla retta dei minimi quadrati della sua curva. È
    dispersione della lettura a pixel, e l'errore di lettura di ~3 % era già una stima.
- **Sabotaggi, tutti rilevati:**
  - un nodo della curva B spostato di 0,1 decadi dà +25,9 %;
  - i tassi di spegnimento −11 % danno −30 %;
  - τ d'accensione +37 % dà +30…+39 %.

  Un sabotaggio che rende la curva non fisica (R che cresce con la corrente) bloccava
  ngspice. Ora ogni corsa ha un timeout di 120 s e una corsa bloccata conta come fuori.

## Due correzioni al generatore, rispetto alla versione del 2026-09-16

1. **Spegnimento.**
   - **Prima**: tassi scelti a mano, con log(tasso) interpolato linearmente fra i nodi.
     Il primo tratto era troppo lento, e tutto il resto ereditava il ritardo: 567 Ω
     contro 1555 Ω a 105 ms, 53 kΩ contro 80 kΩ a 689 ms.
   - **Ora**: il tasso è costante fra due punti letti consecutivi, e vale Δlog R/Δt: i
     punti si ripercorrono per costruzione.
   - Oltre l'ultimo punto (80 kΩ a 689 ms) si usano 0,397 decadi/s, fino a 400 MΩ a
     10,0 s. È il più lento compatibile col minimo del datasheet, cioè la scelta
     pessimistica per il residuo.
2. **Accensione.**
   - **Prima**: un primo ordine su log R, con τ = 3 ms, **dal buio**. Arrivava a 330 Ω in
     6,8 ms, contro 1,51 ms del datasheet.
   - **Cosa mostrano i punti**: nel tratto pubblicato sono esponenziali in log R, con
     τ = 2,70 ms a 40 mA e 3,57 ms a 10 mA (minimi quadrati). Estrapolati a t = 0 partono
     1,23–1,46 decadi sopra il regime, non dal buio.
   - **Ora**: τ e quella distanza (D0) sono funzioni del regime, interpolate fra le due
     correnti pubblicate e costanti fuori. Il salto dal buio a D0 **non è pubblicato**:
     si modella con τ = 2 µs (IPOTESI).
   - Nel mute il LED è comandato a rampe di secondi, e questo tratto non pesa.

## Trappole trovate qui

- **`alter` + `op` in sequenza non convergono**, e stampano cifre sbagliate senza errore:
  7 punti su 18, e a 40 mA una corrente di segno opposto. Ogni `op` riparte dalla
  soluzione precedente, e il log10 della corrente del LED lo manda fuori strada. Da zero,
  ogni `op` converge. Si lancia un processo per punto, oppure si mettono più istanze nello
  stesso `op` (è quello che fa la ricetta di `scripts/validate_models.py`).
- **Col metodo trapezoidale, un gradino sul LED** lascia nella corrente della cella
  un'oscillazione non smorzata, attraverso CIO = 0,5 pF: ±180 % attorno al valore vero
  (1013 contro 362 Ω a 1,48 ms). Lo stato interno `xs` è pulito. In verifica si usa
  `method=gear`.
  - **Da tenere d'occhio sulla catena**, che usa il trapezio. Lì il LED è comandato a
    rampa e non a gradino.
- **La prova originale `prova_modello.cir`** (rimossa) superava i 300 s per il
  `tran 1m 10.2 0 1m`. Con `tmax` = 5 ms, lo spegnimento fino a 10,2 s gira in meno di
  un secondo.

## Cosa resta ipotesi (dichiarato nel `.lib`)

- L'estrapolazione sotto la corrente minima leggibile.
- La coda dello spegnimento oltre gli 80 kΩ.
- Il salto rapido dell'accensione.
- Nessuna distorsione della cella, nessun rumore, nessuna memoria della luce oltre la
  curva, nessuna dispersione fra pezzi, nessuna temperatura.
