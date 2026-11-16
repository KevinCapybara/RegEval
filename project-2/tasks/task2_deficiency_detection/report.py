"""Export only allowlisted source-free metrics; never copy model prose or paragraph IDs."""
import argparse
import json
from pathlib import Path

MODELS=('gpt-6-luna','gpt-5-nano')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def aggregate(rows):
    result={}
    for model in MODELS:
        subset=[r for r in rows if r['name']==model]
        complete=(len(subset)==5 and {r['dataset'] for r in subset}=={f'dataset_{i:02}' for i in range(1,6)}
                  and all(r['status']=='scored' and r['score'] is not None for r in subset))
        result[model]=sum(r['score'] for r in subset)/5 if complete else None
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runs',type=Path,required=True,help='Explicit batch summary.json; never silently choose a better run')
    ap.add_argument('--calibration',type=Path,required=True)
    ap.add_argument('--review',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    rows=load(args.runs)
    calibration=load(args.calibration)
    reviews=load(args.review)
    metrics=[{k:r.get(k) for k in ('dataset','name','status','score','criteria')} for r in rows]
    means=aggregate(rows)
    lines=['# Task 2 results: deficiency-paragraph detection','',
           'Experiment date: November 14, 2026. Five distinct application families; 96 numbered logical paragraphs across complete supplied sections. Gold and all source-bearing inputs, responses, reviews, and verdicts remain local. Public dataset aliases intentionally omit source identities and gold IDs.','',
           '| Dataset | Paragraphs | GPT-6 Luna | GPT-5 nano |','| --- | ---: | ---: | ---: |']
    for n,count in enumerate((22,17,22,15,20),1):
        cells=[]
        for model in MODELS:
            found=[r for r in rows if r['dataset']==f'dataset_{n:02}' and r['name']==model]
            r=found[0] if len(found)==1 else {}
            cells.append(f"{r['score']:.0%}" if r.get('status')=='scored' and r.get('score') is not None else 'UNSCORED')
        lines.append(f'| {n} | {count} | '+ ' | '.join(cells)+' |')
    lines += ['| **Equal-weight mean** | **96** | '+' | '.join(f'{means[m]:.0%}' if means[m] is not None else 'UNSCORED' for m in MODELS)+' |','',
              'Every dataset uses four binary checks worth 25% each: all true deficiency paragraphs found; no non-deficiencies selected; every selection supported by valid evidence; correct count and coverage. GPT-6 Luna judges each answer in a separate request. Python validates and aggregates, without semantic grading. No task-wide pass threshold is defined.','',
              'See [ANALYSIS.md](ANALYSIS.md) for concrete failure analysis, quote-contract sensitivity, alias-error recovery, model settings, and reproduction commands.','',
              '## Gold review and calibration','',
              f"Blinded model review completed for {sum(r['status']=='reviewed' for r in reviews)}/5 datasets; {sum(len(r.get('disagreements',[])) for r in reviews)} disagreements and {sum(len(r.get('ambiguous',[])) for r in reviews)} paragraph ambiguity flags. The reviewer received source and instructions, not draft gold. The author checked source spans and adjudication rules before freezing hashes. This is model-assisted verification, not human expert certification.",'',
              f"Judge calibration: {sum(r.get('calibration_pass') is True for r in calibration)}/{len(calibration)} expected binary vectors matched. Empty, wholly wrong, and gold-equivalent controls were run on every dataset. Dataset 1 additionally tested omission, false positive, fabricated evidence twice, count-only error, equivalent paraphrase/reordering, and repeated gold.",'',
              '| Control | Dataset | Expected matched |','| --- | --- | --- |']
    for r in calibration:
        lines.append(f"| {r['name']} | {r['dataset']} | {'Yes' if r.get('calibration_pass') else 'No / unscored'} |")
    lines += ['', '## Candidate check results','', '| Dataset | Candidate | Recall | Precision | Evidence | Coverage |', '| --- | --- | ---: | ---: | ---: | ---: |']
    for r in rows:
        lines.append('| '+r['dataset']+' | '+r['name']+' | '+' | '.join(str((r.get('criteria') or {}).get(k,'—')) for k in ('recall','precision','evidence','coverage'))+' |')
    lines += ['', '## Scope and limitations','',
              'One candidate run per model per dataset is not a robust model ranking. Repeated judge checks cover only two controlled cases on one dataset; they do not establish general judge reliability. Candidate Luna and judge Luna are separate calls but share a model, creating correlated-error risk. No prior Task 1 answers were reused.', '',
              'Original repeated numbering and OCR artifacts require an explicit logical-paragraph policy. Required remediation can be a positive when its surrounding section identifies a blocker; generic safety updates and deferred reviews are negative. Explicit nonblocking context overrides defect-like recommendation wording. An unreadable section is omitted, not treated as evidence of no deficiency. No concealed content is reconstructed. PDF visual verification and human regulatory expert review remain outstanding.', '',
              'Source versions, prompts, response IDs, usage, hashes, and all failures are retained in private logs. store=false was used for hosted requests with explicit user authorization. GitHub receives task-specific code, documentation, tests, and this source-free report only.']
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (args.out/'metrics.json').write_text(json.dumps({'rows':metrics,'means':means,
        'calibration_matched':sum(r.get('calibration_pass') is True for r in calibration),
        'calibration_total':len(calibration)},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
