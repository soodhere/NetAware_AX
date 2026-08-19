"""Load Cadence 0 configuration entities from YAML. No execution engine."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .config import MODEL_DIR

EVIDENCE_GRADES = {"SOURCE_BACKED", "INFERRED", "NEEDS_REVIEW"}


def _load_yaml(name: str) -> Any:
    path = MODEL_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing model file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data


def index_by_id(items: list[dict[str, Any]], key: str = "id") -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in items:
        ident = str(item[key])
        if ident in out:
            raise ValueError(f"Duplicate {key}: {ident}")
        out[ident] = item
    return out


class ConfigStore:
    def __init__(self) -> None:
        self.domains = _load_yaml("domains.yaml")["domains"]
        self.use_cases = _load_yaml("use-cases.yaml")["useCases"]
        self.intents = _load_yaml("intents.yaml")["intents"]
        self.purposes = _load_yaml("purposes.yaml")["purposes"]
        self.capabilities = _load_yaml("capabilities.yaml")["capabilities"]
        self.enterprises = _load_yaml("enterprises.yaml")["enterprises"]
        self.applications = _load_yaml("applications.yaml")["applications"]
        self.agents = _load_yaml("agents.yaml")["agents"]
        self.policies = _load_yaml("policies.yaml")["policies"]
        self.policy_rules = _load_yaml("policies.yaml")["policyRules"]
        self.consent_rules = _load_yaml("policies.yaml")["consentRules"]
        self.agreements = _load_yaml("agreements.yaml")["agreements"]
        self.autonomy_rules = _load_yaml("autonomy-rules.yaml")["autonomyRules"]
        self.subscriptions = _load_yaml("subscriptions.yaml")["subscriptions"]
        self.entitlements = _load_yaml("entitlements.yaml")["entitlements"]
        self.nv_paths = _load_yaml("nv-paths.yaml")
        self.operator_readiness = _load_yaml("operator-readiness.yaml")
        self.discovery = _load_yaml("discovery.yaml")
        self.tmf931 = _load_yaml("tmf931-alignment.yaml")
        self.product_alignment = _load_yaml("product-alignment.yaml")
        self.high_flight_replacement = _load_yaml("high-flight-replacement.yaml")
        self.ota_device_fleet = _load_yaml("ota-device-fleet.yaml")
        from .intent_profile import load_intent_profiles

        self.intent_profiles = load_intent_profiles()
        providers_doc = _load_yaml("providers.yaml")
        self.providers = providers_doc["providers"]
        self.provider_capabilities = providers_doc.get("providerCapabilities") or []
        self.routes = _load_yaml("routes.yaml")["routes"]
        self.mappings = _load_yaml("mappings.yaml")
        self.placeholders = _load_yaml("execution-placeholders.yaml")
        self.demo = _load_yaml("demo-briefings.yaml")
        self.sales_portfolio = _load_yaml("sales-portfolio.yaml")
        self.fulfillment_coverage = _load_yaml("fulfillment-coverage.yaml")
        self.demand_map = _load_yaml("demand-map.yaml")
        self.stakeholder_entry = _load_yaml("stakeholder-entry.yaml")
        self.meeting_mode = _load_yaml("meeting-mode.yaml")

        self.domain_by_id = index_by_id(self.domains)
        self.use_case_by_id = index_by_id(self.use_cases)
        self.intent_by_id = index_by_id(self.intents)
        self.purpose_by_id = index_by_id(self.purposes)
        self.capability_by_id = index_by_id(self.capabilities)
        self.enterprise_by_id = index_by_id(self.enterprises)
        self.application_by_id = index_by_id(self.applications)
        self.agent_by_id = index_by_id(self.agents)
        self.policy_by_id = index_by_id(self.policies)
        self.provider_by_id = index_by_id(self.providers)
        self.entitlement_by_id = index_by_id(self.entitlements)
        self.intent_profile_by_id = index_by_id(self.intent_profiles, key="intentId")

    def is_subscribed(self, enterprise_id: str, capability_id: str, family: str | None) -> bool:
        for sub in self.subscriptions:
            if sub.get("enterpriseId") != enterprise_id or sub.get("status") != "active":
                continue
            if sub.get("capabilityId") == capability_id:
                return True
            if family and sub.get("capabilityFamily") == family:
                return True
        return False

    def is_entitled(
        self,
        *,
        enterprise_id: str,
        application_id: str | None,
        agent_id: str | None,
        capability_id: str,
        family: str | None,
    ) -> bool:
        """Entitlement is application/agent grant. It is not implied by subscription alone."""
        for ent in self.entitlements:
            if ent.get("status") != "active":
                continue
            if ent.get("enterpriseId") and ent.get("enterpriseId") != enterprise_id:
                continue
            if application_id and ent.get("applicationId") and ent.get("applicationId") != application_id:
                continue
            if agent_id and ent.get("agentId") and ent.get("agentId") != agent_id:
                continue
            if ent.get("capabilityId") == capability_id:
                return True
            if family and ent.get("capabilityFamily") == family:
                return True
        return False

    @staticmethod
    def model_files() -> list[Path]:
        return sorted(MODEL_DIR.glob("*.yaml"))
