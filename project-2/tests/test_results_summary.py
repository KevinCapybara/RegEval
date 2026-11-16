import unittest

from core.results_summary import AGENTS, summary_data


class SummaryTests(unittest.TestCase):
    def task(self, number, luna=1, nano=0):
        return dict(number=number, title='Example', results={
            (i, model): dict(status='scored', score=value)
            for model, value in zip(AGENTS, [luna, nano]) for i in range(1, 6)})

    def test_same_tasks_used_for_both_headline_scores(self):
        complete, pending, failed = [self.task(i) for i in range(1, 4)]
        pending['results'][(3, 'gpt-6-luna')]['status'] = 'needs_review'
        failed['results'][(1, 'gpt-5-nano')]['calibration_valid'] = False
        shared, means, bars, cells = summary_data([complete, pending, failed])
        self.assertEqual([t['number'] for t in shared], [1])
        self.assertEqual(list(means.values()), [1, 0])
        self.assertIsNone(bars[2]['Score'])
        self.assertIsNone(cells[12]['Score'])
        self.assertEqual(cells[5]['Label'], '0%')

    def test_pilot_and_empty_states_do_not_create_overall_scores(self):
        pilot = self.task(5)
        pilot['results'] = {k: v for k, v in pilot['results'].items() if k[0] == 1}
        for tasks in ([], [pilot]):
            shared, means, _, _ = summary_data(tasks)
            self.assertFalse(shared)
            self.assertTrue(all(v is None for v in means.values()))
        self.assertEqual(summary_data([pilot])[3][0]['Score'], 1)
