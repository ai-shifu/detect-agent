# detect-agent.md

Version: **0.1.12** · Evidence reviewed: **2026-11-09** · License: **MIT**

## Purpose and instructions for implementing agents

Implement a small local function that identifies the AI-agent-associated environment
of the process in which it runs. This document is the specification: read it, then
implement the rules in the host project's own language and conventions. No SDK,
network request, vendor application, or dependency on this repository is required
at runtime. This is a community specification, not a vendor standard.

Implement the result contract, exact matching semantics, ordered runtime table,
and context table below. Use a caller-supplied environment mapping in tests.
Preserve the rule order. Do not replace AND with OR or infer rules from variable
prefixes. Run the inline examples and the supplementary conformance cases before
integrating the function into the host application.

The result describes a process environment, **not an authenticated immediate
caller**. A human can export these variables, and a nested agent can inherit them.
It does not identify the model, account, country, subscription, or human operator.

For task instructions, follow [Implement detection](docs/implement-detection.md)
to build a detector in the user's project, or
[Contribute your signals](docs/contribute-agent.md) to improve this specification.
Use [Diagnostics](docs/diagnostics.md) for self-checks, mismatch diagnosis and
repair routing. The optional repository tools are development aids; the rules
in this document remain normative.

## 1. Result contract

Return an object equivalent to:

```text
{
  agent_id: canonical ID or null,
  evidence: "declared" | "runtime-marker" | "context-hint" | "none"
}
```

- `declared`: the process supplied a non-empty `AI_AGENT` or `AGENT` declaration.
  An unknown declared ID returns `agent_id: null`, without falling through to
  inherited markers. Do not echo an unrecognized declaration into the result.
- `runtime-marker`: an ordered runtime rule matched. This is a heuristic, not
  proof that a model initiated the current command.
- `context-hint`: only a workspace, installation, editor, or configuration hint
  matched. Do not present this as confirmed agent execution.
- `none`: no rule matched; return `agent_id: null`. This means no evidence was
  found, not proof that a human is running the process.

If an application requires a boolean, set `is_agent` to true only for `declared`
or `runtime-marker`. Keep `agent_id` and `evidence` available to callers.

## 2. Matching semantics

The environment input is a string-to-string lookup provider; absent keys have
no value. A caller-supplied mapping is also a provider.

1. Look up only the complete variable names listed here through the supplied
   provider. **Preserve the provider's name-lookup semantics**: native Windows
   lookups are case-insensitive, while ordinary mappings and some runtime-specific
   copies can be case-sensitive. Do not enumerate or copy the full native
   environment to normalize names. A missing key and a key with an empty string
   both fail a non-empty check. Name lookup does not alter value comparisons.
2. **Non-empty** means string length greater than zero. Do not trim values:
   `"0"`, `"false"`, and `" "` all pass. Do not parse these values as booleans.
3. **Equals** means a case-sensitive, whole-string comparison. For an exact `1`
   rule, `"true"`, `"01"`, `" 1"`, and `"1\n"` all fail.
4. **OR** requires at least one complete alternative. **AND** requires all
   conditions in that parenthesized group, from the same environment snapshot.
5. Only explicit ID declarations are ASCII-trimmed and ASCII-lowercased for lookup.
   **ASCII trim** removes the longest leading and trailing runs consisting only
   of U+0009 through U+000D (tab, line feed, vertical tab, form feed, carriage
   return) and U+0020 (space). It leaves all other characters and internal
   whitespace unchanged. Do not substitute a language's default trim/strip
   operation unless it removes exactly this character set. In particular,
   non-breaking space (U+00A0) is retained: an NBSP-only declaration is non-empty
   and blocks fallback.
   **ASCII lowercase** maps each `A` through `Z` to the corresponding `a`
   through `z` and leaves every other character unchanged. This operation MUST
   be independent of the host locale; do not use a locale-sensitive lowercase
   operation or Unicode case folding as a substitute. For example, `HI` becomes
   `hi`, while dotless `hı` (U+0131) and `KIMI` (U+212A Kelvin sign) remain
   unrecognized declarations. This normalization does not apply to
   runtime-marker values.
6. Evaluate the current environment when the function is called. Do not cache
   a detection result for the process lifetime: tool-call markers can change.
7. Read only listed variables. Do not enumerate, log, transmit or persist the
   full environment or marker values. Exact rules compare only fixed public
   constants. Session IDs, paths and credentials are never result fields.

### Choosing non-empty or exact comparisons

Use **non-empty** checks for ordinary runtime markers. An observed value such as
`1` or a product-name spelling does not, by itself, establish that other values
are invalid. Do not validate ordinary marker values as paths, IDs, product names
or booleans. A defined but empty variable still fails; `"0"`, `"false"` and `" "`
pass a non-empty check.

Retain exact matching only where the value distinguishes the required context.
There are two exact runtime predicates in this version:

- `GROK_AGENT` equals `1`: the variable also selects agent definitions; the
  terminal launcher writes `1` for its execution marker. The public injection
  source establishes this distinction.
- `CURSOR_EXTENSION_HOST_ROLE` equals `agent-exec`: this predicate selects the
  agent execution role, rather than treating an arbitrary role value as agent
  execution. It follows the referenced registry's role rule; the producer's full
  set of real role values has not been independently verified.

Explicit identity declarations and content-based context hints, such as PATH and
`TERM_PROGRAM`, still require reading their contents. They are not ordinary
runtime-marker presence checks. The non-empty policy is a detection heuristic,
not a claim that a vendor interprets `"0"` or `"false"` as enabled.

## 3. Detection algorithm and priority

Every key-existence check, `environment[key]` access, and runtime/context variable
lookup below uses the same supplied provider and its name-lookup semantics.

```text
DETECT(environment, optional filesystem_probe, optional stdout_is_tty):
    for key in [AI_AGENT, AGENT], in that order:
        if key exists and ASCII_TRIM(environment[key]) is not empty:
            normalized = ASCII_LOWERCASE(ASCII_TRIM(environment[key]))
            id = resolve normalized as a full literal ID or compatibility alias
            if id is not in the canonical catalog:
                for format in the declaration format table, in order:
                    if the normalized declaration matches the entire pattern:
                        id = resolve capture 1 as a literal ID or compatibility alias
                        break
            if id is in the canonical catalog:
                return {agent_id: id, evidence: declared}
            return {agent_id: null, evidence: declared}

    for row in the runtime table, in ascending order:
        if the complete condition in that row is true:
            return {agent_id: row.id, evidence: runtime-marker}

    for row in the context table, in its listed order:
        if the complete condition is true and required probes are available:
            return {agent_id: row.id, evidence: context-hint}

    return {agent_id: null, evidence: none}
```

First match wins within each stage. A runtime marker always wins over a context
hint. Claude Cowork precedes Claude Code; Grok Bot and Grok Build precede their
Cursor or Claude compatibility markers; Cursor CLI precedes the generic Cursor
editor hint. The command-environment markers for Devin, Instinct, Lingguang,
DeepSeek Harness and Today follow the CLI markers, so a nested agent CLI's own
marker wins over these inherited command-environment markers.
Other simultaneous runtime markers use the documented table order. The order is
an implementation policy, not a claim about arbitrary nested-agent ancestry.

## 4. Runtime rules — evaluate in this exact order

These are rules for associated execution context. The evidence column explains
where the marker information came from; it is not a probability score.

