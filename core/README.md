# Grader integration

Install one JSON **array** at `.private/<task>/gold.json`. This is a format contract; case values and verification are deferred.

| Property | Type and meaning |
| --- | --- |
| `id` | Unique stable item ID, compatible with record_id in the answer schema |
| `issue` | Canonical issue reference |
| `aliases` | Optional list of equivalent issue references |
| `claims` | List of complete accepted claim strings, preferred wording first |
| `fields` | The exact additional fields for the task: category + pattern; response_ref + status; status + basis; role; or status (inspection follow-up) |
| `anchors` | List of evidence roles; each role is a nonempty list of alternatives; each alternative is [workspace PDF filename, one-based page, contiguous phrase] |

The task's response key is (issue, response_ref); for other tasks it's issue. Anchor phrases should identify the claim, not just a filename or boilerplate. The grader compares whole normalized claims against accepted wording and does not score isolated keywords as a claim. Gold authors should align the instructions with this constraint (e.g. a shuffled controlled claim bank once the reference is frozen) or populate verified variants. The output contract is available with `python regeval.py schema TASK_ID`. Evaluation weights are in [grader.py](grader.py).

Keep gold outside the workspace. Run `python regeval.py verify-gold TASK_ID` before scoring. Have a domain reviewer confirm the claim inventory, exceptions, and a second source check before freezing a case.
