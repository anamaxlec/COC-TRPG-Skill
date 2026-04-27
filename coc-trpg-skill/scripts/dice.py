#!/usr/bin/env python3
"""
COC 7版 骰子工具
支持：D100检定、属性批量生成、武器伤害投掷、SAN检定、对抗检定
"""
import random
import argparse
import re

RNG = random.SystemRandom()

# ── COC Stats Table ──
BUILD_TABLE = {
    (2, 64): (-2, -2),
    (65, 84): (-1, -1),
    (85, 124): (0, 0),
    (125, 164): (1, "1D4"),
    (165, 204): (2, "1D6"),
    (205, 284): (3, "2D6"),
    (285, 364): (4, "3D6"),
}


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

    detail = {
        "tens": [t * 10 for t in tens],
        "ones": ones,
        "selected_tens": selected_tens * 10,
    }
    return result, detail


def d100_check(skill, bonus=0, penalty=0):
    """D100 技能检定"""
    net = bonus - penalty
    rolls = []
    if net > 0:
        result, detail = roll_d100(net)
        rolls.append(
            f"奖励骰 {net}: tens={detail['tens']}, ones={detail['ones']}, selected_tens={detail['selected_tens']}"
        )
    elif net < 0:
        result, detail = roll_d100(net)
        rolls.append(
            f"惩罚骰 {abs(net)}: tens={detail['tens']}, ones={detail['ones']}, selected_tens={detail['selected_tens']}"
        )
    else:
        result, detail = roll_d100()
        rolls.append(f"D100: tens={detail['tens'][0]}, ones={detail['ones']}")

    # 判定成功等级
    if result == 1:
        level = "🎉 大成功 CRITICAL"
    elif result <= skill // 5:
        level = "⭐ 极难成功 EXTREME"
    elif result <= skill // 2:
        level = "📗 困难成功 HARD"
    elif result <= skill:
        level = "✅ 常规成功 NORMAL"
    elif result >= 96 and skill < 50:
        level = "💀 大失败 FUMBLE"
    elif result == 100:
        level = "💀 大失败 FUMBLE"
    else:
        level = "❌ 失败 FAIL"

    return result, level, rolls


def is_success(level):
    return any(tag in level for tag in ("CRITICAL", "EXTREME", "HARD", "NORMAL"))


def opposed_check(skill_a, skill_b):
    """D100 对抗检定，返回 A vs B 的结果"""
    ra, la, _ = d100_check(skill_a)
    rb, lb, _ = d100_check(skill_b)

    success_order = {
        "🎉 大成功 CRITICAL": 5,
        "⭐ 极难成功 EXTREME": 4,
        "📗 困难成功 HARD": 3,
        "✅ 常规成功 NORMAL": 2,
        "❌ 失败 FAIL": 1,
        "💀 大失败 FUMBLE": 0,
    }
    for k in ["🎉 大成功 CRITICAL", "⭐ 极难成功 EXTREME", "📗 困难成功 HARD", "✅ 常规成功 NORMAL", "❌ 失败 FAIL", "💀 大失败 FUMBLE"]:
        if la == k:
            score_a = success_order[k]
        if lb == k:
            score_b = success_order[k]

    if score_a > score_b:
        win = "A"
    elif score_b > score_a:
        win = "B"
    else:
        win = "平局 DRAW"

    return ra, la, rb, lb, win


def generate_stats():
    """生成8项COC基础属性"""
    stats = {}
    stats["力量 STR"] = roll("3D6") * 5
    stats["体质 CON"] = roll("3D6") * 5
    stats["体型 SIZ"] = roll("2D6+6") * 5
    stats["敏捷 DEX"] = roll("3D6") * 5
    stats["外貌 APP"] = roll("3D6") * 5
    stats["智力 INT"] = roll("2D6+6") * 5
    stats["意志 POW"] = roll("3D6") * 5
    stats["教育 EDU"] = roll("2D6+6") * 5

    # 衍生属性
    con = stats["体质 CON"]
    siz = stats["体型 SIZ"]
    str_ = stats["力量 STR"]
    dex = stats["敏捷 DEX"]
    pow_ = stats["意志 POW"]

    hp = (con + siz) // 10
    san = pow_
    mp = pow_ // 5
    luck = roll("3D6") * 5
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
        "生命值 HP": hp,
        "理智值 SAN": san,
        "魔力值 MP": mp,
        "幸运 Luck": luck,
        "移动力 MOV": mov,
        "体格 Build": build,
        "伤害加值 DB": db,
    }


