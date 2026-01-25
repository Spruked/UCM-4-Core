#!/usr/bin/env python3
"""
ORB_X - Desktop Control Interface for TrueMark UCM
PySide6-based desktop application for UCM system control

Copyright (c) 2026 TrueMark UCM
Licensed under MIT License
"""

import sys
import json
import requests
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QTabWidget, QTableWidget,
    QTableWidgetItem, QProgressBar, QSystemTrayIcon, QMenu,
    QMessageBox, QSplitter, QGroupBox, QFormLayout, QLineEdit,
    QComboBox, QSpinBox, QCheckBox
)
from PySide6.QtCore import QTimer, Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont, QAction

class UCMWorker(QThread):
    """Worker thread for UCM API calls"""
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, endpoint, method="GET", data=None):
        super().__init__()
        self.endpoint = endpoint
        self.method = method
        self.data = data
        self.base_url = "http://localhost:5050"  # Connect to ORB API

    def run(self):
        try:
            url = f"{self.base_url}{self.endpoint}"
            if self.method == "GET":
                response = requests.get(url, timeout=10)
            elif self.method == "POST":
                response = requests.post(url, json=self.data, timeout=10)

            if response.status_code == 200:
                self.finished.emit(response.json())
            else:
                self.error.emit(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.error.emit(str(e))

class ORBXMainWindow(QMainWindow):
    """Main ORB_X application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ORB_X - TrueMark UCM Control")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize system tray
        self.setup_system_tray()

        # Connection status tracking
        self.connection_status = False
        self.last_connection_check = False

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.create_dashboard_tab()
        self.create_workers_tab()
        self.create_cali_tab()
        self.create_commands_tab()

        # Status bar
        self.statusBar().showMessage("ORB_X Ready - Connected to UCM")

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all_tabs)
        self.update_timer.start(5000)  # Update every 5 seconds

        # Initial update
        self.update_all_tabs()

    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon())  # You can set a custom icon

        tray_menu = QMenu()
        show_action = QAction("Show ORB_X", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def create_dashboard_tab(self):
        """Create the dashboard tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Status indicators
        status_group = QGroupBox("System Status")
        status_layout = QFormLayout(status_group)

        self.ucm_status = QLabel("Checking...")
        self.cali_status = QLabel("Checking...")
        self.workers_status = QLabel("Checking...")

        status_layout.addRow("UCM Service:", self.ucm_status)
        status_layout.addRow("CALI Bridge:", self.cali_status)
        status_layout.addRow("Worker Swarm:", self.workers_status)

        layout.addWidget(status_group)

        # Activity log
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)

        self.activity_log = QTextEdit()
        self.activity_log.setMaximumHeight(200)
        self.activity_log.setReadOnly(True)
        log_layout.addWidget(self.activity_log)

        layout.addWidget(log_group)

        self.tabs.addTab(tab, "📊 Dashboard")

    def create_workers_tab(self):
        """Create the workers control tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Workers table
        self.workers_table = QTableWidget()
        self.workers_table.setColumnCount(4)
        self.workers_table.setHorizontalHeaderLabels(["Worker ID", "Status", "Queue Size", "Actions"])
        layout.addWidget(self.workers_table)

        # Control buttons
        controls_layout = QHBoxLayout()

        restart_all_btn = QPushButton("Restart All Workers")
        restart_all_btn.clicked.connect(self.restart_all_workers)
        controls_layout.addWidget(restart_all_btn)

        stop_all_btn = QPushButton("Stop All Workers")
        stop_all_btn.clicked.connect(self.stop_all_workers)
        controls_layout.addWidget(stop_all_btn)

        layout.addLayout(controls_layout)

        self.tabs.addTab(tab, "👥 Workers")

    def create_cali_tab(self):
        """Create the CALI integration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # CALI status
        cali_group = QGroupBox("CALI Bridge Status")
        cali_layout = QFormLayout(cali_group)

        self.cali_bridge_status = QLabel("Checking...")
        self.cali_escalations = QLabel("0 pending")

        cali_layout.addRow("Bridge Status:", self.cali_bridge_status)
        cali_layout.addRow("Pending Escalations:", self.cali_escalations)

        layout.addWidget(cali_group)

        # Escalation handling
        escalation_group = QGroupBox("Escalation Management")
        escalation_layout = QVBoxLayout(escalation_group)

        self.escalation_table = QTableWidget()
        self.escalation_table.setColumnCount(3)
        self.escalation_table.setHorizontalHeaderLabels(["Escalation ID", "Type", "Actions"])
        escalation_layout.addWidget(self.escalation_table)

        layout.addWidget(escalation_group)

        self.tabs.addTab(tab, "🤖 CALI")

    def create_commands_tab(self):
        """Create the command interface tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Command input
        command_group = QGroupBox("Send Command")
        command_layout = QVBoxLayout(command_group)

        self.command_combo = QComboBox()
        self.command_combo.addItems([
            "status", "restart", "shutdown", "health_check",
            "cali_sync", "worker_reset", "certificate_validate"
        ])
        command_layout.addWidget(QLabel("Command:"))
        command_layout.addWidget(self.command_combo)

        self.param_input = QTextEdit()
        self.param_input.setMaximumHeight(100)
        self.param_input.setPlaceholderText('{"key": "value"}')
        command_layout.addWidget(QLabel("Parameters (JSON):"))
        command_layout.addWidget(self.param_input)

        send_btn = QPushButton("Send Command")
        send_btn.clicked.connect(self.send_command)
        command_layout.addWidget(send_btn)

        layout.addWidget(command_group)

        # Response display
        response_group = QGroupBox("Command Response")
        response_layout = QVBoxLayout(response_group)

        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        response_layout.addWidget(self.response_display)

        layout.addWidget(response_group)

        self.tabs.addTab(tab, "⚡ Commands")

    def update_all_tabs(self):
        """Update all tab contents"""
        self.update_dashboard()
        self.update_workers()
        self.update_cali()

    def update_dashboard(self):
        """Update dashboard status"""
        # Test UCM connection
        worker = UCMWorker("/health")
        worker.finished.connect(self.handle_connection_success)
        worker.error.connect(self.handle_connection_error)
        worker.start()

        # Log activity
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.append(f"[{timestamp}] System status updated")

    def handle_connection_success(self, data):
        """Handle successful connection"""
        self.ucm_status.setText("✅ Connected")
        self.check_connection_status_change(True)

    def handle_connection_error(self, error):
        """Handle connection error"""
        self.ucm_status.setText(f"❌ Disconnected: {error}")
        self.check_connection_status_change(False)

    def check_connection_status_change(self, is_connected):
        """Check if connection status changed and notify"""
        if is_connected != self.last_connection_check:
            self.last_connection_check = is_connected
            if is_connected:
                self.show_notification("ORB_X Connected", "Successfully connected to UCM service")
                self.log_activity("🔗 ORB_X connected to UCM")
            else:
                self.show_notification("ORB_X Disconnected", "Lost connection to UCM service")
                self.log_activity("❌ ORB_X disconnected from UCM")

    def show_notification(self, title, message):
        """Show system tray notification"""
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,
                3000  # Show for 3 seconds
            )

    def update_workers(self):
        """Update workers table"""
        worker = UCMWorker("/workers/status")
        worker.finished.connect(self.populate_workers_table)
        worker.error.connect(lambda err: self.log_error(f"Workers update failed: {err}"))
        worker.start()

    def update_cali(self):
        """Update CALI status"""
        worker = UCMWorker("/cali/status")
        worker.finished.connect(self.update_cali_status)
        worker.error.connect(lambda err: self.cali_status.setText(f"❌ {err}"))
        worker.start()

    def populate_workers_table(self, data):
        """Populate workers table with data"""
        if "workers" not in data:
            return

        workers = data["workers"]
        self.workers_table.setRowCount(len(workers))

        for row, worker in enumerate(workers):
            self.workers_table.setItem(row, 0, QTableWidgetItem(worker.get("id", "")))
            self.workers_table.setItem(row, 1, QTableWidgetItem(worker.get("status", "")))
            self.workers_table.setItem(row, 2, QTableWidgetItem(str(worker.get("queue_size", 0))))

            # Actions button
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)

            restart_btn = QPushButton("Restart")
            restart_btn.clicked.connect(lambda: self.restart_worker(worker["id"]))
            actions_layout.addWidget(restart_btn)

            stop_btn = QPushButton("Stop")
            stop_btn.clicked.connect(lambda: self.stop_worker(worker["id"]))
            actions_layout.addWidget(stop_btn)

            self.workers_table.setCellWidget(row, 3, actions_widget)

    def update_cali_status(self, data):
        """Update CALI status display"""
        self.cali_bridge_status.setText("✅ Active" if data.get("active") else "❌ Inactive")
        escalations = data.get("pending_escalations", 0)
        self.cali_escalations.setText(f"{escalations} pending")

    def send_command(self):
        """Send command to UCM"""
        command = self.command_combo.currentText()
        try:
            params = json.loads(self.param_input.toPlainText() or "{}")
        except json.JSONDecodeError:
            self.response_display.setText("❌ Invalid JSON in parameters")
            return

        data = {
            "command": command,
            "parameters": params,
            "timestamp": datetime.now().isoformat()
        }

        worker = UCMWorker("/orb/command", "POST", data)
        worker.finished.connect(lambda resp: self.response_display.setText(
            f"✅ Command sent successfully\n{json.dumps(resp, indent=2)}"
        ))
        worker.error.connect(lambda err: self.response_display.setText(f"❌ Command failed: {err}"))
        worker.start()

    def restart_all_workers(self):
        """Restart all workers"""
        self.send_quick_command("restart_all_workers")

    def stop_all_workers(self):
        """Stop all workers"""
        self.send_quick_command("stop_all_workers")

    def restart_worker(self, worker_id):
        """Restart specific worker"""
        self.send_quick_command("restart_worker", {"worker_id": worker_id})

    def stop_worker(self, worker_id):
        """Stop specific worker"""
        self.send_quick_command("stop_worker", {"worker_id": worker_id})

    def send_quick_command(self, command, params=None):
        """Send a quick command"""
        data = {
            "command": command,
            "parameters": params or {},
            "timestamp": datetime.now().isoformat()
        }

        worker = UCMWorker("/orb/command", "POST", data)
        worker.finished.connect(lambda resp: self.log_activity(f"Command {command} executed"))
        worker.error.connect(lambda err: self.log_error(f"Command {command} failed: {err}"))
        worker.start()

    def log_activity(self, message):
        """Log activity to dashboard"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.append(f"[{timestamp}] {message}")

    def log_error(self, message):
        """Log error to dashboard"""
        self.log_activity(f"❌ {message}")

    def closeEvent(self, event):
        """Handle window close event"""
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "ORB_X",
                "ORB_X is running in the system tray. Right-click to quit.",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("ORB_X")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("TrueMark")

    # Set application icon (optional)
    # app.setWindowIcon(QIcon("orb_x_icon.png"))

    window = ORBXMainWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())