#!/usr/bin/env python3
"""
COC 跑团记忆工具

用 JSON 做源记忆，Markdown 作为可读导出。
"""
import argparse
import json
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_DIR = ROOT / "scenarios"


EMPTY_MEMORY = {
    "meta": {
        "campaign": "",
        "era": "",
        "current_time": "",
        "current_location": "",
        "current_scene": "",
        "player_characters": "",
        "keeper_style": "",
        "boundaries": "",
        "created_at": "",
        "updated_at": "",
    },
    "public": {
        "recap": [],
        "protagonist_anchor": [],
        "cast_anchor": [],
        "current_situation": [],
        "investigator_status": [],
        "known_clues": [],
        "npc_status": [],
        "locations": [],
        "open_questions": [],
        "items": [],
        "timeline": [],
    },
    "keeper": {
        "truth": [],
        "secret_notes": [],
        "hidden_rolls": [],
        "hidden_san": [],
        "countdowns": [],
        "foreshadowing": [],
    },
}


SECTION_MAP = {
    "recap": ("public", "recap"),
    "protagonist": ("public", "protagonist_anchor"),
    "cast": ("public", "cast_anchor"),
    "situation": ("public", "current_situation"),
    "status": ("public", "investigator_status"),
    "clue": ("public", "known_clues"),
    "npc": ("public", "npc_status"),
    "location": ("public", "locations"),
    "question": ("public", "open_questions"),
    "item": ("public", "items"),
    "timeline": ("public", "timeline"),
    "truth": ("keeper", "truth"),
    "secret": ("keeper", "secret_notes"),
    "hidden-roll": ("keeper", "hidden_rolls"),
    "hidden-san": ("keeper", "hidden_san"),
    "countdown": ("keeper", "countdowns"),
    "foreshadowing": ("keeper", "foreshadowing"),
}


META_FIELDS = {
    "campaign": "campaign",
    "era": "era",
    "time": "current_time",
    "location": "current_location",
    "scene": "current_scene",
    "characters": "player_characters",
    "style": "keeper_style",
    "boundaries": "boundaries",
}


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def slugify(name):
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", name.strip(), flags=re.UNICODE)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "campaign"


def memory_paths(name):
    slug = slugify(name)
    return SCENARIOS_DIR / f"{slug}_memory.json", SCENARIOS_DIR / f"{slug}_memory.md"


