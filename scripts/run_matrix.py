"""Run both configured models on all three tasks with the same context settings."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.agent_runner import run
from core.contracts import TASKS
from regeval import context

def main():
    p = argparse.ArgumentParser()
    p.add_argument("models", nargs=2)
    p.add_argument("--backend", choices=["ollama","openai"], default="ollama")
    p.add_argument("--permit-provider", action="store_true")
    p.add_argument("--budget", type=int, default=6500)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--retrieval", choices=["ranked","coverage"], default="coverage")
    a = p.parse_args()
    if a.models[0] == a.models[1]:
        p.error("Supply two distinct model IDs")
    if a.backend == "openai" and not a.permit_provider:
        p.error("Hosted model calls require explicit data-use approval")
    failures = 0
    for task in TASKS:
        spec, w = context(task)
        for model in a.models:
            try:
                result = run(task,spec,w,model,a.backend,a.permit_provider,a.budget,a.timeout,a.retrieval)
                print(json.dumps(result),flush=True)
            except Exception as error:
                failures += 1
                print(json.dumps({"task":task,"model":model,"error":str(error)}),file=sys.stderr,flush=True)
    return bool(failures)

if __name__ == "__main__":
    raise SystemExit(main())

