# Diagnose one command environment

This is a supporting diagnostic for [contributing your product's signals](contribute-agent.md).
It checks whether **the process launched by your command tool** can be recognized.
For the separate task of building a detector in a project, follow
[Implement detection](implement-detection.md).

Read [the specification](../detect-agent.md) for the matching contract. The
optional development checker uses Python 3.9+ and the standard library, with no
installation or network access. It reads the specification from its checkout;
use the pinned checkout chosen for your task rather than mixing revisions.

## 1. Establish the expected identity

Choose a canonical product ID from the specification's runtime, context, or
declaration-only tables. Base that choice on the product or launcher running you,
not the language model serving your responses. For example, the ID for Codex is
`codex`. Do not choose an expected ID by copying the detector's own result.

Record the product version if known and the execution scope: CLI child shell,
editor command tool, desktop host, remote container, plugin hook, or another
specific interface. Different interfaces of the same product may expose
different markers. If you cannot establish the expected identity, run the
diagnostic without `--expect` and report an observation without claiming success.
If the product has no catalog entry, use that observation as the starting point
for an evidence-backed contribution; do not substitute a similar product's ID.

## 2. Check conformance with synthetic inputs

From the repository root:

```sh
python3 scripts/check.py conformance
```

This loads the rules from `detect-agent.md` and evaluates
[`conformance/cases.json`](../conformance/cases.json) using controlled mappings
and simulated capabilities. It checks the repository's rule interpretation and
fixtures. It does **not** prove your live process is detectable, or test a
different detector installed in a consuming project.

For a consuming implementation, run these same fixtures through that
implementation and compare both `agent_id` and `evidence`. Preserve the optional
name-casing adapter, PATH separator, filesystem and TTY inputs. Missing optional
capabilities mean unavailable; do not fill them in from the test machine.

## 3. Check the actual command process

Run this through the same command tool whose environment you want to test,
replacing `codex` with your independently chosen canonical ID:

```sh
python3 scripts/check.py self-check --expect codex
```

Do not export `AI_AGENT`, `AGENT`, or a marker to make this command pass. Use the
existing tool environment. Running it in a separate human terminal only tests
that terminal; a local success does not establish remote/container coverage.

The JSON report includes the specification version, expected identity, standard
`result`, and `automatic_result`. The standard result follows the specification,
including declaration precedence. The automatic result is a diagnostic
counterfactual that ignores only `AI_AGENT` and `AGENT` in a local lookup provider;
it does not change your shell, process environment, or the detection contract.
It reveals runtime markers hidden by a declaration. The report contains catalog
IDs, evidence categories and diagnostic status; environment values are never included.

With `--expect`, exit code **0** means both results recognize the expected ID
using `runtime-marker` evidence. Exit code **1** means this full condition was not
met. For `declaration-masked`, `automatic_result` does match the expected ID with
`runtime-marker` evidence, but a declaration masks the standard `result`. Automatic
recognition is present in that diagnostic; exit code 1 does not mean the marker
is absent. Invalid input or specification syntax uses exit code **2**; the
conformance command also rejects invalid fixture files. Without `--expect`, a
valid diagnostic exits 0 as an observation, regardless of whether it found an agent.

Interpret results using this decision path:

| Observation | Meaning and next action |
| --- | --- |
| Both results match the expected ID with `runtime-marker` | Automatic recognition works for this process and scope. It remains an environment heuristic, not caller authentication. |
| Standard result has `declared` evidence | Only the declaration path was selected. Check the automatic result separately. Even an unknown non-empty declaration blocks fallback. |
| Expected ID appears only as `context-hint` | An editor, workspace, installation or configuration was recognized. Active agent execution was not established. |
| A different runtime ID wins | Review the ordered rules and inherited host markers. Do not infer nested-agent ancestry or reorder rules just to pass this check. |
| `(null, none)` | No supported evidence was found in this scope. This does not prove human execution. Investigate coverage. |

Declaration-only and context-only products are intentionally limited by the
current contract. A deliberate declaration can identify a known product, but
does not add automatic marker coverage. Do not promote hints or invent a marker
to turn a diagnostic into a pass.

If Python is unavailable, implement the specification in an available language,
run the synthetic fixtures first, then perform the same two local lookups: the
standard detection and a separately labeled diagnostic omitting declarations.
Read only listed names, preserve provider semantics, and never print values.
If no command execution is available, report that live detection is unverified.

## Choose the next task

Use [Implement detection](implement-detection.md) to update a detector in the
user's project. Use [Contribute your signals](contribute-agent.md) to investigate
a missing rule or propose an evidence-backed specification change. A declaration masking the result is a launcher/operator decision;
report both results and preserve production declaration precedence.

## Report template

Copy only safe results into your report or pull request:

```text
Expected product / canonical ID:
Product version (or unknown):
Execution scope / platform:
Specification version / Git commit:
Conformance command and outcome:
Standard result (agent_id, evidence):
Automatic result, ignoring declarations (agent_id, evidence):
Self-check status / exit code:
Evidence type / public reference / observation date:
Coverage limits and next action:
```

Keep a live observation separate from synthetic test results. Report only what
was actually checked; do not claim recognition across all product interfaces.
