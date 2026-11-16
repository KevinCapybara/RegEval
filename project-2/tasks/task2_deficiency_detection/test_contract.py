"""Source-free tests for score format and calibration fixture isolation."""
import unittest
from pydantic import ValidationError
from evaluate import Checks, calibrations, reference
from report import aggregate


class ContractTests(unittest.TestCase):
    def test_binary_values_are_strict(self):
        for bad in (True, .5, 1.0, '1', 2, -1):
            with self.assertRaises(ValidationError):
                Checks(recall=bad,precision=1,evidence=1,coverage=1)

    def test_calibration_does_not_mutate_reference(self):
        w={'paragraphs':[{'id':f'P{i:03}'} for i in range(1,4)]}
        g={'selected_ids':['P001','P002'],'records':[
            {'id':f'P{i:03}','is_deficiency':i<3,'quote':'synthetic','explanation':'synthetic'} for i in range(1,4)]}
        before=reference(w,g)
        tests=calibrations(w,g,True)
        self.assertEqual(before,reference(w,g))
        self.assertEqual(10,len(tests))
        self.assertEqual([0,0,0,0],tests[0][2])
        self.assertEqual([1,1,1,1],tests[2][2])
        self.assertEqual(2,before['coverage']['selected_count'])

    def test_no_average_for_incomplete_or_unscored_task(self):
        rows=[{'name':'gpt-6-luna','dataset':f'dataset_{i:02}','status':'scored','score':1.0} for i in range(1,6)]
        self.assertEqual(1.0,aggregate(rows)['gpt-6-luna'])
        self.assertIsNone(aggregate(rows[:4])['gpt-6-luna'])
        self.assertIsNone(aggregate(rows+rows[:1])['gpt-6-luna'])
        rows[0].update(status='needs_review',score=None)
        self.assertIsNone(aggregate(rows)['gpt-6-luna'])


if __name__=='__main__':
    unittest.main()
