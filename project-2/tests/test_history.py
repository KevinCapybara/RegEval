import json
from pathlib import Path
import tempfile
import unittest

from core.history import aggregate, load_history, score


class HistoryTests(unittest.TestCase):
    def test_missing_and_review_results_do_not_become_zero(self):
        rows = {(i, "gpt-6-luna"): {"status": "scored", "score": 1} for i in range(1, 6)}
        task = {"results": rows}
        self.assertEqual(aggregate(task, "gpt-6-luna"), (1, 5))
        rows[(3, "gpt-6-luna")] = {"status": "needs_review", "score": 0.5}
        self.assertEqual(aggregate(task, "gpt-6-luna"), (None, 4))
        self.assertEqual(score({"status": "scored", "score": 0}), 0)

    def test_pilot_uses_candidate_not_judge_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "RegEval"
            target = root / "tasks/task5_duplicate_counting/private/runs/batch/summary.json"
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps({"results": [
                {"candidate_model": "gpt-5-nano", "model": "gpt-6-luna", "status": "scored", "score": 0.25},
                {"candidate_model": "gpt-6-luna", "model": "gpt-6-luna", "status": "scored", "score": 0.75},
            ]}))
            tasks = load_history(root)
            self.assertEqual(len(tasks), 5)
            self.assertEqual(tasks[4]["results"][(1, "gpt-5-nano")]["score"], 0.25)
            self.assertEqual(aggregate(tasks[4], "gpt-6-luna"), (None, 1))
            self.assertEqual(aggregate(tasks[0], "gpt-6-luna"), (None, 0))

    def test_corrupt_summary_is_visible_and_other_tasks_still_load(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / ".private/task4/final_results.json"
            target.parent.mkdir(parents=True)
            target.write_text("{")
            tasks = load_history(root)
            self.assertIsNotNone(tasks[3]["error"])
            self.assertEqual(len(tasks), 5)


if __name__ == "__main__":
    unittest.main()
