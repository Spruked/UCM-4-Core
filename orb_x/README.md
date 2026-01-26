# ORB_X - Desktop Control Interface

**ORB_X** is the desktop control interface for the TrueMark UCM (Unified Consciousness Matrix) system. It provides a comprehensive GUI for monitoring, controlling, and managing UCM operations through an intuitive PySide6-based application.

## Features

### 🖥️ Desktop Interface
- **System Dashboard**: Real-time status monitoring of UCM services, CALI bridge, and worker swarm
- **Worker Management**: Control and monitor distributed worker processes
- **CALI Integration**: Manage CALI (Consciousness Artificial Lifeform Intelligence) escalations and bridge operations
- **Command Interface**: Send commands directly to the UCM system

### 🔗 Connection Monitoring
- **Real-time Connectivity**: Automatic detection of UCM service availability
- **System Tray Notifications**: Desktop notifications for connection status changes
- **Automatic Reconnection**: Seamless reconnection when UCM service comes back online

### 📊 Monitoring & Control
- **Live Status Updates**: 5-second interval updates of all system components
- **Activity Logging**: Comprehensive activity log with timestamps
- **Error Handling**: Robust error handling with user-friendly notifications

## Installation

### Prerequisites
- Python 3.8+
- UCM system running on localhost:5050

### Setup
```bash
# Clone the repository
cd orb_x/

# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup.py
```

### Dependencies
- PySide6 >= 6.5.0 (Qt6-based GUI framework)
- requests >= 2.28.0 (HTTP client)
- psutil >= 5.9.0 (system monitoring)
- pyyaml >= 6.0 (configuration)

## Usage

### Launch ORB_X
```bash
python orb_x.py
```

### Test Connection
```bash
python test_connection.py
```

### System Tray
ORB_X runs in the system tray when minimized. Right-click the tray icon to:
- Show the main window
- Quit the application

## API Integration

ORB_X connects to the UCM system via REST API endpoints:

- `GET /health` - System health check
- `GET /orb/status` - ORB system status
- `GET /cali/status` - CALI bridge status
- `GET /workers/status` - Worker swarm status
- `POST /orb/command` - Send commands to UCM

## Architecture

```
ORB_X (Desktop GUI)
    ↓ HTTP/REST
UCM API Server (localhost:5050)
    ↓ Internal
UCM Core Systems
```

## Development

### Project Structure
```
orb_x/
├── orb_x.py          # Main application
├── test_connection.py # Connection testing
├── setup.py          # Setup script
├── requirements.txt  # Dependencies
└── README.md         # This file
```

### Building from Source
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python test_connection.py

# Launch application
python orb_x.py
```

## Troubleshooting

### Connection Issues
1. Ensure UCM service is running on localhost:5050
2. Check firewall settings
3. Run `python test_connection.py` to diagnose

### GUI Issues
1. Ensure PySide6 is properly installed
2. Check Qt6 compatibility with your system
3. Try reinstalling dependencies

### System Tray Not Working
- On Linux, ensure you have a system tray available
- On Windows, system tray should work by default
- On macOS, system tray functionality may be limited

## License

Copyright (c) 2026 TrueMark UCM
Licensed under MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For support and questions:
- Check the main UCM repository documentation
- Review the activity log in ORB_X for error details
- Ensure all prerequisites are met

---

**ORB_X v1.0** - Desktop Control Interface for TrueMark UCM