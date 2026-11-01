"""
test_mbti.py
Unit tests for the question bank, decision tree, compatibility, charts and records.
Run with:  python -m unittest test_mbti.py -v
"""

import os
import random
import tempfile
import unittest

from quiz import (build_tree, traverse, count_leaves, collect_results, tree_depth,
                  percent_first, INITIAL_QUESTIONS, MAX_QUESTIONS)
from question_bank import load_questions, to_dimensions, MIN_PER_DIMENSION
from personality import PROFILES, is_valid_type, get_profile
from compatibility import calculate_compatibility, compatibility_label
from records import RecordManager, letter_strengths
from charts import bar, strength_bar, count_chart


def fixed_answers(per_dimension):
    """Fake 'ask' function: always gives the same 1-5 answer for each dimension."""
    return lambda question: per_dimension[question.dimension]


def cycling_answers(sequence):
    """Fake 'ask' function: repeats a sequence of answers within each dimension."""
    position = {}

    def ask(question):
        i = position.get(question.dimension, 0)
        position[question.dimension] = i + 1
        return sequence[i % len(sequence)]
    return ask


def write_temp(text):
    path = os.path.join(tempfile.mkdtemp(), "bank.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


class TestQuestionBank(unittest.TestCase):
    def test_real_bank_loads(self):
        bank = load_questions("questions.txt")
        for dim, questions in bank.items():
            self.assertGreaterEqual(len(questions), MAX_QUESTIONS)
            self.assertTrue(all(q.dimension == dim for q in questions))

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_questions("no_such_file.txt")

    def test_bad_line(self):
        path = write_temp("EI | only two parts\n")
        with self.assertRaises(ValueError):
            load_questions(path)

    def test_unknown_dimension(self):
        path = write_temp("XY | q | a | b\n")
        with self.assertRaises(ValueError):
            load_questions(path)

    def test_too_few_questions(self):
        lines = "".join(f"{d} | q | a | b\n" for d in ["EI", "SN", "TF", "JP"])
        with self.assertRaises(ValueError):
            load_questions(write_temp(lines))   # only 1 per dimension

    def test_comments_and_blank_lines_ignored(self):
        lines = "# comment\n\n" + "".join(
            f"{d} | q{i} | a | b\n" for d in ["EI", "SN", "TF", "JP"]
            for i in range(MIN_PER_DIMENSION))
        bank = load_questions(write_temp(lines))
        self.assertEqual(len(bank["EI"]), MIN_PER_DIMENSION)


class TestDecisionTree(unittest.TestCase):
    def setUp(self):
        self.tree = build_tree(to_dimensions(load_questions("questions.txt")))
        self.rng = random.Random(42)

    def test_structure(self):
        results = collect_results(self.tree)
        self.assertEqual(count_leaves(self.tree), 16)
        self.assertEqual(len(set(results)), 16)
        self.assertTrue(all(is_valid_type(r) for r in results))
        self.assertEqual(tree_depth(self.tree), 4)

    def test_percent_first(self):
        self.assertEqual(percent_first([1, 1, 1]), 100)
        self.assertEqual(percent_first([5, 5, 5]), 0)
        self.assertEqual(percent_first([2, 4, 3]), 50)

    def test_strong_answers_need_only_initial_questions(self):
        ask = fixed_answers({"EI": 1, "SN": 1, "TF": 1, "JP": 1})
        result, scores, asked = traverse(self.tree, ask, self.rng)
        self.assertEqual(result, "ESTJ")
        self.assertEqual(scores, {"EI": 100, "SN": 100, "TF": 100, "JP": 100})
        self.assertTrue(all(n == INITIAL_QUESTIONS for n in asked.values()))

    def test_scale_direction(self):
        ask = fixed_answers({"EI": 5, "SN": 4, "TF": 2, "JP": 1})
        result, _, _ = traverse(self.tree, ask, self.rng)
        self.assertEqual(result, "INTJ")

    def test_close_result_asks_extra_until_max(self):
        # Always neutral -> always 50% -> keeps asking up to the maximum
        ask = fixed_answers({"EI": 3, "SN": 3, "TF": 3, "JP": 3})
        result, scores, asked = traverse(self.tree, ask, self.rng)
        self.assertTrue(all(n == MAX_QUESTIONS for n in asked.values()))
        self.assertEqual(result, "ESTJ")          # all-neutral tie defaults to option a

    def test_extra_question_resolves_close_result(self):
        # 2, 4, 3 = 50% (too close), then 1 -> 62.5% -> clear, stops at 4 questions
        result, scores, asked = traverse(self.tree, cycling_answers([2, 4, 3, 1]), self.rng)
        self.assertTrue(all(n == 4 for n in asked.values()))
        self.assertEqual(result, "ESTJ")

    def test_tie_follows_last_non_neutral_answer(self):
        # 1, 5, 3, 3... stays at 50% -> tie -> last non-neutral answer was 5 (option b)
        result, _, asked = traverse(self.tree, cycling_answers([1, 5, 3, 3, 3, 3, 3]), self.rng)
        self.assertEqual(result, "INFP")

    def test_every_type_reachable(self):
        found = set()
        for e in (1, 5):
            for s in (1, 5):
                for t in (1, 5):
                    for j in (1, 5):
                        ask = fixed_answers({"EI": e, "SN": s, "TF": t, "JP": j})
                        found.add(traverse(self.tree, ask, self.rng)[0])
        self.assertEqual(found, set(PROFILES))

    def test_no_repeated_questions(self):
        seen = []
        def ask(question):
            seen.append(question.text)
            return 3
        traverse(self.tree, ask, self.rng)
        self.assertEqual(len(seen), len(set(seen)))


class TestProfiles(unittest.TestCase):
    def test_16_profiles(self):
        self.assertEqual(len(PROFILES), 16)

    def test_case_insensitive_lookup(self):
        self.assertEqual(get_profile(" intj ").code, "INTJ")

    def test_invalid_type(self):
        self.assertIsNone(get_profile("ABCD"))
        self.assertFalse(is_valid_type(""))
        self.assertFalse(is_valid_type(None))


class TestCompatibility(unittest.TestCase):
    def test_symmetric(self):
        for t1 in PROFILES:
            for t2 in PROFILES:
                self.assertEqual(calculate_compatibility(t1, t2)[0],
                                 calculate_compatibility(t2, t1)[0])

    def test_score_range(self):
        scores = [calculate_compatibility(a, b)[0] for a in PROFILES for b in PROFILES]
        self.assertEqual(min(scores), 45)
        self.assertEqual(max(scores), 100)

    def test_known_values(self):
        self.assertEqual(calculate_compatibility("INTJ", "INTJ")[0], 80)
        self.assertEqual(calculate_compatibility("INTJ", "ENFJ")[0], 100)

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            calculate_compatibility("XXXX", "INTJ")

    def test_labels(self):
        # Highest and lowest possible scores
        self.assertEqual(compatibility_label(100), "Excellent match")
        self.assertEqual(compatibility_label(45), "Challenging match")
        # Boundary values: exactly on each threshold, and one point below
        self.assertEqual(compatibility_label(90), "Excellent match")
        self.assertEqual(compatibility_label(89), "Good match")
        self.assertEqual(compatibility_label(75), "Good match")
        self.assertEqual(compatibility_label(74), "Moderate match")
        self.assertEqual(compatibility_label(60), "Moderate match")
        self.assertEqual(compatibility_label(59), "Challenging match")

class TestCharts(unittest.TestCase):
    def test_bar(self):
        self.assertEqual(bar(0.5, 10), "█" * 5 + "░" * 5)
        self.assertEqual(bar(1.5, 4), "████")      # clamped
        self.assertEqual(bar(-1, 4), "░░░░")

    def test_strength_bar(self):
        line = strength_bar("I", 75, width=8)
        self.assertIn("Introversion", line)
        self.assertIn("██████░░", line)
        self.assertTrue(line.endswith(" 75%"))

    def test_count_chart(self):
        self.assertEqual(count_chart({}), [])
        lines = count_chart({"INTJ": 2, "ENFP": 1}, width=10)
        self.assertTrue(lines[0].startswith("INTJ " + "█" * 10))


class TestRecords(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), "test_records.csv")
        self.records = RecordManager(self.path)

    def test_missing_file_returns_empty(self):
        self.assertEqual(self.records.load_all(), [])

    def test_save_and_query(self):
        scores = {"EI": 25, "SN": 33, "TF": 67, "JP": 100}
        self.records.save("Alice", "INTJ", scores)
        self.records.save("Bob", "ENFP", scores)
        self.records.save("alice", "INTP", scores)

        self.assertEqual(len(self.records.load_all()), 3)
        self.assertEqual(len(self.records.find_by_name("ALICE")), 2)
        self.assertEqual(self.records.latest_type_for("Alice"), "INTP")
        self.assertEqual(len(self.records.find_by_type("enfp")), 1)
        self.assertEqual(self.records.type_statistics()["INTJ"], 1)

    def test_letter_strengths(self):
        record = {"type": "INTJ", "EI": "25", "SN": "33", "TF": "67", "JP": "100"}
        self.assertEqual(letter_strengths(record), "I 75%, N 67%, T 67%, J 100%")


if __name__ == "__main__":
    unittest.main()
