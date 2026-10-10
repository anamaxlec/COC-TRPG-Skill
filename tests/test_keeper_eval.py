import importlib.util
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "keeper_eval.py"
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("keeper_eval", SCRIPT)
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


class KeeperEvalTest(unittest.TestCase):
    def test_actor_input_contains_scene_but_not_grading_criteria(self):
        case = {"id": "blind", "references": [], "context": "林知远站在门外。", "user": "我等她说话。", "criteria": ["评分者专用标准，不提供给被测模型。"]}
        prompt = evaluation.actor_prompt(case)
        self.assertIn(case["context"], prompt)
        self.assertIn(case["user"], prompt)
        self.assertNotIn(case["criteria"][0], prompt)

    def test_missing_or_blank_responses_are_not_counted_as_passed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = [{"id": "missing"}, {"id": "blank"}]
            (root / "blank.response.txt").write_text("\n", encoding="utf-8")
            (root / "blank.grade.json").write_text('{"passed": true, "reason": "忽略了空回复"}', encoding="utf-8")
            self.assertEqual([r["status"] for r in evaluation.build_report(cases, root)], ["未运行", "未运行"])

    def test_reports_rejection_ungraded_and_invalid_grades_separately(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = [{"id": name} for name in ("failed", "ungraded", "invalid")]
            for case in cases:
                (root / f"{case['id']}.response.txt").write_text("真实待评分回复", encoding="utf-8")
            (root / "failed.grade.json").write_text('{"passed": false, "reason": "代替玩家回答问题"}', encoding="utf-8")
            (root / "invalid.grade.json").write_text('{"passed": "false", "reason": "类型错误"}', encoding="utf-8")
            self.assertEqual([r["status"] for r in evaluation.build_report(cases, root)], ["失败", "待评分", "评分无效"])

    def test_model_command_receives_stdin_and_returns_stdout(self):
        command = shlex.join([sys.executable, "-c", "import sys; print(sys.stdin.read())"])
        self.assertEqual(evaluation.run_command(command, "场景与玩家输入", 5), "场景与玩家输入")

    def test_run_preserves_actual_responses_and_failed_judgements(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            helper = root / "model_stub.py"
            helper.write_text('import json, sys\ntext = sys.stdin.read()\nif sys.argv[1] == "actor":\n print("不合格的示例回复")\nelse:\n print(json.dumps({"passed": False, "reason": "示例回复未完成场景要求"}, ensure_ascii=False))\n', encoding="utf-8")
            runner = shlex.join([sys.executable, str(helper), "actor"])
            judge = shlex.join([sys.executable, str(helper), "judge"])
            output = root / "result"
            result = subprocess.run([sys.executable, str(SCRIPT), "run", "--output-dir", str(output), "--runner", runner, "--judge", judge], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            rows = json.loads((output / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(len(rows), len(evaluation.load_cases()))
            self.assertTrue(all(row["status"] == "失败" for row in rows))
            self.assertEqual((output / "npc_question.response.txt").read_text(encoding="utf-8"), "不合格的示例回复")


if __name__ == "__main__":
    unittest.main()
