"""Il contratto nel dossier (L42d): il PRB, il registro delle ADR, l'indice dei
requisiti tecnici, e i rimandi PR-n / ADR-0xx / E1...V5 resi cliccabili.

Tutto e' letto dai file versionati, niente e' copiato a mano:
  - docs/preamp/PRB.md              le 29 voci (ADR-053)
  - docs/preamp/REQUIREMENTS.md     gli ID dei requisiti tecnici e il loro titolo
  - docs/preamp/decisions/          ogni ADR (H1, Data, Stato) e l'indice README.md
  - docs/preamp/NONCOMPLIANCE.md    gli ID delle non conformita'
  - circuits/preamp/psu.net         i nomi di rete che somigliano a un requisito (V5)

I controlli (punto 14 della docstring di build_dossier.py) chiamano `refuse`
come tutti gli altri: se uno fallisce, la pagina non si scrive.
  a. il PRB: PR-1...PR-n contigui e unici; ogni voce ha il titolo, la riga
     «Dettagli» e al piu' tre righe di corpo nel sorgente (ADR-053);
  b. ogni requisito, ADR, NC e PR che una voce nomina esiste davvero;
  c. univocita': una voce che cita una ADR superata cita anche quella che la
     supera;
  d. le ADR: file e indice in biiezione, numeri contigui, Data e Stato non
     vuoti, lo Stato del file uguale a quello dell'indice (due strade: la
     regola 2 di decisions/README.md), e ogni ADR nominata in uno stato esiste
     ed e' piu' recente;
  e. i rimandi del testo: un PR, una ADR o un requisito che non esistono sono
     un rifiuto; un token che e' anche un non-requisito noto (NON_REQ) deve
     essere marcato con des(), altrimenti e' un rimando ambiguo; ogni
     href="#..." della pagina ha il suo id.
"""

import glob
import html as _html
import os
import re

DOCS = None      # impostati da init()
REFUSE = None

# I token che sembrano un requisito e non lo sono. «T2» e' il trasformatore
# piccolo (ADR-048), nominato nel testo e non come designatore di psu.net; i
# nomi di rete di psu.net che collidono con un requisito si aggiungono da soli
# (oggi «V5», il rail a 5 V). Nel testo del dossier si scrivono con des().
NON_REQ_DICHIARATI = {"T2": "il trasformatore piccolo di VRELAY e dello standby (ADR-048)"}

# Qualunque suffisso di una lettera si cattura, non solo la «b» di E3b: un E3c
# deve arrivare al controllo ed esserne rifiutato (lo ha mostrato il primo
# sabotaggio di L42d, che con «E\d+b?» passava in silenzio).
REQ_TOKEN = r"[EFTPV]\d+[a-z]?"
TOKEN_RE = re.compile(r"(?<![\w\-])(PR-\d+|ADR-\d{3}|" + REQ_TOKEN + r")(?![\w\-])")


def init(repo, refuse):
    global DOCS, REFUSE, REPO
    REPO = repo
    DOCS = os.path.join(repo, "docs", "preamp")
    REFUSE = refuse


def des(tok):
    """Un non-requisito nel testo: il linker lo salta."""
    return f'<span class="des">{tok}</span>'


def rid(tok):
    """Un requisito scritto dove il linker non puo' indovinarlo: il link esplicito."""
    return f'<a class="ref" href="#req-{tok.lower()}">{tok}</a>'


def self_id(tok):
    """L'ID nella riga che e' la destinazione stessa: niente link."""
    return f'<span class="self">{tok}</span>'


def _cells(line):
    """Le celle di una riga di tabella markdown; «\\|» non separa."""
    parts = re.split(r"(?<!\\)\|", line.strip())
    return [p.strip() for p in parts[1:-1]]


def _strip_code(s):
    return re.sub(r"`[^`]*`", "", s)


