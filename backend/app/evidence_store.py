"""Canonical evidence store for cross-intent reuse (Cadence 5)."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

SIMULATED_NOW_MS = 1_728_000_000_000
DEFAULT_TTL_SECONDS = 300

PURPOSE_REUSE_MATRIX: dict[str, set[str]] = {
    "identity_continuity_assist": {"payment_fraud_assist", "identity_continuity_assist"},
}


@dataclass
class StoredEvidence:
    id: str
    executionId: str
    traceId: str
    enterpriseId: str
    applicationId: str
    agentId: str
    subjectKey: str
    purposeId: str
    operationId: str
    capabilityId: str
    evidenceType: str
    payload: dict[str, Any]
    createdAtMs: int
    ttlSeconds: int = DEFAULT_TTL_SECONDS
    reuseEligible: bool = True

    def age_seconds(self, now_ms: int = SIMULATED_NOW_MS) -> int:
        return max(0, int((now_ms - self.createdAtMs) / 1000))

    def is_fresh(self, now_ms: int = SIMULATED_NOW_MS) -> bool:
        return self.age_seconds(now_ms) <= self.ttlSeconds

    def to_public(self) -> dict[str, Any]:
        body = asdict(self)
        body["ageSeconds"] = self.age_seconds()
        body["fresh"] = self.is_fresh()
        return body


_STORE: list[StoredEvidence] = []


def reset_store() -> None:
    _STORE.clear()


def subject_key(subject: dict[str, Any], fallback: str | None = None) -> str:
    phone = subject.get("phoneNumber") or subject.get("networkIdentifier")
    if phone:
        return str(phone)
    if subject.get("recoveryId") and fallback:
        return str(fallback)
    return str(subject.get("transactionId") or subject.get("bagId") or subject.get("recoveryId") or "unknown")


def purpose_allows_reuse(source_purpose_id: str, target_purpose_id: str) -> bool:
    if source_purpose_id == target_purpose_id:
        return True
    allowed = PURPOSE_REUSE_MATRIX.get(target_purpose_id) or set()
    return source_purpose_id in allowed


def persist_from_trace(
    trace: Any,
    *,
    enterprise_id: str,
    application_id: str,
    agent_id: str,
    subject: dict[str, Any],
    capability_for_op: dict[str, str],
    created_offset_ms: int = 42_000,
) -> None:
    created_at = SIMULATED_NOW_MS - created_offset_ms
    for ev in trace.evidence:
        if not getattr(ev, "reuseEligible", True):
            continue
        op_id = str(ev.operationId)
        _STORE.append(
            StoredEvidence(
                id=str(ev.id),
                executionId=str(trace.executionId),
                traceId=str(trace.traceId),
                enterpriseId=enterprise_id,
                applicationId=application_id,
                agentId=agent_id,
                subjectKey=subject_key(subject),
                purposeId=str(ev.purposeId),
                operationId=op_id,
                capabilityId=capability_for_op.get(op_id, ""),
                evidenceType=str(ev.type),
                payload=dict(ev.payload),
                createdAtMs=created_at,
                ttlSeconds=DEFAULT_TTL_SECONDS,
                reuseEligible=True,
            )
        )


def find_reusable(
    *,
    enterprise_id: str,
    application_id: str,
    agent_id: str,
    subject: dict[str, Any],
    subject_key_override: str | None,
    operation_id: str,
    capability_id: str,
    target_purpose_id: str,
    policy_allows: bool = True,
) -> tuple[StoredEvidence | None, dict[str, Any]]:
    key = subject_key_override or subject_key(subject)
    audit: dict[str, Any] = {
        "operationId": operation_id,
        "capabilityId": capability_id,
        "subjectKey": key,
        "checks": {},
    }
    candidates = [
        e
        for e in _STORE
        if e.enterpriseId == enterprise_id
        and e.applicationId == application_id
        and e.agentId == agent_id
        and e.subjectKey == key
        and e.operationId == operation_id
        and e.reuseEligible
    ]
    audit["checks"]["found"] = bool(candidates)
    if not candidates:
        audit["decision"] = "INVOKE"
        audit["reason"] = "No matching evidence in store."
        return None, audit

    best = max(candidates, key=lambda e: e.createdAtMs)
    audit["checks"]["sourceExecutionId"] = best.executionId
    audit["checks"]["sourceTraceId"] = best.traceId
    audit["checks"]["ageSeconds"] = best.age_seconds()
    audit["checks"]["ttlSeconds"] = best.ttlSeconds
    audit["checks"]["fresh"] = best.is_fresh()
    audit["checks"]["purposeCompatibility"] = purpose_allows_reuse(best.purposeId, target_purpose_id)
    audit["checks"]["policyPermitsReuse"] = policy_allows
    audit["checks"]["evidenceType"] = best.evidenceType

    if not best.is_fresh():
        audit["decision"] = "INVOKE"
        audit["reason"] = "Evidence expired."
        return None, audit
    if not purpose_allows_reuse(best.purposeId, target_purpose_id):
        audit["decision"] = "INVOKE"
        audit["reason"] = "Purpose not compatible for reuse."
        return None, audit
    if not policy_allows:
        audit["decision"] = "INVOKE"
        audit["reason"] = "Policy does not permit reuse."
        return None, audit

    audit["decision"] = "EVIDENCE_REUSED"
    audit["reason"] = f"Reusing evidence from execution {best.executionId}."
    return best, audit


def list_store() -> list[dict[str, Any]]:
    return [e.to_public() for e in _STORE]
