from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, TypeAdapter

TASKS = ()  # Benchmark reset: register new test cases after gold authoring.
Identifier = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]{1,80}$")]
Phrase = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Claim = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=350)]
Quote = Annotated[str, StringConstraints(strip_whitespace=True, min_length=12, max_length=350)]

class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

class Citation(Strict):
    relative_path: Annotated[str, StringConstraints(min_length=1, max_length=260)]
    page: Annotated[int, Field(ge=1)]
    quote: Quote

class Record(Strict):
    record_id: Identifier
    issue_ref: Phrase
    claim: Claim
    citations: Annotated[list[Citation], Field(min_length=1, max_length=8)]

class Reconciliation(Record):
    category: Literal["bridge", "material", "rheology", "test_panel", "method_validation", "particle_size", "solid_state"]
    pattern: Literal["initial_only", "reiterated"]

class Response(Record):
    response_ref: Identifier
    status: Literal["documented", "partial", "not_reviewed", "not_documented"]

class Resolution(Record):
    status: Literal["documented_resolved", "documented_unresolved", "indeterminate"]
    basis: Literal["fda_acceptance", "fda_reiteration", "fda_rejection", "no_issue_specific_finding", "action_rescinded", "review_pending"]

class Answer(Strict):
    task_version: Literal["1.0"]
    answer_version: Literal["1"]
class ReconciliationAnswer(Answer):
    task_id: Literal["reconciliation"]
    records: Annotated[list[Reconciliation], Field(max_length=40)]
class ResponseAnswer(Answer):
    task_id: Literal["response_mapping"]
    records: Annotated[list[Response], Field(max_length=40)]
class ResolutionAnswer(Answer):
    task_id: Literal["resolution_audit"]
    records: Annotated[list[Resolution], Field(max_length=40)]

class ApprovalDependency(Record):
    role: Literal["approval_dependency", "deferred_review", "conditional_acceptance"]

class InspectionFollowup(Record):
    status: Literal["deferred", "still_incomplete", "distinct_issue", "completed", "indeterminate"]

class ApprovalDependencyAnswer(Answer):
    task_id: Literal["approval_dependency"]
    records: Annotated[list[ApprovalDependency], Field(max_length=40)]

class InspectionFollowupAnswer(Answer):
    task_id: Literal["inspection_followup"]
    records: Annotated[list[InspectionFollowup], Field(max_length=40)]

ADAPTER = TypeAdapter(Annotated[ReconciliationAnswer | ResponseAnswer | ResolutionAnswer | ApprovalDependencyAnswer | InspectionFollowupAnswer, Field(discriminator="task_id")])
MODELS = dict(zip(TASKS, (ReconciliationAnswer, ResponseAnswer, ResolutionAnswer, ApprovalDependencyAnswer, InspectionFollowupAnswer)))