class MemoryLock:
    def __init__(self, name):
        self.path = SCENARIOS_DIR / f".{slugify(name)}_memory.lock"
        self.handle = None

    def __enter__(self):
        SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("w", encoding="utf-8")
        if fcntl:
            fcntl.flock(self.handle, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.handle:
            if fcntl:
                fcntl.flock(self.handle, fcntl.LOCK_UN)
            self.handle.close()


def load_memory(name):
    json_path, _ = memory_paths(name)
    if not json_path.exists():
        raise SystemExit(f"找不到记忆文件: {json_path}")
    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memory):
    name = memory["meta"]["campaign"] or "campaign"
    json_path, md_path = memory_paths(name)
    SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)
    memory["meta"]["updated_at"] = now()
    tmp_json = json_path.with_suffix(".json.tmp")
    tmp_md = md_path.with_suffix(".md.tmp")
    with tmp_json.open("w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp_json.replace(json_path)
    tmp_md.write_text(render_markdown(memory), encoding="utf-8")
    tmp_md.replace(md_path)
    return json_path, md_path


def bullet_list(items):
    if not items:
        return "- （暂无）"
    return "\n".join(f"- {item}" for item in items)


def render_markdown(memory):
    meta = memory["meta"]
    public = memory["public"]
    keeper = memory["keeper"]
    return f"""# {meta.get('campaign') or 'COC 跑团'} - 战役记忆

> 玩家可知信息可以回顾；Keeper 记忆不要直接展示给玩家。

## 基本信息

| 项目 | 内容 |
|---|---|
| 团名 / 模组名 | {meta.get('campaign', '')} |
| 时代 | {meta.get('era', '')} |
| 当前日期 / 时间 | {meta.get('current_time', '')} |
| 当前地点 | {meta.get('current_location', '')} |
| 当前场景 | {meta.get('current_scene', '')} |
| 玩家角色 | {meta.get('player_characters', '')} |
| Keeper 风格 | {meta.get('keeper_style', '')} |
| 内容边界 | {meta.get('boundaries', '')} |
| 创建时间 | {meta.get('created_at', '')} |
| 更新时间 | {meta.get('updated_at', '')} |

## 上回回顾（玩家可知）

{bullet_list(public.get('recap', []))}

## 主角人设锚点（玩家可知）

{bullet_list(public.get('protagonist_anchor', []))}

## 配角 NPC 人设锚点

{bullet_list(public.get('cast_anchor', []))}

## 当前状况（玩家可知）

{bullet_list(public.get('current_situation', []))}

## 调查员状态

{bullet_list(public.get('investigator_status', []))}

## 已知线索（玩家可知）

{bullet_list(public.get('known_clues', []))}

## NPC 状态

{bullet_list(public.get('npc_status', []))}

## 地点与场景状态

{bullet_list(public.get('locations', []))}

## 未解决问题（玩家可知）

{bullet_list(public.get('open_questions', []))}

## 物品与资源

{bullet_list(public.get('items', []))}

## 时间线

{bullet_list(public.get('timeline', []))}

## Keeper 记忆（不要直接展示给玩家）

### 真相与幕后

{bullet_list(keeper.get('truth', []))}

### 秘密备注

{bullet_list(keeper.get('secret_notes', []))}

### 暗骰记录

{bullet_list(keeper.get('hidden_rolls', []))}

### 隐藏 / 延迟 SAN

{bullet_list(keeper.get('hidden_san', []))}

### 倒计时与敌方行动

{bullet_list(keeper.get('countdowns', []))}

### 伏笔与回收

{bullet_list(keeper.get('foreshadowing', []))}

## 下一轮前连续性检查

- [ ] 当前时间、地点、同行者一致。
- [ ] HP/SAN/MP/状态/物品一致。
- [ ] 玩家已知线索没有混入 Keeper Only 真相。
- [ ] NPC 位置、态度、秘密一致。
- [ ] 暗骰、延迟 SAN、倒计时、追踪者已记录。
"""


def cmd_init(args):
    with MemoryLock(args.name):
        json_path, _ = memory_paths(args.name)
        if json_path.exists() and not args.force:
            raise SystemExit(f"记忆已存在: {json_path}。如需覆盖，请加 --force。")
        memory = deepcopy(EMPTY_MEMORY)
        memory["meta"].update({
            "campaign": args.name,
            "era": args.era or "",
            "current_location": args.location or "",
            "current_scene": args.scene or "",
            "player_characters": args.characters or "",
            "keeper_style": args.style or "",
            "boundaries": args.boundaries or "",
            "created_at": now(),
            "updated_at": now(),
        })
        if args.recap:
            memory["public"]["recap"].append(args.recap)
        json_path, md_path = save_memory(memory)
    print(f"已创建记忆: {json_path}")
    print(f"已导出 Markdown: {md_path}")


def cmd_list(_args):
    SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(SCENARIOS_DIR.glob("*_memory.json"))
    if not files:
        print("暂无记忆文件。")
        return
    for f in files:
        print(f.name)


def cmd_recall(args):
    with MemoryLock(args.name):
        memory = load_memory(args.name)
    meta = memory["meta"]
    public = memory["public"]
    keeper = memory["keeper"]

    print(f"# 记忆回忆: {meta.get('campaign')}")
    print(f"- 时间: {meta.get('current_time') or '未记录'}")
    print(f"- 地点: {meta.get('current_location') or '未记录'}")
    print(f"- 场景: {meta.get('current_scene') or '未记录'}")
    print(f"- 角色: {meta.get('player_characters') or '未记录'}")
    print("\n## 玩家可知")
    for key in [
        "recap", "protagonist_anchor", "cast_anchor", "current_situation", "investigator_status", "known_clues",
        "npc_status", "locations", "open_questions", "items", "timeline",
    ]:
        title = key.replace("_", " ")
        print(f"\n### {title}")
        print(bullet_list(public.get(key, [])))

    if args.keeper:
        print("\n## Keeper 记忆（不要直接展示给玩家）")
        for key in ["truth", "secret_notes", "hidden_rolls", "hidden_san", "countdowns", "foreshadowing"]:
            title = key.replace("_", " ")
            print(f"\n### {title}")
            print(bullet_list(keeper.get(key, [])))

    print("\n## 继续前检查")
    print("- 核对时间、地点、同行者。")
    print("- 核对 HP/SAN/MP/状态/物品。")
    print("- 不要把 Keeper 记忆直接说给玩家。")
    print("- 结算未处理的暗骰、延迟 SAN、倒计时。")


def cmd_set(args):
    with MemoryLock(args.name):
        memory = load_memory(args.name)
        field = META_FIELDS[args.field]
        memory["meta"][field] = args.value
        json_path, md_path = save_memory(memory)
    print(f"已更新 {args.field}: {args.value}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def cmd_add(args):
    with MemoryLock(args.name):
        memory = load_memory(args.name)
        group, key = SECTION_MAP[args.section]
        memory[group][key].append(args.text)
        json_path, md_path = save_memory(memory)
    print(f"已追加到 {args.section}: {args.text}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def cmd_render(args):
    with MemoryLock(args.name):
        memory = load_memory(args.name)
        json_path, md_path = save_memory(memory)
    print(f"已刷新 Markdown: {md_path}")
    print(f"JSON: {json_path}")


def main():
    parser = argparse.ArgumentParser(description="COC 跑团记忆工具")
    sub = parser.add_subparsers(dest="cmd", required=True)

    init_p = sub.add_parser("init", help="创建新战役记忆")
    init_p.add_argument("--name", required=True, help="团名或模组名")
    init_p.add_argument("--era", default="", help="时代")
    init_p.add_argument("--location", default="", help="初始地点")
    init_p.add_argument("--scene", default="", help="当前场景")
    init_p.add_argument("--characters", default="", help="玩家角色")
    init_p.add_argument("--style", default="", help="Keeper 风格")
    init_p.add_argument("--boundaries", default="", help="内容边界")
    init_p.add_argument("--recap", default="", help="初始回顾")
    init_p.add_argument("--force", action="store_true", help="覆盖已有记忆")
    init_p.set_defaults(func=cmd_init)

    list_p = sub.add_parser("list", help="列出记忆文件")
    list_p.set_defaults(func=cmd_list)

    recall_p = sub.add_parser("recall", help="读取战役记忆")
    recall_p.add_argument("--name", required=True, help="团名或模组名")
    recall_p.add_argument("--keeper", action="store_true", help="包含 Keeper 记忆")
    recall_p.set_defaults(func=cmd_recall)

    set_p = sub.add_parser("set", help="更新基本信息")
    set_p.add_argument("--name", required=True, help="团名或模组名")
    set_p.add_argument("--field", required=True, choices=sorted(META_FIELDS), help="字段")
    set_p.add_argument("--value", required=True, help="值")
    set_p.set_defaults(func=cmd_set)

    add_p = sub.add_parser("add", help="追加记忆条目")
    add_p.add_argument("--name", required=True, help="团名或模组名")
    add_p.add_argument("--section", required=True, choices=sorted(SECTION_MAP), help="记忆分区")
    add_p.add_argument("--text", required=True, help="记忆内容")
    add_p.set_defaults(func=cmd_add)

    render_p = sub.add_parser("render", help="刷新 Markdown 导出")
    render_p.add_argument("--name", required=True, help="团名或模组名")
    render_p.set_defaults(func=cmd_render)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
