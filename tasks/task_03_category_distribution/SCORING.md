# Binary evaluation policy

Version: `binary-v1`. Applies to future evaluations; earlier fractional scores remain historical.

## Requirement and design choice

Raycaster's submission requirements say: **“The grader should give zero credit to an empty or wrong answer and full credit to the verified answer.”** Source: the supplied challenge text and [Raycaster challenge README](../hackathon-2026-11-14-resources/challenges/raycaster/README.md).

To support those required endpoints, Kevin chose a stricter implementation: **each of four criteria is pass (1) or fail (0), with no partial credit within a criterion**. The requirement specifies zero/full-credit behavior; it does not explicitly mandate four binary criteria. That is our adopted design choice, not an additional quotation from the organizers.

## Four equally weighted checks per dataset

| Criterion | Pass (1) | Fail (0) |
| --- | --- | --- |
| Deficiency detection | Every required passage is classified correctly as a deficiency or non-deficiency, with no missing or duplicate passage IDs | Any missed deficiency, false positive, missing decision, or duplicate ID |
| Category assignment | Every passage has the correct complete set of categories; non-deficiencies have none | Any missing or unsupported label, missing decision, or duplicate ID |
| Evidence and explanations | Every decision has a correct explanation supported by the supplied evidence/context; equivalent wording is accepted | Any missing, unsupported, fabricated, or contradictory explanation/reference |
| Distribution accuracy | All required counts, denominators, and percentages agree with verified labels under the counting policy | Any missing or incorrect aggregate; arithmetic consistent with wrong labels does not pass |

Percentages may differ only through ordinary rounding to at least one decimal place (absolute tolerance 0.05 percentage points). Counts and denominators must be exact. Category percentages can exceed 100% in total when labels overlap.

An empty or wholly incorrect answer fails all four checks and receives zero. A complete verified gold-equivalent answer passes all four and receives full credit. A partially correct answer may pass some checks, but each individual check remains strictly binary.

Dataset score = passed checks / 4: **0%, 25%, 50%, 75%, or 100%**. Each criterion has weight 25%. The task score is the equal-weight average across its five dataset scores. These aggregate percentages are not fractional credit within a check. A task-wide pass threshold is not defined.

GPT-6 Luna makes all semantic pass/fail decisions and explains each one. Python validates the binary response format and averages the decisions; it does not perform deterministic semantic grading. Both candidate options remain GPT-5 nano and GPT-6 Luna, with separate Luna judge calls.

If unresolved gold or rubric ambiguity prevents a defensible pass/fail decision, record `needs_review` with no numeric score. API/parse failures also receive no score. Do not silently count these cases as failures or omit them from a supposedly complete task score.

## Validation and historical results

Before claiming compliance, run the actual judge on empty, wholly wrong, and independently verified gold answers and check the required endpoints. Also test single-criterion errors, equivalent paraphrases, fabricated references, and judge consistency. Output-schema tests alone do not demonstrate semantic compliance.

Current gold is still draft and these semantic calibration tests have not been completed. Previous 99.00% / 79.64% task averages used fractional 35/35/15/15 scoring and are **not binary-policy results**. Preserve their raw verdicts. Rejudge saved answers under this new version to obtain binary results; never round or relabel old scores.

## Saved-answer rejudgment completed

All ten saved candidate answers have now been judged under binary-v1 by GPT-6 Luna, without regenerating candidates. Provisional five-dataset averages: Luna 90%, Nano 40%. Dataset 3 requires gold and judge-consistency review. These runs do not replace empty/wrong/verified-gold endpoint calibration. See the private TASK1_RESULTS_BINARY.md report and retained rejudgment logs.
