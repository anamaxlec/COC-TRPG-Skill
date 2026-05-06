#!/usr/bin/env python3
"""
COC 7版 骰子与预设调查员工具
支持：D100检定、属性生成、武器伤害、SAN检定、对抗检定、快速车卡。
"""
import argparse
import random
import re

RNG = random.SystemRandom()

BUILD_TABLE = {
    (2, 64): (-2, "-2"),
    (65, 84): (-1, "-1"),
    (85, 124): (0, "0"),
    (125, 164): (1, "1D4"),
    (165, 204): (2, "1D6"),
    (205, 284): (3, "2D6"),
    (285, 364): (4, "3D6"),
}

OCCUPATIONS = {
    "私家侦探": {
        "attr": ["教育 EDU", "智力 INT", "敏捷 DEX"],
        "credit": (20, 50),
        "skills": ["侦察", "心理学", "图书馆使用", "法律", "话术", "乔装", "格斗(斗殴)", "艺术/手艺(摄影)"],
        "concepts": ["被旧案拖住的私家侦探", "接手失踪委托的调查员", "前警探转行的事务所老板"],
        "hooks": ["委托人失踪后只留下一张奇怪收据", "旧案证人突然寄来一封空信", "警方拒绝重开案件"],
    },
    "记者": {
        "attr": ["教育 EDU", "外貌 APP"],
        "credit": (9, 30),
        "skills": ["图书馆使用", "母语", "心理学", "侦察", "历史", "魅惑", "说服", "艺术/手艺(写作)"],
        "concepts": ["追查地方怪谈的记者", "被停职后独自查案的调查记者", "专写社会新闻的报社新人"],
        "hooks": ["一篇旧报道被人从档案中撕掉", "匿名线人只约在午夜见面", "主编要求压下这条新闻"],
    },
    "医生": {
        "attr": ["教育 EDU"],
        "credit": (30, 80),
        "skills": ["急救", "医学", "心理学", "科学(生物)", "图书馆使用", "侦察", "说服", "外语(拉丁语)"],
        "concepts": ["接连见到异常病症的医生", "被病人遗言卷入事件的外科医生", "研究梦游症的精神科医生"],
        "hooks": ["病人的伤口不像任何已知器械造成", "同一症状在不同城区同时出现", "病历被医院高层调走"],
    },
    "教授": {
        "attr": ["教育 EDU"],
        "credit": (20, 70),
        "skills": ["图书馆使用", "母语", "神秘学", "心理学", "科学(考古)", "说服", "历史", "外语(拉丁语)"],
        "concepts": ["研究禁忌文本的大学教授", "被学生求救信惊动的学者", "追索失窃文物的考古学者"],
        "hooks": ["学生在论文注释里留下求救暗号", "馆藏书页出现不属于原版的插图", "校方要求停止研究"],
    },
    "古董商": {
        "attr": ["教育 EDU", "外貌 APP"],
        "credit": (30, 70),
        "skills": ["估价", "历史", "图书馆使用", "侦察", "神秘学", "魅惑", "外语(阿拉伯语)", "艺术/手艺(修复)"],
        "concepts": ["买到问题藏品的古董商", "替客户鉴定遗物的中间人", "熟悉黑市流通的修复师"],
        "hooks": ["一件赝品拥有真实年代的污痕", "客户要求午夜后交货", "修复夹层里藏着陌生地图"],
    },
    "警员": {
        "attr": ["教育 EDU", "力量 STR", "敏捷 DEX"],
        "credit": (9, 30),
        "skills": ["法律", "侦察", "聆听", "心理学", "格斗(斗殴)", "枪械(手枪)", "急救", "恐吓"],
        "concepts": ["被边缘化的辖区警员", "负责怪案现场封锁的巡警", "不相信官方结论的刑警"],
        "hooks": ["现场记录和尸检报告互相矛盾", "上级要求把案子定性为事故", "嫌疑人说出了只有警员知道的细节"],
    },
    "民俗研究者": {
        "attr": ["教育 EDU", "智力 INT"],
        "credit": (10, 40),
        "skills": ["人类学", "历史", "图书馆使用", "神秘学", "聆听", "侦察", "外语(地方方言)", "说服"],
        "concepts": ["追访地方传说的民俗研究者", "整理家族禁忌记录的归乡者", "研究祭祀遗存的田野调查者"],
        "hooks": ["一段童谣和近期失踪案完全吻合", "村里老人突然集体改口", "旧仪式记录缺了最后一页"],
    },
    "罪犯": {
        "attr": ["教育 EDU", "敏捷 DEX"],
        "credit": (5, 65),
        "skills": ["潜行", "锁匠", "格斗(斗殴)", "乔装", "侦察", "聆听", "枪械(手枪)", "电气维修"],
        "concepts": ["被迫替人取回禁物的窃贼", "想洗白却被旧同伙拖回泥潭的人", "熟悉地下渠道的骗子"],
        "hooks": ["目标房间里有人早已等着他", "雇主付的钱带着新鲜血迹", "保险柜里只有一张写着自己名字的纸"],
    },
}

