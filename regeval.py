import argparse
import json
from pathlib import Path
import sys

from core.contracts import TASKS, MODELS
from core.document_loader import PRIVATE, ROOT, dump, inventory, load, prepare, workspace
from core.grader import grade, oracle

def context(task):
    case = load(PRIVATE / "case.json")
    spec = dict(case["tasks"][task])
    gold = PRIVATE / task / "gold.json"
    if gold.exists():
        spec["gold"] = load(gold)
    return spec, PRIVATE / task / "workspace"

def cli(args=None):
    p = argparse.ArgumentParser(prog="regeval")
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("prepare", help="Build private workspaces from the authorized archive")
    init.add_argument("archive", type=Path)
    init.add_argument("--inventory", action="store_true")
    schema = sub.add_parser("schema")
    schema.add_argument("task", choices=TASKS)
    for command in ("grade","verify-gold","run"):
        c = sub.add_parser(command)
        c.add_argument("task", choices=TASKS)
        if command == "grade":
            c.add_argument("answer", type=Path)
            c.add_argument("--out", type=Path)
        if command == "run":
            c.add_argument("--model", required=True)
            c.add_argument("--backend", choices=["openai","ollama"], default="ollama")
            c.add_argument("--permit-provider", action="store_true")
            c.add_argument("--budget", type=int, default=6500)
            c.add_argument("--timeout", type=int, default=300)
            c.add_argument("--retrieval", choices=["ranked","coverage"], default="coverage")
    a = p.parse_args(args)
    try:
        if a.command == "schema":
            print(json.dumps(MODELS[a.task].model_json_schema(), indent=2))
        elif a.command == "prepare":
            case = load(PRIVATE / "case.json")
            for task in TASKS:
                w = prepare(a.archive, case, task)
                (w / "instruction.md").write_bytes((ROOT / "tasks" / task / "instruction.md").read_bytes())
                dump(w / "schema.json", MODELS[task].model_json_schema())
                workspace(w)
                print(f"Prepared {task}")
            if a.inventory:
                report = inventory(a.archive, {d["member"] for d in case["documents"].values()})
                dump(PRIVATE / "inventory.json", report)
                print(json.dumps(report["counts"]))
        else:
            spec, w = context(a.task)
            if a.command == "run":
                from core.agent_runner import run
                result = run(a.task, spec, w, a.model, a.backend, a.permit_provider, a.budget, a.timeout, a.retrieval)
                print(json.dumps(result, indent=2))
                return
            if not spec.get("gold"):
                raise ValueError(f"Gold is pending. Install .private/{a.task}/gold.json first.")
            pages = workspace(w)
            if a.command == "verify-gold":
                result = grade(a.task, json.dumps(oracle(a.task,spec,pages)), spec, pages)
            else:
                raw = b""
                if a.answer.exists():
                    with a.answer.open("rb") as f:
                        raw = f.read(200_001)
                result = grade(a.task, raw, spec, pages)
            out = getattr(a,"out",None) or PRIVATE / a.task / "score.json"
            dump(out, result)
            print(json.dumps(result, indent=2))
            if a.command == "verify-gold" and result["score"] != 1:
                raise SystemExit(1)
    except (OSError, ValueError, KeyError, ImportError) as error:
        p.exit(2, f"{error}\n")

if __name__ == "__main__":
    cli()

