"""Read-only corpus discovery; all corpus-bearing output stays in ignored private/."""
import argparse
import hashlib
import io
import itertools
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def audit(archive, output):
    from pypdf import PdfReader
    with zipfile.ZipFile(archive) as z:
        records = []
        for n in sorted(z.namelist()):
            if not n.endswith('.json'):
                continue
            d = json.loads(z.read(n))
            text = d.get('text', '')
            words = re.findall(r'\w+', text.lower())
            shingles = set(tuple(words[i:i+8]) for i in range(len(words)-7))
            records.append(dict(path=n, record=d, sha256=digest(z.read(n)),
                                text_sha256=digest(text.encode()),
                                normalized_sha256=digest(''.join(words).encode()),
                                refs=sorted(set(re.findall(r'Reference\s*ID\s*:\s*(\d{6,8})', text, re.I))),
                                shingles=shingles, family=n.split('/')[1]))
        pairs = []
        for a,b in itertools.combinations(records, 2):
            sa,sb=a['shingles'],b['shingles']
            common=len(sa & sb)
            overlap=common/min(len(sa),len(sb)) if sa and sb else 0
            shared=sorted(set(a['refs']) & set(b['refs']))
            same_family=a['family']==b['family']
            same_date=a['record'].get('letter_date')==b['record'].get('letter_date')
            if shared or (same_family and same_date) or overlap >= .65:
                pairs.append(dict(a=a['path'], b=b['path'], shared_refs=shared,
                                  same_family=same_family, same_date=same_date,
                                  exact_text=a['text_sha256']==b['text_sha256'] and bool(sa),
                                  normalized_equal=a['normalized_sha256']==b['normalized_sha256'] and bool(sa),
                                  shingle_containment=round(overlap,6)))
        # Extract page-level evidence for every flagged package, not only the chosen pilot.
        flagged={p[k] for p in pairs for k in ('a','b')}
        pdfs={}
        for r in records:
            if r['path'] not in flagged:
                continue
            n=str(Path(r['path']).parent / r['record']['file_name']).replace('\\','/')
            if n not in z.namelist():
                n=r['path'].split('--record-')[0]+'.pdf'
            if n in pdfs or n not in z.namelist():
                continue
            raw=z.read(n)
            pages=[p.extract_text() or '' for p in PdfReader(io.BytesIO(raw)).pages]
            pdfs[n]=dict(sha256=digest(raw), pages=[dict(page=i+1,text=t) for i,t in enumerate(pages)])
        result=dict(archive_sha256=digest(Path(archive).read_bytes()),
                    counts=dict(json_records=len(records),text_records=sum(bool(r['record'].get('text')) for r in records),
                                pdfs=sum(n.endswith('.pdf') for n in z.namelist()),
                                family_folders_including_unreleased=len({r['family'] for r in records})),
                    candidate_rule='shared Reference ID OR same folder/date OR >=65% 8-word-shingle containment; heuristic, not proof of exhaustiveness',
                    candidate_pairs=pairs,
                    records=[{k:v for k,v in r.items() if k!='shingles'} for r in records],pdf_evidence=pdfs)
        dump(output,result)
        print(json.dumps(dict(counts=result['counts'],candidate_pairs=len(pairs),exact_duplicate_pairs=sum(p['exact_text'] for p in pairs),output=str(output))))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--output',type=Path,default=ROOT/'private/audit.json')
    args=p.parse_args()
    audit(args.archive,args.output)