# --------------------------------------------------------------- letture ---
def read_requirements():
    path = os.path.join(DOCS, "REQUIREMENTS.md")
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    req = {}
    for ln in lines:
        m = re.match(r"^\| (E\d+b?|F\d+|T\d+|P\d+) \|", ln)
        if not m:
            continue
        rid = m.group(1)
        c = _cells(ln)
        if rid in req:
            REFUSE(f"REQUIREMENTS.md: {rid} compare due volte")
        if rid.startswith("E"):
            if len(c) != 4:
                REFUSE(f"REQUIREMENTS.md: la riga di {rid} non ha 4 celle")
                continue
            title = f"{c[1]}: {c[2]}"
        else:
            if len(c) != 3:
                REFUSE(f"REQUIREMENTS.md: la riga di {rid} non ha 3 celle")
                continue
            # il primo tratto in grassetto; senza grassetto (P4) la cella e' il titolo
            b = re.search(r"\*\*(.+?)\*\*", c[1])
            title = b.group(1) if b else c[1]
        req[rid] = {"title": title, "adr": sorted(set(re.findall(r"ADR-(\d{3})", c[-1])))}
    # V1...V5: le intestazioni, e le ADR nominate nella loro sezione
    heads = [(i, re.match(r"^### (V\d+) — (.+)$", ln)) for i, ln in enumerate(lines)]
    heads = [(i, m) for i, m in heads if m]
    for i, m in heads:
        j = next((k for k in range(i + 1, len(lines)) if re.match(r"^#{2,3} ", lines[k])),
                 len(lines))
        body = "\n".join(lines[i + 1:j])
        req[m.group(1)] = {"title": m.group(2), "adr": sorted(set(re.findall(r"ADR-(\d{3})", body)))}
    if not req:
        REFUSE("REQUIREMENTS.md: nessun requisito letto")
    return req


def read_adrs():
    ddir = os.path.join(DOCS, "decisions")
    files = {}
    for p in sorted(glob.glob(os.path.join(ddir, "ADR-*.md"))):
        name = os.path.basename(p)
        m = re.match(r"ADR-(\d{3})-", name)
        if not m:
            REFUSE(f"decisions/{name}: nome fuori convenzione")
            continue
        n = m.group(1)
        with open(p, encoding="utf-8") as f:
            text = f.read()
        h1 = re.match(r"# ADR-(\d{3}) — (.+)\n", text)
        if not h1 or h1.group(1) != n:
            REFUSE(f"decisions/{name}: il titolo non e' «# ADR-{n} — ...»")
            continue
        ds = re.search(r"^Data: (\S*) · Stato: ?(.*)$", text, re.M)
        if not ds:
            REFUSE(f"decisions/{name}: manca la riga «Data: ... · Stato: ...»")
            continue
        if not ds.group(1) or not ds.group(2).strip():
            REFUSE(f"decisions/{name}: Data o Stato vuoti")
        files[n] = {"file": name, "title": h1.group(2).strip(), "data": ds.group(1),
                    "stato": ds.group(2).strip()}
    idx = {}
    with open(os.path.join(ddir, "README.md"), encoding="utf-8") as f:
        for ln in f:
            m = re.match(r"^\| \[(\d{3})\]\(([^)]+)\) \|", ln)
            if not m:
                continue
            c = _cells(ln)
            if len(c) != 3:
                REFUSE(f"decisions/README.md: la riga di ADR-{m.group(1)} non ha 3 celle")
                continue
            idx[m.group(1)] = {"file": m.group(2), "stato": c[2]}
    # d. biiezione, contiguita', stato uguale
    for n in sorted(set(files) - set(idx)):
        REFUSE(f"ADR-{n}: il file esiste ma l'indice decisions/README.md non lo elenca")
    for n in sorted(set(idx) - set(files)):
        REFUSE(f"ADR-{n}: l'indice la elenca ma il file non c'e'")
    nums = sorted(int(n) for n in files)
    if nums and nums != list(range(1, nums[-1] + 1)):
        REFUSE(f"ADR: numerazione non contigua ({nums[0]}...{nums[-1]}, {len(nums)} file)")
    for n in sorted(set(files) & set(idx)):
        a, i = files[n], idx[n]
        if i["file"] != a["file"]:
            REFUSE(f"ADR-{n}: l'indice punta a {i['file']}, il file e' {a['file']}")
        fs = a["stato"]
        if fs != i["stato"]:
            REFUSE(f"ADR-{n}: lo Stato del file («{fs[:70]}») non e' quello dell'indice "
                   f"(«{i['stato'][:70]}»)")
        for m in sorted(set(re.findall(r"ADR-(\d{3})", i["stato"]))):
            if m not in files:
                REFUSE(f"ADR-{n}: lo stato nomina ADR-{m}, che non esiste")
            elif int(m) <= int(n):
                REFUSE(f"ADR-{n}: lo stato nomina ADR-{m}, che non e' piu' recente")
        sup = re.match(r"superata da ADR-(\d{3})", i["stato"])
        a["superata_da"] = sup.group(1) if sup else None
        a["stato"] = i["stato"]
    return files


