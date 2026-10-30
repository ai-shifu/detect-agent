# Detect Agent

A shared specification that agents can implement and maintain. It describes how
to recognize AI agent execution environments using local signals.

## Supported agents

The specification covers **35 product IDs**:

| Recognition | Agents |
| --- | --- |
| Runtime markers (28) | Antigravity, Augment CLI, Claude Code, Claude Cowork, Cline, Codex, Crush, Cue, Cursor CLI, Doubao Work, Gemini CLI, Goose, Grok Bot, Grok Build, Hermes Agent, Junie, Kilo Code, Kimi Code, Kiro, Manus, Muse, OpenClaw, opencode, Pi, QwenWork, TRAE, VT Code, WorkBuddy |
| Context hints (5) | Cursor (editor), Devin, GitHub Copilot, Replit, Zed |
| Explicit declaration only (2) | hi, SandBase Harness |

Coverage and matching conditions are defined in [the specification](detect-agent.md).
Context hints describe an editor or workspace environment; they do not confirm
active agent execution. Every listed product can also be explicitly declared.

Choose one of the two tasks below and **paste its prompt into your agent**. The
agent follows the linked workflow, reads the rules, does the work, and verifies
the result. You do not need to study the rule tables or choose an SDK.

[中文说明](README.zh-CN.md)

## 1. Let an agent implement detection in your project

Use this in the project that needs detection. Your agent implements the
specification in **your project's language and conventions** and tests that
implementation against the shared cases.

```text
Implement agent-environment detection in my current project.
Read https://github.com/ai-shifu/detect-agent and follow docs/implement-detection.md
from a single pinned commit. Read the full specification and conformance cases
at that same commit. Use this project's language and conventions, integrate the
detector, and run all shared cases through the implementation you add here.
Keep environment values private, add no runtime network dependency, and report
the source commit, changed files, actual test results and any coverage limits.
```

The result is working code and tests in your project, with a recorded source
version. [Agent workflow →](docs/implement-detection.md)

## 2. Let an agent contribute its own recognition signals

Use this inside the agent product whose recognition you want to improve. It
checks existing coverage, investigates real signals, and proposes a change to
**this repository** when the evidence supports one.

```text
Help Detect Agent recognize the agent product running this task.
Read https://github.com/ai-shifu/detect-agent and follow docs/contribute-agent.md
from a single pinned commit. Use your actual command environment to check the
existing rule, and gather evidence for any missing or incorrect signals.
If a rule needs changing, prepare and verify a minimal change in a separate
checkout of that repository and open a pull request. Otherwise report the
verified result and coverage limits. Keep environment values private and leave
main unmerged.
```

The result is a verified coverage report or an evidence-backed PR. Recognition
that already works does not need a new rule. [Agent workflow →](docs/contribute-agent.md)

## How it works

[Specification 0.1.5](detect-agent.md) covers **35 canonical product IDs**. It
defines declarations, ordered runtime rules, context hints and exact matching
semantics. Detection describes environment context; it does not authenticate
the immediate caller.

The specification and [synthetic cases](conformance/cases.json) can be read with
an agent's normal tools. A consuming implementation needs no SDK or runtime
connection to this repository. Agents pin a source commit when they start, so
rules and cases stay reproducible.

[Agent entry point](AGENTS.md) · [Live diagnostics](docs/agent-self-check.md) ·
[Contribution requirements](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

Original content is [MIT licensed](LICENSE). Referenced projects retain their
own licenses and attribution.
