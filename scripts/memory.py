#!/usr/bin/env python3
"""
COC 跑团记忆工具。

v2 记忆以 JSON 为源数据，Markdown 和 .cocsave.json 为导出物。脚本只负责
结构化存储、渲染和校验；剧情摘要由 Keeper/Agent 在关键节点写入。
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - unavailable on Windows
    fcntl = None

try:
    import msvcrt
except ImportError:  # pragma: no cover - unavailable on POSIX
    msvcrt = None


ROOT = Path(__file__).resolve().parents[1]
LEGACY_SCENARIOS_DIR = ROOT / "scenarios"
LEGACY_SAVES_DIR = ROOT / "saves"
DATA_ENV = "COC_TRPG_DATA_DIR"
SAVE_FORMAT = "coc-trpg-skill-save"
SAVE_VERSION = 2
SCHEMA_VERSION = 2


RECORD_KINDS = ("scene", "clue", "status", "npc", "roll", "san", "clock", "decision", "note")
VISIBILITIES = ("public", "keeper")
ENTITY_TYPES = ("investigator", "npc", "location", "item")
THREAD_TYPES = ("open-question", "foreshadowing", "unresolved", "delayed-san", "hidden-roll")
THREAD_BUCKETS = {
    "open-question": "open_questions",
    "foreshadowing": "foreshadowing",
    "unresolved": "unresolved",
    "delayed-san": "delayed_san",
    "hidden-roll": "hidden_rolls",
}


EMPTY_MEMORY = {
    "schema_version": SCHEMA_VERSION,
    "meta": {
        "campaign": "",
        "era": "",
        "boundaries": "",
        "keeper_style": "",
        "player_characters": "",
        "created_at": "",
        "updated_at": "",
        "last_snapshot_at": "",
        "last_save_at": "",
    },
    "current": {
        "time": "",
        "location": "",
        "scene": "",
        "companions": "",
        "next_hook": "",
    },
    "journal": [],
    "state": {
        "investigators": {},
        "npcs": {},
        "locations": {},
        "items": {},
    },
    "clues": {},
    "threads": {
        "open_questions": {},
        "foreshadowing": {},
        "unresolved": {},
        "delayed_san": {},
        "hidden_rolls": {},
    },
    "clocks": {},
    "summaries": {
        "updated_at": "",
        "public": "",
        "keeper": "",
        "scene": "",
    },
}


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def slugify(name):
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", name.strip(), flags=re.UNICODE)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "campaign"


def default_data_dir(platform=None, environ=None, home=None):
    platform = platform or sys.platform
    environ = os.environ if environ is None else environ
    home = Path.home() if home is None else Path(home)
    if platform.startswith("win"):
        appdata = environ.get("APPDATA")
        if appdata:
            return Path(appdata).expanduser() / "coc-trpg-skill"
        userprofile = environ.get("USERPROFILE")
        if userprofile:
            return Path(userprofile).expanduser() / ".codex" / "data" / "coc-trpg-skill"
    return home / ".codex" / "data" / "coc-trpg-skill"


def resolve_data_dir(args=None):
    raw = getattr(args, "data_dir", None) if args is not None else None
    if raw:
        return Path(raw).expanduser()
    env_value = os.environ.get(DATA_ENV)
    if env_value:
        return Path(env_value).expanduser()
    return default_data_dir()


def scenarios_dir(data_dir):
    return Path(data_dir) / "scenarios"


def saves_dir(data_dir):
    return Path(data_dir) / "saves"


def memory_paths(data_dir, name):
    slug = slugify(name)
    base = scenarios_dir(data_dir)
    return base / f"{slug}_memory.json", base / f"{slug}_memory.md"


def default_save_path(data_dir, name):
    slug = slugify(name)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return saves_dir(data_dir) / f"{slug}_{stamp}.cocsave.json"


def resolve_user_path(data_dir, path):
    output_path = Path(path).expanduser()
    if output_path.is_absolute():
        return output_path
    return Path(data_dir) / output_path


class MemoryLock:
    def __init__(self, data_dir, name):
        self.path = scenarios_dir(data_dir) / f".{slugify(name)}_memory.lock"
        self.handle = None
        self.mode = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+", encoding="utf-8")
        if fcntl:
            fcntl.flock(self.handle, fcntl.LOCK_EX)
            self.mode = "fcntl"
        elif msvcrt:
            self.handle.seek(0)
            if not self.handle.read(1):
                self.handle.write("0")
                self.handle.flush()
            self.handle.seek(0)
            msvcrt.locking(self.handle.fileno(), msvcrt.LK_LOCK, 1)
            self.mode = "msvcrt"
        else:
            print("警告: 当前平台没有可用文件锁，记忆写入不会互斥。", file=sys.stderr)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.handle:
            if self.mode == "fcntl":
                fcntl.flock(self.handle, fcntl.LOCK_UN)
            elif self.mode == "msvcrt":
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            self.handle.close()


def merge_defaults(default, value):
    if isinstance(default, dict):
        result = deepcopy(default)
        if isinstance(value, dict):
            for key, item in value.items():
                result[key] = merge_defaults(default.get(key), item)
        return result
    return deepcopy(value) if value is not None else deepcopy(default)


def normalize_memory(memory):
    if memory.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit("此文件不是 v2 记忆。旧 v1 记忆请先用 archive-legacy 归档后重新建团。")
    return merge_defaults(EMPTY_MEMORY, memory)


def memory_checksum(memory):
    payload = json.dumps(memory, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_text_atomic(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def write_json_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp_path.replace(path)


def load_memory(data_dir, name):
    json_path, _ = memory_paths(data_dir, name)
    if not json_path.exists():
        raise SystemExit(f"找不到 v2 记忆文件: {json_path}")
    with json_path.open("r", encoding="utf-8") as f:
        return normalize_memory(json.load(f))


def save_memory(data_dir, memory):
    name = memory["meta"]["campaign"] or "campaign"
    json_path, md_path = memory_paths(data_dir, name)
    memory["meta"]["updated_at"] = now()
    write_json_atomic(json_path, memory)
    write_text_atomic(md_path, render_markdown(memory))
    return json_path, md_path


def create_empty_memory(args):
    stamp = now()
    memory = deepcopy(EMPTY_MEMORY)
    memory["meta"].update({
        "campaign": args.name,
        "era": args.era or "",
        "boundaries": args.boundaries or "",
        "keeper_style": args.style or "",
        "player_characters": args.characters or "",
        "created_at": stamp,
        "updated_at": stamp,
    })
    memory["current"].update({
        "location": args.location or "",
        "scene": args.scene or "",
        "companions": args.characters or "",
        "next_hook": args.hook or "",
    })
    if args.recap:
        add_journal(memory, "public", "scene", args.recap)
    return memory


def next_id(items, prefix):
    max_seen = 0
    for key in items:
        match = re.fullmatch(rf"{re.escape(prefix)}-(\d+)", str(key))
        if match:
            max_seen = max(max_seen, int(match.group(1)))
    return f"{prefix}-{max_seen + 1:03d}"


def add_journal(memory, visibility, kind, text, scene=""):
    entry = {
        "id": next_id({item.get("id", ""): item for item in memory["journal"]}, "J"),
        "time": now(),
        "visibility": visibility,
        "kind": kind,
        "scene": scene or memory["current"].get("scene", ""),
        "text": text,
    }
    memory["journal"].append(entry)
    return entry


def entity_bucket(entity_type):
    return {
        "investigator": "investigators",
        "npc": "npcs",
        "location": "locations",
        "item": "items",
    }[entity_type]


def upsert_entity(memory, args):
    bucket = entity_bucket(args.type)
    key = args.id or slugify(args.entity)
    existing = memory["state"][bucket].get(key, {})
    entity = {
        "id": key,
        "type": args.type,
        "name": args.entity,
        "visibility": args.visibility,
        "public": args.public if args.public is not None else existing.get("public", ""),
        "keeper": args.keeper if args.keeper is not None else existing.get("keeper", ""),
        "status": args.status if args.status is not None else existing.get("status", ""),
        "location": args.location if args.location is not None else existing.get("location", ""),
        "tags": split_csv(args.tags) if args.tags is not None else existing.get("tags", []),
        "notes": args.notes if args.notes is not None else existing.get("notes", ""),
        "updated_at": now(),
    }
    memory["state"][bucket][key] = entity
    return entity


def split_csv(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def upsert_clue(memory, args):
    key = args.id or next_id(memory["clues"], "C")
    existing = memory["clues"].get(key, {})
    clue = {
        "id": key,
        "text": args.text if args.text is not None else existing.get("text", ""),
        "source": args.source if args.source is not None else existing.get("source", ""),
        "points_to": args.points_to if args.points_to is not None else existing.get("points_to", ""),
        "visibility": args.visibility,
        "key_inference": args.key_inference if args.key_inference is not None else existing.get("key_inference", ""),
        "alternate_paths": split_csv(args.alternate_path) if args.alternate_path is not None else existing.get("alternate_paths", []),
        "updated_at": now(),
    }
    memory["clues"][key] = clue
    return clue


def upsert_thread(memory, args):
    bucket = THREAD_BUCKETS[args.type]
    key = args.id or next_id(memory["threads"][bucket], "T")
    existing = memory["threads"][bucket].get(key, {})
    thread = {
        "id": key,
        "type": args.type,
        "visibility": args.visibility,
        "text": args.text if args.text is not None else existing.get("text", ""),
        "status": args.status if args.status is not None else existing.get("status", "open"),
        "next": args.next if args.next is not None else existing.get("next", ""),
        "resolution": args.resolution if args.resolution is not None else existing.get("resolution", ""),
        "updated_at": now(),
    }
    memory["threads"][bucket][key] = thread
    return thread


def upsert_clock(memory, args):
    key = args.id or next_id(memory["clocks"], "K")
    existing = memory["clocks"].get(key, {})
    clock = {
        "id": key,
        "name": args.clock if args.clock is not None else existing.get("name", ""),
        "visibility": args.visibility,
        "progress": args.progress if args.progress is not None else existing.get("progress", ""),
        "trigger": args.trigger if args.trigger is not None else existing.get("trigger", ""),
        "visible_sign": args.visible if args.visible is not None else existing.get("visible_sign", ""),
        "next": args.next if args.next is not None else existing.get("next", ""),
        "status": args.status if args.status is not None else existing.get("status", "active"),
        "updated_at": now(),
    }
    memory["clocks"][key] = clock
    return clock


def visible_items(items, keeper=False):
    if keeper:
        return list(items.values())
    return [item for item in items.values() if item.get("visibility") == "public"]


def bullet_lines(items, empty="（暂无记录）"):
    if not items:
        return [f"- {empty}"]
    return [f"- {item}" for item in items]


def render_entity_line(entity, keeper=False):
    pieces = [entity.get("name", "")]
    if entity.get("status"):
        pieces.append(f"状态: {entity['status']}")
    if entity.get("location"):
        pieces.append(f"位置: {entity['location']}")
    if entity.get("public"):
        pieces.append(entity["public"])
    if keeper and entity.get("keeper"):
        pieces.append(f"Keeper: {entity['keeper']}")
    return "；".join(piece for piece in pieces if piece)


def render_clue_line(clue, keeper=False):
    pieces = [f"{clue.get('id')}: {clue.get('text', '')}"]
    if clue.get("source"):
        pieces.append(f"来源: {clue['source']}")
    if clue.get("points_to"):
        pieces.append(f"指向: {clue['points_to']}")
    if keeper and clue.get("key_inference"):
        pieces.append(f"关键推论: {clue['key_inference']}")
    if keeper and clue.get("alternate_paths"):
        pieces.append(f"替代路径: {', '.join(clue['alternate_paths'])}")
    return "；".join(piece for piece in pieces if piece)


def render_thread_line(thread):
    pieces = [f"{thread.get('id')}: {thread.get('text', '')}"]
    if thread.get("status"):
        pieces.append(f"状态: {thread['status']}")
    if thread.get("next"):
        pieces.append(f"下一步: {thread['next']}")
    if thread.get("resolution"):
        pieces.append(f"收束: {thread['resolution']}")
    return "；".join(piece for piece in pieces if piece)


def render_clock_line(clock):
    pieces = [f"{clock.get('id')}: {clock.get('name', '')}"]
    for label, key in [("进度", "progress"), ("触发", "trigger"), ("可见迹象", "visible_sign"), ("下一步", "next"), ("状态", "status")]:
        if clock.get(key):
            pieces.append(f"{label}: {clock[key]}")
    return "；".join(piece for piece in pieces if piece)


def latest_journal(memory, keeper=False, limit=8):
    entries = memory["journal"] if keeper else [entry for entry in memory["journal"] if entry.get("visibility") == "public"]
    return entries[-limit:]


def build_public_summary(memory):
    meta = memory["meta"]
    current = memory["current"]
    lines = [
        f"# {meta.get('campaign') or 'COC 跑团'} - 玩家可知续跑摘要",
        "",
        "## 当前落点",
        f"- 时代: {meta.get('era') or '未记录'}",
        f"- 时间: {current.get('time') or '未记录'}",
        f"- 地点: {current.get('location') or '未记录'}",
        f"- 场景: {current.get('scene') or '未记录'}",
        f"- 同行者: {current.get('companions') or meta.get('player_characters') or '未记录'}",
        f"- 下一轮钩子: {current.get('next_hook') or '从当前场景给出行动切口'}",
        "",
        "## 最近公开事件",
    ]
    lines.extend(bullet_lines([entry["text"] for entry in latest_journal(memory, keeper=False, limit=6)]))
    lines.extend(["", "## 调查员和公开状态"])
    investigators = visible_items(memory["state"]["investigators"], keeper=False)
    lines.extend(bullet_lines([render_entity_line(item) for item in investigators]))
    lines.extend(["", "## 已知线索"])
    clues = visible_items(memory["clues"], keeper=False)
    lines.extend(bullet_lines([render_clue_line(item) for item in clues]))
    lines.extend(["", "## 公开未解决事项"])
    public_threads = []
    for bucket in ("open_questions", "unresolved"):
        public_threads.extend(item for item in memory["threads"][bucket].values() if item.get("visibility") == "public")
    lines.extend(bullet_lines([render_thread_line(item) for item in public_threads]))
    lines.extend(["", "## 续跑入口", "- 只用玩家可知内容做极短回顾。", "- 从当前场景继续，不要重开剧情。", "- 回顾后给 2-4 个行动切口，并允许自由行动。"])
    return "\n".join(lines).strip() + "\n"


def build_keeper_summary(memory):
    meta = memory["meta"]
    current = memory["current"]
    lines = [
        f"# {meta.get('campaign') or 'COC 跑团'} - Keeper 续跑摘要",
        "",
        "## 当前控制面板",
        f"- Keeper 风格: {meta.get('keeper_style') or '平衡 Keeper'}",
        f"- 内容边界: {meta.get('boundaries') or '未记录'}",
        f"- 当前场景: {current.get('scene') or '未记录'}",
        f"- 下一轮钩子: {current.get('next_hook') or '未记录'}",
        "",
        "## 最近完整事件",
    ]
    lines.extend(bullet_lines([f"[{entry.get('visibility')}/{entry.get('kind')}] {entry.get('text')}" for entry in latest_journal(memory, keeper=True, limit=10)]))
    lines.extend(["", "## 状态快照"])
    all_entities = []
    for bucket in ("investigators", "npcs", "locations", "items"):
        all_entities.extend(memory["state"][bucket].values())
    lines.extend(bullet_lines([render_entity_line(item, keeper=True) for item in all_entities]))
    lines.extend(["", "## 线索网络"])
    lines.extend(bullet_lines([render_clue_line(item, keeper=True) for item in memory["clues"].values()]))
    lines.extend(["", "## 未结算线程"])
    all_threads = []
    for bucket in ("open_questions", "foreshadowing", "unresolved", "delayed_san", "hidden_rolls"):
        all_threads.extend(memory["threads"][bucket].values())
    lines.extend(bullet_lines([render_thread_line(item) for item in all_threads]))
    lines.extend(["", "## 威胁时钟"])
    lines.extend(bullet_lines([render_clock_line(item) for item in memory["clocks"].values()]))
    lines.extend(["", "## 续跑前核对", "- 玩家可知摘要不要混入 Keeper Only 真相。", "- 先处理暗骰、隐藏 SAN、倒计时和敌方行动。", "- NPC 真实动机、当前位置和态度要与当前状态一致。"])
    return "\n".join(lines).strip() + "\n"


def build_scene_summary(memory):
    current = memory["current"]
    latest_public = [entry["text"] for entry in latest_journal(memory, keeper=False, limit=3)]
    return "\n".join([
        f"当前场景: {current.get('scene') or '未记录'}",
        f"地点: {current.get('location') or '未记录'}",
        f"下一轮钩子: {current.get('next_hook') or '未记录'}",
        "最近公开变化:",
        *bullet_lines(latest_public),
    ]).strip() + "\n"


def refresh_summaries(memory, public_summary="", keeper_summary="", scene_summary=""):
    stamp = now()
    memory["summaries"] = {
        "updated_at": stamp,
        "public": public_summary or build_public_summary(memory),
        "keeper": keeper_summary or build_keeper_summary(memory),
        "scene": scene_summary or build_scene_summary(memory),
    }
    memory["meta"]["last_snapshot_at"] = stamp
    return memory["summaries"]


def write_save_file(data_dir, memory, output_path="", force=False):
    target = resolve_user_path(data_dir, output_path) if output_path else default_save_path(data_dir, memory["meta"]["campaign"])
    if target.exists() and not force:
        raise SystemExit(f"存档已存在: {target}。如需覆盖，请加 --force。")
    exported_at = now()
    memory_copy = normalize_memory(deepcopy(memory))
    memory_copy["meta"]["last_save_at"] = exported_at
    save_data = {
        "format": SAVE_FORMAT,
        "version": SAVE_VERSION,
        "exported_at": exported_at,
        "checksum": memory_checksum(memory_copy),
        "memory": memory_copy,
    }
    write_json_atomic(target, save_data)
    return target, save_data


def read_save_file(data_dir, path):
    save_path = resolve_user_path(data_dir, path)
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
    memory = normalize_memory(raw_memory)
    if expected and expected != memory_checksum(memory):
        raise SystemExit("存档校验失败，文件可能被改动或复制损坏。")
    return memory, save_path


def markdown_section(title, lines):
    return [f"## {title}", "", *bullet_lines(lines), ""]


def render_markdown(memory):
    meta = memory["meta"]
    current = memory["current"]
    summaries = memory.get("summaries", {})
    lines = [
        f"# {meta.get('campaign') or 'COC 跑团'} - v2 战役记忆",
        "",
        "> 玩家可知信息可以回顾；Keeper 记忆不要直接展示给玩家。",
        "",
        "## 基本信息",
        "",
        "| 项目 | 内容 |",
        "|---|---|",
        f"| 团名 / 模组名 | {meta.get('campaign', '')} |",
        f"| 时代 | {meta.get('era', '')} |",
        f"| 当前时间 | {current.get('time', '')} |",
        f"| 当前地点 | {current.get('location', '')} |",
        f"| 当前场景 | {current.get('scene', '')} |",
        f"| 同行者 | {current.get('companions', '')} |",
        f"| Keeper 风格 | {meta.get('keeper_style', '')} |",
        f"| 内容边界 | {meta.get('boundaries', '')} |",
        f"| 下一轮钩子 | {current.get('next_hook', '')} |",
        f"| 最近快照 | {meta.get('last_snapshot_at', '')} |",
        f"| 最近存档 | {meta.get('last_save_at', '')} |",
        f"| 更新时间 | {meta.get('updated_at', '')} |",
        "",
        "## 玩家可知续跑摘要",
        "",
        summaries.get("public") or "- （运行 snapshot 后生成）\n",
        "## Keeper 续跑摘要（不要直接展示给玩家）",
        "",
        summaries.get("keeper") or "- （运行 snapshot 后生成）\n",
        "## 最近场景摘要",
        "",
        summaries.get("scene") or "- （运行 snapshot 后生成）\n",
    ]

    public_journal = [f"[{item.get('kind')}] {item.get('text')}" for item in memory["journal"] if item.get("visibility") == "public"]
    keeper_journal = [f"[{item.get('kind')}] {item.get('text')}" for item in memory["journal"] if item.get("visibility") == "keeper"]
    lines.extend(markdown_section("公开事件流水", public_journal))
    lines.extend(markdown_section("Keeper 事件流水", keeper_journal))

    for title, bucket, keeper in [
        ("调查员状态", memory["state"]["investigators"], True),
        ("NPC 状态", memory["state"]["npcs"], True),
        ("地点状态", memory["state"]["locations"], True),
        ("物品状态", memory["state"]["items"], True),
    ]:
        lines.extend(markdown_section(title, [render_entity_line(item, keeper=keeper) for item in bucket.values()]))

    lines.extend(markdown_section("线索表", [render_clue_line(item, keeper=True) for item in memory["clues"].values()]))

    for title, bucket in [
        ("公开问题", memory["threads"]["open_questions"]),
        ("伏笔", memory["threads"]["foreshadowing"]),
        ("未结算事项", memory["threads"]["unresolved"]),
        ("延迟 SAN", memory["threads"]["delayed_san"]),
        ("暗骰后果", memory["threads"]["hidden_rolls"]),
    ]:
        lines.extend(markdown_section(title, [render_thread_line(item) for item in bucket.values()]))

    lines.extend(markdown_section("威胁时钟", [render_clock_line(item) for item in memory["clocks"].values()]))
    lines.extend([
        "## 下一轮前连续性检查",
        "",
        "- [ ] 当前时间、地点、同行者一致。",
        "- [ ] HP/SAN/MP/状态/物品一致。",
        "- [ ] 玩家已知线索没有混入 Keeper Only 真相。",
        "- [ ] NPC 位置、态度、秘密一致。",
        "- [ ] 暗骰、延迟 SAN、威胁时钟和未结算事项已记录。",
        "- [ ] 下一轮钩子清楚。",
        "",
    ])
    return "\n".join(lines)


def print_recall(memory, keeper=False):
    meta = memory["meta"]
    current = memory["current"]
    summaries = memory.get("summaries", {})
    print(f"# 记忆回忆: {meta.get('campaign')}")
    print(f"- 时间: {current.get('time') or '未记录'}")
    print(f"- 地点: {current.get('location') or '未记录'}")
    print(f"- 场景: {current.get('scene') or '未记录'}")
    print(f"- 同行者: {current.get('companions') or meta.get('player_characters') or '未记录'}")
    print(f"- Keeper 风格: {meta.get('keeper_style') or '平衡 Keeper'}")
    print(f"- 下一轮钩子: {current.get('next_hook') or '未记录'}")
    print("\n## 玩家可知续跑摘要")
    print((summaries.get("public") or build_public_summary(memory)).strip())
    if keeper:
        print("\n## Keeper 续跑摘要（不要直接展示给玩家）")
        print((summaries.get("keeper") or build_keeper_summary(memory)).strip())
    print("\n## 继续前检查")
    print("- 只对玩家输出玩家可知摘要。")
    print("- 先结算未处理状态，再推进当前场景。")
    print("- 给 2-4 个行动切口，并允许玩家自由行动。")


def archive_legacy_files(data_dir, force=False):
    archive_root = Path(data_dir) / "legacy_archive"
    copied = []
    sources = [
        (LEGACY_SCENARIOS_DIR, archive_root / "scenarios"),
        (LEGACY_SAVES_DIR, archive_root / "saves"),
    ]
    for source_dir, target_dir in sources:
        if not source_dir.exists():
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in sorted(source_dir.iterdir()):
            if source.name in {".gitkeep", "README.md"} or source.name.startswith("."):
                continue
            if not source.is_file():
                continue
            target = target_dir / source.name
            if target.exists() and not force:
                raise SystemExit(f"归档目标已存在: {target}。如需覆盖，请加 --force。")
            shutil.copy2(source, target)
            copied.append(target)
    return copied, archive_root


def cmd_init(args):
    data_dir = resolve_data_dir(args)
    with MemoryLock(data_dir, args.name):
        json_path, _ = memory_paths(data_dir, args.name)
        if json_path.exists() and not args.force:
            raise SystemExit(f"v2 记忆已存在: {json_path}。如需覆盖，请加 --force。")
        memory = create_empty_memory(args)
        json_path, md_path = save_memory(data_dir, memory)
    print(f"已创建 v2 记忆: {json_path}")
    print(f"已导出 Markdown: {md_path}")


def cmd_list(args):
    data_dir = resolve_data_dir(args)
    base = scenarios_dir(data_dir)
    base.mkdir(parents=True, exist_ok=True)
    files = sorted(base.glob("*_memory.json"))
    if not files:
        print("暂无 v2 记忆文件。")
        return
    for path in files:
        try:
            with path.open("r", encoding="utf-8") as f:
                memory = normalize_memory(json.load(f))
            print(f"{memory['meta'].get('campaign') or path.name}\t{path}")
        except (json.JSONDecodeError, SystemExit):
            print(f"跳过非 v2 记忆: {path}")


def cmd_record(args):
    data_dir = resolve_data_dir(args)
    with MemoryLock(data_dir, args.name):
        memory = load_memory(data_dir, args.name)
        entry = add_journal(memory, args.visibility, args.kind, args.text, args.scene)
        json_path, md_path = save_memory(data_dir, memory)
    print(f"已记录事件 {entry['id']}: {entry['text']}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def cmd_set_current(args):
    data_dir = resolve_data_dir(args)
    current_updates = {
        "time": args.time,
        "location": args.location,
        "scene": args.scene,
        "companions": args.companions,
        "next_hook": args.hook,
    }
    meta_updates = {
        "keeper_style": args.style,
        "boundaries": args.boundaries,
        "player_characters": args.characters,
    }
    with MemoryLock(data_dir, args.name):
        memory = load_memory(data_dir, args.name)
        for key, value in current_updates.items():
            if value is not None:
                memory["current"][key] = value
        for key, value in meta_updates.items():
            if value is not None:
                memory["meta"][key] = value
        json_path, md_path = save_memory(data_dir, memory)
    print("已更新当前落点。")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def cmd_entity(args):
    data_dir = resolve_data_dir(args)
    with MemoryLock(data_dir, args.name):
        memory = load_memory(data_dir, args.name)
        entity = upsert_entity(memory, args)
        json_path, md_path = save_memory(data_dir, memory)
    print(f"已更新 {args.type}: {entity['name']} ({entity['id']})")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def cmd_clue(args):
    data_dir = resolve_data_dir(args)
    with MemoryLock(data_dir, args.name):
        memory = load_memory(data_dir, args.name)
        clue = upsert_clue(memory, args)
        json_path, md_path = save_memory(data_dir, memory)
    print(f"已更新线索 {clue['id']}: {clue['text']}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def cmd_thread(args):
    data_dir = resolve_data_dir(args)
    with MemoryLock(data_dir, args.name):
        memory = load_memory(data_dir, args.name)
        thread = upsert_thread(memory, args)
        json_path, md_path = save_memory(data_dir, memory)
    print(f"已更新线程 {thread['id']}: {thread['text']}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def cmd_clock(args):
    data_dir = resolve_data_dir(args)
    with MemoryLock(data_dir, args.name):
        memory = load_memory(data_dir, args.name)
        clock = upsert_clock(memory, args)
        json_path, md_path = save_memory(data_dir, memory)
    print(f"已更新威胁时钟 {clock['id']}: {clock['name']}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def cmd_recall(args):
    data_dir = resolve_data_dir(args)
    with MemoryLock(data_dir, args.name):
        memory = load_memory(data_dir, args.name)
    print_recall(memory, keeper=args.keeper)


def cmd_snapshot(args):
    data_dir = resolve_data_dir(args)
    with MemoryLock(data_dir, args.name):
        memory = load_memory(data_dir, args.name)
        refresh_summaries(memory, args.public_summary, args.keeper_summary, args.scene_summary)
        save_path, save_data = write_save_file(data_dir, memory, args.output, args.force)
        memory["meta"]["last_save_at"] = save_data["exported_at"]
        save_memory(data_dir, memory)
    print(f"已生成 v2 快照: {save_path}")
    print(f"校验值: {save_data['checksum']}")


def cmd_load(args):
    data_dir = resolve_data_dir(args)
    memory, save_path = read_save_file(data_dir, args.file)
    original_name = memory.get("meta", {}).get("campaign") or "campaign"
    target_name = args.name or original_name
    memory["meta"]["campaign"] = target_name
    with MemoryLock(data_dir, target_name):
        json_path, _ = memory_paths(data_dir, target_name)
        if json_path.exists() and not args.force:
            raise SystemExit(f"目标 v2 记忆已存在: {json_path}。如需覆盖，请加 --force。")
        json_path, md_path = save_memory(data_dir, memory)
    print(f"已导入 v2 存档: {save_path}")
    print(f"原团名: {original_name}")
    print(f"当前团名: {target_name}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def cmd_archive_legacy(args):
    data_dir = resolve_data_dir(args)
    copied, archive_root = archive_legacy_files(data_dir, force=args.force)
    if not copied:
        print("没有找到可归档的旧 v1 文件。")
        return
    print(f"已归档旧 v1 文件到: {archive_root}")
    for path in copied:
        print(path)


def add_common_parser(sub, name, **kwargs):
    parser = sub.add_parser(name, **kwargs)
    parser.add_argument("--data-dir", default="", help=f"数据目录；优先于 {DATA_ENV}")
    return parser


def main():
    parser = argparse.ArgumentParser(description="COC 跑团 v2 记忆工具")
    sub = parser.add_subparsers(dest="cmd", required=True)

    init_p = add_common_parser(sub, "init", help="创建 v2 战役记忆")
    init_p.add_argument("--name", required=True, help="团名或模组名")
    init_p.add_argument("--era", default="", help="时代")
    init_p.add_argument("--location", default="", help="初始地点")
    init_p.add_argument("--scene", default="", help="当前场景")
    init_p.add_argument("--characters", default="", help="调查员或同行者")
    init_p.add_argument("--style", default="", help="Keeper 风格")
    init_p.add_argument("--boundaries", default="", help="内容边界")
    init_p.add_argument("--hook", default="", help="下一轮钩子")
    init_p.add_argument("--recap", default="", help="初始公开回顾")
    init_p.add_argument("--force", action="store_true", help="覆盖已有 v2 记忆")
    init_p.set_defaults(func=cmd_init)

    list_p = add_common_parser(sub, "list", help="列出 v2 记忆文件")
    list_p.set_defaults(func=cmd_list)

    record_p = add_common_parser(sub, "record", help="追加本轮事件")
    record_p.add_argument("--name", required=True, help="团名或模组名")
    record_p.add_argument("--visibility", choices=VISIBILITIES, default="public", help="玩家可知或 Keeper Only")
    record_p.add_argument("--kind", choices=RECORD_KINDS, required=True, help="事件类型")
    record_p.add_argument("--text", required=True, help="事件内容")
    record_p.add_argument("--scene", default="", help="事件所属场景；默认当前场景")
    record_p.set_defaults(func=cmd_record)

    current_p = add_common_parser(sub, "set-current", help="更新当前落点")
    current_p.add_argument("--name", required=True, help="团名或模组名")
    current_p.add_argument("--time", default=None, help="当前时间")
    current_p.add_argument("--location", default=None, help="当前地点")
    current_p.add_argument("--scene", default=None, help="当前场景")
    current_p.add_argument("--companions", default=None, help="同行者")
    current_p.add_argument("--hook", default=None, help="下一轮钩子")
    current_p.add_argument("--style", default=None, help="Keeper 风格")
    current_p.add_argument("--boundaries", default=None, help="内容边界")
    current_p.add_argument("--characters", default=None, help="调查员")
    current_p.set_defaults(func=cmd_set_current)

    entity_p = add_common_parser(sub, "entity", help="维护调查员、NPC、地点或物品状态")
    entity_p.add_argument("--name", required=True, help="团名或模组名")
    entity_p.add_argument("--entity", required=True, help="实体名称")
    entity_p.add_argument("--type", required=True, choices=ENTITY_TYPES, help="实体类型")
    entity_p.add_argument("--id", default="", help="实体 ID；默认由名称生成")
    entity_p.add_argument("--visibility", choices=VISIBILITIES, default="public", help="默认可见性")
    entity_p.add_argument("--public", default=None, help="玩家可知状态")
    entity_p.add_argument("--keeper", default=None, help="Keeper Only 状态")
    entity_p.add_argument("--status", default=None, help="状态")
    entity_p.add_argument("--location", default=None, help="当前位置")
    entity_p.add_argument("--tags", default=None, help="逗号分隔标签")
    entity_p.add_argument("--notes", default=None, help="备注")
    entity_p.set_defaults(func=cmd_entity)

    clue_p = add_common_parser(sub, "clue", help="新增或更新线索")
    clue_p.add_argument("--name", required=True, help="团名或模组名")
    clue_p.add_argument("--id", default="", help="线索 ID；默认 C-001 递增")
    clue_p.add_argument("--text", default=None, help="线索内容")
    clue_p.add_argument("--source", default=None, help="线索来源")
    clue_p.add_argument("--points-to", default=None, help="线索指向")
    clue_p.add_argument("--visibility", choices=VISIBILITIES, default="public", help="公开或 Keeper Only")
    clue_p.add_argument("--key-inference", default=None, help="关键推论")
    clue_p.add_argument("--alternate-path", default=None, help="逗号分隔替代路径")
    clue_p.set_defaults(func=cmd_clue)

    thread_p = add_common_parser(sub, "thread", help="维护问题、伏笔和未结算事项")
    thread_p.add_argument("--name", required=True, help="团名或模组名")
    thread_p.add_argument("--id", default="", help="线程 ID；默认 T-001 递增")
    thread_p.add_argument("--type", required=True, choices=THREAD_TYPES, help="线程类型")
    thread_p.add_argument("--visibility", choices=VISIBILITIES, default="keeper", help="公开或 Keeper Only")
    thread_p.add_argument("--text", default=None, help="线程内容")
    thread_p.add_argument("--status", default=None, help="状态")
    thread_p.add_argument("--next", default=None, help="下一步")
    thread_p.add_argument("--resolution", default=None, help="收束方式")
    thread_p.set_defaults(func=cmd_thread)

    clock_p = add_common_parser(sub, "clock", help="维护威胁时钟和敌方行动")
    clock_p.add_argument("--name", required=True, help="团名或模组名")
    clock_p.add_argument("--id", default="", help="时钟 ID；默认 K-001 递增")
    clock_p.add_argument("--clock", default=None, help="时钟名称")
    clock_p.add_argument("--visibility", choices=VISIBILITIES, default="keeper", help="公开或 Keeper Only")
    clock_p.add_argument("--progress", default=None, help="当前进度")
    clock_p.add_argument("--trigger", default=None, help="触发条件")
    clock_p.add_argument("--visible", default=None, help="玩家可感知迹象")
    clock_p.add_argument("--next", default=None, help="下一步")
    clock_p.add_argument("--status", default=None, help="状态")
    clock_p.set_defaults(func=cmd_clock)

    recall_p = add_common_parser(sub, "recall", help="读取续团摘要")
    recall_p.add_argument("--name", required=True, help="团名或模组名")
    recall_p.add_argument("--keeper", action="store_true", help="包含 Keeper Only 摘要")
    recall_p.set_defaults(func=cmd_recall)

    snapshot_p = add_common_parser(sub, "snapshot", help="生成续跑快照和 .cocsave.json")
    snapshot_p.add_argument("--name", required=True, help="团名或模组名")
    snapshot_p.add_argument("--public-summary", default="", help="玩家可知续跑摘要；不填则自动汇总")
    snapshot_p.add_argument("--keeper-summary", default="", help="Keeper 续跑摘要；不填则自动汇总")
    snapshot_p.add_argument("--scene-summary", default="", help="最近场景摘要；不填则自动汇总")
    snapshot_p.add_argument("--output", default="", help="输出路径；相对路径按 data dir 解析")
    snapshot_p.add_argument("--force", action="store_true", help="覆盖同名存档")
    snapshot_p.set_defaults(func=cmd_snapshot)

    load_p = add_common_parser(sub, "load", help="导入 v2 .cocsave.json")
    load_p.add_argument("--file", required=True, help=".cocsave.json 存档路径")
    load_p.add_argument("--name", default="", help="导入后使用的新团名；默认沿用存档团名")
    load_p.add_argument("--force", action="store_true", help="覆盖已有同名 v2 记忆")
    load_p.set_defaults(func=cmd_load)

    archive_p = add_common_parser(sub, "archive-legacy", help="归档旧 v1 scenarios/saves 文件")
    archive_p.add_argument("--force", action="store_true", help="覆盖已有归档文件")
    archive_p.set_defaults(func=cmd_archive_legacy)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
