# L29b — le coppie DMN6040SVT_SUB sulla catena intera: il banco non converge alle tolleranze di V2

**SIMULATO, scratch, nessuna cifra di V2.** Si ferma qui, per decisione della
sessione del 2026-09-16: l'utente ha chiesto di cercare in rete strade più
semplici prima di proseguire.

## Il banco (`build.py`)

- Il blocco CANALE di `tb_v2_mute_graduale.cir`, senza gli elementi ideali
  `BSER*`, `BJK*` e `RBY*`, coi bleeder lato condensatore di `g4`.
- Per ogni uscita: una coppia **in serie** (condensatore–jack) e una coppia
  **verso massa** (jack–massa), fatte di `DMN6040SVT_SUB` (vth = 2,0 V,
  s = 0,08 o 0,12 V/dec).
- La tensione di gate è **ideale**: un generatore comandato flottante fra gate e
  source comuni, 1 GΩ dal source a massa come `RDUMMY` del modello VOM1271.
- Una sola variabile di profondità p(t) comanda entrambe le coppie, così
  un'inversione ripercorre la stessa strada.
- `prova.py`: a riposo la serie ha 8 V e la derivazione 0 V; «sempre in mute» dà
  il contrario, con p = 2,2. La logica è giusta.

## Cosa succede

1. **Il transitorio si ferma** con «Timestep too small … trouble with
   lsk489x-instance j.xa.jq110a», attorno a 0,15 s, durante l'entrata del tono
   (`prova.py`, `isola.py`). L'errore nomina il JFET d'ingresso del blocco A, ma:
   - con le coppie in serie sostituite da 1 mΩ e le derivazioni tolte, corre;
   - con le sole coppie in serie reali, corre;
   - con la sola derivazione della principale, corre fino a 0,37 s;
   - con tutte le derivazioni, cade.

   **La causa è la coppia verso massa.**
2. **Il nodo dei source della derivazione si pompa** al picco negativo del jack:
   **−11,89 V** (`isola2.py`, `solo_jM`). Il diodo di corpo del MOSFET lato jack
   raddrizza, e a riportarlo su resta solo la perdita.
   - **È fisica, non un artefatto**: in un circuito reale il nodo è isolato
     (datasheet VOM1271: RIO ≥ 1e12 Ω).
   - Il MOSFET lato massa vive quindi con ~12 V fra drain e source.
   - Quando la derivazione si accende, quella carica deve scendere attraverso le
     capacità dei due MOSFET: un possibile evento al jack, da misurare.
3. **Tentativi di convergenza** (`isola2.py`, `isola3.py`, 1 s simulato):

| Variante | Esito |
|---|---|
| 1 pF dai source a massa (capacità d'isolamento, **non pubblicata**) | cade a 0,148 s |
| `method=gear` | cade a 0,147 s |
| 1 TΩ invece di 1 GΩ | cade a 0,149 s |
| `reltol=1e-5` | cade a 0,267 s |
| `reltol=1e-5 abstol=1e-9` | corre, 12 s |
| `reltol=1e-4` | corre, 30 s |
| `reltol=1e-6 method=gear maxord=2` | cade a 0,147 s |

**Nessuna delle due varianti che corrono è accettabile per V2 senza una
verifica.**
- `reltol=1e-4` ammette errori relativi di 1e-4, cioè 1,2 mV su 12 V: quanto la
  soglia di C.
- `abstol=1e-9` è 1 nA: B e A si misurano a nV–pV, cioè a correnti di pA su
  ~68 kΩ.

## Stato

**Il banco con le coppie reali non è ancora eseguibile alle tolleranze di V2.**
Cifre non ce ne sono.
