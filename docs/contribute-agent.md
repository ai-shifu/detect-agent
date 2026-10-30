# Contribute your product's recognition signals

Follow this workflow when the user asks you to add or correct recognition of the
agent product running the task. Your write target is **Detect Agent**, not the
user's business project or the vendor's launcher. If the user wants detection code
in their project, follow [Implement detection](implement-detection.md) instead.

Successful outcomes are either a verified report that existing coverage is
sufficient, or an evidence-backed specification change with tests and a PR.
Do not manufacture a rule change when the current rule already works.

## 1. Read one revision and establish your scope

Use `https://github.com/ai-shifu/detect-agent` as the source repository. Use the
user's supplied revision, or resolve its default branch to a Git commit SHA.
Read this workflow,
[`AGENTS.md`](../AGENTS.md), [the specification](../detect-agent.md),
[the fixtures](../conformance/cases.json) and
[the contribution requirements](../CONTRIBUTING.md) in full from that commit.
GitHub blob/raw views or a local checkout are both suitable. Record the commit
and specification version; do not combine files from moving branch snapshots.

Establish your product/launcher independently of the detector output. A model
name is not a product identity. Record product version if known, platform, and
the actual command scope: CLI child shell, editor tool, desktop host, remote
container, plugin hook, or another specific interface.

Find the existing canonical ID and its rules. If the product is absent, keep it
explicitly unregistered while investigating; do not borrow another product's ID
or pass an invented ID to the checker's `--expect` option.

## 2. Test existing coverage through your actual tool

Use an independent checkout of this repository when running its optional Python
3.9+ development tools. Follow [live diagnostics](agent-self-check.md) to run the
synthetic conformance check and a separately labeled live self-check. Launch the
checker through your actual command tool; cloning a repository by itself does
not select the product environment being tested.

For a registered product, choose `--expect` from its independently established
identity. For an unregistered product or unknown identity, omit that option and
report an observation. Never export declarations or marker variables to make a
live check pass. Python is optional: the diagnostic guide includes a manual path.

Compare the standard result and the automatic diagnostic that ignores
declarations. Use the following decision path before changing any rule:

| Result | Next action |
| --- | --- |
| Expected runtime rule matches in the supported scope | Report verified coverage; a new rule is unnecessary. |
| A declaration masks runtime markers | Report both results. The operator/launcher may deliberately correct its declaration; preserve declaration precedence. |
| Only a context hint or declaration identifies the product | Report that limited evidence. Investigate automatic coverage only if supported by new evidence. |
| Another runtime rule wins | Examine documented priority and inherited markers. Do not reorder rules just to match your claimed identity. |
| No supported rule covers this product/interface | Collect evidence for the gap in the next step. |

If this specification already has the right rule but a consuming implementation
is outdated, report that distinction and use the
[implementation workflow](implement-detection.md) when authorized to update that
project. Do not change the specification to work around a stale implementation.

## 3. Gather evidence for a concrete gap

Use published source/documentation, a permitted distribution inspection, or a
redacted runtime observation. Read the specification's evidence categories and
label your source honestly. A product website supports identity, not its marker
contract; your own assertion about being that product is not marker evidence.

Query only specific candidate names established by those sources. Record absent,
empty, non-empty, or equality with a fixed public discriminator. Do not enumerate
the environment, scan variable prefixes, or retain actual values such as paths,
IDs, tokens and addresses. Use synthetic replacements in fixtures. Do not publish
proprietary source. A local observation establishes only its recorded scope.

For each proposed rule, establish:

- Canonical ID and official product reference; distinguish a new product from
  another interface of an existing product.
- Variable names, evidence type/reference/date, product version when known,
  injection path or observed command scope, and coverage limits.
- Non-empty versus exact-value semantics, complete AND/OR grouping, and priority
  relative to inherited or compatibility markers. An observed fixed value alone
  does not justify exact matching for an ordinary runtime marker.

If you cannot establish a candidate or sufficient evidence, report the gap and
what observation or source is missing. Do not add speculative rules. A redacted,
honestly scoped observation can be contributed without claiming a vendor contract.

## 4. Make and verify the smallest supported change

Work in the Detect Agent checkout, respecting its instructions and preserving
unrelated work. Refresh the remote state, create a feature branch from current
`main`, and record the resulting source revision. If it differs from the revision
you investigated, reread changed rules and re-evaluate whether a fix is needed.

1. Update `detect-agent.md` first with the rule, evidence and coverage limits.
2. Add isolated synthetic positives and negatives to `conformance/cases.json`:
   missing/empty values, non-empty `"0"`/`"false"`/whitespace cases, wrong exact
   discriminators, partial conjunctions, declaration interactions and coexistence.
3. For a detection-contract change, update the specification version, fixture
   `spec_version`, version references in both READMEs and `CHANGELOG.md`. Evidence
   or documentation edits alone do not require a contract version bump.
4. Extend the development checker and its focused tests if a new predicate form
   is necessary. Unsupported syntax must fail explicitly; keep one rule source.
5. Run `python3 scripts/check.py conformance` and
   `python3 -m unittest discover -s tests -v`. Verify local links and unique IDs
   and case names. Repeat the live diagnostic in the affected scope if available;
   otherwise mark that part unverified. Synthetic success is not live proof.

## 5. Deliver a report or pull request

For sufficient existing coverage, report the product, source commit/specification
version, command scope, expected ID, standard and automatic results, and limits.
Avoid a no-op PR or changes made only to claim recognition.

For a change, use the [PR template](../.github/pull_request_template.md). Include
before/after behavior, evidence, scope, actual verification commands/results and
remaining gaps. Push the feature branch and open a PR to this repository when
the user's task authorizes submission. Never push directly to `main` or merge into it.

If submission credentials are unavailable, prepare the verified patch and PR
text and report the submission limitation. If execution or source access is
unavailable, report what could not be verified. Distinguish a prepared patch,
an open PR, an accepted specification update and a downstream rollout.
