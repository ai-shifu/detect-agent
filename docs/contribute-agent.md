# Contribute your product's recognition signals

Use this workflow to add or correct recognition of the product running the task.
Your **write target is Detect Agent**, in an independent checkout. For source
pinning, private values and authorization, follow
[the common rules](../AGENTS.md#common-rules). A valid result is either a verified
coverage report or an evidence-backed rule change and PR.

## Check coverage and establish a gap

1. Pin the source under the common rules. Read `AGENTS.md`, this guide,
   [the specification](../detect-agent.md), [the fixtures](../conformance/cases.json)
   and [CONTRIBUTING.md](../CONTRIBUTING.md) at the same SHA.
2. Follow [Diagnostics](diagnostics.md) to establish product identity and execution
   scope, run the relevant synthetic and live checks, and classify the result.
   It includes the no-Python and unavailable-execution paths.
3. If existing coverage is sufficient, deliver the diagnostic report and finish
   without a no-op PR. For a consuming implementation defect or stale port, use
   [Implement detection](implement-detection.md) only when that project is an
   authorized write target. Continue here for a concrete upstream rule gap.

## Gather evidence

Follow [the evidence and rule requirements](../CONTRIBUTING.md#evidence-and-rule-requirements).
Use published source/documentation, a permitted distribution inspection or an
honestly scoped redacted observation; the specification defines the evidence types.
A product website establishes identity, and your own identity claim establishes
neither a marker contract nor its injection scope.

Use this repeatable investigation sequence for any product:

1. Establish the product identity and the exact execution surface independently.
   Record what is being identified (for example, a launcher, runtime, hosted
   worker or integration) and which process, version and scope the evidence covers.
2. Trace the documented or public launcher path where possible. If it is not
   available, inspect a permitted, versioned distribution source. Prefer evidence
   that shows how a value reaches the relevant process over documentation that
   merely names a product.
3. Record only exact variable names supported by that evidence. Do not infer
   identity or injection from a variable prefix, marketing copy or a process's
   self-assertion. A name alone is not evidence of the value's semantics.
4. Separate runtime execution markers from persistent configuration or context
   hints. A runtime marker should support a claim about the current execution;
   a context hint may only support the narrower claim that configuration or
   surrounding context is present.
5. If source and distribution evidence are unavailable, a narrowly scoped,
   redacted runtime observation may support a limited heuristic. Describe the
   observed execution surface, version and date, and do not promote that
   observation into a vendor-wide guarantee.
6. State coverage limits explicitly, including versions, launch paths and
   environments not examined. Validate the proposed behavior with synthetic
   positive, negative and coexistence cases rather than using a contributor's
   live environment as a test fixture.

Establish the proposed canonical ID, source/date/version/scope, exact candidate
names, matching/grouping, precedence and known limits. Query only evidence-backed
candidates under the common privacy rules and use synthetic replacements in tests.
If evidence is insufficient, report the missing source/observation without adding
a speculative rule. A scoped observation need not claim a vendor guarantee.

## Make the supported change

Refresh the Detect Agent checkout's remote state, preserve unrelated work and
create a feature branch from current `main`. Record that base SHA. If it differs
from the investigated revision, reread the affected rules and instructions and
re-evaluate the proposed fix before editing.

Update `detect-agent.md` first, then its synthetic regressions and any required
version/changelog references, following CONTRIBUTING.md. Keep an isolated case
for the reported gap and appropriate negative/coexistence cases. Extend the
checker and focused tests only if a new predicate form needs support; keep one
normative rule source.

## Verify and deliver

Complete [the repository verification](../CONTRIBUTING.md#verification), including
its conformance and tooling-test commands. Use [Diagnostics](diagnostics.md) to
recheck the affected live path when available and record a separate live result
or the unverified limitation. Do not substitute synthetic success for a live fix.

Submit using [the PR template](../.github/pull_request_template.md) when the task
authorizes submission. Include the diagnostic report, evidence, before/after
behavior, changed files, actual verification results and remaining gaps. If
submission access is unavailable, deliver the verified patch and PR text and
state that limitation. Distinguish the verified proposal from upstream acceptance
and downstream adoption under the common reporting rules.
