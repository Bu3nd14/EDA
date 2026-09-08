# ADR-015 — Rail a ±15 V, non ±18 V

Data: 2026-09-08 · Stato: accettata

## Contesto

La Fase 2 ha misurato che in modalità **+10 dB** con il K11 a fondo
scala (2,7 V, requisito E6) l'uscita richiesta è **8,54 V RMS**, contro
un clipping del blocco a **9,31 V RMS**: **0,75 dB di margine**.

È un limite strutturale: sui rail ±15 V non c'è spazio per 2,7 × 3,16.
La domanda è se alzare i rail.

## Decisione

**Si resta a ±15 V**, confermando E7. Il margine si recupera con il trim
di ADR-011.

## Perché

- **Il +10 dB è assicurazione per un finale futuro, non la modalità
  d'uso.** Oggi il cj Evolution 250 vuole 612-750 mV e il preamp lavora
  a guadagno unitario, dove di margine ce n'è in abbondanza.
- **Il trim di ADR-011 risolve il caso.** Con l'ingresso K11 a −6 dB, in
  modalità +10 dB l'uscita richiesta scende a 4,27 V RMS: oltre 6 dB di
  margine. Il meccanismo esiste già ed è progettato per questo.
- **±18 V costano calore in un mobile chiuso.** La dissipazione degli
  stadi d'uscita salirebbe da 214 a ~265 mW ciascuno, e con i regolatori
  si passerebbe da ~3,2 W a circa 4 W. ADR-010 ha già accettato il
  telaio unico sapendo che la ventilazione va prevista: non conviene
  aggravare il problema per una modalità che potrebbe non essere mai
  usata.
- Alzare i rail contraddirebbe E7 e richiederebbe di rivedere i punti di
  lavoro di tutti e quattro i blocchi.

## Conseguenza operativa, da non perdere

**In modalità +10 dB il trim sull'ingresso ad alto livello non è
opzionale.** Va scritto sul pannello o nella documentazione d'uso: è
l'unica cosa che separa quella modalità dal clipping a 0,75 dB.

## Alternative scartate

- **±18 V**: ~11,4 V RMS di headroom, ma più calore in un telaio chiuso,
  contraddice E7, e richiede una revisione dei punti di lavoro.
- **Ridurre il guadagno alternativo da +10 a +6 dB**: allevierebbe il
  problema ma ridurrebbe l'utilità dell'assicurazione, che serve proprio
  per un finale molto meno sensibile.

## Da riaprire se

Entra in catena un finale che richiede davvero il +10 dB **e** una
sorgente che non tollera l'attenuazione del trim.
