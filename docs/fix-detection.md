# Fix an incorrect detection

Use this workflow when an observed result disagrees with the expected product or
evidence. Diagnose the cause, make the smallest justified repair in the correct
repository, and verify the result. A mismatch alone is not a reason to add a
marker or change rule priority. [The specification](../detect-agent.md) describes
environment context, not an authenticated immediate caller.

## 1. Reproduce the reported error

Establish the expected product independently of the detector output or model
name. Record its canonical ID if registered, version when known, platform and
execution scope. An editor shell, CLI child process, plugin hook and remote
container may expose different signals.

Find the detector and call site that produced the reported result. For a repository
self-check report, use that checker and its specification as the implementation
and source under investigation; no separate business application is needed. For
a consuming application, locate its actual detector and integration. Record the
implementation version and the specification commit/version it implements.
Resolve every source ref to a full immutable SHA and read the complete
specification and fixtures at that SHA. If provenance is missing, report that
gap and establish a chosen baseline before claiming the implementation is current.

Capture the expected and actual **`(agent_id, evidence)` pair**, not just a product
name or boolean. Invoke the actual implementation through the affected application
or tool path. A successful repository checker does not establish that a different
implementation or its application integration is correct.

Use [live diagnostics](agent-self-check.md) to distinguish the standard result
from a separately labeled automatic diagnostic that ignores only declarations.
Never replace production detection with that diagnostic. For example,
`declaration-masked` exits 1 even when `automatic_result` correctly matches; an
unknown non-empty declaration returning `(null, declared)` is specified behavior.

Read only documented names or evidence-backed candidates. Record whether each is
absent, empty, non-empty, or equal to a fixed public discriminator. Do not dump or
retain the real environment, marker values, private paths, tokens or runtime IDs.
Canonical product IDs and evidence categories can be reported.

## 2. Build a controlled reproduction and classify the cause

Create the smallest synthetic mapping that preserves the relevant conditions.
Replace private non-empty values with synthetic strings; preserve empty/missing
states, public exact discriminators, AND groups and competing markers. Reproduce
PATH structure with synthetic paths. Supply synthetic name-lookup, filesystem,
TTY and PATH-separator inputs as needed, with missing capabilities unavailable.
Never merge the host environment into a fixture.

Evaluate **that same mapping and optional inputs** through the target detector
and the pinned specification. Compare both result fields. Keep existing fixture
expectations intact when checking an implementation against its current contract.

| Finding | Repair and write target |
| --- | --- |
| Target output differs from the pinned contract | Fix the implementation, input adapter or fixture adapter in the target project. Check declaration normalization, missing/empty handling, exact comparisons, AND/OR, provider name semantics and priority. Add the failing regression there. |
| Target follows an older specification | Resolve and review a newer source SHA. Update the target's complete implementation and fixtures to that chosen revision using [Implement detection](implement-detection.md). Keep rule refresh at development time. |
| Detector result is correct, but the caller displays or interprets it incorrectly | Fix the application integration/UI. Preserve `evidence`; derive `is_agent` only from `declared` or `runtime-marker`. A context hint must not be displayed as confirmed execution, and `none` must not be displayed as proof of a human caller. |
| A declaration masks the expected runtime marker | Preserve declaration precedence and report both results. Correcting the launcher's declaration is an explicit launcher/operator decision. Do not silently skip declarations, change global shell settings, or export markers merely to pass a check. |
| Another runtime rule wins because markers coexist | Compare complete predicates and documented order. Add a coexistence reproduction. If the result follows the contract, report the inherited-context limitation; do not reorder rules or discard markers to force the claimed identity. Investigate an evidence-backed discriminator if one is needed. |
| Result follows the contract, but a rule is demonstrably wrong or missing | Gather producer/observation evidence and propose a change in an independent Detect Agent checkout using [Contribute your signals](contribute-agent.md). A target-project implementation task does not silently authorize switching the write target to upstream. |
| Product has only a context hint, declaration coverage, or no rule for this interface | Report the supported boundary. Without new evidence, this can be the correct outcome. Do not invent a runtime marker, promote hints or claim a declaration proves automatic recognition. |

If the expected identity or source evidence cannot be established, report what is
missing and keep the outcome unverified. A supported coverage limit can be the
final diagnosis without manufacturing a code change.

## 3. Repair the responsible layer

**Target implementation or integration:** follow the target project's instructions.
Add a regression for the reported failure before changing the affected code,
confirm that it fails on the old behavior, then repair that behavior. Run the
shared fixtures through the actual target implementation, plus the relevant
application/UI integration checks. Do not change upstream expectations to make
incorrect code pass or hard-code your own product ID.

For example, `{"CURSOR_AGENT": "synthetic", "SAND_MANIFEST_V2": "synthetic"}`
must not select Grok Bot: the complete cloud conjunction is missing its third
condition. If the target returns `grok-bot` while the pinned specification returns
`cursor-cli / runtime-marker`, fix the target's conjunction handling and keep a
partial-conjunction regression.

**Upstream rule:** follow the contribution workflow for evidence, matching
semantics, scope and precedence. Update `detect-agent.md` first, add synthetic
regressions, synchronize the contract version/fixtures/changelog when behavior
changes, and verify the repository checks. Submit through a feature branch and
PR; never merge into `main`. An open upstream PR is not an accepted or deployed
fix. Record the exact source revision selected for any downstream update.
Track proposed, accepted and downstream-adopted states separately. If the user's
task ends with a verified proposal, deliver that proposal and report adoption or
live verification outside the authorized task as pending.

**Launcher declaration:** show the concrete declaration problem and proposed
correction to the responsible operator. If changing launcher configuration is
within the user's authorized task, make only that scoped change; otherwise
report the required correction without modifying the environment. Start a fresh
command through the affected tool and verify both standard and automatic results.
Do not treat an injected declaration as a repair of automatic marker coverage.

## 4. Verify and report the outcome

For an implementation repair, require the new regression, all selected-version
shared fixtures, and relevant integration checks to pass on the repaired target.
For a rule repair, run both repository commands:

```sh
python3 scripts/check.py conformance
python3 -m unittest discover -s tests -v
```

Repeat the original live reproduction in the same command scope when available.
Report a live fix only if that path was actually retested. Otherwise distinguish
the passing synthetic repair from the still-unverified live outcome.

Deliver:

- Expected identity/scope and before/after `(agent_id, evidence)` pairs.
- Diagnosed cause and whether the repair belongs to the target implementation,
  application integration, launcher, or upstream rule.
- Source commit/specification version, changed files, and patch/PR reference.
- Failing regression before the repair, actual verification commands and results,
  and any separately labeled live recheck.
- Remaining coverage limits or blocked steps; for a supported boundary, explain
  why no code change is warranted.

Do not call a mismatch repaired merely because a declaration was added, an
expected test result was changed, the reference checker passed, or a PR was opened.
