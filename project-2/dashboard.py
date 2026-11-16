from pathlib import Path
import json
import pandas as pd
import streamlit as st

from core.catalog import catalog, archive_files, plan
from core.dashboard_runner import start_batch
from core.llm import LOCAL_MODEL, DEFAULT_JUDGE, JUDGES, RESULT_MODELS
from core.history import MODELS, aggregate, load_history, percent, read, score
from core.history_view import render_history
from ui import apply_style, masthead, section_heading, evaluation_guide

ROOT = Path(__file__).resolve().parent


def show_file(path, key):
    if not path.is_file():
        st.info("This artifact is not installed.")
        return
    if path.suffix.lower() == '.pdf':
        st.download_button("Download source PDF", path.read_bytes(), file_name=path.name, key=key)
        return
    content = path.read_text(encoding='utf-8-sig')
    try:
        if path.suffix == '.json':
            st.json(json.loads(content), expanded=False)
        elif path.suffix == '.md':
            st.markdown(content)
        else:
            st.code(content, language=None)
    except ValueError:
        st.code(content, language=None)
    st.download_button("Download artifact", content, file_name=path.name, key=key)


def main():
    st.set_page_config(page_title="RegEval", layout="wide")
    apply_style()
    masthead()
    tasks = catalog(ROOT)
    history_judge = st.sidebar.selectbox("Results judged by", list(JUDGES), format_func=JUDGES.get)
    history = load_history(ROOT, judge_model=history_judge)
    task_label = lambda n: f"Task {n} \u00b7 {tasks[n-1]['title']}"
    run_tab, compare_tab, setup_tab, history_tab = st.tabs(["Run evaluation", "Compare", "Benchmark setup", "Eval Results"])
    with run_tab:
        evaluation_guide(tasks)
        with st.container(key="evaluation_config"):
            st.html('''<div class="re-config-heading"><span class="re-config-badge">START HERE</span><h2>Configure your evaluation</h2><p>Choose your tasks, select your models, and put them to the test.</p></div>''')
            a, b, c = st.columns(3)
            a.metric("Tasks", len(tasks))
            b.metric("Available datasets", sum(d['ready'] for t in tasks for d in t['datasets']))
            c.metric("Saved dataset/model evaluations", sum(sum(model in RESULT_MODELS for _, model in t['results']) for t in history))
            choice = st.selectbox("Test cases", [0, *range(1, 6)], format_func=lambda n: "All five tasks" if n == 0 else task_label(n))
            selected_tasks = tasks if choice == 0 else [tasks[choice-1]]
            agent = st.selectbox("Test agent", ["All hosted models", *MODELS.values()])
            models = [m for m in MODELS if m != LOCAL_MODEL] if agent == "All hosted models" else [m for m, label in MODELS.items() if label == agent]
            st.caption("Each selected task runs all installed datasets per model. Check Benchmark setup for dataset availability.")
            judge = st.selectbox("Judge model", list(JUDGES), format_func=JUDGES.get)
            st.caption("Candidates receive instructions and source data; gold is supplied only to the separate judge call.")
            jobs = plan(tasks, [t['number'] for t in selected_tasks], range(1, 6), models)
            st.write(f"**Run plan: {len(jobs)} dataset/model evaluations** \u2014 each generates one answer and a separate judge verdict.")
            hosted = judge != LOCAL_MODEL or any(m != LOCAL_MODEL for m in models)
            permit = st.checkbox("I verified that the corpus terms and provider settings permit sending these documents") if hosted else False
            if st.button("Run evaluation", type="primary", disabled=not jobs or (hosted and not permit)):
                try:
                    batch = start_batch(ROOT, jobs, permit, judge)
                    st.session_state['active_batch'] = str(batch)
                    st.success("Evaluation started. Progress appears below; results are saved automatically.")
                except (OSError, ValueError, RuntimeError) as exc:
                    st.error(f"Could not start evaluation: {exc}")
        progress()

    with compare_tab:
        section_heading("Compare evaluations", "All five tasks, Luna and Nano, every dataset and scoring dimension. Results use the judge selected in the sidebar.")
        summaries = []
        for t in history:
            for model, label in RESULT_MODELS.items():
                mean, count = aggregate(t, model)
                value = mean
                summaries.append({'Task': task_label(t['number']), 'Model': label, 'Score': percent(value),
                                  'Score basis': 'Five-dataset average' if mean is not None else 'Incomplete / awaiting review',
                                  'Scored datasets': f'{count}/5'})
        st.dataframe(pd.DataFrame(summaries), hide_index=True, width="stretch")
        choice = st.selectbox("Compare task details", list(range(1, 6)), format_func=task_label)
        selected = history[choice-1]
        rows = []
        for i in range(1, 6):
            for model, label in RESULT_MODELS.items():
                result = selected['results'].get((i, model), {})
                value = score(result)
                row = {'Dataset': i, 'Model': label, 'Score': percent(value), 'Status': result.get('status', 'Not evaluated')}
                for key, label in selected['dimensions'].items():
                    row[label] = (result.get('criteria') or {}).get(key) if value is not None else None
                rows.append(row)
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("Dimensions: 1 = pass, 0 = fail. Blank = unscored or unavailable. Task averages require five scored datasets.")
        st.download_button("Download comparison CSV", pd.DataFrame(rows).to_csv(index=False), file_name=f'task_{choice}_comparison.csv')

    with setup_tab:
        section_heading("Benchmark setup", "Browse installed instructions, rubrics, source inputs, gold, and verification records.")
        st.markdown("### How we evaluated the LLM judge")
        st.markdown("""
- **Separate judge calls:** GPT-6 Luna receives the source evidence, reference answer, task rubric, and candidate answer in a separate call\u2014even when Luna is also the candidate. It explains four binary decisions; Python validates the verdict and averages the checks.
- **Known-answer calibration:** We tested the actual judge with empty and wholly wrong answers (expected 0%) and complete reference-equivalent answers (expected 100%). We compared its individual pass/fail decisions with the expected decisions, not just the total score.
- **Controlled mistakes:** Additional probes introduced omissions, unsupported additions, fabricated evidence, incorrect counts, and task-specific errors such as merging distinct letters. These check whether the judge penalizes the relevant rubric criteria.
- **Equivalent answers and consistency:** Paraphrased or reordered correct answers should retain full credit. Repeated judgments test consistency; disagreement is retained for review rather than resolved by choosing the more favorable score.
- **Judge scope:** The calibration results below apply to GPT-6 Luna only.
- **Recorded results:** Task 2 passed 22/22 calibration checks; Task 3 passed 22/22; Task 4 passed 24/24; Task 5 passed 15/15 endpoint checks across its five-case Luna suite (and historically 10/10 pilot checks). Task 1 endpoint calibration remains pending, so these results do not establish calibration for all five tasks.
- **Limits and audit trail:** Calibration is a finite set of checks, not proof of reliability or independent expert validation. Task 4 still produced conflicting judgments on a real answer after calibration; that result remains unscored. Open **Eval Results \u2192 All saved artifacts** and filter for `calibr` to inspect saved calibration prompts, responses, and verdicts.
""")
        choice = st.selectbox("Inspect task", list(range(1, 6)), format_func=task_label)
        t = tasks[choice-1]
        st.dataframe(pd.DataFrame([{'Dataset': d['number'], 'Source data': 'Installed' if d['workspace'].is_file() else 'Missing',
            'Gold': 'Installed' if d['gold'].is_file() else 'Missing', 'Ready to run': t['ready'] and d['ready']} for d in t['datasets']]), hide_index=True)
        with st.expander("Task instructions"):
            show_file(t['instruction'], 'instruction_download')
        with st.expander("Scoring rubric"):
            show_file(t['rubric'], 'rubric_download')
        ds = st.selectbox("Inspect dataset", [d['number'] for d in t['datasets']], format_func=lambda n: f'Dataset {n}')
        dataset = next(d for d in t['datasets'] if d['number'] == ds)
        with st.expander("Candidate input / source evidence"):
            show_file(dataset['workspace'], 'workspace_download')
        with st.expander("Evaluator-only golden answer"):
            show_file(dataset['gold'], 'gold_download')
        supporting = sorted(p for p in dataset['folder'].rglob('*') if p.is_file() and p.suffix in ('.json', '.md', '.txt')
                            and p not in (dataset['workspace'], dataset['gold']))
        if supporting:
            p = st.selectbox("Dataset supporting artifacts", supporting, format_func=lambda p: str(p.relative_to(dataset['folder'])))
            show_file(p, 'support_download')

    with history_tab:
        section_heading("Eval Results", "Explore results and the local archive: answers, judge findings, calibration, source records, and metadata.")
        view = st.radio("Results view", ["Latest results (including webapp runs)", "Original benchmark results"], horizontal=True)
        render_history(ROOT, history if view.startswith('Latest') else load_history(ROOT, include_dashboard=False, judge_model=history_judge))
        st.subheader("All saved artifacts")
        choice = st.selectbox("Archive task", list(range(1, 6)), format_func=task_label)
        files = archive_files(tasks[choice-1], ROOT)
        query = st.text_input("Filter artifact paths", placeholder="e.g. calibration, answer, verdict, metadata")
        if query:
            files = [p for p in files if query.lower() in str(p).lower()]
        st.caption(f"{len(files)} matching local artifacts. Original runs and rejudgments remain available.")
        if files:
            p = st.selectbox("Artifact", files, format_func=lambda p: str(p.relative_to(ROOT.parent)))
            show_file(p, 'archive_download')
        else:
            st.info("No artifacts match this filter.")


