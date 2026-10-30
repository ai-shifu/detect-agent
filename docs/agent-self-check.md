# Agent self-check and rule updates

Use this guide when you want to know whether **the process launched by your
command tool** can be recognized, or when you want to improve recognition of your
product. Read [the specification](../detect-agent.md) for the matching contract.
The repository remains a specification, not a detector SDK. Its optional checker
uses Python 3.9+ and the standard library, with no installation or network access.

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
It reveals runtime markers hidden by a declaration. Matched rule IDs and variable
names may be reported; environment values are never included.

With `--expect`, exit code **0** means both results recognize the expected ID
using `runtime-marker` evidence. Exit code **1** means automatic recognition has
not been established for that expectation. A declaration that masks an otherwise
matching marker still requires attention. Invalid input or a broken specification
or fixture file uses exit code **2**. Without `--expect`, a valid diagnostic exits
0 as an observation, regardless of whether it found an agent.

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

## 4. Decide what needs updating

1. **The consuming implementation is behind this specification.** Pin the
   specification commit, port the existing rules using that project's language
   and conventions, and run all fixtures against the updated implementation.
   Then repeat the live check through the relevant command tool. The repository
   checker passing does not validate the port.
2. **A declaration masks the intended result.** Report the standard and automatic
   results together. Let the launcher or operator deliberately correct its
   declaration; do not silently ignore it in production or alter global settings.
3. **The documented marker is missing in one interface.** Identify the affected
   product version and scope. Check the marker's published injection path or
   inspect a permitted distribution. Keep unsupported interfaces explicit.
4. **The rule itself is missing, wrong, or too broad.** Collect evidence and
   propose a specification change using the procedure below.

## 5. Investigate and propose a rule change

Read [CONTRIBUTING.md](../CONTRIBUTING.md) before editing. Use published source,
documentation, a permitted distribution inspection, or a redacted runtime
observation. A product website supports identity, not a variable contract. An
agent's assertion about its own product is not sufficient marker evidence.

For live investigation, query only specific candidate names supported by the
evidence. Record whether each is absent, empty, non-empty, or matches a fixed
public discriminator. Never run `env`, `printenv`, `set`, an environment dump, or
a prefix scan. Do not save actual marker values, including paths and IDs. Do not
paste proprietary application source. Use synthetic replacements in fixtures.

Complete the following changes on a feature branch:

1. Update `detect-agent.md` first: canonical ID and product reference, evidence
   type/date/version/scope, exact variable names, non-empty or exact semantics,
   AND/OR grouping, priority, and known coverage gaps. Ordinary runtime markers
   use non-empty checks; exact comparisons need a supported discriminator.
2. Update `conformance/cases.json`: isolated positives, missing/empty negatives,
   `"0"`/`"false"`/whitespace positives for non-empty markers, wrong discriminator
   values, partial conjunctions, declaration interaction, and coexistence with
   inherited markers. Keep case names unique and all values synthetic.
3. For a matching/priority/catalog/result change, update the specification version,
   fixture `spec_version`, version references in both READMEs, and `CHANGELOG.md`.
   Documentation and tooling changes alone do not change the detection version.
4. If a new rule form is needed, update the development checker and its focused
   tests to interpret it. The checker must reject unsupported syntax rather than
   quietly skip a rule. Do not introduce a parallel catalog of production rules.
5. Run the conformance command and
   `python3 -m unittest discover -s tests -v`. Repeat the live check if the affected
   interface is available; otherwise explicitly mark it unverified.
6. Open a pull request with the evidence, scope, before/after behavior, synthetic
   test result and separately labeled live observation. Use the
   [pull request template](../.github/pull_request_template.md). Never merge into
   `main`. A local fix or open PR is not an accepted or deployed rule update.

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
