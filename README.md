# COC TRPG Skill 🐙🎲

> **让 AI 成为你的《克苏鲁的呼唤》Keeper。**
>
> 面向中文玩家的 Call of Cthulhu 第 7 版 Agent Skill：支持 AI 主持跑团、自由行动、车卡与检定、现成剧本、长期记忆，以及可迁移的本地与 GitHub 团档。

[![Codex Skill](https://img.shields.io/badge/Codex-Agent%20Skill-blue)](https://developers.openai.com/codex/skills)
![COC 7th](https://img.shields.io/badge/COC-7th%20Edition-purple)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Language](https://img.shields.io/badge/语言-简体中文-red)

你可以直接描述调查员想做的事情，由 AI Keeper 扮演 NPC、呈现场景、处理规则并记录故事。适用于单人团、即兴调查、短团和跨会话长期战役。玩家始终掌握调查员的台词、行动与决定权。

## ✨ 主要功能

- **🎭 自由行动与 Keeper 主持**：自然语言推进调查；NPC 等待玩家回答时及时停下，不替玩家作出决定。支持平衡、剧情沉浸、规则教学三种风格及自定义 KP 风格。
- **🎲 COC 7e 骰子工具**：D100 技能检定、奖励/惩罚骰、普通对抗、SAN、伤害与属性生成。实际骰点由 Python 脚本产生。
- **📝 调查员与 NPC**：按时代、职业、地区生成预设角色草稿，提供人物背景、弱点、关系钩子和 NPC / 模组模板。
- **🧠 v2 长团记忆**：分别记录玩家已知信息和 Keeper 幕后内容，持续维护场景、角色状态、线索、未结算事项与威胁时钟。
- **💾 本地与 GitHub 团档**：导出单文件 `.cocsave.json`；可选通过私有 GitHub 仓库换机恢复、备份与处理多设备冲突。
- **📚 现成剧本库**：内置《古城诡秘》三篇中文模组的原 PDF 与分篇文本，另提供四篇 Chaosium 官方免费模组入口。
- **🧪 主持对话评估**：使用固定场景检查 NPC 互动、玩家行动权、隐藏信息隔离和续团一致性。

## 🆕 2026-10-10 更新

本轮更新集中在 **主持体验、规则准确性、长团连续性和跨设备存档**。

**主持与剧情**
- 减少每轮固定菜单及重复提示，根据场景提供行动切口；自由行动始终有效。
- NPC 向调查员提问、等待表态或邀请回应时，Keeper 必须停下交给玩家回答；加强跨回合叙事变化和模组事件的因果连续性。
- 现成剧本按原作真相与线索备团，玩家行动可以改变后续事件，但不随意重写已确定的真相。

**检定与角色**
- 修复普通对抗双方成功等级、技能值相同时的处理：追加 D100 决胜骰并显示每轮结果；决胜重复同点最多处理 10 轮，再交由 Keeper 裁定。
- SAN 结算支持单次损失达到 5 点后的 INT 检定，以及根据游戏日初 SAN 和当日累计损失判断不定疯狂。
- 修正 MOV 计算、对抗同级比较和预设角色技能点分配。

**记忆与续团**
- 修复状态修改后摘要滞后、隐藏线索可见性更新、已解决事项仍进入待办等问题。
- 将下一轮提示拆为**玩家可见的公开接续**和 **Keeper 幕后安排**；回顾时区分调查员与同行者。
- 旧 `--hook` 兼容为 Keeper 专用提示；重命名导入存档时重新生成对应摘要。

**剧本、同步与评估**
- 新增《古城诡秘》中文剧本库及四篇 Chaosium 官方免费模组的获取入口。
- 新增 GitHub 团档同步：优先使用独立私有仓库，支持跨设备恢复、覆盖前备份与冲突阻止。
- 新增 [Keeper 对话评估工具](tests/keeper_evals/README.md)，可准备固定场景、保存实际回复和独立评分结果。

## 🚀 快速开始

### 1. 安装

需要 **Python 3.8+**；运行本地骰子与记忆工具无须第三方 Python 依赖。

个人安装（对所有 Codex 项目可用），在 macOS / Linux 终端执行：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/anamaxlec/COC-TRPG-Skill.git ~/.agents/skills/coc-trpg-skill
```

Windows PowerShell：

```powershell
git clone https://github.com/anamaxlec/COC-TRPG-Skill.git "$env:USERPROFILE\.agents\skills\coc-trpg-skill"
```

只在特定项目中使用时，进入项目根目录后安装：

```bash
mkdir -p .agents/skills
git clone https://github.com/anamaxlec/COC-TRPG-Skill.git .agents/skills/coc-trpg-skill
```

也可以下载仓库并将文件夹复制到对应目录，确保目录中直接包含 `SKILL.md`。安装位置以 [Codex Skills 文档](https://developers.openai.com/codex/skills) 为准。已有安装可在 Skill 目录运行 `git pull --ff-only` 更新；如未识别新 Skill，请刷新或重新启动 Codex。

### 2. 唤醒 Keeper

在 Codex 中输入：

```text
克总发糖
```

或直接提出需求：

```text
你当 Keeper，带我跑一个发生在 1990 年代中国南方小城的 COC 单人团。
希望慢热调查、小说式叙事，规则解释简短，不要替我决定调查员的行动。
```

Keeper 会按已有信息直接推进开团；只有缺少关键设置时才确认。进入场景后，你可以自由描述动作，例如：

```text
我先不进去，站在门外听听屋子里的动静。
```

不需要每回合从菜单选一个动作。

### 3. 常用指令

```text
切到剧情沉浸。
使用我的 KP 风格：自然长段落、慢热调查、少给固定选项，NPC 问话后等我回答。
帮我车一张现代中国记者调查员卡，输出 Markdown。
打开剧本库，先不要剧透。
继续《榕渊》，从上次的场景接着跑。
```

## 🕯️ Keeper 主持协议

默认使用**平衡 Keeper** 风格，可随时切换：

| 风格 | 主持特点 |
|---|---|
| 平衡 Keeper | 叙事与规则适度结合，按需要给出行动切口 |
| 剧情沉浸 | 增加场景、人物与环境细节，降低规则说明频率 |
| 规则教学 | 解释关键检定、成功等级与后果，适合新玩家 |

也可以直接描述自己的风格并保存。风格只影响叙事和信息呈现，不会修改骰子结果、NPC 隐藏动机或剧本真相。

Keeper 每轮先结算玩家已声明的行动，再描述可感知的变化，并在下一个需要玩家决定的时刻停下。NPC 提问后不会自动替调查员答话。检定只用于结果不确定且失败有实际影响的行动；核心推论保留替代线索路径，失败仍可能带来时间、危险或机会成本。

具体约定参见 [KP 风格](references/keeper_style.md)、[检定与 SAN](references/checks_and_san.md) 和 [模组设计](references/scenario_design.md)。

## 📚 剧本库

输入“剧本库”或“推荐一个现成剧本”可先获得**无剧透介绍**。确定剧本后，Keeper 再按需读取原作正文与幕后资料；没有取得正文时，不会仅凭简介声称在主持原作。

### 内置中文模组：《古城诡秘》

作者：**MasterNoah（诺亚城主）**

| 剧本 | 题材 | 原作人数 | 预计时长 |
|---|---|---|---|
| 校园黑色怪谈 | 校园失踪、现代怪谈 | 3–6 人 | 3–8 小时 |
| 深埋地底的呼唤 | 地铁施工、古墓调查 | 3–6 人 | 2–4 小时 |
| 可曾遇见梦中仙境 | 山庄度假、梦境解谜 | 2–4 人 | 3–6 小时 |

三篇剧本处于同一现代中国背景，可按顺序连跑。仓库收录原 PDF、逐篇 Markdown 文本以及按页定位的 Keeper 阅读入口；地图、展示材料和表格以原 PDF 为准。

这些都是多人模组。单人游玩时，Keeper 会调整遭遇与技能覆盖，并在团档中记录本团改编。

```text
打开剧本库，先不要剧透。
你当 KP，带我跑《校园黑色怪谈》，沿用原作真相和线索。
```

### Chaosium 官方免费模组

| 模组 | 适合的体验 | 官方入口 |
|---|---|---|
| Alone Against the Flames | 原生单人冒险、规则入门 | [PDF](https://www.chaosium.com/content/FreePDFs/CoC/Adventures/CHA23145%20-%20Alone%20Against%20the%20Flames.pdf) |
| The Dead Boarder | 面向新玩家的短篇体验 | [PDF](https://www.chaosium.com/content/FreePDFs/CoC/Cult%20of%20Chaos%20Scenarios/Dead%20Boarder.pdf) |
| The Lightless Beacon | 灯塔主题的短篇调查 | [官方目录](https://www.chaosium.com/cthulhu-adventures/) |
| The Haunting | Quick-Start 内的入门调查 | [Quick-Start PDF](https://www.chaosium.com/content/FreePDFs/CoC/CHA23131%20Call%20of%20Cthulhu%207th%20Edition%20Quick-Start%20Rules.pdf) |

上述英文模组**仅提供官方入口，仓库不收录正文**。其中 `Alone Against the Flames` 按编号段落推进，应遵循原作跳转与选择结构。

详见 [剧本库与读取方式](references/scenario_library.md)。中文合集的第三方授权见 [来源与许可](assets/scenarios/ancient-city/NOTICE.md)。

## 🧠 长期记忆 v2

长期战役需要记住哪些事件已经发生、人物现在在哪里、哪些线索已经揭露，以及尚未兑现的幕后后果。本项目将这些内容保存为结构化记忆，而非依赖完整对话历史。

| 模块 | 内容 |
|---|---|
| `meta` / `current` | 团名、调查员、游戏时间、地点、场景与接续信息 |
| `journal` | 已发生的事件与玩家决定 |
| `state` | 调查员、NPC、地点和物品的当前状态 |
| `clues` | 线索、来源、关键推论和替代路径 |
| `threads` / `clocks` | 未解决问题、延迟结算、伏笔及威胁进度 |
| `summaries` | 玩家可知摘要、Keeper 摘要与场景摘要 |

Agent 可以在关键事件后使用脚本更新记忆，不必每一轮普通叙事都写入。

### 创建与继续战役

以下命令在 Skill 根目录执行：

```bash
# 建立团档
python scripts/memory.py init \
  --name "榕渊" \
  --era modern \
  --location "福州" \
  --scene "旧仓山洋楼" \
  --characters "林知远" \
  --style "平衡 Keeper"

# 查看当前团档（Keeper 信息用于幕后恢复，不应直接贴给玩家）
python scripts/memory.py recall --name "榕渊" --keeper

# 导出单文件快照
python scripts/memory.py snapshot --name "榕渊"
```

普通 `recall` 只输出玩家可知摘要；加上 `--keeper` 才输出幕后信息、暗骰和隐藏事件。下一轮接续也明确区分可见范围：

```bash
python scripts/memory.py set-current --name "榕渊" \
  --public-hook "调查员停在二层门口，听到房内传来脚步声" \
  --keeper-hook "馆长正在门内销毁最后一封信"
```

`--public-hook` 用于玩家可见的接续，`--keeper-hook` 仅用于幕后主持；旧版 `--hook` 仍可使用，但视作 Keeper 专用提示。

角色数值、线索、NPC 行动和未结算事件分别由 `entity`、`clue`、`record`、`thread`、`clock` 等命令维护。详细例子见 [v2 记忆与续团手册](references/memory_playbook.md)。

### 存档、导入与数据目录

`snapshot` 导出 `.cocsave.json` 文件，用于备份与迁移。需要导入时：

```bash
python scripts/memory.py load --file "/path/to/save.cocsave.json"
```

默认数据目录：

| 系统 | 路径 |
|---|---|
| macOS / Linux | `~/.codex/data/coc-trpg-skill` |
| Windows | `%APPDATA%\coc-trpg-skill` |

可通过 `COC_TRPG_DATA_DIR` 或 `--data-dir` 更改。旧 v1 的 `scenarios/`、`saves/` 不自动迁移，可执行 `python scripts/memory.py archive-legacy` 复制到归档目录。

**注意**：玩家与 Keeper 信息隔离用于控制回顾输出，并不对本地文件加密。直接打开完整团档仍能看到幕后内容。

## ☁️ GitHub 团档同步（可选）

建议建立一个**独立私有 GitHub 仓库**（例如 `yourname/COC-Saves`），用于保存完整团档。同步使用目标仓库的 `coc-saves` 分支，不会把团档提交到本 Skill 的 `main` 分支。

在 GitHub 创建好私有仓库，并配置 Git 提交身份与访问权限后：

```bash
# 配置目标仓库（仅本地配置，不会创建或上传远程仓库）
python scripts/github_memory.py init --repo yourname/COC-Saves
python scripts/github_memory.py status

# 上传指定团的完整存档
python scripts/github_memory.py push --name "榕渊" --include-keeper

# 在新设备配置同一仓库后恢复
python scripts/github_memory.py list
python scripts/github_memory.py pull --name "榕渊"
python scripts/memory.py recall --name "榕渊" --keeper
```

`--include-keeper` 表示明确允许上传包含幕后秘密的完整团档。Agent 只有在用户授权目标仓库和上传范围后才可以同步；普通“存档”仍只保存本地。

已有同名本地团档时，`pull` 默认停止。确认采用云端进度后，可使用 `--replace-local`，脚本会在覆盖前生成本地备份。同步也会检测同团远端变化，冲突时拒绝擅自覆盖，不执行强推或自动剧情合并。

也可以使用自己的 [fork](https://github.com/anamaxlec/COC-TRPG-Skill/fork)，但**公开 fork 的所有分支均可被访问**，包括 `coc-saves` 中的完整 Keeper 秘密；提交历史也不会因为删除当前文件而自动消失。私密团应使用私有仓库。

目前同步的是结构化团档，外部图片、模组 PDF 和角色附件不会自动上传。SSH、备份恢复与冲突处理参见 [GitHub 存档手册](references/github_memory.md)。

## 🐙 交互菜单

输入 `克总发糖`、`COC菜单` 或 `COC帮助`：

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

数字只关联最近一次仍有效的菜单或选项；自然语言动作优先。

## 🛠️ Python 工具速查

在 Skill 根目录执行：

```bash
# D100、奖励骰、普通对抗
python scripts/dice.py --check 55
python scripts/dice.py --check 55 --bonus 1
python scripts/dice.py --opposed 60 45

# 通用骰式、SAN 与伤害
python scripts/dice.py --roll "1d6+1d4"
python scripts/dice.py --san-check 60 0/1d6
python scripts/dice.py --san-check 51 0/1d6 --int 65 --day-start-san 60 --lost-today 9
python scripts/dice.py --damage 1d10+2 1d4

# 属性、技能点和预设调查员
python scripts/dice.py --coc-stats
python scripts/dice.py --skill-calc 70 60 65 --credit 20
python scripts/dice.py --pregen --era modern --occupation 记者 --region cn --format markdown

# 随机素材
python scripts/random_name.py --era 1920s --region cn --count 5
python scripts/random_encounter.py --era modern --type urban --count 3
```

SAN 示例中的 `--lost-today 9` 指**本次检定前**已经损失的 SAN；跨游戏日需更新 `--day-start-san` 并重置累计值。脚本负责给出骰点和结算结果，**不会自动修改团档中的调查员数值**。

`--pregen` 提供记者、医生、教授、警员、私家侦探、古董商、民俗研究者和罪犯等主题职业。生成的是已按预算分配技能点的**角色草稿**；正式职业技能表、年龄调整和装备仍需核对。

## 🧪 测试与 Keeper 行为评估

运行 Python 单元测试：

```bash
python -m unittest discover -s tests -v
```

测试覆盖骰子规则、记忆状态、存档与 GitHub 冲突处理等；GitHub 同步相关测试需要本机安装 Git，并使用本地测试仓库，不上传真实团档。

Keeper 的实际主持表现单独评估：

```bash
# 创建独立的评估输入
python scripts/keeper_eval.py prepare --output-dir /tmp/coc-keeper-eval

# 在填入被测回复和评分文件后生成报告
python scripts/keeper_eval.py report --output-dir /tmp/coc-keeper-eval
```

这套评估覆盖 NPC 提问时停顿、隐藏信息、失败后果、玩家改变事件、续团连续性和叙事重复等场景。评估需使用模型实际生成的回复，并独立给出评分和具体依据；`prepare` 本身不代表模型已经接受测试，也不会自动给出通过结论。

支持接收 stdin、输出 stdout 的模型命令时，也可使用 `keeper_eval.py run --runner ... --judge ...` 执行。详见 [Keeper 对话评估说明](tests/keeper_evals/README.md)。

## 📦 项目结构

```text
coc-trpg-skill/
├── SKILL.md                 # Skill 入口、触发与主持协议
├── scripts/
│   ├── dice.py              # 骰子、SAN、角色草稿
│   ├── memory.py            # v2 长期记忆与存档
│   ├── github_memory.py     # GitHub 同步
│   ├── keeper_eval.py       # 主持对话评估
│   ├── random_name.py
│   └── random_encounter.py
├── references/              # KP、规则、记忆、剧本等按需加载的文档
├── templates/               # 调查员、NPC、模组与风格模板
├── assets/scenarios/
│   └── ancient-city/        # 《古城诡秘》原 PDF、分篇文本、许可说明
├── tests/
│   └── keeper_evals/        # 固定评估场景及使用说明
├── characters/              # 旧版输出目录（运行数据已迁出）
├── npcs/
├── scenarios/
└── saves/
```

常用参考文档：

| 文档 | 用途 |
|---|---|
| [keeper_style.md](references/keeper_style.md) | KP 风格、NPC 互动与叙事节奏 |
| [checks_and_san.md](references/checks_and_san.md) | D100、对抗、暗骰与 SAN |
| [memory_playbook.md](references/memory_playbook.md) | 结构化记忆、续团与数据写入 |
| [github_memory.md](references/github_memory.md) | 私有仓库同步、冲突和备份 |
| [scenario_library.md](references/scenario_library.md) | 内置模组及官方免费入口 |
| [scenario_design.md](references/scenario_design.md) | 场景节点、线索网与威胁时钟 |
| [character_npc.md](references/character_npc.md) | 车卡和 NPC |
| [character_sheet.md](templates/character_sheet.md) | 调查员模板 |
| [npc_card.md](templates/npc_card.md) | NPC 数据卡 |
| [scenario_outline.md](templates/scenario_outline.md) | 模组大纲 |

## 📌 使用边界

- 默认遵循《克苏鲁的呼唤》第 7 版；可另行约定房规，但脚本不保证覆盖所有变体，也不替代正式规则书。
- 只有能够执行 Python 脚本的环境才能实际运行骰子和记忆工具；无法执行时应请玩家自行投骰，不能编造随机结果或声称已经保存。
- 角色草稿需要进一步核对正式职业规则；现成模组需先取得原作正文。
- 单人团可针对原作的多人遭遇与技能覆盖进行适配，变动应写入本团记忆。

## ⚖️ 许可证

本项目自有代码与文档采用 [MIT License](LICENSE)。

`assets/scenarios/ancient-city/` 中的《古城诡秘》原作及文本转换版本遵循 **CC BY-NC-SA 4.0**，须保留署名、遵守非商业使用与相同方式共享要求。作者、来源和转换说明参见 [NOTICE.md](assets/scenarios/ancient-city/NOTICE.md)。Chaosium 官方免费模组仅提供原始获取入口，仓库没有重新分发其正文。

本项目是独立社区工具，与 Chaosium 无官方关联。
