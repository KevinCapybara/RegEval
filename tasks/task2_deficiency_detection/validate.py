"""Structural/provenance checks only; does not replace semantic Luna grading."""
import argparse
import hashlib
import json
from pathlib import Path


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def validate(root):
    families = set()
    summary = []
    for n in range(1,6):
        d = root / 'datasets' / f'dataset_{n:02}'
        w, g = read(d/'workspace.json'), read(d/'gold.json')
        raw = (d/'source_record.json').read_bytes()
        source = json.loads(raw.decode('utf-8-sig'))['text']
        assert hashlib.sha256(raw).hexdigest() == g['source_sha256']
        families.add(json.dumps(w['family'], sort_keys=True))
        ids = [p['id'] for p in w['paragraphs']]
        assert ids == [f'P{i:03}' for i in range(1,len(ids)+1)]
        assert [r['id'] for r in g['records']] == ids
        assert 0 < len(g['selected_ids']) < len(ids)
        assert [r['id'] for r in g['records'] if r['is_deficiency']] == g['selected_ids']
        assert not any(k in w for k in ('gold', 'selected_ids', 'records'))
        previous = 0
        for p, r in zip(w['paragraphs'],g['records']):
            ref = r['source_reference']
            a,b = ref['start_char'],ref['end_char_exclusive']
            assert previous <= a < b
            previous = b
            assert source[a:b] == r['raw_span']
            assert ' '.join(r['raw_span'].split()) == p['text']
            assert r['quote'] in p['text']
            assert r['explanation'].strip()
        for section in read(d/'sections.json'):
            a,b=section['start'],section['end']
            assert source[a:b] == section['raw_text']
            rows=[r for r in g['records'] if a <= r['source_reference']['start_char'] < b]
            assert rows[-1]['source_reference']['end_char_exclusive'] == b
            for left,right in zip(rows,rows[1:]):
                assert left['source_reference']['end_char_exclusive'] == right['source_reference']['start_char']
        summary.append({'dataset':w['dataset_id'],'paragraphs':len(ids),'structural_checks':'passed'})
    assert len(families)==5
    return summary


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--private-root',type=Path,required=True)
    print(json.dumps(validate(ap.parse_args().private_root),indent=2))
