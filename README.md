# UCM_4_Core

**Unified Consciousness Matrix - Core 4**  
*An advanced AI orchestration system featuring CALI intelligence, ORB observation vessels, and POM speech synthesis.*

## Overview

UCM_4_Core is a sophisticated AI framework that integrates multiple intelligent systems into a unified consciousness matrix. The system features:

- **CALI (Consciousness and Learning Intelligence)**: Self-repairing knowledge graph intelligence
- **ORB (Ontologically Recursive Bubble)**: Floating UI observation vessel with cursor tracking
- **POM (Phonatory Output Module)**: Advanced speech synthesis with biological voice modeling
- **Multi-System Integration**: Seamless communication between CALI, ORB, and various AI subsystems

## Key Features

### 🧠 CALI Intelligence Engine
- Self-repairing NetworkX knowledge graphs
- Autonomous conflict resolution and tension management
- Consciousness emergence detection
- Multi-head orchestration capabilities

### 🎯 ORB Observation Vessel
- Floating transparent UI overlay (55% opacity for optimal visibility)
- Real-time cursor tracking with application awareness
- Electron-based desktop integration
- WebSocket communication with Python backend

### 🗣️ POM Speech Synthesis
- Coqui TTS integration with advanced phonatory processing
- Biological voice modeling (larynx, formant, articulation)
- Elegant female voice synthesis
- Real-time CALI response vocalization

### 🔗 System Integration
- Unified communication protocols
- Tension ledger for conflict tracking
- Resolution engine with escalation handling
- Master dashboard for system monitoring

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CALI SKG      │    │     ORB UI      │    │     POM TTS     │
│ Knowledge Graph │◄──►│ Floating Window │◄──►│ Speech Synthesis│
│ Self-Repair     │    │ Cursor Tracking │    │ Voice Modeling  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Core 4 Hub    │
                    │ Orchestration  │
                    │ State Management│
                    └─────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for Electron ORB UI)
- TTS dependencies (Coqui TTS)

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

3. **Install Electron dependencies**
   ```bash
   cd CALI/orb/ui_overlay/electron
   npm install
   cd ../../..
   ```

### Launch Systems

1. **Start CALI Intelligence**
   ```bash
   python CALI_Intelligence_Launcher.py
   ```

2. **Launch ORB Interface**
   ```bash
   python CALI_Orb_Launcher.py
   ```

3. **Run Full System**
   ```bash
   python UCM_Core_4_Launcher.py
   ```

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

### POM Speech
- `Caleon_Genesis_1.12/Phonatory Output Module/`: Complete POM implementation
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

# Validate POM speech
python Caleon_Genesis_1.12/Phonatory Output Module/test_tts_basic.py
```

### Architecture Validation
```bash
# Check system integrity
python CALI/validate_orb_files.py

# Test consciousness emergence
python CALI/orb/test_consciousness_probe.py
```

## Contributing

1. Follow the design constitution in `UCM_CALI_DESIGN_CONSTITUTION.md`
2. Maintain system transparency and self-repair capabilities
3. Ensure all changes pass integration tests
4. Update documentation for any architectural changes

## License

See individual component licenses. Core system components are proprietary to the UCM framework.

## Contact

For questions about the UCM_4_Core system architecture or integration, refer to the documentation or create an issue in this repository.