#!/usr/bin/env python3
"""
COC 随机姓名生成器
按时代和地区生成角色姓名
"""
import random
import argparse

# ── 1920s 美国姓名库 ──
FIRST_MALE_1920s = [
    "James", "John", "Robert", "William", "Charles", "George", "Joseph", "Frank",
    "Edward", "Henry", "Thomas", "Walter", "Harry", "Arthur", "Albert", "Clarence",
    "Harold", "Raymond", "Paul", "Richard", "Roy", "Joe", "Louis", "Carl",
    "Ernest", "Fred", "Howard", "Ralph", "Earl", "Francis", "Lawrence", "Herbert",
    "Alfred", "Leonard", "Jack", "Bernard", "Leo", "Samuel", "David", "Michael",
    "Peter", "Daniel", "Victor", "Edwin", "Frederick", "Chester", "Herman", "Lloyd",
]

FIRST_FEMALE_1920s = [
    "Mary", "Dorothy", "Helen", "Margaret", "Ruth", "Florence", "Elizabeth", "Ethel",
    "Anna", "Marie", "Lillian", "Alice", "Mildred", "Frances", "Evelyn", "Rose",
    "Catherine", "Louise", "Edna", "Gladys", "Marjorie", "Josephine", "Gertrude", "Esther",
    "Martha", "Eleanor", "Bertha", "Irene", "Sarah", "Agnes", "Virginia", "Beatrice",
    "Clara", "Grace", "Thelma", "Doris", "Edith", "Lucille", "Lois", "Hazel",
    "Norma", "Emma", "Jean", "Ruby", "Pauline", "Pearl", "Gloria", "Laura",
]

LAST_NAMES_1920s = [
    "Smith", "Johnson", "Brown", "Williams", "Miller", "Jones", "Davis", "Anderson",
    "Wilson", "Taylor", "Thomas", "Moore", "Martin", "Jackson", "Thompson", "White",
    "Harris", "Clark", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Green", "Baker", "Adams", "Nelson", "Hill", "Campbell",
    "Mitchell", "Carter", "Roberts", "Turner", "Phillips", "Collins", "Stewart", "Morris",
    "Murphy", "Cook", "Rogers", "Reed", "Morgan", "Bell", "Cooper", "Richardson",
    "Cox", "Howard", "Ward", "Wood", "Brooks", "Gray", "James", "Watson",
    "Bennett", "Cole", "Hayes", "Sullivan", "Porter", "Shaw", "Gordon", "Harrison",
]

# ── 中文名库（1920s 中国） ──
CN_SURNAME = [
    "张", "王", "李", "赵", "陈", "杨", "刘", "黄", "吴", "周",
    "徐", "孙", "朱", "马", "胡", "林", "郭", "何", "高", "郑",
    "罗", "梁", "谢", "宋", "唐", "韩", "曹", "许", "冯", "董",
]

CN_MALE = [
    "文渊", "志明", "国强", "浩然", "子轩", "鸿飞", "景行", "清源",
    "松年", "云鹤", "远航", "立诚", "知行", "博文", "仲卿", "思远",
    "伯安", "守仁", "若虚", "长风", "明哲", "逸仙", "怀瑾", "子期",
    "承志", "靖宇", "永年", "元璋", "天佑", "占鳌",
]

CN_FEMALE = [
    "婉清", "子衿", "思柔", "静姝", "若兰", "灵犀", "紫薇", "凝香",
    "潇然", "碧落", "如烟", "流萤", "天瑜", "瑶光", "芷若", "飞燕",
    "秋白", "含芳", "墨兰", "琴心", "玉簪", "清瑶", "巧云", "冷香",
    "雪吟", "风裳", "绮罗", "青鸾", "银薇", "红药",
]

# ── 1890s 煤气灯 ──
FIRST_MALE_1890s = [
    "Arthur", "Percy", "Reginald", "Cecil", "Algernon", "Horace", "Eustace",
    "Bertram", "Cyril", "Hubert", "Wilfred", "Ernest", "Montague", "Ambrose",
    "Marmaduke", "Lionel", "Nigel", "Rupert", "Godfrey", "Basil",
]
FIRST_FEMALE_1890s = [
    "Beatrice", "Constance", "Adelaide", "Mabel", "Edith", "Gwendolyn",
    "Henrietta", "Lavinia", "Cordelia", "Penelope", "Maud", "Agatha",
    "Sybil", "Euphemia", "Millicent", "Letitia", "Prudence", "Cecily",
]
LAST_NAMES_1890s = [
    "Ashworth", "Blackwood", "Carrington", "Devereux", "Faulkner", "Harrington",
    "Kingsley", "Lockwood", "Montgomery", "Pemberton", "Ravenscroft",
    "Sinclair", "Thornhill", "Whitmore", "Worthington", "Yarborough",
]


def generate_name(era, gender, region="us"):
    if era == "1920s" and region == "cn":
        surname = random.choice(CN_SURNAME)
        if gender == "male":
            first = random.choice(CN_MALE)
        else:
            first = random.choice(CN_FEMALE)
        return surname + first

    if era == "1920s":
        if gender == "male":
            first = random.choice(FIRST_MALE_1920s)
        else:
            first = random.choice(FIRST_FEMALE_1920s)
        last = random.choice(LAST_NAMES_1920s)
        return f"{first} {last}"

    if era == "1890s":
        if gender == "male":
            first = random.choice(FIRST_MALE_1890s)
        else:
            first = random.choice(FIRST_FEMALE_1890s)
        last = random.choice(LAST_NAMES_1890s)
        return f"{first} {last}"

    # modern - use 1920s name pool as foundation
    if era == "modern":
        if gender == "male":
            first = random.choice(FIRST_MALE_1920s)
        else:
            first = random.choice(FIRST_FEMALE_1920s)
        last = random.choice(LAST_NAMES_1920s)
        return f"{first} {last}"

    return "Unknown"


def main():
    parser = argparse.ArgumentParser(description="COC 随机姓名生成器")
    parser.add_argument("--era", default="1920s", choices=["1890s", "1920s", "modern"],
                        help="时代背景")
    parser.add_argument("--gender", default=None, choices=["male", "female"],
                        help="性别")
    parser.add_argument("--region", default="us", choices=["us", "cn"],
                        help="地区")
    parser.add_argument("--count", type=int, default=1, help="生成数量")

    args = parser.parse_args()

    gender = args.gender if args.gender else random.choice(["male", "female"])

    for i in range(args.count):
        g = gender if args.count == 1 else random.choice(["male", "female"])
        name = generate_name(args.era, g, args.region)
        print(f"[{i+1}] {name}  ({g}, {args.era})")


if __name__ == "__main__":
    main()
