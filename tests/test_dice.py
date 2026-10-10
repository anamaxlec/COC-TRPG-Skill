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
            _loss, _new_san, output = dice.san_check(4, "0/1", day_start_san=4)
        self.assertTrue(any("不定疯狂" in item for item in output))

    def test_five_san_loss_requires_int_before_temporary_insanity(self):
        dice = load_dice_module()
        with mock.patch.object(dice, "parse_san_loss", return_value=(80, "失败 FAIL", "5", 5, [])):
            output = dice.san_check(60, "0/5")[2]
            self.assertTrue(any("待 INT 检定" in s for s in output))
            with mock.patch.object(dice.RNG, "randint", return_value=90):
                output = dice.san_check(60, "0/5", int_value=60)[2]
                self.assertIn("INT 失败 -> 未触发临时疯狂", output)
            with mock.patch.object(dice.RNG, "randint", return_value=2):
                output = dice.san_check(60, "0/5", int_value=60)[2]
                self.assertIn("INT 成功 -> 临时疯狂 (2 小时)", output)

    def test_indefinite_insanity_accumulates_over_game_day(self):
        dice = load_dice_module()
        with mock.patch.object(dice, "parse_san_loss", return_value=(80, "失败 FAIL", "3", 3, [])):
            output = dice.san_check(51, "0/3", day_start_san=60, lost_today=9)[2]
            self.assertTrue(any("-> 不定疯狂" in s for s in output))
            output = dice.san_check(51, "0/3")[2]
            self.assertFalse(any("-> 不定疯狂" in s for s in output))

    def test_san_never_negative_and_zero_takes_precedence(self):
        dice = load_dice_module()
        loss, value, output = dice.san_check(4, "8", int_value=60, day_start_san=4)
        self.assertEqual((loss, value), (8, 0))
        self.assertTrue(any("永久疯狂" in s for s in output))
        self.assertFalse(any("INT 检定" in s for s in output))

    def test_invalid_dice_expression_is_not_silently_repaired(self):
        dice = load_dice_module()
        for expr in ("1d6++2", "1d6-", "--2", "+", "0d6"):
            with self.subTest(expr=expr), self.assertRaises(ValueError):
                dice.roll(expr)

    def test_opposed_equal_success_compares_skill_values(self):
        dice = load_dice_module()
        with mock.patch.object(dice, "d100_check", side_effect=[(55, "常规成功 REGULAR", []), (40, "常规成功 REGULAR", [])]):
            self.assertEqual(dice.opposed_check(70, 50)[-1], "A")

    def test_movement_rate_three_cases(self):
        dice = load_dice_module()
        for strength, dexterity, expected in ((9, 9, 7), (12, 9, 8), (15, 15, 9)):
            with self.subTest(mov=expected), mock.patch.object(dice, "roll", side_effect=[strength, 10, 12, dexterity, 10, 12, 10, 12, 10]):
                self.assertEqual(dice.generate_stats()["移动力 MOV"], expected)

    def test_pregen_points_balance_for_every_occupation(self):
        dice = load_dice_module()
        for occupation in dice.OCCUPATIONS:
            with self.subTest(occupation=occupation):
                c = dice.pregen_character(occupation=occupation)
                spent = sum(c["skills"][s] - base for s, base in c["skill_bases"].items()) + c["credit"]
                self.assertEqual(spent + c["occupation_remaining"] + c["hobby_remaining"], c["occupation_points"] + c["hobby_points"])
                self.assertGreaterEqual(c["skills"]["母语"], c["stats"]["教育 EDU"])


if __name__ == "__main__":
    unittest.main()
