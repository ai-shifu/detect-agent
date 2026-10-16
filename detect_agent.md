# detect_agent.md

Version: **0.1.1** · Evidence reviewed: **2026-10-16** · License: **MIT**

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

The environment input is a string-to-string mapping; absent keys have no value.

1. Environment variable **names are case-sensitive**. Check only the complete
   names listed here. A missing key and a key with an empty string both fail a
   non-empty check.
2. **Non-empty** means string length greater than zero. Do not trim values:
   `"0"`, `"false"`, and `" "` all pass. Do not parse these values as booleans.
3. **Equals** means a case-sensitive, whole-string comparison. For an exact `1`
   rule, `"true"`, `"01"`, `" 1"`, and `"1\n"` all fail.
4. **OR** requires at least one complete alternative. **AND** requires all
   conditions in that parenthesized group, from the same environment snapshot.
5. Only explicit ID declarations are trimmed and ASCII-lowercased for lookup.
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

## 3. Detection algorithm and priority

```text
DETECT(environment, optional filesystem_probe, optional stdout_is_tty):
    for key in [AI_AGENT, AGENT], in that order:
        if key exists and trim(environment[key]) is not empty:
            id = ASCII_LOWERCASE(trim(environment[key]))
            id = map documented compatibility aliases to canonical IDs
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
hint. Cowork precedes Claude Code; Grok Bot and Grok Build precede their Cursor or
Claude compatibility markers; Cursor CLI precedes the generic Cursor editor hint.
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
| 5 | `vtcode` | VT Code | `VTCODE` equals `1` | registry |
| 6 | `workbuddy` | WorkBuddy | `WORKBUDDY_APPLICATION_NAME` equals `WorkBuddy` OR `WORKBUDDY_APP_NAME` equals `WorkBuddy` | static-distribution |
| 7 | `grok-bot` | Grok Bot | `SAND_AGENT` equals `1` OR (non-empty `CURSOR_AGENT` AND `SAND_MANIFEST_V2` equals `1` AND `SAND_SUPERVISOR_ENABLED` equals `1`) | static-distribution (local); reported-shell (cloud) |
| 8 | `qwenwork` | QwenWork | non-empty `QODER_WORK_INTEGRATION_PRODUCT` | static-distribution / reported-shell |
| 9 | `cue` | Cue | `MANUS_LONG_DESKTOP_WORKER` equals `1` | reported-shell |
| 10 | `muse` | Muse | `JARVIS_IS_ASSIGNED` equals `1` OR non-empty `JARVIS_TOOL_CALL_ID` | reported-shell |
| 11 | `manus` | Manus | non-empty `MANUS_ADDON_RUNTIME_SPEC_PATH` OR non-empty `MANUS_ADDON_RUNTIME_SPECS_REVISION` | reported-shell |
| 12 | `doubao-work` | Doubao Work | non-empty `DOUBAO_OFFICE_AGENT_NAME` | reported-shell |
| 13 | `kimi` | Kimi Code | non-empty `KIMI_PLUGIN_ROOT` | public-source |
| 14 | `grok-build` | Grok Build | `GROK_AGENT` equals `1` OR non-empty `GROK_PLUGIN_ROOT` OR non-empty `GROK_PLUGIN_DATA` | public-source |
| 15 | `gemini-cli` | Gemini CLI | non-empty `GEMINI_CLI` | registry |
| 16 | `cline` | Cline | non-empty `CLINE_ACTIVE` | registry |
| 17 | `codex` | Codex | non-empty `CODEX_SANDBOX` OR non-empty `CODEX_CI` OR non-empty `CODEX_THREAD_ID` OR non-empty `CODEX_SANDBOX_NETWORK_DISABLED` | public-source / registry |
| 18 | `antigravity` | Antigravity | non-empty `ANTIGRAVITY_AGENT` OR non-empty `ANTIGRAVITY_CLI_ALIAS` | registry |
| 19 | `augment-cli` | Augment CLI | non-empty `AUGMENT_AGENT` | registry |
| 20 | `opencode` | opencode | non-empty `OPENCODE_CLIENT` OR non-empty `OPENCODE` | registry |
| 21 | `goose` | Goose | non-empty `GOOSE_TERMINAL` | registry |
| 22 | `junie` | Junie | non-empty `JUNIE_DATA` OR non-empty `JUNIE_SHIM_PATH` | public-source |
| 23 | `pi` | Pi | non-empty `PI_CODING_AGENT` | registry |
| 24 | `cowork` | Cowork | non-empty `CLAUDE_CODE_IS_COWORK` AND (non-empty `CLAUDECODE` OR non-empty `CLAUDE_CODE`) | registry |
| 25 | `claude-code` | Claude Code | non-empty `CLAUDECODE` OR non-empty `CLAUDE_CODE` | registry |
| 26 | `cursor-cli` | Cursor CLI | non-empty `CURSOR_AGENT` OR `CURSOR_EXTENSION_HOST_ROLE` equals `agent-exec` | registry |
| 27 | `kiro` | Kiro | non-empty `AGENT_CONTEXT_OUT` | registry |
| 28 | `openclaw` | OpenClaw | non-empty `OPENCLAW_SHELL` | registry |

Important boundaries:

- QwenWork requires only non-empty `QODER_WORK_INTEGRATION_PRODUCT`; it is **not**
  restricted to `qwenworkcn`. That value was observed in an inspected build,
  but other non-empty values also match this specification.
- Doubao Work requires only non-empty `DOUBAO_OFFICE_AGENT_NAME`; do not require
  a particular agent-name value. The internal `OFFICE` namespace is retained
  even though the product's official English name is Doubao Work.
- `MANUS_LONG_DESKTOP_WORKER=1` identifies the reported **Cue** context.
  Do not classify it as Manus just because the name starts with `MANUS_`.
- Manus uses its two add-on runtime descriptors as alternatives. Other add-on
  and group configuration flags do not satisfy this rule.
- Grok Bot's cloud alternative requires **all three** listed conditions.
  The shared Sand flags by themselves do not identify Grok Bot.
- Grok Build is a separate product and ID. `GROK_AGENT` has selector uses,
  so its value must be exactly `1` for the terminal-marker alternative.
- Kimi's plugin marker covers plugin-hook context, not every Kimi command.
  `KIMI_CODE_HOME` is not an alternative marker.
- Cowork requires both its specific marker and a Claude Code marker here.
  This is more restrictive than registries that check the Cowork flag alone.

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

The runtime and context tables together define 33 unique canonical IDs.
Also recognize the following two IDs **only when explicitly declared**:

| Canonical ID | Product | Reference |
| --- | --- | --- |
| `hi` | hi | [Official repository](https://github.com/PipeNetwork/hi) |
| `sandbase-harness` | SandBase Harness | [Official repository](https://github.com/sandbaseai/sandbase-harness) |

No automatic marker is asserted for those two products in this version.
The complete catalog therefore has **35 IDs**. Explicit declaration also works
for every product in the runtime and context tables.

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

## 7. Inline conformance examples

All values below are synthetic, except fixed product/sentinel constants.
`{}` means an empty environment mapping. A result pair is `(agent_id, evidence)`.

| Environment / extra input | Expected result |
| --- | --- |
| `{}` | `(null, none)` |
| `AI_AGENT=" codex_cli "`, `CURSOR_AGENT="1"` | `(codex, declared)` |
| `AI_AGENT="HI"` | `(hi, declared)` |
| `AGENT="KIMI"` | `(kimi, declared)` |
| `AI_AGENT="KIMI"` (U+212A Kelvin sign) | `(null, declared)` |
| `AI_AGENT="unregistered-example"`, `CURSOR_AGENT="1"` | `(null, declared)` |
| `AI_AGENT=" "`, `AGENT="manus"` | `(manus, declared)` |
| `QODER_WORK_INTEGRATION_PRODUCT="another-name"` | `(qwenwork, runtime-marker)` |
| `QODER_WORK_INTEGRATION_PRODUCT=""` | `(null, none)` |
| `DOUBAO_OFFICE_AGENT_NAME=" "` | `(doubao-work, runtime-marker)` |
| `DOUBAO_OFFICE_AGENT_NAME=""` | `(null, none)` |
| `WORKBUDDY_APPLICATION_NAME="workbuddy"` | `(null, none)` |
| `SAND_AGENT="1"`, `CURSOR_AGENT="1"` | `(grok-bot, runtime-marker)` |
| `CURSOR_AGENT="1"`, `SAND_MANIFEST_V2="1"`, `SAND_SUPERVISOR_ENABLED="1"` | `(grok-bot, runtime-marker)` |
| `CURSOR_AGENT="1"`, `SAND_MANIFEST_V2="1"` | `(cursor-cli, runtime-marker)` |
| `SAND_MANIFEST_V2="1"`, `SAND_SUPERVISOR_ENABLED="1"` | `(null, none)` |
| `GROK_AGENT="other-selector"` | `(null, none)` |
| `MANUS_LONG_DESKTOP_WORKER="1"` | `(cue, runtime-marker)` |
| `MANUS_ADDON_RUNTIME_SPEC_PATH="synthetic-spec"` | `(manus, runtime-marker)` |
| `JARVIS_SESSION_ID="synthetic-session"` | `(null, none)` |
| `JARVIS_TOOL_CALL_ID="synthetic-tool"` | `(muse, runtime-marker)` |
| `CLAUDE_CODE_IS_COWORK="1"`, `CLAUDECODE="1"` | `(cowork, runtime-marker)` |
| `CLAUDE_CODE_IS_COWORK="1"` | `(null, none)` |
| `ZED_TERM="1"` | `(zed, context-hint)` |
| `ZED_TERM="1"`, `CODEX_THREAD_ID="synthetic-thread"` | `(codex, runtime-marker)` |
| `GOOSE_PROVIDER="synthetic-provider"` | `(goose, context-hint)` |
| `TERM_PROGRAM="kiro"`, `stdout_is_tty=false` | `(kiro, context-hint)` |
| `TERM_PROGRAM="kiro"`, TTY state unavailable | `(null, none)` |

The supplementary [`conformance/cases.json`](conformance/cases.json) is portable
input/output data, not another source of rules. A case's absent `files` or
`stdout_is_tty` field means the capability is unavailable. An optional
`path_separator` case field selects the emulated platform's PATH-list separator,
so tests do not depend on the host platform. `files: []` means
an available probe that reports no listed paths exist. Never use the machine's
actual environment, filesystem, or terminal state when running these cases.

## 8. Evidence, coverage and references

The specification separates a product's official positioning from evidence for
its internal environment variables. A product website is not a variable contract.
Reviewed source snapshots and proposed contributions are linked below; pending
contributions are not claims of upstream acceptance or deployed availability.

- **public-source**: inspected published source or documentation describes a
  particular injection path. It does not establish every shell/interface.
- **static-distribution**: independently inspected installed macOS packages:
  WorkBuddy 5.8.3, Grok Bot 0.71.2, QwenWorkCN 1.3.1. The propagation review
  was static; no vendor agent was launched. QwenWork's new product marker was
  confirmed on local/host paths, not ordinary VM/QXC guest shells.
- **reported-shell**: user-provided shell observations on 2026-10-16 for Cue,
  Muse, Manus, Doubao Work, and the Grok Bot cloud combination. They were not
  independently reproduced and are not public stability guarantees.
- **registry**: a rule appears in the referenced open-source detector snapshots.
  This attribution alone does not establish an official vendor contract.

### Detector snapshots and attribution

This document independently states detection policies and factual marker names;
it does not vendor implementation code or copy proprietary application source.
The underlying open-source projects retain their own licenses and attribution:

- [Hugging Face agent registry](https://github.com/huggingface/huggingface.js/blob/477b1ef2f0a879c4887360725bf2e4499cedd65d/packages/tasks/src/agent-harnesses.ts)
  (MIT; Hugging Face), including the accompanying [evidence notes](https://github.com/huggingface/huggingface.js/blob/477b1ef2f0a879c4887360725bf2e4499cedd65d/packages/tasks/agent-harnesses.md).
- [Vercel detector contribution snapshot](https://github.com/vercel/detect-agent/blob/57dac7a7c444a52702d26f462e49f14c19621b22/agents.json)
  (Apache-2.0), with [marker and product evidence](https://github.com/vercel/detect-agent/blob/57dac7a7c444a52702d26f462e49f14c19621b22/docs/environment-marker-evidence.md).
- [Together Python port contribution snapshot](https://github.com/togethercomputer/detect_agent/blob/19f6b9f7f751181de61caaa044adef7e1fea3e13/detect_agent/agents.json)
  (Apache-2.0; Together).

The Hugging Face snapshot uses simpler OR matching and does not contain the
compound Grok Bot cloud rule. This specification can express the conjunction
without requiring a change to that registry or its clients.

### Published marker injection references

- [Kimi plugin hooks](https://github.com/MoonshotAI/kimi-code/blob/18c6d64272952503baccf706bff455bb6a2c488e/docs/en/customization/plugins.md#L482-L486).
- [Grok Build marker definition](https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-tools/src/util/env.rs#L31-L42)
  and [terminal injection](https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-tools/src/computer/local/terminal.rs#L3315-L3323).
- [Junie launcher exports](https://github.com/JetBrains/junie/blob/cdbfbcf6a9f17951c94dd2902619dffc37f5881f/templates/junie.shim.sh#L684-L700).
- [Codex child-process injection](https://github.com/openai/codex/blob/6ae8b8aa7c608730d4315d59c5c081897ae02780/codex-rs/core/src/spawn.rs#L85-L88).
- [Hermes terminal wrapper](https://github.com/NousResearch/hermes-agent/blob/e5eb6b36fe78eb012cefd1f5f436cd458411b8b3/tools/environments/base_session_env.py#L132-L159).

### Official product identity references

- [WorkBuddy](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Product-Guide),
  [QwenWork](https://qwenwork.cn/docs/product-introduction),
  [Doubao Work introduction](https://www.feishu.cn/content/article/7677519271848610746)
  and [official English usage](https://www.feishu.cn/hc/en-US/articles/428390929435-admin-configure-screen-capture-protection).
- [Grok Bot](https://cursor.com/docs/grok-bot),
  [Cue](https://cue.im/) and its [Manus API association](https://open.manus.ai/docs/v2/agents-overview),
  [Muse](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse),
  [Manus](https://www.manus.im/about).

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
