#!/bin/zsh
# chunk_close.sh - close a lotto: verify, merge, realign the human's
# checkout, and PROVE the handoff is reachable from it.
#
# Usage:
#   /bin/zsh scripts/chunk_close.sh <lotto> [--dry-run]
#
#   <lotto>     the lotto being closed, exactly as STATE.md names it (L4, L3c)
#   --dry-run   run every check, then stop before merging. Changes nothing.
#
# WHY THIS EXISTS
#
# A push makes work DURABLE. It does not make it REACHABLE. L3 was pushed,
# committed and PR'd correctly and still failed the user: `main` - the
# checkout the human actually opens - kept the PREVIOUS lotto's handoff
# prompt, so the documented next step handed them the wrong file. The
# repo was disaligned and nothing said so.
#
# So a lotto is not closed when its PR is open. It is closed when `main`
# contains the work and the human's own checkout names the NEXT lotto.
#
# This script refuses rather than warns, like export_fab.sh does on DRC.
# There is no bypass flag, on purpose: the checks below are exactly the
# ones that were "remembered" and then forgotten.
#
# Exit codes:
#   0  closed (or dry-run passed)
#   1  usage
#   2  a pre-merge check refused
#   3  run_tests.sh failed
#   4  merge failed
#   5  could not realign the main checkout (usually: it is dirty)
#   6  merged, but the post-merge proof failed - READ THE MESSAGE

set -u

