# COC TRPG Skill 🐙🎲

> 面向中文玩家的《克苏鲁的呼唤》（Call of Cthulhu）第 7 版跑团助手：车卡、投骰、SAN、NPC、模组大纲与 Keeper 辅助。

[![Codex Skill](https://img.shields.io/badge/Codex-Skill-blue)](https://openai.com/codex)
![COC 7th](https://img.shields.io/badge/COC-7th%20Edition-purple)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Language](https://img.shields.io/badge/语言-简体中文-red)

## ✨ 特色

- **🎭 中文 COC 跑团流程**：支持模型担任 Keeper，和用户进行短团、单人团、即兴调查与剧情续跑。
- **📝 7 版车卡辅助**：生成 STR/CON/SIZ/DEX/APP/INT/POW/EDU，计算 HP、SAN、MP、Luck、MOV、Build、DB，并提供角色卡模板。
- **🎲 标准 D100 检定**：支持普通检定、奖励骰、惩罚骰、对抗检定、SAN 损失、伤害计算。
- **⚙️ 更稳的骰子实现**：支持 `1d4-1`、`1d6+1d4` 等 COC 常见骰式；D100 按十位骰 + 个位骰处理，正确识别 `00+0=100`。
- **🕯️ Keeper 友好**：内置“不剧透真相”“关键线索不被单次检定卡死”“失败推进局势”等跑团原则。
- **🧭 行动选项循环**：每次场景推进、玩家行动结算或 NPC 互动后，默认给出 2-4 个可行动选项，同时保留自由行动。
- **🎭 暗骰与 SAN 策略**：支持隐藏侦察、心理学、灵感、POW 等暗骰；SAN 检定可按场景选择公开、隐藏或延迟公开。
- **🧰 轻量无依赖**：Python 脚本仅使用标准库，不需要额外安装第三方包。

## 📦 项目结构

```text
coc-trpg-skill/
├── SKILL.md                         # Skill 入口与使用规则
├── README.md                         # 本文件
├── LICENSE                           # MIT 许可证
├── scripts/
│   ├── dice.py                       # 骰子、检定、SAN、伤害、技能点
│   ├── random_name.py                # 随机姓名生成
│   └── random_encounter.py           # 随机遭遇生成
├── templates/
│   ├── character_sheet.md            # COC 7 版角色卡模板
│   ├── scenario_outline.md           # 模组/剧本大纲模板
│   ├── npc_card.md                   # NPC 数据卡模板
│   ├── background_table.md           # D100 背景表
│   └── pregens.md                    # 预设调查员
├── characters/
│   └── README.md                     # 角色卡保存目录说明
├── scenarios/
│   └── README.md                     # 模组保存目录说明
└── npcs/
    └── README.md                     # NPC 保存目录说明
```

## 🚀 安装

### 作为 Codex Skill 安装

```bash
git clone https://github.com/<your-username>/coc-trpg-skill.git \
  ~/.codex/skills/coc-trpg-skill
```

重启或刷新 Codex 后，在对话里输入：

```text
克总发糖
```

即可打开 COC 菜单。

### 手动安装

将整个 `coc-trpg-skill/` 文件夹复制到 Codex skills 目录：

```text
~/.codex/skills/coc-trpg-skill/
```

## 🎮 使用示例

```text
克总发糖
```

```text
你当 Keeper，带我跑一个 1920 年代、2 小时内能结束的 COC 短团。
```

```text
帮我车一张 1920 年代私家侦探卡，偏调查和心理学。
```

```text
生成一个现代都市怪谈 COC 模组，地点在福州，3 名调查员，普通难度。
```

```text
我要做侦察检定，技能 55，有 1 个奖励骰。
```

```text
生成 5 个 1920 年代美国 NPC 姓名，再给 3 个城市随机遭遇。
```

## 🐙 交互菜单

输入 `克总发糖`、`COC菜单` 或 `COC帮助` 时，Skill 会展示：

```text
克总发糖 - COC TRPG 助手
[1] 🎭 开始跑团 / 继续剧情
[2] 📝 车卡 / 生成调查员
[3] 📜 快速预设角色
[4] 🏚️ 撰写模组 / 场景
[5] 🎩 生成 NPC
[6] 🎲 投骰 / 技能检定 / SAN
[7] 🧰 规则速查 / Keeper 工具箱
```

用户只回复数字时，模型会直接进入对应流程。

## 🛠️ 脚本工具

### `scripts/dice.py`

```bash
# 生成 COC 7 版基础属性与派生值
python scripts/dice.py --coc-stats

# 快速生成预设调查员
python scripts/dice.py --pregen

# D100 技能检定
python scripts/dice.py --check 50
python scripts/dice.py --check 50 --bonus 1
python scripts/dice.py --check 50 --penalty 1

# 重复检定并统计成功数
python scripts/dice.py --check 50 --repeat 5

# 对抗检定
python scripts/dice.py --opposed 60 45

# 通用骰式，支持加减与组合骰
python scripts/dice.py --roll "1d4-1"
python scripts/dice.py --roll "1d6+1d4"
python scripts/dice.py --roll "2d6+6" --repeat 3

# SAN 损失
python scripts/dice.py --san-check 60 1d6

# 伤害计算：武器伤害 + DB
python scripts/dice.py --damage 1d10+2 1d4

# 技能点计算：EDU 职业指定属性 INT
python scripts/dice.py --skill-calc 70 60 65 --credit 20
```

### `scripts/random_name.py`

```bash
# 1920 年代美国姓名
python scripts/random_name.py --era 1920s --region us --count 5

# 中文姓名
python scripts/random_name.py --era 1920s --region cn --count 5

# 指定性别
python scripts/random_name.py --era 1890s --gender female --count 3
```

### `scripts/random_encounter.py`

```bash
# 1920 年代城市遭遇
python scripts/random_encounter.py --era 1920s --type urban --count 3

# 1920 年代乡村遭遇
python scripts/random_encounter.py --era 1920s --type rural --count 3

# 现代城市遭遇
python scripts/random_encounter.py --era modern --type urban --count 3
```

## 🎯 D100 规则说明

本 Skill 默认采用 COC 7 版常见判定：

| 结果 | 判定 |
|---|---|
| 01 | 大成功 Critical |
| <= 技能值 / 5 | 极难成功 Extreme |
| <= 技能值 / 2 | 困难成功 Hard |
| <= 技能值 | 常规成功 Regular |
| > 技能值 | 失败 |
| 技能值 < 50 时 96-100；技能值 >= 50 时 100 | 大失败 Fumble |

奖励骰与惩罚骰互相抵消，只取净值。D100 使用十位骰和个位骰组合，`00 + 0` 视为 `100`。

## 🕯️ Keeper 使用原则

- 不提前泄露 Keeper Only 真相。
- 每次描述新场景、回应 NPC、结算玩家行动或检定后，都给出 2-4 个具体可行动选项，并允许玩家自由行动。
- 关键线索至少准备 3 条路径，不让剧情卡在一次失败检定上。
- 检定失败应带来代价、风险或局势变化，而不是直接让故事停止。
- 遇到血腥、身体恐怖、宗教敏感或精神崩溃内容时，先给玩家简短提醒，并允许淡化处理。

### 行动选项循环

跑团时默认每轮输出：

1. 当前状况
2. 已知线索
3. A/B/C/D 可选行动
4. “你也可以做其他行动”

选项不是固定路线，玩家可以随时提出自由行动。模型会优先响应玩家行动，再结算后果并给出下一组选择。

### 暗骰与 SAN

- **公开检定**：开锁、追逐、战斗、说服、跳跃、公开阅读禁书等玩家明确知道自己在尝试的行动。
- **暗骰**：侦察暗处、聆听远处动静、心理学识破谎言、灵感发现矛盾、POW/CON 抵抗隐性影响等公开检定会暴露隐藏信息的情况。
- **公开 SAN**：角色直观看到尸体、怪物、仪式、严重超自然现象或身体恐怖。
- **隐藏 SAN**：梦境、记忆篡改、潜意识污染、不可见神话影响、现实错位等不应提前暴露来源的情况。
- **延迟公开 SAN**：影响已发生，但在真相揭露或场景结束时再统一结算，以保留悬疑。

## 📄 模板文件

| 文件 | 用途 |
|---|---|
| `templates/character_sheet.md` | 完整调查员角色卡 |
| `templates/scenario_outline.md` | Keeper 版模组大纲 |
| `templates/npc_card.md` | 路人、配角、核心 NPC 数据卡 |
| `templates/background_table.md` | D100 背景关键词表 |
| `templates/pregens.md` | 预设调查员库 |

## 📌 依赖

- Python 3.8+
- 无第三方依赖

## 🧭 适用范围

本项目适合：

- 想和模型进行中文 COC 单人跑团的玩家
- 需要快速车卡、生成 NPC、构建场景的 Keeper
- 需要一个轻量骰子与随机遭遇工具的 COC 桌面团
- 想把 COC 辅助流程封装成 Agent Skill 的用户

本项目不包含《克苏鲁的呼唤》官方规则书全文，也不替代正式规则书。规则细节存在争议时，以你的桌面规则或官方资料为准。

## 🤝 贡献

欢迎提交改进：

- 增加职业、预设调查员或背景表
- 扩展随机姓名库与随机遭遇库
- 优化角色卡、NPC 卡、模组模板
- 修正 COC 7 版规则细节
- 增加更多时代支持，如煤气灯、现代、民国、本土城市背景

## ⚖️ 许可证

本项目采用 [MIT License](LICENSE)。

你可以自由使用、复制、修改、合并、发布、分发、再授权或出售本项目的副本，但需要在副本或主要部分中保留原始许可证与版权声明。

本项目按“原样”提供，不附带任何明示或暗示担保。作者不对使用本项目产生的任何损失、索赔或责任负责。完整条款请查看 [LICENSE](LICENSE) 文件。

## ⚠️ 免责声明

- 本项目是面向桌面角色扮演游戏的非官方辅助工具，不隶属于 Chaosium Inc.、Call of Cthulhu 官方出版方或任何相关权利方。
- “Call of Cthulhu”“克苏鲁的呼唤”等名称及相关商标、规则体系、世界观版权归其各自权利人所有。本项目仅作为玩家与 Keeper 的辅助工具使用。
- 本项目不包含官方规则书全文，也不替代正式规则书。规则争议、角色创建细节、战斗流程和出版物内容请以官方资料或你的桌面规则为准。
- 本项目可能生成恐怖、血腥、精神崩溃、身体恐怖、宗教敏感、暴力或其他令人不适的虚构内容。使用前请与玩家确认内容边界，建议采用 X-Card、Lines & Veils 等安全工具。
- 脚本中的随机结果仅用于游戏娱乐，不应用于现实决策、赌博、抽奖或任何需要可审计随机性的场景。
- AI 生成的剧情、规则解释、NPC、模组和角色卡可能存在错误、遗漏或不符合某一版本规则的情况。公开发布或正式开团前，建议由 Keeper 人工复核。
- 如果你将本项目生成的内容公开发布、商业使用或改编为其他作品，请自行确认其版权、授权和平台规则风险。
