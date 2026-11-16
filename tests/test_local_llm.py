import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
from types import SimpleNamespace
from pydantic import BaseModel, Field, ValidationError

from core.llm import Client, LOCAL_MODEL, DEFAULT_JUDGE, clients, check_local
from core.dashboard_runner import save, execute_batch, start_batch, evaluate
from core.history import load_history


class Verdict(BaseModel):
    check: int = Field(strict=True, ge=0, le=1)


class LocalModelTests(unittest.TestCase):
    def response(self, content='{"check":1}', reason='stop'):
        return dict(model=LOCAL_MODEL, done=True, done_reason=reason, message={'content': content})

    def test_schema_and_local_transport(self):
        with patch('core.llm.local_request', return_value=self.response()) as request:
            result = Client(LOCAL_MODEL).parse(model=DEFAULT_JUDGE, input='evidence', text_format=Verdict)
        self.assertEqual(result.output_parsed.check, 1)
        payload = request.call_args.args[1]
        self.assertEqual(payload['model'], LOCAL_MODEL)
        self.assertFalse(payload['think'])
        self.assertEqual(payload['format'], Verdict.model_json_schema())
        json.dumps(result.model_dump())

    def test_invalid_and_truncated_verdicts_never_pass(self):
        with patch('core.llm.local_request', return_value=self.response('{"check":0.5}')):
            with self.assertRaises(ValidationError):
                Client(LOCAL_MODEL).parse(input='x', text_format=Verdict)
        with patch('core.llm.local_request', return_value=self.response(reason='length')):
            result = Client(LOCAL_MODEL).parse(input='x', text_format=Verdict)
            self.assertEqual(result.status, 'incomplete')
            self.assertIsNone(result.output_parsed)

    def test_missing_model_has_actionable_error(self):
        with patch('core.llm.local_request', return_value={'models': []}):
            with self.assertRaisesRegex(RuntimeError, 'ollama pull'):
                check_local()

    def test_fully_local_never_constructs_hosted_client(self):
        with patch('core.llm.check_local'), patch('openai.OpenAI') as hosted:
            candidate, judge = clients(LOCAL_MODEL, LOCAL_MODEL)
            self.assertIsNone(candidate.hosted)
            self.assertIsNone(judge.hosted)
            hosted.assert_not_called()

    def test_mixed_roles_route_independently(self):
        api = Mock()
        api.models.list.return_value = [Mock(id=DEFAULT_JUDGE)]
        with patch('core.llm.check_local'), patch('openai.OpenAI', return_value=api):
            candidate, judge = clients(LOCAL_MODEL, DEFAULT_JUDGE)
            with patch('core.llm.local_request', return_value=self.response()) as local:
                candidate.create(input='candidate evidence')
                judge.create(model=LOCAL_MODEL, input='judge gold')
            self.assertEqual(local.call_count, 1)
            self.assertEqual(api.responses.create.call_args.kwargs['model'], DEFAULT_JUDGE)

    def test_task1_gold_only_goes_to_judge(self):
        from core.task1_evaluator import evaluate_task1
        from core.llm import Record
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            save(root/'workspace/answer_schema.json', {})
            save(root/'workspace/passages.json', {'passages': 'visible'})
            save(root/'gold.json', {'status': 'draft', 'secret': 'gold only'})
            (root/'workspace/instruction.md').write_text('instructions')
            (root/'judge_rubric.md').write_text('rubric')
            candidate = Mock(model=LOCAL_MODEL)
            judge = Mock(model=LOCAL_MODEL)
            candidate.responses.create.return_value = Record(status='completed', output_text='{}')
            parsed = Record(scorable=True, criteria={'a': 1})
            judge.responses.parse.return_value = Record(status='completed', model=LOCAL_MODEL, output_parsed=parsed)
            mod = SimpleNamespace(Verdict=Verdict, WEIGHTS={'a': 1}, SCORING_VERSION='test')
            task = dict(runner=root/'runner.py', datasets=[dict(number=1, folder=root)])
            result = evaluate_task1(task, 1, candidate, judge, root/'out', lambda *args: mod)
            self.assertNotIn('secret', candidate.responses.create.call_args.kwargs['input'])
            self.assertIn('secret', judge.responses.parse.call_args.kwargs['input'])
            self.assertEqual(result['score'], 1)

    def test_task_runners_use_separate_role_clients(self):
        for number in (2, 3, 4, 5):
            with self.subTest(task=number), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                candidate, judge = object(), object()
                seen = []
                def call(api, *args):
                    seen.append(('candidate', api))
                    return 'answer'
                def grade(api, *args):
                    seen.append(('judge', api))
                    return {'status': 'scored', 'score': 1}
                mod = SimpleNamespace(REPORTED_MODELS={}, HERE=root, instruction=lambda: 'instruction',
                    read=lambda p: 'instruction', call=call, judge=grade, candidate=call, grade=grade,
                    dataset=lambda i: ({'source':'visible'}, {}, {}), context=lambda p: ({'source':'visible'}, {}),
                    load=lambda *args: ({'source':'visible'}, {'gold':'secret'}) if len(args)==2 else {},
                    snapshot=lambda p: 'snapshot')
                task = dict(number=number, runner=root/'runner.py', private=root, code=root,
                            datasets=[dict(number=1,workspace=root/'pilot/workspace.json',gold=root/'pilot/gold.json')])
                with patch('core.dashboard_runner.module', return_value=mod), patch('core.dashboard_runner.clients', return_value=(candidate, judge)):
                    result = evaluate(root, task, 1, LOCAL_MODEL, root/'out', LOCAL_MODEL)
                self.assertEqual(seen, [('candidate', candidate), ('judge', judge)])
                if number == 4:
                    self.assertFalse(result['calibration_valid'])
                if number == 5:
                    self.assertNotIn(':', Path(result['artifact_path']).name)

    def test_local_batch_permissions_paths_and_history_isolation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            jobs = [dict(task=1, dataset=1, model=LOCAL_MODEL)]
            with patch('core.dashboard_runner.subprocess.Popen', return_value=Mock(pid=1)):
                batch = start_batch(root, jobs, False, LOCAL_MODEL)
            task = dict(number=1, ready=True, datasets=[dict(number=1, ready=True)])
            with patch('core.dashboard_runner.catalog', return_value=[task]), patch('core.dashboard_runner.evaluate', return_value={'status':'scored', 'score':1}) as evaluate:
                execute_batch(root, batch)
            self.assertEqual(evaluate.call_args.args[-1], LOCAL_MODEL)
            self.assertNotIn(':', evaluate.call_args.args[-2].name)
            self.assertEqual(load_history(root)[0]['results'], {})
            self.assertEqual(load_history(root, judge_model=LOCAL_MODEL)[0]['results'][(1, LOCAL_MODEL)]['score'], 1)
            with self.assertRaises(ValueError):
                start_batch(root, jobs, False, DEFAULT_JUDGE)


if __name__ == '__main__':
    unittest.main()
