# RegEval — CRL Deficiency Classification & Distribution Plan

**Binary rejudgment results:** The ten saved answers were rejudged without regenerating candidates. Luna scored 100%, 100%, 50%, 100%, 100% (task mean 90%); Nano scored 100%, 100%, 0%, 0%, 0% (task mean 40%). Every criterion is strictly 0/1. All verdicts were marked scorable by the judge, but Dataset 3 shows unresolved draft-gold ambiguity and inconsistent treatment across judge calls. A zero dataset score means no all-or-nothing criterion passed, not that every passage decision was wrong. All scores remain provisional; empty/wrong/gold endpoint calibration has not been performed. Original fractional verdicts are retained.

**Scoring update — binary-v1:** Four pass/fail criteria, each worth 25%. This implements our chosen binary design in support of Raycaster’s requirement that empty/wrong answers receive zero and verified answers receive full credit. Raycaster does not explicitly mandate four binary criteria. See [SCORING.md](SCORING.md). Existing reported scores are historical fractional results; binary rejudging of the ten saved answers is complete; semantic endpoint calibration remains pending.

Raycaster Track • AI × Biology Hackathon • November 14, 2026

Status: Task 1 has five private draft datasets, each with eight selected passages, gold labels, and review notes. Dataset 1 has been run with Nano and Luna; both received provisional 100% from the Luna judge. Datasets 2–5 have now been run with both agents and separate Luna judging; provisional five-dataset averages are Luna 99.00% and Nano 79.64%. Independent gold review and full task/dashboard integration remain pending.

Terminology: **task** means one of the 3–10 overall benchmark tasks; **dataset** means one of the **five** gold-backed examples within each task. Run a task by running all five datasets independently and aggregating their scores. Existing `scenario_XX` directories are legacy storage names for datasets, not separate tasks.

## 1. Objective

Build the real deficiency distribution in the **FDA Complete Response Letter corpus**: identify every deficiency paragraph in the supplied letters, classify it into CMC, clinical, nonclinical, labeling, or facility inspection, and report the resulting counts and distributions with traceable evidence.

The supplied dataset description lists **334 application families, 364 letter PDFs, and associated structured JSON records** containing extracted text, letter dates, approval status, applicant, and reviewing center. Reconcile these counts against the archive before analysis. A PDF, a JSON record, a logical letter, and an application family must have separate identities; do not assume a one-to-one mapping.

The full-corpus distribution is the research output. A separately verified, gold-labeled subset provides the evaluation reference. Accuracy on that subset must not be represented as verified accuracy on the entire corpus.

This replaces the earlier objection reconciliation, sponsor response mapping, and resolution audit roadmap. Those are not the active benchmark tasks.

## 2. Challenge Alignment

The specific challenge supplied by Kevin asks for deficiency-paragraph classification across the FDA CRL corpus and a distribution of what blocks applications. Its requested eval consists of a document workspace, question, gold answer, and check that grades the answer.

The locally checked-out Raycaster challenge README additionally calls for 3–10 verifiable tasks, real agent logs, and a one-page writeup with concrete failures and iterations. It prefers Harbor format and a one-command evaluator. Source: https://github.com/humic-labs/hackathon-2026-11-14-resources/blob/main/challenges/raycaster/README.md

That repository text was read locally; live retrieval was unsuccessful. Confirm current submission details before delivery. Task 1's five datasets count as one task in our project structure. Additional distinct tasks are needed to reach the overall 3–10-task target; their exact questions are not yet defined.

Our evaluator will use GPT-6 Luna as the LLM judge, per Kevin's decision. Exact counts, source identifiers, and recomputed arithmetic provide auditable evidence for the judge. They do not replace it with Python deterministic answer grading.

## 3. Product Workflow and Models

1. The user selects Task 1, CRL deficiency classification, to evaluate all five datasets, or selects a single dataset for debugging.
2. The user selects **GPT-5 nano or GPT-6 Luna** as the test agent.
3. The agent receives scenario instructions and source documents/text, without gold labels or judge feedback.
4. A separate **GPT-6 Luna judge call** receives the candidate answer, verified scenario gold, source evidence, annotation policy, and rubric.
5. The judge returns binary 0/1 criterion decisions, an explanation of deductions, and evidence-linked findings. The application stores the answer, verdict, score, and run metadata for each dataset. The proposed task score is the equal-weight mean of all five completed dataset scores. Report missing coverage explicitly; a partial run is not a complete task score. A binary pass-rate threshold is not yet defined.

