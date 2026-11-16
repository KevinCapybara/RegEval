"""Publish completed Task 5 scores locally without copying source into public files."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.dashboard_runner import save
from core.history import read, load_history, aggregate


def publish(run):
    run = Path(run).resolve()
    task = run.parents[2]
    summary = read(run/'summary.json')
    rows = summary['results']
    assert summary['status'] == 'complete'
    assert {r['dataset'] for r in rows} == set(range(1,6))
    assert all(r['status']=='scored' and r['candidate_model']=='gpt-6-luna'
               and r['judge_model']=='gpt-6-luna' for r in rows)
    now = datetime.now(timezone.utc).isoformat()
    batch = ROOT/'.private/dashboard_runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-task5-suite')
    jobs = [dict(task=5,dataset=r['dataset'],model='gpt-6-luna') for r in rows]
    save(batch/'configuration.json',dict(jobs=jobs,judge='gpt-6-luna',permit_provider=True,
         source_run=str(run), publication_only=True))
    calibration_count = 0
    for row in rows:
        folder = run/f"dataset_{row['dataset']:02}"
        checks = read(folder/'calibration_summary.json')
        assert all(c['passed'] for c in checks)
        calibration_count += len(checks)
        row.update(artifact_path=str(folder),finished_at=now,batch=batch.name)
        save(batch/'results'/f"{row['dataset']:03}.json",row)
    save(batch/'status.json',dict(status='finished',finished=5,total=5,current=None))
    summary['updated_at'] = now
    save(run/'summary.json',summary)
    save(task/'private/suite_latest.json',summary)
    latest_path = task/'private/latest_evaluation.json'
    previous = read(latest_path) if latest_path.is_file() else {}
    retained = [r for r in previous.get('results',[]) if r.get('candidate_model',r.get('model'))!='gpt-6-luna']
    save(latest_path,dict(task=5,updated_at=now,results=retained+rows,
        task_scores={'gpt-6-luna':summary['task_score']},source_run=str(run),note=summary['limitation']))
    public = dict(task=5,candidate='gpt-6-luna',judge='gpt-6-luna',updated_at=now,
        datasets_scored=5,task_score=summary['task_score'],calibration_passed=calibration_count,
        limitation=summary['limitation'],
        results=[{k:r[k] for k in ('dataset','status','score','criteria')} for r in rows])
    save(ROOT/'TASK5_RESULTS.json',public)
    lines = ['# Task 5 — five-dataset Luna evaluation', '', f'Updated: {now}', '',
        'Candidate: OpenAI GPT-6 Luna. Judge: separate OpenAI GPT-6 Luna calls. No local model used.', '',
        '| Dataset | Case | Score |', '|---|---|---:|']
    cases = ['Genuine duplicate plus distinct review cycles','Same-date Original subnumbers',
             'Shared package ID, distinct review cycles A','Shared package ID, distinct review cycles B',
             'Same-date package, different base applications']
    lines += [f"| {r['dataset']} | {cases[r['dataset']-1]} | {r['score']:.0%} |" for r in rows]
    lines += ['',f"**Task average: {summary['task_score']:.0%}; 5/5 scored.**",'',
        f'All five references passed independent Luna review. {calibration_count}/{calibration_count} endpoint checks passed '
        '(empty and wholly wrong answers: 0%; reference answers: 100%).', '', summary['limitation'], '',
        'This run evaluates Luna only. Previous Nano results are historical and do not establish five-dataset Nano coverage.', '',
        'Public score files contain only aggregate metrics and criterion scores. Source evidence, gold, review records, '
        'candidate answers and raw API responses remain in ignored private folders. API calls used store=false.', '']
    report = '\n'.join(lines)
    (ROOT/'TASK5_RESULTS.md').write_text(report,encoding='utf-8')
    (task/'SUITE_RESULTS.md').write_text(report,encoding='utf-8')
    (task/'private/LATEST_EVALUATION.md').write_text(report,encoding='utf-8')
    loaded = load_history(ROOT)[4]
    assert aggregate(loaded,'gpt-6-luna') == (summary['task_score'],5)
    assert all(loaded['results'][(r['dataset'],'gpt-6-luna')]['score']==r['score'] for r in rows)
    print(json.dumps(dict(task_score=summary['task_score'],datasets=5,calibration=calibration_count,
                         webapp_verified=True,batch=str(batch))))


if __name__ == '__main__':
    publish(sys.argv[1])
