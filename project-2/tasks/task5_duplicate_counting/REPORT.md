# Current five-dataset results

The five-case OpenAI GPT-6 Luna suite is complete: 95% mean, 5/5 scored, 15/15 endpoint calibration checks passed. See [SUITE_RESULTS.md](SUITE_RESULTS.md). It adds four false-merge controls to the genuine-duplicate pilot; it does not establish five independent positive duplicate examples.

The report below describes the historical pilot and its earlier coverage.

---

# Task 5 report: evidence-limited pilot

## Latest targeted rerun — November 14, 2026

The rerun on the available dataset scored Nano 25% (checks: 1/0/0/0) and Luna 100% (checks: 1/1/1/1). Coverage remains 1/5 datasets; there is no five-dataset mean. Full verdicts and artifact paths are recorded in the private latest_evaluation.json and LATEST_EVALUATION.md.

The original evaluation report below is retained as historical context.

**The requested five-dataset task is not complete.** The supplied archive supports one verified duplicate pair in this audit. One real pilot was built and evaluated; four additional datasets were not fabricated or produced by repeating the same duplicate pair. There is no five-dataset task score.

## Evidence and design

The audit read all 458 JSON records (457 contain text) and screened exact/normalized text equality, shared Reference IDs, same-folder/date matches, and eight-word-shingle containment. The archive contains 364 PDFs and 335 record folders, including an unreleased placeholder; folders are not a verified count of application families. The heuristic overlap screen returned 4,155 pairs, mainly because of common boilerplate. Only one pair reached 95% containment and it was the exact duplicate pair. This is a search result, not proof that no undiscovered overlap exists.

Nine priority identity candidates received source review: one duplicate, five shared-Reference-ID pairs that are separate signed actions under a common package ID, and three same-date/folder pairs addressing different Originals or base applications. Shared dates, headings, wording and package identifiers are insufficient merge evidence. The duplicate was independently checked against both PDFs' extracted page text; its signature and the pilot's separate review-cycle signatures were also visually inspected.

The pilot combines the genuine duplicate pair with distinct review-cycle letters from another application. The duplicate's own family has no additional distinct letter represented in the supplied JSON. Thus the pilot does not meet a stricter requirement that duplicate and distinct-cycle examples all occur within one application. Its duplicate has no in-scope labels, so deduplication affects denominators rather than category numerators. These are material coverage limitations.

Fixed, source-supported annotations cover visible findings in five categories. Redacted findings are outside scope; an empty category set does not mean no approval blocker. Hidden gold includes the complete mapping, all pairwise merge/separation evidence, exact union counts and percentages. Independently enumerated arithmetic and a separate Luna source/gold review both passed. Candidate calls never received gold.

## Binary evaluation and calibration

SCORING.md's binary-v1 policy is adapted to the four requested identity/counting checks, each weighted 25%. Luna makes semantic decisions; Python validates binary output and averages. Errors and unresolved ambiguity are unscored.

Ten real Luna calibration calls passed their expected outcomes: empty and wholly wrong 0%; gold, renamed/paraphrased gold and repeated gold 100%; duplicate splitting, distinct merging, missing evidence, fabricated references, and count errors produced the expected individual failed checks. Split/merge perturbations also fail evidence because the mapping contradicts the retained pair decisions. Three local format/failure-handling tests passed; these are separate from semantic calibration.

| Candidate | Group duplicates | Separate distinct | Evidence | Counts | Pilot score |
|---|---:|---:|---:|---:|---:|
| GPT-5 nano | 0 | 1 | 0 | 0 | 25% |
| GPT-6 Luna | 1 | 1 | 1 | 0 | 75% |

Separate Luna calls judged both candidates. Nano contradicted its own duplicate decision in its mapping and returned all-zero category values. Luna's totals, percentages and category vectors were correct, but it omitted the required category-to-count aggregate objects, returning per-letter/per-family vectors instead. Its failed counting check is therefore an output-contract failure, not arithmetic failure. This limits claims that the score measures counting ability alone; a future version should include an explicit schema example and recalibrate.

The saved Nano judge rationale also incorrectly calls a shared Original designation an error. That ancillary statement is not relied on: the mapping/decision contradiction independently establishes the evidence failure. Preserve the raw verdict for auditability.

A summary-generation bug was fixed after the calls; the summary was rebuilt from saved responses without rerunning or replacing any verdict. No task-wide performance claim is made from this small pilot.

## Delivery

The task-local README documents the one-command grader. Code and this sanitized report are publishable; source JSON/PDFs, annotations, hidden gold, audit extracts and raw API logs remain under ignored `private/`. The user explicitly authorized OpenAI API evaluation with `store=false`. No restricted submission route was authorized, so none of these private artifacts was uploaded to GitHub or a submission service. All work is isolated on `codex/task5-duplicate-counting`; shared project files were not changed.
