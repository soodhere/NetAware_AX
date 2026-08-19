"""Cadence 15 stakeholder sales entry. Presentation context only — not a second product."""
from __future__ import annotations

from typing import Any

from .model import ConfigStore


def public_start(store: ConfigStore) -> dict[str, Any]:
    doc = dict(store.stakeholder_entry or {})
    stories = doc.get("stories") or {}
    if isinstance(stories, dict):
        doc["stories"] = [{"id": key, **value} for key, value in stories.items()]
    doc["headline"] = doc.get("welcome") or "Welcome to NetAware AX"
    doc["consumesCoverage"] = True
    doc["consumesDemand"] = True
    doc["sharedExplorer"] = True
    doc["sharedRuntime"] = True
    doc["notRevenue"] = True
    doc["notTam"] = True
    doc["notMeetingMode"] = True
    doc["notTenant"] = True
    doc["auth"] = {
        "kind": "HTTP_BASIC",
        "serverSide": True,
        "environmentDriven": True,
        "usernameVars": ["BASIC_AUTH_USERNAME", "DEMO_USERNAME"],
        "passwordVars": ["BASIC_AUTH_PASSWORD", "DEMO_PASSWORD"],
        "healthUnauthenticated": True,
        "localBypass": "If neither username/password pair is set, the demo gate is off for local development.",
        "notUserAccounts": True,
        "notSso": True,
        "notRbac": True,
    }
    return doc