CN_NAMES = ["林知远", "陈绍安", "许明岚", "周若衡", "郑秋白", "何静姝", "陆文渊", "唐思柔"]
US_NAMES = ["James Carter", "Helen Ward", "Arthur Blackwood", "Ruth Morgan", "Walter Reed", "Edith Sinclair"]

WEAKNESSES = ["失眠", "容易冲动", "害怕封闭空间", "过度共情", "债务压力", "对旧案有执念", "不信任权威"]
RELATIONS = ["旧友", "导师", "前任", "失踪者家属", "债主", "同事", "房东", "病人"]
HOBBY_SKILLS = ["侦察", "聆听", "潜行", "急救", "心理学", "图书馆使用", "闪避", "话术", "驾驶"]


def roll(die_str):
    """投掷 XdY、XdY+Z、XdY-Z、XdY+AdB 或纯数字格式。"""
    expr = die_str.strip().replace(" ", "")
    if not expr:
        raise ValueError("骰式不能为空")

    total = 0
    for sign, token in re.findall(r"([+-]?)([^+-]+)", expr):
        factor = -1 if sign == "-" else 1
        dice_match = re.fullmatch(r"(\d*)[dD](\d+)", token)
        if dice_match:
            count = int(dice_match.group(1) or 1)
            sides = int(dice_match.group(2))
            if count <= 0 or sides <= 0:
                raise ValueError(f"骰子数量和面数必须为正数: {token}")
            value = sum(RNG.randint(1, sides) for _ in range(count))
        elif token.isdigit():
            value = int(token)
        else:
            raise ValueError(f"不支持的骰式: {die_str}")
        total += factor * value
    return total


def d100_value(tens, ones):
    """把一颗十位骰和一颗个位骰转换为 COC 百分骰结果。"""
    if tens == 0 and ones == 0:
        return 100
    return tens * 10 + ones


def roll_d100(net_bonus=0):
    """投 COC D100。net_bonus > 0 为奖励骰，< 0 为惩罚骰。"""
    tens = [RNG.randint(0, 9) for _ in range(abs(net_bonus) + 1)]
    ones = RNG.randint(0, 9)
    candidates = [(d100_value(t, ones), t) for t in tens]

    if net_bonus > 0:
        result, selected_tens = min(candidates, key=lambda item: item[0])
    elif net_bonus < 0:
        result, selected_tens = max(candidates, key=lambda item: item[0])
    else:
        result, selected_tens = candidates[0]

    return result, {
        "tens": [t * 10 for t in tens],
        "ones": ones,
        "selected_tens": selected_tens * 10,
    }


