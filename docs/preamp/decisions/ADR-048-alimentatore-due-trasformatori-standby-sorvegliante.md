# ADR-048 — L'alimentatore: due trasformatori standard, `VRELAY` a 12 V, standby con interruttore posteriore, sorvegliante a comparatore con rivelatore di rete, temporizzatore ibrido

Data: 2026-09-26 · Stato: accettata

## Contesto

NC-036 chiede il circuito che realizza P9 (ADR-046) e i contratti di J1, J3 e J4. Restavano
aperte sei scelte che toccano l'utente:
- la struttura nel sorgente;
- il trasformatore;
- la tensione di `VRELAY`, lasciata aperta da L35 e L36;
- la meccanica dell'interruttore morbido;
- la tecnica del sorvegliante;
- la tecnica del temporizzatore.

Se ne è parlato il 2026-09-26 (L41a), una alla volta, con i numeri davanti.

## Decisione

Parole dell'utente, in ordine: «2×15 V 50 VA standard»; «sono disposto a cambiare l'alimentatore
(24v? o altre proposte) ma non accetto uno switching, siamo troppo deboli sulla PSRR»; «avere due
trafo standard? potrebbe risolvere e costare meno?», «si confermo»; «mi piace la 3, ma é possibile
avere un secondo switch sul retro del tealio per un off completo?», «si confermo la 3 con
l'interruttore posteriore»; sul sorvegliante «accetto la tua raccomandazione»; «accetto
l'ibrido»; su P5 «si lo accetto».

1. **Struttura.** L'alimentatore è `circuits/preamp/psu.py`, con la sua netlist: è il secondo PCB
   di P4. I connettori verso la scheda audio (J1, J2, J3, J4) hanno la stessa piedinatura dei loro
   gemelli in `preamp_audio.py`, e un controllo meccanico lo verifica.
2. **I trasformatori sono due, entrambi standard.**
   - Il toroidale **2×15 V, 50 VA**, a catalogo: i rail ±15 V e nient'altro.
   - Un **piccolo trasformatore standard** a parte per `VRELAY`, la logica e lo standby.
     **Toroidale richiesto** (lavora sempre, punto 4): perdite a vuoto basse e poco campo
     disperso. Preferenza per il giro componenti: secondario da **12 V AC**, invece di 15, per il
     calore (punto 7).
   - **Nessuno switching** nel telaio.
3. **`VRELAY` = 12 V**, lineare, dal secondario del piccolo trasformatore, con un serbatoio proprio.
   Le correnti delle bobine non passano mai dai grezzi dei rail audio.
   - Sulla scheda audio: bobine **12 VDC** su K1–K12, e resistenze dei LED da 1,5 k a **4,99 k**
     (R3, `R_LED` in `trim.py` e `gain_interlock.py`). Sono valori fuori dal percorso del
     segnale.
   - Budget: 72,8 mA di bobine più ~6 mA di LED.
   - Il vincolo Schottky di L36 si soddisfa con ~1,4 V di margine.
4. **L'interruttore morbido è la forma «standby» (3), con un interruttore posteriore.**
   - Sul retro un **modulo IEC con fusibile e interruttore bipolare** (fase e neutro): spento =
     rete staccata da tutto, consumo zero.
   - Col retro acceso il piccolo trasformatore è **sempre alimentato** e tiene la logica in
     standby. L'interruttore **frontale è solo a bassa tensione**: è un ingresso del
     temporizzatore, come SW3.
   - Il **relè di rete comanda il solo toroidale**; diseccitato = toroidale staccato.
   - Spegnere dal retro mentre suona è una perdita di rete, cioè il caso guasto di P9 (b).
