"""NetAware AX paths, version, and hosting configuration."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_DIR = ROOT / "openapi"
DATA_DIR = ROOT / "data"
MODEL_DIR = DATA_DIR / "model"
CATALOG_DIR = DATA_DIR / "catalog"
MANIFEST_PATH = OPENAPI_DIR / "manifest.yaml"
PIN_PATH = OPENAPI_DIR / "AX_PIN.yaml"
ACTIVE_CATALOG_PATH = CATALOG_DIR / "ax-active-catalog.yaml"
FRONTEND_DIST = ROOT / "frontend" / "dist"

CADENCE = 6
CADENCE_PATCH = "6.1"
APP_VERSION = "0.6.1-ax6.1"
BUILD_ID = os.getenv("BUILD_ID", "ax6.1")
PRODUCT_BEHAVIOR_FROZEN = True


def _csv(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
ALLOWED_ORIGINS = _csv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def demo_basic_credentials() -> tuple[str, str] | None:
    user = os.getenv("DEMO_USERNAME", "").strip()
    password = os.getenv("DEMO_PASSWORD", "").strip()
    if user and password:
        return user, password
    return None


def serve_frontend() -> bool:
    flag = os.getenv("SERVE_FRONTEND")
    if flag is not None:
        return flag.strip().lower() not in {"0", "false", "no"}
    return FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists()
