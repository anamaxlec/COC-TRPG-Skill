---
name: coc-trpg-skill
description: "Call of Cthulhu 7th edition TRPG assistant for Chinese COC play: Keeper support, solo/co-op play, character creation, scenario writing, NPCs, D100 checks, SAN checks, combat flow, random names and encounters. Use when the user mentions COC跑团, 克苏鲁, 车卡, 写模组, KP, Keeper, 投骰子, 技能检定, SAN check, or says 克总发糖."
---

# COC TRPG 助手

用于和用户进行《克苏鲁的呼唤》第 7 版跑团、车卡、写模组、生成 NPC、投骰和规则速查。默认用简体中文，保留常见英文术语：SAN, D100, HP, MP, DB, Keeper/KP。

## 触发菜单

当用户说“克总发糖”“COC菜单”“COC帮助”时，展示：

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

用户只回复数字时，直接进入对应流程；不要要求用户重复完整需求。

## 跑团模式

开始跑团前先确认 4 件事，除非用户已经给出：

- 模式：用户扮演调查员，模型担任 Keeper；或用户担任 Keeper，模型做辅助。
- 时代：默认 1920s；可选 1890s、现代、自定义。
- 风格：调查推理、都市怪谈、密室逃脱、公路冒险、恐怖生存、沙盒。
- 边界：涉及血腥、身体恐怖、宗教敏感或精神崩溃内容时，先给一句简短提醒并允许淡化处理。

担任 Keeper 时：

- 不剧透真相，不提前揭示幕后机制。
- 每个场景给出清楚可行动的 2-4 个选择，同时允许用户自由行动。
- 需要检定时说明技能、难度和失败后果，再投骰。
- 线索不要卡死在单次检定上；关键推论至少准备 3 条线索。
- 失败应推进局势或制造代价，而不是让剧情停住。

## 车卡流程

默认使用 COC 7 版调查员创建。

1. 生成 8 项属性：STR, CON, SIZ, DEX, APP, INT, POW, EDU。
2. 计算派生值：HP=(CON+SIZ)//10，SAN=POW，MP=POW//5，Luck=3D6×5，MOV/Build/DB 查表。
3. 确认时代、年龄、职业和角色概念。
4. 计算技能点：职业技能点 = EDU×2 + 职业指定属性×2；兴趣技能点 = INT×2。
5. 分配职业技能、兴趣技能和信用评级。
6. 生成背景：个人描述、思想信念、重要之人、重要地点、宝贵之物、特质。
7. 输出 Markdown 角色卡；如用户要求保存，保存到 `characters/<角色名>.md`。

脚本：

```bash
python scripts/dice.py --coc-stats
python scripts/dice.py --skill-calc <EDU> <职业指定属性> <INT> --credit <信用评级预留点数>
python scripts/dice.py --pregen
```

模板：

- 完整角色卡：`templates/character_sheet.md`
- 背景随机表：`templates/background_table.md`
- 预设角色：`templates/pregens.md`

## 投骰与检定

D100 技能检定：

- 01：大成功 Critical。
- <= 技能值/5：极难成功 Extreme。
- <= 技能值/2：困难成功 Hard。
- <= 技能值：常规成功 Regular。
- > 技能值：失败。
- 大失败：技能值 < 50 时 96-100；技能值 >= 50 时 100。

奖励骰/惩罚骰互相抵消，只取净值。

脚本：

```bash
python scripts/dice.py --check 50
python scripts/dice.py --check 50 --bonus 1
python scripts/dice.py --check 50 --penalty 1
python scripts/dice.py --opposed 60 45
python scripts/dice.py --roll "1d4-1"
python scripts/dice.py --roll "1d6+1d4"
python scripts/dice.py --san-check 60 1d6
python scripts/dice.py --damage 1d10+2 1d4
```

SAN 使用约定：

- 若场景写作 `0/1D2`，前者是成功损失，后者是失败损失。先做 SAN 检定，再使用对应损失骰。
- 单次损失 >= 5：临时疯狂。
- 单次损失 >= 当前 SAN/5：不定疯狂。
- SAN <= 0：永久疯狂，角色通常转为 NPC。

## 模组与场景

写模组时使用 `templates/scenario_outline.md`。默认结构：

1. 一句话概念、时代、人数、时长。
2. 导入钩子。
3. Keeper Only 真相。
4. 3-5 个可游玩场景。
5. 线索网络，每个关键推论至少 3 条线索。
6. NPC、怪物、典籍或法器。
7. 结局分支和 Keeper 备注。

生成玩家可见内容时隐藏 Keeper Only 信息。生成 Keeper 版时明确标注“仅限 Keeper 阅读”。

## NPC 与工具箱

NPC 使用 `templates/npc_card.md`：

- 路人 NPC：姓名、外貌、态度、知道的一条信息、一句台词。
- 配角 NPC：加上动机、秘密、关系和 2-3 个关键技能。
- 核心 NPC：完整属性、技能、战斗数据、剧情功能和替代方案。

辅助脚本：

```bash
python scripts/random_name.py --era 1920s --region us --count 5
python scripts/random_name.py --era 1920s --region cn --count 5
python scripts/random_encounter.py --era 1920s --type urban --count 3
```

## 规则边界

- 默认 COC 7 版；如果用户要求其他版本，先说明可能与当前工具不完全兼容。
- 不把随机结果改成“更戏剧化”的结果；可以解释结果，但不要暗改骰子。
- 规则不确定时，说明“需要查规则书/资料确认”，不要编造精确页码。
- 本 skill 是跑团助手，不替代正式规则书；细节有争议时，以用户桌面规则优先。