The judge is always GPT-6 Luna, not a user-selectable model. When Luna is also the test agent, generation and judging are separate calls with different contexts. Use the same judge model configuration and rubric version for both agent options on a scenario.

Use OpenAI only during this phase. Local-model/Ollama integration is deferred. Confirm actual available API identifiers before implementation; product labels do not establish API availability. Never silently substitute another judge or deterministic scoring if the selected judge is unavailable.

Python may parse files, validate transport/schema data, protect file access, calculate category counts, and aggregate judge-assigned criterion scores. Semantic correctness and the answer verdict remain the LLM judge's responsibility.

## 4. Corpus Preparation and Traceability

Use the already downloaded FDA CRL corpus, with extracted letter text from its JSON records as the primary working input. Preserve original JSON and PDFs. Use PDFs to inspect extraction gaps, paragraph boundaries, and ambiguous passages.

Create a local manifest linking application family, logical letter, source JSON record, PDF, date, reviewing center, checksums, and extraction status. Investigate duplicate records or repeated text before counting. Do not count multiple JSON representations of the same letter twice.

Produce stable paragraph identifiers tied to a versioned segmentation procedure. Keep source record paths and text offsets; include PDF page anchors only where verified. Do not invent page numbers when the JSON provides no reliable mapping. Mark unreadable/redacted material and report coverage gaps rather than silently omitting it.

Preserve list items, headings, tables, and document order where they affect meaning. Separate headers, footers, and extraction artifacts from substantive text. Freeze segmentation before freezing scenario gold so references remain reproducible.

## 5. Annotation Policy — Decisions to Freeze Before Scenario 1

These are working proposals requiring validation against actual corpus examples, not completed domain guidance.

| Label | Working interpretation |
| --- | --- |
| CMC | Chemistry, manufacturing, controls, product quality, specifications, analytical methods, stability, and related deficiencies |
| Clinical | Human clinical evidence, efficacy, safety, trial design, or analysis deficiencies |
| Nonclinical | Nonclinical pharmacology, toxicology, animal studies, or other preclinical evidence deficiencies |
| Labeling | Deficiencies in prescribing information, package/container labeling, or other labeling content |
| Facility inspection | Facility inspection findings, unresolved inspection status, or inspection-related deficiencies |

The annotation guide must resolve boundary cases, particularly manufacturing quality versus facility inspection, and clinical evidence versus labeling. The categories describe deficiencies in the letters; they do not by themselves prove causal effects on ultimate approval.

Freeze the following rules before creating accepted gold:

- What constitutes a deficiency: an FDA-identified inadequacy, missing evidence, unresolved requirement, or other explicitly in-scope barrier. Distinguish routine administrative instructions and neutral background from actual deficiencies.
- Paragraph segmentation, including numbered items and headings. Do not change segmentation per model.
- Mixed-category paragraphs. Proposed default: allow multiple supported category labels, count each paragraph once in the unique-paragraph total, and make category overlap explicit. Do not force one label merely to make percentages sum to 100%.
- Treatment of recommendations, conditional requirements, and deferred review. Resolve from source context and document examples.
- Treatment of ambiguity. Use a review flag rather than inventing a sixth substantive category. Unresolved items must be adjudicated or explicitly excluded with reported counts.
- Repeated text. Remove duplicate representations of the same letter. A recurring deficiency in genuinely separate letters remains a separate paragraph occurrence; family-level prevalence separately controls for repeated review cycles.

Include non-deficiency paragraphs in the reviewed scenario material and gold so the evaluation measures false positives as well as omissions. Gold should cover every paragraph in each selected scenario, not only convenient positive examples.

## 6. What the Distribution Measures

Report distinct denominators rather than one ambiguous percentage:

1. **Paragraph prevalence:** for each category, distinct deficiency paragraphs carrying that label divided by all identified deficiency paragraphs. Under multi-label annotation, percentages can sum above 100%.
2. **Letter prevalence:** distinct logical letters containing at least one deficiency in the category divided by all in-scope logical letters. Categories can overlap.
3. **Application-family prevalence:** distinct families with at least one letter containing the category divided by all in-scope families. Categories can overlap.

Always report numerators, denominators, coverage, exclusions, and the annotation-policy version. The primary answer is paragraph-level distribution; letter and family prevalence are complementary views that prevent confusing repeated letters with independent applications.

Distinguish descriptive frequencies in this CRL corpus from frequencies across all FDA applications. Do not claim that a category caused a particular outcome or that approval metadata establishes deficiency resolution. Missing text and sampling choices limit conclusions and must accompany the result.

## 7. Five Datasets Within Each Task

