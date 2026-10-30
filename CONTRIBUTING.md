# Contributing

Use a pull request for every change. Update `detect-agent.md` first; it is the
normative source. This project does not accept arbitrary environment-prefix
matching or product-identity claims inferred only from variable names.

## Naming conventions

- Use `detect-agent` as the project name and `detect-agent.md` for the specification.
- Use lowercase names with hyphens for new files and directories. Keep conventional
  repository files such as `README.md`, `README.zh-CN.md`, `CHANGELOG.md`,
  `CONTRIBUTING.md` and `LICENSE` in their standard forms.
- Use camelCase for project-defined result fields, conformance fields and
  pseudocode identifiers, such as `agentId`, `specVersion` and `filesystemProbe`.
- Keep canonical product IDs and evidence values in their documented form; use
  lowercase names with hyphens to separate words in new IDs and evidence values.
- Preserve exact external names: environment variables, compatibility declaration
  aliases, synthetic marker values and source URLs may contain underscores.

## Rule changes and validation

For a rule change, include:

1. The canonical product ID and official identity reference.
2. A published injection path, a distribution/version inspection, or a redacted
   runtime observation. Label the evidence type and execution scope honestly.
3. Exact variable names, non-empty or exact-value semantics, AND/OR grouping,
   and priority relative to inherited host markers.
4. Synthetic positive and negative cases in `conformance/cases.json`, including
   missing/empty values, discriminator wrong values, partial conjunctions,
   and coexistence.
5. A specification version and changelog update if behavior changes.

Use non-empty checks for ordinary runtime markers. Any exact-value predicate
must explain how the value distinguishes the required context, with supporting
evidence. A fixed value observed in one build or shell is insufficient on its own
to require that value. Add `"0"`, `"false"` and whitespace positives for ordinary
markers; retain missing/empty negatives and discriminator wrong-value negatives.

A product's marketing page can support its name and positioning but does not
establish an environment-variable contract. Do not include actual credentials,
session/message/log IDs, internal service addresses, user paths, environment
dumps, or proprietary source. Small fixed sentinel values are appropriate.

Check that all canonical IDs are unique, context hints stay separate from runtime
markers, local relative links resolve, and conformance data is valid JSON with
unique case names. Run an implementation against controlled mappings only;
never infer conformance from the contributor's real environment.

Keep an isolated positive case for every canonical ID; cover `runtime-marker`
and `context-hint` separately when both apply, and use declaration positives for
declaration-only products.

Contributions to original project content are made under the MIT license.
