# Task 2 failure analysis and reproducibility

The five-dataset mean was **95% for GPT-6 Luna and 45% for GPT-5 nano**. These are means of four equally weighted binary checks, not paragraph-level accuracy. The two models received identical source/instruction payloads within each dataset. There was one candidate response per model per dataset, with no regeneration or best-of selection.

Nano overselected routine instructions in Datasets 1 and 3 and explicitly nonblocking recommendations in Dataset 4. Its explanations sometimes recognized nonblocking context while the selection list still included those paragraphs. This suggests difficulty keeping the final selection set aligned with the stated decision rule. In Dataset 2, it omitted an explicit approval prerequisite and reported an incorrect denominator. Dataset 3 also contained an internal mismatch between the selection list length and reported count. Dataset 5 passed all four checks. These descriptions omit source text, gold IDs, and document identities; exact evidence and judge reasoning are retained locally.

Luna's only failed check was evidence in Dataset 3. Its selection set, explanations, and counts were otherwise correct. The judge rejected a quote containing an ellipsis because the candidate instruction requires a short verbatim span. This is a quote-contract failure, not evidence that Luna misunderstood the defect. A policy accepting faithful ellipses might score differently; the rubric was not relaxed after observing the answer. This strictness limits how the 95% result should be interpreted. Equivalent explanation wording is accepted, but quoted evidence has a separate verbatim requirement.

The judge's endpoint calibration passed on every dataset. Twenty-two controlled judgments matched the expected binary vectors. Omission and over-selection controls showed the intended distinct recall/precision behavior; fabricated evidence and count-only errors isolated those checks. Repeated gold and fabricated-evidence judgments agreed. The saved-answer CLI was then exercised on a gold-equivalent answer and returned 100% in an additional separate judge call. Three source-free unit tests cover binary validation, calibration fixture isolation, and withholding incomplete task averages. Structural checks validate all 96 source mappings, every gold record, positive/negative presence, complete selected-section coverage, and five distinct families.

The original runner rejected all five completed Nano responses because the official API reported the alias's dated snapshot, `gpt-5-nano-2025-08-07`, rather than `gpt-5-nano`. The exact dated ID is now explicitly accepted and retained as provenance; no other model was substituted. All five saved responses were recovered and judged without regenerating candidates. Original validator failures and API responses remain local. A network-restricted initial attempt also failed before model processing; automatic approval initially rejected an escalation, then the user explicitly authorized the hosted source/gold processing. These infrastructure events are not model failures or zero scores.

Successful response calls: 5 blinded gold reviews, 22 calibration judgments, 10 candidate generations, 10 separate candidate judgments, and 1 saved-answer grading smoke test. Candidate settings: 12,000 maximum output tokens, JSON-object output; Nano reasoning effort minimal, Luna service default. Review/judge settings: 12,000 maximum output tokens and structured Pydantic output, Luna service default. No temperature override or prior conversation is supplied. All calls use `store=false`. The official model-list endpoint confirmed the requested aliases before the main batches. The returned Luna ID was `gpt-6-luna`.

Private batch identifiers for authorized local reproduction:

- Review: `review-20261114T223547Z-2a72ae`
- Calibration: `calibrate-20261114T223654Z-8a1f3c`
- Original candidates and Luna judgments: `run-20261114T223740Z-49600e`
- Nano recovery and consolidated result index: `nano-saved-recovery`
- Saved-answer grader: `grade-20261114T223942Z-8f2f88`

The public report can be regenerated from those explicit local indexes:

```powershell
python tasks/task2_deficiency_detection/report.py --runs .private/task2/logs/nano-saved-recovery/summary.json --calibration .private/task2/logs/calibrate-20261114T223654Z-8a1f3c/summary.json --review .private/task2/logs/review-20261114T223547Z-2a72ae/summary.json --out tasks/task2_deficiency_detection
```

The independently blinded model review agreed on all labels, but its model family is also used by one candidate and the judge. Correlated errors remain possible. No human expert certification or original-PDF visual verification is claimed. Complete selected sections preserve relevant context, but omitted sections, OCR quality, editorial paragraph grouping, and a small sample restrict generalization. The hidden source snapshots and frozen manifest are the authoritative reproducibility materials, not the public metrics alone.
