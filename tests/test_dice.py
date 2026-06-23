import importlib.util
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_dice_module():
    spec = importlib.util.spec_from_file_location("dice_script", ROOT / "scripts" / "dice.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DiceRulesTest(unittest.TestCase):
    def test_d100_result_100_is_fumble_even_for_high_skill(self):
        dice = load_dice_module()
        detail = {"tens": [0], "ones": 0, "selected_tens": 0}
        with mock.patch.object(dice, "roll_d100", return_value=(100, detail)):
            self.assertIn("FUMBLE", dice.d100_check(100)[1])
            self.assertIn("FUMBLE", dice.d100_check(120)[1])

    def test_d100_result_1_is_critical(self):
        dice = load_dice_module()
        detail = {"tens": [0], "ones": 1, "selected_tens": 0}
        with mock.patch.object(dice, "roll_d100", return_value=(1, detail)):
            self.assertIn("CRITICAL", dice.d100_check(5)[1])

    def test_zero_san_loss_does_not_trigger_indefinite_insanity(self):
        dice = load_dice_module()
        with mock.patch.object(dice, "parse_san_loss", return_value=(50, "失败 FAIL", "0", 0, [])):
            _loss, _new_san, output = dice.san_check(4, "0/0")
        self.assertFalse(any("不定疯狂" in item for item in output))

    def test_low_san_indefinite_threshold_uses_ceil(self):
        dice = load_dice_module()
        with mock.patch.object(dice, "parse_san_loss", return_value=(50, "失败 FAIL", "1", 1, [])):
            _loss, _new_san, output = dice.san_check(4, "0/1")
        self.assertTrue(any("不定疯狂" in item for item in output))


if __name__ == "__main__":
    unittest.main()
