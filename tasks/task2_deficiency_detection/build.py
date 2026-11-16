"""Build private datasets from an authorized private annotation specification."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(b):
    return hashlib.sha256(b).hexdigest()


def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def build(spec, out):
    families = set()
    for case in spec:
        raw = Path(case['source_path']).read_bytes()
        source = json.loads(raw.decode('utf-8-sig'))
        text = source['text']
        families.add(json.dumps(source['application_number'], sort_keys=True))
        paragraphs, records, sections = [], [], []
        for section in case['sections']:
            start = text.index(section['start'])
            end = text.index(section['end'], start + len(section['start']))
            positions = [text.index(item['start'], start, end) for item in section['items']]
            assert positions == sorted(set(positions))
            assert not text[start:positions[0]].strip().replace(section['heading'], '').strip(), 'Unassigned section prefix'
            sections.append({'heading': section['heading'], 'start': start, 'end': end,
                             'raw_text': text[start:end]})
            for i, item in enumerate(section['items']):
                a, b = positions[i], positions[i+1] if i+1 < len(positions) else end
                pid = f'P{len(paragraphs)+1:03}'
                body = ' '.join(text[a:b].split())
                ref = {'source_member': case['source_member'], 'start_char': a,
                       'end_char_exclusive': b, 'source_record_sha256': digest(raw)}
                paragraphs.append({'id': pid, 'section': section['heading'], 'text': body})
                records.append({'id': pid, 'is_deficiency': item['positive'],
                                'explanation': item['reason'], 'source_reference': ref,
                                'raw_span': text[a:b], 'quote': item.get('quote', body[:160])})
        ids = [r['id'] for r in records if r['is_deficiency']]
        assert ids and len(ids) < len(records)
        target = out / case['id']
        workspace = {'dataset_id': case['id'], 'family': source['application_number'],
                     'letter_date': source['letter_date'], 'scope': case['scope'],
                     'paragraphs': paragraphs,
                     'transcription': 'Whitespace reflow only. OCR artifacts and visible redactions retained. No redacted content inferred. Headings are context, not scored units.'}
        gold = {'selected_ids': ids, 'records': records, 'total_paragraphs': len(records),
                'review_status': 'assistant-authored; separate blinded model review required',
                'source_member': case['source_member'], 'source_sha256': digest(raw)}
        dump(target / 'workspace.json', workspace)
        dump(target / 'gold.json', gold)
        (target / 'source_record.json').write_bytes(raw)
        dump(target / 'sections.json', sections)
        lines = [workspace['scope'], '', workspace['transcription'], '']
        last = None
        for p in paragraphs:
            if p['section'] != last:
                lines += ['## ' + p['section'], '']
                last = p['section']
            lines += ['[' + p['id'] + '] ' + p['text'], '']
        (target / 'letter.md').write_text('\n'.join(lines), encoding='utf-8')
    assert len(spec) == len(families) == 5


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    build(json.loads(args.spec.read_text(encoding='utf-8')), args.out)
