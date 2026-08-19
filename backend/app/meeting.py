"""Cadence 16 meeting presentation overlay. Not a second runtime."""
from __future__ import annotations

from typing import Any

from .config import APP_VERSION, MODEL_CADENCE, UI_CADENCE, UI_CADENCE_PATCH, serve_frontend
from .model import ConfigStore
from .portfolio import visible_rows
from .registry import CatalogRegistry
from .runtime import EXECUTABLE_INTENTS


CORE_SCENARIOS = (
    "passwordless-mobile-sign-in",
    "high-value-payment-protection",
    "baggage-connection",
    "critical-inspection-camera",
    "fleet-firmware-rollout",
    "pharmacy-age-gate",
)


def public_meet(store: ConfigStore) -> dict[str, Any]:
    doc = dict(store.meeting_mode or {})
    doc["headline"] = "Guided meeting"
    doc["presentationOnly"] = True
    doc["doesNotAlterRuntime"] = True
    doc["doesNotAlterCoverage"] = True
    doc["doesNotAlterDemand"] = True
    doc["notTimer"] = True
    doc["notRevenue"] = True
    doc["notTenant"] = True
    doc["consumesCoverage"] = True
    doc["consumesDemand"] = True
    doc["sharedExplorer"] = True
    return doc


def preflight(store: ConfigStore, registry: CatalogRegistry) -> dict[str, Any]:
    families = len(registry.families)
    use_cases = len(visible_rows(store))
    missing = [sid for sid in CORE_SCENARIOS if not any(row.get("useCaseId") == sid for row in visible_rows(store))]
    ready = (
        families == 13
        and use_cases == 17
        and not missing
        and APP_VERSION == "0.6.1-ax6.1"
        and UI_CADENCE >= 16
        and MODEL_CADENCE == 7
    )
    return {
        "ready": ready,
        "label": "DEMO READY" if ready else "DEMO NOT READY",
        "version": APP_VERSION,
        "uiCadence": UI_CADENCE,
        "uiCadencePatch": UI_CADENCE_PATCH,
        "modelCadence": MODEL_CADENCE,
        "frontendLoaded": serve_frontend(),
        "catalogFamilies": families,
        "portfolioUseCases": use_cases,
        "coreScenarios": list(CORE_SCENARIOS),
        "coreScenariosMissing": missing,
        "executableIntents": sorted(EXECUTABLE_INTENTS),
        "secretsExposed": False,
        "honesty": "Configured demo coverage. Not a live operator SLA.",
    }