@st.fragment(run_every=3)
def progress():
    batches = sorted((ROOT / '.private/dashboard_runs').glob('*/status.json'), reverse=True)
    if not batches:
        return
    st.divider()
    st.subheader("Most recent eval")
    path = Path(st.session_state['active_batch']) / 'status.json' if st.session_state.get('active_batch') else batches[0]
    try:
        state = read(path)
    except (OSError, ValueError):
        st.info("Waiting for the evaluation worker\u2026")
        return
    total = state.get('total', 0)
    st.progress(state.get('finished', 0) / total if total else 0,
                text=f"{state.get('status', 'Unknown').title()} \u00b7 {state.get('finished', 0)}/{total} evaluations finished")
    if state.get('current'):
        job = state['current']
        st.caption(f"Task {job['task']} \u00b7 Dataset {job['dataset']} \u00b7 {RESULT_MODELS.get(job['model'], 'Selected local model')}")
    if state.get('error'):
        st.error(state['error'])
    results = [read(p) for p in sorted((path.parent / 'results').glob('*.json'))]
    results = [r for r in results if r['model'] in RESULT_MODELS and r.get('judge_model', DEFAULT_JUDGE) != LOCAL_MODEL]
    if results:
        st.dataframe(pd.DataFrame([{'Task': r['task'], 'Dataset': r['dataset'], 'Model': MODELS[r['model']],
            'Judge': JUDGES.get(r.get('judge_model', DEFAULT_JUDGE), r.get('judge_model')), 'Status': r['status'], 'Score': percent(score(r)), 'Error': r.get('error', '')} for r in results]), hide_index=True)
    if state['status'] in ('finished', 'failed') and st.button("Refresh saved results", key="refresh_results"):
        st.rerun()