def read_nc_ids():
    with open(os.path.join(DOCS, "NONCOMPLIANCE.md"), encoding="utf-8") as f:
        ids = set(re.findall(r"^### (NC-\d{3})\b", f.read(), re.M))
    if not ids:
        REFUSE("NONCOMPLIANCE.md: nessuna voce letta")
    return ids


def non_req(req):
    """NON_REQ: i dichiarati, piu' i nomi di rete di psu.net che sono anche un requisito."""
    out = dict(NON_REQ_DICHIARATI)
    with open(os.path.join(REPO, "circuits", "preamp", "psu.net"), encoding="utf-8") as f:
        nets = set(re.findall(r'\(name "/?([^"]+)"\)', f.read()))
    for n in sorted(nets & set(req)):
        out.setdefault(n, f"la rete {n} di psu.net")
    return out


def read_prb():
    path = os.path.join(DOCS, "PRB.md")
    with open(path, encoding="utf-8") as f:
        lines = f.read().rstrip("\n").split("\n")
    # blocchi separati da righe vuote
    blocks, cur = [], []
    for ln in lines:
        if ln.strip():
            cur.append(ln)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    prb = {"title": None, "intro": [], "groups": [], "coda": [], "voci": {}}
    state = "intro"
    for b in blocks:
        first = b[0]
        if first.startswith("# ") and prb["title"] is None:
            prb["title"] = first[2:].strip()
            if len(b) > 1:
                prb["intro"].append(b[1:])
            continue
        g = re.match(r"^## ([A-Z])\. (.+)$", first)
        if g:
            state = "voci"
            prb["groups"].append({"key": g.group(1), "name": g.group(2), "voci": []})
            if len(b) > 1:
                REFUSE(f"PRB.md: testo attaccato al titolo del gruppo {g.group(1)}")
            continue
        if state == "voci" and first.startswith("## "):
            state = "coda"
        if state == "voci" and first == "---":
            state = "coda"
            continue
        if state == "voci":
            # il titolo in grassetto puo' andare a capo (PR-4, PR-17, PR-23, PR-25)
            v = re.match(r"^\*\*PR-(\d+) · (.+?)\*\*", " ".join(b), re.S)
            if not v:
                REFUSE(f"PRB.md: nel gruppo {prb['groups'][-1]['key']} un blocco non e' una "
                       f"voce: «{first[:50]}»")
                continue
            n = int(v.group(1))
            det = [x for x in b if x.startswith("*Dettagli:")]
            body = [x for x in b if not x.startswith("*Dettagli:")]
            if len(det) != 1 or b[-1] != det[0]:
                REFUSE(f"PRB.md: PR-{n} senza la riga «*Dettagli: ...*» in fondo")
            if len(body) > 3:
                REFUSE(f"PRB.md: PR-{n} ha {len(body)} righe di corpo, il PRB ne ammette al "
                       "piu' tre (ADR-053)")
            if n in prb["voci"]:
                REFUSE(f"PRB.md: PR-{n} compare due volte")
            voce = {"n": n, "title": v.group(2), "body": body,
                    "det": det[0] if det else "", "group": prb["groups"][-1]["key"]}
            prb["voci"][n] = voce
            prb["groups"][-1]["voci"].append(n)
            continue
        if state == "intro":
            prb["intro"].append(b)
        else:
            prb["coda"].append(b)
    ns = sorted(prb["voci"])
    if not ns or ns != list(range(1, ns[-1] + 1)):
        REFUSE(f"PRB.md: le voci non sono PR-1...PR-n contigue ({ns[:3]}...)")
    return prb


