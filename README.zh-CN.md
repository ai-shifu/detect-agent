# Detect Agent：让智能体实现和维护智能体检测

一份供 Agent 阅读、实现和维护的运行环境识别规范：让 Agent 按文档为你的项目实现检测能力，
也让各种 Agent 补充自己的识别特征。

## 支持识别的 Agent

规范目前覆盖 **35 个产品 ID**：

| 识别方式 | Agent |
| --- | --- |
| 运行标记（28） | Antigravity、Augment CLI、Claude Code、Claude Cowork、Cline、Codex、Crush、Cue、Cursor CLI、Doubao Work、Gemini CLI、Goose、Grok Bot、Grok Build、Hermes Agent、Junie、Kilo Code、Kimi Code、Kiro、Manus、Muse、OpenClaw、opencode、Pi、QwenWork、TRAE、VT Code、WorkBuddy |
| 上下文提示（5） | Cursor（编辑器）、Devin、GitHub Copilot、Replit、Zed |
| 仅显式声明（2） | hi、SandBase Harness |

具体覆盖范围和匹配条件以[规范](detect-agent.md)为准。上下文提示说明编辑器或工作区环境，
不能确认 Agent 正在执行；所有列出的产品也都支持显式声明。

**选一个场景，把对应提示词复制给你的 Agent 即可。** 它会自行读取流程和规范、完成工作并验证结果。
你只需要理解这两个场景，无需先研究规则表或选择 SDK。

[English](README.md)

## 1. 让 Agent 为你的项目实现检测

在需要检测能力的项目中使用。Agent 会使用 **你的项目已有的语言和代码风格** 实现规范，
并用共享案例验证它实际写出的代码。

```text
请在我的当前项目中实现智能体运行环境检测。
阅读 https://github.com/ai-shifu/detect-agent ，选定一个 Git commit，
按同一版本中的 docs/implement-detection.md 执行，完整读取该版本的规范和合成案例。
使用当前项目已有的语言和代码风格，完成实现与接入，将全部共享案例送入本次实现进行验证。
不要公开环境变量值，不要增加运行时联网依赖。
完成后报告来源 commit、修改文件、实际测试结果及覆盖范围。
```

你会得到项目内可用的检测代码与测试，以及可追溯的规范版本。
[Agent 完整工作流 →](docs/implement-detection.md)

## 2. 让 Agent 更新自己的识别特征

在你希望被正确识别的 Agent 产品里使用。Agent 会先检查已有规则，再查证真实特征；
确有缺漏时，为 **Detect Agent 仓库** 提交改动。

```text
请帮助 Detect Agent 正确识别正在执行这项任务的 Agent 产品。
阅读 https://github.com/ai-shifu/detect-agent ，选定一个 Git commit，
按同一版本中的 docs/contribute-agent.md 执行。
通过你实际使用的命令环境验证已有规则，为缺失或错误的识别特征收集证据。
需要修改规则时，在该仓库的独立检出中完成最小改动、验证并提交 PR；
已有规则足够时，报告验证结果和覆盖范围即可。不要公开环境变量值，不要合并 main。
```

你会得到一份有验证依据的覆盖报告，或一个有证据和测试的 PR。已有规则正确时无需新增规则。
[Agent 完整工作流 →](docs/contribute-agent.md)

## 项目提供什么

[规范 0.1.5](detect-agent.md) 覆盖 **35 个统一产品 ID**，定义声明身份、运行标记、上下文提示、
匹配语义和判定优先级。检测结果描述进程环境，不能证明当前命令由谁直接发起。

Agent 可通过自己的工具读取规范和[合成案例](conformance/cases.json)。实现无需 SDK，
运行时也不依赖本仓库联网。Agent 开始任务时固定来源 commit，让规则和测试可以复现。

完整规范和 Agent 工作流以英文维护；上面的中文提示词可以直接使用。

[Agent 入口](AGENTS.md) · [运行环境诊断](docs/agent-self-check.md) ·
[贡献要求](CONTRIBUTING.md) · [更新记录](CHANGELOG.md)

原创内容采用 [MIT](LICENSE) 许可，引用项目保留各自的许可和署名。
