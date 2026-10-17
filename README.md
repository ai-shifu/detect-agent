# detect_agent.md

A language-independent Markdown specification for identifying AI agent execution
environments. Give an agent one document; let it implement the detector in your
project's own language, without an SDK or runtime network access.

**[Read the specification](detect_agent.md)** · [中文说明](README.zh-CN.md) · [Conformance cases](conformance/cases.json)

## Use it in an agent

```text
Read detect_agent.md from this repository. Implement its detection contract in
this project using our existing language and conventions. Preserve the listed
matching semantics and priority. Distinguish runtime markers from editor and
workspace hints. Use synthetic inputs to verify the conformance cases. Do not
add a runtime network dependency or log environment values.
```

You can paste the document into context, attach a local copy, or link to it using
your agent's normal document-reading tools. Pin a Git commit for reproducible
implementations; review changes before refreshing a vendored copy.

Version 0.1.3 covers **35 canonical product IDs**, with ordered runtime rules,
explicit self-declarations, optional context hints, source/coverage notes and
portable examples. Detection identifies environment context, not an authenticated
caller. Product names include **QwenWork, Doubao Work, Manus, Cue and Muse**.

This repository contains a specification and test data, not a detector library.
[Contributions](CONTRIBUTING.md) are welcome. Original content is [MIT licensed](LICENSE);
referenced projects retain their own licenses and attribution.
