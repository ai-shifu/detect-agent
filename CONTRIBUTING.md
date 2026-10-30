# Contributing

Use a pull request for every change. Update `detect-agent.md` first; it is the
normative source. This project does not accept arbitrary environment-prefix
matching or product-identity claims inferred only from variable names.

Agents contributing their product's signals should follow
[the contribution workflow](docs/contribute-agent.md), starting from
[AGENTS.md](AGENTS.md). First distinguish a
missing specification rule from an outdated consuming implementation or a
declaration masking runtime evidence. Run a live diagnostic through the affected
command interface; keep it separate from synthetic conformance results.

To implement detection in another project, use
[the implementation workflow](docs/implement-detection.md). That task writes to
the target project and validates its implementation against the shared cases.

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

Run the repository checks with Python 3.9+ (standard library only):

```sh
python3 scripts/check.py conformance
python3 -m unittest discover -s tests -v
```

The checker interprets `detect-agent.md` and runs the synthetic cases. For a new
rule form, extend the checker and its focused tests as needed; unsupported forms
must fail explicitly. Do not introduce a second rule catalog. For a behavior
change, keep the specification version, fixture `spec_version`, both README
version references, and changelog in sync. Documentation/tooling-only changes do
not require a detection-contract version bump.

Use the [pull request template](.github/pull_request_template.md) to record
evidence, validation and coverage limits. Never merge into `main`.

Contributions to original project content are made under the MIT license.
