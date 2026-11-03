# detect-agent.md

一份文档，让 Agent 实现并共同维护 Agent 检测。

这份 Markdown 规范描述如何识别 AI Agent 的运行环境。让 Agent 按文档为你的项目实现检测能力，
也让各种 Agent 补充自己的识别特征。

## 支持识别的 Agent

规范目前覆盖 **40 个产品 ID**：

| 识别方式 | Agent |
| --- | --- |
| 运行标记（35） | Antigravity、Augment CLI、Claude Code、Claude Cowork、Cline、Codex、Crush、Cue、Cursor CLI、DeepSeek Harness、Devin、豆包工作、Gemini CLI、GitHub Copilot CLI、Goose、Grok Bot、Grok Build、Hermes Agent、Instinct、Junie、Kilo Code、Kimi Code、Kiro、灵光、Manus、Muse、OpenClaw、opencode、Pi、Qwen Code、千问办公、Roo Code、TRAE、VT Code、WorkBuddy |
| 上下文提示（3） | Cursor（编辑器）、Replit、Zed |
| 仅显式声明（2） | hi、SandBase Harness |

具体覆盖范围和匹配条件以[规范](detect-agent.md)为准。上下文提示说明编辑器或工作区环境，
不能确认 Agent 正在执行；所有列出的产品也都支持显式声明。

