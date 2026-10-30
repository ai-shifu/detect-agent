# Implement detection in your project

Use this workflow to add or update agent detection in the user's application.
The application is the **target project**; Detect Agent is a **read-only reference**.
Follow the target project's instructions, language, tests and contribution rules.
This workflow does not require Python, a vendor application, or a known identity
for the agent doing the implementation.

## Establish the target and source

1. Identify the target repository from the user's task and current workspace.
   Inspect its instructions, existing detector, language, test runner and intended
   integration point. Preserve unrelated changes. Reuse the existing integration
   where appropriate; add only the detection capability the user requested.
2. Locate Detect Agent using the supplied checkout or repository reference.
   Resolve the user's specified commit or ref, including a branch or tag, to a
   full immutable commit SHA before reading any reference file. If none was
   supplied, resolve the upstream default branch to a full commit SHA. Record the
   resolved SHA and use it for every reference-file read.
3. Read the **complete contents** of this guide, `detect-agent.md`, and
   `conformance/cases.json` at that same commit. Read the specification version
   from the document and verify it matches the fixture `spec_version`. GitHub
   blob/raw URLs, repository tools, or a local checkout are all suitable. Follow
   relative links within the same pinned revision rather than mixing revisions.

The upstream repository is <https://github.com/ai-shifu/detect-agent>. Resolve and
fetch reference material during development only. Do not add a production network
request to refresh rules. A clone is optional; if you use one, keep it separate
from the target project and do not replace the target's checkout or instructions.

If the target project or integration point cannot be established, ask for that
missing information. If source content is unavailable or truncated, obtain the
remaining content before claiming a complete implementation. Do not reconstruct
rules from a summary, a partial table, or the current agent's observed markers.

## Implement the pinned contract locally

Implement a small function in the target project's language and conventions.
Port the result contract, matching semantics, ordered algorithm and complete
catalog from [the specification](../detect-agent.md), which remains authoritative.
The function must accept a caller-supplied environment lookup provider, with
optional filesystem and stdout-TTY capabilities where the contract uses them.
Use named lookups and preserve the actual provider's name-lookup semantics.

Pay particular attention to ASCII-only declaration normalization and unknown
declarations blocking fallback; non-empty versus exact comparisons; complete
AND/OR groups; ordered runtime rules before context hints; and unavailable probes.
Preserve `agent_id` and `evidence` in the result. If the application also needs a
boolean, derive it using the specification's rule rather than collapsing hints
into confirmed agent execution. Evaluate inputs on each call; markers can change
between tool calls, so do not cache a result for the process lifetime.

The Python checker in this repository is a development aid. Do not import it as a
production SDK, make Python a dependency of a different-language application, or
parse the remote Markdown on every production request. Keep the implementation
local and testable. Avoid logging or returning environment values, including
declarations that are not recognized catalog IDs.

An existing implementation may disagree with the pinned contract. Update that
implementation and its tests to match the contract; do not edit the reference
specification or fixture expectations just to make the existing code pass. A
suspected upstream gap can be reported separately through the
[contribution workflow](contribute-agent.md).

For an incorrect result in the actual application, follow
[Fix incorrect detection](fix-detection.md). Reproduce it through the target
function and call site, add a failing regression, and repair the responsible
implementation or integration. Use upstream contribution only when evidence
shows the rule itself needs changing; preserve the user's authorized write target.

## Run the fixtures through the target implementation

Create a test adapter in the target project's language that loads the pinned
`conformance/cases.json`, invokes **the implementation you just changed**, and
compares both `agent_id` and `evidence` with each case's `expected` result. Keep
fixture provenance with the target tests, using the source commit and version.
Running Detect Agent's reference checker does not validate the target detector.

The adapter must honor all fixture inputs:

| Input | Required test behavior |
| --- | --- |
| `env` | Use only the supplied synthetic mapping, including an empty mapping. Never merge in the test process's environment. |
| `env_name_case` | Default to `sensitive`; implement `ascii-insensitive` with the specification's ASCII name transform. It changes key lookup, not value comparison. Reject keys that collide under that transform. |
| `path_separator` | Use the case's emulated PATH-list separator when supplied. Otherwise use a documented, deterministic emulated platform; a POSIX `:` baseline is suitable. Do not select it from the test host. |
| `files` | An absent field means no filesystem capability. An empty list means an available probe reporting that no listed paths exist. Never consult the real filesystem for a fixture. |
| `stdout_is_tty` | Use the supplied boolean. An absent field means unknown/unavailable; never fill it from the test runner's terminal. |
| `expected` | Compare the canonical ID or null and the exact evidence category. A matching ID with different evidence is a failure. |

Validate that the adapter has loaded every case; report the actual executed count
and any failures. Do not skip unsupported fixture fields or mark an unimplemented
capability's tests as passing. These inputs emulate provider and platform
behavior independently of the machine running the suite.

Run the inline examples from the specification as additional contract checks.
If the language has configurable default locales, verify that declaration results
remain identical under relevant host locale settings, including Turkish where
available. Configure the language runtime itself; adding a synthetic environment
entry named `locale` does not exercise locale-dependent string operations.

Then run the target project's relevant integration checks. Confirm that callers
receive the result and evidence correctly, optional capabilities are supplied
deliberately, and the detector fits the intended call site without unrelated
telemetry, authorization or application behavior changes.

## Optional live observation and completion

A live smoke check is separate from conformance. If useful and available, invoke
the target implementation through the actual command tool and report its result
and execution scope without environment values. Do not export declarations or
markers to make it pass. [The self-check guide](agent-self-check.md) explains how
declarations can mask automatic evidence; running its reference command alone
still does not validate your target implementation.

An unrecognized current agent does not block completing a portable detector.
`none` and `context-hint` are valid outcomes. Do not add upstream rules as a
prerequisite for implementing the existing specification.

Complete the task with the target code, meaningful tests and integration, plus:

- The upstream Git commit and specification version used.
- The target files changed and the resulting API/integration point.
- The commands actually executed, fixture count, results and integration checks.
- Any separately labeled live observation and its execution scope.
- Remaining limitations or checks that could not be run.

If tools or access prevent implementation or verification, deliver the concrete
patch or findings available and state the blocked step. Do not claim conformance
when only the reference checker passed or the target tests were not executed.