| Priority | Canonical ID | Product | Match condition | Marker evidence |
| --- | --- | --- | --- | --- |
| 1 | `crush` | Crush | non-empty `CRUSH` | registry |
| 2 | `hermes-agent` | Hermes Agent | non-empty `HERMES_SESSION_ID` OR non-empty `HERMES_AGENT` | public-source / registry |
| 3 | `kilo-code` | Kilo Code | non-empty `KILOCODE_FEATURE` | registry |
| 4 | `trae` | TRAE | non-empty `TRAE_AI_SHELL_ID` | registry |
| 5 | `vtcode` | VT Code | non-empty `VTCODE` | registry |
| 6 | `workbuddy` | WorkBuddy | non-empty `WORKBUDDY_APPLICATION_NAME` OR non-empty `WORKBUDDY_APP_NAME` | static-distribution |
| 7 | `grok-bot` | Grok Bot | non-empty `SAND_AGENT` OR (non-empty `CURSOR_AGENT` AND non-empty `SAND_MANIFEST_V2` AND non-empty `SAND_SUPERVISOR_ENABLED`) | static-distribution (local); reported-shell (cloud) |
| 8 | `qwenwork` | QwenWork | non-empty `QODER_WORK_INTEGRATION_PRODUCT` | static-distribution / reported-shell |
| 9 | `cue` | Cue | non-empty `MANUS_LONG_DESKTOP_WORKER` OR non-empty `MANUS_OPERATOR_PLATFORM` | reported-shell |
| 10 | `muse` | Muse | non-empty `JARVIS_IS_ASSIGNED` OR non-empty `JARVIS_TOOL_CALL_ID` | reported-shell |
| 11 | `manus` | Manus | non-empty `MANUS_ADDON_RUNTIME_SPEC_PATH` OR non-empty `MANUS_ADDON_RUNTIME_SPECS_REVISION` | reported-shell |
| 12 | `doubao-work` | Doubao Work | non-empty `DOUBAO_OFFICE_AGENT_NAME` | reported-shell |
| 13 | `kimi` | Kimi Code | non-empty `KIMI_PLUGIN_ROOT` | public-source |
| 14 | `grok-build` | Grok Build | `GROK_AGENT` equals `1` OR non-empty `GROK_PLUGIN_ROOT` OR non-empty `GROK_PLUGIN_DATA` | public-source |
| 15 | `qwen-code` | Qwen Code | non-empty `QWEN_CODE` | public-source |
| 16 | `gemini-cli` | Gemini CLI | non-empty `GEMINI_CLI` | registry |
| 17 | `roo-code` | Roo Code | non-empty `ROO_ACTIVE` OR non-empty `ROO_CLI_RUNTIME` | public-source |
| 18 | `cline` | Cline | non-empty `CLINE_ACTIVE` OR non-empty `CLINE_WRAPPER_PATH` | public-source / registry |
| 19 | `codex` | Codex | non-empty `CODEX_SANDBOX` OR non-empty `CODEX_CI` OR non-empty `CODEX_THREAD_ID` OR non-empty `CODEX_SANDBOX_NETWORK_DISABLED` | public-source / registry |
| 20 | `antigravity` | Antigravity | non-empty `ANTIGRAVITY_AGENT` OR non-empty `ANTIGRAVITY_CLI_ALIAS` | registry |
| 21 | `augment-cli` | Augment CLI | non-empty `AUGMENT_AGENT` | registry |
| 22 | `opencode` | opencode | non-empty `OPENCODE_CLIENT` OR non-empty `OPENCODE` | registry |
| 23 | `goose` | Goose | non-empty `GOOSE_TERMINAL` | registry |
| 24 | `junie` | Junie | non-empty `JUNIE_SHIM_PATH` | public-source |
| 25 | `pi` | Pi | non-empty `PI_CODING_AGENT` | registry |
| 26 | `cowork` | Claude Cowork | non-empty `CLAUDE_CODE_IS_COWORK` AND (non-empty `CLAUDECODE` OR non-empty `CLAUDE_CODE`) | registry |
| 27 | `claude-code` | Claude Code | non-empty `CLAUDECODE` OR non-empty `CLAUDE_CODE` | registry |
| 28 | `cursor-cli` | Cursor CLI | non-empty `CURSOR_AGENT` OR `CURSOR_EXTENSION_HOST_ROLE` equals `agent-exec` | registry |
| 29 | `github-copilot` | GitHub Copilot CLI | non-empty `COPILOT_CLI` OR non-empty `COPILOT_AGENT_SESSION_ID` | public-source |
| 30 | `kiro` | Kiro | non-empty `AGENT_CONTEXT_OUT` | registry |
| 31 | `openclaw` | OpenClaw | non-empty `OPENCLAW_SHELL` | registry |
| 32 | `devin` | Devin | non-empty `DEVIN_DIR` OR non-empty `DEVIN_DISABLE_HISTEXPAND` | reported-shell |
| 33 | `instinct` | Instinct | non-empty `INSTINCT_OUTER_TOOL_USE_ID` OR non-empty `INSTINCT_OUTER_TOOL_USE_STARTED_AT` OR non-empty `INSTINCT_OUTER_TOOL_USE_TIMEOUT_SECONDS` | reported-shell |
| 34 | `lingguang` | Lingguang | non-empty `EXEC_FROM` | reported-shell |
| 35 | `deepseek-harness` | DeepSeek Harness | non-empty `DSH_SHELL` | public-source / static-distribution |
| 36 | `today` | Today | non-empty `TODAY_ENV` | reported-shell (task-command sandbox) |

Important boundaries:

- WorkBuddy requires a non-empty product-name variable; its value's spelling or
  case is not validated. The inspected build's `WorkBuddy` value is evidence of
  injection, not a requirement for other builds.
- VT Code, Cue, Muse and Grok Bot's ordinary markers use non-empty checks even
  when their names resemble flags. Missing and empty values fail; non-empty
  values are not interpreted as booleans.
- QwenWork requires only non-empty `QODER_WORK_INTEGRATION_PRODUCT`; it is **not**
  restricted to `qwenworkcn`. That value was observed in an inspected build,
  but other non-empty values also match this specification.
- Doubao Work requires only non-empty `DOUBAO_OFFICE_AGENT_NAME`; do not require
  a particular agent-name value. The internal `OFFICE` namespace is retained
  even though the product's official English name is Doubao Work.
- Cue's [official product site](https://cue.im/) establishes its identity, not
  an environment-variable contract. Non-empty `MANUS_LONG_DESKTOP_WORKER` is the
  previously reported Cue marker; its observed `1` is not a matching restriction.
- Non-empty `MANUS_OPERATOR_PLATFORM` is an alternative Cue marker based on a
  redacted task-command observation on 2026-10-30. This scoped observation does
  not establish a vendor-wide injection guarantee. Match presence only; do not
  infer product identity from a `MANUS_` prefix or map other such names to Cue.
- Manus uses its two add-on runtime descriptors as alternatives. Other add-on
  and group configuration flags do not satisfy this rule.
- Grok Bot's cloud alternative requires **all three** listed conditions.
  The shared Sand flags by themselves do not identify Grok Bot.
- Grok Build is a separate product and ID. `GROK_AGENT` has selector uses,
  so its value must be exactly `1` for the terminal-marker alternative.
- Kimi's plugin marker covers plugin-hook context, not every Kimi command.
  `KIMI_CODE_HOME` is not an alternative marker.
- Junie requires non-empty `JUNIE_SHIM_PATH`, exported by the CLI launcher.
  `JUNIE_DATA` configures the data directory and can be set globally by the user;
  it is ignored for detection. Junie execution without the shim marker is not
  covered by this rule.
