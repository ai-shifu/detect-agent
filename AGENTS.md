# Agent task entry point

Detect Agent supports two tasks. Choose the one the user requested before editing.

| User's task | Follow | Write to | Deliver |
| --- | --- | --- | --- |
| Add agent detection to a project | [Implement detection](docs/implement-detection.md) | The user's target project | Integrated detector and tests against the shared fixtures |
| Contribute or correct this product's recognition signals | [Contribute your signals](docs/contribute-agent.md) | An independent checkout of Detect Agent | Verified coverage report, or a justified rule change and PR |

Both workflows use [detect-agent.md](detect-agent.md) as the only normative rule
source and [conformance/cases.json](conformance/cases.json) as shared test data.
When reading remotely, pin one Git commit and read each required file in full
from that commit. Resolve relative links within that repository and revision.

Use [live diagnostics](docs/agent-self-check.md) when investigating one command
environment. Self-check is a tool within the workflows, not a prerequisite for
implementing a detector. The Python checker is a development aid, not a production
SDK; passing it does not test an implementation in another project.

If a detection result is wrong, follow [Fix incorrect detection](docs/fix-detection.md).
Reproduce the expected/actual ID and evidence, classify the cause, repair the
responsible implementation, integration, launcher or upstream rule, and verify
the original failure. Do not stop at reporting a mismatch when a supported repair
is within the user's task.

## Working rules

- Establish which repository is the write target. Reference-repository guidance
  does not replace the target project's own development instructions.
- Read only documented variables or specific evidence-backed candidate names.
  Never dump the environment, scan prefixes, or publish marker values, credentials,
  session/message/log IDs, internal endpoints, user paths or proprietary source.
  Canonical product IDs from the specification may be included in reports.
- Keep declarations, runtime markers and context hints distinct. Passing
  synthetic cases and recognizing a live process are separate claims.
- For Detect Agent changes, follow [CONTRIBUTING.md](CONTRIBUTING.md). Change rules
  in the specification first, add synthetic regressions, and update the version
  and changelog for a detection-contract change. Do not add a second rule catalog.
- Verify Detect Agent changes with `python3 scripts/check.py conformance` and
  `python3 -m unittest discover -s tests -v`. For a consuming implementation,
  run the fixtures through that implementation in the target project's language.
- Use feature branches and pull requests for changes to this repository. Never
  merge code into `main`.
