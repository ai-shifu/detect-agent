# detect-agent.md

A Markdown specification that agents implement and maintain.

It describes how to recognize AI agent execution environments using local signals.

## Supported agents

The specification covers **40 product IDs**:

| Recognition | Agents |
| --- | --- |
| Runtime markers (35) | Antigravity, Augment CLI, Claude Code, Claude Cowork, Cline, Codex, Crush, Cue, Cursor CLI, DeepSeek Harness, Devin, Doubao Work, Gemini CLI, GitHub Copilot CLI, Goose, Grok Bot, Grok Build, Hermes Agent, Instinct, Junie, Kilo Code, Kimi Code, Kiro, Lingguang, Manus, Muse, OpenClaw, opencode, Pi, Qwen Code, QwenWork, Roo Code, TRAE, VT Code, WorkBuddy |
| Context hints (3) | Cursor (editor), Replit, Zed |
| Explicit declaration only (2) | hi, SandBase Harness |

Coverage and matching conditions are defined in [the specification](detect-agent.md).
Context hints describe an editor or workspace environment; they do not confirm
active agent execution. Every listed product can also be explicitly declared.

See [Agent descriptions](#agent-descriptions) for each product’s introduction and official source.

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
If detection is wrong, follow docs/diagnostics.md to locate and repair the cause.
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
Help detect-agent.md recognize the agent product running this task.
Read https://github.com/ai-shifu/detect-agent and follow docs/contribute-agent.md
from a single pinned commit. Use your actual command environment to check the
existing rule, and gather evidence for any missing or incorrect signals.
If detection is wrong, follow docs/diagnostics.md to locate and repair the cause.
If a rule needs changing, prepare and verify a minimal change in a separate
checkout of that repository and open a pull request. Otherwise report the
verified result and coverage limits. Keep environment values private and leave
main unmerged.
```

The result is a verified coverage report or an evidence-backed PR. Recognition
that already works does not need a new rule. [Agent workflow →](docs/contribute-agent.md)

## How it works

[Specification 0.1.11](detect-agent.md) covers **40 canonical product IDs**. It
defines declarations, ordered runtime rules, context hints and exact matching
semantics. Detection describes environment context; it does not authenticate
the immediate caller.

Known declarations can include a version suffix. Optional diagnostics retain
all runtime and context matches without exposing their values; the
[match matrix](conformance/matches.json) checks intended overlaps and foreign
matches hidden by a correct winner. Core detection does not inspect process trees.

The specification and [synthetic cases](conformance/cases.json) can be read with
an agent's normal tools. A consuming implementation needs no SDK or runtime
connection to this repository. Agents pin a source commit when they start, so
rules and cases stay reproducible.

## Agent descriptions

The descriptions below summarize the linked official product websites,
documentation, company announcements and repository READMEs, reviewed on
**2026-11-03**. Repository sources are explicitly labeled. Product positioning
does not establish a runtime marker or extend the recognition coverage defined
in the specification.

| Canonical ID | Agent | Description | Official source |
| --- | --- | --- | --- |
| `antigravity` | Antigravity | Google’s agent development platform, with app, CLI and IDE interfaces for building software with coding agents. | [Website](https://antigravity.google/) |
| `augment-cli` | Augment CLI | Augment’s Auggie coding agent for planning, executing and reviewing codebase work interactively or through terminal automation. | [Website](https://www.augmentcode.com/product/cli) |
| `claude-code` | Claude Code | Anthropic’s coding agent for building features, fixing bugs, writing tests and carrying out migrations across developer tools. | [Website](https://claude.com/product/claude-code) |
| `cowork` | Claude Cowork | Now part of Claude, Cowork works across files and tools to produce documents, spreadsheets, research and other deliverables. | [Website](https://claude.com/product/cowork) |
| `cline` | Cline | Open source coding agent runtime that plans tasks, edits projects and runs terminal commands across editors, CLI and SDK integrations. | [Website](https://cline.bot/) |
| `codex` | Codex | OpenAI’s coding agent for implementing features, debugging, refactoring and reviewing code across ChatGPT, editors, terminals and cloud environments. | [Website](https://openai.com/codex/) |
| `crush` | Crush | Terminal coding assistant connecting existing tools, code and workflows to a language model of your choice. | [Website](https://charm.land/) |
| `cue` | Cue | Desktop AI assistant using voice requests and screen context to help with everyday work, including drafting, tasks and meeting notes. | [Website](https://heycue.io/) |
| `cursor` | Cursor (editor) | AI editor and coding agent for understanding codebases, building features, fixing bugs, and reviewing changes. | [Documentation](https://cursor.com/docs) |
| `cursor-cli` | Cursor CLI | Coding agents in the terminal, with interactive use, scripts, automation and GitHub Actions integration. | [Website](https://cursor.com/cli) |
| `deepseek-harness` | DeepSeek Harness | Open source agent harness using composable plugins for everyday work, coding, research and customized agent capabilities. | [Website](https://deepseek.com/harness/) |
| `devin` | Devin | Autonomous software engineer that works in cloud or local environments, tests changes and prepares pull requests. | [Website](https://devin.ai/) |
| `doubao-work` | Doubao Work | AI work platform for individuals and teams that executes tasks and creates documents, spreadsheets, presentations and applications with Feishu integration. | [Website](https://www.feishu.cn/content/article/7677519271848610746) |
| `gemini-cli` | Gemini CLI | Terminal AI tool for querying and editing codebases, building applications, debugging, deployment and automating complex workflows. | [Website](https://geminicli.com/) |
| `github-copilot` | GitHub Copilot CLI | Terminal AI agent that answers questions, writes and debugs code, and works with GitHub issues and pull requests. | [Documentation](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-cli) |
| `goose` | Goose | Open-source AI agent that runs locally for coding, research, writing, automation and data analysis. | [Website](https://goose-docs.ai/) |
| `grok-bot` | Grok Bot | AI teammates that retain context and complete tasks across apps and websites on a persistent cloud computer. | [Documentation](https://cursor.com/docs/grok-bot) |
| `grok-build` | Grok Build | Terminal coding agent for planning, building, testing and deploying software, with skills, tools and parallel subagents. | [Website](https://x.ai/build) |
| `hermes-agent` | Hermes Agent | Open-source agent with persistent memory, automatically generated skills and integrations across messaging platforms and the command line. | [Website](https://hermes-agent.nousresearch.com/) |
| `hi` | hi | Coding agent using Pipe Network inference to read, write and edit project files and run shell commands. | [Official repository](https://github.com/PipeNetwork/hi) |
| `instinct` | Instinct | Personal assistant that understands your work and priorities, accepts texts or calls, and uses phones and computers to complete tasks. | [Website](https://instinct.com/) |
| `junie` | Junie | JetBrains coding agent that combines IDE code intelligence with terminal workflows and lets developers choose their models. | [Website](https://junie.jetbrains.com/) |
| `kilo-code` | Kilo Code | Open-source coding agent for writing, planning and debugging code across IDE, command-line and cloud workflows. | [Website](https://kilo.ai/) |
| `kimi` | Kimi Code | AI coding agent available on desktop, command line and IDE plugins for completing programming tasks. | [Website](https://www.kimi.com/code) |
| `kiro` | Kiro | AI coding agent for specification-driven development, parallel implementation and code correctness testing. | [Website](https://kiro.dev/) |
| `lingguang` | Lingguang | Ant Group’s multimodal personal AI agent that identifies needs and manages tasks over time with user authorization. | [Company announcement](https://www.antgroup.com/en/news-media/press-releases/1793066400000) |
| `manus` | Manus | General-purpose AI agent for automating workflows, conducting research and turning instructions into completed work. | [Website](https://manus.im/about) |
| `muse` | Muse | Meta’s personal AI agent that handles tasks and projects across everyday apps and turns long-term goals into action plans. | [Company announcement](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/) |
| `openclaw` | OpenClaw | Open-source AI assistant that runs on your machine and carries out tasks through the chat apps you already use. | [Website](https://openclaw.ai/) |
| `opencode` | opencode | Open-source coding agent for writing and running code from a terminal, IDE extension, or desktop app. | [Website](https://opencode.ai/) |
| `pi` | Pi | Extensible terminal AI agent that can inspect files, run commands, edit content, and complete tasks involving multiple steps. | [Documentation](https://pi.dev/docs/latest) |
| `qwen-code` | Qwen Code | Qwen's terminal coding agent for turning ideas into code, with tools and developer workflow integrations. | [Documentation](https://qwenlm.github.io/qwen-code-docs/en/users/overview/) |
| `qwenwork` | QwenWork | Alibaba's AI office platform for completing tasks and delivering documents, spreadsheets, presentations, websites, and other work products. | [Documentation](https://docs.qwenwork.cn/product-introduction) |
| `replit` | Replit | AI application platform that turns natural language ideas into apps and provides hosting, databases, authentication, and monitoring. | [Website](https://replit.com/) |
| `roo-code` | Roo Code | Open-source AI coding agent for VS Code; its official documentation notes the extension has been shut down. | [Documentation](https://roocodeinc.github.io/Roo-Code/) |
| `sandbase-harness` | SandBase Harness | AI agent runtime hosted on your infrastructure, with persistent sessions, sandboxed tools, memory, credentials, audit trails, and a management console. | [Official repository](https://github.com/sandbaseai/sandbase-harness) |
| `trae` | TRAE | AI coding environment combining an assisted IDE with an autonomous agent for planning, implementing, and delivering software. | [Website](https://www.trae.ai/blog/trae_work_0609) |
| `vtcode` | VT Code | Rust coding agent for exploring, planning, editing, and verifying repositories from a terminal or native macOS app. | [Official repository](https://github.com/vinhnx/VTCode) |
| `workbuddy` | WorkBuddy | Tencent's AI workspace that plans workflows, uses tools, and creates finished documents, spreadsheets, presentations, and other work. | [Documentation](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Product-Guide) |
| `zed` | Zed | Open-source code editor with integrated collaboration and AI tools. | [Documentation](https://zed.dev/docs/) |

## Acknowledgments

Thank you to the maintainers and contributors of these open-source projects for
sharing recognition rules, agent signals, evidence and design ideas that informed
this specification and its diagnostics:

- [Hugging Face · huggingface.js](https://github.com/huggingface/huggingface.js) — public agent harness registry.
- [Vercel · detect-agent](https://github.com/vercel/detect-agent) — shared detection rules and the `AI_AGENT` naming convention.
- [Together · detect_agent](https://github.com/togethercomputer/detect_agent) — Python port and rule-evaluation reference.
- [Expo · agent-cli-detector](https://github.com/expo/agent-cli-detector) — runtime signals and extensible detection strategies.
- [am-i-vibing](https://github.com/ascorbic/am-i-vibing) — execution-environment classification and recognition signals.
- [uarix · agent-harness-detector](https://github.com/uarix/agent-harness-detector) — investigation leads for additional desktop and hosted products.
- [ai-agent-detect](https://github.com/agent-detect/ai-agent-detect) — evidence records, all-match diagnostics and cross-detector tests.

The [specification's references](detect-agent.md#8-evidence-coverage-and-references)
record the adopted signals, reviewed snapshots and their coverage limits.

[Agent entry point](AGENTS.md) · [Diagnostics and repairs](docs/diagnostics.md) ·
[Contribution requirements](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

Original content is [MIT licensed](LICENSE). Referenced projects retain their
own licenses and attribution.
