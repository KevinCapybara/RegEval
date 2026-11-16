"""Transport and aggregation tests. Actual Luna calibration tests semantics."""
import unittest
import copy
import tempfile
from pathlib import Path
from unittest.mock import patch
from pydantic import ValidationError
from grader import Checks, Verdict, aggregate, AGENTS, judge, dump, sha


class ContractTests(unittest.TestCase):
    def test_reject_fraction_and_boolean(self):
        for bad in [0.5, True, '1', 2, -1]:
            with self.assertRaises(ValidationError):
                Checks(no_omissions=bad,no_additions=1,evidence=1,distribution=1)

    def test_review_has_no_numeric_criteria(self):
        with self.assertRaises(ValidationError):
            Verdict(status='needs_review',criteria=dict.fromkeys(['no_omissions','no_additions','evidence','distribution'],0),
                    reasons=dict.fromkeys(['no_omissions','no_additions','evidence','distribution'],'ambiguous'),findings=[],gold_concerns=[])

    def test_no_partial_task_average(self):
        rows={f'dataset_{i:02}/{m}':dict(status='scored',score=1) for m in AGENTS for i in range(1,6)}
        self.assertEqual(aggregate(rows,True)[AGENTS[0]]['task_mean'],1)
        self.assertIsNone(aggregate(rows,False)[AGENTS[0]]['task_mean'])
        rows[f'dataset_03/{AGENTS[0]}']=dict(status='needs_review',score=None)
        self.assertIsNone(aggregate(rows,True)[AGENTS[0]]['task_mean'])
        self.assertEqual(aggregate(rows,True)[AGENTS[1]]['task_mean'],1)

    def test_known_answer_disagreement_stays_unscored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); dataset=root/'dataset_03';answer={'decisions':[]}
            dump(root/'judge_concerns.json',{'dataset_03/gpt-6-luna':dict(answer_sha256=sha(answer),reason='Conflicting real judge evidence verdicts')})
            verdict=dict(status='scored',criteria=dict.fromkeys(['no_omissions','no_additions','evidence','distribution'],1),
                         reasons={},findings=[],gold_concerns=[])
            with patch('grader.context',return_value=({'question':'test','paragraphs':[]},{'status':'reviewed'})), patch('grader.call',side_effect=lambda *a:copy.deepcopy(verdict)):
                flagged=judge(None,dataset,answer,root/'flagged')
                self.assertEqual(flagged['status'],'needs_review')
                self.assertIsNone(flagged['score'])
                self.assertIsNone(flagged['criteria'])
                other=judge(None,dataset,{'different':'answer'},root/'other')
                self.assertEqual(other['score'],1)


if __name__=='__main__':unittest.main()
