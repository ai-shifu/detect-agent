# Implement detection in your project

Use this workflow to add, update or repair detection in the user's application.
The application is the **write target**; Detect Agent is a **read-only reference**.
Follow [the common rules](../AGENTS.md#common-rules) for source pinning, privacy
and authorization. Python, a vendor application and recognition of the agent
performing the work are not prerequisites.

## Establish the target and source

1. Identify the target repository, its instructions, existing detector, language,
   test runner and intended integration point. Reuse the existing integration and
   preserve unrelated work. Ask for the target or call site only if it cannot be
   established from the user's task and workspace.
2. Pin the reference source using the common rules. Read `AGENTS.md`, this guide,
   [the full specification](../detect-agent.md) and
   [the fixtures](../conformance/cases.json) at that same SHA. The upstream source
   is <https://github.com/ai-shifu/detect-agent>; a separate reference clone is
   optional. Fetch material during development, without replacing the target checkout.

## Implement and integrate locally

Implement the complete pinned contract in the target project's language and
conventions. Accept a caller-supplied environment lookup provider and optional
filesystem/TTY capabilities. Preserve provider name semantics and both result
fields; follow the specification for normalization, matching, priority and
per-call evaluation. Derive any boolean using its documented evidence rule.

Keep the detector local and testable. Do not import the repository's Python
checker as a production SDK, add Python to another-language application, parse
remote Markdown on production requests or add runtime rule-refresh networking.

Update existing code to match the chosen contract; keep the fixture expectations
intact. For an unexpected result, use [Diagnostics](diagnostics.md) to identify
the responsible layer rather than changing upstream rules to fit incorrect code.
For an implementation repair, add a regression that fails before the repair and
passes afterward. Integrate only the capability the user requested.

## Run the fixtures through the target implementation

Create a test adapter in the target language that loads the pinned cases and
invokes **the implementation you changed**. Compare `agent_id` and `evidence`
with every `expected` pair. Preserve source commit/version with the target tests;
passing Detect Agent's reference checker does not validate this implementation.

| Fixture input | Required adapter behavior |
| --- | --- |
| `env` | Use only the supplied synthetic mapping, even when empty; never merge the host environment. |
| `env_name_case` | Default to `sensitive`; `ascii-insensitive` uses the specification's ASCII name transform, not value normalization. Reject colliding keys. |
| `path_separator` | Honor the emulated separator. If absent, use a documented deterministic emulation, such as POSIX `:`, rather than the test host. |
| `files` | Absent means no capability; `[]` means an available probe finding no paths. Never access the actual filesystem for a fixture. |
| `stdout_is_tty` | Use the supplied boolean; absent means unavailable, not the test runner's terminal state. |
| `expected` | Compare both fields exactly, including null IDs. A matching ID with different evidence is a failure. |

Execute every case and report its count and failures. Do not skip unsupported
fields or treat unimplemented capabilities as passing. Run the inline specification
examples too. For languages with configurable default locales, check relevant
host locale settings, including Turkish where available; configure the runtime,
not an invented fixture field or merely an environment entry named `locale`.

Run relevant application integration checks: confirm callers receive the result
and evidence, forward optional capabilities deliberately, and avoid unrelated
telemetry, authorization or behavior changes.

## Complete the task

Deliver target code and tests, the source commit/specification version, changed
files and API/call site, plus the commands actually run, fixture count, integration
results and remaining limitations. If tools or access block work, deliver the
concrete patch/findings and state the unchecked step.

Use [Diagnostics](diagnostics.md) for an optional original-path live recheck or
any unresolved mismatch; include its report when relevant. An unrecognized
current agent, `none` or `context-hint` can be a valid outcome and does not require
adding upstream rules before completing the existing portable contract.