if [ $# -lt 1 ]; then
    echo "Usage: $0 <lotto> [--dry-run]" >&2
    exit 1
fi

LOTTO="$1"
DRY_RUN=0
if [ "${2:-}" = "--dry-run" ]; then
    DRY_RUN=1
fi

# Derived, never hard-coded - the lesson ROOT taught twice already.
ROOT=${0:A:h:h}
# The main checkout is the parent of the common git dir, so this works
# identically from a worktree and from the checkout itself.
MAIN=$(git -C "$ROOT" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
MAIN=${MAIN:h}

BRANCH=$(git -C "$ROOT" rev-parse --abbrev-ref HEAD)
NEXTDOC="docs/preamp/NEXT-SESSION.md"
STATEDOC="docs/preamp/STATE.md"

echo "== chunk_close.sh: chiusura di $LOTTO =="
echo "   ramo         : $BRANCH"
echo "   worktree     : $ROOT"
echo "   checkout main: $MAIN"
if [ $DRY_RUN -eq 1 ]; then
    echo "   MODO         : --dry-run (nessuna modifica)"
fi
echo

refuse() {
    echo "RIFIUTATO: $1" >&2
    shift
    for line in "$@"; do
        echo "           $line" >&2
    done
    exit 2
}

# --- 1. non si chiude un lotto da main -------------------------------------
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    refuse "sei su $BRANCH, non su un ramo di lotto." \
           "Il lavoro di un lotto sta su un ramo, e ci arriva da un worktree."
fi

# --- 2. niente lavoro non committato ---------------------------------------
if [ -n "$(git -C "$ROOT" status --porcelain)" ]; then
    refuse "il working tree non e' pulito." \
           "Committa (o scarta) prima di chiudere il lotto:" \
           "  git -C $ROOT status --short"
fi

# --- 3. niente commit non pushati ------------------------------------------
# Questo e' il controllo che CLAUDE.md dice di fare "verificandolo, non
# assumendolo". Qui e' verificato per costruzione.
if ! git -C "$ROOT" rev-parse --verify --quiet "origin/$BRANCH" > /dev/null; then
    refuse "il ramo $BRANCH non esiste su origin." \
           "  git -C $ROOT push -u origin $BRANCH"
fi
UNPUSHED=$(git -C "$ROOT" log --oneline "origin/$BRANCH..HEAD")
if [ -n "$UNPUSHED" ]; then
    refuse "ci sono commit non pushati su $BRANCH:" "$UNPUSHED" \
           "  git -C $ROOT push"
fi

# --- 4. il lotto deve aver aggiornato lo stato -----------------------------
# Un lotto che non tocca STATE.md non e' un lotto: e' lavoro che la
# sessione dopo dovra' prima capire e poi riparare.
BASE=$(git -C "$ROOT" merge-base HEAD origin/main)
if ! git -C "$ROOT" diff --name-only "$BASE" HEAD | grep -qx "$STATEDOC"; then
    refuse "questo ramo non ha modificato $STATEDOC." \
           "Ogni lotto aggiorna lo stato prima di chiudere - e' cio' che" \
           "rende ripartibile il progetto a freddo."
fi

# --- 5. STATE.md deve dichiarare FATTO il lotto che stiamo chiudendo -------
if ! grep -Eq "^\| *${LOTTO} *\|.*\*\*fatto\*\*" "$ROOT/$STATEDOC"; then
    refuse "la tabella dei lotti in $STATEDOC non segna $LOTTO come **fatto**." \
           "Riga attesa, nella tabella dei lotti:" \
           "  | $LOTTO | ... | **fatto** |"
fi

# --- 6. l'handoff deve nominare il PROSSIMO lotto, non questo -------------
# IL controllo. E' esattamente l'errore commesso alla chiusura di L3.
if [ ! -f "$ROOT/$NEXTDOC" ]; then
    refuse "$NEXTDOC non esiste."
fi
NEXT_TITLE=$(head -1 "$ROOT/$NEXTDOC")
if echo "$NEXT_TITLE" | grep -Eq "(^|[^A-Za-z0-9])${LOTTO}([^A-Za-z0-9]|$)"; then
    refuse "$NEXTDOC nomina ancora $LOTTO, il lotto appena finito." \
           "Titolo trovato: $NEXT_TITLE" \
           "L'handoff deve gia' descrivere il lotto SUCCESSIVO: e' il file" \
           "che l'umano apre per far ripartire il lavoro."
fi
echo "   handoff: \"$NEXT_TITLE\" (non nomina $LOTTO) OK"

# --- 7. la suite ------------------------------------------------------------
echo
echo "-- run_tests.sh --"
/bin/zsh "$ROOT/scripts/run_tests.sh" > "$ROOT/.chunk_close_tests.log" 2>&1
rc=$?
tail -1 "$ROOT/.chunk_close_tests.log"
rm -f "$ROOT/.chunk_close_tests.log"
if [ $rc -ne 0 ]; then
    echo "RIFIUTATO: run_tests.sh esce $rc. Un lotto non si chiude sui test rossi." >&2
    exit 3
fi

# --- 8. la PR deve esistere -------------------------------------------------
PR=$(gh pr list --head "$BRANCH" --state open --json number --jq '.[0].number' 2>/dev/null)
if [ -z "$PR" ] || [ "$PR" = "null" ]; then
    refuse "nessuna PR aperta per $BRANCH." \
           "La PR e' la traccia del lotto, non cerimonia: URL stabile, un" \
           "commit per lotto su main, e un corpo che il gate potra' citare." \
           "  gh pr create --base main --head $BRANCH --title ... --body-file ..."
fi
echo "   PR #$PR aperta OK"

if [ $DRY_RUN -eq 1 ]; then
    echo
    echo "== --dry-run: tutti i controlli passati, niente e' stato modificato =="
    echo "   Per chiudere davvero: /bin/zsh scripts/chunk_close.sh $LOTTO"
    exit 0
fi

# --- 9. merge ---------------------------------------------------------------
echo
echo "-- merge della PR #$PR --"
if ! gh pr merge "$PR" --squash --delete-branch; then
    echo "MERGE FALLITO: la PR #$PR non e' stata mergiata." >&2
    exit 4
fi

# --- 10. riallineo del checkout dell'umano ---------------------------------
# Il punto di tutto lo script. Senza questo il lavoro e' durevole ma non
# raggiungibile, che e' il difetto che ha prodotto questo file.
echo
echo "-- riallineo di $MAIN --"
MAIN_BRANCH=$(git -C "$MAIN" rev-parse --abbrev-ref HEAD)
if [ "$MAIN_BRANCH" != "main" ]; then
    echo "NON RIALLINEATO: $MAIN e' sul ramo '$MAIN_BRANCH', non su main." >&2
    echo "                 La PR #$PR E' GIA' MERGIATA. Riallinea a mano:" >&2
    echo "                   git -C $MAIN checkout main && git -C $MAIN pull --ff-only" >&2
    exit 5
fi
if ! git -C "$MAIN" pull --ff-only; then
    echo "NON RIALLINEATO: 'git pull --ff-only' ha rifiutato in $MAIN." >&2
    echo "                 Di solito significa che quel checkout ha modifiche" >&2
    echo "                 locali o commit propri. NON le tocco." >&2
    echo "                 La PR #$PR E' GIA' MERGIATA: sistema quel checkout e" >&2
    echo "                 rilancia:  git -C $MAIN pull --ff-only" >&2
    exit 5
fi

# --- 11. la prova, letta DAL checkout dell'umano ---------------------------
# Non si dichiara riallineato: si legge da li' e si verifica.
echo
echo "-- prova, letta da $MAIN --"
MAIN_NEXT=$(head -1 "$MAIN/$NEXTDOC" 2>/dev/null)
if echo "$MAIN_NEXT" | grep -Eq "(^|[^A-Za-z0-9])${LOTTO}([^A-Za-z0-9]|$)"; then
    echo "PROVA FALLITA: $MAIN/$NEXTDOC nomina ancora $LOTTO." >&2
    echo "               Titolo: $MAIN_NEXT" >&2
    exit 6
fi
if ! grep -Eq "^\| *${LOTTO} *\|.*\*\*fatto\*\*" "$MAIN/$STATEDOC"; then
    echo "PROVA FALLITA: $MAIN/$STATEDOC non segna $LOTTO come fatto." >&2
    exit 6
fi
echo "   $MAIN/$STATEDOC     : $LOTTO segnato **fatto** OK"
echo "   $MAIN/$NEXTDOC: \"$MAIN_NEXT\" OK"
echo "   HEAD di main             : $(git -C "$MAIN" log --oneline -1)"

# --- 12. igiene del worktree -----------------------------------------------
# Un worktree non puo' rimuovere se stesso mentre ci sei dentro.
echo
echo "== $LOTTO CHIUSO. main contiene il lavoro e l'handoff nomina il prossimo lotto. =="
if [ "$ROOT" != "$MAIN" ]; then
    echo
    echo "Resta da rimuovere questo worktree (non puo' farlo da se'):"
    echo "  git -C $MAIN worktree remove $ROOT"
    echo "  git -C $MAIN branch -D $BRANCH"
fi
exit 0
