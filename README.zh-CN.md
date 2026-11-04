# detect-agent.md

一份文档，让 Agent 实现并共同维护 Agent 检测。

这份 Markdown 规范描述如何识别 AI Agent 的运行环境。让 Agent 按文档为你的项目实现检测能力，
也让各种 Agent 补充自己的识别特征。

## 支持识别的 Agent

规范目前覆盖 **41 个产品 ID**：

| 识别方式 | Agent |
| --- | --- |
| 运行标记（36） | Antigravity、Augment CLI、Claude Code、Claude Cowork、Cline、Codex、Crush、Cue、Cursor CLI、DeepSeek Harness、Devin、豆包工作、Gemini CLI、GitHub Copilot CLI、Goose、Grok Bot、Grok Build、Hermes Agent、Instinct、Junie、Kilo Code、Kimi Code、Kiro、灵光、Manus、Muse、OpenClaw、opencode、Pi、Qwen Code、千问办公、Roo Code、TRAE、VT Code、WorkBuddy |
| 上下文提示（3） | Cursor（编辑器）、Replit、Zed |
| 仅显式声明（2） | hi、SandBase Harness |

具体覆盖范围和匹配条件以[规范](detect-agent.md)为准。上下文提示说明编辑器或工作区环境，
不能确认 Agent 正在执行；所有列出的产品也都支持显式声明。

产品描述与官方来源可按产品 ID 从规范的[产品元数据表](detect-agent.md#product-metadata)获取。

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

[规范 0.1.12](detect-agent.md) 覆盖 **41 个统一产品 ID**，定义声明身份、运行标记、上下文提示、
匹配语义和判定优先级。检测结果描述进程环境，不能证明当前命令由谁直接发起。

已知身份的声明可携带版本后缀。可选诊断保留所有运行标记和上下文命中，且不输出变量值；
[交叉匹配案例](conformance/matches.json)检查允许的重叠和被正确结果遮住的误报。
核心检测不读取进程树。

Agent 可通过自己的工具读取规范和[合成案例](conformance/cases.json)。实现无需 SDK，
运行时也不依赖本仓库联网。Agent 开始任务时固定来源 commit，让规则和测试可以复现。

完整规范和 Agent 工作流以英文维护；上面的中文提示词可以直接使用。

## 产品元数据

产品名、中英文描述、官方来源和核验日期统一维护在规范的[产品元数据表](detect-agent.md#product-metadata)中，
使用与识别特征相同的产品 ID。描述优先采用官方产品仓库的 GitHub About 文案，
没有适用 About 时使用官网等官方资料。实现检测时，可从同一版本读取规则和元数据，
将元数据内置为本地映射，再按检测返回的 `agent_id` 直接获取描述。

开发工具可从规范读取数据并输出 JSON：

```sh
python3 scripts/check.py agent-info --id codex
python3 scripts/check.py export-metadata > agent-metadata.json
```

导出用于开发时生成当前项目语言的本地数据表。元数据查询与检测的两个返回字段分开，
未知 ID 返回 null；生产查询无需联网或依赖 Python。
具体约定见[实现工作流](docs/implement-detection.md#provide-product-metadata-when-needed)。

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
