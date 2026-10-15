<!--
L59, 2026-10-15. Proposta di un altro modello, scritta offline e incollata dall'utente nella
sessione. Copiata verbatim, senza correzioni. adversarial-architect NON l'ha vista: era già partito
quando è arrivata. Il confronto sta in reports/2026-10-15-L59-esiti-architetto.md.
-->

# Specifiche di Progetto: Rilevatore DC a Microcontrollore con Trigger a 100 ms

## 1. Obiettivo e Vincoli Complessivi
* **Obiettivo Primario:** Identificare la presenza di tensione continua (**DC pura da guasto hardware**) sul percorso del segnale audio e attivare la protezione (relè/mute) entro un tempo massimo di **100 ms**.
* **Vincolo Hardware del Trigger:** Un tempo di trigger di 100 ms è matematicamente compatibile con frequenze AC fino a **5 Hz** (limite teorico) e sicuro con musica normale (che opera sopra i 20 Hz, dove la semionda dura solo 25 ms).
* **Il Problema del Vinile Ondulato (*Warped Vinyl*):** I dischi rovinati generano forti oscillazioni subsoniche ad alta energia tra **0,5 Hz e 5 Hz**. Avendo una semionda che supera i 100 ms, queste oscillazioni ingannerebbero un semplice timer software, causando falsi positivi (l'apparecchio va in protezione durante l'ascolto).

---

## 2. Architettura della Soluzione (Disaccoppiamento Guasto vs Infrasuono)

Per mantenere il trigger ultrarapido a 100 ms senza subire i falsi allarmi del giradischi, il sistema deve implementare una delle seguenti tre strategie (o una combinazione di esse):

### Soluzione A: Analisi della Derivata Software (Rilevamento del Trend)
* **Principio:** Un guasto hardware (es. rottura di un transistor) si presenta come un gradino di tensione istantaneo che si stabilizza fisso (DC pura, variazione nulla). L'ondulazione del vinile è invece un'onda lenta che continua a cambiare valore nel tempo.
* **Logica Software:** 
  1. Il microcontrollore campiona il segnale (es. ogni 1-2 ms) e verifica il superamento della `SOGLIA_PERICOLO`.
  2. Se la soglia è superata, calcola la derivata (la variazione di tensione tra campioni successivi \(\Delta V / \Delta t\)).
  3. Se la variazione è prossima a zero (segnale bloccato fisso), il tempo di trigger viene impostato a **100 ms** (Guasto Critico).
  4. Se la variazione è presente (segnale in movimento lento), il sistema riconosce l'infrasuono e sposta dinamicamente il trigger a **1500 ms** o ignora l'evento.

### Soluzione B: Filtro Passa-Alto / Subsonico Digitale (DSP Software)
* **Principio:** Ripulire il segnale digitalizzato prima di inviarlo al contatore di protezione, isolando l'offset DC fisso dalle oscillazioni subsoniche.
* **Logica Software:**
  1. Si applica al segnale d'ingresso un filtro digitale passa-alto (IIR o FIR) del 2° ordine con frequenza di taglio a **15 - 20 Hz**.
  2. Questo filtro attenua drasticamente i 2-4 Hz del braccio del giradischi, impedendo al timer di partire durante i sobbalzi.
  3. L'algoritmo parallelo monitora invece il valore medio a lungo termine (DC offset statico) per intercettare il guasto hardware a 0 Hz.

### Soluzione C: Filtro Anti-Rumble Hardware (Approccio Analogico)
* **Principio:** Eliminare l'energia subsonica prima ancora che raggiunga il convertitore ADC del microcontrollore.
* **Logica Hardware:** 
  1. Inserimento di un filtro passa-alto attivo analogico (filtro subsonico/anti-rumble) tarato a **18 Hz** (pendenza minima 12 o 18 dB/ottava) a monte del circuito di condizionamento del microcontrollore.
  2. In questo modo, l'energia generata dal disco ondulato viene soppressa dall'hardware e il micro riceverà solo la musica pulita o la DC pura in caso di guasto, potendo utilizzare un algoritmo a timer lineare da 100 ms senza logiche complesse.

---

## 3. Logica dell'Algoritmo Consigliata (Pseudo-Codice)

```c
// Eseguito in un loop ad alta priorità o timer interrupt (es. ogni 1 ms)
void process_dc_protection() {
    float current_sample = read_adc_and_remove_hardware_offset();
    
    // Calcolo della variazione (derivata) per discriminare DC fissa da oscillazione
    float delta_v = abs(current_sample - previous_sample);
    previous_sample = current_sample;

    if (abs(current_sample) > SOGLIA_DC_PERICOLO) {
        
        if (delta_v < SOGLIA_VARIAZIONE_MINIMA) {
            // Caso 1: Il segnale è fermo e oltre la soglia -> VERA DC (Guasto)
            target_trigger_time_ms = 100; 
        } else {
            // Caso 2: Il segnale si muove lentamente -> INFRASUONO (Disco Warped)
            target_trigger_time_ms = 1500; 
        }

        counter_ms++;
        if (counter_ms >= target_trigger_time_ms) {
            trigger_protection_relay(); // Attiva protezione
        }
    } else {
        // Il segnale è nella zona sicura (musica AC che incrocia lo zero)
        counter_ms = 0; 
    }
}
```
