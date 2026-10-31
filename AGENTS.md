# Agent task entry point

Choose the user's task before editing:

| Task | Workflow | Write target | Deliverable |
| --- | --- | --- | --- |
| Implement or update detection | [Implement detection](docs/implement-detection.md) | The user's project | Integrated detector and tests against the shared fixtures |
| Contribute recognition signals | [Contribute your signals](docs/contribute-agent.md) | An independent Detect Agent checkout | Verified coverage report, or an evidence-backed rule change and PR |

[Diagnostics](docs/diagnostics.md) is the shared path for self-checks, unexpected
results, controlled reproductions and repair routing. It is not a prerequisite
for implementing a detector. Its Python checker is a development aid, not a
production SDK or validation of an implementation in another project.

## Common rules

- **Pin the source.** Before reading reference files, resolve the user's supplied
  commit/ref, including a branch or tag, to a full immutable commit SHA. If none
  was supplied, resolve the upstream default branch. Read this entry point and
  all required task files completely at that SHA, following relative links within
  the same revision. Record the SHA and ensure the specification version matches
  the fixture `spec_version`. Obtain missing/truncated content before proceeding.
- **Use one contract.** [detect-agent.md](detect-agent.md) is the only normative
  rule source; [conformance/cases.json](conformance/cases.json) supplies synthetic
  cases. Do not infer rules from product names, variable prefixes or a partial table.
- **Respect the write target.** Follow the target project's own instructions and
  preserve unrelated work. Reading Detect Agent as a reference does not authorize
  modifying it, another repository, or launcher/global shell configuration.
- **Protect values.** Query only documented variable names or specific
  evidence-backed candidates. Never dump environment values, scan prefixes or publish
  marker values, credentials, session/message/log IDs, internal endpoints, user
  paths or proprietary source. An operator-authorized, names-only listing is
  allowed only for a [self-observation](docs/contribute-agent.md#gather-evidence);
  never publish that listing. Canonical product IDs may be reported. Never export
  declarations or markers merely to make a check pass.
- **Report evidence honestly.** Synthetic conformance and live recognition are
  separate claims; test the actual implementation or affected path. Record checks
  actually run and remaining limitations. A verified upstream proposal can complete
  a proposal task; acceptance, downstream adoption and live verification remain
  separate states. Do not claim a repaired application merely because a PR exists.
- **Submit safely.** For changes to Detect Agent, follow [CONTRIBUTING.md](CONTRIBUTING.md)
  for rule evidence, checks and submission requirements. Use feature branches and
  PRs; never push directly to or merge code into `main`.
