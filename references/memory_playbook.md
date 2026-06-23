# v2 记忆与续团手册

长期团记忆的目标不是保存全部对话，而是保留下次能继续成立的状态：当前场景、调查员状态、线索网络、NPC 动向、未结算事项、威胁时钟和 Keeper Only 真相。

## 数据位置

`scripts/memory.py` 默认不再写入 skill 安装目录。

- macOS/Linux: `~/.codex/data/coc-trpg-skill`
- Windows: `%APPDATA%\coc-trpg-skill`
- 覆盖方式: `COC_TRPG_DATA_DIR` 或每个命令的 `--data-dir <path>`

旧 v1 `scenarios/`、`saves/` 不自动迁移。需要保留时运行：

```bash
python scripts/memory.py archive-legacy
```

## 续团流程

1. 不明确团名时先列出：`python scripts/memory.py list`
2. 读取完整 Keeper 摘要：`python scripts/memory.py recall --name "<团名>" --keeper`
3. 对玩家只输出玩家可知摘要，不展示 Keeper 段落。
4. 从 `当前场景` 和 `下一轮钩子` 继续，不重开剧情。
5. 场景结束或关键状态变化后写入 v2 记忆，并在需要时 `snapshot`。

## 自动写入时机

不要每轮普通对话都写记忆。只在以下情况写入：

- 新开团、角色锚定、内容边界或 KP 风格确定。
- 场景结束、地点/时间改变、进入新节点。
- 玩家获得关键线索、作出不可逆选择。
- 调查员 HP/SAN/MP、伤势、异常状态、物品变化。
- NPC 态度、位置、真实状态、关系发生变化。
- 暗骰、隐藏 SAN、延迟公开 SAN、倒计时、敌方行动或伏笔发生。
- 用户说“继续”“回忆一下”“存档”“导出”“更新记忆”。

## 命令映射

新开团：

```bash
python scripts/memory.py init --name "<团名>" --era "modern" --location "<地点>" --scene "<当前场景>" --characters "<调查员>" --style "平衡 Keeper" --boundaries "<内容边界>"
```

更新当前落点：

```bash
python scripts/memory.py set-current --name "<团名>" --time "<时间>" --location "<地点>" --scene "<场景>" --companions "<同行者>" --hook "<下一轮钩子>"
python scripts/memory.py set-current --name "<团名>" --style "<KP风格>" --boundaries "<内容边界>"
```

公开事件、决定、状态变化：

```bash
python scripts/memory.py record --name "<团名>" --visibility public --kind scene --text "<玩家可知事件>"
python scripts/memory.py record --name "<团名>" --visibility public --kind decision --text "<玩家作出的不可逆选择>"
```

Keeper Only 事件：

```bash
python scripts/memory.py record --name "<团名>" --visibility keeper --kind note --text "<幕后真相或敌方行动>"
python scripts/memory.py record --name "<团名>" --visibility keeper --kind roll --text "<暗骰原因、结果、后续影响>"
python scripts/memory.py record --name "<团名>" --visibility keeper --kind san --text "<隐藏或延迟 SAN>"
```

实体状态：

```bash
python scripts/memory.py entity --name "<团名>" --type investigator --entity "<调查员>" --status "HP 12 SAN 50 MP 10" --public "<玩家可知状态>" --keeper "<隐藏状态>"
python scripts/memory.py entity --name "<团名>" --type npc --entity "<NPC>" --location "<位置>" --public "<公开身份/态度>" --keeper "<真实动机/下一步行动>"
python scripts/memory.py entity --name "<团名>" --type location --entity "<地点>" --public "<玩家已知信息>" --keeper "<隐藏风险>"
python scripts/memory.py entity --name "<团名>" --type item --entity "<物品>" --status "<状态>" --public "<用途>" --keeper "<隐藏性质>"
```

线索网络：

```bash
python scripts/memory.py clue --name "<团名>" --id C-001 --text "<线索>" --source "<来源>" --points-to "<指向>" --visibility public --key-inference "<关键推论>" --alternate-path "<替代路径1>,<替代路径2>"
```

未结算线程：

```bash
python scripts/memory.py thread --name "<团名>" --type open-question --visibility public --text "<玩家可知疑问>" --next "<下一步>"
python scripts/memory.py thread --name "<团名>" --type unresolved --visibility keeper --text "<未结算事项>" --next "<何时结算>"
python scripts/memory.py thread --name "<团名>" --type delayed-san --visibility keeper --text "<延迟 SAN 原因>" --next "<公开时机>"
python scripts/memory.py thread --name "<团名>" --type hidden-roll --visibility keeper --text "<暗骰后果>" --next "<后续影响>"
python scripts/memory.py thread --name "<团名>" --type foreshadowing --visibility keeper --text "<伏笔>" --resolution "<回收方式>"
```

威胁时钟：

```bash
python scripts/memory.py clock --name "<团名>" --clock "<时钟名>" --progress "1/4" --trigger "<触发条件>" --visible "<玩家可感知迹象>" --next "<下一步>"
```

生成续跑快照：

```bash
python scripts/memory.py snapshot --name "<团名>"
```

## 写入质量

- `public` 只能写玩家已经知道或能观察到的内容。
- `keeper` 写幕后真相、隐藏动机、暗骰、隐藏 SAN、敌方行动和威胁时钟。
- 每条线索尽量写清 `来源`、`指向`、`关键推论` 和至少一个替代路径。
- 实体状态要写“现在是什么”，不要只写历史经过。
- `thread` 只放未解决、待回收或待结算内容；已经解决的事项要更新 `status` 或 `resolution`。
- 场景结束时必须更新 `set-current --hook`，保证下次能直接开场。

## 续跑前检查

- 当前时间、地点、场景和同行者一致。
- HP/SAN/MP、伤势、异常状态、物品一致。
- 玩家已知线索没有混入 Keeper Only 真相。
- NPC 位置、态度、秘密和下一步行动一致。
- 暗骰、延迟 SAN、威胁时钟和敌方行动已记录。
- 下一轮钩子足够具体，能直接接入玩家行动。
