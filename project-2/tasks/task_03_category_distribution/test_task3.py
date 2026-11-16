"""Reference-construction tests, never semantic answer grading."""
import copy
import unittest
from task3 import reference, independent_sql, validate


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.data = {'families': ['A', 'B', 'C'], 'letters': [
            {'letter_id': 'A1', 'family_id': 'A', 'review_cycle': 1},
            {'letter_id': 'A2', 'family_id': 'A', 'review_cycle': 2},
            {'letter_id': 'B1', 'family_id': 'B', 'review_cycle': 1}], 'paragraphs': [
            {'paragraph_id': 'p1', 'letter_id': 'A1', 'deficiency': True, 'labels': ['CMC', 'clinical']},
            {'paragraph_id': 'p2', 'letter_id': 'A1', 'deficiency': True, 'labels': ['CMC']},
            {'paragraph_id': 'p3', 'letter_id': 'A2', 'deficiency': True, 'labels': ['CMC']},
            {'paragraph_id': 'p4', 'letter_id': 'B1', 'deficiency': False, 'labels': []}]}

    def test_hand_calculated_denominators_and_cycles(self):
        gold, ledger = reference(self.data)
        self.assertEqual(gold['categories']['CMC'], {
            'paragraphs': {'numerator': 3, 'denominator': 3, 'percent': 100.0},
            'letters': {'numerator': 2, 'denominator': 3, 'percent': 66.6667},
            'families': {'numerator': 1, 'denominator': 3, 'percent': 33.3333}})
        self.assertEqual(gold['categories']['nonclinical']['families']['numerator'], 0)
        self.assertEqual(ledger['category_members']['CMC']['families'], ['A'])
        self.assertEqual(gold['categories'], independent_sql(self.data))

    def test_duplicate_exports_do_not_change_totals(self):
        original, _ = reference(self.data)
        self.data['paragraphs'].append(copy.deepcopy(self.data['paragraphs'][0]))
        duplicate, ledger = reference(self.data)
        self.assertEqual(original, duplicate)
        self.assertEqual(ledger['duplicate_export_rows_removed'], 1)
        self.assertEqual(duplicate['categories'], independent_sql(self.data))

    def test_conflicting_ids_rejected(self):
        changed = copy.deepcopy(self.data['paragraphs'][0]); changed['labels'] = ['labeling']
        self.data['paragraphs'].append(changed)
        with self.assertRaises(AssertionError): validate(self.data)

    def test_nondeficiency_labels_rejected(self):
        self.data['paragraphs'][-1]['labels'] = ['CMC']
        with self.assertRaises(AssertionError): validate(self.data)


if __name__ == '__main__': unittest.main()
