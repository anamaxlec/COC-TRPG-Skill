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
- **☁️ GitHub 存档**：使用独立私有仓库保存完整团档，支持换机恢复、覆盖前备份和多设备冲突处理，也支持使用自己的 fork。
- **🎩 NPC 与模组模板**：支持公开身份、隐藏动机、线索、误导点、逼问反应和离场替代方案。
- **📚 现成剧本库**：内置《古城诡秘》三个中文剧本的原 PDF 与分篇文本，另有四个 Chaosium 官方免费模组入口，支持无剧透选本、按原作备团与续跑。
- **🧰 轻量无依赖**：Python 脚本仅使用标准库。

## 🆕 更新说明 · 2026-10-10

- 跑团叙事减少固定菜单与重复提示，按场景需要给行动切口，保留玩家决定权。
- 修复续团摘要滞后、隐藏线索更新后可见性变化，以及已解决事项仍进入待办的问题。
- SAN 支持单次损失后的 INT 检定和按游戏日累计损失判定不定疯狂；修正 MOV、普通对抗同级比较与预设角色技能点分配。
- 新增 [GitHub 团档同步](#github-存档独立私有仓库)：使用独立私有仓库保存进度，支持换机恢复、覆盖前备份与多设备冲突处理。
- 新增 [剧本库](#-剧本库)：内置《古城诡秘》三个中文剧本的原 PDF 与分篇文本，并提供四个 Chaosium 官方免费模组入口。
- 对抗检定在成功等级与技能值均相同时自动投决胜骰，并显示每轮结果。
- 续团提示区分公开接续与 Keeper 安排，回顾分别列出玩家调查员与同行者；重命名导入存档时同步更新摘要中的团名。
- 主持流程细化 NPC 等待回应的停顿、跨回合叙事变化与玩家行动对原作后续事件的影响。
- 新增 [主持对话评估工具](tests/keeper_evals/README.md)，支持按固定场景生成回复、独立评分与保存评估记录。

## v2 记忆系统

本版本重建了长期跑团记忆系统，重点保证续团时能恢复当前场景、调查员状态、线索网络、NPC 动向、未结算事项、威胁时钟和 Keeper Only 真相。

- **新的 v2 结构**：记忆拆分为 `meta`、`current`、`journal`、`state`、`clues`、`threads`、`clocks` 和 `summaries`，既保留事件流水，也沉淀当前可用状态。
- **自动沉淀命令**：新增 `record`、`set-current`、`entity`、`clue`、`thread`、`clock`、`snapshot`，方便 Agent 在关键节点自动写入，而不是只追加松散文本。
- **玩家/Keeper 隔离**：默认 `recall` 只输出玩家可知摘要；只有 `--keeper` 才会显示幕后真相、暗骰、隐藏 SAN 和敌方行动。
- **跨平台数据目录**：macOS/Linux 默认写入 `~/.codex/data/coc-trpg-skill`，Windows 默认写入 `%APPDATA%\coc-trpg-skill`，避免把长期团资料混进 skill 安装目录。
- **旧数据归档**：旧 v1 的 `scenarios/` 和 `saves/` 不自动迁移，可用 `python scripts/memory.py archive-legacy` 复制到归档目录。

## 📦 项目结构

```text
coc-trpg-skill/
├── SKILL.md
├── README.md
├── scripts/
│   ├── dice.py
│   ├── memory.py
│   ├── github_memory.py
│   ├── keeper_eval.py
│   ├── random_name.py
│   └── random_encounter.py
├── references/
│   ├── keeper_style.md
│   ├── memory_playbook.md
│   ├── github_memory.md
│   ├── checks_and_san.md
│   ├── scenario_library.md
│   ├── scenario_design.md
│   └── character_npc.md
├── assets/
│   └── scenarios/ancient-city/   # 原 PDF、分篇文本与许可说明
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
├── tests/
│   └── keeper_evals/            # 主持对话场景与运行说明
└── npcs/
```

## 🚀 安装

个人安装，对所有项目可用：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/anamaxlec/COC-TRPG-Skill.git ~/.agents/skills/coc-trpg-skill
```

项目安装，在目标项目根目录执行：

```bash
mkdir -p .agents/skills
git clone https://github.com/anamaxlec/COC-TRPG-Skill.git .agents/skills/coc-trpg-skill
```

也可以下载仓库并将文件夹放入相应目录，目录中直接包含 `SKILL.md`。目录约定见 [Codex 官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills)。

Codex 加载 skill 后输入：

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

## 📚 剧本库

输入“剧本库”或“推荐一个现成剧本”，先看无剧透介绍，再选择开团。

内置 **MasterNoah（诺亚城主）** 的《古城诡秘》合集：

| 剧本 | 题材 | 原作人数 / 预计时长 |
|---|---|---|
| 校园黑色怪谈 | 现代校园、失踪调查 | 3–6 人 / 3–8 小时 |
| 深埋地底的呼唤 | 地铁施工、古墓探索 | 3–6 人 / 2–4 小时 |
| 可曾遇见梦中仙境 | 山庄度假、梦境解谜 | 2–4 人 / 3–6 小时 |

这三个剧本可按顺序连跑，单人游玩由 KP 调整遭遇与技能覆盖。正文随仓库提供，包含原 PDF、可直接读取的分篇文本和按页定位的备团入口。地图、展示材料与表格保留在原 PDF 中。

```text
打开剧本库，先不要剧透。
你当 KP，带我们跑《校园黑色怪谈》，使用原作真相和线索。
我想一个人玩，帮我选适合单人的现成剧本。
```

另提供 **Alone Against the Flames、The Dead Boarder、The Lightless Beacon、The Haunting** 的 [Chaosium 官方免费入口](https://www.chaosium.com/cthulhu-adventures/)。选择后从官方来源获取正文，其中 **Alone Against the Flames** 是按编号段落推进的单人冒险。

使用现成剧本时，Skill 会先读取所选剧本的真相、线索与结局，再根据调查员背景准备导入。长团存档记录剧本来源、当前场景、已发现线索与本团调整；下次说“继续《团名》”，即可从存档位置续跑。

完整目录和读取方式见 [剧本库](references/scenario_library.md)。中文合集按 **CC BY-NC-SA 4.0** 收录，须署名、非商业使用，改编采用相同许可；详见 [来源与许可](assets/scenarios/ancient-city/NOTICE.md)。

## 🐙 交互菜单

输入 `克总发糖`、`COC菜单` 或 `COC帮助` 时，Skill 会展示：

```text
克总发糖 - COC TRPG 助手
[1] 🎭 开始跑团 / 继续剧情
[2] 📝 车卡 / 生成调查员
[3] 📜 快速预设角色
[4] 🏚️ 挑选剧本 / 撰写模组
[5] 🎩 生成 NPC
[6] 🎲 投骰 / 技能检定 / SAN
[7] 🧰 规则速查 / Keeper 工具箱
[8] 💾 存档 / 读档 / 导入导出
```

用户只回复数字时，引用最近一次仍有效的菜单或行动选项。

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

`--pregen` 内置主题职业：私家侦探、记者、医生、教授、古董商、警员、民俗研究者、罪犯。技能在基础值上按职业与兴趣点数分配，Keeper 可继续按所选职业、年龄和时代完善角色卡与装备。

新增的 SAN 参数用于一起结算理智损失、INT 检定与本游戏日的累计损失：

```bash
python scripts/dice.py --san-check 51 0/1d6 --int 65 --day-start-san 60 --lost-today 9
```

此例中调查员当前 SAN 为 51、INT 为 65、日初 SAN 为 60，本次检定前已累计损失 9 点。`--lost-today` 填写本次之前的累计损失；换游戏日时更新日初 SAN 并重置累计值。

### `scripts/memory.py`

```bash
# 创建 v2 跑团记忆
python scripts/memory.py init \
  --name "榕渊" \
  --era "modern" \
  --location "福州" \
  --scene "旧仓山洋楼" \
  --characters "林知远" \
  --style "平衡 Keeper"

# 自动沉淀关键状态
python scripts/memory.py record --name "榕渊" --visibility public --kind scene --text "调查员进入旧仓山洋楼。"
python scripts/memory.py record --name "榕渊" --visibility keeper --kind note --text "墙内有未公开的仪式残留。"
python scripts/memory.py entity --name "榕渊" --type investigator --entity "林知远" --status "HP 12 SAN 50" --public "携带相机和旧报纸"
python scripts/memory.py clue --name "榕渊" --id C-001 --text "二层门把手有潮湿手印" --source "洋楼二层" --points-to "有人刚离开" --visibility public
python scripts/memory.py thread --name "榕渊" --type unresolved --visibility keeper --text "延迟公开 SAN 1 点" --next "真相揭露时结算"
python scripts/memory.py clock --name "榕渊" --clock "仪式推进" --progress "1/4" --next "调查员拖延时推进"

# 续团、快照、导入导出
python scripts/memory.py recall --name "榕渊" --keeper
python scripts/memory.py snapshot --name "榕渊"
python scripts/memory.py load --file "saves/<存档名>.cocsave.json"
```

`memory.py` 默认数据目录：macOS/Linux 为 `~/.codex/data/coc-trpg-skill`，Windows 为 `%APPDATA%\coc-trpg-skill`。可用 `COC_TRPG_DATA_DIR` 或 `--data-dir` 覆盖。旧 v1 `scenarios/` 和 `saves/` 可用 `python scripts/memory.py archive-legacy` 归档。

下一轮提示分别保存玩家已知的接续入口与 Keeper 幕后安排：

```bash
python scripts/memory.py set-current --name "榕渊" \
  --public-hook "调查员停在二层门口，门内传来脚步声" \
  --keeper-hook "馆长正在门内销毁最后一封信"
```

普通 `recall` 展示公开接续提示，`recall --keeper` 同时读取幕后安排。旧 `--hook` 继续作为 Keeper 安排参数使用。

### 随机素材

```bash
python scripts/random_name.py --era 1920s --region cn --count 5
python scripts/random_encounter.py --era modern --type urban --count 3
```

随机姓名脚本只负责姓名素材；复杂 NPC 建议按 `templates/npc_card.md` 由模型生成。

### GitHub 存档：独立私有仓库

安装 skill 后，在 GitHub 创建一个独立私有仓库，例如 `COC-Saves`，并配置好 Git 身份与仓库访问权限。团档保存到该仓库的 `coc-saves` 分支，包含玩家进度、Keeper 信息与内容边界，可见性跟随目标仓库。

在 skill 目录执行以下命令，将 `你的用户名` 替换为实际 GitHub 用户名：

```bash
# 配置自己的存档仓库
python scripts/github_memory.py init --repo 你的用户名/COC-Saves
python scripts/github_memory.py status

# 按上方 memory.py 示例建团后，上传当前进度
python scripts/github_memory.py push --name "榕渊" --include-keeper

# 新电脑配置相同仓库后，列出并恢复进度
python scripts/github_memory.py list
python scripts/github_memory.py pull --name "榕渊"
python scripts/memory.py recall --name "榕渊" --keeper
```

也可以直接对 Agent 说：

```text
把《榕渊》的完整团档上传到我的私有仓库“你的用户名/COC-Saves”。
```

```text
从我的 GitHub 存档库恢复《榕渊》，接着上次的场景继续。
```

本地保存使用 `memory.py snapshot`，云端同步使用 `github_memory.py push`。换机时先配置相同仓库，再下载团档。SSH、同名团档替换、备份恢复与冲突处理见 [GitHub 存档手册](references/github_memory.md)。

希望公开分享完整团档时，也可以 [fork 本项目](https://github.com/anamaxlec/COC-TRPG-Skill/fork)，将同步目标改为自己的 fork。公开 fork 中的团档及 Keeper 信息对外可见。

## 📄 模板与参考

| 文件 | 用途 |
|---|---|
| `references/keeper_style.md` | KP 风格、短输入处理、自定义风格 |
| `references/memory_playbook.md` | v2 记忆触发、续团、自动写入命令 |
| `references/github_memory.md` | 私有仓库存档、上传下载、换机与冲突处理 |
| `references/checks_and_san.md` | D100、暗骰、SAN |
| `references/scenario_library.md` | 内置剧本、官方免费入口、无剧透选本与原作备团 |
| `references/scenario_design.md` | 模组、场景节点、线索网 |
| [tests/keeper_evals/README.md](tests/keeper_evals/README.md) | 主持对话评估的场景与运行方法 |
| `references/character_npc.md` | 车卡、职业、NPC |
| `templates/keeper_style_profile.md` | 玩家自定义 KP 风格档案 |
| `templates/npc_card.md` | 路人、配角、核心 NPC 数据卡 |
| `templates/character_sheet.md` | 完整调查员角色卡 |
| `templates/scenario_outline.md` | Keeper 版模组大纲 |

## 📌 依赖

- Python 3.8+
- 无第三方依赖
- 可选 GitHub 同步需要 Git，以及目标仓库的现有认证与写入权限

## 🧭 适用范围

适合中文 COC 单人团、短团、Keeper 备团、快速车卡、NPC 生成和长期团续跑。规则采用 COC 7 版，开团时可以约定本团房规。

## ⚖️ 许可证

本项目代码和自有文档采用 [MIT License](LICENSE)。`assets/scenarios/ancient-city/` 内的第三方剧本及文本转换版本采用 **CC BY-NC-SA 4.0**；作者、来源和改动说明见 [NOTICE.md](assets/scenarios/ancient-city/NOTICE.md)。
