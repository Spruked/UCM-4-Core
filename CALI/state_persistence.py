#!/usr/bin/env python3
"""
Append-only persistence for CALI state hub.

- Events: JSONL with rotation (append-only)
- Snapshots: periodic JSONL (derived, not authoritative)
- Replay on startup: load last snapshot, replay subsequent events
- Integrity signals: visible only; no enforcement
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

from cali_state_hub import _get_state_hub

BASE_DIR = Path(__file__).parent / "state_store"
EVENTS_DIR = BASE_DIR / "events"
SNAPSHOTS_DIR = BASE_DIR / "snapshots"

DEFAULT_CONFIG = {
    "events": {"rotate_mb": 100, "keep_archives": True},
    "snapshots": {"interval_sec": 5},
}

_INTEGRITY = {
    "last_snapshot_ts": None,
    "last_event_ts": None,
    "replay_duration_ms": None,
    "integrity_status": "unknown",
}


def _ensure_dirs():
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)


class AppendOnlyEventStore:
    def __init__(self, rotate_mb: int = 100, keep_archives: bool = True):
        _ensure_dirs()
        self.rotate_bytes = rotate_mb * 1024 * 1024
        self.keep_archives = keep_archives
        self._lock = threading.Lock()
        self._current_path = self._new_file_path()
        self._fh = self._current_path.open("a", encoding="utf-8")

    def _new_file_path(self) -> Path:
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        return EVENTS_DIR / f"events-{ts}.jsonl"

    def append(self, event: Dict[str, Any]):
        line = json.dumps(event, ensure_ascii=False)
        with self._lock:
            self._fh.write(line + "\n")
            self._fh.flush()
            if self._fh.tell() >= self.rotate_bytes:
                self._fh.close()
                rotated = self._current_path
                self._current_path = self._new_file_path()
                self._fh = self._current_path.open("a", encoding="utf-8")
                if not self.keep_archives:
                    try:
                        rotated.unlink()
                    except Exception:
                        pass


class SnapshotWriter(threading.Thread):
    def __init__(self, hub, interval_sec: int = 5):
        super().__init__(daemon=True)
        self.hub = hub
        self.interval_sec = max(1, interval_sec)
        self._stop = threading.Event()
        _ensure_dirs()

    def run(self):
        while not self._stop.is_set():
            time.sleep(self.interval_sec)
            snapshot = self.hub.snapshot()
            entry = {"timestamp": time.time(), "state": snapshot}
            path = SNAPSHOTS_DIR / "snapshots.jsonl"
            try:
                with path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
                _set_integrity(last_snapshot_ts=entry["timestamp"])
            except Exception:
                continue

    def stop(self):
        self._stop.set()


def _iter_snapshot_entries() -> Iterable[Dict[str, Any]]:
    path = SNAPSHOTS_DIR / "snapshots.jsonl"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def _iter_event_entries() -> Iterable[Dict[str, Any]]:
    if not EVENTS_DIR.exists():
        return []
    for path in sorted(EVENTS_DIR.glob("events-*.jsonl")):
        try:
            with path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except Exception:
                        continue
        except Exception:
            continue


def _set_integrity(**kwargs):
    _INTEGRITY.update(kwargs)
    try:
        _get_state_hub().set_integrity(_INTEGRITY)
    except Exception:
        pass


def get_integrity_signals() -> Dict[str, Any]:
    return dict(_INTEGRITY)


def _hash_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _collect_time_range(entries: Iterable[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float]]:
    start = None
    end = None
    for ev in entries:
        ts = ev.get("timestamp")
        if ts is None:
            continue
        start = ts if start is None else min(start, ts)
        end = ts if end is None else max(end, ts)
    return start, end


def replay_into_hub(hub) -> Dict[str, Any]:
    start = time.time()
    last_snapshot_ts = None
    last_event_ts = None
    status = "ok"

    # load last snapshot
    snapshot_state: Optional[Dict[str, Any]] = None
    for entry in _iter_snapshot_entries():
        snapshot_state = entry.get("state") or snapshot_state
        last_snapshot_ts = entry.get("timestamp", last_snapshot_ts)

    if snapshot_state:
        try:
            hub.restore(snapshot_state)
        except Exception:
            status = "partial"

    # replay events newer than snapshot
    try:
        for ev in _iter_event_entries():
            ts = ev.get("timestamp")
            if last_snapshot_ts is not None and ts is not None and ts <= last_snapshot_ts:
                continue
            hub.record_event(ev, notify_listeners=False)
            if ts is not None:
                last_event_ts = ts if last_event_ts is None else max(last_event_ts, ts)
    except Exception:
        status = "needs_attention"

    duration_ms = int((time.time() - start) * 1000)
    _set_integrity(
        last_snapshot_ts=last_snapshot_ts,
        last_event_ts=last_event_ts,
        replay_duration_ms=duration_ms,
        integrity_status=status,
    )
    return _INTEGRITY


class PersistenceManager:
    def __init__(self, hub=None, config: Optional[Dict[str, Any]] = None):
        self.hub = hub or _get_state_hub()
        cfg = DEFAULT_CONFIG.copy()
        if config:
            cfg["events"].update(config.get("events", {}))
            cfg["snapshots"].update(config.get("snapshots", {}))

        _ensure_dirs()
        self.event_store = AppendOnlyEventStore(
            rotate_mb=cfg["events"].get("rotate_mb", 100),
            keep_archives=cfg["events"].get("keep_archives", True),
        )
        self.snapshot_writer = SnapshotWriter(
            self.hub,
            interval_sec=cfg["snapshots"].get("interval_sec", 5),
        )

    def start(self):
        # replay existing data first
        replay_into_hub(self.hub)
        # register sink and start snapshots
        self.hub.add_event_listener(self.event_store.append)
        self.snapshot_writer.start()

    def stop(self):
        try:
            self.snapshot_writer.stop()
        except Exception:
            pass


def init_persistence(config: Optional[Dict[str, Any]] = None) -> PersistenceManager:
    mgr = PersistenceManager(config=config)
    mgr.start()
    return mgr


# -------- Export / Import (append-only) --------

def export_bundle(dest_dir: Path = Path("export_bundle")) -> Dict[str, Any]:
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    events_out = dest_dir / "events.jsonl"
    snapshots_out = dest_dir / "snapshots.jsonl"

    # Write concatenated events
    with events_out.open("w", encoding="utf-8") as out_fh:
        for ev in _iter_event_entries():
            out_fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

    # Write concatenated snapshots
    with snapshots_out.open("w", encoding="utf-8") as out_fh:
        for snap in _iter_snapshot_entries():
            out_fh.write(json.dumps(snap, ensure_ascii=False) + "\n")

    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "events": {
            "hash": _hash_file(events_out),
            "path": str(events_out),
        },
        "snapshots": {
            "hash": _hash_file(snapshots_out),
            "path": str(snapshots_out),
        },
    }

    # Re-open to compute ranges
    with events_out.open("r", encoding="utf-8") as fh:
        ev_entries = [json.loads(line) for line in fh if line.strip()]
    with snapshots_out.open("r", encoding="utf-8") as fh:
        snap_entries = [json.loads(line) for line in fh if line.strip()]

    ev_start, ev_end = _collect_time_range(ev_entries)
    snap_start, snap_end = _collect_time_range(snap_entries)
    manifest["events"].update({"count": len(ev_entries), "start_ts": ev_start, "end_ts": ev_end})
    manifest["snapshots"].update({"count": len(snap_entries), "start_ts": snap_start, "end_ts": snap_end})

    manifest_path = dest_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def import_bundle(source_dir: Path = Path("export_bundle"), hub=None) -> Dict[str, Any]:
    source_dir = Path(source_dir)
    events_path = source_dir / "events.jsonl"
    snaps_path = source_dir / "snapshots.jsonl"
    manifest_path = source_dir / "manifest.json"

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        # validate hashes if present
        try:
            if manifest.get("events", {}).get("hash") and _hash_file(events_path) != manifest["events"]["hash"]:
                raise ValueError("events hash mismatch")
            if manifest.get("snapshots", {}).get("hash") and _hash_file(snaps_path) != manifest["snapshots"]["hash"]:
                raise ValueError("snapshots hash mismatch")
        except Exception as exc:
            return {"status": "needs_attention", "detail": str(exc)}

    # append to new store files (no overwrite)
    _ensure_dirs()
    imported_ev = EVENTS_DIR / f"imported-events-{int(time.time())}.jsonl"
    imported_snap = SNAPSHOTS_DIR / f"imported-snapshots-{int(time.time())}.jsonl"

    if events_path.exists():
        imported_ev.write_text(events_path.read_text(encoding="utf-8"), encoding="utf-8")
    if snaps_path.exists():
        imported_snap.write_text(snaps_path.read_text(encoding="utf-8"), encoding="utf-8")

    # rebuild in-memory hub if provided
    if hub is None:
        hub = _get_state_hub()
    replay_info = replay_into_hub(hub)
    return {"status": "ok", "replay": replay_info, "events_file": str(imported_ev), "snapshots_file": str(imported_snap)}