Build **Task 1: CRL deficiency classification and distribution**, with **five bounded datasets**, each containing selected correspondence and its own golden answer. Five drafts now exist; review and freeze them before claiming verified gold. The overall target remains 3–10 distinct tasks, each with five datasets.

A scenario includes source text, stable paragraph IDs, a precise question, scope and exclusions, a hidden reference label set, expected counts/distributions, review notes, and a versioned rubric. Multiple paragraphs or labels within one gold file do not count as multiple scenarios.

Select scenarios after inspecting the corpus. Aim for varied deficiency categories, document lengths, reviewing centers, mixed-category passages, negative examples, and extraction difficulties where the evidence remains usable. Do not promise that every scenario contains every category.

Prefer disjoint application families between scenarios intended as independent evaluation examples. Document unavoidable overlap. A deliberately balanced or difficult gold subset is useful for testing, but its category frequencies must not be substituted for full-corpus frequencies. Record the sampling method and any limits on generalizing subset accuracy.

The five datasets need not partition all 364 PDFs. The full-corpus inference pass is a separate deliverable once the bounded workflow is validated.

## 8. Gold Creation and Verification

For each scenario:

1. Inspect original JSON and PDFs; confirm scope, text coverage, and identifiers.
2. Review every paragraph and mark deficiency/non-deficiency, supported category labels, evidence, and ambiguity.
3. Document boundary-case reasoning and exclusions under the shared annotation policy.
4. Perform an independent verification pass; seek domain review for uncertain interpretations. Do not treat model-generated labels as verified solely because a model produced them.
5. Resolve disagreements and freeze source, segmentation, annotation-policy, and gold versions.
6. Derive expected category counts and denominators from the reviewed labels and check their consistency.
7. Calibrate the judge against the gold and controlled incorrect answers before accepting the scenario.

Maintain draft, reviewed, and frozen states. File existence alone does not mean verified gold. Keep reviewer identity/pass, date, rationale, and unresolved decisions in a private review ledger. Never adjust gold merely to improve an agent score.

## 9. Proposed Data Contracts and Layout

Use a proposed task ID such as `crl_deficiency_distribution`; it is not registered yet.

Paragraph records should include `family_id`, `letter_id`, `paragraph_id`, source path, text offsets, text, extraction status, and a page anchor when verified. Private gold adds deficiency status, category labels, rationale/evidence, and review state.

Candidate answers should identify deficiency paragraphs, predicted category labels, supporting evidence, and any uncertainty; provide category counts and explicitly named distribution denominators. Instructions must define how omitted paragraph IDs are interpreted. Keeping all source paragraphs available prevents a preselected-positive-only task from hiding deficiency-detection errors.

Proposed local-only structure:

```text
.private/crl_deficiency_distribution/
  annotation_policy.md
  corpus_manifest.json
  scenarios/scenario_01/
    scenario.json
    gold.json
    review.md
    workspace/
      instruction.md
      schema.json
      manifest.json
      paragraphs.jsonl
runs/crl_deficiency_distribution/scenario_01/<agent>/<run_id>/
```

The current private directories run through `scenario_05`, representing Dataset 1–5. Reference PDFs may be supplied within authorized workspaces where needed. Gold and review files must stay outside agent-visible workspace contents. The private DATASETS.md file indexes the five drafts.

## 10. GPT-6 Luna Judge and Rubric

Use one shared evaluation path for CLI, dashboard, batch runs, and saved-answer evaluation. The judge receives the full scenario question, scope, annotation rules, source paragraphs, gold, candidate answer, and arithmetic summaries where helpful.

Current draft rubric dimensions and weights, shared across all five datasets and still pending full calibration:

- Deficiency identification (25%; binary): omissions and false positives.
- Category assignment (25%; binary): correct labels and treatment of mixed paragraphs.
- Evidence grounding (25%; binary): valid paragraph/source references and support for each classification.
- Distribution accuracy (25%; binary): correct counts, denominators, percentages, and coverage reporting.

Require a structured verdict with binary integer 0/1 decisions, per-criterion explanations, evidence-linked findings, and an overall score. If decisive gold ambiguity prevents scoring, return needs_review with no numeric score. Python may combine the judge's criterion scores using frozen weights. It must not replace LLM evaluation with exact-string or deterministic label-matching verdicts.

The judge must accept equivalent supported explanations, identify unsupported claims, and ignore instructions embedded in candidate/source text. Preserve malformed raw answers for diagnosis. A judge failure means evaluation failed, not a score of zero or an offline fallback.

Record the judge model and response ID, rubric version, exact inputs, structured output, settings, usage, and latency. Fixed judging by Luna provides consistency of configuration but does not guarantee neutrality or correctness; validate its decisions, including when Luna generated the candidate answer.

