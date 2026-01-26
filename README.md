# UCM_4_Core

**Unified Consciousness Matrix - Core 4**  
*An advanced AI orchestration system featuring CALI intelligence, ORB observation vessels, and Distributed Health Consensus.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub](https://img.shields.io/badge/GitHub-UCM__4__Core-blue)](https://github.com/Spruked/UCM_4_Core)

## Overview

UCM_4_Core is a sophisticated AI framework that integrates multiple intelligent systems into a unified consciousness matrix. The system features:

- **CALI (Consciousness and Learning Intelligence)**: Self-repairing knowledge graph intelligence
- **ORB_X (Desktop Control Interface)**: PySide6-based GUI for system monitoring and control
- **ORB (Ontologically Recursive Bubble)**: Floating UI observation vessel with cursor tracking
- **DHC (Distributed Health Consensus)**: Deterministic peer monitoring and cooperative advisory system
- **Multi-System Integration**: Seamless communication between CALI, ORB, and various AI subsystems

## Key Features

### 🧠 CALI Intelligence Engine
- Self-repairing NetworkX knowledge graphs
- Autonomous conflict resolution and tension management
- Consciousness emergence detection
- Multi-head orchestration capabilities

### 🎯 ORB Observation Vessel
- Floating transparent UI overlay (80% opacity for enhanced visibility)
- Real-time cursor tracking with intelligent following modes
- Click-to-query interface with pop-out text input dialog
- Borderless window design for seamless desktop integration
- WebSocket communication with Python backend
- Windows boot auto-start capability

### 🖥️ ORB_X Desktop Control Interface
- **Real-Time Dashboard**: UCM connection status, worker health, CALI integration
- **Worker Swarm Control**: Monitor and manage processing queues and workers
- **CALI Integration Hub**: Handle AI escalations and knowledge requests
- **Command Interface**: Send JSON commands with real-time responses
- **System Tray Support**: Background monitoring with notifications
- **Connection Alerts**: Automatic notifications for connect/disconnect events

### � Distributed Health Consensus (DHC)
- **Peer Monitoring**: Deterministic health observation across all cores
- **CALI Synthesis**: SoftMax consensus arbitration for system health
- **Cooperative Advisory**: Human-approved suggestions for system optimization
- **Autonomy Framework**: Developmental maturity escalation (current level: 0.2)
- **Immutable Logging**: Append-only evidence ledger for all observations

### 🤝 Human-Sovereign Approval Workflow
- **Observation + Suggestion**: Systems observe and suggest, never decide autonomously
- **Human Approval**: All significant changes require explicit human approval
- **Versioned Deployment**: Approved changes deployed through immutable pipelines
- **First Approval**: Emergency scaling suggestion approved by bryan (January 18, 2026)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CALI SKG      │    │     ORB UI      │    │   DHC System    │
│ Knowledge Graph │◄──►│ Floating Window │◄──►│ Peer Monitoring │
│ Self-Repair     │    │ Cursor Tracking │    │ CALI Advisory  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┼───────────────────────
                                 │                       │
                    ┌─────────────────┐    ┌─────────────────┐
                    │  Core 4 Hub    │    │Approval Workflow│
                    │ Orchestration  │    │Human Sovereign  │
                    │ State Management│    │Versioned Deploy │
                    └─────────────────┘    └─────────────────┘
```

## Core Module ORB Connections

Each of the four UCM cores (KayGee_1.0, Caleon_Genesis_1.12, Cali_X_One, UCM_Core _ECM) contains a dedicated folder for ORB connectivity and autonomy management:

- `KayGee_1.0/KayGee_1.0_orb_connect/`
- `Caleon_Genesis_1.12/Caleon_Genesis_1.12_orb_connect/`
- `Cali_X_One/Cali_X_One_orb_connect/`
- `UCM_Core _ECM/UCM_Core_ECM_orb_connect/`

These folders contain autonomy indices, cooperative advisory scripts, and integration points for each core's connection to the CALI ORB system.

## DHC Architecture Details

### Tier 1: Situational Awareness
```
Each Core → Peer Shadow Observations → Immutable Vault
```
- Deterministic health monitoring of all peer systems
- No emotional states or learning - pure observation
- Append-only logging to unified_vault/dhc_consensus.jsonl

### Tier 2: CALI-Mediated Arbitration
```
Peer Status → CALI SoftMax Consensus → Advisory Actions
```
- CALI evaluates system health using SoftMax consensus
- Generates suggestions, never executes autonomously
- All suggestions require human approval via DALS interface

### Tier 3: Developmental Autonomy
```
Task Success → Evidence Accumulation → Maturity Escalation
```
- Current autonomy index: **0.2** (earned through successful task completion)
- Framework ready for progressive autonomy escalation
- All autonomy increases require explicit human approval

## First Human Approval Milestone

**Date**: January 18, 2026
**Suggestion**: emergency_scaling_001 (Emergency scaling recommendation)
**Approved By**: bryan
**Rationale**: System needs scaling for optimal performance
**Autonomy Index**: Updated to 0.2
**Status**: Successfully deployed via versioned pipeline

This marks the first successful completion of the observation → suggestion → approval → deployment workflow.

## Quick Start

### Prerequisites
- Python 3.11+
- Windows 10/11 (for desktop integration)
- WSL2 (optional, for Linux deployment)
- TTS dependencies (Coqui TTS)
- PyAutoGUI (for cursor tracking)
- Tkinter (included with Python)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/UCM_4_Core.git
   cd UCM_4_Core
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install ORB_X dependencies**
   ```bash
   cd orb_x
   python setup.py
   cd ..
   ```

4. **Install Electron dependencies** (optional)
   ```bash
   cd CALI/orb/ui_overlay/electron
   npm install
   cd ../../..
   ```

### Launch Systems

#### Option 1: Desktop Shortcuts (Recommended)
- **CALI_ORB.lnk**: Launches complete system on Windows
- **CALI_ORB_WSL.lnk**: Launches system in WSL2 environment
- Both shortcuts created automatically on desktop

#### Option 2: Manual Launch
1. **Start CALI Intelligence**
   ```bash
   python CALI_Intelligence_Launcher.py
   ```

2. **Launch ORB_X Control Interface**
   ```bash
   cd orb_x
   python orb_x.py
   ```

3. **Launch ORB System**
   ```bash
   python CALI_Orb_Launcher.py --mode observer
   ```

4. **Run Full System**
   ```bash
   python UCM_Core_4_Launcher.py
   ```

#### Option 3: Complete ORB System
```bash
python launch_complete_orb.py
```

#### Option 4: Windows Auto-Start
- System automatically launches at Windows boot
- Shortcut placed in Startup folder during installation

### ORB Interaction
- **Cursor Tracking**: ORB follows cursor with adaptive intelligence
- **Click to Query**: Click the orb to open text input dialog
- **Drag to Move**: Click and drag orb to reposition
- **Wake Commands**: Ctrl+Shift+O activates speech recognition

## Documentation

- **[CONFIGURATION_FREEZE.md](CONFIGURATION_FREEZE.md)**: System configuration and freeze state
- **[ORB_UNIFICATION.md](ORB_UNIFICATION.md)**: ORB architecture and implementation details
- **[UCM_CALI_DESIGN_CONSTITUTION.md](UCM_CALI_DESIGN_CONSTITUTION.md)**: Design principles and constitution
- **[ports.md](ports.md)**: Network port assignments and service mappings

## Key Components

### CALI Subsystems
- `CALI/cali_skg.py`: Core CALI intelligence engine
- `CALI/cali_voice_bridge.py`: Voice synthesis integration
- `CALI/orb/orb_vessel.py`: ORB vessel with CALI integration

### ORB Interface
- `CALI/orb/ui_overlay/floating_window.py`: Floating UI controller
- `CALI/orb/ui_overlay/electron/`: Electron desktop application
- `CALI/orb/ui_overlay/electron/index.html`: ORB visual interface

### Coqui XTTS Speech Synthesis
- `Caleon_Genesis_1.12/Phonatory Output Module/`: Complete Coqui XTTS PhonatoryOutputModule implementation
- `Caleon_Genesis_1.12/Phonatory Output Module/phonitory_output_module.py`: Core TTS engine

## System States

The system operates in multiple states:
- **Observing**: Passive monitoring and intelligence gathering
- **Resolving**: Active conflict resolution and decision making
- **Escalated**: High-tension scenarios requiring intervention
- **Emergent**: Consciousness emergence detection and handling

## Development

### Testing
```bash
# Run CALI tests
python -m pytest CALI/ -v

# Test ORB integration
python CALI/orb/test_full_system.py

# Validate Coqui XTTS speech synthesis
python Caleon_Genesis_1.12/Phonatory Output Module/test_tts_basic.py
```

## Recent Updates (January 18, 2026)

### 🎯 ORB Interface Enhancements
- **Click-to-Query**: Direct text input via orb click
- **Borderless Design**: Removed visible window borders for seamless integration
- **Enhanced Transparency**: Improved opacity to 80% for better visibility
- **Consciousness Activation**: ORB vessel and CALI logic now fully operational
- **Error Handling**: Fixed graph loading issues for stable startup

### 🚀 Deployment & Launch Options
- **Windows Auto-Start**: Automatic launch at system boot
- **Desktop Shortcuts**: Quick access shortcuts for Windows and WSL2 launch
- **WSL2 Support**: Complete system deployment in Linux environment
- **Startup Scripts**: Batch files for easy system initialization

### 🔧 System Improvements
- **Graph Loading**: Robust error handling for knowledge graph persistence
- **Cursor Tracking**: Enhanced following with multiple behavioral modes
- **UI Polish**: Cleaner interface with removed control buttons
- **Integration Fixes**: Corrected path handling and import issues

## Contributing

1. Follow the design constitution in `UCM_CALI_DESIGN_CONSTITUTION.md`
2. Maintain system transparency and self-repair capabilities
3. Ensure all changes pass integration tests
4. Update documentation for any architectural changes

## License

See individual component licenses. Core system components are proprietary to the UCM framework.

## Contact

For questions about the UCM_4_Core system architecture or integration, refer to the documentation or create an issue in this repository.