def d100_check(skill, bonus=0, penalty=0):
    """D100 技能检定。"""
    net = bonus - penalty
    result, detail = roll_d100(net)
    if net > 0:
        rolls = [f"奖励骰 {net}: tens={detail['tens']}, ones={detail['ones']}, selected_tens={detail['selected_tens']}"]
    elif net < 0:
        rolls = [f"惩罚骰 {abs(net)}: tens={detail['tens']}, ones={detail['ones']}, selected_tens={detail['selected_tens']}"]
    else:
        rolls = [f"D100: tens={detail['tens'][0]}, ones={detail['ones']}"]

    if result == 1:
        level = "大成功 CRITICAL"
    elif result <= skill // 5:
        level = "极难成功 EXTREME"
    elif result <= skill // 2:
        level = "困难成功 HARD"
    elif result <= skill:
        level = "常规成功 REGULAR"
    elif result >= 96 and skill < 50:
        level = "大失败 FUMBLE"
    elif result == 100:
        level = "大失败 FUMBLE"
    else:
        level = "失败 FAIL"
    return result, level, rolls


def is_success(level):
    return any(tag in level for tag in ("CRITICAL", "EXTREME", "HARD", "REGULAR"))


def opposed_check(skill_a, skill_b):
    """D100 对抗检定，返回 A vs B 的结果。"""
    ra, la, _ = d100_check(skill_a)
    rb, lb, _ = d100_check(skill_b)
    order = {"CRITICAL": 5, "EXTREME": 4, "HARD": 3, "REGULAR": 2, "FAIL": 1, "FUMBLE": 0}
    score_a = next(score for tag, score in order.items() if tag in la)
    score_b = next(score for tag, score in order.items() if tag in lb)

    if score_a > score_b:
        win = "A"
    elif score_b > score_a:
        win = "B"
    else:
        win = "平局 DRAW"
    return ra, la, rb, lb, win


def generate_stats():
    """生成8项COC基础属性与派生值。"""
    stats = {
        "力量 STR": roll("3D6") * 5,
        "体质 CON": roll("3D6") * 5,
        "体型 SIZ": roll("2D6+6") * 5,
        "敏捷 DEX": roll("3D6") * 5,
        "外貌 APP": roll("3D6") * 5,
        "智力 INT": roll("2D6+6") * 5,
        "意志 POW": roll("3D6") * 5,
        "教育 EDU": roll("2D6+6") * 5,
    }
    con = stats["体质 CON"]
    siz = stats["体型 SIZ"]
    str_ = stats["力量 STR"]
    dex = stats["敏捷 DEX"]
    pow_ = stats["意志 POW"]

    mov = 7
    if dex < siz and str_ < siz:
        mov -= 1
    if dex > siz and str_ > siz:
        mov += 1

    total_str_siz = str_ + siz
    build = 0
    db = "0"
    for (lo, hi), (b, d) in BUILD_TABLE.items():
        if lo <= total_str_siz <= hi:
            build = b
            db = d
            break
    if total_str_siz > 364:
        build = 5
        db = "4D6"

    return {
        **stats,
        "生命值 HP": (con + siz) // 10,
        "理智值 SAN": pow_,
        "魔力值 MP": pow_ // 5,
        "幸运 Luck": roll("3D6") * 5,
        "移动力 MOV": mov,
        "体格 Build": build,
        "伤害加值 DB": db,
    }


def parse_san_loss(current_san, loss_expr):
    """支持 legacy 单损失骰，也支持 0/1d6 格式。"""
    if "/" not in loss_expr:
        return None, None, loss_expr, roll(loss_expr), []

    success_loss, fail_loss = [part.strip() for part in loss_expr.split("/", 1)]
    result, level, info = d100_check(current_san)
    selected = success_loss if is_success(level) else fail_loss
    return result, level, selected, roll(selected), info


