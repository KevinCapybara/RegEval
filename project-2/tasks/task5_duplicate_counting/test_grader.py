"""Format and failure-handling tests only; semantic calibration uses real Luna calls."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from grade import Criteria,ROOT,grade
from pydantic import ValidationError

class GraderTests(unittest.TestCase):
    def test_binary_only(self):
        for bad in (0.5,True,'1',2,-1):
            with self.assertRaises(ValidationError):
                Criteria(duplicate_grouping=bad,distinct_separation=1,evidence=1,counts=1)

    def test_failure_is_unscored(self):
        def fail(**kwargs):
            raise RuntimeError('synthetic transport failure')
        c=SimpleNamespace(responses=SimpleNamespace(parse=fail))
        (ROOT/'private').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'private') as d:
            v=grade(c,{}, {},'',Path(d))
            self.assertEqual(v['status'],'error')
            self.assertIsNone(v['score'])
            self.assertTrue((Path(d)/'judge_input.json').exists())

    def test_logs_must_be_private(self):
        with self.assertRaises(ValueError):
            grade(None,{},{},'',ROOT/'public-output')

if __name__=='__main__':
    unittest.main()