def refs_in(text):
    t = _strip_code(text)
    return {"pr": set(int(x) for x in re.findall(r"(?<![\w\-])PR-(\d+)(?![\w\-])", t)),
            "adr": set(re.findall(r"(?<![\w\-])ADR-(\d{3})(?![\w\-])", t)),
            "nc": set(re.findall(r"(?<![\w\-])(NC-\d{3})(?![\w\-])", t)),
            "req": set(re.findall(r"(?<![\w\-])(" + REQ_TOKEN + r")(?![\w\-])", t))}


def check_prb(prb, req, adrs, ncs):
    """b. e c.: ogni rimando del PRB esiste; una superata viaggia con chi la supera."""
    used = {}
    for n, v in sorted(prb["voci"].items()):
        r = refs_in(" ".join(v["body"] + [v["det"]]))
        v["refs"] = r
        for x in sorted(r["req"] - set(req)):
            REFUSE(f"PRB.md: PR-{n} nomina {x}, che REQUIREMENTS.md non ha")
        for x in sorted(r["adr"] - set(adrs)):
            REFUSE(f"PRB.md: PR-{n} nomina ADR-{x}, che decisions/ non ha")
        for x in sorted(r["nc"] - ncs):
            REFUSE(f"PRB.md: PR-{n} nomina {x}, che NONCOMPLIANCE.md non ha")
        for x in sorted(r["pr"] - set(prb["voci"])):
            REFUSE(f"PRB.md: PR-{n} nomina PR-{x}, che il PRB non ha")
        for x in sorted(r["adr"] & set(adrs)):
            s = adrs[x].get("superata_da")
            if s and s not in r["adr"]:
                REFUSE(f"PRB.md: PR-{n} cita ADR-{x}, superata da ADR-{s}, senza citare "
                       f"ADR-{s}: il contratto non e' univoco")
        for x in r["req"]:
            used.setdefault(x, []).append(n)
    return used


# ------------------------------------------------------------- markdown ---
def inline(s):
    if re.search(r"!?\[[^\]]*\]\(", s) or re.search(r"<[A-Za-z/!]", s):
        REFUSE(f"PRB.md: costrutto non gestito (link o HTML) in «{s[:50]}»")
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"
    s = re.sub(r"`([^`]+)`", keep, s)
    s = _html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    if "*" in s:
        REFUSE(f"PRB.md: asterisco non chiuso in «{s[:50]}»")
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{_html.escape(codes[int(m.group(1))])}</code>", s)


def block_html(b):
    first = b[0]
    if first.startswith("## "):
        out = [f"<h3>{inline(first[3:])}</h3>"]
        return "\n".join(out + ([block_html(b[1:])] if len(b) > 1 else []))
    if first == "---":
        return ""
    if all(x.startswith("|") for x in b):
        if len(b) < 2 or not re.match(r"^\|[\s\-|:]+\|$", b[1]):
            REFUSE(f"PRB.md: tabella senza riga di separazione: «{first[:40]}»")
            return ""
        h = ['<div class="tablewrap"><table><tr>']
        h += [f"<th>{inline(c)}</th>" for c in _cells(b[0])]
        h.append("</tr>")
        for row in b[2:]:
            h.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in _cells(row)) + "</tr>")
        h.append("</table></div>")
        return "".join(h)
    if all(x.startswith("- ") for x in b):
        return "<ul>" + "".join(f"<li>{inline(x[2:])}</li>" for x in b) + "</ul>"
    # un paragrafo seguito da un elenco nello stesso blocco
    k = next((i for i, x in enumerate(b) if x.startswith("- ")), None)
    if k:
        return block_html(b[:k]) + block_html(b[k:])
    for x in b:
        if re.match(r"^(#|>|\d+\.\s|- |\|)", x):
            REFUSE(f"PRB.md: costrutto markdown non gestito: «{x[:40]}»")
    return f"<p>{inline(' '.join(b))}</p>"


