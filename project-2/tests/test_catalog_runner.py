import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.catalog import catalog, plan
from core.dashboard_runner import evaluate, execute_batch, save
from core.history import load_history, read


class DashboardIntegrationTests(unittest.TestCase):
    def test_task5_suite_discovers_five_distinct_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            task = root/'tasks/task5_duplicate_counting'
            task.mkdir(parents=True)
            for name in ('run_pilot.py', 'instruction.md', 'rubric.md'):
                (task/name).touch()
            for i in range(1, 6):
                base = task/'private/datasets'/f'dataset_{i:02}'
                save(base/'workspace.json', {'dataset': i})
                save(base/'gold.json', {})
                save(base/'verification.json', {})
            selected = catalog(root)[4]
            self.assertEqual(len(selected['datasets']), 5)
            self.assertEqual(len({d['workspace'] for d in selected['datasets']}), 5)
            self.assertEqual(len(plan([selected], [5], range(1,6), ['gpt-6-luna'])), 5)

    def test_missing_data_never_creates_runnable_jobs(self):
        with tempfile.TemporaryDirectory() as folder:
            tasks = catalog(Path(folder))
            self.assertEqual(len(tasks), 5)
            self.assertEqual(plan(tasks, range(1, 6), range(1, 6), ['gpt-5-nano']), [])

    def test_task5_uses_requested_dataset_and_separates_logs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            datasets = []
            for i in (1, 2):
                base = root/f'dataset_{i:02}'
                save(base/'workspace.json', {'dataset': i})
                save(base/'gold.json', {'gold_dataset': i})
                datasets.append(dict(number=i, workspace=base/'workspace.json', gold=base/'gold.json'))
            seen, outputs = [], []
            def candidate(api, model, workspace, destination):
                seen.append(workspace)
                outputs.append(destination)
                return 'answer'
            def grade(api, workspace, gold, answer, destination):
                self.assertEqual(workspace['dataset'], gold['gold_dataset'])
                return {'status': 'scored', 'score': 1}
            mod = SimpleNamespace(load=read, candidate=candidate, grade=grade)
            task = dict(number=5,code=root,private=root,runner=root/'run_pilot.py',datasets=datasets)
            with patch('core.dashboard_runner.module',return_value=mod), patch('core.dashboard_runner.clients',return_value=(None,None)):
                for i in (1,2):
                    evaluate(root,task,i,'gpt-6-luna',root/'batch'/f'job_{i}')
            self.assertEqual(seen, [{'dataset': 1}, {'dataset': 2}])
            self.assertNotEqual(outputs[0], outputs[1])

    def test_task2_candidate_does_not_receive_gold(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            workspace, gold = {'source': 'visible'}, {'secret': 'gold only'}
            api = SimpleNamespace(models=SimpleNamespace(list=lambda: [SimpleNamespace(id=m) for m in ('gpt-5-nano', 'gpt-6-luna')]))
            payloads = []
            judgments = []
            def call(api, out, model, instruction, payload):
                payloads.append(payload)
                return {'answer': 'candidate'}
            def judge(api, out, w, g, answer):
                judgments.append((w, g, answer))
                return {'status': 'scored', 'score': 1}
            mod = SimpleNamespace(client=lambda env: api, load=lambda r, d: (workspace, gold),
                                  instruction=lambda: 'task instructions', call=call, judge=judge, REPORTED_MODELS={})
            task = dict(number=2, runner=root/'evaluate.py', private=root)
            with patch('core.dashboard_runner.module', return_value=mod), patch('core.dashboard_runner.clients', return_value=(api, api)):
                evaluate(root, task, 1, 'gpt-5-nano', root/'out')
            self.assertEqual(payloads, [{'instruction': 'task instructions', 'workspace': workspace}])
            self.assertEqual(judgments[0][1], gold)

    def test_batch_preserves_candidate_identity_errors_and_history(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            batch = root/'.private/dashboard_runs/test'
            jobs = [dict(task=5, dataset=1, model=m) for m in ('gpt-5-nano','gpt-6-luna')]
            save(batch/'configuration.json', {'permit_provider': True, 'jobs': jobs})
            task = dict(number=5, ready=True, datasets=[dict(number=1,ready=True)])
            with patch('core.dashboard_runner.catalog', return_value=[task]), patch('core.dashboard_runner.evaluate', side_effect=[
                {'model':'gpt-6-luna','status':'scored','score':0.25}, RuntimeError('transport failure')]):
                execute_batch(root,batch)
            state = read(batch/'status.json')
            self.assertEqual((state['status'],state['finished']),('finished',2))
            latest = load_history(root)[4]['results']
            self.assertEqual(latest[(1,'gpt-5-nano')]['score'],0.25)
            self.assertEqual(latest[(1,'gpt-6-luna')]['status'],'error')
            self.assertIsNone(latest[(1,'gpt-6-luna')]['score'])
            self.assertEqual(load_history(root, include_dashboard=False)[4]['results'],{})


if __name__ == '__main__':
    unittest.main()
