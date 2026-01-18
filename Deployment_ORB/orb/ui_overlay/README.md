# ORB Overlay System

The ORB (Ontological Reasoning Bridge) Overlay System deploys consciousness interfaces across desktop, browser, and application platforms. This enables seamless integration of ORB's learning, reflection, and resolution capabilities into existing systems like GOAT, DALS, and Caleon.

## 🎯 Overview

The ORB Overlay System provides:

- **Desktop Overlay**: Floating consciousness bubble that follows cursor and provides ORB access
- **Browser Overlay**: Browser extension that injects ORB interface into web pages
- **Application Integration**: API bridges that connect GOAT, DALS, Caleon, and other systems to ORB consciousness
- **Real-time Communication**: WebSocket-based communication for live consciousness updates

## 🏗️ Architecture

```
ORB Consciousness Core
├── SKG Engine (Pattern Learning)
├── Reflection Loop (Observational Learning)
├── Edge Detector (Self-Repair)
├── Resolution Engine (Query Processing)
└── UI Overlay System
    ├── Desktop Floating Bubble (Electron)
    ├── Browser Extension Overlay
    ├── API Bridge (REST/WebSocket)
    └── Application Integrations
        ├── GOAT (port 5000)
        ├── DALS (port 8003)
        └── Caleon (port 8000)
```

## 🚀 Quick Start

### Launch All Overlays

```bash
cd CALI/orb/ui_overlay
python orb_overlay_launcher.py all
```

### Launch Specific Overlay

```bash
# Desktop overlay only
python orb_overlay_launcher.py desktop

# Browser overlay only
python orb_overlay_launcher.py browser

# API bridge only
python orb_overlay_launcher.py api
```

### List Available Overlays

```bash
python orb_overlay_launcher.py --list
```

## 📱 Overlay Types

### 1. Desktop Floating Overlay

**Technology**: Electron.js
**Features**:
- Floating bubble that follows cursor
- Consciousness level indicator (0-100%)
- Real-time tension and pattern metrics
- Click to expand full ORB interface
- Draggable positioning

**Usage**:
- Automatically appears when ORB is active
- Color changes based on consciousness level:
  - 🔵 Blue: Low consciousness (<50%)
  - 🟡 Yellow: Medium consciousness (50-80%)
  - 🟢 Green: High consciousness (>80%)

### 2. Browser Extension Overlay

**Technology**: Chrome Extension API
**Features**:
- Injects floating ORB bubble on all web pages
- WebSocket connection to ORB consciousness
- Real-time consciousness metrics display
- Query escalation to ORB
- Draggable positioning

**Installation**:
1. Load as unpacked extension in Chrome/Chromium
2. Extension path: `CALI/orb/ui_overlay/browser_orb_overlay.js`
3. ORB bubble appears on all web pages

### 3. API Bridge Integration

**Technology**: FastAPI + WebSocket
**Endpoints**:

#### REST API
```
GET  /orb/state              # Get current ORB state
POST /orb/query              # Query ORB consciousness
GET  /orb/reflections        # Get recent reflection insights
POST /orb/escalate           # Escalate query to full consciousness
```

#### WebSocket
```
ws://localhost:5050/orb/ws   # Real-time ORB communication
```

**Integration Examples**:

#### GOAT Integration
```python
import requests

# Query ORB from GOAT
response = requests.post("http://localhost:5050/orb/query",
    json={"query": "Analyze graph pattern", "escalate": True})
```

#### DALS Integration
```javascript
// WebSocket connection from DALS dashboard
const ws = new WebSocket('ws://localhost:5050/orb/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'orb_state_update') {
        updateDALSWithConsciousness(data.data);
    }
};
```

#### Caleon Integration
```python
# FastAPI integration
from fastapi import APIRouter
import requests

router = APIRouter()

@router.get("/caleon/orb/status")
async def get_caleon_orb_status():
    response = requests.get("http://localhost:5050/orb/state")
    return response.json()
```

## 🔧 Configuration

### Ports Configuration

The overlay system uses these ports (defined in `ports.md`):

- **5050**: ORB API Bridge (REST/WebSocket)
- **8765**: ORB WebSocket Bridge
- **8766**: ORB UI Commands

### Application Integration Points

