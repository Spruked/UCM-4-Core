#!/usr/bin/env python3
"""Electron bridge shim for CALI Orb.
Exposes CALIFloatingOrb for PythonShell usage and supports a simple stdin/stdout
message loop so the Electron bridge can coordinate readiness and queries.
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from Orb_Assistant.Orb.floating_assistant_orb import CALIFloatingOrb  # noqa: E402

__all__ = ["CALIFloatingOrb"]


def _main() -> None:
	"""Run Orb and respond to simple IPC messages over stdin/stdout (JSON lines)."""
	orb = CALIFloatingOrb(PROJECT_ROOT)
	orb.start()

	# Signal readiness to Electron bridge
	print(json.dumps({"type": "ready"}), flush=True)

	for line in sys.stdin:
		try:
			msg = json.loads(line.strip())
		except Exception:
			continue

		msg_type = msg.get("type")

		if msg_type == "shutdown":
			orb.stop()
			print(json.dumps({"type": "shutdown_ack"}), flush=True)
			break

		if msg_type == "query":
			text = msg.get("text", "")
			# Stub response; integrate real orb query handling as needed
			response = {
				"type": "query_result",
				"data": {
					"echo": text,
					"state": orb.get_status(),
				},
			}
			print(json.dumps(response), flush=True)


if __name__ == "__main__":
	_main()
