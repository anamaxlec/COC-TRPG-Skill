import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "memory.py"


def load_memory_module():
    spec = importlib.util.spec_from_file_location("memory_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MemoryCliTest(unittest.TestCase):
    def run_cmd(self, data_dir, *args):
        cmd = [sys.executable, str(SCRIPT), *args]
        env = os.environ.copy()
        env.pop("COC_TRPG_DATA_DIR", None)
        result = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        return result.stdout

    def test_edits_after_snapshot_are_visible_immediately(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cmd(tmp, "init", "--data-dir", tmp, "--name", "续团")
            self.run_cmd(tmp, "entity", "--data-dir", tmp, "--name", "续团", "--type", "investigator", "--entity", "调查员", "--status", "HP 12")
            self.run_cmd(tmp, "snapshot", "--data-dir", tmp, "--name", "续团")
            self.run_cmd(tmp, "entity", "--data-dir", tmp, "--name", "续团", "--type", "investigator", "--entity", "调查员", "--status", "HP 7")
            out = self.run_cmd(tmp, "recall", "--data-dir", tmp, "--name", "续团", "--keeper")
            self.assertIn("HP 7", out)
            self.assertNotIn("HP 12", out)

    def test_keeper_hook_is_private_before_and_after_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            public = "门外响起敲门声，调查员尚未开门"
            secret = "今晚凶手会伪装成警察登门"
            self.run_cmd(tmp, "init", "--data-dir", tmp, "--name", "钩子隔离", "--public-hook", public, "--keeper-hook", secret)
            for snapshot in (False, True):
                if snapshot:
                    self.run_cmd(tmp, "snapshot", "--data-dir", tmp, "--name", "钩子隔离")
                with self.subTest(snapshot=snapshot):
                    player = self.run_cmd(tmp, "recall", "--data-dir", tmp, "--name", "钩子隔离")
                    keeper = self.run_cmd(tmp, "recall", "--data-dir", tmp, "--name", "钩子隔离", "--keeper")
                    self.assertIn(public, player)
                    self.assertNotIn(secret, player)
                    self.assertIn(secret, keeper)
            memory = load_memory_module().load_memory(tmp, "钩子隔离")
            self.assertNotIn(secret, memory["summaries"]["scene"])

    def test_player_character_and_companions_are_distinct_in_recall(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cmd(tmp, "init", "--data-dir", tmp, "--name", "人物身份", "--characters", "林知远")
            self.run_cmd(tmp, "snapshot", "--data-dir", tmp, "--name", "人物身份")
            out = self.run_cmd(tmp, "recall", "--data-dir", tmp, "--name", "人物身份")
            self.assertIn("玩家调查员: 林知远", out)
            self.assertNotIn("同行者: 林知远", out)
            self.run_cmd(tmp, "set-current", "--data-dir", tmp, "--name", "人物身份", "--companions", "门卫李青")
            out = self.run_cmd(tmp, "recall", "--data-dir", tmp, "--name", "人物身份")
            self.assertIn("玩家调查员: 林知远", out)
            self.assertIn("同行者: 门卫李青", out)

    def test_hook_alias_is_private_and_public_updates_preserve_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            secret = "地下室的守卫将在午夜撤走"
            self.run_cmd(tmp, "init", "--data-dir", tmp, "--name", "旧口令", "--hook", secret)
            self.run_cmd(tmp, "set-current", "--data-dir", tmp, "--name", "旧口令", "--public-hook", "刚到走廊")
            player = self.run_cmd(tmp, "recall", "--data-dir", tmp, "--name", "旧口令")
            self.assertIn("刚到走廊", player)
            self.assertNotIn(secret, player)
            self.run_cmd(tmp, "set-current", "--data-dir", tmp, "--name", "旧口令", "--public-hook", "")
            memory = load_memory_module().load_memory(tmp, "旧口令")
            self.assertEqual(memory["current"]["public_hook"], "")
            self.assertEqual(memory["current"]["next_hook"], secret)

    def test_updates_preserve_visibility_and_closed_threads_leave_recall(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cmd(tmp, "init", "--data-dir", tmp, "--name", "隔离")
            self.run_cmd(tmp, "clue", "--data-dir", tmp, "--name", "隔离", "--id", "C-001", "--visibility", "keeper", "--text", "馆长是幕后主使")
            self.run_cmd(tmp, "clue", "--data-dir", tmp, "--name", "隔离", "--id", "C-001", "--source", "地下室")
            self.run_cmd(tmp, "entity", "--data-dir", tmp, "--name", "隔离", "--type", "investigator", "--entity", "秘密调查员", "--visibility", "keeper")
            self.run_cmd(tmp, "entity", "--data-dir", tmp, "--name", "隔离", "--type", "investigator", "--entity", "秘密调查员", "--status", "失踪")
            self.run_cmd(tmp, "thread", "--data-dir", tmp, "--name", "隔离", "--type", "unresolved", "--id", "T-001", "--visibility", "public", "--text", "尚待送信")
            self.run_cmd(tmp, "thread", "--data-dir", tmp, "--name", "隔离", "--type", "unresolved", "--id", "T-001", "--status", "resolved")
            out = self.run_cmd(tmp, "recall", "--data-dir", tmp, "--name", "隔离")
            self.assertNotIn("馆长是幕后主使", out)
            self.assertNotIn("秘密调查员", out)
            self.assertNotIn("尚待送信", out)
            data = load_memory_module().load_memory(tmp, "隔离")
            self.assertEqual(data["threads"]["unresolved"]["T-001"]["visibility"], "public")
            self.assertEqual(data["threads"]["unresolved"]["T-001"]["status"], "resolved")

    def test_v2_flow_and_keeper_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cmd(
                tmp,
                "init", "--data-dir", tmp, "--name", "榕渊", "--era", "modern",
                "--location", "福州", "--scene", "旧仓山洋楼", "--characters", "林知远",
                "--style", "平衡 Keeper", "--public-hook", "二层潮湿手印",
            )
            self.run_cmd(tmp, "record", "--data-dir", tmp, "--name", "榕渊", "--visibility", "public", "--kind", "scene", "--text", "调查员进入旧仓山洋楼。")
            self.run_cmd(tmp, "record", "--data-dir", tmp, "--name", "榕渊", "--visibility", "keeper", "--kind", "note", "--text", "墙内有未公开的仪式残留。")
            self.run_cmd(tmp, "entity", "--data-dir", tmp, "--name", "榕渊", "--type", "investigator", "--entity", "林知远", "--status", "HP 12 SAN 50", "--public", "携带相机和旧报纸")
            self.run_cmd(tmp, "clue", "--data-dir", tmp, "--name", "榕渊", "--id", "C-001", "--text", "二层门把手有潮湿手印", "--source", "洋楼二层", "--points-to", "有人刚离开", "--visibility", "public")
            self.run_cmd(tmp, "thread", "--data-dir", tmp, "--name", "榕渊", "--type", "unresolved", "--visibility", "keeper", "--text", "延迟公开 SAN 1 点", "--next", "真相揭露时结算")
            self.run_cmd(tmp, "clock", "--data-dir", tmp, "--name", "榕渊", "--clock", "仪式推进", "--progress", "1/4", "--trigger", "拖延", "--visible", "墙纸渗水")
            self.run_cmd(tmp, "set-current", "--data-dir", tmp, "--name", "榕渊", "--style", "剧情沉浸", "--boundaries", "淡化身体恐怖")
            self.run_cmd(tmp, "snapshot", "--data-dir", tmp, "--name", "榕渊")

            public_out = self.run_cmd(tmp, "recall", "--data-dir", tmp, "--name", "榕渊")
            self.assertIn("调查员进入旧仓山洋楼", public_out)
            self.assertIn("二层门把手有潮湿手印", public_out)
            self.assertNotIn("墙内有未公开的仪式残留", public_out)
            self.assertNotIn("延迟公开 SAN", public_out)

            keeper_out = self.run_cmd(tmp, "recall", "--data-dir", tmp, "--name", "榕渊", "--keeper")
            self.assertIn("墙内有未公开的仪式残留", keeper_out)
            self.assertIn("延迟公开 SAN", keeper_out)
            self.assertIn("仪式推进", keeper_out)
            self.assertIn("剧情沉浸", keeper_out)
            self.assertIn("淡化身体恐怖", keeper_out)

            memory_path = Path(tmp) / "scenarios" / "榕渊_memory.json"
            with memory_path.open("r", encoding="utf-8") as f:
                memory = json.load(f)
            self.assertEqual(memory["schema_version"], 2)
            self.assertEqual(memory["current"]["scene"], "旧仓山洋楼")
            self.assertEqual(memory["clues"]["C-001"]["visibility"], "public")
            self.assertTrue(list((Path(tmp) / "saves").glob("*.cocsave.json")))

    def test_load_v2_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cmd(tmp, "init", "--data-dir", tmp, "--name", "原团", "--era", "modern")
            self.run_cmd(tmp, "snapshot", "--data-dir", tmp, "--name", "原团")
            save_path = next((Path(tmp) / "saves").glob("*.cocsave.json"))
            self.run_cmd(tmp, "load", "--data-dir", tmp, "--file", str(save_path), "--name", "导入团")
            out = self.run_cmd(tmp, "list", "--data-dir", tmp)
            self.assertIn("原团", out)
            self.assertIn("导入团", out)
            for scope in ([], ["--keeper"]):
                out = self.run_cmd(tmp, "recall", "--data-dir", tmp, "--name", "导入团", *scope)
                self.assertIn("导入团", out)
                self.assertNotIn("原团", out)
            imported = load_memory_module().load_memory(tmp, "导入团")
            self.assertIn("# 导入团", imported["summaries"]["public"])
            self.assertIn("# 导入团", imported["summaries"]["keeper"])

    def test_env_data_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["COC_TRPG_DATA_DIR"] = tmp
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "init", "--name", "环境团"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn(str(Path(tmp) / "scenarios" / "环境团_memory.json"), result.stdout)


class MemoryModuleTest(unittest.TestCase):
    def legacy_save(self, memory, path):
        value = deepcopy(memory.EMPTY_MEMORY)
        value["meta"]["campaign"] = "旧格式"
        value["meta"]["player_characters"] = "林知远"
        value["current"]["companions"] = "林知远"
        value["current"].pop("public_hook")
        secret = "凶手将在今晚伪装成警察"
        value["current"]["next_hook"] = secret
        value["summaries"]["public"] = "旧公开摘要：" + secret
        value["summaries"]["scene"] = "旧场景摘要：" + secret
        value["summaries"]["keeper"] = "Keeper 备忘：" + secret
        payload = {"format": memory.SAVE_FORMAT, "version": 2, "memory": value, "checksum": memory.memory_checksum(value)}
        memory.write_json_atomic(path, payload)
        return payload, secret

    def test_legacy_save_keeps_hook_private_and_discards_public_caches(self):
        memory = load_memory_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "old.cocsave.json"
            _, secret = self.legacy_save(memory, path)
            original = path.read_bytes()
            loaded, _ = memory.read_save_file(tmp, str(path))
            self.assertEqual(loaded["current"]["next_hook"], secret)
            self.assertEqual(loaded["current"]["public_hook"], "")
            self.assertEqual(loaded["summaries"]["public"], "")
            self.assertEqual(loaded["summaries"]["scene"], "")
            self.assertNotIn(secret, memory.build_public_summary(loaded))
            self.assertNotIn(secret, memory.build_scene_summary(loaded))
            self.assertIn(secret, memory.build_keeper_summary(loaded))
            self.assertIn(secret, loaded["summaries"]["keeper"])
            self.assertIn("玩家调查员: 林知远", memory.build_public_summary(loaded))
            self.assertNotIn("同行者: 林知远", memory.build_public_summary(loaded))
            self.assertEqual(path.read_bytes(), original)

    def test_legacy_payload_integrity_is_checked_before_migration(self):
        memory = load_memory_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tampered.cocsave.json"
            payload, _ = self.legacy_save(memory, path)
            payload["memory"]["summaries"]["public"] = "已被篡改的旧缓存"
            memory.write_json_atomic(path, payload)
            with self.assertRaisesRegex(SystemExit, "校验失败"):
                memory.read_save_file(tmp, str(path))

    def test_malformed_import_shapes_are_rejected(self):
        memory = load_memory_module()
        for patch in ({"state": {"npcs": []}}, {"journal": [{}]}, {"clues": {"C-001": "not-an-object"}}):
            value = {"schema_version": 2, "meta": {"campaign": "输入检查"}, **patch}
            with self.subTest(patch=patch), self.assertRaises(SystemExit):
                memory.normalize_memory(value)

    def test_default_data_dir_platforms(self):
        memory = load_memory_module()
        mac_dir = memory.default_data_dir(platform="darwin", environ={}, home=Path("/Users/example"))
        self.assertEqual(mac_dir, Path("/Users/example/.codex/data/coc-trpg-skill"))
        win_dir = memory.default_data_dir(
            platform="win32",
            environ={"APPDATA": r"C:\Users\example\AppData\Roaming"},
            home=Path("/ignored"),
        )
        self.assertTrue(str(win_dir).endswith("coc-trpg-skill"))
        fallback = memory.default_data_dir(
            platform="win32",
            environ={"USERPROFILE": r"C:\Users\example"},
            home=Path("/ignored"),
        )
        self.assertIn(".codex", str(fallback))

    def test_memory_lock_creates_lock_file(self):
        memory = load_memory_module()
        with tempfile.TemporaryDirectory() as tmp:
            with memory.MemoryLock(Path(tmp), "锁测试"):
                lock_path = Path(tmp) / "scenarios" / ".锁测试_memory.lock"
                self.assertTrue(lock_path.exists())

    def test_archive_legacy_copies_without_deleting(self):
        memory = load_memory_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy_scenarios = root / "legacy" / "scenarios"
            legacy_saves = root / "legacy" / "saves"
            legacy_scenarios.mkdir(parents=True)
            legacy_saves.mkdir(parents=True)
            old_memory = legacy_scenarios / "旧团_memory.json"
            old_save = legacy_saves / "旧团.cocsave.json"
            old_memory.write_text('{"schema_version": 1}\n', encoding="utf-8")
            old_save.write_text('{"version": 1}\n', encoding="utf-8")

            original_scenarios = memory.LEGACY_SCENARIOS_DIR
            original_saves = memory.LEGACY_SAVES_DIR
            memory.LEGACY_SCENARIOS_DIR = legacy_scenarios
            memory.LEGACY_SAVES_DIR = legacy_saves
            try:
                copied, archive_root = memory.archive_legacy_files(root / "data")
            finally:
                memory.LEGACY_SCENARIOS_DIR = original_scenarios
                memory.LEGACY_SAVES_DIR = original_saves

            self.assertEqual(len(copied), 2)
            self.assertTrue((archive_root / "scenarios" / old_memory.name).exists())
            self.assertTrue((archive_root / "saves" / old_save.name).exists())
            self.assertTrue(old_memory.exists())
            self.assertTrue(old_save.exists())


if __name__ == "__main__":
    unittest.main()
