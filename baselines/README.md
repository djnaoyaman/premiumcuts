# Fixed Premium Cuts reference

Snapshot: `f09529d6b5043927ad127866eecdecd17fbe643c` (2026-10-27).

- `songs-fixed.csv`: 675 original source entries in archive order.
- `essentials-fixed.csv`: 33 owner-selected recording entries in selection order.
- `premiumcuts-fixed.json`: machine-readable equivalent and source provenance.
- `SHA256SUMS`: hashes of the three current data files and archived Essentials CSV.

My-Spin is deliberately excluded. Video registrations/availability may change without changing the source tracklist. Do not regenerate this baseline as part of a normal build. A deliberate owner-requested catalog correction requires a separately reviewed baseline update.

Verify after building: `python scripts/verify_fixed.py`.

## Essentials revision 2 (2026-10-27)
Explicit owner selection appends The Jumping Jacques — Gossip and Chatter after the original 32. The original selection CSV is preserved in `revisions/essentials-20261027-r1.csv`; JSON records prior IDs and hashes. Songs and its original source commit remain unchanged.
