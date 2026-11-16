# RegEval Task 3 — category-distribution aggregation

Run date: November 14, 2026 (America/Los_Angeles). Scoring: `task3-binary-v1`, applying the supplied `SCORING.md` policy with Task 3's requested four equally weighted binary checks.

## Outcome

All five datasets were run independently with both requested candidate models. Every answer was evaluated in a separate GPT-6 Luna call. Luna averaged **100%**, and Nano averaged **20%** across five equally weighted datasets. All ten results were scorable; there were no unresolved gold concerns or incomplete candidate/judge responses in the completed matrix.

Bits below are paragraph counts / letter counts / application-family counts / percentages, denominators and explanations. Each bit is strictly 0 or 1, worth 25%. A zero score means no entire criterion passed, not that every individual number was wrong.

| Dataset | Nano checks | Nano score | Luna checks | Luna score |
| --- | --- | ---: | --- | ---: |
| 1 | 1 / 0 / 1 / 0 | 50% | 1 / 1 / 1 / 1 | 100% |
| 2 | 0 / 1 / 0 / 0 | 25% | 1 / 1 / 1 / 1 | 100% |
| 3 | 0 / 1 / 0 / 0 | 25% | 1 / 1 / 1 / 1 | 100% |
| 4 | 0 / 0 / 0 / 0 | 0% | 1 / 1 / 1 / 1 | 100% |
| 5 | 0 / 0 / 0 / 0 | 0% | 1 / 1 / 1 / 1 | 100% |
| Equal-weight mean | | **20%** | | **100%** |

## Dataset and gold verification

Five newly authored synthetic datasets contain multiple letters and families, repeated review cycles, multi-label paragraphs, non-deficiency rows and unaffected registered entities. Dataset 3 includes a zero-prevalence category; Dataset 4 includes duplicate export rows. Inputs contain authoritative labels and identifiers, without source paragraphs. Classification is neither requested nor graded. These labels are verified by construction, not claimed to be expert-reviewed FDA annotations.

The denominator populations are respectively 10/8/4, 12/8/5, 11/10/5, 12/8/4 and 23/13/6 (unique deficiency paragraphs / registered letters / registered families). Every category has an exact numerator, denominator and percentage at each level. An ID-level ledger records all numerator members, denominator members, excluded non-deficiencies and removed duplicate exports. Multi-label paragraph assignments and overlapping affected letters/families are counted independently; category percentages need not sum to 100%.

Gold was computed using identity sets and independently recomputed from raw export rows with SQLite joins and COUNT(DISTINCT). All 75 category-level fraction/percentage cells agreed. Four reference tests passed, covering hand-calculated totals, repeated review cycles, unaffected registry populations, duplicate-export invariance, conflicting IDs and invalid non-deficiency labels. Verification was rerun after reconstructing private gold from the public synthetic inputs. Python performs reference arithmetic and verdict-format validation only; all answer evaluations are Luna decisions.

## Judge calibration

All **22/22** actual Luna calibration calls matched their expected four-bit vectors:

- Empty, wholly wrong and gold-equivalent answers on each of five datasets: 15/15 endpoint checks passed. Empty/wrong scored 0%; gold scored 100%.
- Dataset 1: isolated paragraph, letter, family and percentage failures each scored 75%, with only the intended check failing.
- Equivalent prose scored 100%; a fabricated FDA source claim failed the explanation/percentages check and scored 75%.
- A repeated Dataset 1 gold judgment again scored 100%, with identical decisions.

Calibration expectations and fixture names were not included in judge requests. The frozen rubric explicitly separates an extra contradictory count field from otherwise correct fractions, permitting a single count-check failure without forcing the percentages check to fail. When the fraction itself has a wrong numerator, both checks fail. This convention was fixed before calibration and candidate evaluation; no rubric tuning based on observed scores occurred.

## Observed failures

Nano Dataset 1 had correct paragraph and family counts, but undercounted affected clinical and facility-inspection letters and overcounted nonclinical letters. Dataset 2 had incorrect paragraph and family counts and used incorrect paragraph/letter denominators. Dataset 3 omitted a facility-inspection paragraph, overcounted several families and used incorrect denominator populations. Dataset 4 returned zero denominators and null percentages, as well as incorrect category counts. Dataset 5 failed all four all-or-nothing checks. Complete judge explanations and verbatim answers are retained locally.

The saved-answer CLI was exercised on Nano Dataset 1 with one additional Luna call. It reproduced the original 1/0/1/0 vector and 50% score. Its rationale also identified the nonclinical letter overcount, which the original judge rationale missed (and incorrectly described as correct). Inspection of the saved answer confirmed the overcount. Both judgments correctly failed the overall letter and percentage checks, so the score did not change. Original verdicts are preserved; rationale completeness is a demonstrated judge limitation.

## Reproducibility and artifacts

Requested candidate IDs were `gpt-5-nano` and `gpt-6-luna`. Returned IDs were `gpt-5-nano-2025-08-07` and `gpt-6-luna`; every judge returned `gpt-6-luna`. Model availability was checked before execution. Both candidates received identical per-dataset inputs and instructions, without tools, retrieval, gold or ledgers. Calls used the official OpenAI Responses endpoint, `store=false`, 10,000 output-token limits, Nano minimal reasoning and Luna defaults. The same model family serving as candidate and judge is a limitation, even though calls and contexts are separate.

Private artifacts under this task directory:

- `.private/datasets/`: five inputs, hidden gold files, auditable ledgers and independent verification records.
- `.private/calibration-v1-network/`: all 22 calibration prompts, raw responses, verdicts and summary.
- `.private/matrix-v1/`: ten candidate calls, ten separate judge calls and the five-dataset averages.
- `.private/saved-answer-smoke/`: one additional Luna call through the saved-answer CLI, without candidate regeneration.
- `.private/task3_evaluated_v1.py`: frozen source used for calibration and matrix evaluation. Subsequent CLI improvements added public-input rebuilding and preflight-error recording without changing candidate instructions, judge rubric or reference arithmetic.
- `.private/audit_manifest.json`: hashes and sizes of retained audit artifacts.

Complete request/response JSON, raw output, response IDs, model IDs, usage, timings, hashes and verdict reasons are saved. An initial sandbox DNS failure occurred during model-availability preflight; no candidate or judge calls ran in that attempt. It is recorded separately under `.private/calibration-v1/`; the network-enabled retry completed. Failures are never converted into zero scores or dropped from a supposedly complete average.

See [README.md](README.md) for build, verification, calibration, matrix and one-command saved-answer grading commands. Code, source-free synthetic inputs and this report are publishable. Gold, full logs, local credentials and all restricted source-bearing materials are excluded from Git. The work is isolated to `tasks/task_03_category_distribution/` on `codex/task-3-category-distribution`; shared tasks and historical scores are unchanged.

## Limits

This is a small synthetic aggregation benchmark with one candidate sample per model/dataset. It establishes arithmetic and identity-handling performance under supplied labels, not regulatory expertise or real-corpus prevalence. Gold verification is computational plus a hand-calculated unit fixture, not a second human annotation review. Calibration and the repeated gold call support the tested rubric endpoints; they do not establish general judge reliability. No task-wide pass threshold is defined.
