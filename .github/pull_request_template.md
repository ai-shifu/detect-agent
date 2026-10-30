## Change and scope

Describe the problem and resulting behavior. For a rule change, include the
canonical product ID, affected product version/interface, and before/after result.

## Evidence (rule changes)

- Official product identity reference:
- Marker reference or redacted observation; type and date:
- Injection/execution scope and known coverage limits:
- Matching semantics, AND/OR grouping, and precedence:

Use synthetic values. Do not include environment dumps, actual marker values,
credentials, IDs, internal addresses, user paths, or proprietary source.
For documentation/tooling-only changes, mark this section not applicable.

## Verification

- [ ] `python3 scripts/check.py conformance`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] Rule changes include positive/negative/coexistence fixtures and a matching
      specification version/changelog update, or this is not a rule change.

Live self-check, if available (separate from synthetic verification): expected
ID, scope, standard result, automatic result, status/exit code, and limitations.
If unavailable, say unverified. A declaration alone is not automatic recognition.