- Qwen Code is distinct from QwenWork. Its published shell executor injects
  `QWEN_CODE` into both ordinary and PTY child environments. Its manual `!`
  shell escape also receives the marker: it identifies associated execution
  context, not proof that a model initiated the command. Qwen Code precedes
  Gemini CLI because a fork or inherited environment can carry both markers.
- Roo Code's VS Code terminal path injects `ROO_ACTIVE`; its headless CLI sets
  `ROO_CLI_RUNTIME` process-wide. The inline execa provider does not itself set
  `ROO_ACTIVE`, so those two paths do not establish coverage of every Roo interface.
  Roo Code precedes Cline compatibility markers. Other simultaneous runtime
  markers retain table order; no ancestry is inferred.
- Cline's npm CLI wrapper sets `CLINE_WRAPPER_PATH`, which its bash executor
  propagates to child commands. This alternative covers that CLI path; it is
  not a guarantee for every editor integration. A configured API key or data
  directory alone is not a runtime marker.
- GitHub Copilot CLI documents `COPILOT_CLI` in subprocesses and
  `COPILOT_AGENT_SESSION_ID` in shell commands and MCP servers. These dedicated
  execution markers are distinct from the model, permission and token settings
  in the context table. The rule identifies the CLI-associated environment, not
  every GitHub Copilot product or execution surface.
- Claude Cowork requires both its specific marker and a Claude Code marker here.
  This is more restrictive than registries that check the Claude Cowork flag alone.
- Devin's [official product site](https://devin.ai/) establishes its identity, not
  an environment-variable contract. Non-empty `DEVIN_DIR` or
  `DEVIN_DISABLE_HISTEXPAND` is based on a redacted observation of Devin's agent
  command tool on a Linux cloud VM on 2026-10-31. The tool's non-interactive bash
  startup file assigns `DEVIN_DIR`; `DEVIN_DISABLE_HISTEXPAND` arrives in the
  command process environment. Neither name was present in a fresh login shell,
  the global shell profiles or the inspected service process environments. This
  scoped observation does not establish a vendor-wide injection guarantee or
  cover Outposts, Windows or macOS machines, or human terminals on the VM. Match
  presence only; do not infer identity from a `DEVIN_` prefix. The `/opt/.devin`
  file probe remains a context hint.
- Instinct's [official product site](https://instinct.com/) establishes its
  identity, not an environment-variable contract. Non-empty
  `INSTINCT_OUTER_TOOL_USE_ID`, `INSTINCT_OUTER_TOOL_USE_STARTED_AT` or
  `INSTINCT_OUTER_TOOL_USE_TIMEOUT_SECONDS` is based on a redacted observation
  of Instinct's agent command execution environments (Linux cloud sandboxes) on
  2026-10-31: all three names arrived non-empty in the observed command process
  environments and were checked by name only, never by value. This scoped
  observation does not establish a vendor-wide injection guarantee or cover
  other interfaces, operating systems or human terminals. Match presence only;
  do not infer identity from an `INSTINCT_` prefix.
- Lingguang's [official product site](https://www.lingguang.com/) establishes its
  identity, not an environment-variable contract. Non-empty `EXEC_FROM` is based
  on a redacted observation of Lingguang's agent command execution environments
  (Linux cloud sandboxes) on 2026-10-31: the name arrived non-empty in the
  observed command process environments and was checked by name only, never by
  value. It was absent from a fresh login shell and from the inspected global
  shell profiles. This scoped observation does not establish a vendor-wide
  injection guarantee or cover other interfaces, operating systems or human
  terminals. Match presence only; do not infer identity from an `EXEC_` prefix.
- DeepSeek Harness's [published shell environment](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/shell/shell-env/README.md)
  states that every model shell call receives `DSH_HOME` and `DSH_SHELL=1`, and
  that agent calls also receive `DSH_SESSION_ID`. Its [source](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/shell/shell-env/src/index.ts)
  collects those values per execution; the shell executor discards inherited
  `DSH_*` names and merges the fresh snapshot into the spawned command
  environment. The inspected macOS build (0.2.1-rc.5) and a live command through
  that build's shell tool on 2026-11-02 showed the names non-empty, while a
  fresh login shell and the inspected shell profiles had none. Only the
  always-present `DSH_SHELL` sentinel is matched: `DSH_SESSION_ID` is emitted for
  agent calls but always alongside it, `DSH_HOME` is the harness-home
  configuration name, `DSH_PROFILE`/`DSH_PROFILE_DIR` are launch context, and
  plugin-registered facts (for example `DSH_DEPLOYMENT_REGION`) are not
  asserted. The rule follows the CLI markers because a nested agent CLI
  inherits these names from the harness shell. The harness rebuilds the markers
  per execution. This does not cover human terminals, cloud workers, non-desktop
  builds or other harness interfaces. Match only the named sentinel and ignore
  other `DSH_` names.
- Today's rule is based on a redacted task-command sandbox observation on
  2026-11-09 that recorded only the non-empty status of `TODAY_ENV`. The
  observation is limited to that sandbox and does not establish a vendor-wide
  injection guarantee or coverage across other versions and launch paths.
  Match only non-empty `TODAY_ENV`. Ignore `TODAY_SKILL_DIR` and other
  `TODAY_` configuration variables.

## 5. Context hints — only after all runtime rules fail

These hints are useful for diagnostics and UI context. They must not be upgraded
to `runtime-marker` solely to report more detected agents.

| Order | Canonical ID | Match condition and meaning |
| --- | --- | --- |
| 1 | `pi` | A PATH entry contains consecutive path components `.pi` and `agent`. Normalize backslashes to forward slashes and compare components case-sensitively; `.pi/agents` does not match. Split PATH using the target platform's path-list separator. This describes an installation/search path. |
| 2 | `kiro` | `TERM_PROGRAM` contains the case-sensitive substring `kiro` AND the caller explicitly supplies `stdout_is_tty = false`. Missing TTY information does not satisfy this condition. |
| 3 | `goose` | non-empty `GOOSE_PROVIDER`. This may be persistent provider configuration. |
| 4 | `github-copilot` | non-empty `COPILOT_MODEL` OR non-empty `COPILOT_ALLOW_ALL` OR non-empty `COPILOT_GITHUB_TOKEN`. Model, permission and credential configuration alone does not establish an active agent. |
| 5 | `replit` | non-empty `REPL_ID`. This identifies a Replit workspace. |
| 6 | `devin` | The caller-provided filesystem probe reports that `/opt/.devin` exists. Skip this hint if no probe is supplied or if access is unavailable. Do not run a subprocess to check it. |
| 7 | `cursor` | non-empty `CURSOR_TRACE_ID`. This can be inherited from an editor terminal. |
| 8 | `zed` | non-empty `ZED_TERM`. This can identify a human-operated editor terminal. |

This specification deliberately treats several broad upstream heuristics as
context hints. In particular, a Copilot token, Goose provider setting, PATH entry,
Replit workspace, or editor terminal may exist without an active agent. This is
not a bit-for-bit reproduction of any one upstream library.

## 6. Canonical IDs and declaration-only products

The runtime and context tables together define 39 unique canonical IDs.
Also recognize the following two IDs **only when explicitly declared**:

