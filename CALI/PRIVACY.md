# Privacy & Data Handling

This project ships assistant components with different visibility capabilities. Nothing collects keystrokes or clipboard data, and outbound network calls are limited to the services described below.

## Capabilities by component

- **Browser Assistant (`bubble_forge/orb_interface/core/browser_assistant.py`)**
  - Captures browser page screenshots and extracts DOM data only when the user explicitly grants permission and assisted mode is enabled.
  - Uses Playwright to automate the browser; no stealth action occurs until the user approves access.
  - No credentials are auto-filled; actions are limited to guided steps unless explicitly allowed.

- **Floating Orb (`electron/src/floating_assistant_orb.py`, `masterdashboard/backend/orb_server.py`)**
  - Tracks cursor coordinates to move the on-screen orb; does **not** capture screen pixels or keystrokes.
  - Learning is based solely on voluntary interactions.

- **Unanswered Query Vault (`vault_system/unanswered_query_vault/uqv.py`)**
  - Sends query metadata to a local endpoint at `http://localhost:8002/uqv` only. No external hosts are contacted.

## Consent paths

- Browser access requires an explicit user grant (`request_permission`) before any monitoring or screenshots occur.
- Assisted mode must be enabled for periodic screenshots to run.
- Orb cursor tracking is passive and does not collect content; starting it does not require screen/keyboard permission.

## Dependency minimization

- Screen-capture/OCR dependencies (`mss`, `pytesseract`, `opencv-python`) are removed unless re-enabled for a declared feature.
- If a feature later requires visual capture, it must document the purpose, consent flow, and destination of any captured data before re-adding such packages.
