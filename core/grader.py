from .contracts import ADAPTER
from .citation_checker import supports, verify
from .document_loader import normalize

WEIGHTS = {
    "reconciliation": {"factual": .30, "completeness": .25, "evidence": .30, "reasoning": .15},
    "response_mapping": {"factual": .40, "completeness": .20, "evidence": .25, "reasoning": .15},
    "resolution_audit": {"factual": .35, "completeness": .15, "evidence": .25, "reasoning": .25},
}
WEIGHTS["approval_dependency"] = WEIGHTS["reconciliation"].copy()
WEIGHTS["inspection_followup"] = WEIGHTS["resolution_audit"].copy()
VERSION = "1.1.0"

def grade(task, raw, spec, pages, judge=None):
    expected = spec["gold"]
    weights = WEIGHTS[task]
    report = {"score": 0.0, "max_score": 1.0, "grader_version": VERSION,
              "criteria": dict.fromkeys(weights, 0.0), "weights": weights, "errors": [], "matched": [], "claim_judgments": []}
    errors = report["errors"]
    try:
        if len(raw) > 200_000:
            raise ValueError()
        # Reject ambiguous JSON instead of silently accepting duplicate object keys.
        import json
        def unique(pairs):
            result = {}
            for k,v in pairs:
                if k in result:
                    raise ValueError()
                result[k] = v
            return result
        obj = ADAPTER.validate_python(json.loads(raw, object_pairs_hook=unique))
        if obj.task_id != task:
            raise ValueError()
    except (ValueError, TypeError, RecursionError):
        errors.append({"code":"invalid_answer_contract"})
        return report
    if not obj.records:
        errors.append({"code":"empty_answer"})
        return report

    def key(issue, edge=""):
        return (normalize(issue), normalize(edge))
    lookup = {}
    for item in expected:
        for alias in [item["issue"], *item.get("aliases", [])]:
            k = key(alias, item["fields"].get("response_ref", ""))
            if k in lookup and lookup[k] is not item:
                raise ValueError("Ambiguous gold alias")
            lookup[k] = item

    seen_ids, seen_items = set(), set()
    credited = dict.fromkeys(weights, 0.0)
    false_resolutions = 0
    rows = obj.records
    for row in rows:
        def error(code, **extra):
            errors.append({"record_id":row.record_id,"code":code,**extra})
        verified = []
        for citation in row.citations:
            c, problem = verify(citation, pages)
            if problem:
                error(problem, relative_path=citation.relative_path, page=citation.page)
            else:
                verified.append(c)
        row_id = row.record_id.casefold()
        if row_id in seen_ids:
            error("duplicate_record_id")
            continue
        seen_ids.add(row_id)
        item = lookup.get(key(row.issue_ref, getattr(row, "response_ref", "")))
        if task == "resolution_audit" and row.status == "documented_resolved" and (
            not item or item["fields"]["status"] != row.status
        ):
            false_resolutions += 1
            error("unsupported_fda_acceptance")
        if not item:
            error("unknown_issue_or_response")
            continue
        if item["id"] in seen_items:
            error("duplicate_issue_or_edge")
            continue
        seen_items.add(item["id"])
        classification_ok = all(normalize(str(getattr(row,k))) == normalize(str(v)) for k,v in item["fields"].items())
        if not classification_ok:
            error("incorrect_classification", gold_id=item["id"])
        hit = sum(any(supports(anchor, verified) for anchor in group) for group in item["anchors"])
        if not hit:
            error("missing_claim_support", gold_id=item["id"])
        accepted = normalize(row.claim) in {normalize(c) for c in item["claims"]}
        if not accepted and judge is not None:
            verdict = judge(row.claim, item["claims"])
            report["claim_judgments"].append({"record_id": row.record_id, "gold_id": item["id"], **verdict})
            accepted = verdict["equivalent"]
        if not accepted:
            error("claim_not_equivalent", gold_id=item["id"])
            continue
        credited["factual"] += 1
        credited["completeness"] += 1
        all_relevant = all(any(supports(anchor, [citation]) for group in item["anchors"] for anchor in group) for citation in verified)
        if len(verified) == len(row.citations) and all_relevant:
            credited["evidence"] += hit / len(item["anchors"])
        else:
            error("invalid_or_irrelevant_evidence", gold_id=item["id"])
        if classification_ok:
            credited["reasoning"] += 1
        if hit < len(item["anchors"]):
            error("missing_evidence_role", gold_id=item["id"])
        report["matched"].append(item["id"])

    for item in expected:
        if item["id"] not in report["matched"]:
            errors.append({"code":"missing_gold_item", "gold_id":item["id"]})
    for name, count in credited.items():
        denominator = len(expected) if name == "completeness" else max(len(expected), len(rows))
        report["criteria"][name] = round(count / denominator, 6)
    base = sum(weights[k]*report["criteria"][k] for k in weights)
    # Additional penalty for turning silence or an adverse action into FDA acceptance.
    report["score"] = round(max(0.0, base * (1 - false_resolutions / len(rows))), 6)
    return report

def oracle(task, spec, pages):
    from .document_loader import normalize
    def excerpt(path, page, phrase):
        normalized_page = normalize(pages[path][page-1])
        quote = normalize(phrase)
        if f" {quote} " not in f" {normalized_page} ":
            raise ValueError(f"Reviewed anchor absent: {path} p{page}: {phrase}")
        return {"relative_path":path,"page":page,"quote":phrase}
    records = []
    for row in spec["gold"]:
        citations = [excerpt(*group[0]) for group in row["anchors"]]
        records.append({"record_id":row["id"],"issue_ref":row["issue"],"claim":row["claims"][0],
                        "citations":citations, **row["fields"]})
    return {"task_id":task, "task_version":"1.0","answer_version":"1","records":records}

