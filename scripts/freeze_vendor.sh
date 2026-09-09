#!/bin/sh
# freeze_vendor.sh - make every file under vendor/ read-only (0444).
# Idempotent: safe to re-run any time. This is the structural
# enforcement that vendor originals are never hand-edited in place.
set -e

# Derived from this script's own location, never hard-coded: run from a
# worktree, a hard-coded path would freeze the MAIN checkout and not the
# files just added here, in silence. Same family as ROOT in run_tests.sh
# and run_simulation.sh. This is /bin/sh, so no ${0:A:h:h}.
VENDOR_DIR="$(cd "$(dirname "$0")/.." && pwd)/vendor"

if [ ! -d "$VENDOR_DIR" ]; then
    echo "ERROR: $VENDOR_DIR does not exist" >&2
    exit 1
fi

count=0
while IFS= read -r f; do
    chmod 0444 "$f"
    count=$((count + 1))
done << EOF
$(find "$VENDOR_DIR" -type f ! -name "README.md" ! -name ".DS_Store")
EOF

echo "Froze $count file(s) under $VENDOR_DIR to mode 0444."
