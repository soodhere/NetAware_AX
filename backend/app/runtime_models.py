"""Canonical execution-trace models. Shared by all Cadence 2+ views."""

from __future__ import annotations



from dataclasses import asdict, dataclass, field

from typing import Any





def public(obj: Any) -> Any:

    if hasattr(obj, "to_public"):

        return obj.to_public()

    if isinstance(obj, list):

        return [public(x) for x in obj]

    if isinstance(obj, dict):

        return {k: public(v) for k, v in obj.items()}

    return obj





@dataclass

class PlanStep:

    n: int

    action: str

    capabilityId: str | None = None

    operationId: str | None = None

    apiKind: str | None = None

    state: str = "PLANNED"

    change: str | None = None



    def to_public(self) -> dict[str, Any]:

        return asdict(self)





@dataclass

class Plan:

    id: str

    intentId: str

    executionId: str

    steps: list[PlanStep] = field(default_factory=list)

    version: int = 1

    label: str = ""

    note: str = "Derived from configured mappings and deterministic scenario rules."

    supersedes: str | None = None



    def to_public(self) -> dict[str, Any]:

        return {

            "id": self.id,

            "intentId": self.intentId,

            "executionId": self.executionId,

            "version": self.version,

            "label": self.label,

            "note": self.note,

            "supersedes": self.supersedes,

            "steps": [s.to_public() for s in self.steps],

        }





@dataclass

class Decision:

    id: str

    capabilityId: str | None

    familyId: str | None

    operationId: str | None

    label: str

    relevant: bool

    availability: str

    policyResult: str

    state: str

    why: str

    stage: str



    def to_public(self) -> dict[str, Any]:

        return asdict(self)





@dataclass

class Invocation:

    id: str

    operationId: str

    source: str

    familyId: str

    familyLabel: str

    specMaturity: str

    businessStatus: str

    method: str

    providerId: str

    providerLabel: str

    routeType: str

    correlationId: str

    latencyMs: int

    httpStatus: int

    raw: dict[str, Any]

    state: str = "INVOKED"

    apiKind: str = "NETWORK"

    simulated: bool = False

    aggregatorLabel: str = ""

    owner: str = ""

    routeDisplay: str = ""



    def to_public(self) -> dict[str, Any]:

        return asdict(self)





@dataclass

class Evidence:

    id: str

    operationId: str

    type: str

    status: str

    payload: dict[str, Any]

    purposeId: str

    reuseEligible: bool = True

    apiKind: str = "NETWORK"

    reused: bool = False

    sourceExecutionId: str | None = None

    sourceTraceId: str | None = None

    ageSeconds: int | None = None

    reuseAudit: dict[str, Any] | None = None



    def to_public(self) -> dict[str, Any]:

        return asdict(self)





@dataclass

class PolicyEvaluation:

    id: str

    stage: str

    subject: str

    result: str

    source: str

    detail: str

    configured: bool = True



    def to_public(self) -> dict[str, Any]:

        return asdict(self)





@dataclass

class Outcome:

    outcome: str

    confidence: float

    recommendedAction: str

    decisionOwner: str

    reasonCodes: list[str]

    summary: str

    networkTrust: str = ""

    approvalRequired: bool = False

    limitingFactor: str = ""

    networkConstraint: bool = False

    objective: str = ""

    sloMs: int = 0

    networkAction: str = ""

    autonomousAction: bool = False

    verification: str = ""

    dataUsed: str = ""

    broaderKycUsed: bool = False

    ageThreshold: int = 0

    ageVerified: bool = False



    def to_public(self) -> dict[str, Any]:

        return asdict(self)





@dataclass

class Beat:

    n: int

    tMs: int

    lane: str

    stage: str

    title: str

    detail: str

    actor: str



    def to_public(self) -> dict[str, Any]:

        return asdict(self)





@dataclass

class ExecutionTrace:

    executionId: str

    traceId: str

    correlationId: str

    intentId: str

    status: str

    request: dict[str, Any]

    knownFromConfiguration: dict[str, Any]

    purpose: dict[str, Any]

    actor: dict[str, Any]

    telcoFinder: dict[str, Any]

    apiFinder: dict[str, Any]

    route: dict[str, Any]

    plan: Plan

    decisions: list[Decision]

    invocations: list[Invocation]

    evidence: list[Evidence]

    policyEvaluations: list[PolicyEvaluation]

    autonomy: dict[str, Any]

    outcome: Outcome

    economy: dict[str, Any]

    beats: list[Beat]

    honesty: dict[str, Any]

    executable: bool = True

    planHistory: list[Plan] = field(default_factory=list)

    replan: dict[str, Any] | None = None

    routes: list[dict[str, Any]] = field(default_factory=list)

    conditionChange: dict[str, Any] | None = None

    verificationResult: dict[str, Any] | None = None



    def to_public(self) -> dict[str, Any]:

        body: dict[str, Any] = {

            "executionId": self.executionId,

            "traceId": self.traceId,

            "correlationId": self.correlationId,

            "intentId": self.intentId,

            "status": self.status,

            "request": self.request,

            "knownFromConfiguration": self.knownFromConfiguration,

            "purpose": self.purpose,

            "actor": self.actor,

            "telcoFinder": self.telcoFinder,

            "apiFinder": self.apiFinder,

            "route": self.route,

            "plan": self.plan.to_public(),

            "decisions": [d.to_public() for d in self.decisions],

            "invocations": [i.to_public() for i in self.invocations],

            "evidence": [e.to_public() for e in self.evidence],

            "policyEvaluations": [p.to_public() for p in self.policyEvaluations],

            "autonomy": self.autonomy,

            "outcome": self.outcome.to_public(),

            "economy": self.economy,

            "beats": [b.to_public() for b in self.beats],

            "honesty": self.honesty,

            "executable": self.executable,

            "views": {

                "overview": True,

                "liveFlow": True,

                "decisions": True,

                "apis": True,

                "policy": True,

                "discovery": True,

                "derivedFrom": self.executionId,

            },

        }

        if self.planHistory:

            body["planHistory"] = [p.to_public() for p in self.planHistory]

        if self.replan:

            body["replan"] = self.replan

        if self.routes:

            body["routes"] = self.routes

        if self.conditionChange:

            body["conditionChange"] = self.conditionChange

        if self.verificationResult:

            body["verificationResult"] = self.verificationResult

        return body

