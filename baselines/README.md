# Fixed Premium Cuts reference

Snapshot: `f09529d6b5043927ad127866eecdecd17fbe643c` (2026-10-27).

- `songs-fixed.csv`: 675 original source entries in archive order.
- `essentials-fixed.csv`: 38 owner-selected recording entries in Songs source order.
- `premiumcuts-fixed.json`: machine-readable equivalent and source provenance.
- `SHA256SUMS`: hashes of the three current data files and archived Essentials CSV.

My-Spin is deliberately excluded. Video registrations/availability may change without changing the source tracklist. Do not regenerate this baseline as part of a normal build. A deliberate owner-requested catalog correction requires a separately reviewed baseline update.

Verify after building: `python scripts/verify_fixed.py`.

## Essentials revision 2 (2026-10-27)
Explicit owner selection appends The Jumping Jacques — Gossip and Chatter after the original 32. The original selection CSV is preserved in `revisions/essentials-20261027-r1.csv`; JSON records prior IDs and hashes. Songs and its original source commit remain unchanged.

## Essentials revision 3 (2026-10-27)
Explicit owner requests append Tant de nuits (Bitter Sweet Samba), Chico Arnez’s Eso Beso, and Caterina Valente’s Saudades da Bahia. Prior 33 entries retain their relative order; the prior CSV is preserved as revisions/essentials-20261027-r2.csv. Existing source entries and My-Spin are unchanged.

## Essentials revision 4 (2026-10-27)
Explicit owner request removes only Berry Lipman — The Girls from Paramaribo ’82 from Essentials, keeping its Songs entry and playback source. The remaining 35 selections are sorted in Songs source order. Prior 36-entry order is archived as revisions/essentials-20261027-r3.csv. No Songs or Spin membership changes.

## Essentials revision 5 (2026-10-27)
Explicit owner requests add only Carol Burnett & Martha Raye — Let Go (005-a-01) and The Jumping Jacques — Lucinda (005-a-02). All 37 entries remain in Songs source order. Prior 35-entry selection is archived as revisions/essentials-20261027-r4.csv. Songs, Spin, and existing audio references are unchanged.

## Essentials revision 6 (2026-10-28)
Explicit owner request adds only Les Petits Chanteurs du Rock — Aquarela (004-b-02). Its CD00 appearance (cd-00-d1-14) shares the same verified audio and receives the Essentials badge, but does not duplicate the 38-recording selection or playback queue. The previous 37-recording CSV is archived as `revisions/essentials-20261027-r5.csv`. Songs order, all other Essentials members, Spin and all audio references remain unchanged.
