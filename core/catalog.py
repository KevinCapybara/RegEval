"""Local task catalog shared by evaluation, setup, comparison and archives."""
from pathlib import Path
from .history import TASK_INFO, read


def existing(paths):
    return next((p for p in paths if p.exists()), paths[0])


def catalog(root):
    root = Path(root).resolve()
    roots = [root, existing([root / 'tasks/task2_deficiency_detection', root.parent / 'RegEval-task2/tasks/task2_deficiency_detection']).parents[1],
             existing([root / 'tasks/task_03_category_distribution', root.parent / 'RegEval-task3/tasks/task_03_category_distribution']).parents[1],
             existing([root / 'tasks/task_04_mixed_category', root / 'task4-worktree/tasks/task_04_mixed_category']).parents[1],
             existing([root / 'tasks/task5_duplicate_counting', root.parent / 'RegEval-task5/tasks/task5_duplicate_counting']).parents[1]]
    code = [root / '.private/crl_deficiency_distribution/scenarios/scenario_01',
            roots[1] / 'tasks/task2_deficiency_detection', roots[2] / 'tasks/task_03_category_distribution',
            roots[3] / 'tasks/task_04_mixed_category', roots[4] / 'tasks/task5_duplicate_counting']
    private = [root / '.private/crl_deficiency_distribution', roots[1] / '.private/task2', code[2] / '.private',
               roots[3] / '.private/task4', code[4] / 'private']
    tasks = []
    for n, (title, note, dimensions) in enumerate(TASK_INFO, 1):
        datasets = []
        suite_installed = (private[4] / 'datasets/dataset_01/verification.json').is_file()
        for i in range(1, 2 if n == 5 and not suite_installed else 6):
            folder = [private[0] / f'scenarios/scenario_{i:02}', private[1] / f'datasets/dataset_{i:02}',
                      private[2] / f'datasets/dataset_{i:02}', private[3] / f'dataset_{i:02}', private[4] / 'pilot'][n-1]
            if n == 5 and suite_installed:
                folder = private[4] / f'datasets/dataset_{i:02}'
            workspace = folder / ['workspace/passages.json', 'workspace.json', 'input.json', 'workspace/paragraphs.json', 'workspace.json'][n-1]
            gold = folder / 'gold.json'
            datasets.append(dict(number=i, folder=folder, workspace=workspace, gold=gold,
                                 ready=workspace.is_file() and gold.is_file()))
        instruction = code[n-1] / ('workspace/instruction.md' if n == 1 else 'instruction.md')
        rubric = code[n-1] / ('judge_rubric.md' if n == 1 else 'rubric.md')
        runner = code[n-1] / ['run_luna.py', 'evaluate.py', 'task3.py', 'grader.py', 'run_pilot.py'][n-1]
        tasks.append(dict(number=n, title=title, note=note, dimensions=dimensions, root=roots[n-1], code=code[n-1],
                          private=private[n-1], datasets=datasets, instruction=instruction, rubric=rubric,
                          runner=runner, ready=runner.is_file() and instruction.is_file() and rubric.is_file()))
    return tasks


def plan(tasks, task_numbers, datasets, models):
    from .history import MODELS
    if not set(models) <= set(MODELS):
        raise ValueError('Unsupported candidate model')
    return [dict(task=t['number'], dataset=d['number'], model=m)
            for t in tasks if t['number'] in task_numbers and t['ready']
            for d in t['datasets'] if d['ready'] and d['number'] in datasets for m in models]


def archive_files(task, root):
    """Only task artifacts, never credentials, installed packages, or unrelated workspaces."""
    bases = [task['private'], task['code']]
    if task['number'] == 1:
        bases.append(Path(root) / 'runs/crl_deficiency_distribution')
    files = set()
    for base in bases:
        if base.is_dir():
            for p in base.rglob('*'):
                if p.is_file() and p.suffix.lower() in {'.json', '.md', '.txt', '.pdf'} and not any(
                    part in {'__pycache__', '.git', '.venv'} for part in p.parts):
                    files.add(p)
    for p in (Path(root) / '.private/dashboard_runs').glob('*/results/*.json'):
        try:
            if read(p).get('task') == task['number']:
                files.add(p)
                for name in ('configuration.json', 'status.json', 'process.json', 'worker.log'):
                    metadata = p.parent.parent / name
                    if metadata.is_file():
                        files.add(metadata)
        except (OSError, ValueError):
            pass
    for base in (Path(root) / '.private/dashboard_runs').glob(f"*/task_{task['number']}_*"):
        files.update(p for p in base.rglob('*') if p.is_file() and p.suffix in {'.json', '.txt', '.log'})
    return sorted(files, key=lambda p: str(p).lower())
