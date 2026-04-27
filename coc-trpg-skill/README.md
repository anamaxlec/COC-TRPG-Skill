# COC TRPG Skill

《克苏鲁的呼唤》第 7 版中文跑团助手，用于和模型一起跑 COC、车卡、写模组、生成 NPC、投骰和做规则速查。

## 安装到 Codex

将整个目录复制到 Codex skills 目录：

```bash
/Users/max333/.codex/skills/coc-trpg-skill/
```

安装后可以说：

- `克总发糖`
- `帮我车一张 1920 年代私家侦探卡`
- `你当 Keeper，带我跑一个 2 小时 COC 短团`
- `帮我写一个现代都市怪谈 COC 模组`

## 包含内容

```text
coc-trpg-skill/
├── SKILL.md
├── scripts/
│   ├── dice.py
│   ├── random_name.py
│   └── random_encounter.py
├── templates/
│   ├── character_sheet.md
│   ├── scenario_outline.md
│   ├── npc_card.md
│   ├── background_table.md
│   └── pregens.md
├── characters/
├── scenarios/
└── npcs/
```

## 常用脚本

```bash
# 属性批量生成
python scripts/dice.py --coc-stats

# 技能检定
python scripts/dice.py --check 50 --bonus 1

# 通用骰式，支持加减和组合骰
python scripts/dice.py --roll "1d4-1"
python scripts/dice.py --roll "1d6+1d4"

# SAN 损失
python scripts/dice.py --san-check 60 1d6

# 技能点计算：EDU 职业指定属性 INT
python scripts/dice.py --skill-calc 70 60 65 --credit 20

# 快速预设角色
python scripts/dice.py --pregen

# 随机姓名 / 遭遇
python scripts/random_name.py --era 1920s --region cn --count 5
python scripts/random_encounter.py --era 1920s --type urban --count 3
```

## 依赖

- Python 3.8+
- 无第三方依赖

## 说明

默认使用 COC 7 版规则。具体桌面规则存在争议时，以用户指定规则优先。
