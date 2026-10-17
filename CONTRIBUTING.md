# Contributing

Use a pull request for every change. Update `detect_agent.md` first; it is the
normative source. This project does not accept arbitrary environment-prefix
matching or product-identity claims inferred only from variable names.

For a rule change, include:

1. The canonical product ID and official identity reference.
2. A published injection path, a distribution/version inspection, or a redacted
   runtime observation. Label the evidence type and execution scope honestly.
3. Exact variable names, non-empty or exact-value semantics, AND/OR grouping,
   and priority relative to inherited host markers.
4. Synthetic positive and negative cases in `conformance/cases.json`, including
   missing/empty values, wrong sentinels, partial conjunctions, and coexistence.
5. A specification version and changelog update if behavior changes.

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
