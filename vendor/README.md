# vendor/ — READ-ONLY vendor originals

## Rule (enforced, not just documented)

Everything under `vendor/` is an **unmodified original** file exactly as
obtained from its source (a vendor website, a datasheet zip, an email
attachment, etc.). Files here are:

- Never hand-edited in place.
- Set to file mode `0444` (read-only for everyone, no write bit) immediately
  after being added, via `scripts/freeze_vendor.sh`. Attempting to edit one
  in place will fail with a permission error — that is the point.
- Accompanied by a `PROVENANCE.json` sidecar (per part directory) recording
  where the file came from, when it was obtained, and its checksum.
- Accompanied by a `<file>.sha256` checksum file for tamper detection.

If you need a modified/patched/converted version of a vendor file (fixed
syntax, renamed subckt, ngspice-compatibility patch, extracted single
model from a multi-part library, etc.), **do not edit the file here**.
Instead:

1. Copy it into the matching device-class directory under `models/`.
2. Record what you changed and why in that copy's `.provenance.json`
   sidecar (see `models/README.md` and `models/PROVENANCE_CONVENTION.md`).
3. Leave this original untouched, forever, as the audit trail.

## Layout

```
vendor/<device_class>/<vendor_name>/<part_name>/
    <original_file(s) exactly as obtained>
    <original_file>.sha256
    PROVENANCE.json
```

## Re-enforcing read-only mode

If a file here ever ends up writable again (e.g. after `git clone` on some
systems, or `cp` from elsewhere), re-run:

```
/Users/roberto/EDA/scripts/freeze_vendor.sh
```

This is idempotent and safe to run any time / in CI.

## Note on the demo vendor file in this repo

`vendor/diodes/demo_vendor/1N4148_TEST/` contains a **fabricated,
disposable** "vendor-style" diode model file used only to demonstrate the
vendor-original -> curated-copy workflow (see
`models/diodes/generic_diode_from_vendor.lib` and its `.provenance.json`).
It is NOT a real datasheet-derived 1N4148 model and must not be used for
anything beyond demonstrating this pipeline.
