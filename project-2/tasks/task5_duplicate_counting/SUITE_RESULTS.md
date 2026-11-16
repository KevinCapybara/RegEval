# Task 5 — five-dataset Luna evaluation

Updated: 2026-11-14T23:31:02.678537+00:00

Candidate: OpenAI GPT-6 Luna. Judge: separate OpenAI GPT-6 Luna calls. No local model used.

| Dataset | Case | Score |
|---|---|---:|
| 1 | Genuine duplicate plus distinct review cycles | 75% |
| 2 | Same-date Original subnumbers | 100% |
| 3 | Shared package ID, distinct review cycles A | 100% |
| 4 | Shared package ID, distinct review cycles B | 100% |
| 5 | Same-date package, different base applications | 100% |

**Task average: 95%; 5/5 scored.**

All five references passed independent Luna review. 15/15 endpoint checks passed (empty and wholly wrong answers: 0%; reference answers: 100%).

One genuine-duplicate dataset plus four distinct-letter negative controls; positive duplicate diversity remains limited to one pair. Annotations and gold are model-reviewed, not expert-certified.

This run evaluates Luna only. Previous Nano results are historical and do not establish five-dataset Nano coverage.

Public score files contain only aggregate metrics and criterion scores. Source evidence, gold, review records, candidate answers and raw API responses remain in ignored private folders. API calls used store=false.
