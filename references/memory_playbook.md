# 记忆与续团手册

长期团的目标不是记录所有对话，而是保留能让剧情继续成立的状态。

## 记忆层

- 玩家可知：已公开线索、NPC 公开状态、地点、物品、HP/SAN/MP、未解决问题。
- Keeper：真相、隐藏动机、暗骰、隐藏 SAN、倒计时、伏笔。
- 剧本连续性：核心设定、分幕、场景节点、线索网、NPC 剧本功能、威胁时钟、结局条件。
- 风格：当前 KP 风格或玩家自定义风格，保存到 `meta.keeper_style`。

## 更新时机

不要每轮普通对话都写记忆。只在以下情况更新：

- 新开团或角色/NPC 锚定完成。
- 用户切换或保存 KP 风格。
- 场景结束、地点或时间改变。
- 玩家获得关键线索或作出不可逆选择。
- NPC 态度、位置、秘密、关系发生变化。
- HP/SAN/MP/物品/伤势/异常状态发生变化。
- 暗骰、隐藏 SAN、倒计时、敌方行动或伏笔发生。
- 用户要求继续、回忆、存档、读档、导入、导出。

## 续团流程

1. 找到团名；不明确时先 `python scripts/memory.py list`。
2. 读取 `python scripts/memory.py recall --name "<团名>" --keeper`。
3. 先恢复当前场景、玩家可知摘要、Keeper 摘要、KP 风格、未结算事项。
4. 对玩家只输出玩家可知的极短上回回顾。
5. 从当前场景继续，给 2-4 个行动切口。

## 常用命令

```bash
python scripts/memory.py init --name "<团名>" --era "modern" --location "<地点>" --characters "<调查员>" --style "平衡 Keeper"
python scripts/memory.py set --name "<团名>" --field style --value "<KP风格>"
python scripts/memory.py set --name "<团名>" --field hook --value "<下一轮开场钩子>"
python scripts/memory.py add --name "<团名>" --section clue --text "<玩家已知线索>"
python scripts/memory.py add --name "<团名>" --section secret --text "<Keeper秘密>"
python scripts/memory.py add --name "<团名>" --section unresolved --text "<未结算事项>"
python scripts/memory.py recall --name "<团名>" --keeper
python scripts/memory.py save --name "<团名>"
```

## 存档前检查

- 当前时间、地点、同行者一致。
- HP/SAN/MP/状态/物品一致。
- 玩家已知线索没有混入 Keeper Only 真相。
- NPC 位置、态度、秘密一致。
- 当前 KP 风格已记录。
- 未结算暗骰、隐藏 SAN、倒计时、追踪者已记录。
- 下一轮开场钩子清楚。
