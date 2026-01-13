#!/usr/bin/env python3
"""
Minimal CALI immutable memory (coordination ledger).
Non-hierarchical: records assertions/monitoring without adjudicating truth.
"""

import hashlib
import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class CALIOperationType(Enum):
	AUTHORITY_ASSERTED = "authority_asserted"
	MONITORING_DETECTED = "monitoring_detected"
	RESOURCE_ALLOCATED = "resource_allocated"
	POLICY_ENFORCED = "policy_enforced"
	PEER_CONFLICT_RESOLVED = "peer_conflict_resolved"
	ERROR_RECOVERED = "error_recovered"
	PEER_SYNCHRONIZATION = "peer_synchronization"
	SYSTEM_SELF_REFLECTION = "system_self_reflection"
	CAPABILITY_EVOLVED = "capability_evolved"


class SiblingCore4(Enum):
	KAYGEE_10 = "KayGee_1.0"
	CALI_X_ONE = "Cali_X_One"
	UMC_CORE_ECM = "UCM_Core_ECM"
	CALEON_GENESIS = "Caleon_Genesis_1.12"


@dataclass
class CALIOperationEntry:
	entry_id: str
	sequence_number: int
	timestamp: str
	operation_type: CALIOperationType
	content: Dict[str, Any] = field(default_factory=dict)
	metadata: Dict[str, Any] = field(default_factory=dict)
	previous_hash: str = ""
	writer_id: str = "CALI_Peer_Orchestrator"
	sibling_target: Optional[SiblingCore4] = None
	assertion_level: str = "observation"
	integrity_verified: bool = True
	entry_hash: str = ""

	def to_dict(self) -> Dict[str, Any]:
		return {
			"entry_id": self.entry_id,
			"sequence_number": self.sequence_number,
			"timestamp": self.timestamp,
			"operation_type": self.operation_type.value,
			"content": self.content,
			"metadata": self.metadata,
			"previous_hash": self.previous_hash,
			"writer_id": self.writer_id,
			"sibling_target": self.sibling_target.value if self.sibling_target else None,
			"assertion_level": self.assertion_level,
			"integrity_verified": self.integrity_verified,
			"entry_hash": self.entry_hash,
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> "CALIOperationEntry":
		return cls(
			entry_id=data["entry_id"],
			sequence_number=data["sequence_number"],
			timestamp=data["timestamp"],
			operation_type=CALIOperationType(data["operation_type"]),
			content=data.get("content", {}),
			metadata=data.get("metadata", {}),
			previous_hash=data.get("previous_hash", ""),
			writer_id=data.get("writer_id", "CALI_Peer_Orchestrator"),
			sibling_target=SiblingCore4(data["sibling_target"]) if data.get("sibling_target") else None,
			assertion_level=data.get("assertion_level", "observation"),
			integrity_verified=data.get("integrity_verified", True),
			entry_hash=data.get("entry_hash", ""),
		)

	def compute_hash(self) -> str:
		payload = json.dumps(
			{
				"entry_id": self.entry_id,
				"sequence_number": self.sequence_number,
				"timestamp": self.timestamp,
				"operation_type": self.operation_type.value,
				"content": self.content,
				"metadata": self.metadata,
				"previous_hash": self.previous_hash,
				"writer_id": self.writer_id,
				"sibling_target": self.sibling_target.value if self.sibling_target else None,
				"assertion_level": self.assertion_level,
			},
			sort_keys=True,
		)
		return hashlib.sha256(payload.encode("utf-8")).hexdigest()

	def verify(self, expected_previous_hash: str) -> bool:
		if self.previous_hash != expected_previous_hash:
			self.integrity_verified = False
			return False
		computed = self.compute_hash()
		if self.entry_hash and self.entry_hash != computed:
			self.integrity_verified = False
			return False
		self.entry_hash = computed
		self.integrity_verified = True
		return True


class IntegrityError(RuntimeError):
	pass


class CALIPeerOrchestrationMatrix:
	"""
	Immutable-ish coordination log.
	Records assertions/monitoring with attribution. No adjudication, no hierarchy.
	"""

	def __init__(self, ucm_4_core_path: Path, matrix_id: str = "CALI_Peer_Operations"):
		self.ucm_root = Path(ucm_4_core_path)
		self.cali_path = self.ucm_root / "CALI"
		self.matrix_id = matrix_id
		self.matrix_path = self.cali_path / "cali_immutable_matrix" / f"{matrix_id}.matrix.jsonl"
		self.matrix_path.parent.mkdir(parents=True, exist_ok=True)
		self.entries: List[CALIOperationEntry] = []
		self.sequence_index: Dict[int, CALIOperationEntry] = {}
		self.last_sequence = 0
		self.last_hash = ""
		self.lock = threading.RLock()
		self._load_from_disk()

	# ---------- public API used by orchestration ----------
	def record_sibling_monitoring(self, sibling: SiblingCore4, detection_type: str, detected_metric: str, metric_value: Any, metadata: Optional[Dict[str, Any]] = None) -> CALIOperationEntry:
		return self._append(
			operation_type=CALIOperationType.MONITORING_DETECTED,
			content={"detection_type": detection_type, "detected_metric": detected_metric, "metric_value": metric_value},
			metadata=metadata or {},
			sibling=sibling,
			assertion_level="observation",
		)

	def record_authority_command(self, sibling: SiblingCore4, command: str, justification: str, command_params: Optional[Dict[str, Any]] = None, assertion_level: str = "command") -> CALIOperationEntry:
		return self._append(
			operation_type=CALIOperationType.AUTHORITY_ASSERTED,
			content={"action_taken": command, "justification": justification, "params": command_params or {}},
			metadata={"note": "authority routed, not adjudicated"},
			sibling=sibling,
			assertion_level=assertion_level,
		)

	def record_capability_evolution(self, capability_name: str, significance: float, derivation_context: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> CALIOperationEntry:
		return self._append(
			operation_type=CALIOperationType.CAPABILITY_EVOLVED,
			content={"capability_name": capability_name, "significance": significance, "derivation_context": derivation_context},
			metadata=metadata or {},
			sibling=None,
			assertion_level="observation",
		)

	def get_operational_summary(self) -> Dict[str, Any]:
		with self.lock:
			counts: Dict[str, int] = {}
			per_sibling: Dict[str, int] = {}
			for e in self.entries:
				counts[e.operation_type.value] = counts.get(e.operation_type.value, 0) + 1
				if e.sibling_target:
					name = e.sibling_target.value
					per_sibling[name] = per_sibling.get(name, 0) + 1
			return {
				"total_entries": len(self.entries),
				"last_sequence": self.last_sequence,
				"operation_counts": counts,
				"sibling_interactions": per_sibling,
			}

	# ---------- internal helpers ----------
	def _append(self, operation_type: CALIOperationType, content: Dict[str, Any], metadata: Dict[str, Any], sibling: Optional[SiblingCore4], assertion_level: str) -> CALIOperationEntry:
		with self.lock:
			self.last_sequence += 1
			entry = CALIOperationEntry(
				entry_id=str(uuid.uuid4()),
				sequence_number=self.last_sequence,
				timestamp=datetime.now().isoformat(),
				operation_type=operation_type,
				content=content,
				metadata=metadata,
				sibling_target=sibling,
				assertion_level=assertion_level,
				previous_hash=self.last_hash,
			)
			entry.entry_hash = entry.compute_hash()
			if not entry.verify(self.last_hash):
				raise IntegrityError(f"Entry {entry.sequence_number} failed integrity")
			self.entries.append(entry)
			self.sequence_index[self.last_sequence] = entry
			self.last_hash = entry.entry_hash
			self._write_entry(entry)
			return entry

	def _load_from_disk(self):
		if not self.matrix_path.exists():
			return
		try:
			with self.matrix_path.open("r", encoding="utf-8") as f:
				for line in f:
					data = json.loads(line)
					entry = CALIOperationEntry.from_dict(data)
					expected_prev = self.last_hash
					if entry.entry_hash:
						entry.integrity_verified = entry.verify(expected_prev)
					else:
						entry.entry_hash = entry.compute_hash()
						entry.integrity_verified = entry.verify(expected_prev)
					self.entries.append(entry)
					self.sequence_index[entry.sequence_number] = entry
					self.last_sequence = max(self.last_sequence, entry.sequence_number)
					self.last_hash = entry.entry_hash
		except Exception:
			# On load failure, start clean but do not crash orchestration
			self.entries = []
			self.sequence_index = {}
			self.last_sequence = 0
			self.last_hash = ""

	def _write_entry(self, entry: CALIOperationEntry):
		try:
			with self.matrix_path.open("a", encoding="utf-8") as f:
				f.write(json.dumps(entry.to_dict()) + "\n")
		except Exception:
			# Logging suppressed to keep minimal; could be extended.
			pass

	def verify_chain(self) -> Tuple[bool, int]:
		"""Verify continuity and hashes; returns (ok, first_bad_sequence)."""
		with self.lock:
			expected = ""
			for entry in sorted(self.entries, key=lambda e: e.sequence_number):
				if not entry.verify(expected):
					return False, entry.sequence_number
				expected = entry.entry_hash
			return True, 0

	def export_snapshot(self) -> List[Dict[str, Any]]:
		with self.lock:
			return [e.to_dict() for e in sorted(self.entries, key=lambda e: e.sequence_number)]
