# Fixed Premium Cuts reference

Snapshot: `f09529d6b5043927ad127866eecdecd17fbe643c` (2026-10-27).

- `songs-fixed.csv`: 675 original source entries in archive order.
- `essentials-fixed.csv`: 32 owner-selected recording entries in selection order.
- `premiumcuts-fixed.json`: machine-readable equivalent and source provenance.
- `SHA256SUMS`: hashes of the three data files.

My-Spin is deliberately excluded. Video registrations/availability may change without changing the source tracklist. Do not regenerate this baseline as part of a normal build. A deliberate owner-requested catalog correction requires a separately reviewed baseline update.

Verify after building: `python scripts/verify_fixed.py`.