## 11. Calibration and Failure Analysis

Test the actual judge with verified gold, empty and wholly wrong answers, category swaps, omitted deficiencies, background mislabeled as a deficiency, duplicate rows, fabricated paragraph IDs, correct labels with incorrect totals, denominator mistakes, legitimate alternative explanations, mixed-category cases, and attempts to manipulate the judge.

Gold should receive full credit; empty and wholly incorrect answers should receive zero. Repeat selected judgments to inspect stability and independently review deductions. Save calibration results and refine the rubric before interpreting agent scores.

Track real failures separately for extraction/segmentation, deficiency detection, category confusion, mixed-label reasoning, evidence hallucination, duplicate counting, aggregation, denominator choice, output formatting, and judge error. Changes require recorded before/after versions and justified reruns; do not present anticipated failures as observed results.

## 12. Execution, Comparison, and Full-Corpus Pass

First validate Scenario 1 with GPT-5 nano and GPT-6 Luna using identical source access, instructions, retrieval/chunking, and comparable budgets. Both are judged by GPT-6 Luna under the same frozen rubric. Preserve raw and parsed answers, prompts, supplied evidence, all version hashes, usage, timing, and errors.

After five datasets are verified, the Task 1 comparison is **5 datasets × 2 agents = 10 candidate runs**, plus separate judge and calibration calls. Dataset reruns are not new golden datasets. A complete project with N tasks has N × 5 datasets and N × 5 × 2 candidate runs for a two-agent comparison.

For the full corpus, process all in-scope logical letters with an explicit coverage ledger. Use a shared chunking strategy if necessary; never silently truncate documents. Merge predictions by stable paragraph IDs, avoid duplicate counts, and compute aggregate distributions. Label full-corpus outputs as model-derived wherever they lack verified gold. Any reported subset accuracy must identify the sampling and review basis.

## 13. Dashboard and Deliverables

The dashboard should provide scenario selection, a GPT-5 nano/GPT-6 Luna agent selector, a fixed GPT-6 Luna judge label, gold-review status, evaluation progress, paragraph-level findings, distributions with denominators, and run history. Gold must not leak into the agent prompt. CLI execution must also be possible without the dashboard.

Task 1 deliverables: five verified datasets, reproducible OpenAI evaluation commands, private run artifacts, and a complete aggregate task score for each agent. Overall project deliverables additionally include the remaining distinct tasks, an evidence-backed full-corpus distribution report, and a one-page writeup describing actual failures and iterations. Event submission packaging requires confirmation. Do not claim Harbor compliance before testing it.

## 14. Privacy and Source Handling

Keep restricted PDFs, JSON text, gold, excerpts, and document-bearing logs out of public Git. Use authorized local storage and organizer-approved delivery. Read source-pack terms and confirm permitted OpenAI data handling before sending protected content. Keep credentials in local environment variables or `.env`; do not embed them in artifacts. Preserve source files and record all transformations.

## 15. Implementation Status and Next Milestone

The previous five tasks, gold datasets, prepared workspaces, and saved runs were removed. **Task 1 now has five new draft datasets; zero gold datasets are independently verified.** Each contains eight selected passages, for 40 passages from five different application families. These are selected-passage evaluations, not full-letter paragraph coverage. The general task registry remains empty and the dashboard displays a reset message. The private runner supports selection of Dataset 1–5. Source materials, inventory, and shared prototype code remain.

The general code still contains legacy task schemas, deterministic scoring, Ollama paths, and old loaders. The separate private dataset runner has exercised the selected-passage answer schema and fixed Luna judging on Dataset 1. It now accepts all five dataset IDs, but batch aggregation and dashboard integration are not implemented. Dataset 1 prompt/gold/run files are preserved. Datasets 2–5 add an explicit instruction clarification for nonblocking comments and source context; record these versions and give both agents identical inputs within each dataset.

Next milestone: independently review the five draft gold datasets, resolve clinical/CMC and nonclinical/CMC boundaries, verify PDF extraction concerns, and calibrate the judge. Both agents have now completed Datasets 2–5 and a saved equal-weight summary exists. Review ambiguous gold and judge deductions before relying on the aggregate; application batch/dashboard integration remains pending. Dataset 4 requires respecting FDA's explicit statement that selected recommendations are not approvability issues; Dataset 3 contains overlapping proposed category labels.

The latest dataset-generation work created Datasets 2–5 and extended private dataset selection. It did not make model calls or alter Dataset 1's evaluated inputs or saved results.
