"""Combine explicitly selected runs, retaining retries and unresolved judge concerns."""
import argparse
from pathlib import Path
from grader import AGENTS, aggregate, context, dump, load, sha, snapshot


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--private-root',type=Path,required=True)
    ap.add_argument('--runs',type=Path,nargs='+',required=True,help='Primary then authorized retry runs, in order')
    ap.add_argument('--needs-review',type=Path,help='JSON keyed by dataset/model with reason and verdict references')
    args=ap.parse_args()
    rows={}; provenance={}
    for run in args.runs:
        for key,verdict in load(run/'summary.json').items():
            ds,model=key.split('/')
            if model not in AGENTS:raise ValueError('Unexpected model')
            if verdict.get('status')=='scored':
                request=load(run/ds/model/'judge/request.json')
                payload=__import__('json').loads(request['input'])
                visible,gold=context(args.private_root/ds)
                if payload['paragraphs']!=visible['paragraphs'] or payload['gold']!=gold:
                    raise ValueError('Cannot aggregate changed source or gold')
                if payload['question']!=visible['question']:
                    raise ValueError('Cannot aggregate changed instructions')
            rows[key]=verdict
            provenance.setdefault(key,[]).append(str(run))
    overrides=load(args.needs_review) if args.needs_review else {}
    for key,concern in overrides.items():
        if key not in rows:raise ValueError('Unknown review target')
        rows[key]=dict(status='needs_review',score=None,criteria=None,review_concern=concern)
    certs=sorted((args.private_root/'runs').glob('*-calibrate-*/calibration.json'))
    cert=load(certs[-1]) if certs else {}
    valid=cert.get('passed') is True and cert.get('snapshot')==snapshot(args.private_root)
    report=dict(results=rows,provenance=provenance,task_scores=aggregate(rows,valid),
                calibration_certificate=str(certs[-1]) if certs else None,
                source_manifest_hash=sha(load(args.private_root/'manifest.json')))
    target=args.private_root/'final_results.json'
    dump(target,report)
    print(target)
    print(__import__('json').dumps(report['task_scores'],indent=2))


if __name__=='__main__':main()
