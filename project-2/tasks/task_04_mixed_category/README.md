# Task 4: mixed-category deficiency classification

Five private datasets test complete, justified category sets for paragraphs already identified as deficiencies. Task 4 does not test deficiency detection. Each dataset has five paragraphs: two mixed-category passages and three single-category controls. This is a curated boundary test, not a corpus prevalence estimate.

Install once with `python -m pip install -r tasks/task_04_mixed_category/requirements.txt`. Supply `OPENAI_API_KEY` in the environment or use `--env-file /private/path/.env`. The runner uses the official OpenAI endpoint, verifies exact model availability, and never substitutes a model. All semantic decisions are made by `gpt-6-luna`; candidates are independently generated with `gpt-5-nano` and `gpt-6-luna`.

One-command grading, from the repository root:

```sh
python tasks/task_04_mixed_category/grader.py grade --private-root /authorized/task4 --dataset 1 --answer /private/answer.json --permit-provider
```

The authorized private package must have `dataset_01` through `dataset_05`, each with `workspace/paragraphs.json`, `gold.json`, and `source_records.json`. Give candidates only the instruction and workspace paragraphs. Gold and source review records stay outside the candidate workspace. The grader sends the candidate answer, question, paragraphs, gold, and rubric to a separate Luna call. It writes exact requests, raw responses, parsed responses, metadata, and verdicts under the private root's `runs/` directory. It prints status, score, and log path. No separate app, registry, shared grader, or dashboard is needed.

Private workflow commands:

```sh
python tasks/task_04_mixed_category/grader.py review --private-root /authorized/task4 --permit-provider
python tasks/task_04_mixed_category/grader.py calibrate --private-root /authorized/task4 --permit-provider
python tasks/task_04_mixed_category/grader.py evaluate --private-root /authorized/task4 --permit-provider
```

`evaluate` independently runs both candidates on all five datasets and judges each with Luna. `--agent` and `--dataset` restrict debugging runs. `--workers` controls concurrent API requests (default 3). Each invocation creates a new run directory; nothing silently overwrites prior calls. API or JSON failures remain errors with no score. `needs_review` also has no numeric score. A complete task average requires all five scores and a passing calibration certificate matching the current instruction, rubric, and gold hashes. There is no task pass threshold.

The four equally weighted checks are no omissions, no additions, evidence, and distribution. Every criterion is binary across all paragraphs. See [rubric.md](rubric.md) and [instruction.md](instruction.md). Python performs format validation, source-integrity checks, and aggregation; it does not decide semantic correctness. The observed Luna calibration suite tests empty, wholly wrong, and gold answers on every dataset, plus omission, addition, fabricated evidence, incorrect distribution, equivalent explanation, repeated calls, duplicate IDs, and candidate-instruction injection. Unsupported additions naturally also fail evidence; they are not falsely described as an isolated evidence-correct error.

Run transport/aggregation tests with `python -m unittest discover -s tasks/task_04_mixed_category -p test_grader.py`. These tests do not substitute for real semantic endpoint calibration.

To consolidate explicit retry runs without discarding failed attempts, use `summarize.py --private-root /authorized/task4 --runs /private/primary-run /private/retry-run --needs-review /authorized/task4/judge_concerns.json`. The final private `final_results.json` is authoritative over earlier run-level averages. The known Luna Dataset 3 answer has conflicting evidence verdicts; its saved answer hash is flagged in the private concern ledger so grading that same answer again remains unscored until adjudicated. Raw verdicts are preserved.

## Source access and publication

The [Raycaster access terms](https://www.raycaster.ai/hackathon) permit hackathon and related research use, prohibit document/excerpt redistribution outside the event, and require training and data sharing to be disabled for AI tools. The archive README also says not to redistribute. The user confirmed both settings were disabled for the RegEval API project on November 14, 2026; all calls use `store=false`. This flag alone is not proof of disabled account-level data sharing or zero retention. `--permit-provider` asserts that the caller has verified permitted processing and provider settings.

This public directory contains implementation, rules, and sanitized findings only. Restricted source text, PDFs, hidden gold, selection recipe, review ledgers, and document-bearing logs are retained locally in `.private/task4/`. Obtain the private package only through the event-authorized route; a public clone alone cannot execute source-backed grading. Do not upload those files to a public repository or include them in a public pull request. No source access restrictions are bypassed.

Gold received an author source-reading pass and separate Luna audits. Targeted PDF visual checks resolved selected OCR/boundary concerns. This is not independent human regulatory validation; the same model family auditing and judging can share blind spots. See [TASK4_REPORT.md](TASK4_REPORT.md) for actual results and limitations.
