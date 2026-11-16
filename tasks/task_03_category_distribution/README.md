# Task 3: category-distribution aggregation

Five authored synthetic datasets supply authoritative paragraph labels directly. No source text is needed and no restricted CRL material or real application identifiers are included. This tests aggregation only; it does not validate real-world classification or estimate FDA corpus prevalence.

The candidate receives only `instruction.md` and one `inputs/dataset_XX/input.json`. Hidden gold, membership ledgers, verification records, calibration fixtures and complete API logs live under ignored `.private/`. Gold is hidden from candidate calls, not cryptographically secret: supplied labels necessarily determine all totals. Public synthetic inputs permit reconstruction for independent audit.

## Run from the repository root

Requires Python 3.10+ and the OpenAI Python SDK (`python -m pip install openai`). Set `OPENAI_API_KEY` in the environment, or append `--env-file /path/to/.env` to API commands. Only the official OpenAI endpoint is used, with `store=false`; requested IDs are `gpt-5-nano` and `gpt-6-luna`, without substitutions.

```powershell
python tasks/task_03_category_distribution/task3.py build
python tasks/task_03_category_distribution/task3.py verify
python -m unittest discover -s tasks/task_03_category_distribution -p test_task3.py -v
python tasks/task_03_category_distribution/task3.py calibrate
python tasks/task_03_category_distribution/task3.py run
```

Inspect calibration results before interpreting candidate scores. Run directories are unique by default; `--out` must name a new directory. Each candidate has its own separate Luna judge request, including when the candidate is Luna. Judge prompts do not disclose model identity or expected calibration outcomes. Candidate and judge calls have 10,000 output-token limits; Nano uses minimal reasoning, while Luna uses its default. There are no tools or retrieval in candidate calls. API/parse failures and needs_review results have no numeric score; a task mean is reported only if all five datasets have scores.

## One-command saved-answer grader

After `build`, grade any saved UTF-8 answer (JSON, prose or a table) without regenerating it:

```powershell
python tasks/task_03_category_distribution/task3.py grade --dataset 1 --answer path/to/saved-answer.txt
```

This always calls Luna. Python validates strict binary verdicts and averages the four decisions; it does not semantically evaluate the answer. The answer is retained verbatim inside the saved judge request. Equivalent formatting is accepted.

## Dataset design

| Dataset | Deficiency paragraphs | All letters | All families | Deliberate difficulty |
| --- | ---: | ---: | ---: | --- |
| 1 | 10 | 8 | 4 | Baseline multi-label paragraphs, repeated cycles, unaffected family and empty letter |
| 2 | 12 | 8 | 5 | Five-label paragraph, three cycles, unequal family sizes, empty registered letter |
| 3 | 11 | 10 | 5 | Zero-prevalence nonclinical category, repeated category across cycles |
| 4 | 12 | 8 | 4 | Five duplicate export rows; distinct IDs with identical labels must remain distinct |
| 5 | 23 | 13 | 6 | Larger uneven families, two triple-label paragraphs, unaffected letters/families |

Paragraph denominators exclude non-deficiencies. Letter and family denominators include every registered entity. Categories overlap at every level; neither multi-label assignment totals nor review-cycle counts replace these denominators. See `instruction.md` for the complete counting policy.

`SCORING.md` is an unchanged snapshot of the supplied project policy, including its historical Task 1 status. `rubric.md` applies its binary, rounding, endpoint and unscored-error rules using Task 3's four requested checks. No shared Task 1 files or dashboard code were changed.

## Audit and publication

Every hidden ledger lists denominator members, category numerator members, excluded non-deficiency IDs and duplicate-row counts. A separate SQLite relational query verifies the set-based reference calculation. Tests use a hand-calculated fixture to check identities, cycles, empty populations and conflicting duplicates. These are reference-construction tests, not substitute answer graders.

Logs retain complete prompts, raw responses, response IDs, reported models, token usage, elapsed times, code/request hashes, verdict reasons and errors. The public report contains aggregate evaluation results. Hidden gold and logs are intentionally excluded from Git. All published inputs are newly authored synthetic records; no restricted source-bearing data is redistributed.