# -------------------------------------------------------------- sezioni ---
def _rids(frag):
    """Nel PRB un token E/F/T/P/V e' sempre un requisito (check_prb l'ha verificato):
    il link si scrive esplicito, e il linker non deve indovinare (T2, V5)."""
    parts = re.split(r"(<code>.*?</code>|<[^>]+>)", frag)
    pat = re.compile(r"(?<![\w\-])(" + REQ_TOKEN + r")(?![\w\-])")
    return "".join(p if p.startswith("<") else pat.sub(lambda m: rid(m.group(1)), p)
                   for p in parts)



def section_prb(prb):
    h = ['<p class="meta">Letto da <code>docs/preamp/PRB.md</code> a ogni generazione, '
         'nessuna riga copiata a mano. Il contratto sta sopra <code>REQUIREMENTS.md</code> '
         '(il <em>come si misura</em>, appendice B) e sopra le ADR (il <em>come si è deciso</em>, '
         'appendice A).</p>']
    for b in prb["intro"]:
        h.append(block_html(b))
    for g in prb["groups"]:
        h.append(f'<h3 class="prbg">{g["key"]}. {inline(g["name"])}</h3>')
        for n in g["voci"]:
            v = prb["voci"][n]
            body = " ".join(v["body"])
            head = f"**PR-{n} · {v['title']}**"
            if not body.startswith(head):
                REFUSE(f"PRB.md: PR-{n}, titolo non riconosciuto")
            rest = body[len(head):]
            h.append(f'<div class="voce" id="pr-{n}"><p><strong class="prn">PR-{n}</strong> '
                     f'<strong>{_rids(inline(v["title"]))}</strong>{_rids(inline(rest))}</p>'
                     f'<p class="det">{_rids(inline(v["det"][1:-1]))}</p></div>')
    for b in prb["coda"]:
        h.append(block_html(b))
    return "\n".join(h)


def section_adr(adrs):
    h = ['<p class="meta">Letto da <code>docs/preamp/decisions/</code>: la decisione è il '
         'titolo di ogni file; lo stato è quello del file, che deve coincidere con '
         'l&rsquo;indice <code>decisions/README.md</code> (due strade). Il testo intero, col '
         'contesto, le alternative scartate e il «Da riaprire se», resta nei file.</p>',
         '<div class="tablewrap"><table class="adrreg"><tr><th>ADR</th><th>Data</th>'
         '<th>La decisione</th><th>Stato</th></tr>']
    for n in sorted(adrs):
        a = adrs[n]
        cls = ' class="sup"' if a.get("superata_da") else ""
        h.append(f'<tr id="adr-{n}"{cls}><td class="num">{n}</td><td class="num">{a["data"]}</td>'
                 f'<td>{inline(a["title"])}</td><td>{inline(a["stato"])}</td></tr>')
    h.append("</table></div>")
    return "\n".join(h)


def section_req(req, used):
    order = {"E": 0, "F": 1, "T": 2, "P": 3, "V": 4}

    def key(r):
        m = re.match(r"([A-Z])(\d+)(\w*)", r)
        return (order[m.group(1)], int(m.group(2)), m.group(3))
    h = ['<p class="meta">Letto da <code>docs/preamp/REQUIREMENTS.md</code>: per E il parametro '
         'e il valore, per F, T e P la prima frase in grassetto, per V il titolo della '
         'sezione. Il testo completo, le note e il metodo di misura restano là. Le ADR sono '
         'quelle della riga del requisito (per V, quelle nominate nella sua sezione); le voci '
         'del PRB sono quelle che lo nominano.</p>',
         '<div class="tablewrap"><table class="reqidx"><tr><th>Req.</th><th>Che cosa</th>'
         '<th>ADR</th><th>PRB</th></tr>']
    for r in sorted(req, key=key):
        x = req[r]
        adr = ", ".join(f"ADR-{a}" for a in x["adr"]) or "&mdash;"
        prs = ", ".join(f"PR-{n}" for n in sorted(set(used.get(r, [])))) or "&mdash;"
        h.append(f'<tr id="req-{r.lower()}"><td class="num">{self_id(r)}</td>'
                 f'<td>{inline(x["title"])}</td>'
                 f'<td>{adr}</td><td>{prs}</td></tr>')
    h.append("</table></div>")
    return "\n".join(h)


