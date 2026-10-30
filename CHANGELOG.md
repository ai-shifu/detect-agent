# Changelog

## Unreleased

- Add an incorrect-detection repair workflow covering implementation, integration,
  launcher and upstream-rule causes; link it from both task prompts and Agent guides.
- Organize both READMEs around two copy-paste prompts: implement detection in the
  user's project first, then contribute a product's signals.
- Add dedicated Agent workflows with explicit write targets, source revisions,
  verification and deliverables; keep live diagnostics as a supporting guide.
- Add an Agent entry point and a self-check/update guide linked from both READMEs.
- Add optional local development checks, redacted live diagnostics and CI.
- Add a pull request template for rule evidence, scope and verification.
- Keep the 0.1.5 detection contract unchanged.

## 0.1.5 — 2026-10-17

- Use non-empty checks for ordinary VT Code, WorkBuddy, Grok Bot, Cue and Muse markers.
- Retain exact Grok Build sentinel and Cursor execution-role comparisons.
- Cover arbitrary non-empty values, empty markers and compound-rule boundaries.

## 0.1.4 — 2026-10-17

- Remove configurable `JUNIE_DATA` from Junie detection; require non-empty `JUNIE_SHIM_PATH`.
- Add configuration-only negatives and coexistence/fallback regression cases.

## 0.1.3 — 2026-10-16

- Preserve the actual environment provider's name-lookup semantics, including native Windows lookup.
- Add explicit synthetic name-casing adapters and cross-provider conformance cases.

## 0.1.2 — 2026-10-16

- Define declaration trimming as U+0009 through U+000D and U+0020 at string boundaries.
- Add ASCII whitespace, retained NBSP, internal whitespace and control-character cases.

## 0.1.1 — 2026-10-16

- Define declaration normalization as locale-independent ASCII lowercase.
- Add uppercase-I and non-ASCII declaration cases to prevent language/runtime differences.
- Complete isolated catalog, runtime/context and alternative coverage; remove a duplicate fixture.

## 0.1.0 — 2026-10-16

- Initial language-independent detection contract and ordered marker rules.
- 35 canonical IDs, declaration aliases, and separate context-hint semantics.
- Non-empty QwenWork and Doubao Work rules; separate Manus and Cue identities.
- Evidence classifications, pinned source snapshots, and synthetic conformance cases.