def san_check(current_san, loss_expr):
    """SAN 检定与疯狂判定。"""
    check_result, level, selected_expr, loss, info = parse_san_loss(current_san, loss_expr)
    new_san = current_san - loss
    output = []
    if check_result is not None:
        output.append(f"SAN 检定: {check_result} -> {level}")
        for item in info:
            output.append(f"检定细节: {item}")
        output.append(f"损失格式: {loss_expr}，本次采用: {selected_expr}")
    output.append(f"SAN 损失: {loss} (投骰: {selected_expr})")
    output.append(f"SAN 变化: {current_san} -> {new_san}")

    if loss >= 5:
        output.append("单次损失 >= 5 -> 临时疯狂 (1D10 小时)")
        output.append(f"疯狂表现: D10 = {RNG.randint(1, 10)} (查临时疯狂表)")
    if current_san > 0 and loss >= current_san // 5:
        output.append("单次损失 >= SAN/5 -> 不定疯狂 (持续到剧情解决)")
    if new_san <= 0:
        output.append("SAN 归零 -> 永久疯狂 (角色通常转为 NPC)")
    return loss, new_san, output


def damage_roll(weapon_dmg, db_str):
    """武器伤害 + DB 计算。"""
    wd = roll(weapon_dmg)
    db = roll(db_str) if db_str and db_str != "0" else 0
    return wd, db, wd + db


def skill_points(edu, occupation_attr, int_value, credit=0):
    """计算职业技能点与兴趣技能点。occupation_attr 是职业指定属性值。"""
    occupation = edu * 2 + occupation_attr * 2
    hobby = int_value * 2
    return occupation, hobby, max(occupation - credit, 0)


def pick_occupation(name):
    if name and name in OCCUPATIONS:
        return name, OCCUPATIONS[name], False
    if name:
        fallback = "民俗研究者"
        return fallback, OCCUPATIONS[fallback], True
    occ_name = RNG.choice(list(OCCUPATIONS))
    return occ_name, OCCUPATIONS[occ_name], False


def choose_name(region):
    return RNG.choice(CN_NAMES if region == "cn" else US_NAMES)


def score_skill(base=25, spread=45):
    return min(85, base + RNG.randint(0, spread))