CSS = """
a.ref{color:inherit;text-decoration:underline dotted var(--accent);text-underline-offset:2px}
a.ref:hover{color:var(--accent)}
.voce{margin:10px 0 14px;max-width:78ch}
.voce p{margin:0}
.voce .prn{color:var(--accent);font-family:"IBM Plex Mono",ui-monospace,monospace;font-weight:500}
.voce p.det{color:var(--muted);font-size:13.5px;margin-top:3px}
h3.prbg{margin-top:26px}
table.adrreg tr.sup td{color:var(--muted)}
table.adrreg td:nth-child(3){min-width:22ch}
table.adrreg td:nth-child(2){white-space:nowrap}
"""


# ---------------------------------------------------------------- link ---
SKIP_TAGS = {"svg", "style", "code", "a", "h2", "sub", "sup", "title", "script", "pre"}


def linkify(page, prb, req, adrs, nonreq):
    """e. i rimandi nei nodi di testo diventano link; gli ambigui e gli inesistenti rifiutano."""
    parts = re.split(r"(<[^>]+>)", page)
    depth = {t: 0 for t in SKIP_TAGS}
    spans = []
    out, count = [], {"n": 0}
    bad = []

    def sub(m):
        tok = m.group(1)
        if tok.startswith("PR-"):
            n = int(tok[3:])
            if n not in prb["voci"]:
                bad.append(f"il testo nomina {tok}, che il PRB non ha")
                return tok
            count["n"] += 1
            return f'<a class="ref" href="#pr-{n}">{tok}</a>'
        if tok.startswith("ADR-"):
            if tok[4:] not in adrs:
                bad.append(f"il testo nomina {tok}, che decisions/ non ha")
                return tok
            count["n"] += 1
            return f'<a class="ref" href="#adr-{tok[4:]}">{tok}</a>'
        if tok in nonreq:
            ctx = m.string[max(0, m.start() - 30):m.end() + 20].replace("\n", " ")
            bad.append(f"rimando ambiguo: «{tok}» nudo nel testo («…{ctx}…»), ma {tok} e' "
                       f"anche {nonreq[tok]}: scrivilo con des() se non e' il requisito, "
                       "con rid() se lo e'")
            return tok
        if tok not in req:
            bad.append(f"il testo nomina {tok}, che REQUIREMENTS.md non ha")
            return tok
        count["n"] += 1
        return f'<a class="ref" href="#req-{tok.lower()}">{tok}</a>'

    for p in parts:
        if p.startswith("<"):
            m = re.match(r"<(/?)([a-zA-Z][\w-]*)", p)
            if m and not p.endswith("/>"):
                name = m.group(2).lower()
                if name in depth:
                    depth[name] += -1 if m.group(1) else 1
                elif name == "span":
                    if m.group(1):
                        if spans:
                            spans.pop()
                    else:
                        spans.append('class="des"' in p or 'class="self"' in p)
            out.append(p)
            continue
        if any(depth.values()) or any(spans):
            out.append(p)
            continue
        out.append(TOKEN_RE.sub(sub, p))
    for b in sorted(set(bad)):
        REFUSE(b)
    page = "".join(out)
    ids = set(re.findall(r'\bid="([^"]+)"', page))
    for h in sorted(set(re.findall(r'href="#([^"]+)"', page)) - ids):
        REFUSE(f"ancora rotta: href=\"#{h}\" senza un id nella pagina")
    return page, count["n"]