def san_check(current_san, loss_die):
    """SAN 检定与疯狂判定"""
    loss = roll(loss_die)
    new_san = current_san - loss

    output = []
    output.append(f"SAN 损失: {loss} (投骰: {loss_die})")
    output.append(f"SAN 变化: {current_san} → {new_san}")

    if loss >= 5:
        output.append("⚠️ 单次损失 ≥ 5 → 临时疯狂 (1D10 小时)")
        output.append(f"    疯狂表现: D10 = {RNG.randint(1, 10)} (查临时疯狂表)")

    if current_san > 0 and loss >= current_san // 5:
        output.append("⚠️ 单次损失 ≥ SAN/5 → 不定疯狂 (持续到剧情解决)")

    if new_san <= 0:
        output.append("💀 SAN 归零 → 永久疯狂 (角色变为NPC)")

    return loss, new_san, output


def damage_roll(weapon_dmg, db_str):
    """武器伤害 + DB 计算"""
    wd = roll(weapon_dmg)
    if db_str and db_str != "0":
        db = roll(db_str)
    else:
        db = 0
    total = wd + db
    return wd, db, total


def skill_points(edu, occupation_attr, int_value, credit=0):
    """计算职业技能点与兴趣技能点。occupation_attr 是职业指定属性值。"""
    occupation = edu * 2 + occupation_attr * 2
    hobby = int_value * 2
    spendable = max(occupation - credit, 0)
    return occupation, hobby, spendable


def pregen_character(era="1920s"):
    """快速生成预设角色"""
    stats = generate_stats()

    occupations = [
        ("私家侦探", ["侦察", "心理学", "格斗", "话术", "图书馆", "法律", "乔装", "艺术/手艺(摄影)"]),
        ("记者", ["图书馆", "母语", "心理学", "侦察", "历史", "魅惑", "说服", "艺术/手艺(写作)"]),
        ("医生", ["急救", "医学", "心理学", "科学(生物)", "图书馆", "侦察", "说服", "外语(拉丁语)"]),
        ("教授", ["图书馆", "母语", "神秘学", "心理学", "科学(考古)", "说服", "历史", "外语(拉丁语)"]),
        ("古董商", ["估价", "历史", "图书馆", "侦察", "神秘学", "魅惑", "外语(阿拉伯语)", "艺术/手艺(修复)"]),
        ("罪犯", ["潜行", "锁匠", "格斗", "乔装", "侦察", "聆听", "枪械(手枪)", "电气维修"]),
    ]

    occ = RNG.choice(occupations)
    occ_name, occ_skills = occ

    edu = stats["教育 EDU"]
    inte = stats["智力 INT"]

    occ_points = edu * 2 + RNG.choice([edu, inte, stats["敏捷 DEX"]]) * 2
    hobby_points = inte * 2

    # 简单分配技能点 (信用评级 20-50 之间)
    credit = RNG.randint(20, 50)
    occ_points -= credit

    skills = {}
    for s in occ_skills:
        skills[s] = 30 + RNG.randint(0, 20)

    skills["信用评级"] = credit
    skills["图书馆使用"] = 40 + RNG.randint(0, 20)
    skills["侦察"] = 40 + RNG.randint(0, 20)
    skills["聆听"] = 30 + RNG.randint(0, 20)
    skills["闪避"] = stats["敏捷 DEX"] // 2 + RNG.randint(0, 20)

    return stats, occ_name, skills


