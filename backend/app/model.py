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
        providers_doc = _load_yaml("providers.yaml")
        self.providers = providers_doc["providers"]
        self.provider_capabilities = providers_doc.get("providerCapabilities") or []
        self.routes = _load_yaml("routes.yaml")["routes"]
        self.mappings = _load_yaml("mappings.yaml")
        self.placeholders = _load_yaml("execution-placeholders.yaml")
        self.demo = _load_yaml("demo-briefings.yaml")

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

    @staticmethod
    def model_files() -> list[Path]:
        return sorted(MODEL_DIR.glob("*.yaml"))
