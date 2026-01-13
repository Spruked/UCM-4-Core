#!/usr/bin/env python3
"""
Lightweight launcher for CALI Floating Assistant Orb.
- Initializes the orb with repository root context
- Provides signal-aware graceful shutdown
- Writes logs to ./logs/orb.log (relative to CALI root)
"""
import argparse
import logging
import signal
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from orb import OntologicallyRecursiveBubble  # Unified ORB


def configure_logging(debug: bool = False) -> None:
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / "orb.log", encoding="utf-8"),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch CALI Floating Assistant Orb")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    configure_logging(debug=args.debug)
    logger = logging.getLogger("orb.launcher")

    orb = OntologicallyRecursiveBubble(PROJECT_ROOT)
    shutdown_requested = False

    def _handle_signal(signum, _frame):
        nonlocal shutdown_requested
        logger.info("Received signal %s, shutting down orb...", signum)
        shutdown_requested = True
        try:
            orb.stop()
        except Exception:
            logger.exception("Error during orb stop")

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    try:
        orb.start()
        logger.info("CALI Orb started. Press Ctrl+C to stop.")

        while not shutdown_requested:
            time.sleep(2.0)
            if not orb.is_healthy():
                logger.error("Orb reported unhealthy state; stopping.")
                shutdown_requested = True
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received; stopping orb.")
    except Exception:
        logger.exception("Orb launcher encountered an error")
    finally:
        try:
            orb.stop()
        except Exception:
            logger.exception("Error during orb stop")
        logger.info("Orb shutdown complete.")


if __name__ == "__main__":
    main()
