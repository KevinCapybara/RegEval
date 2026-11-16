# Task 2 results: deficiency-paragraph detection

Experiment date: November 14, 2026. Five distinct application families; 96 numbered logical paragraphs across complete supplied sections. Gold and all source-bearing inputs, responses, reviews, and verdicts remain local. Public dataset aliases intentionally omit source identities and gold IDs.

| Dataset | Paragraphs | GPT-6 Luna | GPT-5 nano |
| --- | ---: | ---: | ---: |
| 1 | 22 | 100% | 25% |
| 2 | 17 | 100% | 50% |
| 3 | 22 | 75% | 25% |
| 4 | 15 | 100% | 25% |
| 5 | 20 | 100% | 100% |
| **Equal-weight mean** | **96** | 95% | 45% |

Every dataset uses four binary checks worth 25% each: all true deficiency paragraphs found; no non-deficiencies selected; every selection supported by valid evidence; correct count and coverage. GPT-6 Luna judges each answer in a separate request. Python validates and aggregates, without semantic grading. No task-wide pass threshold is defined.

See [ANALYSIS.md](ANALYSIS.md) for concrete failure analysis, quote-contract sensitivity, alias-error recovery, model settings, and reproduction commands.

## Gold review and calibration

Blinded model review completed for 5/5 datasets; 0 disagreements and 0 paragraph ambiguity flags. The reviewer received source and instructions, not draft gold. The author checked source spans and adjudication rules before freezing hashes. This is model-assisted verification, not human expert certification.

Judge calibration: 22/22 expected binary vectors matched. Empty, wholly wrong, and gold-equivalent controls were run on every dataset. Dataset 1 additionally tested omission, false positive, fabricated evidence twice, count-only error, equivalent paraphrase/reordering, and repeated gold.

| Control | Dataset | Expected matched |
| --- | --- | --- |
| empty | dataset_01 | Yes |
| wholly_wrong | dataset_01 | Yes |
| gold_equivalent | dataset_01 | Yes |
| omission | dataset_01 | Yes |
| false_positive | dataset_01 | Yes |
| fabricated_evidence | dataset_01 | Yes |
| fabricated_evidence_repeat | dataset_01 | Yes |
| count_only | dataset_01 | Yes |
| paraphrase_reordered | dataset_01 | Yes |
| gold_repeat | dataset_01 | Yes |
| empty | dataset_02 | Yes |
| wholly_wrong | dataset_02 | Yes |
| gold_equivalent | dataset_02 | Yes |
| empty | dataset_03 | Yes |
| wholly_wrong | dataset_03 | Yes |
| gold_equivalent | dataset_03 | Yes |
| empty | dataset_04 | Yes |
| wholly_wrong | dataset_04 | Yes |
| gold_equivalent | dataset_04 | Yes |
| empty | dataset_05 | Yes |
| wholly_wrong | dataset_05 | Yes |
| gold_equivalent | dataset_05 | Yes |

## Candidate check results

| Dataset | Candidate | Recall | Precision | Evidence | Coverage |
| --- | --- | ---: | ---: | ---: | ---: |
| dataset_01 | gpt-5-nano | 1 | 0 | 0 | 0 |
| dataset_01 | gpt-6-luna | 1 | 1 | 1 | 1 |
| dataset_02 | gpt-5-nano | 0 | 1 | 1 | 0 |
| dataset_02 | gpt-6-luna | 1 | 1 | 1 | 1 |
| dataset_03 | gpt-5-nano | 1 | 0 | 0 | 0 |
| dataset_03 | gpt-6-luna | 1 | 1 | 0 | 1 |
| dataset_04 | gpt-5-nano | 1 | 0 | 0 | 0 |
| dataset_04 | gpt-6-luna | 1 | 1 | 1 | 1 |
| dataset_05 | gpt-5-nano | 1 | 1 | 1 | 1 |
| dataset_05 | gpt-6-luna | 1 | 1 | 1 | 1 |

## Scope and limitations

One candidate run per model per dataset is not a robust model ranking. Repeated judge checks cover only two controlled cases on one dataset; they do not establish general judge reliability. Candidate Luna and judge Luna are separate calls but share a model, creating correlated-error risk. No prior Task 1 answers were reused.

Original repeated numbering and OCR artifacts require an explicit logical-paragraph policy. Required remediation can be a positive when its surrounding section identifies a blocker; generic safety updates and deferred reviews are negative. Explicit nonblocking context overrides defect-like recommendation wording. An unreadable section is omitted, not treated as evidence of no deficiency. No concealed content is reconstructed. PDF visual verification and human regulatory expert review remain outstanding.

Source versions, prompts, response IDs, usage, hashes, and all failures are retained in private logs. store=false was used for hosted requests with explicit user authorization. GitHub receives task-specific code, documentation, tests, and this source-free report only.
