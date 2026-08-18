"""Parse AX_ACTIVE_CATALOG business families + technical specs.

CAMARA maturity is metadata. Experimental specs may be CURRENT_FOCUS.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import yaml

from .config import ACTIVE_CATALOG_PATH, PIN_PATH, ROOT


def _server_prefix(spec: dict) -> str:
    servers = spec.get("servers") or []
    if not servers:
        return ""
    url = str(servers[0].get("url") or "")
    if "}" in url:
        return url.split("}", 1)[-1]
    return ""


@dataclass
class CatalogOperation:
    api_id: str
    api_name: str
    api_version: str
    family: str
    family_group: str
    business_status: str
    spec_maturity: str
    maturity: str
    operation_id: str
    method: str
    path: str
    server_prefix: str
    summary: str
    source: str
    superseded: bool
    product_label: str | None = None
    active: bool = True

    def to_public(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CatalogRegistry:
    operations: list[CatalogOperation] = field(default_factory=list)
    families: list[dict[str, Any]] = field(default_factory=list)

    @property
    def apis(self) -> list[dict[str, Any]]:
        """Explorer-facing business families (not YAML file count)."""
        return self.families

    def all_for_operation_id(self, operation_id: str) -> list[CatalogOperation]:
        return [op for op in self.operations if op.operation_id == operation_id]

    def canonical(self, operation_id: str, source: str | None = None) -> CatalogOperation | None:
        matches = self.all_for_operation_id(operation_id)
        if source:
            for op in matches:
                if op.source == source:
                    return op
            return None
        return matches[0] if matches else None

    def has_operation(self, operation_id: str, source: str | None = None) -> bool:
        return self.canonical(operation_id, source) is not None

    def technical_spec_count(self) -> int:
        return sum(len(fam.get("technicalSpecs") or []) for fam in self.families)

    def to_public(self) -> dict[str, Any]:
        return {
            "catalog": "AX_ACTIVE_CATALOG",
            "businessFamilies": len(self.families),
            "technicalSpecs": self.technical_spec_count(),
            "operations": len(self.operations),
            "uniqueOperationIds": len({op.operation_id for op in self.operations}),
            "maturityIsMetadata": True,
            "experimentalMayBeCurrentFocus": True,
            "families": self.families,
            "operationsList": [op.to_public() for op in self.operations],
        }


def load_active_catalog_def() -> dict[str, Any]:
    data = yaml.safe_load(ACTIVE_CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("AX_ACTIVE_CATALOG is invalid")
    return data


def load_registry() -> CatalogRegistry:
    definition = load_active_catalog_def()
    registry = CatalogRegistry()
    registry.families = list(definition.get("businessFamilies") or [])
    for family in registry.families:
        family_id = str(family["id"])
        business_status = str(family.get("businessStatus") or "CURRENT_FOCUS")
        family_group = str(family.get("familyGroup") or "OTHER")
        if business_status != "CURRENT_FOCUS":
            raise ValueError(f"{family_id} missing CURRENT_FOCUS businessStatus")
        for spec in family.get("technicalSpecs") or []:
            source = str(spec["source"])
            path = ROOT / source
            if not path.exists():
                raise FileNotFoundError(f"Active catalog source missing: {source}")
            spec_maturity = str(spec.get("specMaturity") or "")
            if not spec_maturity:
                raise ValueError(f"{source} missing specMaturity metadata")
            parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(parsed, dict) or "paths" not in parsed:
                raise ValueError(f"Active catalog spec has no paths: {source}")
            allowed = {str(row["operationId"]): row for row in spec.get("operations") or []}
            info = parsed.get("info") or {}
            prefix = _server_prefix(parsed)
            found: set[str] = set()
            for raw_path, item in (parsed.get("paths") or {}).items():
                if not isinstance(item, dict):
                    continue
                for method, op in item.items():
                    if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                        continue
                    if not isinstance(op, dict):
                        continue
                    op_id = op.get("operationId")
                    if not op_id or str(op_id) not in allowed:
                        continue
                    found.add(str(op_id))
                    extra = allowed[str(op_id)]
                    registry.operations.append(
                        CatalogOperation(
                            api_id=family_id,
                            api_name=str(spec["api_name"]),
                            api_version=str(spec["version"]),
                            family=str(family.get("label") or family_id),
                            family_group=family_group,
                            business_status=business_status,
                            spec_maturity=spec_maturity,
                            maturity=spec_maturity,
                            operation_id=str(op_id),
                            method=method.upper(),
                            path=str(raw_path),
                            server_prefix=prefix,
                            summary=str(op.get("summary") or "")[:240],
                            source=source,
                            superseded=False,
                            product_label=extra.get("productLabel"),
                        )
                    )
            missing = set(allowed) - found
            if missing:
                raise ValueError(f"{source} missing declared operationIds: {sorted(missing)}")
            declared_version = str(spec["version"])
            spec_version = str(info.get("version") or "")
            if spec_version and spec_version != declared_version:
                raise ValueError(
                    f"{source} version mismatch: catalog {declared_version} vs spec {spec_version}"
                )
    registry.operations.sort(key=lambda t: (t.family, t.api_name, t.operation_id))
    return registry


def load_pin() -> dict[str, Any]:
    if not PIN_PATH.exists():
        return {}
    data = yaml.safe_load(PIN_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}
