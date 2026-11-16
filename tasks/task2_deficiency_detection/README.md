# Task 2: deficiency-paragraph detection

Identify every numbered paragraph that states an approval-blocking deficiency in complete supplied letter sections. This is paragraph retrieval, not Task 1 category classification. Five distinct application families contribute 96 numbered logical paragraphs. Complete sections contain positive and negative material; this is not a selection of isolated task-relevant excerpts. Original repeated numbering is replaced by unique benchmark IDs.

The private workspace has five `datasets/dataset_XX/` folders. Each contains agent-facing `workspace.json` and readable `letter.md`, hidden `gold.json`, exact `source_record.json`, and `sections.json`. Gold labels every paragraph and records inclusion/exclusion reasons, archive-member references, source SHA-256, and zero-based character offsets into the source record's text. `spec.json` retains the manual boundaries and annotations. Source text, family identities, gold, and transcripts stay local. Public code cannot recreate the restricted datasets without the authorized private pack and specification.

Only whitespace is reflowed. OCR artifacts, page furniture, and visible redactions are retained; nothing concealed is reconstructed. The unreadable section in one letter is explicitly outside the dataset, not a negative label. Some numbered source items include nested bullets/remediation; these remain one logical unit. Separately segmented required remedies count as separate paragraphs, even if they address the same defect. Coverage refers only to supplied paragraphs. Section selection and these grouping choices limit generalization to other letters. PDF visual verification and human regulatory expert review have not been performed.

Install dependencies with `python -m pip install -r tasks/task2_deficiency_detection/requirements.txt`. Set `OPENAI_API_KEY` locally or use `--env-file` pointing to a local credential file. Calls use the official OpenAI endpoint and `store=false`; provider retention controls are separate from this flag. Use hosted processing only with source-owner/user authorization. The user expressly authorized this task's source and gold processing on November 14, 2026.

From the repository root, grade a saved answer with one command:

```powershell
python tasks/task2_deficiency_detection/evaluate.py grade --private-root .private/task2 --dataset dataset_01 --answer C:/private/saved-answer.json
```

The answer contract is in [instruction.md](instruction.md). A fresh, separate GPT-6 Luna call grades every answer, including Luna-generated answers. No deterministic semantic grading is used. Each command prints its private log folder and machine-readable outcomes. Empty files are treated as empty answers. Nonempty invalid JSON, API failures, and incomplete responses produce no numeric score. Existing files are never overwritten by a new evaluation batch.

```powershell
python tasks/task2_deficiency_detection/build.py --spec .private/task2/spec.json --out .private/task2/datasets
python tasks/task2_deficiency_detection/validate.py --private-root .private/task2
python tasks/task2_deficiency_detection/evaluate.py review --private-root .private/task2
python tasks/task2_deficiency_detection/evaluate.py calibrate --private-root .private/task2
python tasks/task2_deficiency_detection/evaluate.py run --private-root .private/task2
python tasks/task2_deficiency_detection/test_contract.py
```

Review is a blinded Luna annotation with no draft gold in its input. Compare every decision and adjudicate disagreements before freezing gold. Calibration runs empty, wholly wrong, and gold-equivalent answers for each dataset, plus omission, false positive, fabricated evidence, count-only error, paraphrase/reordering, and repeated calls on Dataset 1. Evidence and count errors isolate single checks. Recall/precision errors can inherently affect evidence or the required true count too; the checks are equally weighted, not statistically independent.

[rubric.md](rubric.md) implements the four requested checks using the shared `SCORING.md` binary-v1 policy as read on November 14, 2026. Shared files and Task 1 remain untouched. Every check is 0/1; score is their mean. Empty/wholly wrong answers receive zero through an explicit endpoint override. `needs_review` and errors are unscored, and a five-dataset mean is withheld if any result is missing or unscorable. No pass threshold is defined.

Raw requests, responses, response IDs, usage, hashes, judgments, and error details stay in `.private/task2/logs/`. [RESULTS.md](RESULTS.md) is the source-free public report. Only files under this task's code directory are intended for publication; never publish the private datasets or logs through a public PR.
