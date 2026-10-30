# Detect Agent

A language-independent Markdown specification for identifying AI agent execution
environments. Give an agent one document; let it implement the detector in your
project's own language, without an SDK or runtime network access.

**[Read the specification](detect-agent.md)** · [中文说明](README.zh-CN.md) · [Conformance cases](conformance/cases.json)

## Check your own agent

Start with [AGENTS.md](AGENTS.md) and the
[self-check and rule-update guide](docs/agent-self-check.md). From this repository,
using Python 3.9+ with no dependencies:

```sh
python3 scripts/check.py conformance
python3 scripts/check.py self-check --expect codex
```

Replace `codex` with your expected canonical product ID and run through your
agent's actual command tool. The first command checks synthetic fixtures; the
second reports your live process without printing environment values. A successful
declaration or context hint alone does not establish automatic recognition. The
guide explains how to diagnose a mismatch, update a consuming implementation,
and contribute evidence-backed rule changes.

## Use it in an agent

```text
Read detect-agent.md from this repository. Implement its detection contract in
this project using our existing language and conventions. Preserve the listed
matching semantics and priority. Distinguish runtime markers from editor and
workspace hints. Use synthetic inputs to verify the conformance cases. Do not
add a runtime network dependency or log environment values.
```

You can paste the document into context, attach a local copy, or link to it using
your agent's normal document-reading tools. Pin a Git commit for reproducible
implementations; review changes before refreshing a vendored copy.

Version 0.1.5 covers **35 canonical product IDs**, with ordered runtime rules,
explicit self-declarations, optional context hints, source/coverage notes and
portable examples. Ordinary runtime markers use non-empty checks; exact values
are reserved for context selectors. Detection identifies environment context,
not an authenticated caller. Product names include **QwenWork, Doubao Work, Manus,
Cue and Muse**.

This repository contains a specification, test data and optional development
tools, not a detector library. The checker reads the specification's tables;
it does not maintain a second rule catalog.
[Contributions](CONTRIBUTING.md) are welcome. Original content is [MIT licensed](LICENSE);
referenced projects retain their own licenses and attribution.
