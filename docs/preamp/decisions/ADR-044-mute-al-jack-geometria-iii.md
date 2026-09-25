# ADR-044 — Il mute al jack diventa serie più derivazione dal lato del condensatore (geometria iii); a riposo il jack va a massa attraverso il bleed

Data: 2026-09-25 · Stato: accettata

## Contesto

L29c ha misurato V2 col mute reale. Fuori soglia, senza musica, erano:
- il cambio di guadagno o di trim a relè chiuso: fino a **267 µV** con la dispersione;
- l'accensione: fino a **11 mV**.

La causa è una sola: il contatto in derivazione al jack, 0,1 Ω dietro 47 Ω, attenua solo ~1/471.
La sonda di L29d ha provato quattro geometrie con un contatto in serie. Solo la **iii** ha retto
quasi tutto: la serie fra il condensatore d'uscita e il jack, più la derivazione a massa **dal
lato del condensatore**. Ha lasciato all'utente tre scelte: la geometria, lo stato sicuro e i
valori. L29d2 ha misurato la scelta su tutta la matrice di L29c
(`reports/2026-09-25-L29d2-matrice-contatto-serie.md`).

## Decisione

Le parole dell'utente, il 2026-09-25, a tre domande poste una alla volta:
- geometria: «**iii**»;
- stato sicuro: «**Il bleed basta**»;
- valori: «**C dal datasheet + cavo realistico**».

1. **Il mute al jack è la geometria iii** su tutte e tre le uscite:
   - all'inserzione la serie apre, e 1 ms dopo la derivazione dal lato del condensatore chiude;
   - al rilascio avviene l'inverso.

   Il contatto in derivazione **al jack** di ADR-038 (punto 2) non c'è più.
2. **Lo stato sicuro di ADR-012**, nella lettura di ADR-037 e ADR-038: «a macchina spenta il jack a
   massa». Diventa **a massa attraverso il bleed del jack**:
   - principale `RBLM` 220 kΩ, fisse `RBL1`/`RBL2` 470 kΩ, già nel blocco;
   - nessun contatto chiude il jack a massa;
   - a riposo il lato del condensatore è a massa attraverso il contatto.

   Non si aggiunge un secondo polo.
3. **I valori con cui la scelta è stata misurata**:
   - contatto aperto **0,1 pF**: 0,075–0,080 pF dalla curva d'isolamento del G6K, arrotondati per
     eccesso;
   - cavo al jack 0 e 100 pF;
   - bleed lato condensatore 220 kΩ / 470 kΩ;
   - trasferimento fra i contatti 1 ms.

**Cosa non decide.** Il cablaggio nel sorgente non è qui. La forma naturale è **un deviatore per
uscita**: comune al lato del condensatore, NC a massa, NO al jack. Con il G6K-2F-Y è lo stesso
numero di relè di oggi. Va portata in `circuits/` da **L29e**, prima di L36: l'utente il 2026-09-25, «L29e prima di L36,
concordo con la tua proposta». L29e deve rifare sul sorgente le celle peggiori di L29d2.
Anche la necessità del bleed lato condensatore resta aperta: nel deviatore conta solo durante
il trasferimento, e non è stato misurato senza.

## Perché

- **Regge V2 ovunque tranne lo spegnimento**, che è di L30. Sono 253 verdetti, nessuno fuori,
  più 47 nelle varianti. A 0 pF e 100 kΩ, contro L29c:
  - cambio di guadagno a relè chiuso da **111,5 a 0,17 µV**;
  - trim da **101,7 a 0,10 µV**;
  - dispersione, sul cambio, da **267 a ≤ 0,60 µV**;
  - accensione da **11 280 a 4,4 µV**.
- **La musica non cambia**: S ≤ 7,16 dB, come in L29c; B2 col contatto aperto ≤ 8,7 µV
  (10,2 µV a 10 kΩ).
- **Il cavo e il carico basso migliorano**: con 100 pF di cavo o 10 kΩ di carico ogni cifra del
  contatto scende. Lo 0 pF e i 100 kΩ sono davvero il caso peggiore.
- **La cella più alta, 69,7 µV, non è del contatto.** È la dissolvenza delle LDR con ±20 mV di VOS:
  identica in L29c, e il picco cade 1,32 s dopo il rilascio, dentro la dissolvenza.
- **Il bleed basta** perché V2 guarda i transitori, e lo stato sicuro è un'altra cosa: a macchina
  spenta, nel jack non entra niente con un percorso resistivo dal lato del condensatore, e il bleed
  tiene il nodo a massa. È la risposta dell'utente, ed è una preferenza: nessuna misura dice che un
  contatto a massa sul jack servisse.

## Alternative scartate

- **(ii) serie sola**: 10 mV dopo il cambio di guadagno, fino a 193 mV all'accensione (L29d).
- **(iA) serie più derivazione al jack**: la carica presa a mute inserito arriva al rilascio, fino a
  190 mV (L29d).
- **(iB) la stessa, con la serie che chiude per prima**: 0,3–5,6 mV con 1 ms (L29d). Un
  trasferimento più lungo sarebbe servito, ma solo calcolato; non scelta dall'utente.
- **iii più un secondo polo a massa sul jack**: non scelta dall'utente («Il bleed basta»).
- **La derivazione al jack di L29c**: fuori su cambio e accensione.

## Da riaprire se

- **La capacità fra il lato condensatore e il jack supera ~2,4 pF.** Contatto e piste insieme,
  sulla scheda vera. L'accensione scala circa lineare: 4,4 µV a 0,1 pF, 205 µV a 5 pF. È un
  **vincolo per il layout (G2)**.
- Il relè cambia, e il nuovo ha la C del contatto aperto o il tempo di trasferimento molto
  diversi.
- L30 trova che il failsafe dello spegnimento chiede un contatto a massa **sul jack**: allora il
  secondo polo torna in discussione, con l'utente.
- Il cablaggio nel sorgente non riesce a essere un deviatore, per piedinatura o per poli.
- L29e, sul sorgente, non riproduce le celle peggiori di L29d2. Allora si riapre anche la parte
  del mute di NC-028, che l'utente ha chiuso su questa misura («chiudi la parte mute di NC-028»).

**Precisa** ADR-012 (lo stato sicuro: il jack a massa attraverso il bleed) e **ADR-038** punto 2
(il relè al jack diventa la geometria iii). Il punto 4 di ADR-038 («guadagno e trim si cambiano
solo col jack a massa») si legge ora così: col **lato del condensatore** a massa e il jack isolato.
**È la condizione di ADR-043** «Da riaprire se» («un elemento in serie al segnale o un cambio dello
stato sicuro di ADR-012»): la scelta è dell'utente, e questa ADR la registra. ADR-043 resta
valida: lo spegnimento, con la iii, è ancora fuori (diagnostica nel report, § 4.3).
