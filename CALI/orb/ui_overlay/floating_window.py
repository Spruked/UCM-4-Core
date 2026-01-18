# UCM_4_Core/CALI/orb/ui_overlay/floating_window.py
"""
Floating ORB UI: Tracks cursor, stays out of the way, deploys on demand.
This is the physical manifestation of ORB in user space.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import json
import websockets
import webbrowser
import pygetwindow as gw
import pyautogui
from datetime import datetime
import pygame  # For cross-platform audio playback

# Import CALI components
from CALI.cali_skg import CALISKGEngine
from CALI.cali_voice_bridge import CALIVoiceBridge

# Import POM 2.0 for speech synthesis (DISABLED - using fallback TTS)
# import sys
# import os
# pom_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'Caleon_Genesis_1.12', 'Phonatory Output Module')
# sys.path.append(pom_path)
# try:
#     from phonitory_output_module import PhonatoryOutputModule
#     pom_available = True
# except ImportError as e:
#     print(f"[FLOATING UI] POM 2.0 not available ({e}), using fallback TTS")
#     PhonatoryOutputModule = None
#     pom_available = False
#     # Fallback TTS using pyttsx3 or similar
#     try:
#         import pyttsx3
#         fallback_tts_available = True
#     except ImportError:
#         fallback_tts_available = False
#         print("[FLOATING UI] No TTS available, text-only mode")

# For now, disable POM and use only fallback TTS
pom_available = False
try:
    import pyttsx3
    fallback_tts_available = True
    print("[FLOATING UI] Using fallback TTS (pyttsx3)")
except ImportError:
    fallback_tts_available = False
    print("[FLOATING UI] No TTS available, text-only mode")

class FloatingOrbUI:
    """
    The floating bubble that follows cursor, provides ORB access,
    and deploys resolution interface when needed.
    """

    def __init__(self):
        self.ui_root = Path(__file__).resolve().parents[3] / "CALI" / "orb" / "ui_overlay"

        # State
        self.is_visible = True  # Start visible by default
        self.cursor_position = (0, 0)
        self.active_application = None

        # ORB state tracking
        self.orb_state = {
            "status": "observing",  # observing | resolving | escalated
            "depth": 0.0,
            "tension": 0.0,
            "emergence_ready": False
        }

        # CALI SKG integration
        self.cali_skg = CALISKGEngine(Path(__file__).resolve().parents[3])

        # POM 2.0 speech synthesis (disabled)
        self.pom = None
        print("[FLOATING UI] POM 2.0 disabled, using fallback TTS")

        # Initialize pygame for audio playback
        pygame.mixer.init()

        # Browser overlay (if browser permission granted)
        self.browser_ws = None
        self.browser_port = 8765

        # UI command WebSocket
        self.ui_ws = None
        self.ui_port = 8766

        # Application tracking with auto-hide logic
        self.tracked_applications = {
            "auto_hide": {"youtube", "netflix", "vlc", "media player", "fullscreen"},
            "auto_show": {"worker", "goat", "dals", "terminal", "vscode"}
        }

    async def start_floating(self):
        """Start floating UI service"""
        print("[FLOATING UI] ORB UI initializing...")

        # Start WebSocket servers
        ui_server = await websockets.serve(self._handle_ui_commands, "localhost", 8766)
        browser_server = await websockets.serve(self._handle_browser_ws, "localhost", self.browser_port)

        print(f"[FLOATING UI] UI commands on ws://localhost:8766")
        print(f"[FLOATING UI] Browser integration on ws://localhost:{self.browser_port}")

        # Launch Electron app
        await self._launch_electron_app()

        # Show UI initially
        await self._show_ui()

        # Start cursor tracking loop
        await self._track_cursor_loop()

    async def _launch_electron_app(self):
        """Launch the Electron floating UI app"""
        import subprocess
        import os
        
        electron_dir = self.ui_root / "electron"
        
        try:
            # Launch electron app
            if os.name == 'nt':  # Windows
                subprocess.Popen(['electron.cmd', '.'], 
                               cwd=str(electron_dir),
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(['electron', '.'], 
                               cwd=str(electron_dir))
            
            print("[FLOATING UI] Electron app launched")
            await asyncio.sleep(2)  # Give electron time to start
            
        except Exception as e:
            print(f"[FLOATING UI] Failed to launch Electron app: {e}")
            print("[FLOATING UI] Continuing with WebSocket-only mode")

    async def _track_cursor_loop(self):
        """Track cursor position and active window with application awareness"""
        last_app = None

        while True:
            try:
                # Get cursor position
                self.cursor_position = pyautogui.position()

                # Get active window
                active_window = gw.getActiveWindow()
                if active_window:
                    current_app = {
                        "title": active_window.title,
                        "pid": getattr(active_window, 'pid', None),
                        "bounds": active_window.box._asdict() if hasattr(active_window, 'box') else None
                    }

                    # Check for application changes
                    if current_app["title"] != last_app:
                        await self._handle_application_change(current_app)
                        last_app = current_app["title"]

                    self.active_application = current_app

                # Update UI position based on cursor and active app
                await self._update_ui_position()

                # Small delay to prevent CPU overload
                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"[FLOATING UI] Cursor tracking error: {e}")
                await asyncio.sleep(1.0)

    async def _handle_application_change(self, app_info: Dict[str, Any]):
        """Handle application context changes for auto-hide/show"""
        app_title = app_info.get("title", "").lower()

        # Check auto-hide applications
        should_hide = any(hide_app in app_title for hide_app in self.tracked_applications["auto_hide"])

        # Check auto-show applications
        should_show = any(show_app in app_title for show_app in self.tracked_applications["auto_show"])

        if should_hide and self.is_visible:
            print(f"[FLOATING UI] Auto-hiding for application: {app_info.get('title')}")
            await self._hide_ui()

        elif should_show and not self.is_visible:
            print(f"[FLOATING UI] Auto-showing for application: {app_info.get('title')}")
            await self._show_ui()

    async def _update_ui_position(self):
        """Update ORB bubble position with smoothing and boundary checks"""
        if not self.is_visible:
            return

        # Position logic: follow cursor but with offset and inertia
        # Stay in periphery (e.g., top-right of cursor)
        offset_x = 50
        offset_y = -50

        target_x = self.cursor_position[0] + offset_x
        target_y = self.cursor_position[1] + offset_y

        # Get monitor bounds for the current cursor position
        try:
            # Try to get monitor info (requires screeninfo package)
            from screeninfo import get_monitors
            monitors = get_monitors()
            
            # Find which monitor contains the cursor
            cursor_monitor = None
            for monitor in monitors:
                if (monitor.x <= self.cursor_position[0] < monitor.x + monitor.width and
                    monitor.y <= self.cursor_position[1] < monitor.y + monitor.height):
                    cursor_monitor = monitor
                    break
            
            if cursor_monitor:
                # Keep within the monitor bounds where cursor is located
                monitor_left = cursor_monitor.x
                monitor_top = cursor_monitor.y
                monitor_right = cursor_monitor.x + cursor_monitor.width
                monitor_bottom = cursor_monitor.y + cursor_monitor.height
                
                target_x = max(monitor_left, min(target_x, monitor_right - 120))
                target_y = max(monitor_top, min(target_y, monitor_bottom - 120))
            else:
                # Fallback to primary screen if monitor detection fails
                screen_width, screen_height = pyautogui.size()
                target_x = max(0, min(target_x, screen_width - 120))
                target_y = max(0, min(target_y, screen_height - 120))
                
        except ImportError:
            # Fallback if screeninfo not available
            screen_width, screen_height = pyautogui.size()
            target_x = max(0, min(target_x, screen_width - 120))
            target_y = max(0, min(target_y, screen_height - 120))

        # Send position update to UI renderer (Electron)
        await self._send_ui_command({
            "command": "update_position",
            "x": target_x,
            "y": target_y,
            "application": self.active_application
        })

    async def update_orb_state(self, state: Dict[str, Any]):
        """Update ORB state and reflect in UI"""
        self.orb_state.update(state)

        # Send state update to UI
        await self._send_ui_command({
            "command": "update_state",
            "state": self.orb_state
        })

    async def _ensure_ui_connection(self):
        """Ensure UI WebSocket connection is active"""
        if not self.ui_ws or self.ui_ws.closed:
            print("[FLOATING UI] UI connection lost, attempting to reconnect...")
            # Connection will be re-established when Electron reconnects
            # For now, just log and continue
            pass

    async def deploy_resolution_interface(self, resolution_data: Dict[str, Any]):
        """Deploy resolution UI when worker escalates"""
        print(f"[FLOATING UI] Deploying resolution interface for worker {resolution_data.get('worker_id')}")

        # Show UI if hidden
        if not self.is_visible:
            await self._show_ui()

        # Update ORB state to resolving
        self.orb_state["status"] = "resolving"

        # Send resolution data to UI
        await self._send_ui_command({
            "command": "show_resolution",
            "data": resolution_data,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _show_ui(self):
        """Show floating ORB UI"""
        self.is_visible = True
        await self._send_ui_command({"command": "show"})

    async def _hide_ui(self):
        """Hide floating ORB UI"""
        self.is_visible = False
        await self._send_ui_command({"command": "hide"})

    async def _send_ui_command(self, command: Dict[str, Any]):
        """Send command to Electron UI via WebSocket"""
        if self.ui_ws and not self.ui_ws.closed:
            try:
                await self.ui_ws.send(json.dumps(command))
            except Exception as e:
                print(f"[FLOATING UI] Failed to send UI command: {e}")
                self.ui_ws = None  # Reset connection
        else:
            print(f"[UI COMMAND QUEUED] {json.dumps(command)} (Electron not connected)")

    async def _handle_browser_ws(self, websocket, path):
        """Handle browser WebSocket connections for dashboard reading"""
        self.browser_ws = websocket
        try:
            async for message in websocket:
                data = json.loads(message)
                await self._handle_browser_message(data)
        finally:
            self.browser_ws = None

    async def _handle_ui_commands(self, websocket, path):
        """Handle UI command WebSocket connections from Electron"""
        self.ui_ws = websocket
        try:
            async for message in websocket:
                data = json.loads(message)
                await self._handle_ui_message(data)
        finally:
            self.ui_ws = None

    async def _handle_ui_message(self, data: Dict[str, Any]):
        """Handle messages from Electron UI"""
        msg_type = data.get("type")

        if msg_type == "user_interaction":
            # User clicked the bubble
            await self._handle_bubble_click(data)

        elif msg_type == "resolution_response":
            # User responded to resolution interface
            await self._handle_resolution_response(data)

        elif msg_type == "permission_request":
            # UI requesting permission for something
            await self._handle_ui_permission_request(data)

    async def _handle_bubble_click(self, data: Dict[str, Any]):
        """Handle user clicking the ORB bubble"""
        print(f"[FLOATING UI] Bubble clicked - state: {data.get('state')}")

        # Update status to converging
        await self.update_orb_state({"status": "Converging"})
        await self._send_ui_command({"command": "update_status", "status": "Converging", "theme": "converging"})

        # Generate CALI greeting/response
        try:
            # Create a simple query for CALI
            user_query = "User has interacted with the ORB interface"

            # Get CALI response
            cali_response = self.cali_skg.generate_orb_response(user_query, {})

            # Generate speech if POM is available
            if "text" in cali_response and self.pom:
                response_text = cali_response["text"]
                print(f"[CALI VOICE] Generating speech: {response_text[:100]}...")

                # Generate audio file with POM 2.0
                import time
                audio_path = f"cali_response_{int(time.time())}.wav"

                try:
                    # Use POM to generate elegant female voice
                    generated_file = self.pom.phonate(
                        text=response_text,
                        out_path=audio_path,
                        pitch_factor=1.0,  # CALI's elegant female pitch
                        formant_target={"f1": 500, "f2": 1500},  # Female formants
                        articulation={"vowel": "a"},  # Natural articulation
                        nasalization={"level": 0.3}  # Slight nasal quality
                    )

                    print(f"[CALI VOICE] Speech generated: {generated_file}")

                    # Play the audio with pygame
                    pygame.mixer.music.load(generated_file)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)

                    print("[CALI VOICE] Speech playback completed")

                except Exception as e:
                    print(f"[CALI VOICE] POM speech generation failed: {e}")
                    # Fallback to simple TTS
                    self._fallback_speech(response_text)

            elif "text" in cali_response and fallback_tts_available:
                # Use fallback TTS
                response_text = cali_response["text"]
                self._fallback_speech(response_text)

            elif "text" in cali_response:
                # Fallback to text-only response
                print(f"[CALI TEXT] {cali_response['text']}")

        except Exception as e:
            print(f"[FLOATING UI] CALI interaction error: {e}")

        # Update status back to ready
        await self.update_orb_state({"status": "Ready"})
        await self._send_ui_command({"command": "update_status", "status": "Ready", "theme": "ready"})

    def _fallback_speech(self, text: str):
        """Fallback speech synthesis using pyttsx3"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            # Set female voice properties
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            engine.setProperty('rate', 180)  # Slightly slower for elegance
            engine.say(text)
            engine.runAndWait()
            print("[CALI VOICE] Fallback speech completed")
        except Exception as e:
            print(f"[CALI VOICE] Fallback speech failed: {e}")
            print(f"[CALI TEXT] {text}")

    async def process_user_query(self, query: str, context: Dict = {}):
        """Process user query using frozen SKG"""
        # Update status to converging
        await self.update_orb_state({"status": "Converging"})
        await self._send_ui_command({"command": "update_status", "status": "Converging", "theme": "converging"})

        try:
            # Use frozen SKG to generate response
            response = self.cali_skg.generate_orb_response(query, context)

            # Generate speech if available
            if response.get("text") and self.pom:
                response_text = response["text"]
                print(f"[CALI VOICE] Generating speech: {response_text[:100]}...")

                import time
                audio_path = f"cali_response_{int(time.time())}.wav"

                try:
                    generated_file = self.pom.phonate(
                        text=response_text,
                        out_path=audio_path,
                        pitch_factor=1.0,
                        formant_target={"f1": 500, "f2": 1500},
                        articulation={"vowel": "a"},
                        nasalization={"level": 0.3}
                    )

                    # Play with pygame
                    pygame.mixer.music.load(generated_file)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)

                    print("[CALI VOICE] Speech playback completed")

                except Exception as e:
                    print(f"[CALI VOICE] Speech generation failed: {e}")
                    print(f"[CALI TEXT] {response_text}")

            # Learn from interaction
            self.cali_skg.learn_from_user_feedback({"interaction_quality": "positive", "query_type": "informational"})

        except Exception as e:
            print(f"[FLOATING UI] Query processing error: {e}")

        # Update status back to ready
        await self.update_orb_state({"status": "Ready"})
        await self._send_ui_command({"command": "update_status", "status": "Ready", "theme": "ready"})

        return response

    async def _handle_resolution_response(self, data: Dict[str, Any]):
        """Handle user response to resolution interface"""
        action = data.get("action")
        resolution_data = data.get("resolution_data", {})

        print(f"[FLOATING UI] Resolution response: {action}")

        # Forward to resolution engine or escalation handler
        # This would integrate with the main ORB escalation pipeline

    async def _handle_ui_permission_request(self, data: Dict[str, Any]):
        """Handle permission requests from UI"""
        # UI might request permissions for various actions
        pass

    async def _handle_browser_message(self, data: Dict[str, Any]):
        """Handle messages from browser extension"""
        if data.get("type") == "dashboard_update":
            # Browser sent dashboard data (with user permission)
            dashboard_data = data.get("data", {})
            print(f"[BROWSER] Received dashboard update: {dashboard_data.keys()}")

            # Store in ORB context for resolution relevance
            await self._update_browser_context(dashboard_data)

        elif data.get("type") == "permission_request":
            # Handle permission request from browser
            await self._handle_permission_request(data)

    async def _update_browser_context(self, dashboard_data: Dict[str, Any]):
        """Update ORB's context with browser data"""
        # Store in a context file that resolution engine can access
        context_file = self.ui_root / "browser_context.json"
        with open(context_file, 'w') as f:
            json.dump({
                "data": dashboard_data,
                "last_update": datetime.utcnow().isoformat()
            }, f)

    async def _handle_permission_request(self, data: Dict[str, Any]):
        """Handle permission request from browser"""
        # Placeholder - in production, this would show a permission dialog
        print(f"[BROWSER] Permission request: {data}")

    def get_browser_context(self) -> Optional[Dict[str, Any]]:
        """Get browser context for resolution engine"""
        context_file = self.ui_root / "browser_context.json"
        if context_file.exists():
            with open(context_file, 'r') as f:
                return json.load(f)
        return None

# Singleton UI controller
FLOATING_UI = FloatingOrbUI()