各产品的介绍与官方来源见下方 [Agent 介绍](#agent-介绍)。

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
如果识别结果不符合预期，按 docs/diagnostics.md 定位原因、在正确的位置修复并验证。
不要公开环境变量值，不要增加运行时联网依赖。
完成后报告来源 commit、修改文件、实际测试结果及覆盖范围。
```

你会得到项目内可用的检测代码与测试，以及可追溯的规范版本。
[Agent 完整工作流 →](docs/implement-detection.md)

## 2. 让 Agent 更新自己的识别特征

在你希望被正确识别的 Agent 产品里使用。Agent 会先检查已有规则，再查证真实特征；
确有缺漏时，为 **detect-agent.md 仓库** 提交改动。

```text
请帮助 detect-agent.md 正确识别正在执行这项任务的 Agent 产品。
阅读 https://github.com/ai-shifu/detect-agent ，选定一个 Git commit，
按同一版本中的 docs/contribute-agent.md 执行。
通过你实际使用的命令环境验证已有规则，为缺失或错误的识别特征收集证据。
如果识别结果不符合预期，按 docs/diagnostics.md 定位原因、在正确的位置修复并验证。
需要修改规则时，在该仓库的独立检出中完成最小改动、验证并提交 PR；
已有规则足够时，报告验证结果和覆盖范围即可。不要公开环境变量值，不要合并 main。
```

你会得到一份有验证依据的覆盖报告，或一个有证据和测试的 PR。已有规则正确时无需新增规则。
[Agent 完整工作流 →](docs/contribute-agent.md)

## 项目提供什么

[规范 0.1.11](detect-agent.md) 覆盖 **40 个统一产品 ID**，定义声明身份、运行标记、上下文提示、
匹配语义和判定优先级。检测结果描述进程环境，不能证明当前命令由谁直接发起。

已知身份的声明可携带版本后缀。可选诊断保留所有运行标记和上下文命中，且不输出变量值；
[交叉匹配案例](conformance/matches.json)检查允许的重叠和被正确结果遮住的误报。
核心检测不读取进程树。

Agent 可通过自己的工具读取规范和[合成案例](conformance/cases.json)。实现无需 SDK，
运行时也不依赖本仓库联网。Agent 开始任务时固定来源 commit，让规则和测试可以复现。

完整规范和 Agent 工作流以英文维护；上面的中文提示词可以直接使用。

## Agent 介绍

以下描述根据各产品官网、官方文档、官方公告或官方仓库 README 整理并翻译，核验日期为 **2026-11-03**。
使用官方仓库作为产品介绍来源的项目已明确标注。产品介绍不构成运行标记证据，
具体识别范围仍以规范为准。

| 产品 ID | Agent | 描述 | 官方来源 |
| --- | --- | --- | --- |
| `antigravity` | Antigravity | Google 的 Agent 开发平台，通过应用、命令行和 IDE 支持与编程 Agent 协作开发软件。 | [官网](https://antigravity.google/) |
| `augment-cli` | Augment CLI | Augment 的 Auggie 编程 Agent，可交互式规划、执行和审查代码库工作，也可用于终端自动化。 | [官网](https://www.augmentcode.com/product/cli) |
| `claude-code` | Claude Code | Anthropic 的编程 Agent，可在开发工具中实现功能、修复问题、编写测试并执行代码迁移。 | [官网](https://claude.com/product/claude-code) |
| `cowork` | Claude Cowork | 现已融入 Claude，可跨文件和工具完成工作，交付文档、表格、研究等成果。 | [官网](https://claude.com/product/cowork) |
| `cline` | Cline | 开源编程 Agent 运行时，可通过编辑器、命令行和 SDK 规划任务、修改项目并执行终端命令。 | [官网](https://cline.bot/) |
| `codex` | Codex | OpenAI 的编程 Agent，可在 ChatGPT、编辑器、终端和云端实现功能、调试、重构及审查代码。 | [官网](https://openai.com/codex/) |
| `crush` | Crush | 终端编程助手，将现有工具、代码和工作流连接到用户选择的语言模型。 | [官网](https://charm.land/) |
| `cue` | Cue | 桌面 AI 助手，结合语音请求和屏幕上下文，协助日常写作、任务执行与会议记录。 | [官网](https://heycue.io/) |
| `cursor` | Cursor（编辑器） | AI 编辑器与编程 Agent，可理解代码库、开发功能、修复问题和审查改动。 | [官方文档](https://cursor.com/docs) |
| `cursor-cli` | Cursor CLI | 在终端中使用编程 Agent，支持交互操作、脚本、自动化及 GitHub Actions 集成。 | [官网](https://cursor.com/cli) |
| `deepseek-harness` | DeepSeek Harness | 开源 Agent Harness，通过可组合插件处理日常工作、编程和资料研究，并定制 Agent 能力。 | [官网](https://deepseek.com/harness/) |
| `devin` | Devin | 自主软件工程师，可在云端或本地环境工作、测试改动并准备拉取请求。 | [官网](https://devin.ai/) |
| `doubao-work` | 豆包工作 | 面向个人和团队的智能体工作平台，可执行任务、生成文档、表格、演示与应用，并接入飞书协作。 | [官网](https://www.feishu.cn/content/article/7677519271848610746) |
| `gemini-cli` | Gemini CLI | 终端 AI 工具，可查询和编辑代码库、构建应用、调试部署，并自动执行复杂工作流。 | [官网](https://geminicli.com/) |
| `github-copilot` | GitHub Copilot CLI | 在终端中回答问题、编写和调试代码，并处理 GitHub Issue 与 Pull Request 的 AI Agent。 | [官方文档](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-cli) |
| `goose` | Goose | 在本机运行的开源 AI Agent，可用于编程、研究、写作、自动化和数据分析。 | [官网](https://goose-docs.ai/) |
| `grok-bot` | Grok Bot | 保留上下文、在持久云电脑上跨应用和网站完成任务的 AI 队友。 | [官方文档](https://cursor.com/docs/grok-bot) |
| `grok-build` | Grok Build | 在终端中规划、开发、测试和部署软件的编程 Agent，支持技能、工具和并行子 Agent。 | [官网](https://x.ai/build) |
| `hermes-agent` | Hermes Agent | 支持持久记忆、自动生成技能，并可接入聊天平台和命令行的开源 Agent。 | [官网](https://hermes-agent.nousresearch.com/) |
| `hi` | hi | 使用 Pipe Network 推理服务的编程 Agent，可读写和编辑项目文件并运行 Shell 命令。 | [官方仓库](https://github.com/PipeNetwork/hi) |
| `instinct` | Instinct | 理解你的工作和关注事项，可通过短信或电话交流，并操作手机和电脑完成任务的个人助手。 | [官网](https://instinct.com/) |
| `junie` | Junie | 结合 IDE 代码智能与终端工作流、支持开发者选择模型的 JetBrains 编程 Agent。 | [官网](https://junie.jetbrains.com/) |
| `kilo-code` | Kilo Code | 覆盖 IDE、命令行和云端工作流，可编写、规划和调试代码的开源编程 Agent。 | [官网](https://kilo.ai/) |
| `kimi` | Kimi Code | 可通过桌面应用、命令行和 IDE 插件完成编程任务的 AI 编程 Agent。 | [官网](https://www.kimi.com/code) |
| `kiro` | Kiro | 支持规范驱动开发、并行实现和代码正确性测试的 AI 编程 Agent。 | [官网](https://kiro.dev/) |
| `lingguang` | 灵光 | 蚂蚁集团的多模态个人 AI Agent，在用户授权下识别需求并持续管理任务。 | [官方公告](https://www.antgroup.com/en/news-media/press-releases/1793066400000) |
| `manus` | Manus | 可自动执行工作流、开展研究，并将指令转化为实际成果的通用 AI Agent。 | [官网](https://manus.im/about) |
| `muse` | Muse | Meta 的个人 AI Agent，可跨日常应用处理任务和项目，并将长期目标转化为行动计划。 | [官方公告](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/) |
| `openclaw` | OpenClaw | 在你的设备上运行的开源 AI 助手，可通过常用聊天应用执行任务。 | [官网](https://openclaw.ai/) |
| `opencode` | opencode | 开源编程 Agent，可通过终端、IDE 扩展或桌面应用编写和运行代码。 | [官网](https://opencode.ai/) |
| `pi` | Pi | 可扩展的终端 AI Agent，能检查文件、运行命令、编辑内容并完成多步骤任务。 | [官方文档](https://pi.dev/docs/latest) |
| `qwen-code` | Qwen Code | Qwen 推出的终端编程 Agent，通过工具与开发工作流集成把想法变为代码。 | [官方文档](https://qwenlm.github.io/qwen-code-docs/en/users/overview/) |
| `qwenwork` | 千问办公 | 阿里巴巴推出的一站式 AI 办公平台，可执行复杂任务并交付文档、表格、PPT、网页等成果。 | [官方文档](https://docs.qwenwork.cn/product-introduction) |
| `replit` | Replit | 将自然语言想法变为应用的 AI 平台，并提供托管、数据库、身份认证和监控。 | [官网](https://replit.com/) |
| `roo-code` | Roo Code | 面向 VS Code 的开源 AI 编程 Agent；官方文档已公告扩展停止服务。 | [官方文档](https://roocodeinc.github.io/Roo-Code/) |
| `sandbase-harness` | SandBase Harness | 运行在自有基础设施上的 AI Agent 运行时，提供持久会话、沙箱工具、记忆、凭据管理、审计与管理控制台。 | [官方仓库](https://github.com/sandbaseai/sandbase-harness) |
| `trae` | TRAE | 融合 AI 辅助 IDE 与自主编程 Agent 的开发环境，可规划、实现并交付软件。 | [官网](https://www.trae.ai/blog/trae_work_0609) |
| `vtcode` | VT Code | 使用 Rust 开发的编程 Agent，可在终端或原生 macOS 应用中探索、规划、修改和验证代码仓库。 | [官方仓库](https://github.com/vinhnx/VTCode) |
| `workbuddy` | WorkBuddy | 腾讯推出的 AI 工作台，可规划流程、调用工具并交付文档、表格、演示文稿等工作成果。 | [官方文档](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Product-Guide) |
| `zed` | Zed | 集成协作与 AI 工具的开源代码编辑器。 | [官方文档](https://zed.dev/docs/) |

## 致谢

感谢以下开源项目的维护者和贡献者，公开分享识别规则、运行标记、证据资料和设计经验，
为本规范的规则整理、信号调查和诊断设计提供了重要基础与参考：

- [Hugging Face · huggingface.js](https://github.com/huggingface/huggingface.js) — 公开的 Agent harness 注册表。
- [Vercel · detect-agent](https://github.com/vercel/detect-agent) — 共享识别规则和 `AI_AGENT` 命名约定。
- [Together · detect_agent](https://github.com/togethercomputer/detect_agent) — Python 移植与规则求值参考。
- [Expo · agent-cli-detector](https://github.com/expo/agent-cli-detector) — 运行标记和可扩展检测策略。
- [am-i-vibing](https://github.com/ascorbic/am-i-vibing) — 执行环境分类与识别信号。
- [uarix · agent-harness-detector](https://github.com/uarix/agent-harness-detector) — 更多桌面与云端产品的识别线索。
- [ai-agent-detect](https://github.com/agent-detect/ai-agent-detect) — 证据记录、全部命中诊断与交叉测试。

具体采用的信号、核验过的源码版本及适用边界，见[规范中的来源引用](detect-agent.md#8-evidence-coverage-and-references)。

[Agent 入口](AGENTS.md) · [自检、诊断与修复](docs/diagnostics.md) ·
[贡献要求](CONTRIBUTING.md) · [更新记录](CHANGELOG.md)

原创内容采用 [MIT](LICENSE) 许可，引用项目保留各自的许可和署名。
