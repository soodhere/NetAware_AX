"""Configuration-driven Domain ↔ Catalog graph. No runtime planning."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from .model import ConfigStore
from .registry import CatalogRegistry


class KnowledgeGraph:
    def __init__(self, store: ConfigStore, registry: CatalogRegistry) -> None:
        self.store = store
        self.registry = registry
        rows = store.mappings.get("capabilityOperations") or []
        self.cap_ops: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.op_caps: dict[tuple[str, str], list[str]] = defaultdict(list)
        for row in rows:
            cap = str(row["capabilityId"])
            op_id = str(row["operationId"])
            source = str(row["source"])
            self.cap_ops[cap].append(row)
            self.op_caps[(op_id, source)].append(cap)

        self.intent_caps: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.cap_intents: dict[str, list[str]] = defaultdict(list)
        for row in store.mappings.get("intentCapabilities") or []:
            intent_id = str(row["intentId"])
            cap = str(row["capabilityId"])
            self.intent_caps[intent_id].append(row)
            self.cap_intents[cap].append(intent_id)

        self.use_case_intents: dict[str, list[str]] = defaultdict(list)
        self.intent_use_case: dict[str, str] = {}
        for row in store.mappings.get("useCaseIntents") or []:
            uc = str(row["useCaseId"])
            intent_id = str(row["intentId"])
            self.use_case_intents[uc].append(intent_id)
            self.intent_use_case[intent_id] = uc

        self.domain_use_cases: dict[str, list[str]] = defaultdict(list)
        self.use_case_domain: dict[str, str] = {}
        for row in store.mappings.get("domainUseCases") or []:
            domain_id = str(row["domainId"])
            uc = str(row["useCaseId"])
            self.domain_use_cases[domain_id].append(uc)
            self.use_case_domain[uc] = domain_id

    def operation_public(self, operation_id: str, source: str) -> dict[str, Any] | None:
        op = self.registry.canonical(operation_id, source)
        return op.to_public() if op else None

    def forward_intent(self, intent_id: str) -> dict[str, Any]:
        intent = self.store.intent_by_id.get(intent_id)
        if not intent:
            return {}
        uc_id = self.intent_use_case.get(intent_id)
        use_case = self.store.use_case_by_id.get(uc_id or "")
        domain_id = self.use_case_domain.get(uc_id or "")
        domain = self.store.domain_by_id.get(domain_id or "")
        capabilities = []
        for link in self.intent_caps.get(intent_id, []):
            cap_id = str(link["capabilityId"])
            cap = self.store.capability_by_id.get(cap_id) or {"id": cap_id}
            operations = []
            for op_link in self.cap_ops.get(cap_id, []):
                rec = self.operation_public(str(op_link["operationId"]), str(op_link["source"]))
                operations.append(
                    {
                        "operationId": op_link["operationId"],
                        "source": op_link["source"],
                        "evidence": op_link.get("evidence"),
                        "catalog": rec,
                    }
                )
            capabilities.append(
                {
                    "capability": cap,
                    "evidence": link.get("evidence"),
                    "role": link.get("role"),
                    "operations": operations,
                }
            )
        return {
            "intent": intent,
            "useCase": use_case,
            "domain": domain,
            "capabilities": capabilities,
        }

    def reverse_operation(self, operation_id: str) -> dict[str, Any]:
        variants = [op.to_public() for op in self.registry.all_for_operation_id(operation_id)]
        cap_ids: list[str] = []
        for op in self.registry.all_for_operation_id(operation_id):
            cap_ids.extend(self.op_caps.get((operation_id, op.source), []))
        cap_ids = list(dict.fromkeys(cap_ids))
        capabilities = []
        intent_ids: list[str] = []
        for cap_id in cap_ids:
            intent_ids.extend(self.cap_intents.get(cap_id, []))
            capabilities.append(self.store.capability_by_id.get(cap_id))
        intent_ids = list(dict.fromkeys(intent_ids))
        intents = []
        use_cases = []
        domains = []
        seen_uc: set[str] = set()
        seen_dom: set[str] = set()
        for intent_id in intent_ids:
            intents.append(self.store.intent_by_id.get(intent_id))
            uc_id = self.intent_use_case.get(intent_id)
            if uc_id and uc_id not in seen_uc:
                seen_uc.add(uc_id)
                use_cases.append(self.store.use_case_by_id.get(uc_id))
                domain_id = self.use_case_domain.get(uc_id)
                if domain_id and domain_id not in seen_dom:
                    seen_dom.add(domain_id)
                    domains.append(self.store.domain_by_id.get(domain_id))
        return {
            "operationId": operation_id,
            "catalogVariants": variants,
            "capabilities": [c for c in capabilities if c],
            "intents": [i for i in intents if i],
            "useCases": [u for u in use_cases if u],
            "domains": [d for d in domains if d],
        }

    def forward_domain(self, domain_id: str) -> dict[str, Any]:
        domain = self.store.domain_by_id.get(domain_id)
        use_cases = []
        for uc_id in self.domain_use_cases.get(domain_id, []):
            intents = [self.forward_intent(i) for i in self.use_case_intents.get(uc_id, [])]
            use_cases.append({"useCase": self.store.use_case_by_id.get(uc_id), "intents": intents})
        return {"domain": domain, "useCases": use_cases}

    def forward_use_case(self, use_case_id: str) -> dict[str, Any]:
        use_case = self.store.use_case_by_id.get(use_case_id)
        if not use_case:
            return {}
        domain_id = self.use_case_domain.get(use_case_id)
        domain = self.store.domain_by_id.get(domain_id or "")
        intents = [self.forward_intent(i) for i in self.use_case_intents.get(use_case_id, [])]
        return {"useCase": use_case, "domain": domain, "intents": intents}

    def reverse_capability(self, capability_id: str) -> dict[str, Any]:
        cap = self.store.capability_by_id.get(capability_id)
        if not cap:
            return {}
        operations = []
        for row in self.cap_ops.get(capability_id, []):
            operations.append(
                {
                    **row,
                    "catalog": self.operation_public(str(row["operationId"]), str(row["source"])),
                }
            )
        intent_ids = list(dict.fromkeys(self.cap_intents.get(capability_id, [])))
        intents = []
        use_cases = []
        domains = []
        seen_uc: set[str] = set()
        seen_dom: set[str] = set()
        for intent_id in intent_ids:
            intents.append(self.store.intent_by_id.get(intent_id))
            uc_id = self.intent_use_case.get(intent_id)
            if uc_id and uc_id not in seen_uc:
                seen_uc.add(uc_id)
                use_cases.append(self.store.use_case_by_id.get(uc_id))
                domain_id = self.use_case_domain.get(uc_id)
                if domain_id and domain_id not in seen_dom:
                    seen_dom.add(domain_id)
                    domains.append(self.store.domain_by_id.get(domain_id))
        families = [
            fam
            for fam in self.registry.families
            if capability_id in (fam.get("capabilities") or [])
        ]
        return {
            "capability": cap,
            "operations": operations,
            "intents": [i for i in intents if i],
            "useCases": [u for u in use_cases if u],
            "domains": [d for d in domains if d],
            "catalogFamilies": families,
        }

    def reverse_api(self, api_id: str) -> dict[str, Any]:
        api = next((a for a in self.registry.apis if a.get("id") == api_id), None)
        if not api:
            return {}
        ops = [op.to_public() for op in self.registry.operations if op.api_id == api_id]
        cap_ids: list[str] = list(api.get("capabilities") or [])
        for op in self.registry.operations:
            if op.api_id != api_id:
                continue
            cap_ids.extend(self.op_caps.get((op.operation_id, op.source), []))
        cap_ids = list(dict.fromkeys(cap_ids))
        intent_ids: list[str] = []
        for cap_id in cap_ids:
            intent_ids.extend(self.cap_intents.get(cap_id, []))
        intent_ids = list(dict.fromkeys(intent_ids))
        use_cases = []
        domains = []
        seen_uc: set[str] = set()
        seen_dom: set[str] = set()
        intents = []
        for intent_id in intent_ids:
            intents.append(self.store.intent_by_id.get(intent_id))
            uc_id = self.intent_use_case.get(intent_id)
            if uc_id and uc_id not in seen_uc:
                seen_uc.add(uc_id)
                use_cases.append(self.store.use_case_by_id.get(uc_id))
                domain_id = self.use_case_domain.get(uc_id)
                if domain_id and domain_id not in seen_dom:
                    seen_dom.add(domain_id)
                    domains.append(self.store.domain_by_id.get(domain_id))
        return {
            "api": api,
            "businessStatus": api.get("businessStatus"),
            "specMaturity": [s.get("specMaturity") for s in (api.get("technicalSpecs") or [])],
            "operations": ops,
            "capabilities": [self.store.capability_by_id.get(c) for c in cap_ids if c in self.store.capability_by_id],
            "intents": [i for i in intents if i],
            "useCases": [u for u in use_cases if u],
            "domains": [d for d in domains if d],
        }