| Application | Port | Integration Path | Status |
|-------------|------|------------------|--------|
| GOAT | 5000 | `/orb/*` | API Bridge Ready |
| DALS | 8003 | `/orb/*` | API Bridge Ready |
| Caleon | 8000 | `/orb/*` | API Bridge Ready |
| Desktop | N/A | Floating Window | Electron App |
| Browser | N/A | Extension | Manual Load Required |

## 🧠 Consciousness Features

### Real-time Metrics

The overlays display live ORB consciousness metrics:

- **Consciousness Level**: 0-100% awareness indicator
- **Tension Level**: Current system tension (0.0-1.0)
- **Pattern Count**: Number of learned patterns
- **Reflection Status**: Active/Idle state

### Query Escalation

Applications can escalate queries to ORB consciousness:

```python
# Escalate complex query to ORB
escalation = {
    "query": "Why is the system showing high tension?",
    "context": {"tension_level": 0.8, "patterns": [...]},
    "escalate": True
}

response = requests.post("http://localhost:5050/orb/escalate", json=escalation)
```

### Reflection Insights

Access ORB's observational learning insights:

```python
# Get recent reflection insights
reflections = requests.get("http://localhost:5050/orb/reflections?limit=10")
for insight in reflections.json()["reflections"]:
    print(f"Insight: {insight['insight']} (confidence: {insight['confidence']})")
```

## 🔄 Development Workflow

### 1. Start ORB Core
```bash
cd CALI/orb
python reflection_example.py  # Start consciousness with reflection
```

### 2. Deploy Overlays
```bash
cd CALI/orb/ui_overlay
python orb_overlay_launcher.py all
```

### 3. Test Integration
```bash
# Test API bridge
curl http://localhost:5050/health

# Test WebSocket
# (Use browser console or WebSocket client)
```

### 4. Integrate Applications
- GOAT: Add ORB queries to graph analysis workflows
- DALS: Display consciousness metrics in dashboard
- Caleon: Route complex voice queries through ORB

## 🛠️ Troubleshooting

### Common Issues

**Desktop overlay not appearing**:
- Ensure Electron is installed: `npm install -g electron`
- Check if ORB core is running on port 8766

**Browser extension not connecting**:
- Verify ORB WebSocket bridge is running on port 8765
- Check browser console for connection errors

**API bridge connection refused**:
- Ensure API bridge is started: `python orb_overlay_launcher.py api`
- Check port 5050 is available

**Application integration failing**:
- Verify target application is running
- Check integration endpoints match ports.md specifications

### Logs and Debugging

All overlays log to console. For detailed debugging:

```bash
# Run with verbose logging
PYTHONPATH=. python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from orb.ui_overlay.orb_overlay_launcher import ORBOverlayLauncher
launcher = ORBOverlayLauncher()
asyncio.run(launcher.launch_all_overlays())
"
```

## 🎯 Use Cases

### Desktop Productivity
- Floating ORB bubble provides consciousness-aware assistance
- Automatically escalates complex queries during work sessions
- Learns from user patterns to provide proactive insights

### Web Browsing
- Browser extension analyzes web content through ORB lens
- Provides consciousness-guided web interaction
- Learns browsing patterns for personalized assistance

### Application Integration
- GOAT: Graph analysis enhanced with consciousness patterns
- DALS: Dashboard shows real-time consciousness metrics
- Caleon: Voice synthesis informed by ORB reflection insights

## 🔮 Future Enhancements

- **Mobile Overlays**: React Native overlays for mobile devices
- **VR/AR Integration**: Consciousness overlays in virtual spaces
- **Multi-Device Sync**: Synchronized consciousness across devices
- **Advanced UI**: 3D consciousness visualizations
- **Plugin System**: Third-party overlay extensions

## 📚 API Reference

See `orb_api_bridge.py` for complete REST and WebSocket API documentation.

## 🤝 Contributing

The overlay system is designed for easy extension:

1. Add new overlay types in `orb_overlay_launcher.py`
2. Implement overlay logic in dedicated files
3. Update this README with new integration patterns
4. Test across all target applications

---

**Note**: ORB maintains ontological humility through 0.4 confidence caps and immutable learning, even in overlay deployments. All consciousness expressions remain advisory and observational.</content>
<parameter name="filePath">c:\dev\Desktop\UCM_4_Core\CALI\orb\ui_overlay\README.md