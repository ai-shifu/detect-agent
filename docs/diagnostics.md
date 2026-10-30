# Diagnose and repair a detection result

Use this shared workflow to check one command environment or investigate a
reported mismatch. Return to [Implement detection](implement-detection.md) for
target-project work or [Contribute your signals](contribute-agent.md) for an
evidence-backed rule change. [AGENTS.md](../AGENTS.md) supplies the common source
pinning, privacy and authorized-write rules; [the specification](../detect-agent.md)
remains the detection contract.

## 1. Establish what is being checked

Establish the expected product/launcher independently of the detector output or
model name. Record its canonical ID if registered, product version when known,
platform and command scope: editor shell, CLI child process, plugin hook, desktop
host, remote container or another interface. Coverage can differ by interface.

Locate the detector and call site that produced the result. For a repository
self-check, investigate that checker and its specification; no business application
is needed. For a consuming application, invoke its actual detector and integration
through the affected path. Record the implementation version and pinned source
commit/specification version. If provenance is missing, report the gap and choose
a baseline before claiming the implementation is current.

Compare the expected and actual **`(agent_id, evidence)` pair**, not just a product
name or boolean. This contract describes environment context, not an authenticated
immediate caller.

## 2. Run the relevant checks

The optional repository checker uses Python 3.9+ and the standard library, with
no installation or network access. From the pinned Detect Agent checkout:

```sh
python3 scripts/check.py conformance
python3 scripts/check.py self-check --expect codex
```

Replace `codex` with the independently established canonical ID. If the identity
is unknown or the product is unregistered, omit `--expect`; do not invent or borrow
an ID. Launch self-check through the actual command tool being investigated.
Running it in a human terminal only tests that terminal. Do not export declarations
or markers to make it pass.

`conformance` evaluates synthetic fixtures; `self-check` observes its command
process. These are separate claims. Passing the repository checker does not test
a consuming implementation. To test that implementation, run the shared fixtures
through it as described in [Implement detection](implement-detection.md#run-the-fixtures-through-the-target-implementation).
The Python checker is a development aid, not a production SDK.

If Python is unavailable, evaluate the pinned specification and fixtures using an
available language, then perform standard detection and a separately labeled
declaration-omitting diagnostic through the relevant tool. Preserve lookup semantics
and keep values private. If execution or required source access is unavailable,
report the unchecked step; do not claim conformance or live recognition.

## 3. Read the diagnostic correctly

The JSON `result` follows the full contract. `automatic_result` is a diagnostic
counterfactual that ignores only `AI_AGENT` and `AGENT` in a local lookup provider.
It changes neither the process/shell environment nor production declaration
precedence. Never replace production detection with this diagnostic.

For `self-check`:

- With `--expect`, exit **0** means both results match the expected ID with
  `runtime-marker` evidence.
- Exit **1** means that full condition was not met. In `declaration-masked`,
  `automatic_result` correctly matches the expected runtime marker while a
  declaration masks `result`; exit 1 does not mean the marker is absent.
- Without `--expect`, a valid diagnostic exits **0** as an observation, regardless
  of whether it found an agent. This does not establish correct recognition.
- Exit **2** means invalid arguments or specification/input errors. The
  conformance command also rejects invalid fixture files.

## 4. Reproduce and choose the responsible layer

Build the smallest synthetic mapping that preserves the relevant conditions.
Replace private values with synthetic strings while preserving missing/empty
states, public exact discriminators, complete AND/OR groups, competing markers
and relevant PATH structure. Supply synthetic lookup, filesystem, TTY and PATH
separator capabilities; missing capabilities stay unavailable. Never merge host
environment values or real filesystem/TTY state into fixtures.

Evaluate **the same mapping and optional inputs** through the actual target
detector and the pinned contract. Compare both result fields, keeping the existing
fixture expectations intact. An unexpected name or exit code alone does not
establish a rule defect.

| Finding | Action and write target |
| --- | --- |
| Both results match the expected runtime marker in the supported scope | Report verified coverage for that scope; no rule change is needed. |
| Target output differs from the pinned contract | Add the failing regression and fix the target implementation, input adapter or test adapter using [Implement detection](implement-detection.md). Do not change upstream expectations to make incorrect code pass. |
| Target implements an older specification | Review and select a newer full source SHA, then update the target implementation and fixtures using [Implement detection](implement-detection.md). Keep rule refresh at development time. |
| Detector result is correct but the application interprets it incorrectly | Fix the target integration/UI. Preserve `evidence`, apply the specification's evidence-based `is_agent` rule and keep `agent_id` separate. Do not display hints as confirmed execution or `none` as proof of a human caller. |
| A declaration masks runtime markers | Preserve declaration precedence. An unknown non-empty declaration returning `(null, declared)` and blocking fallback is specified behavior. Show both results; correcting a launcher declaration is an explicit operator decision, made only within an authorized task. Do not silently skip declarations or change global shell settings. |
| Another runtime rule wins because markers coexist | Compare complete predicates and documented priority, and retain a coexistence reproduction. A contract-compliant result can describe inherited context; do not reorder rules or discard markers to force a claimed identity. Investigate a supported discriminator if needed. |
| The target follows the contract but a rule is demonstrably wrong or missing | Gather producer/observation evidence and follow [Contribute your signals](contribute-agent.md) and [CONTRIBUTING.md](../CONTRIBUTING.md) in an independent Detect Agent checkout, when that write target is authorized. |
| Coverage is only a context hint, an explicit declaration, or absent for this interface | Report the supported boundary. A hint does not confirm execution, a declaration does not prove automatic recognition, and `(null, none)` does not prove human execution. Do not invent markers or promote hints without evidence. |

If identity or evidence is insufficient, report what is missing and keep that
outcome unverified. A supported coverage limit can be the final diagnosis.

## 5. Verify the repair and report

For a target repair, first confirm the new regression fails on the old behavior.
Follow the [implementation workflow](implement-detection.md) for the complete
shared-fixture and integration checks on the repaired target. For a rule repair,
follow the [contribution workflow](contribute-agent.md) for evidence, contract
updates and repository checks. Do not hard-code your own ID to pass a check.

Repeat the original application/tool path in the same scope when available. After
an authorized launcher change, start a fresh command and verify both results.
Claim a live fix only when that path was actually retested; otherwise distinguish
passing synthetic tests from the unverified live outcome.

An upstream PR is a proposal, not proof of acceptance or downstream adoption.
Report those states separately. If the authorized task ends at a verified proposal,
deliver it and report adoption or live checks outside that task as pending.

Use one diagnostic report, including only checks actually performed:

```text
Expected product / canonical ID / product version (or unknown):
Execution scope / platform / detector and call site:
Implementation version / source commit / specification version:
Expected and actual (agent_id, evidence), before and after if repaired:
Standard result / automatic diagnostic result (or not run):
Self-check status and exit code (or not run):
Diagnosis / responsible layer / authorized write target:
Regression, fixture count and integration commands/results:
Evidence reference/date, changed files and patch/PR/adoption status:
Original-path live recheck / remaining limits or pending steps:
```