def main():
    parser = argparse.ArgumentParser(description="COC 7版 骰子工具")
    parser.add_argument("--roll", help="投骰公式 (如 2d6+6, 3d6, 1d100)")
    parser.add_argument("--repeat", type=int, default=1, help="重复次数")
    parser.add_argument("--check", type=int, help="D100 技能检定 (提供技能值)")
    parser.add_argument("--bonus", type=int, default=0, help="奖励骰数量")
    parser.add_argument("--penalty", type=int, default=0, help="惩罚骰数量")
    parser.add_argument("--opposed", nargs=2, type=int, help="D100 对抗检定 (A 技能值 B 技能值)")
    parser.add_argument("--coc-stats", action="store_true", help="生成完整 COC 属性")
    parser.add_argument("--san-check", nargs=2, help="SAN检定 (当前SAN 损失骰公式) e.g. --san-check 60 1d6")
    parser.add_argument("--damage", nargs=2, help="伤害计算 (武器伤害公式 DB公式) e.g. --damage 1d10+2 1d4")
    parser.add_argument("--pregen", action="store_true", help="快速生成预设角色")
    parser.add_argument("--skill-calc", nargs=3, type=int,
                        metavar=("EDU", "职业属性", "INT"),
                        help="计算技能点: EDU 职业指定属性 INT")
    parser.add_argument("--credit", type=int, default=0, help="信用评级预留点数，用于 --skill-calc")

    args = parser.parse_args()

    if args.coc_stats:
        print("══════════ COC 7版 属性生成 ══════════")
        stats = generate_stats()
        for k, v in stats.items():
            print(f"  {k:12s}: {v}")
        print("══════════════════════════════════════")

    elif args.pregen:
        print("══════════ 快速预设角色 ══════════")
        stats, occ, skills = pregen_character()
        for k, v in stats.items():
            print(f"  {k:12s}: {v}")
        print(f"  {'职业':12s}: {occ}")
        print(f"  --- 技能 ---")
        for k, v in skills.items():
            print(f"  {k:12s}: {v}%")
        print("══════════════════════════════════")

    elif args.check is not None:
        skill = args.check
        success_count = 0
        print(f"⚅ D100 技能检定 (技能值: {skill}%)")
        for idx in range(args.repeat):
            result, level, info = d100_check(skill, args.bonus, args.penalty)
            success_count += 1 if is_success(level) else 0
            desc = f"[{idx+1}/{args.repeat}] " if args.repeat > 1 else ""
            print(f"   {desc}掷骰结果: {result}  →  {level}")
            for i in info:
                print(f"   ({i})")
        if args.repeat > 1:
            print(f"   成功统计: {success_count}/{args.repeat}")

    elif args.opposed:
        sa, sb = args.opposed
        ra, la, rb, lb, win = opposed_check(sa, sb)
        print(f"⚅ D100 对抗检定")
        print(f"   A (技能 {sa}%): 掷骰 {ra} → {la}")
        print(f"   B (技能 {sb}%): 掷骰 {rb} → {lb}")
        winner = "A 获胜" if win == "A" else ("B 获胜" if win == "B" else "平局")
        print(f"   结果: {winner}")

    elif args.san_check:
        san, loss_die = args.san_check
        san = int(san)
        loss, new_san, outs = san_check(san, loss_die)
        print(f"⚅ SAN 检定 (当前: {san})")
        for o in outs:
            print(f"   {o}")

    elif args.damage:
        wdmg, dbstr = args.damage
        wd, db, total = damage_roll(wdmg, dbstr)
        print(f"⚔️ 伤害计算")
        print(f"   武器伤害: {wd} ({wdmg})")
        print(f"   伤害加值 (DB): {db} ({dbstr})")
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
        formula = args.roll
        for i in range(args.repeat):
            try:
                r = roll(formula)
                desc = f"[{i+1}/{args.repeat}]" if args.repeat > 1 else ""
                print(f"⚅ {desc} {formula} = {r}")
            except ValueError as exc:
                print(f"错误: {exc}")
                raise SystemExit(2)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
