# Premium Cuts analytics

The unchanged owner-supplied Google tag (`G-H3JRZ1NCM9`) appears exactly once in every generated HTML head. `analytics-privacy.js` runs synchronously before that tag: it sets query/hash-free `page_location` and `page_referrer`, and refreshes the page location before `pushState`/`replaceState` and on `popstate`. It does not change the browser URL or search behavior. The custom code never sends a `page_view`.

Custom events (all parameters are allowlisted):

| Event | Parameters | Trigger |
| --- | --- | --- |
| `pc_player_intent` | `action`, optional public `song_id` | Player buttons / song or queue selection, before playback outcome |
| `pc_playback_state` | `state` (`playing`, `paused`, `completed`), public `song_id` | Matching active YouTube API state, not a click |
| `pc_catalog_search` | boolean `query_present`, bounded `result_count` | Search input settles for 500 ms; never the text |
| `pc_catalog_filter` | fixed `filter_type`, bounded `result_count` | Filter/sort input |
| `pc_destination_open` | fixed destination category | YouTube, sibling archive, or other external link intent; never its URL |

Repeated identical playback states are suppressed. Pause/end before playing are suppressed; completion after pause/stop is not counted. Changing the loaded recording resets state. Document delegation and a global installation guard prevent duplicate listeners during SPA navigation. Reference renditions report the public catalog song ID, not an arbitrary supplied ID.

Google's account-controlled enhanced measurement is separate. This code does not re-emit its standard `video_*`, `click`, `view_search_results`, or `page_view` names. Such automatic events may still exist alongside these differently scoped operational events; do not add their counts together. No claim is made that site code can disable account enhanced measurement. In particular, query-free page fields alone require review against automatic site-search extraction: the actual browser URL still contains the existing catalog `q` parameter. No Analytics management setting has been accessed or changed, and server receipt has not been tested.

Offline checks: `python scripts/verify_analytics.py` checks every generated page; `node scripts/verify_analytics.cjs` verifies state deduplication, intent separation, query-free custom payloads, SPA listener guarding, privacy/history ordering and real player callbacks via the existing mock harness. They do not assert browser network delivery or Premium membership/ad behavior.

Official references: https://developers.google.com/analytics/devguides/collection/ga4/reference/config and https://support.google.com/analytics/answer/9216061?hl=en . Enhanced site-search can send search_term from q if enabled in the property; this uninspected account setting is not claimed disabled.
