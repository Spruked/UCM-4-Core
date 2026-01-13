#!/usr/bin/env python3
"""
Brain state telemetry provider (read-only, no synthesis).

Sources (existing, no new endpoints):
- UCM_Core_ECM: GET http://localhost:8002/api/health
- Caleon_Genesis_1.12: file activity in monitoring/ or vaults/
- Cali_X_One: SQLite liveness ucm_skg.db (read-only open + mtime)
- KayGee_1.0: log activity in logs/

States (enum in cali_orchestrator.BrainState): AVAILABLE, SILENT, UNAVAILABLE.
"""

import json
import sqlite3
import urllib.request
from pathlib import Path
from typing import Dict
import time

from core4_superintelligence.cali_orchestrator import BrainState


class BrainTelemetryProvider:
    def __init__(self, ucm_root: Path, stale_seconds: int = 60):
        self.ucm_root = Path(ucm_root)
        self.stale_seconds = stale_seconds

    def sample(self) -> Dict[str, BrainState]:
        """Collect availability from all known siblings (read-only)."""
        return {
            "UCM_Core_ECM": self._ecm_health(),
            "Caleon_Genesis_1.12": self._caleon_activity(),
            "Cali_X_One": self._cali_x_db(),
            "KayGee_1.0": self._kaygee_logs(),
        }

    def _ecm_health(self) -> BrainState:
        url = "http://localhost:8002/api/health"
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status != 200:
                    return BrainState.UNAVAILABLE
                raw = resp.read()
                data = json.loads(raw.decode("utf-8")) if raw else {}
                available = data.get("status") == "healthy"
                return BrainState.AVAILABLE if available else BrainState.SILENT
        except Exception:
            return BrainState.UNAVAILABLE

    def _caleon_activity(self) -> BrainState:
        base = self.ucm_root.parent / "Caleon_Genesis_1.12"
        if not base.exists():
            return BrainState.UNAVAILABLE
        recent = self._latest_mtime([base / "monitoring", base / "vaults"])
        if recent is None:
            return BrainState.SILENT
        return self._recent_to_state(recent)

    def _cali_x_db(self) -> BrainState:
        db_path = self.ucm_root.parent / "Cali_X_One" / "ucm_skg.db"
        if not db_path.exists():
            return BrainState.UNAVAILABLE
        try:
            # Read-only open to avoid side effects
            sqlite3.connect(f"file:{db_path}?mode=ro", uri=True).close()
        except Exception:
            return BrainState.UNAVAILABLE
        recent = db_path.stat().st_mtime
        return self._recent_to_state(recent)

    def _kaygee_logs(self) -> BrainState:
        logs_dir = self.ucm_root.parent / "KayGee_1.0" / "logs"
        if not logs_dir.exists():
            return BrainState.UNAVAILABLE
        recent = self._latest_mtime([logs_dir])
        if recent is None:
            return BrainState.SILENT
        return self._recent_to_state(recent)

    def _latest_mtime(self, paths) -> float:
        latest = None
        for p in paths:
            if not p.exists():
                continue
            if p.is_file():
                mtime = p.stat().st_mtime
                latest = mtime if latest is None else max(latest, mtime)
            else:
                for sub in p.rglob("*"):
                    try:
                        mtime = sub.stat().st_mtime
                        latest = mtime if latest is None else max(latest, mtime)
                    except Exception:
                        continue
        return latest

    def _recent_to_state(self, mtime: float) -> BrainState:
        now = time.time()
        if (now - mtime) <= self.stale_seconds:
            return BrainState.AVAILABLE
        return BrainState.SILENT
