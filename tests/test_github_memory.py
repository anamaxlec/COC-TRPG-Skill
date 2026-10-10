import os
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import github_memory as sync
import memory


class GithubMemoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = mock.patch.dict(os.environ, {
            "GIT_CONFIG_GLOBAL": str(self.root / "empty-config"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "COC Test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "COC Test", "GIT_COMMITTER_EMAIL": "test@example.invalid",
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.remote = self.root / "remote.git"
        sync.git(self.root, "init", "--bare", "--quiet", str(self.remote))
        seed = self.root / "seed"
        seed.mkdir()
        sync.git(seed, "init", "--quiet")
        sync.git(seed, "symbolic-ref", "HEAD", "refs/heads/main")
        (seed / "SKILL.md").write_text("Original skill code\n", encoding="utf-8")
        sync.git(seed, "add", "SKILL.md")
        sync.git(seed, "commit", "--quiet", "-m", "Initial skill")
        sync.git(seed, "push", str(self.remote), "HEAD:refs/heads/main")
        self.main_before = sync.git(self.remote, "rev-parse", "refs/heads/main").stdout
        self.a = self.client("machine-a")
        self.b = self.client("machine-b")

    def client(self, name):
        path = self.root / name
        sync.configure(path, self.remote.as_uri())
        return path

    def create(self, client, name="榕渊", scene="旧屋"):
        value = deepcopy(memory.EMPTY_MEMORY)
        value["meta"]["campaign"] = name
        value["current"]["scene"] = scene
        value["state"]["npcs"]["keeper-secret"] = {
            "name": "馆长", "visibility": "keeper", "keeper": "幕后主使",
        }
        memory.save_memory(client, value)

    def edit(self, client, scene, name="榕渊"):
        value = memory.load_memory(client, name)
        value["current"]["scene"] = scene
        memory.save_memory(client, value)

    def test_round_trip_preserves_keeper_and_leaves_main_untouched(self):
        self.create(self.a)
        path, _ = sync.push(self.a, "榕渊", True)
        self.assertEqual(sync.list_cloud(self.b), [path])
        sync.pull(self.b, "榕渊")
        value = memory.load_memory(self.b, "榕渊")
        self.assertEqual(value["current"]["scene"], "旧屋")
        self.assertEqual(value["state"]["npcs"]["keeper-secret"]["keeper"], "幕后主使")
        self.assertEqual(sync.git(self.remote, "rev-parse", "refs/heads/main").stdout, self.main_before)
        files = sync.git(self.remote, "ls-tree", "-r", "--name-only", "refs/heads/coc-saves").stdout
        self.assertNotIn("SKILL.md", files)
        self.assertEqual(len(files.splitlines()), 1)

    def test_upload_requires_explicit_full_save_scope(self):
        self.create(self.a)
        with self.assertRaises(SystemExit):
            sync.push(self.a, "榕渊")
        self.assertEqual(sync.list_cloud(self.a), [])

    def test_remote_newer_save_blocks_stale_upload(self):
        self.create(self.a)
        sync.push(self.a, "榕渊", True)
        sync.pull(self.b, "榕渊")
        self.edit(self.a, "码头")
        sync.push(self.a, "榕渊", True)
        self.edit(self.b, "医院")
        with self.assertRaisesRegex(SystemExit, "云端同团存档已变化"):
            sync.push(self.b, "榕渊", True)
        self.assertEqual(memory.load_memory(self.b, "榕渊")["current"]["scene"], "医院")

    def test_pulling_another_campaign_does_not_authorize_stale_overwrite(self):
        self.create(self.a)
        sync.push(self.a, "榕渊", True)
        sync.pull(self.b, "榕渊")
        self.edit(self.a, "码头")
        sync.push(self.a, "榕渊", True)
        self.create(self.a, "新团")
        sync.push(self.a, "新团", True)
        sync.pull(self.b, "新团")
        with self.assertRaisesRegex(SystemExit, "云端同团存档已变化"):
            sync.push(self.b, "榕渊", True)

    def test_replace_local_requires_flag_and_retains_backup(self):
        self.create(self.a)
        sync.push(self.a, "榕渊", True)
        sync.pull(self.b, "榕渊")
        self.edit(self.b, "本地支线")
        with self.assertRaisesRegex(SystemExit, "本地已有同名"):
            sync.pull(self.b, "榕渊")
        backup = sync.pull(self.b, "榕渊", replace_local=True)
        prior, _ = memory.read_save_file(self.b, str(backup))
        self.assertEqual(prior["current"]["scene"], "本地支线")
        self.assertEqual(memory.load_memory(self.b, "榕渊")["current"]["scene"], "旧屋")

    def test_existing_remote_campaign_requires_pull_on_new_machine(self):
        self.create(self.a)
        sync.push(self.a, "榕渊", True)
        self.create(self.b, scene="完全不同的团")
        with self.assertRaisesRegex(SystemExit, "从未同步"):
            sync.push(self.b, "榕渊", True)

    def test_failed_push_can_retry_but_not_upload_other_campaign_silently(self):
        self.create(self.a)
        real_git = sync.git

        def offline(repo, *args, **kwargs):
            if args[0] == "push":
                raise SystemExit("模拟网络故障")
            return real_git(repo, *args, **kwargs)

        with mock.patch.object(sync, "git", side_effect=offline), self.assertRaises(SystemExit):
            sync.push(self.a, "榕渊", True)
        self.create(self.a, "另一团")
        with self.assertRaisesRegex(SystemExit, "其他团档"):
            sync.push(self.a, "另一团", True)
        sync.push(self.a, "榕渊", True)
        self.assertEqual(len(sync.list_cloud(self.b)), 1)

    def test_remote_race_is_rejected_without_force_push(self):
        self.create(self.a)
        sync.push(self.a, "榕渊", True)
        sync.pull(self.b, "榕渊")
        self.edit(self.a, "A 的进度")
        self.edit(self.b, "B 的进度")
        real_git = sync.git
        raced = False

        def race(repo, *args, **kwargs):
            nonlocal raced
            if args[0] == "push" and Path(repo) == self.b / "github-cache" and not raced:
                raced = True
                sync.push(self.a, "榕渊", True)
            return real_git(repo, *args, **kwargs)

        with mock.patch.object(sync, "git", side_effect=race), self.assertRaises(SystemExit):
            sync.push(self.b, "榕渊", True)
        third = self.client("machine-c")
        sync.pull(third, "榕渊")
        self.assertEqual(memory.load_memory(third, "榕渊")["current"]["scene"], "A 的进度")
        self.assertEqual(memory.load_memory(self.b, "榕渊")["current"]["scene"], "B 的进度")

    def test_reconfigure_and_repository_input_validation(self):
        with self.assertRaises(SystemExit):
            sync.configure(self.a, "https://github.com/someone/else.git")
        for value in ("https://github.com/me/repo", "me/repo;echo", "-flag/repo", "me/.."):
            with self.subTest(repo=value), self.assertRaises(SystemExit):
                sync.github_url(value)
        self.assertEqual(sync.github_url("me/COC-TRPG-Skill"), "https://github.com/me/COC-TRPG-Skill.git")

    def test_bad_remote_save_is_not_imported(self):
        self.create(self.a)
        sync.push(self.a, "榕渊", True)
        cache = self.a / "github-cache"
        path = cache / sync.save_relative_path("榕渊")
        path.write_text('{"format": "not-a-save"}', encoding="utf-8")
        sync.git(cache, "add", ".")
        sync.git(cache, "commit", "--quiet", "-m", "Bad archive")
        sync.git(cache, "push", "origin", "HEAD:refs/heads/coc-saves")
        with self.assertRaises(SystemExit):
            sync.pull(self.b, "榕渊")
        self.assertFalse(memory.memory_paths(self.b, "榕渊")[0].exists())


if __name__ == "__main__":
    unittest.main()