5. **Il sorvegliante** è un comparatore doppio con un riferimento di precisione.
   - Le uscite open-drain, in AND, **spengono in hardware** il gate del sink di `MUTE_CMD`, senza
     passare dal firmware.
   - Soglia |13,5 V| ± ~0,15 V. Senza alimentazione il gate è a zero, quindi mute.
   - **In più, un rivelatore di rete** sul secondario del piccolo trasformatore: le semionde
     mancanti fanno scattare lo stesso mute netto.
     - Se i rail non sono mai scesi sotto |13,5 V|, il temporizzatore rilascia poi il mute con la
       sequenza normale.
   - **E `VRELAY` stessa** (aggiunto in L41a dopo la simulazione, nella stessa forma: il canale
     libero del secondo comparatore, mute sotto 11,0 V, più 2200 µF dopo il suo regolatore).
     Senza, un regolatore di `VRELAY` che cede faceva cadere insieme tutte le bobine: il caso
     «senza Δ» di L30.
   - **Dopo un guasto con la rete presente** (un rail scende e la rete c'è), il temporizzatore,
     completato il mute, stacca il relè del toroidale, e **resta spento** finché non si gira
     l'interruttore frontale.
6. **Il temporizzatore è ibrido.**
   - Un **microcontrollore** fa la sequenza: il profilo v4 delle LDR, `MUTE_CMD`, `PERMIT_CMD`,
     l'accensione, lo spegnimento, l'OR con SW3, il debounce, il rilascio dopo un buco di rete e la
     ritenuta dopo un guasto. È fuori dal segnale, come ammette ADR-022.
   - **L'ordine di sicurezza è in hardware**, e nessun firmware lo può violare:
     - `MUTE_CMD` è spento dal sorvegliante;
     - `PERMIT_CMD` si rilascia **non prima di Δ dopo `MUTE_CMD`**, per un ritardo RC: Δ ≥ 10 ms
       vale anche col micro morto o in reset;
     - un micro in reset ha le uscite a zero, quindi mute.
   - Le LDR: il micro dà una tensione di comando, un convertitore esponenziale analogico la
     trasforma in corrente.
   - Lo realizza **L41b**.
7. **I regolatori** (scelta di progetto, non dell'utente; letti sui datasheet in L41a):
   TPS7A4701 per +15 V e per `VRELAY` a 12 V (ANY-OUT, SBVS204G §6.5.1), TPS7A3301 per −15 V
   (V_REF −1,175 V, SBVS169D). 35 V all'ingresso, contro ~22,5 V di grezzo con la rete a
   +10 %.
8. **P5 cambia**: ~17 W nominali, **≤ 20 W** nel caso peggiore, alimentatore compreso.
   - Nel telaio ≤ 58 °C con un vano chiuso a 3 cm e la stanza a 35 °C: i 60 °C di ADR-021 reggono,
     col margine ridotto a ~2 °C.
   - Le due leve si applicano come preferenze, con una stima di ~19,5 W: il piccolo trasformatore
     a 12 V AC e un relè di rete a bobina sensibile.

## Perché

**Il trasformatore** (`data/2026-09-26/L41a/scelte/raddrizzatore.csv`; modello di toroidale
ipotetico, dichiarato nel file). Margine della valle sopra 15,6 V con la rete a −10 %:

| Secondario | Margine |
|---|---|
| 2×12 V | −1,3 V: escluso |
| 2×13 V | −0,1 V: escluso |
| 2×14 V | +1,0 V (su misura) |
| 2×15 V a 50 VA | +2,5 V |

Con 2×15 V e la rete a +10 % i regolatori dissipano 4,14 W: è la voce principale del nuovo P5.

**`VRELAY` a 12 V con un avvolgimento proprio.**
- Il 5 V lineare dal rail + dissiperebbe ~2,7 W. Il 5 V switching è escluso dall'utente (PSRR+
  ~10 dB a 100 kHz, il fuori banda lasciato aperto da ADR-020).
- Il 24 V vorrebbe un secondario da ≥ 25 V.
- Col 12 V preso dal rail +, le bobine tirerebbero dal grezzo del rail debole (PSRR+ ~23 dB a
  10 kHz, ADR-042). L'avvolgimento proprio lo evita.
- Pick-up dietro lo Schottky, con `VRELAY` a −5 %: ~92 % della nominale. Il must-operate massimo
  è ~78 % a 60 °C e ~81 % a 70 °C: curva di en-g6k.pdf p. 4, campione di 10 pezzi, quindi non
  garantita; la tabella garantisce l'80 % a 23 °C.

**Lo standby.**
- Rispetto all'interruttore di rete in parallelo al relè (forma 1), toglie la rete dal pannello
  frontale.
- Un buco di rete non si confonde con «spento».
- `VRELAY` e la logica sono stabili prima che il toroidale parta: i 13 ms di ADR-027 sono
  soddisfatti per costruzione.
- Il rivelatore di rete viene quasi gratis.

**Il rivelatore di rete.**
- Scatta ~15–20 ms dopo la perdita, invece di 66–133 ms, coi rail ancora a 15 V.
- Toglie la parte PSRR del residuo di L30 (0,5–1,8 mV, ~58 dB SPL di picco a 1 m): quanto la
  cifra scenda lo misura L41c.
- Accorcia la tenuta di `VRELAY` da ~160 a ~45 ms dalla perdita.

**Il calore** (`data/2026-09-26/L41a/scelte/stima_telaio_l41a.py`, stesso modello di L30).
Rispetto a L30, +2,4 W nel caso peggiore:
- regolatori a 50 VA: +0,4 W;
- `VRELAY`: +0,5 W;
- bobina del relè di rete: +0,5 W, prima nel «resto»;
- piccolo trasformatore: +0,9 W.

Le ultime due sono ipotesi da confermare sui pezzi.

## Alternative scartate

- **Un toroidale su misura 2×15 + 1×15 V** (la «A»): un solo campo disperso, ma un pezzo non a
  scaffale. L'utente ha preferito due pezzi standard.
- **`VRELAY` dal grezzo del rail +** (la «A″»): le correnti delle bobine sul rail debole.
- **`VRELAY` a 24 V** (la «B»): serve un secondario su misura, e la logica dissipa di più.
- **L'interruttore di rete in parallelo al relè** (la «1»): la rete al pannello, e l'ambiguità
  fra un buco di rete e «spento».
- **Il deviatore misto rete/bassa tensione** (la «2»): chiede isolamento rinforzato fra i poli.
- **Il sorvegliante a zener**: ±0,7 V di soglia.
- **Il sorvegliante integrato**: sul rail − serve comunque un traslatore.
- **Il temporizzatore tutto analogico**: molti stati in logica discreta, e un convertitore
  esponenziale a spezzata su 6 decadi da dimostrare.

## Da riaprire se

- Il ronzio del prototipo non rientra, e il secondo trasformatore ne è la causa (ADR-010, «Da
  riaprire se»).
- Il consumo in standby supera il limite europeo applicabile. La fonte e la cifra vanno scritte
  nel registro di sicurezza.
- Il piccolo trasformatore a 12 V AC non tiene `VRELAY` sopra il dropout con la rete a −10 %.
- La misura del calore nel prototipo supera i 60 °C nel vano stretto.
- Il firmware non riesce a rispettare il profilo v4 con il convertitore esponenziale scelto (L41b).
- La quota di ADR-020 non regge coi TPS7A4701: il datasheet dà 12,28 µVrms a 15 V
  (10 Hz–100 kHz), e la densità letta a occhio dal grafico a 1 kHz (~0,1–0,15 µV/√Hz) supera
  il limite di 87 nV/√Hz sul rail +. Non è verificato: va misurato col modello o sul prototipo.

**Supera ADR-046 al punto 1**, per la sola frase «il relè di rete … diseccitato = rete staccata»:
ora il relè stacca il toroidale, e la rete si stacca dal retro. Il resto di ADR-046 resta in
vigore. **Supera ADR-047 per la cifra di P5.** **Precisa ADR-020**: il rimedio sono regolatori
lineari, e nel telaio non c'è nessuno switching.
