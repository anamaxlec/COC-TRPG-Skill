# COC TRPG Skill 🐙🎲

> 面向中文玩家的《克苏鲁的呼唤》（Call of Cthulhu）第 7 版跑团助手：Keeper 主持、车卡、投骰、SAN、NPC、模组大纲、长期记忆与可迁移存档。

[![Codex Skill](https://img.shields.io/badge/Codex-Skill-blue)](https://openai.com/codex)
![COC 7th](https://img.shields.io/badge/COC-7th%20Edition-purple)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Language](https://img.shields.io/badge/语言-简体中文-red)

## ✨ 特色

- **🎭 中文 COC 跑团流程**：支持模型担任 Keeper，适合单人团、短团、即兴调查和长期续跑。
- **🕯️ KP 风格协议**：内置平衡 Keeper、剧情沉浸、规则教学，也支持玩家保存自定义 KP 风格。
- **📝 更可用的车卡**：`--pregen` 可按时代、职业、地区生成 Markdown 调查员卡，包含背景钩子、弱点和关系钩子。
- **🎲 标准 D100 工具**：支持技能检定、奖励骰、惩罚骰、对抗检定、SAN 损失、伤害和技能点计算。
- **🧠 跑团记忆系统**：记录玩家可知内容、Keeper Only 信息、剧本连续性、未结算事项和下一轮开场钩子。
- **💾 可迁移存档**：导出 `.cocsave.json` 单文件存档，换电脑后可导入继续。
- **🎩 NPC 与模组模板**：支持公开身份、隐藏动机、线索、误导点、逼问反应和离场替代方案。
- **🧰 轻量无依赖**：Python 脚本仅使用标准库。

## 📦 项目结构

```text
coc-trpg-skill/
├── SKILL.md
├── README.md
├── scripts/
│   ├── dice.py
│   ├── memory.py
│   ├── random_name.py
│   └── random_encounter.py
├── references/
│   ├── keeper_style.md
│   ├── memory_playbook.md
│   ├── checks_and_san.md
│   ├── scenario_design.md
│   └── character_npc.md
├── templates/
│   ├── character_sheet.md
│   ├── npc_card.md
│   ├── scenario_outline.md
│   ├── campaign_memory.md
│   ├── cast_anchor.md
│   ├── keeper_style_profile.md
│   └── pregens.md
├── characters/
├── scenarios/
├── saves/
└── npcs/
```

## 🚀 安装

```bash
git clone https://github.com/anamaxlec/COC-TRPG-Skill.git ~/.codex/skills/coc-trpg-skill
```

或把整个 `coc-trpg-skill/` 文件夹复制到：

```text
~/.codex/skills/coc-trpg-skill/
```

重启或刷新 Codex 后输入：

```text
克总发糖
```

即可打开 COC 菜单。

## 🎮 使用示例

```text
你当 Keeper，带我跑一个现代都市怪谈 COC 短团。
```

```text
切到剧情沉浸
```

```text
使用我的 KP 风格：慢热调查，少讲规则，隐藏信息允许暗骰，身体恐怖淡化。
```

```text
帮我车一张现代中国记者调查员卡，输出 Markdown。
```

```text
我要做侦察检定，技能 55，有 1 个奖励骰。
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
[8] 💾 存档 / 读档 / 导入导出
```

用户只回复数字时，模型会直接进入对应流程。

## 🛠️ 脚本工具

### `scripts/dice.py`

```bash
# D100 技能检定
python scripts/dice.py --check 50
python scripts/dice.py --check 50 --bonus 1
python scripts/dice.py --opposed 60 45

# 通用骰式、SAN 和伤害
python scripts/dice.py --roll "1d6+1d4"
python scripts/dice.py --san-check 60 0/1d6
python scripts/dice.py --damage 1d10+2 1d4

# 车卡与技能点
python scripts/dice.py --coc-stats
python scripts/dice.py --skill-calc 70 60 65 --credit 20
python scripts/dice.py --pregen --era modern --occupation 记者 --region cn --format markdown
```

`--pregen` 内置职业：私家侦探、记者、医生、教授、古董商、警员、民俗研究者、罪犯。

### `scripts/memory.py`

```bash
# 创建新跑团记忆
python scripts/memory.py init \
  --name "榕渊" \
  --era "modern" \
  --location "福州" \
  --characters "林知远" \
  --style "平衡 Keeper"

# 保存 KP 风格和下一轮开场钩子
python scripts/memory.py set --name "榕渊" --field style --value "玩家自定义：慢热、少讲规则、暗骰优先"
python scripts/memory.py set --name "榕渊" --field hook --value "从旧仓山洋楼二层的潮湿手印继续"

# 追加未结算事项
python scripts/memory.py add --name "榕渊" --section unresolved --text "延迟公开 SAN 1 点，真相揭露时结算"

# 续团、存档、读档
python scripts/memory.py recall --name "榕渊" --keeper
python scripts/memory.py save --name "榕渊"
python scripts/memory.py load --file "saves/<存档名>.cocsave.json"
```

### 随机素材

```bash
python scripts/random_name.py --era 1920s --region cn --count 5
python scripts/random_encounter.py --era modern --type urban --count 3
```

随机姓名脚本只负责姓名素材；复杂 NPC 建议按 `templates/npc_card.md` 由模型生成。

## 📄 模板与参考

| 文件 | 用途 |
|---|---|
| `references/keeper_style.md` | KP 风格、短输入处理、自定义风格 |
| `references/memory_playbook.md` | 记忆触发、续团、存档前检查 |
| `references/checks_and_san.md` | D100、暗骰、SAN |
| `references/scenario_design.md` | 模组、场景节点、线索网 |
| `references/character_npc.md` | 车卡、职业、NPC |
| `templates/keeper_style_profile.md` | 玩家自定义 KP 风格档案 |
| `templates/npc_card.md` | 路人、配角、核心 NPC 数据卡 |
| `templates/character_sheet.md` | 完整调查员角色卡 |
| `templates/scenario_outline.md` | Keeper 版模组大纲 |

## 📌 依赖

- Python 3.8+
- 无第三方依赖

## 🧭 适用范围

适合中文 COC 单人团、短团、Keeper 备团、快速车卡、NPC 生成和长期团续跑。本项目不包含官方规则书全文，也不替代正式规则书。规则细节存在争议时，以你的桌面规则或官方资料为准。

## ⚖️ 许可证

本项目采用 [MIT License](LICENSE)。

## ⚠️ 免责声明

- 本项目是面向桌面角色扮演游戏的非官方辅助工具，不隶属于 Chaosium Inc.、Call of Cthulhu 官方出版方或任何相关权利方。
- “Call of Cthulhu”“克苏鲁的呼唤”等名称及相关商标、规则体系、世界观版权归其各自权利人所有。
- 本项目不包含官方规则书全文，也不替代正式规则书。
- 脚本中的随机结果仅用于游戏娱乐，不应用于现实决策、赌博、抽奖或任何需要可审计随机性的场景。
- AI 生成的剧情、规则解释、NPC、模组和角色卡可能存在错误，正式开团或公开发布前建议由 Keeper 人工复核。
