"""Read the five task result formats without rerunning or changing judgments."""
import json
from pathlib import Path

from .llm import MODELS, DEFAULT_JUDGE
TASK_INFO = [
    ("Deficiency classification and distribution", "Draft gold; provisional scores. Dataset 3 has unresolved gold/judge ambiguity; endpoint calibration is pending.",
     {"detection": "Deficiency detection", "classification": "Category assignment", "evidence": "Evidence and explanations", "distribution": "Distribution accuracy"}),
    ("Deficiency-paragraph detection", "Five datasets; 22/22 semantic calibration checks passed. Gold is model-assisted, not expert-certified.",
     {"recall": "All deficiencies found", "precision": "No false positives", "evidence": "Evidence support", "coverage": "Count and coverage"}),
    ("Category distribution across counting units", "Five datasets covering paragraph, letter, and application-family counts and percentages.",
     {"paragraphs": "Paragraph counts", "letters": "Letter counts", "families": "Application-family counts", "percentages": "Percentages"}),
    ("Mixed-category deficiency classification", "Dataset 3 / Luna requires adjudication of conflicting evidence verdicts. Its task mean is withheld.",
     {"no_omissions": "No omitted categories", "no_additions": "No unsupported categories", "evidence": "Evidence support", "distribution": "Distribution accuracy"}),
    ("Duplicate-aware corpus counting", "Five-case suite: one genuine-duplicate case and four false-merge controls. Positive duplicate diversity is limited; annotations are model-reviewed, not expert-certified.",
     {"duplicate_grouping": "Group duplicates", "distinct_separation": "Separate distinct letters", "evidence": "Evidence support", "counts": "Counts and percentages"}),
]


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def first_existing(paths):
    return next((p for p in paths if p.is_file()), None)


def load_history(root, include_dashboard=True, judge_model=DEFAULT_JUDGE):
    root = Path(root)
    sibling = root.parent
    sources = [
        [root / ".private/crl_deficiency_distribution/TASK1_RESULTS_BINARY.json"],
        [r / ".private/task2/logs/nano-saved-recovery/summary.json" for r in (root, sibling / "RegEval-task2")],
        [r / "tasks/task_03_category_distribution" / suffix
         for suffix in (".private/matrix-v1/results.json", "RESULTS.json")
         for r in (root, sibling / "RegEval-task3")],
        [r / ".private/task4/final_results.json" for r in (root, root / "task4-worktree")],
        [p for r in (root, sibling / "RegEval-task5") for p in sorted(
            (r / "tasks/task5_duplicate_counting/private/runs").glob("*/summary.json"), reverse=True)],
    ]
    tasks = []
    for number, ((title, note, dimensions), candidates) in enumerate(zip(TASK_INFO, sources), 1):
        task = dict(number=number, title=title, note=note, dimensions=dimensions, results={}, source=None, error=None)
        path = first_existing(candidates)
        if path and judge_model == DEFAULT_JUDGE:
            task["source"] = str(path)
            try:
                data = read(path)
                if number == 4:
                    rows = [dict(value, dataset=key.split("/")[0], candidate_model=key.split("/")[1])
                            for key, value in data["results"].items()]
                else:
                    rows = data if isinstance(data, list) else data.get("results", data.get("rows", []))
                for row in rows:
                    if number == 2 and row.get("path"):
                        detail = Path(row["path"]) / "judge/verdict.json"
                        if detail.is_file() and detail.resolve().is_relative_to(sibling.resolve()):
                            try:
                                row = {**read(detail), **row}
                            except (OSError, ValueError, TypeError):
                                pass  # The summary still contains the authoritative score.
                    # Task 5's `model` is the JUDGE; candidate_model takes precedence.
                    model = row.get("candidate_model", row.get("agent", row.get("name", row.get("model"))))
                    dataset = int(str(row.get("dataset", 1)).split("_")[-1])
                    if model in MODELS and 1 <= dataset <= 5:
                        task["results"][(dataset, model)] = row
            except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
                task["error"] = f"Could not read result summary: {error}"
        tasks.append(task)
    if include_dashboard:
        for path in sorted((root / '.private/dashboard_runs').glob('*/results/*.json')):
            try:
                row = read(path)
                if row.get('judge_model', DEFAULT_JUDGE) != judge_model:
                    continue
                task = tasks[int(row['task']) - 1]
                if row['model'] in MODELS and 1 <= int(row['dataset']) <= 5:
                    task['results'][(int(row['dataset']), row['model'])] = row
            except (OSError, ValueError, TypeError, KeyError, IndexError):
                continue
    return tasks


def score(row):
    if row.get("status") not in ("scored", "completed") or row.get("scorable") is False:
        return None
    value = row.get("score")
    return value if isinstance(value, (int, float)) and 0 <= value <= 1 else None


def aggregate(task, model):
    values = [score(task["results"].get((i, model), {})) for i in range(1, 6)]
    count = sum(v is not None for v in values)
    calibrated = all(r.get('calibration_valid') is not False for (i, m), r in task['results'].items() if m == model)
    return (sum(values) / 5 if count == 5 and calibrated else None), count


def percent(value):
    return "—" if value is None else f"{value:.0%}"


def render_history(root, tasks=None):
    """Compatibility entry point for the history presentation module."""
    from .history_view import render_history as render
    return render(root, tasks)