| Canonical ID | Product | Reference |
| --- | --- | --- |
| `hi` | hi | [Official repository](https://github.com/PipeNetwork/hi) |
| `sandbase-harness` | SandBase Harness | [Official repository](https://github.com/sandbaseai/sandbase-harness) |

No automatic marker is asserted for those two products in this version.
The complete catalog therefore has **41 IDs**. Explicit declaration also works
for every product in the runtime and context tables.

### Product metadata

Product metadata reviewed: **2026-11-03**

The table below is the source for product names, descriptions and official
sources, keyed by the same canonical IDs as the detection rules. Descriptions
prefer the official product repository's GitHub About text when it is non-empty.
Verify that the repository represents this product, rather than a namesake, SDK
or related project. Otherwise use official product websites, documentation,
company announcements or explicitly labeled official repository READMEs. Keep
concise source wording or summarize it faithfully, and translate the other
language from the same source. Product positioning does not establish a runtime
marker or extend recognition coverage.
Codex uses its official product page to cover its ChatGPT, editor, terminal and
cloud interfaces.
Every canonical ID must have exactly one metadata row, with both descriptions
and an official source. The table does not introduce additional canonical IDs.

| Canonical ID | Product | Description (en) | Description (zh-CN) | Official source |
| --- | --- | --- | --- | --- |
| `antigravity` | Antigravity | Google’s agent development platform, with app, CLI and IDE interfaces for building software with coding agents. | Google 的 Agent 开发平台，通过应用、命令行和 IDE 支持与编程 Agent 协作开发软件。 | [Website](https://antigravity.google/) |
| `augment-cli` | Augment CLI | An AI agent that brings Augment Code's power to the terminal. | 将 Augment Code 的能力带入终端的 AI Agent。 | [GitHub About](https://github.com/augmentcode/auggie) |
| `claude-code` | Claude Code | Terminal coding agent that understands codebases, executes routine tasks, explains complex code and handles Git workflows through natural language. | 在终端中理解代码库、执行日常任务、解释复杂代码，并通过自然语言处理 Git 工作流的编程 Agent。 | [GitHub About](https://github.com/anthropics/claude-code) |
| `cline` | Cline | Autonomous coding agent as an SDK, IDE extension, or CLI assistant. | 可作为 SDK、IDE 扩展或命令行助手使用的自主编程 Agent。 | [GitHub About](https://github.com/cline/cline) |
| `codex` | Codex | OpenAI’s coding agent for engineering tasks, parallel agent workflows and code review across ChatGPT, editors, terminals and the cloud. | OpenAI 的编程 Agent，可在 ChatGPT、编辑器、终端和云端处理工程任务，并支持多 Agent 并行协作及代码审查。 | [Website](https://openai.com/codex/) |
| `cowork` | Claude Cowork | Now part of Claude, Cowork works across files and tools to produce documents, spreadsheets, research and other deliverables. | 现已融入 Claude，可跨文件和工具完成工作，交付文档、表格、研究等成果。 | [Website](https://claude.com/product/cowork) |
| `crush` | Crush | Glamourous agentic coding for all 💘 | 面向所有人的精彩 Agent 编程体验。 | [GitHub About](https://github.com/charmbracelet/crush) |
| `cue` | Cue | Manus’s personal agent app, where agents have their own identities, tools and permissions and can collaborate on tasks. | Manus 的个人 Agent 应用，每个 Agent 都有自己的身份、工具与权限，并可协作完成任务。 | [Website](https://cue.im/) |
| `cursor` | Cursor (editor) | AI editor and coding agent for understanding codebases, building features, fixing bugs, and reviewing changes. | AI 编辑器与编程 Agent，可理解代码库、开发功能、修复问题和审查改动。 | [Documentation](https://cursor.com/docs) |
| `cursor-cli` | Cursor CLI | Coding agents in the terminal, with interactive use, scripts, automation and GitHub Actions integration. | 在终端中使用编程 Agent，支持交互操作、脚本、自动化及 GitHub Actions 集成。 | [Website](https://cursor.com/cli) |
| `deepseek-harness` | DeepSeek Harness | DeepSeek Harness: Everything is a Plugin. | DeepSeek Harness：一切皆插件。 | [GitHub About](https://github.com/deepseek-ai/deepseek-harness) |
| `devin` | Devin | Autonomous software engineer that works in cloud or local environments, tests changes and prepares pull requests. | 自主软件工程师，可在云端或本地环境工作、测试改动并准备拉取请求。 | [Website](https://devin.ai/) |
| `doubao-work` | Doubao Work | AI work platform for individuals and teams that executes tasks and creates documents, spreadsheets, presentations and applications with Feishu integration. | 面向个人和团队的智能体工作平台，可执行任务、生成文档、表格、演示与应用，并接入飞书协作。 | [Website](https://www.feishu.cn/content/article/7677519271848610746) |
| `gemini-cli` | Gemini CLI | An open-source AI agent that brings the power of Gemini directly into your terminal. | 将 Gemini 能力直接带入终端的开源 AI Agent。 | [GitHub About](https://github.com/google-gemini/gemini-cli) |
| `github-copilot` | GitHub Copilot CLI | GitHub Copilot CLI brings the power of Copilot coding agent directly to your terminal. | 将 Copilot 编程 Agent 的能力直接带入终端。 | [GitHub About](https://github.com/github/copilot-cli) |
| `goose` | Goose | an open source, extensible AI agent that goes beyond code suggestions - install, execute, edit, and test with any LLM | 开源、可扩展的 AI Agent，不仅提供代码建议，还能使用任意大语言模型安装、执行、编辑和测试。 | [GitHub About](https://github.com/aaif-goose/goose) |
| `grok-bot` | Grok Bot | AI teammates that retain context and complete tasks across apps and websites on a persistent cloud computer. | 保留上下文、在持久云电脑上跨应用和网站完成任务的 AI 队友。 | [Documentation](https://cursor.com/docs/grok-bot) |
| `grok-build` | Grok Build | SpaceXAI's coding agent harness and TUI. Fullscreen, mouse interactive, extensible. | SpaceXAI 的编程 Agent harness 与终端界面，全屏显示，支持鼠标交互和扩展。 | [GitHub About](https://github.com/xai-org/grok-build) |
| `hermes-agent` | Hermes Agent | The agent that grows with you | 与你共同成长的 Agent。 | [GitHub About](https://github.com/NousResearch/hermes-agent) |
| `hi` | hi | Coding agent using Pipe Network inference to read, write and edit project files and run shell commands. | 使用 Pipe Network 推理服务的编程 Agent，可读写和编辑项目文件并运行 Shell 命令。 | [Official repository](https://github.com/PipeNetwork/hi) |
| `instinct` | Instinct | Personal assistant that understands your work and priorities, accepts texts or calls, and uses phones and computers to complete tasks. | 理解你的工作和关注事项，可通过短信或电话交流，并操作手机和电脑完成任务的个人助手。 | [Website](https://instinct.com/) |
| `junie` | Junie | An AI coding agent by JetBrains that ships code from your terminal, IDE, or CI/CD pipeline - powered by any LLM you choose | JetBrains 的 AI 编程 Agent，可从终端、IDE 或 CI/CD 流水线交付代码，并支持选择任意大语言模型。 | [GitHub About](https://github.com/JetBrains/junie) |
| `kilo-code` | Kilo Code | Kilo is the all-in-one agentic engineering platform. Build, ship, and iterate faster with the most popular open source coding agent. | 一体化智能体工程平台，通过开源编程 Agent 更快地构建、交付和迭代。 | [GitHub About](https://github.com/Kilo-Org/kilocode) |
| `kimi` | Kimi Code | Kimi Code CLI  —  The Starting Point for Next-Gen Agents | Kimi Code CLI：下一代 Agent 的起点。 | [GitHub About](https://github.com/MoonshotAI/kimi-code) |
| `kiro` | Kiro | Kiro is an agentic IDE that works alongside you from prototype to production. | 从原型到生产始终与你协作的智能体 IDE。 | [GitHub About](https://github.com/kirodotdev/Kiro) |
| `lingguang` | Lingguang | Ant Group’s multimodal personal AI agent that identifies needs and manages tasks over time with user authorization. | 蚂蚁集团的多模态个人 AI Agent，在用户授权下识别需求并持续管理任务。 | [Company announcement](https://www.antgroup.com/en/news-media/press-releases/1793066400000) |
| `manus` | Manus | General-purpose AI agent for automating workflows, conducting research and turning instructions into completed work. | 可自动执行工作流、开展研究，并将指令转化为实际成果的通用 AI Agent。 | [Website](https://manus.im/about) |
| `muse` | Muse | Meta’s personal AI agent that handles tasks and projects across everyday apps and turns long-term goals into action plans. | Meta 的个人 AI Agent，可跨日常应用处理任务和项目，并将长期目标转化为行动计划。 | [Company announcement](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/) |
| `openclaw` | OpenClaw | The AI that really does things. Any OS. Any Platform. The lobster way. 🦞 | 真正能办事的 AI。支持各种操作系统与平台，走龙虾自己的路。🦞 | [GitHub About](https://github.com/openclaw/openclaw) |
| `opencode` | opencode | The open source coding agent. | 开源编程 Agent。 | [GitHub About](https://github.com/anomalyco/opencode) |
| `pi` | Pi | AI agent toolkit: unified LLM API, agent loop, TUI, coding agent CLI | AI Agent 工具包，包含统一的大模型 API、Agent 循环、终端界面和编程 Agent 命令行。 | [GitHub About](https://github.com/earendil-works/pi) |
| `qwen-code` | Qwen Code | An open-source AI coding agent that lives in your terminal. | 在终端中运行的开源 AI 编程 Agent。 | [GitHub About](https://github.com/QwenLM/qwen-code) |
| `qwenwork` | QwenWork | Alibaba's AI office platform for completing tasks and delivering documents, spreadsheets, presentations, websites, and other work products. | 阿里巴巴推出的一站式 AI 办公平台，可执行复杂任务并交付文档、表格、PPT、网页等成果。 | [Documentation](https://docs.qwenwork.cn/product-introduction) |
| `replit` | Replit | AI application platform that turns natural language ideas into apps and provides hosting, databases, authentication, and monitoring. | 将自然语言想法变为应用的 AI 平台，并提供托管、数据库、身份认证和监控。 | [Website](https://replit.com/) |
| `roo-code` | Roo Code | Roo Code gives you a whole dev team of AI agents in your code editor. | 在代码编辑器中为你提供一整支 AI Agent 开发团队。 | [GitHub About](https://github.com/RooCodeInc/Roo-Code) |
| `sandbase-harness` | SandBase Harness | Local-first, self-hosted AI agent runtime and MCP bridge with sandboxed sessions, memory, credentials, audit/replay, and a local Console. | 以本地为先、可自行托管的 AI Agent 运行时与 MCP 桥接，提供沙箱会话、记忆、凭据、审计回放和本地控制台。 | [GitHub About](https://github.com/sandbaseai/sandbase-harness) |
| `today` | Today | AI personal assistant with long-term memory that plans, remembers, and helps manage work and life across channels. | 具备长期记忆的 AI 个人助手，可规划、记忆并帮助管理跨渠道的工作与生活。 | [Website](https://today.ai) |
| `trae` | TRAE | AI coding environment combining an assisted IDE with an autonomous agent for planning, implementing, and delivering software. | 融合 AI 辅助 IDE 与自主编程 Agent 的开发环境，可规划、实现并交付软件。 | [Website](https://www.trae.ai/blog/trae_work_0609) |
| `vtcode` | VT Code | VT Code is an open-source Rust terminal coding agent. | VT Code 是使用 Rust 开发的开源终端编程 Agent。 | [GitHub About](https://github.com/vinhnx/VTCode) |
| `workbuddy` | WorkBuddy | Tencent's AI workspace that plans workflows, uses tools, and creates finished documents, spreadsheets, presentations, and other work. | 腾讯推出的 AI 工作台，可规划流程、调用工具并交付文档、表格、演示文稿等工作成果。 | [Documentation](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Product-Guide) |
| `zed` | Zed | Code at the speed of thought – Zed is a high-performance, multiplayer code editor from the creators of Atom and Tree-sitter. | 由 Atom 和 Tree-sitter 创作者打造的高性能多人协作代码编辑器，让编程跟上思考速度。 | [GitHub About](https://github.com/zed-industries/zed) |

Applications that need product information can implement a separate local
`AGENT_INFO(canonical_id)` lookup from this table at the same pinned source
commit as their detection rules. It returns the following public metadata:

```text
{
  agent_id: canonical ID,
  name: Product column,
  descriptions: {"en": Description (en), "zh-CN": Description (zh-CN)},
  source: {type: source type, url: linked official URL},
  reviewed_at: product metadata review date in YYYY-MM-DD format
}
```

Source link labels map to types as follows: `GitHub About` to `github-about`,
`Website` to `website`,
`Documentation` to `documentation`, `Company announcement` to
`company-announcement`, and `Official repository` to `official-repository`.
The review date above applies to every row. Names and descriptions are strings;
the two description keys are language tags, with no implicit locale selection.

Look up the complete canonical ID exactly. Null, unknown IDs, declaration aliases
and versioned declaration strings return null; callers can use the canonical ID
returned by `DETECT`. Do not echo an unknown input, inspect environment variables
or fetch sources during lookup. Keep this optional metadata lookup separate from
the unchanged two-field detection result and its evidence:

```text
result = DETECT(environment)
info = AGENT_INFO(result.agent_id)
description = info.descriptions["zh-CN"] if info is not null else null
```

The optional development tools can query a single record or export all records
as JSON directly from this table:

```sh
python3 scripts/check.py agent-info --id codex
python3 scripts/check.py export-metadata
```

`agent-info` returns the record or JSON null for an unknown ID. `export-metadata`
returns `{spec_version, agents}`, with records sorted by canonical ID. Both
commands exit 0 on a successful query/export and 2 on invalid arguments or
specification errors. They read no command environment or live capabilities.
Use an export at development time to generate a local table in the target
project's language; production code needs neither Python nor runtime access to
this repository. Exports are derived data, not a separately maintained catalog.

Accept these compatibility spellings in **declarations only**:

| Alias | Canonical ID |
| --- | --- |
| `codex_cli` | `codex` |
| `claude_code` | `claude-code` |
| `gemini_cli` | `gemini-cli` |
| `open_code` | `opencode` |
| `grok` | `grok-build` |

Declaration results MUST stay identical across host locales, including Turkish.
When testing a language runtime with configurable default locales, run the same
conformance cases under each locale; the fixtures do not define a `locale` field
and changing the supplied environment alone is not a substitute for configuring
the host runtime. The [Java String documentation](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/String.html#toLowerCase())
illustrates why a default-locale lowercase operation can change ASCII `I`.

The `grok` alias records the Together/Vercel detector's historical Grok Build ID;
it does not mean that every product named Grok is Grok Build. Product names such
as Manus and Doubao Work have canonical IDs `manus` and `doubao-work`.

### Versioned declarations

After ASCII trimming and lowercasing, first resolve the **entire** declaration
as a literal ID or compatibility alias. Only if that fails, evaluate these
full-string patterns in table order. The patterns use ASCII character classes;
`+` means one or more repetitions and capture 1 is the product name. Resolve
that capture using the same catalog and alias table. Do not recursively parse
the captured name or accept an unknown product.

| Declaration format | Full-string pattern | Name capture |
| --- | --- | --- |
| name-at-version | `([a-z][a-z0-9_-]*)@([a-z0-9][a-z0-9.+-]*)` | 1 |
| claude-agent | `(claude-code)_[0-9]+-[0-9]+-[0-9]+_agent` | 1 |
| claude-harness | `(claude-code)_[0-9]+-[0-9]+-[0-9]+_harness` | 1 |

The `@` suffix is an opaque, non-empty ASCII version label, not a SemVer claim.
The Claude forms cover its three numeric version components with dots encoded
as hyphens and the two execution labels in the inspected distribution. They are not a
general underscore-splitting convention. Literal `claude_code` remains the
existing alias; `claude_code_2-1-205_agent` is not a supported spelling.
Only the canonical product ID is returned. Discard version/mode text and never
echo the declaration. Malformed formats and unknown names still return
`(null, declared)` and block all fallback, including the second declaration.

The naming convention and inspected producer scope are recorded in the evidence
references below. These are compatibility rules, not an authentication scheme.

## 7. Inline conformance examples

All values below are synthetic, except fixed product/sentinel constants.
`{}` means an empty environment mapping. A result pair is `(agent_id, evidence)`.

| Environment / extra input | Expected result |
| --- | --- |
| `{}` | `(null, none)` |
| `AI_AGENT=" codex_cli "`, `CURSOR_AGENT="1"` | `(codex, declared)` |
| `AI_AGENT="codex@1.0"`, `CLAUDECODE="1"` | `(codex, declared)` |
| `AI_AGENT="claude-code_2-1-205_agent"`, `CLAUDECODE="1"` | `(claude-code, declared)` |
| `AI_AGENT="claude_code"` | `(claude-code, declared)` |
| `AI_AGENT="unknown@1.0"`, `CODEX_THREAD_ID="synthetic-thread"` | `(null, declared)` |
| `AI_AGENT="HI"` | `(hi, declared)` |
| `AGENT="KIMI"` | `(kimi, declared)` |
| `AI_AGENT="KIMI"` (U+212A Kelvin sign) | `(null, declared)` |
| `AI_AGENT="unregistered-example"`, `CURSOR_AGENT="1"` | `(null, declared)` |
| `AI_AGENT=" "`, `AGENT="manus"` | `(manus, declared)` |
| `AI_AGENT="\t\r\nHI\v\f "` | `(hi, declared)` |
| `AI_AGENT="\u00A0"`, `AGENT="manus"`, `CURSOR_AGENT="1"` | `(null, declared)` |
| `QODER_WORK_INTEGRATION_PRODUCT="another-name"` | `(qwenwork, runtime-marker)` |
| `QODER_WORK_INTEGRATION_PRODUCT=""` | `(null, none)` |
| `DOUBAO_OFFICE_AGENT_NAME=" "` | `(doubao-work, runtime-marker)` |
| `DOUBAO_OFFICE_AGENT_NAME=""` | `(null, none)` |
| `WORKBUDDY_APPLICATION_NAME="workbuddy"` | `(workbuddy, runtime-marker)` |
| `VTCODE="0"` | `(vtcode, runtime-marker)` |
| `VTCODE=""` | `(null, none)` |
| `MANUS_LONG_DESKTOP_WORKER="false"` | `(cue, runtime-marker)` |
| `JARVIS_IS_ASSIGNED=" "` | `(muse, runtime-marker)` |
| `SAND_AGENT="0"`, `CURSOR_AGENT="1"` | `(grok-bot, runtime-marker)` |
| `CURSOR_AGENT="1"`, `SAND_MANIFEST_V2="0"`, `SAND_SUPERVISOR_ENABLED="false"` | `(grok-bot, runtime-marker)` |
| `SAND_AGENT="1"`, `CURSOR_AGENT="1"` | `(grok-bot, runtime-marker)` |
| `CURSOR_AGENT="1"`, `SAND_MANIFEST_V2="1"`, `SAND_SUPERVISOR_ENABLED="1"` | `(grok-bot, runtime-marker)` |
| `CURSOR_AGENT="1"`, `SAND_MANIFEST_V2="1"` | `(cursor-cli, runtime-marker)` |
| `SAND_MANIFEST_V2="1"`, `SAND_SUPERVISOR_ENABLED="1"` | `(null, none)` |
| `GROK_AGENT="other-selector"` | `(null, none)` |
| `GROK_AGENT=" 1"` | `(null, none)` |
| `CURSOR_EXTENSION_HOST_ROLE="agent-exec"` | `(cursor-cli, runtime-marker)` |
| `CURSOR_EXTENSION_HOST_ROLE="synthetic-other-role"` | `(null, none)` |
| `MANUS_LONG_DESKTOP_WORKER="1"` | `(cue, runtime-marker)` |
| `MANUS_ADDON_RUNTIME_SPEC_PATH="synthetic-spec"` | `(manus, runtime-marker)` |
| `JARVIS_SESSION_ID="synthetic-session"` | `(null, none)` |
| `JARVIS_TOOL_CALL_ID="synthetic-tool"` | `(muse, runtime-marker)` |
| `CLAUDE_CODE_IS_COWORK="1"`, `CLAUDECODE="1"` | `(cowork, runtime-marker)` |
| `CLAUDE_CODE_IS_COWORK="1"` | `(null, none)` |
| `DEVIN_DIR="synthetic-dir"` | `(devin, runtime-marker)` |
| `DEVIN_DIR="synthetic-dir"`, `CLAUDECODE="1"` | `(claude-code, runtime-marker)` |
| `ZED_TERM="1"` | `(zed, context-hint)` |
| `ZED_TERM="1"`, `CODEX_THREAD_ID="synthetic-thread"` | `(codex, runtime-marker)` |
| `GOOSE_PROVIDER="synthetic-provider"` | `(goose, context-hint)` |
| `TERM_PROGRAM="kiro"`, `stdout_is_tty=false` | `(kiro, context-hint)` |
| `TERM_PROGRAM="kiro"`, TTY state unavailable | `(null, none)` |
| `DSH_SHELL="1"` | `(deepseek-harness, runtime-marker)` |
| `DSH_HOME="synthetic-home"` | `(null, none)` |
| `DSH_SHELL="1"`, `CODEX_THREAD_ID="synthetic-thread"` | `(codex, runtime-marker)` |
| `QWEN_CODE="1"`, `GEMINI_CLI="1"` | `(qwen-code, runtime-marker)` |
| `ROO_CLI_RUNTIME="1"`, `CLINE_ACTIVE="1"` | `(roo-code, runtime-marker)` |
| `CLINE_WRAPPER_PATH="synthetic-wrapper"` | `(cline, runtime-marker)` |
| `COPILOT_CLI="1"`, `COPILOT_MODEL="synthetic-model"` | `(github-copilot, runtime-marker)` |

The supplementary [`conformance/cases.json`](conformance/cases.json) is portable
input/output data, not another source of rules. The optional `env_name_case`
field selects the synthetic mapping adapter: `sensitive` (the default), or
`ascii-insensitive`. The latter compares names after mapping ASCII `A` through
`Z` to `a` through `z`, leaving other characters unchanged. Fixtures in this
mode MUST NOT contain keys that collide under that transformation. It models
ASCII name casing only, not every native Windows name-equivalence rule; it does
not depend on the test host and does not change production provider semantics.

A case's absent `files` or `stdout_is_tty` field means the capability is
unavailable. An optional `path_separator` case field selects the emulated
platform's PATH-list separator, so tests do not depend on the host platform.
`files: []` means an available probe that reports no listed paths exist. Never use
the machine's actual environment, filesystem, or terminal state when running
these cases.

### Optional all-match diagnostics

The production result remains exactly the two-field result in section 1, with
declaration precedence and first-match selection unchanged. An optional diagnostic
may additionally return `matches`: every matching runtime row in table order,
followed by every matching context row in table order. Each item has only
`agent_id` and `evidence`, with evidence limited to `runtime-marker` or
`context-hint`. Include a row once even when multiple alternatives match. The
same product may appear once per evidence stage. No matches is an empty array.

This diagnostic ignores declarations without modifying the supplied environment.
It uses the same named-key snapshot, provider semantics and optional capabilities
as detection. Missing capabilities remain unavailable. Do not return marker
values, paths, session IDs or arbitrary declared names, and do not inspect a
process tree. Ordering expresses this specification's priority, not agent ancestry.
The first match, when present, is the declaration-omitting `automatic_result`.

The optional development checker exposes this list in `self-check`; core-only
consumers do not need a diagnostic API. [The match matrix](conformance/matches.json)
uses the same synthetic input fields and `spec_version` as the core fixtures,
but each case's `expected` is the complete ordered match array. It checks foreign
matches hidden by a correct winner, deliberate coexistence and unavailable probes.
The matrix must cover each runtime/context row with no unlisted foreign matches;
compound rules may necessarily match their documented compatibility row as well.
Its expectations are test data, not a second rule source.

## 8. Evidence, coverage and references

The specification separates a product's official positioning from evidence for
its internal environment variables. A product website is not a variable contract.
Reviewed source snapshots and proposed contributions are linked below; pending
contributions are not claims of upstream acceptance or deployed availability.

- **public-source**: inspected published source or documentation describes a
  particular injection path. It does not establish every shell/interface.
- **static-distribution**: independently inspected installed macOS packages:
  WorkBuddy 5.8.3, Grok Bot 0.71.2, QwenWorkCN 1.3.1, DeepSeek Harness
  0.2.1-rc.5. The propagation review was static; no vendor agent was launched.
  QwenWork's new product marker was confirmed on local/host paths, not ordinary
  VM/QXC guest shells.
- **reported-shell**: user-provided shell observations on 2026-10-16 for Cue,
  Muse, Manus, Doubao Work, and the Grok Bot cloud combination. They were not
  independently reproduced and are not public stability guarantees. Later
  redacted task-command observations cover Cue (2026-10-30), Devin's agent
  command tool on a Linux cloud VM (2026-10-31), Instinct's agent command
  environments on Linux cloud sandboxes (2026-10-31), Lingguang's agent command
  environments on Linux cloud sandboxes (2026-10-31), and Today's task-command
  sandbox (2026-11-09).
- **registry**: a rule appears in the referenced open-source detector snapshots.
  This attribution alone does not establish an official vendor contract.

### Environment provider references

- [Microsoft Environment.GetEnvironmentVariable](https://learn.microsoft.com/en-us/dotnet/api/system.environment.getenvironmentvariable?view=net-9.0#remarks)
  documents case-sensitive name lookup on Unix-like systems and case-insensitive
  name lookup on Windows.
- [Python os.environ](https://docs.python.org/3.14/library/os.html#os.environ)
  documents uppercase key conversion for its Windows environment mapping.
- [Node.js process.env](https://nodejs.org/api/process.html#processenv) documents
  case-insensitive Windows lookups in the main thread, but a case-sensitive
  environment copy in a Worker. Select semantics for the actual provider rather
  than inferring them solely from the host OS.

### Detector snapshots and attribution

This document independently states detection policies and factual marker names;
it does not vendor implementation code or copy proprietary application source.
The underlying open-source projects retain their own licenses and attribution:

- [Hugging Face agent registry](https://github.com/huggingface/huggingface.js/blob/b672b597f4960f00fac502475b3dd0d4b1422909/packages/tasks/src/agent-harnesses.ts)
  (MIT; Hugging Face), including the accompanying [evidence notes](https://github.com/huggingface/huggingface.js/blob/b672b597f4960f00fac502475b3dd0d4b1422909/packages/tasks/agent-harnesses.md).
- [Vercel detector contribution snapshot](https://github.com/vercel/detect-agent/blob/e3dd1b263646d913482c3504acae9aa91926e800/agents.json)
  (Apache-2.0), with [marker and product evidence](https://github.com/vercel/detect-agent/blob/e3dd1b263646d913482c3504acae9aa91926e800/docs/environment-marker-evidence.md).
- [Together Python port contribution snapshot](https://github.com/togethercomputer/detect_agent/blob/a804bd9a94bacd0d50bf7ee7b072374c297f3e6d/detect_agent/agents.json)
  (Apache-2.0; Together).

The Hugging Face snapshot uses simpler OR matching and does not contain the
compound Grok Bot cloud rule. This specification can express the conjunction
without requiring a change to that registry or its clients.

The linked snapshots establish variable evidence, not this specification's full
matching policy. Ordinary markers here use non-empty checks even where a source
snapshot compares a fixed sentinel or product spelling. This is a deliberate
local policy; it does not claim an upstream change or a new vendor contract.

Additional detector and design references reviewed on 2026-11-03:

- [Expo detector snapshot](https://github.com/expo/agent-cli-detector/blob/d2f8b90f539fd6e3af3c74e76cd0bd200fa8aee0/src/agents.ts)
  supplied CLI-marker candidates. Its [strategy implementation](https://github.com/expo/agent-cli-detector/blob/d2f8b90f539fd6e3af3c74e76cd0bd200fa8aee0/src/detector.ts)
  informed the separation of rules and diagnostic capabilities. Adopted CLI
  markers are supported by the producer-path references below.
- [am-i-vibing provider snapshot](https://github.com/ascorbic/am-i-vibing/blob/76104566f3cb3a399e8420e31bb14fff03ffa26d/packages/am-i-vibing/src/providers.ts)
  supplied recognition leads and execution-environment classification ideas.
  Editor or workspace context remains distinct from runtime evidence here.
- [uarix detector snapshot](https://github.com/uarix/agent-harness-detector/blob/1c0df54832c6173f07ac99113bcc5c3cb3be4daf/src/detectors.ts)
  supplied investigation leads for additional desktop and hosted products.
  Configuration, directory and credential heuristics require separate injection
  evidence before they can become runtime rules in this specification.
- [ai-agent-detect claims snapshot](https://github.com/agent-detect/ai-agent-detect/blob/771f5bb5d46db473d01eacaf370ba601d6e76881/index.js)
  and its [cross-detector test matrix](https://github.com/agent-detect/ai-agent-detect/blob/771f5bb5d46db473d01eacaf370ba601d6e76881/test/matrix.test.js)
  informed all-match diagnostics and tests for foreign matches hidden by a winner.
  This specification's diagnostics retain only canonical IDs and evidence types.

These snapshots supplied research leads and design references. The rule tables
and individual producer references define the adopted signals and their scope.
Synthetic checks are separate from live recognition; this review did not exercise
every product, interface or platform covered by the referenced projects.

### Published marker injection references

- [Qwen Code shell executor](https://github.com/QwenLM/qwen-code/blob/212fedbdc7d95562a8448d926ce4731d112a561d/packages/core/src/services/shellExecutionService.ts#L1010-L1020)
  and its [PTY path](https://github.com/QwenLM/qwen-code/blob/212fedbdc7d95562a8448d926ce4731d112a561d/packages/core/src/services/shellExecutionService.ts#L2000-L2010)
  inject `QWEN_CODE`; the [shell-tool documentation](https://github.com/QwenLM/qwen-code/blob/212fedbdc7d95562a8448d926ce4731d112a561d/docs/developers/tools/shell.md#L169-L171)
  and [manual shell escape documentation](https://github.com/QwenLM/qwen-code/blob/212fedbdc7d95562a8448d926ce4731d112a561d/docs/users/features/commands.md#L531-L537)
  establish the execution-context boundary. The official repository establishes
  the Qwen Code product identity, distinct from QwenWork.
- [Roo Code terminal environment](https://github.com/RooCodeInc/Roo-Code/blob/b867ec9145750d0ae1ff7f02d35406e9bf2a0b16/src/integrations/terminal/Terminal.ts#L153-L160)
  and [terminal creation](https://github.com/RooCodeInc/Roo-Code/blob/b867ec9145750d0ae1ff7f02d35406e9bf2a0b16/src/integrations/terminal/Terminal.ts#L15-L20)
  inject `ROO_ACTIVE`; the [headless CLI](https://github.com/RooCodeInc/Roo-Code/blob/b867ec9145750d0ae1ff7f02d35406e9bf2a0b16/apps/cli/src/agent/extension-host.ts#L175-L182)
  sets `ROO_CLI_RUNTIME`. The [inline execa provider](https://github.com/RooCodeInc/Roo-Code/blob/b867ec9145750d0ae1ff7f02d35406e9bf2a0b16/src/integrations/terminal/ExecaTerminalProcess.ts#L42-L54)
  does not independently inject the terminal marker. The official repository
  establishes the Roo Code product identity.
- [Cline CLI wrapper](https://github.com/cline/cline/blob/5b454165353ac1edc9a7db0ff416739044985908/apps/cli/bin/cline#L19-L24)
  sets `CLINE_WRAPPER_PATH` and [passes it to the CLI child](https://github.com/cline/cline/blob/5b454165353ac1edc9a7db0ff416739044985908/apps/cli/bin/cline#L68-L72);
  the [bash executor](https://github.com/cline/cline/blob/5b454165353ac1edc9a7db0ff416739044985908/sdk/packages/core/src/extensions/tools/executors/bash.ts#L733-L736)
  inherits that environment. This is evidence for the wrapper-launched CLI path.
- [GitHub Copilot CLI 1.0.29 release notes](https://github.com/github/copilot-cli/blob/e1928292498bd60d8b8730381ed3818e82453711/changelog.md#L2020-L2027)
  document `COPILOT_AGENT_SESSION_ID` in shell commands and MCP servers;
  [0.0.421 release notes](https://github.com/github/copilot-cli/blob/e1928292498bd60d8b8730381ed3818e82453711/changelog.md#L2566-L2573)
  document `COPILOT_CLI` in subprocesses. These published paths were reviewed on
  2026-11-03 without running the vendor agents; synthetic coverage is separate
  from live recognition on a particular installation.
- [Kimi plugin hooks](https://github.com/MoonshotAI/kimi-code/blob/18c6d64272952503baccf706bff455bb6a2c488e/docs/en/customization/plugins.md#L482-L486).
- [Grok Build marker definition](https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-tools/src/util/env.rs#L31-L42)
  and [terminal injection](https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-tools/src/computer/local/terminal.rs#L3315-L3323).
- [Junie launcher exports](https://github.com/JetBrains/junie/blob/cdbfbcf6a9f17951c94dd2902619dffc37f5881f/templates/junie.shim.sh#L684-L700).
- [Codex child-process injection](https://github.com/openai/codex/blob/6ae8b8aa7c608730d4315d59c5c081897ae02780/codex-rs/core/src/spawn.rs#L85-L88).
- [Hermes terminal wrapper](https://github.com/NousResearch/hermes-agent/blob/e5eb6b36fe78eb012cefd1f5f436cd458411b8b3/tools/environments/base_session_env.py#L132-L159).
- [DeepSeek Harness shell environment](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/shell/shell-env/src/index.ts)
  and its [package documentation](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/shell/shell-env/README.md);
  the [subprocess scrub](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/subprocess/subprocess/src/index.ts)
  drops inherited `DSH_*` names before the fresh snapshot is merged.

### Official product identity references

The [product metadata table](#product-metadata) provides descriptions and
official sources for every canonical ID. It is read alongside the detection
rules; marker evidence and execution coverage remain separate from descriptions.

- [Claude Cowork](https://claude.com/product/cowork).
- [WorkBuddy](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Product-Guide),
  [QwenWork](https://docs.qwenwork.cn/product-introduction),
  [Doubao Work introduction](https://www.feishu.cn/content/article/7677519271848610746)
  and [official English usage](https://www.feishu.cn/hc/en-US/articles/428390929435-admin-configure-screen-capture-protection).
- [Grok Bot](https://cursor.com/docs/grok-bot),
  [Cue](https://cue.im/) and its [Manus API association](https://open.manus.ai/docs/v2/agents-overview),
  [Muse](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/),
  [Manus](https://www.manus.im/about).
- [Devin](https://devin.ai/) and its [documentation](https://docs.devin.ai/).
- [Instinct](https://instinct.com/).
- [Today](https://today.ai), [Google Play listing](https://play.google.com/store/apps/details?id=ai.today.android.app).
- [Lingguang](https://www.lingguang.com/).

### Declaration-format references

- [Vercel's recommended naming convention](https://github.com/vercel/detect-agent/blob/3ab1df1e4eaae153cf66f4a5018e4c5854855212/README.md#L104-L108)
  recommends an `@` separator for versioned names. This is a community proposal,
  not a vendor-wide standard. This specification accepts only known IDs/aliases
  and the bounded ASCII suffix syntax in its own declaration table; it does not
  return arbitrary names or version text.
- **static-distribution**: [Anthropic's official macOS ARM64 distribution,
  version 2.1.205](https://www.npmjs.com/package/@anthropic-ai/claude-code-darwin-arm64/v/2.1.205),
  with [official version metadata](https://registry.npmjs.org/@anthropic-ai/claude-code-darwin-arm64/2.1.205),
  was statically inspected on 2026-11-03. It constructs `AI_AGENT` in the
  `claude-code_<version>_<mode>` format, replaces version dots with hyphens,
  and uses `harness` in an initialization path and `agent` in an agent-environment
  path. The inspected tarball's SHA-256 is
  `2491465de769953037bb8fd315aafecbe3607325b1fb07efbae4ca7bd5540b28`.
  No package or vendor agent was executed. This supports the two compatibility
  formats for that distribution; it does not establish injection in every
  shell/interface, platform or release. No proprietary source is reproduced here.

## 9. Adding or changing rules

Include a public source or a redacted observation with date, product version and
execution scope when available. Explain why the marker is preferable to generic
configuration. State non-empty/exact semantics, conjunctions, precedence, and
known coverage limits. Add synthetic positive, empty/wrong-value, partial-AND,
and coexistence cases. Do not submit environment dumps, real tokens, session IDs,
internal endpoints, user paths, or proprietary source files.

Changes to matching behavior, priority, canonical IDs or result semantics require
a version update and a changelog entry. Product-description/source-link edits
alone do not change the detection contract. See [CONTRIBUTING.md](CONTRIBUTING.md).
