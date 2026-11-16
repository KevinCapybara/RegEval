# Task 5: duplicate-aware corpus counting

Status: five source-grounded datasets evaluated with OpenAI GPT-6 Luna (95% mean, 5/5 scored). See SUITE_RESULTS.md. The suite contains one genuine-duplicate case and four false-merge controls; positive-duplicate diversity remains limited. REPORT.md retains the historical pilot report. No source files, hidden gold, or document-bearing logs are included in Git. Obtain the authorized local private bundle separately; this repository does not authorize redistributing it.

The candidate receives only `instruction.md` and `private/pilot/workspace.json`. The evaluator alone receives `private/pilot/gold.json` and logs. Keep these in separate environments when running an agent with filesystem access. The API runner sends only the candidate workspace to each test model and gives gold solely to independent review/judge calls.

Dependencies: Python 3.10+, `openai`, `pydantic>=2`, `pypdf`. Set `OPENAI_API_KEY` locally. Run from the repository root. All model requests use the OpenAI API with `store=false`; that setting does not itself establish contractual data-use permission. The local pilot run was explicitly authorized by the user.

One-command grader:

```powershell
python tasks/task5_duplicate_counting/grade.py --workspace tasks/task5_duplicate_counting/private/pilot/workspace.json --gold tasks/task5_duplicate_counting/private/pilot/gold.json --answer ANSWER.json
```

The grader prints status, score and log path. It exits 2 for unscored errors/review and 0 for a completed judgment (including a scored incorrect answer). GPT-6 Luna makes all semantic decisions; Python validates strict integer 0/1 values and calculates their equal-weight average. No deterministic fallback or model substitution is used.

Reproduce the corpus screen (does not produce verified datasets):

```powershell
python tasks/task5_duplicate_counting/audit.py --archive PATH_TO_AUTHORIZED_CORPUS.zip
```

Run the verified private pilot, including independent gold review, ten real semantic calibrations, and separate candidate/judge calls:

```powershell
python tasks/task5_duplicate_counting/run_pilot.py --dataset tasks/task5_duplicate_counting/private/pilot
```

Optional `--env-file PATH` loads a local credentials file without publishing it. Private runs contain the exact source/gold snapshots, prompts, responses, usage/model metadata, calibration verdicts, and scores. An API or parse failure is never a scored failure. A pilot score must not be reported as a five-dataset task score.

Format/failure checks (not a substitute for semantic calibration):

```powershell
python tasks/task5_duplicate_counting/test_grader.py
```

## Five-dataset suite

Run `python tasks/task5_duplicate_counting/run_suite.py --env-file PATH_TO_LOCAL_ENV` to construct, independently review, calibrate, and evaluate all five cases with OpenAI GPT-6 Luna. This sends source evidence and reference data to OpenAI with `store=false` and requires authorized provider use. All document-bearing artifacts are stored under ignored `private/`. Use `--resume PRIVATE_RUN_PATH` to retain completed evaluations.

The webapp discovers verified datasets under `private/datasets/dataset_01` through `dataset_05`. Publish a completed run from the main RegEval checkout with `python scripts/publish_task5_suite.py PRIVATE_RUN_PATH`; this updates local webapp results and sanitized score reports without rerunning model calls.
