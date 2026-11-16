import hashlib
import io
import json
import re
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / ".private"
MAX_PDF = 50_000_000

def sha(data):
    return hashlib.sha256(data).hexdigest()

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def normalize(text):
    value = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(re.findall(r"[^\W_]+", value))

def member(z, path):
    info = z.getinfo(path)
    if info.file_size > MAX_PDF:
        raise ValueError("Oversized archive member")
    return z.read(info)

def pdf(data):
    return PdfReader(io.BytesIO(data))

def extract(reader):
    return [page.extract_text() or "" for page in reader.pages]

def slice_pdf(reader, first, last):
    if not 1 <= first <= last <= len(reader.pages):
        raise ValueError("Invalid PDF range")
    writer = PdfWriter()
    for i in range(first - 1, last):
        writer.add_page(reader.pages[i], excluded_keys=("/Annots", "/AA"))
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()

def inventory(archive, selected):
    result = []
    with zipfile.ZipFile(archive) as z:
        records = {}
        for info in z.infolist():
            if info.filename.endswith(".json"):
                record = json.loads(member(z, info.filename))
                if not all(k in record for k in ("file_name", "letter_type", "letter_date")):
                    continue
                path = str(Path(info.filename).parent / record["file_name"]).replace("\\", "/")
                records.setdefault(path, []).append((record["letter_type"], record["letter_date"]))
        for info in z.infolist():
            name = info.filename
            if info.is_dir():
                continue
            item = dict(relative_path=name, size=info.file_size, checksum=None, page_count=None,
                        document_type="metadata" if name.endswith(".json") else "documentation",
                        date=[], extraction_method=None, relevance="selected" if name in selected else "out_of_scope")
            try:
                data = member(z, name)
                item["checksum"] = sha(data)
                if name.lower().endswith(".pdf"):
                    types = records.get(name, [])
                    item.update(page_count=len(pdf(data).pages), document_type="FDA correspondence package",
                                letter_types=sorted({t for t,d in types}), date=sorted({d for t,d in types if d}),
                                extraction_method="pypdf embedded text; no OCR")
            except Exception as error:
                item["error"] = type(error).__name__
            result.append(item)
    return {"counts":dict(Counter(x["document_type"] for x in result)), "files": result}

def prepare(archive, case, task):
    spec = case["tasks"][task]
    task_root = PRIVATE / task
    w = task_root / "workspace"
    w.mkdir(parents=True, exist_ok=True)
    entries = {}
    with zipfile.ZipFile(archive) as z:
        for alias in spec["documents"]:
            source = case["documents"][alias]
            if not re.fullmatch(r"[a-z0-9_-]+", alias):
                raise ValueError("Invalid document alias")
            original = member(z, source["member"])
            if sha(original) != source["sha256"]:
                raise ValueError("Source checksum differs from reviewed case")
            data = slice_pdf(pdf(original), source["first"], source["last"])
            name = alias + ".pdf"
            (w / name).write_bytes(data)
            pages = extract(pdf(data))
            entries[name] = {"sha256":sha(data), "page_count":len(pages),
                "date":source["date"], "type":source["type"],
                "blank_or_low_text_pages":[i for i,p in enumerate(pages,1) if len(p.strip()) < 150]}
    dump(w / "manifest.json", entries)
    dump(w / "transcriptions.json", spec.get("transcriptions", {}))
    (w / "case.md").write_text(spec["brief"] + "\n", encoding="utf-8")
    return w

def workspace(w):
    entries = load(w / "manifest.json")
    pages = {}
    for name, info in entries.items():
        if not re.fullmatch(r"[a-z0-9_-]+\.pdf", name):
            raise ValueError("Invalid manifest filename")
        p = w / name
        if p.is_symlink() or p.resolve().parent != w.resolve():
            raise ValueError("PDF must be inside workspace")
        data = p.read_bytes()
        if sha(data) != info["sha256"]:
            raise ValueError("Workspace checksum mismatch")
        items = extract(pdf(data))
        if len(items) != info["page_count"]:
            raise ValueError("Workspace page count mismatch")
        pages[name] = items
    transcriptions = w / "transcriptions.json"
    if transcriptions.is_file():
        for name, by_page in load(transcriptions).items():
            for page, spans in by_page.items():
                i = int(page) - 1
                if not 0 <= i < len(pages[name]):
                    raise ValueError("Transcription page out of bounds")
                # Keep separate spans separated so citations cannot join them into one quote.
                pages[name][i] += "\n verified transcription excerpt \n" + "\n verified transcription excerpt \n".join(spans)
    return pages
