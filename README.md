# COC TRPG Skill

> 面向中文玩家的《克苏鲁的呼唤》（Call of Cthulhu）第 7 版跑团助手：车卡、投骰、SAN、NPC、模组大纲与 Keeper 辅助。

[![Codex Skill](https://img.shields.io/badge/Codex-Skill-blue)](https://openai.com/codex)
![COC 7th](https://img.shields.io/badge/COC-7th%20Edition-purple)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Language](https://img.shields.io/badge/语言-简体中文-red)

## 特色

- **中文 COC 跑团流程**：支持模型担任 Keeper，和用户进行短团、单人团、即兴调查与剧情续跑。
- **7 版车卡辅助**：生成 STR/CON/SIZ/DEX/APP/INT/POW/EDU，计算 HP、SAN、MP、Luck、MOV、Build、DB，并提供角色卡模板。
- **标准 D100 检定**：支持普通检定、奖励骰、惩罚骰、对抗检定、SAN 损失、伤害计算。
- **更稳的骰子实现**：支持 `1d4-1`、`1d6+1d4` 等 COC 常见骰式；D100 按十位骰 + 个位骰处理，正确识别 `00+0=100`。
- **Keeper 友好**：内置“不剧透真相”“关键线索不被单次检定卡死”“失败推进局势”等跑团原则。
- **轻量无依赖**：Python 脚本仅使用标准库，不需要额外安装第三方包。

## 项目结构

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
├── characters/                       # 生成角色卡保存目录
├── scenarios/                        # 生成模组保存目录
└── npcs/                             # 生成 NPC 保存目录
```

## 安装

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

## 使用示例

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

## 交互菜单

输入 `克总发糖`、`COC菜单` 或 `COC帮助` 时，Skill 会展示：

```text
克总发糖 - COC TRPG 助手
[1] 开始跑团 / 继续剧情
[2] 车卡 / 生成调查员
[3] 快速预设角色
[4] 撰写模组 / 场景
[5] 生成 NPC
[6] 投骰 / 技能检定 / SAN
[7] 规则速查 / Keeper 工具箱
```

用户只回复数字时，模型会直接进入对应流程。

## 脚本工具

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

## D100 规则说明

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

## Keeper 使用原则

- 不提前泄露 Keeper Only 真相。
- 每个场景给出可行动选择，但允许玩家自由行动。
- 关键线索至少准备 3 条路径，不让剧情卡在一次失败检定上。
- 检定失败应带来代价、风险或局势变化，而不是直接让故事停止。
- 遇到血腥、身体恐怖、宗教敏感或精神崩溃内容时，先给玩家简短提醒，并允许淡化处理。

## 模板文件

| 文件 | 用途 |
|---|---|
| `templates/character_sheet.md` | 完整调查员角色卡 |
| `templates/scenario_outline.md` | Keeper 版模组大纲 |
| `templates/npc_card.md` | 路人、配角、核心 NPC 数据卡 |
| `templates/background_table.md` | D100 背景关键词表 |
| `templates/pregens.md` | 预设调查员库 |

## 依赖

- Python 3.8+
- 无第三方依赖

## 适用范围

本项目适合：

- 想和模型进行中文 COC 单人跑团的玩家
- 需要快速车卡、生成 NPC、构建场景的 Keeper
- 需要一个轻量骰子与随机遭遇工具的 COC 桌面团
- 想把 COC 辅助流程封装成 Agent Skill 的用户

本项目不包含《克苏鲁的呼唤》官方规则书全文，也不替代正式规则书。规则细节存在争议时，以你的桌面规则或官方资料为准。

## 贡献

欢迎提交改进：

- 增加职业、预设调查员或背景表
- 扩展随机姓名库与随机遭遇库
- 优化角色卡、NPC 卡、模组模板
- 修正 COC 7 版规则细节
- 增加更多时代支持，如煤气灯、现代、民国、本土城市背景

## 许可证

[MIT License](LICENSE)
