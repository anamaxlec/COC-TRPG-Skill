# Keeper 对话评估

这些场景评估实际生成的下一轮主持回复，与脚本单测分开运行。覆盖 NPC 提问与邀请、幕后钩子隔离、失败检定、玩家改变未来事件、续团状态、叙事变化和修辞问句。场景为本项目自编，与内置第三方模组无关。

## 准备独立输入

在 skill 根目录运行：

```bash
python scripts/keeper_eval.py prepare --output-dir /tmp/coc-keeper-eval
```

每个 `.prompt.md` 包含所需 skill 指令、场景、玩家输入，以及适用时通过真实记忆工具生成的 Keeper 回顾。评分标准留在 `cases.json`，不会进入被测模型的提示。

让被测模型在新会话读取一个提示，只生成面向玩家的下一轮回复，保存为对应的 `<id>.response.txt`。每个场景使用独立会话。评分者随后按 `cases.json` 的该项标准检查回复，将判断与具体依据保存为 `<id>.grade.json`：

```json
{"passed": false, "reason": "说明回复在哪个具体位置违背了哪项标准。"}
```

一次运行保留全部输入、原始回复、评分与报告；记录被测模型、评分者、运行日期和使用的 skill Git commit，便于再次运行时比较行为。

```bash
python scripts/keeper_eval.py report --output-dir /tmp/coc-keeper-eval
```

报告区分通过、失败、未运行、待评分与评分无效。缺少回复或评分的场景不会计为通过；失败或未完成时命令返回非零。

## 自动调用模型

已有模型命令支持从 stdin 接收提示、仅向 stdout 输出回复时，可以自动运行：

```text
python scripts/keeper_eval.py run --output-dir <新的评估目录> --runner "<被测模型命令>" --judge "<独立评分命令>"
```

`--runner` 每次调用须开启独立会话；`--judge` 每次接收场景、评分标准和实际回复，输出上述 JSON。命令按参数数组执行，支持带空格的引号参数；管道或其他 shell 组合应放在单独包装脚本中。模型命令的访问权限、费用与输出格式由使用者的现有工具配置负责。脚本本身只使用 Python 标准库。

人工或 Agent 评分时同样保留具体依据。一次通过只说明这些固定场景的本次输出符合标准；持续改进时重新生成回复，不把旧回复当成新模型运行结果。
