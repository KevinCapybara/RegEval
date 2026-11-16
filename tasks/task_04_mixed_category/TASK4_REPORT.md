# Task 4 report — November 14, 2026

## Latest targeted rerun — November 14, 2026

A fresh Luna Dataset 3 answer scored 50%, with passing calibration. The latest five-dataset averages are Nano 45% and Luna 90%. The earlier disputed answer remains in the historical record; this rerun does not adjudicate it. Full verdicts and artifact paths are recorded in the private latest_evaluation.json and LATEST_EVALUATION.md.

The original evaluation report below is retained as historical context.

Task 4 tests complete category sets for **already identified deficiency paragraphs**. Five datasets contain 25 genuine source paragraphs: 10 mixed-category cases and 15 single-category controls. Categories are CMC, clinical, nonclinical, labeling, and facility inspection. Every assigned category requires exact evidence. No synthetic combinations of unrelated deficiencies were used.

The datasets emphasize quality characterization versus toxicological qualification, clinical analysis versus concrete labeling requirements, regulatory inspection versus product testing, and clinical context versus an actual clinical deficiency. Each dataset has two mixed passages (40%) and three controls. Some application families recur; these are curated diagnostic sets, not independent samples or corpus prevalence estimates.

## Results

Every candidate was generated separately; every semantic judgment used GPT-6 Luna. The four checks—no omissions, no additions, evidence, and distribution—each carry 25% and are strictly binary across a dataset.

| Dataset | GPT-5 nano | GPT-6 Luna |
|---|---:|---:|
| 1 | 100% | 100% |
| 2 | 0% | 100% |
| 3 | 25% | needs_review |
| 4 | 50% | 100% |
| 5 | 50% | 100% |
| Five-dataset mean | **45%** | **Withheld** |

Nano missed eight supported label assignments and added two unsupported assignments across its five completed answers. Its recurring failure was assigning only one category to mixed passages; it also treated references to labeling as label deficiencies. One answer corrupted a purported exact quote. Several aggregates were internally consistent with the candidate's labels but wrong against the verified sets. A 0% dataset score means all four all-or-nothing checks failed, not that every paragraph was wrong.

Luna omitted an inspection label in Dataset 3, causing incorrect category and multi-label aggregates. Its identical saved answer received 50% and 25% on separate judgments: the judge disagreed about whether a narrow inspection citation was sufficient when another quoted span supplied the required-correction context. Both raw judgments remain private. Dataset 3 is **needs_review with no numeric score**; neither a preferred verdict nor an average of conflicting verdicts was selected. Earlier run-level means are superseded by the consolidated private report.

## Verification and concerns

The actual Luna judge passed **24/24 calibration probes**: empty and wholly wrong answers scored zero and reviewed gold scored 100% on all five datasets; Dataset 1 also tested omissions, additions, evidence fabrication, aggregate errors, equivalent explanations, repeated gold/fabrication judgments, duplicate IDs, and candidate injection. The standalone CLI independently graded the reviewed reference at 100%. Four transport/aggregation tests passed. Passing finite calibration did not prevent the real-answer disagreement above.

Gold has 35 exact per-label citations, checked against source offsets and record hashes. Author review plus separate Luna source audits resolved clinical-synthesis rules and expanded insufficient inspection citations. Targeted PDF inspection identified an OCR-rendered redacted number; that example was replaced before candidate generation. Three other ambiguous alternatives remain excluded with needs_review. All five retained gold sets passed review; no independent human regulatory review occurred, and not every paragraph was visually checked against PDF. Shared reviewer/judge model biases remain a limitation.

All calls used a 9,000-output-token ceiling, no SDK retries, and `store=false`. Nano's first Dataset 3 attempt exhausted that ceiling; a single retry with identical inputs and budget completed. Logs preserve 11 candidate calls, 10 primary judgments, the separate consistency rejudgment, source audits, calibration, and the CLI smoke test. The model requests were `gpt-5-nano` and `gpt-6-luna`; reported IDs, usage, exact requests/responses, versions, and hashes are retained privately.

## Delivery

The [standalone grader and commands](README.md) require the authorized private package. Public Git contains only Task 4 code, rules, and this sanitized report. Source PDFs/JSON, excerpts, hidden gold, selection recipe, review ledgers, and document-bearing logs remain local under `.private/task4/`, consistent with the [source access terms](https://www.raycaster.ai/hackathon). Training/data sharing were confirmed disabled by the user. No shared project files or task registry were edited.
