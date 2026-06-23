import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RandomNameTest(unittest.TestCase):
    def test_modern_cn_returns_chinese_name(self):
        names = load_module("random_name_script", "scripts/random_name.py")
        with mock.patch.object(names.random, "choice", side_effect=lambda seq: seq[0]):
            generated = names.generate_name("modern", "male", "cn")
        self.assertEqual(generated, names.CN_SURNAME[0] + names.CN_MODERN_MALE[0])

    def test_modern_us_uses_modern_pool(self):
        names = load_module("random_name_script", "scripts/random_name.py")
        with mock.patch.object(names.random, "choice", side_effect=lambda seq: seq[0]):
            generated = names.generate_name("modern", "female", "us")
        self.assertEqual(generated, f"{names.FIRST_FEMALE_MODERN[0]} {names.LAST_NAMES_MODERN[0]}")

    def test_gender_argument_applies_to_all_generated_names(self):
        result = subprocess.run(
            [sys.executable, "scripts/random_name.py", "--era", "modern", "--region", "cn", "--gender", "male", "--count", "5"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.stdout.count("(male, modern)"), 5)
        self.assertNotIn("(female, modern)", result.stdout)


class RandomEncounterTest(unittest.TestCase):
    def test_modern_rural_uses_rural_scene_and_npc(self):
        encounters = load_module("random_encounter_script", "scripts/random_encounter.py")
        with mock.patch.object(encounters.random, "choice", side_effect=lambda seq: seq[0]):
            scene, npc = encounters.generate_encounter("modern", "rural")
        self.assertEqual(scene, encounters.MODERN_RURAL[0])
        self.assertEqual(npc, encounters.MODERN_RURAL_NPC[0])
        self.assertNotEqual(npc, "（NPC由Keeper即兴发挥）")

    def test_modern_urban_has_npc_pool(self):
        encounters = load_module("random_encounter_script", "scripts/random_encounter.py")
        with mock.patch.object(encounters.random, "choice", side_effect=lambda seq: seq[0]):
            scene, npc = encounters.generate_encounter("modern", "urban")
        self.assertEqual(scene, encounters.MODERN_URBAN[0])
        self.assertEqual(npc, encounters.MODERN_URBAN_NPC[0])


if __name__ == "__main__":
    unittest.main()