def pregen_character(era="1920s", occupation="", region="us"):
    """快速生成可直接开团的预设调查员。"""
    stats = generate_stats()
    occ_name, occ, used_fallback = pick_occupation(occupation)
    attr_value = max(stats[attr] for attr in occ["attr"])
    credit = RNG.randint(*occ["credit"])
    occupation_points, hobby_points, spendable = skill_points(stats["教育 EDU"], attr_value, stats["智力 INT"], credit)

    skills = {skill: score_skill(35, 40) for skill in occ["skills"]}
    for skill in RNG.sample(HOBBY_SKILLS, 3):
        skills[skill] = max(skills.get(skill, 0), score_skill(25, 35))
    skills["信用评级"] = credit
    skills["闪避"] = max(skills.get("闪避", 0), stats["敏捷 DEX"] // 2 + RNG.randint(0, 20))

    concept = RNG.choice(occ["concepts"])
    hook = RNG.choice(occ["hooks"])
    weakness = RNG.choice(WEAKNESSES)
    relation = RNG.choice(RELATIONS)

    return {
        "name": choose_name(region),
        "era": era,
        "region": region,
        "occupation": occ_name,
        "occupation_fallback": used_fallback,
        "stats": stats,
        "occupation_points": occupation_points,
        "hobby_points": hobby_points,
        "spendable_occupation_points": spendable,
        "credit": credit,
        "occupation_skills": occ["skills"],
        "skills": dict(sorted(skills.items())),
        "concept": concept,
        "hook": hook,
        "weakness": weakness,
        "relation_hook": relation,
        "keeper_entry": f"{hook}；{relation}可以作为第一幕联系人或失踪者家属。",
    }


def format_pregen_text(character):
    lines = ["══════════ 快速预设调查员 ══════════"]
    if character["occupation_fallback"]:
        lines.append("  提示: 指定职业不在内置表，已用 民俗研究者 作为底座。")
    lines.extend([
        f"  姓名        : {character['name']}",
        f"  时代        : {character['era']}",
        f"  职业        : {character['occupation']}",
        f"  核心概念    : {character['concept']}",
        f"  背景钩子    : {character['hook']}",
        f"  弱点        : {character['weakness']}",
        f"  关系钩子    : {character['relation_hook']}",
        "  --- 属性 ---",
    ])
    lines.extend(f"  {k:12s}: {v}" for k, v in character["stats"].items())
    lines.extend([
        "  --- 技能 ---",
        f"  职业技能点  : {character['occupation_points']} (信用评级 {character['credit']} 后可分配 {character['spendable_occupation_points']})",
        f"  兴趣技能点  : {character['hobby_points']}",
    ])
    lines.extend(f"  {k:12s}: {v}%" for k, v in character["skills"].items())
    lines.append(f"  Keeper 接入 : {character['keeper_entry']}")
    lines.append("════════════════════════════════════")
    return "\n".join(lines)


def format_pregen_markdown(character):
    fallback = "\n> 指定职业不在内置表，已用“民俗研究者”作为底座，需要 Keeper 人工微调。\n" if character["occupation_fallback"] else ""
    stats_rows = "\n".join(f"| {k} | {v} | {v // 2 if isinstance(v, int) else ''} | {v // 5 if isinstance(v, int) else ''} |" for k, v in character["stats"].items())
    skills_rows = "\n".join(f"| {k} | {v}% | {v // 2}% | {v // 5}% |" for k, v in character["skills"].items())
    occ_skills = "、".join(character["occupation_skills"])
    return f"""# {character['name']} - COC 7版预设调查员
{fallback}
## 基础信息

| 项目 | 内容 |
|---|---|
| 时代 | {character['era']} |
| 地区 | {character['region']} |
| 职业 | {character['occupation']} |
| 核心概念 | {character['concept']} |
| 背景钩子 | {character['hook']} |
| 弱点 | {character['weakness']} |
| 关系钩子 | {character['relation_hook']} |

## 属性

| 属性 | 值 | 半值 | 五分之一 |
|---|---:|---:|---:|
{stats_rows}

## 技能点

| 项目 | 数值 |
|---|---:|
| 职业技能点 | {character['occupation_points']} |
| 信用评级预留 | {character['credit']} |
| 可分配职业技能点 | {character['spendable_occupation_points']} |
| 兴趣技能点 | {character['hobby_points']} |

职业技能建议：{occ_skills}

## 已分配技能建议

| 技能 | 值 | 半值 | 五分之一 |
|---|---:|---:|---:|
{skills_rows}

## Keeper 接入

- {character['keeper_entry']}
- 可把“{character['relation_hook']}”设为第一幕联系人、委托人、目击者或失踪者关联人。
- 可用“{character['weakness']}”作为压力场景或 SAN 后续表现的触发点。
"""


def main():
    parser = argparse.ArgumentParser(description="COC 7版 骰子与预设调查员工具")
    parser.add_argument("--roll", help="投骰公式 (如 2d6+6, 3d6, 1d100)")
    parser.add_argument("--repeat", type=int, default=1, help="重复次数")
    parser.add_argument("--check", type=int, help="D100 技能检定 (提供技能值)")
    parser.add_argument("--bonus", type=int, default=0, help="奖励骰数量")
    parser.add_argument("--penalty", type=int, default=0, help="惩罚骰数量")
    parser.add_argument("--opposed", nargs=2, type=int, help="D100 对抗检定 (A 技能值 B 技能值)")
    parser.add_argument("--coc-stats", action="store_true", help="生成完整 COC 属性")
    parser.add_argument("--san-check", nargs=2, help="SAN检定 (当前SAN 损失格式) e.g. --san-check 60 0/1d6")
    parser.add_argument("--damage", nargs=2, help="伤害计算 (武器伤害公式 DB公式) e.g. --damage 1d10+2 1d4")
    parser.add_argument("--pregen", action="store_true", help="快速生成预设调查员")
    parser.add_argument("--era", default="1920s", choices=["1890s", "1920s", "modern"], help="预设调查员时代")
    parser.add_argument("--occupation", default="", help="预设调查员职业，如 记者、警员、民俗研究者")
    parser.add_argument("--region", default="us", choices=["us", "cn"], help="预设调查员姓名地区")
    parser.add_argument("--format", dest="output_format", default="text", choices=["text", "markdown"], help="预设调查员输出格式")
    parser.add_argument("--skill-calc", nargs=3, type=int, metavar=("EDU", "职业属性", "INT"), help="计算技能点: EDU 职业指定属性 INT")
    parser.add_argument("--credit", type=int, default=0, help="信用评级预留点数，用于 --skill-calc")

    args = parser.parse_args()

    if args.coc_stats:
        print("══════════ COC 7版 属性生成 ══════════")
        for k, v in generate_stats().items():
            print(f"  {k:12s}: {v}")
        print("══════════════════════════════════════")
    elif args.pregen:
        character = pregen_character(args.era, args.occupation, args.region)
        if args.output_format == "markdown":
            print(format_pregen_markdown(character))
        else:
            print(format_pregen_text(character))
    elif args.check is not None:
        success_count = 0
        print(f"D100 技能检定 (技能值: {args.check}%)")
        for idx in range(args.repeat):
            result, level, info = d100_check(args.check, args.bonus, args.penalty)
            success_count += 1 if is_success(level) else 0
            desc = f"[{idx + 1}/{args.repeat}] " if args.repeat > 1 else ""
            print(f"   {desc}掷骰结果: {result} -> {level}")
            for item in info:
                print(f"   ({item})")
        if args.repeat > 1:
            print(f"   成功统计: {success_count}/{args.repeat}")
    elif args.opposed:
        sa, sb = args.opposed
        ra, la, rb, lb, win = opposed_check(sa, sb)
        print("D100 对抗检定")
        print(f"   A (技能 {sa}%): 掷骰 {ra} -> {la}")
        print(f"   B (技能 {sb}%): 掷骰 {rb} -> {lb}")
        print(f"   结果: {'A 获胜' if win == 'A' else ('B 获胜' if win == 'B' else '平局')}")
    elif args.san_check:
        san, loss_expr = args.san_check
        loss, new_san, outs = san_check(int(san), loss_expr)
        print(f"SAN 检定 (当前: {san})")
        for item in outs:
            print(f"   {item}")
    elif args.damage:
        wdmg, dbstr = args.damage
        wd, db, total = damage_roll(wdmg, dbstr)
        print("伤害计算")
        print(f"   武器伤害: {wd} ({wdmg})")
        print(f"   伤害加值 DB: {db} ({dbstr})")
        print(f"   总计: {total}")
    elif args.skill_calc:
        edu, occupation_attr, int_value = args.skill_calc
        occupation, hobby, spendable = skill_points(edu, occupation_attr, int_value, args.credit)
        print("══════════ COC 技能点计算 ══════════")
        print(f"  职业技能点: EDU×2 + 职业属性×2 = {occupation}")
        if args.credit:
            print(f"  信用评级预留: {args.credit}")
            print(f"  可分配职业技能点: {spendable}")
        print(f"  兴趣技能点: INT×2 = {hobby}")
        print("════════════════════════════════════")
    elif args.roll:
        for idx in range(args.repeat):
            try:
                result = roll(args.roll)
            except ValueError as exc:
                print(f"错误: {exc}")
                raise SystemExit(2)
            desc = f"[{idx + 1}/{args.repeat}] " if args.repeat > 1 else ""
            print(f"{desc}{args.roll} = {result}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
