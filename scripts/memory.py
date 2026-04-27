#!/usr/bin/env python3
"""
COC 跑团记忆工具

用 JSON 做源记忆，Markdown 作为可读导出。
"""
import argparse
import hashlib
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
SAVES_DIR = ROOT / "saves"
SAVE_FORMAT = "coc-trpg-skill-save"
SAVE_VERSION = 1


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
        "last_save_at": "",
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
    "scenario": {
        "premise": [],
        "acts": [],
        "scene_nodes": [],
        "clue_web": [],
        "npc_functions": [],
        "threat_clock": [],
        "endings": [],
        "continuity": [],
    },
    "resume": {
        "updated_at": "",
        "public": "",
        "keeper": "",
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
    "scenario": ("scenario", "premise"),
    "outline": ("scenario", "premise"),
    "act": ("scenario", "acts"),
    "scene-node": ("scenario", "scene_nodes"),
    "clue-web": ("scenario", "clue_web"),
    "npc-function": ("scenario", "npc_functions"),
    "threat-clock": ("scenario", "threat_clock"),
    "ending": ("scenario", "endings"),
    "continuity": ("scenario", "continuity"),
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


def default_save_path(name):
    slug = slugify(name)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return SAVES_DIR / f"{slug}_{stamp}.cocsave.json"


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
        return normalize_memory(json.load(f))


def merge_defaults(default, value):
    if isinstance(default, dict):
        result = deepcopy(default)
        if isinstance(value, dict):
            for key, item in value.items():
                result[key] = merge_defaults(default.get(key), item)
        return result
    return deepcopy(value) if value is not None else deepcopy(default)


def normalize_memory(memory):
    return merge_defaults(EMPTY_MEMORY, memory)


def memory_checksum(memory):
    payload = json.dumps(memory, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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


def write_save_file(memory, output_path, force=False):
    output_path = Path(output_path).expanduser()
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    if output_path.exists() and not force:
        raise SystemExit(f"存档已存在: {output_path}。如需覆盖，请加 --force。")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    exported_at = now()
    memory_copy = normalize_memory(deepcopy(memory))
    memory_copy["meta"]["last_save_at"] = exported_at
    memory_copy["resume"] = build_resume(memory_copy, exported_at)
    save_data = {
        "format": SAVE_FORMAT,
        "version": SAVE_VERSION,
        "exported_at": exported_at,
        "resume": memory_copy["resume"],
        "checksum": memory_checksum(memory_copy),
        "memory": memory_copy,
    }
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp_path.replace(output_path)
    return output_path, save_data


def read_save_file(path):
    save_path = Path(path).expanduser()
    if not save_path.is_absolute():
        save_path = ROOT / save_path
    if not save_path.exists():
        raise SystemExit(f"找不到存档文件: {save_path}")
    with save_path.open("r", encoding="utf-8") as f:
        save_data = json.load(f)
    if save_data.get("format") != SAVE_FORMAT:
        raise SystemExit("存档格式不正确，不是 coc-trpg-skill 存档。")
    if save_data.get("version") != SAVE_VERSION:
        raise SystemExit(f"不支持的存档版本: {save_data.get('version')}")
    raw_memory = save_data.get("memory")
    if not isinstance(raw_memory, dict):
        raise SystemExit("存档缺少 memory 数据。")
    expected = save_data.get("checksum")
    raw_checksum = memory_checksum(raw_memory)
    memory = normalize_memory(raw_memory)
    normalized_checksum = memory_checksum(memory)
    if expected and expected not in {raw_checksum, normalized_checksum}:
        raise SystemExit("存档校验失败，文件可能被改动或复制损坏。")
    return memory, save_path


def section_text(items, empty="（暂无记录）"):
    return "\n".join(f"- {item}" for item in items) if items else f"- {empty}"


def build_resume(memory, exported_at):
    meta = memory["meta"]
    public = memory["public"]
    keeper = memory["keeper"]
    scenario = memory["scenario"]
    title = meta.get("campaign") or "COC 跑团"

    public_resume = f"""# {title} - 续跑摘要（玩家可知）

## 当前落点

- 时代：{meta.get('era') or '未记录'}
- 当前时间：{meta.get('current_time') or '未记录'}
- 当前地点：{meta.get('current_location') or '未记录'}
- 当前场景：{meta.get('current_scene') or '未记录'}
- 玩家角色：{meta.get('player_characters') or '未记录'}
- Keeper 风格：{meta.get('keeper_style') or '未记录'}

## 已进行流程

{section_text(public.get('timeline') or public.get('recap'))}

## 主角与重要关系

{section_text(public.get('protagonist_anchor') + public.get('cast_anchor'))}

## 当前状况与调查员状态

{section_text(public.get('current_situation') + public.get('investigator_status'))}

## 已知线索

{section_text(public.get('known_clues'))}

## NPC、地点与物品

{section_text(public.get('npc_status') + public.get('locations') + public.get('items'))}

## 未解决问题

{section_text(public.get('open_questions'))}

## 续跑入口

- 导入后先用玩家可知信息做极短“上回回顾”。
- 从“当前场景”继续，不要重开剧情。
- 回顾后给 2-4 个可行动选项，并允许玩家自由行动。
"""

    keeper_resume = f"""# {title} - Keeper 续跑摘要

## 幕后真相与秘密

{section_text(keeper.get('truth') + keeper.get('secret_notes'))}

## 暗骰与隐藏 SAN

{section_text(keeper.get('hidden_rolls') + keeper.get('hidden_san'))}

## 倒计时、敌方行动与伏笔

{section_text(keeper.get('countdowns') + keeper.get('foreshadowing'))}

## 剧本连续性

### 核心设定与分幕

{section_text(scenario.get('premise') + scenario.get('acts'))}

### 场景节点与线索网络

{section_text(scenario.get('scene_nodes') + scenario.get('clue_web'))}

### NPC 剧本功能、威胁时钟与结局条件

{section_text(scenario.get('npc_functions') + scenario.get('threat_clock') + scenario.get('endings'))}

### 连续性备注

{section_text(scenario.get('continuity'))}

## 续跑前必须核对

- 当前时间、地点、同行者与调查员状态是否一致。
- 已知线索不要混入 Keeper Only 真相。
- 未结算暗骰、隐藏 SAN、延迟公开 SAN、倒计时需要先处理或继续挂起。
- NPC 的真实动机、态度和当前位置不能和上一轮冲突。
- 剧本当前节点必须能接回核心设定、线索网络、威胁时钟和可能结局。
- 若当前摘要缺少核心真相、线索链、场景节点或倒计时，继续前先补写记忆再推进。
"""

    return {
        "updated_at": exported_at,
        "public": public_resume.strip() + "\n",
        "keeper": keeper_resume.strip() + "\n",
    }


def bullet_list(items):
    if not items:
        return "- （暂无）"
    return "\n".join(f"- {item}" for item in items)


def render_markdown(memory):
    meta = memory["meta"]
    public = memory["public"]
    keeper = memory["keeper"]
    scenario = memory["scenario"]
    resume = memory.get("resume", {})
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
| 最近存档 | {meta.get('last_save_at', '')} |
| 创建时间 | {meta.get('created_at', '')} |
| 更新时间 | {meta.get('updated_at', '')} |

## 续跑摘要（玩家可知）

{resume.get('public') or '- （下次存档时自动生成）'}

## Keeper 续跑摘要（不要直接展示给玩家）

{resume.get('keeper') or '- （下次存档时自动生成）'}

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

## 剧本连续性记忆（Keeper）

### 核心设定 / 剧本前提

{bullet_list(scenario.get('premise', []))}

### 分幕与结构

{bullet_list(scenario.get('acts', []))}

### 场景节点

{bullet_list(scenario.get('scene_nodes', []))}

### 线索网络

{bullet_list(scenario.get('clue_web', []))}

### NPC 剧本功能

{bullet_list(scenario.get('npc_functions', []))}

### 威胁时钟

{bullet_list(scenario.get('threat_clock', []))}

### 结局条件

{bullet_list(scenario.get('endings', []))}

### 剧本连续性备注

{bullet_list(scenario.get('continuity', []))}

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
    scenario = memory["scenario"]
    resume = memory.get("resume", {})

    print(f"# 记忆回忆: {meta.get('campaign')}")
    print(f"- 时间: {meta.get('current_time') or '未记录'}")
    print(f"- 地点: {meta.get('current_location') or '未记录'}")
    print(f"- 场景: {meta.get('current_scene') or '未记录'}")
    print(f"- 角色: {meta.get('player_characters') or '未记录'}")
    if resume.get("public"):
        print("\n## 续跑摘要（玩家可知）")
        print(resume["public"].strip())
    if args.keeper and resume.get("keeper"):
        print("\n## Keeper 续跑摘要（不要直接展示给玩家）")
        print(resume["keeper"].strip())
    print("\n## 玩家可知")
    for key in [
        "recap", "protagonist_anchor", "cast_anchor", "current_situation", "investigator_status", "known_clues",
        "npc_status", "locations", "open_questions", "items", "timeline",
    ]:
        title = key.replace("_", " ")
        print(f"\n### {title}")
        print(bullet_list(public.get(key, [])))

    if args.keeper:
        print("\n## 剧本连续性记忆（Keeper）")
        for key in ["premise", "acts", "scene_nodes", "clue_web", "npc_functions", "threat_clock", "endings", "continuity"]:
            title = key.replace("_", " ")
            print(f"\n### {title}")
            print(bullet_list(scenario.get(key, [])))

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


def cmd_save(args):
    with MemoryLock(args.name):
        memory = load_memory(args.name)
        output_path = args.output or default_save_path(args.name)
        save_path, save_data = write_save_file(memory, output_path, force=args.force)
        memory["meta"]["last_save_at"] = save_data["exported_at"]
        memory["resume"] = save_data["resume"]
        save_memory(memory)
    print(f"已导出可迁移存档: {save_path}")
    print(f"团名: {save_data['memory']['meta'].get('campaign')}")
    print(f"导出时间: {save_data['exported_at']}")
    print(f"校验值: {save_data['checksum']}")
    print("已生成续跑摘要: public + keeper + scenario")
    print("将这个 .cocsave.json 文件复制到另一台电脑后，可用 load 命令继续游玩。")


def cmd_load(args):
    memory, save_path = read_save_file(args.file)
    original_name = memory.get("meta", {}).get("campaign") or "campaign"
    target_name = args.name or original_name
    memory["meta"]["campaign"] = target_name
    resume_time = memory.get("resume", {}).get("updated_at") or memory["meta"].get("last_save_at") or now()
    memory["resume"] = build_resume(memory, resume_time)
    with MemoryLock(target_name):
        json_path, _ = memory_paths(target_name)
        if json_path.exists() and not args.force:
            raise SystemExit(f"目标记忆已存在: {json_path}。如需覆盖，请加 --force。")
        json_path, md_path = save_memory(memory)
    print(f"已导入存档: {save_path}")
    print(f"原团名: {original_name}")
    print(f"当前团名: {target_name}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print("导入后可用 recall --keeper 回忆当前进度。")


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

    save_p = sub.add_parser("save", help="导出可迁移存档")
    save_p.add_argument("--name", required=True, help="团名或模组名")
    save_p.add_argument("--output", default="", help="输出路径，默认保存到 saves/<团名>_<时间>.cocsave.json")
    save_p.add_argument("--force", action="store_true", help="覆盖同名存档")
    save_p.set_defaults(func=cmd_save)

    load_p = sub.add_parser("load", help="导入可迁移存档")
    load_p.add_argument("--file", required=True, help=".cocsave.json 存档路径")
    load_p.add_argument("--name", default="", help="导入后使用的新团名；默认沿用存档团名")
    load_p.add_argument("--force", action="store_true", help="覆盖已有同名记忆")
    load_p.set_defaults(func=cmd_load)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
