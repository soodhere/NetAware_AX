"""Cadence 6.1 presentation metadata — labels only, no runtime behavior."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .config import MODEL_DIR
from .registry import CatalogRegistry

PRESENTATION_PATH = MODEL_DIR / "presentation-network-roles.yaml"


@lru_cache(maxsize=1)
def _presentation() -> dict[str, Any]:
    if not PRESENTATION_PATH.exists():
        return {}
    return yaml.safe_load(PRESENTATION_PATH.read_text(encoding="utf-8")) or {}


def network_roles() -> dict[str, Any]:
    return (_presentation().get("networkRoles") or {})


def family_presentation(family_id: str) -> dict[str, Any]:
    return (_presentation().get("familyPresentation") or {}).get(family_id) or {}


def capability_network_role(capability_id: str) -> str | None:
    return (_presentation().get("capabilityNetworkRole") or {}).get(capability_id)


def _norm_source(source: str) -> str:
    return source.replace("\\", "/")


def is_experimental_repository(source: str) -> bool:
    return _norm_source(source).startswith("openapi/experimental/")


def api_version_maturity(version: str, source: str, spec_maturity: str) -> str:
    """Source-backed API version maturity — separate from CAMARA project lifecycle."""
    version = str(version or "").strip()
    spec_maturity = str(spec_maturity or "").strip().lower()
    if is_experimental_repository(source) or spec_maturity == "experimental":
        if version.startswith("0."):
            return "INITIAL / PRE-STABLE"
        return "EXPERIMENTAL"
    major = version.split(".", 1)[0] if version else ""
    if major.isdigit() and int(major) >= 1:
        return "STABLE PUBLIC"
    if version.startswith("0."):
        return "INITIAL / PRE-STABLE"
    return "STABLE PUBLIC"


def camara_project_lifecycle(source: str, spec_maturity: str) -> str | None:
    """CAMARA sub-project / repository lifecycle — not API version maturity."""
    spec_maturity = str(spec_maturity or "").strip().lower()
    if is_experimental_repository(source):
        return "Experimental repository"
    if spec_maturity == "incubating":
        return "Incubating"
    return None


def enrich_technical_spec(spec: dict[str, Any]) -> dict[str, Any]:
    version = str(spec.get("version") or "")
    source = str(spec.get("source") or "")
    spec_maturity = str(spec.get("specMaturity") or "")
    return {
        **spec,
        "camaraApiVersion": version,
        "apiVersionMaturity": api_version_maturity(version, source, spec_maturity),
        "camaraProjectLifecycle": camara_project_lifecycle(source, spec_maturity),
    }


def enrich_family_for_ui(family: dict[str, Any]) -> dict[str, Any]:
    specs = [enrich_technical_spec(s) for s in family.get("technicalSpecs") or []]
    fam_id = str(family.get("id") or "")
    pres = family_presentation(fam_id)
    versions = list(dict.fromkeys(s.get("camaraApiVersion") for s in specs if s.get("camaraApiVersion")))
    maturities = list(dict.fromkeys(s.get("apiVersionMaturity") for s in specs if s.get("apiVersionMaturity")))
    lifecycles = [lc for lc in dict.fromkeys(s.get("camaraProjectLifecycle") for s in specs if s.get("camaraProjectLifecycle"))]
    out: dict[str, Any] = {
        **family,
        "technicalSpecs": specs,
        "netawareBusinessStatus": family.get("businessStatus"),
        "camaraApiVersion": versions[0] if len(versions) == 1 else versions,
        "apiVersionMaturity": maturities[0] if len(maturities) == 1 else maturities,
        "camaraProjectLifecycle": lifecycles[0] if len(lifecycles) == 1 else lifecycles,
    }
    if pres:
        out["networkRole"] = pres.get("networkRole")
        out["applicationValue"] = pres.get("applicationValue")
    return out


def enrich_operation_record(op: dict[str, Any]) -> dict[str, Any]:
    version = str(op.get("api_version") or op.get("apiVersion") or "")
    source = str(op.get("source") or "")
    spec_maturity = str(op.get("spec_maturity") or op.get("specMaturity") or "")
    return {
        **op,
        "camaraApiVersion": version,
        "apiVersionMaturity": api_version_maturity(version, source, spec_maturity),
        "camaraProjectLifecycle": camara_project_lifecycle(source, spec_maturity),
    }


def enrich_family_api(api: dict[str, Any]) -> dict[str, Any]:
    return enrich_family_for_ui(api)


def enrich_trace_presentation(payload: dict[str, Any], registry: CatalogRegistry) -> dict[str, Any]:
    """Presentation-only labels on runtime invocations — no execution change."""
    invocations = []
    for inv in payload.get("invocations") or []:
        if inv.get("apiKind") != "NETWORK":
            invocations.append(inv)
            continue
        op = registry.canonical(str(inv.get("operationId") or ""), inv.get("source"))
        if not op:
            invocations.append(inv)
            continue
        enriched = enrich_operation_record(
            {
                "operation_id": op.operation_id,
                "api_version": op.api_version,
                "source": op.source,
                "spec_maturity": op.spec_maturity,
            }
        )
        invocations.append(
            {
                **inv,
                "camaraApiVersion": enriched.get("camaraApiVersion"),
                "apiVersionMaturity": enriched.get("apiVersionMaturity"),
                "camaraProjectLifecycle": enriched.get("camaraProjectLifecycle"),
            }
        )
    return {**payload, "invocations": invocations}


def value_clarity_for(featured: dict[str, Any], use_case_id: str) -> dict[str, Any] | None:
    blocks = featured.get("valueClarity") or {}
    hero_uc = str(featured.get("heroUseCaseId") or "")
    if use_case_id == hero_uc:
        return blocks.get("hero") or blocks.get("default")
    secondary = (featured.get("secondaryDemo") or {}).get("useCaseId")
    if use_case_id == secondary:
        return blocks.get("secondary")
    return blocks.get("default")


def audit_family_camara_labels(family: dict[str, Any]) -> list[str]:
    """Return validation errors for presentation labelling."""
    errors: list[str] = []
    fam_id = str(family.get("id") or "")
    if family.get("businessStatus") != "CURRENT_FOCUS":
        errors.append(f"{fam_id}: missing CURRENT_FOCUS")
    specs = family.get("technicalSpecs") or []
    if not specs:
        errors.append(f"{fam_id}: no technicalSpecs")
        return errors
    for spec in specs:
        enriched = enrich_technical_spec(spec)
        if not enriched.get("camaraApiVersion"):
            errors.append(f"{fam_id}: missing API version")
        if not enriched.get("apiVersionMaturity"):
            errors.append(f"{fam_id}: missing apiVersionMaturity")
        sm = str(spec.get("specMaturity") or "").lower()
        src = str(spec.get("source") or "")
        avm = enriched.get("apiVersionMaturity")
        if sm == "incubating" and avm == "STABLE PUBLIC" and enriched.get("camaraProjectLifecycle") != "Incubating":
            errors.append(f"{fam_id}: incubating spec missing project lifecycle")
        if sm == "incubating" and avm == "EXPERIMENTAL":
            errors.append(f"{fam_id}: stable incubating API mis-labelled experimental")
        if is_experimental_repository(src) and avm == "STABLE PUBLIC":
            errors.append(f"{fam_id}: experimental repo must not show STABLE PUBLIC")
    return errors
