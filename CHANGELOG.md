# Changelog

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
