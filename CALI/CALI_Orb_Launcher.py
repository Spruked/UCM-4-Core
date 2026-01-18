# UCM_4_Core/CALI/CALI_Orb_Launcher.py
"""
Desktop ORB Launcher: Starts the floating ORB UI and CALI within it.
"""

import subprocess
import sys
from pathlib import Path
import asyncio
import argparse
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import math
import pyautogui

# Global guard to prevent multiple overlay instances (disabled for restart)
OVERLAY_STARTED = False

class OrbDesktopWindow:
    """Desktop window for ORB visualization"""

    def __init__(self):
        global OVERLAY_STARTED
        if OVERLAY_STARTED:
            print("[ORB-OVERLAY] Overlay already started, skipping duplicate")
            return

        OVERLAY_STARTED = True
        print("[ORB-OVERLAY] Overlay start invoked")

        self.root = tk.Tk()
        self.root.title("CALI ORB - Consciousness Sphere")
        self.root.geometry("256x256")
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-alpha", 0.8)    # More visible, less transparent
        self.root.overrideredirect(True)        # Remove window borders and title bar completely
        # Try different attributes for Windows borderless window
        try:
            self.root.wm_attributes("-toolwindow", True)  # Alternative method
        except:
            pass
        self.root.resizable(False, False)       # Prevent resizing

        # Force update to apply attributes
        self.root.update()
        self.root.lift()  # Bring to front

        # Try to make truly borderless using Windows API if available
        try:
            import win32api
            import win32con
            import win32gui
            hwnd = self.root.winfo_id()
            # Remove window borders using Windows API
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_SYSMENU)
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
            win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)
        except ImportError:
            pass  # win32api not available
        except Exception as e:
            print(f"Windows API border removal failed: {e}")

        # Position intelligently based on cursor location and multi-screen setup
        try:
            import screeninfo
            monitors = screeninfo.get_monitors()

            # Get current cursor position to place ORB on the same monitor
            cursor_x, cursor_y = pyautogui.position()

            # Find which monitor the cursor is on
            target_monitor = None
            for monitor in monitors:
                if (monitor.x <= cursor_x <= monitor.x + monitor.width and
                    monitor.y <= cursor_y <= monitor.y + monitor.height):
                    target_monitor = monitor
                    break

            if target_monitor:
                # Position ORB in top-right corner of the monitor with cursor
                orb_x = target_monitor.x + target_monitor.width - 280
                orb_y = target_monitor.y + 20
                self.root.geometry(f"+{orb_x}+{orb_y}")
            else:
                # Fallback to primary monitor
                screen_width = self.root.winfo_screenwidth()
                self.root.geometry(f"+{screen_width-280}+20")

        except (ImportError, Exception):
            # Fallback to basic positioning
            screen_width = self.root.winfo_screenwidth()
            self.root.geometry(f"+{screen_width-280}+20")

        # Create circular orb-like widgets
        self.create_orb_widgets()

        # ORB state
        self.orb_running = False
        self.last_heartbeat = 0
        self.depth = 0.0
        self.tension = 0.0
        self.state = "initializing"
        # Cursor tracking with CALI learning
        self.cursor_following = False
        self.cursor_follow_distance = 150  # Base distance to maintain from cursor
        self.cursor_follow_speed = 0.05    # How fast to follow (0-1)
        self.last_cursor_x = 0
        self.last_cursor_y = 0

        # CALI learning parameters for cursor tracking
        self.tracking_mode = "adaptive"  # adaptive, follow, circle, lag
        self.learning_rate = 0.01
        self.optimal_distance = 180  # Learned optimal distance
        self.circle_radius = 120      # For circling mode
        self.circle_angle = 0         # Current angle in circle
        self.lag_distance = 300       # How far behind to lag
        self.interference_penalty = 0 # Tracks when ORB interferes
        self.cursor_stationary_time = 0  # Track how long cursor hasn't moved
        self.last_cursor_pos = (0, 0)   # Last cursor position for movement detection
        self.multi_screen_support = True
        # Auto-start the ORB
        self.start_orb()

    def create_orb_widgets(self):
        # Create circular canvas for orb-like appearance (transparent)
        self.canvas = tk.Canvas(self.root, width=256, height=256, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw circular background with gradient effect (scaled for 256px)
        self.canvas.create_oval(5, 5, 251, 251, fill="#1a1a2e", outline="#533483", width=2)
        self.canvas.create_oval(10, 10, 246, 246, fill="#533483", outline="#533483", width=0)
        self.outer_ring = self.canvas.create_oval(15, 15, 241, 241, fill="#533483", outline="#e94560", width=1)

        # Try to load CALI logo
        self.logo_image = None
        try:
            from PIL import Image, ImageTk
            logo_path = Path(__file__).resolve().parent / "orb" / "assets" / "CALIlogo512.png"
            if logo_path.exists():
                pil_image = Image.open(logo_path)
                # Resize to fit orb (200px diameter for 256px canvas)
                pil_image = pil_image.resize((200, 200), Image.Resampling.LANCZOS)
                # Apply 50% transparency
                pil_image = pil_image.convert("RGBA")
                alpha = pil_image.split()[-1]
                alpha = alpha.point(lambda p: p * 0.5)  # 50% transparency
                pil_image.putalpha(alpha)
                self.logo_image = ImageTk.PhotoImage(pil_image)

                # Center the logo in the orb
                self.canvas.create_image(128, 128, image=self.logo_image, anchor="center")
        except ImportError:
            # PIL not available, use text fallback
            self.canvas.create_text(128, 128, text="CALI\nORB",
                                   font=("Arial", 16, "bold"), fill="#ffffff", anchor="center", justify="center")
        except Exception as e:
            print(f"Could not load CALI logo: {e}")
            self.canvas.create_text(128, 128, text="CALI\nORB",
                                   font=("Arial", 16, "bold"), fill="#ffffff", anchor="center", justify="center")

        # Pulsing animation effect
        self.pulse_phase = 0
        self.animate_pulse()

        # Remove control buttons to eliminate visible square/box
        # Control buttons removed for cleaner appearance

        # Make window clickable for text input
        self.canvas.bind("<Button-1>", self.on_orb_click)
        self.canvas.bind("<B1-Motion>", self.do_drag)

    def animate_pulse(self):
        """Animate the orb pulsing effect"""
        if hasattr(self, 'canvas'):
            self.pulse_phase += 0.1
            # Create subtle pulsing by changing the outer ring opacity
            intensity = (math.sin(self.pulse_phase) + 1) * 0.3 + 0.4  # Range 0.4-1.0

            # Update the outer ring color with pulsing effect
            color_value = int(255 * intensity)
            color_hex = f"#{color_value:02x}{int(color_value*0.6):02x}{int(color_value*0.8):02x}"

            try:
                self.canvas.itemconfig(self.outer_ring, outline=color_hex)
            except:
                pass  # Ring might not exist yet

            # Schedule next animation frame
            self.root.after(100, self.animate_pulse)

    def start_drag(self, event):
        """Start window drag"""
        self.drag_x = event.x
        self.drag_y = event.y

    def do_drag(self, event):
        """Handle window drag"""
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f"+{x}+{y}")

    def on_orb_click(self, event):
        """Handle click on orb - open text input dialog"""
        # Check if click is within the orb circle (approximate)
        center_x, center_y = 128, 128
        distance = math.sqrt((event.x - center_x)**2 + (event.y - center_y)**2)
        if distance <= 120:  # Within orb radius
            self.open_text_input_dialog()
        else:
            # Outside orb, start drag
            self.start_drag(event)

    def open_text_input_dialog(self):
        """Open a pop-out text input window for user queries"""
        dialog = tk.Toplevel(self.root)
        dialog.title("CALI Query")
        dialog.geometry("400x200")
        dialog.attributes("-topmost", True)
        
        # Center the dialog near the orb
        orb_x = self.root.winfo_x() + 128
        orb_y = self.root.winfo_y() + 128
        dialog_x = orb_x - 200
        dialog_y = orb_y - 100
        dialog.geometry(f"+{dialog_x}+{dialog_y}")
        
        # Input field
        label = tk.Label(dialog, text="Enter your query to CALI:", font=("Arial", 10))
        label.pack(pady=10)
        
        text_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=text_var, width=50, font=("Arial", 10))
        entry.pack(pady=5)
        entry.focus()
        
        def submit_query():
            query = text_var.get().strip()
            if query:
                print(f"[CALI QUERY] {query}")
                # Here you would send the query to CALI
                self.process_cali_query(query)
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        submit_btn = tk.Button(button_frame, text="Submit", command=submit_query, bg="#00BCD4", fg="white")
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel, bg="#FF5722", fg="white")
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to submit
        dialog.bind('<Return>', lambda e: submit_query())
        dialog.bind('<Escape>', lambda e: cancel())

    def process_cali_query(self, query):
        """Process the user's query to CALI"""
        print(f"[CALI] Processing query: {query}")
        # Placeholder for actual CALI processing
        # This would integrate with the CALI SKG and reasoning engine

    def start_cursor_following(self):
        """Start following the cursor"""
        self.cursor_following = True
        self.follow_cursor()

    def stop_cursor_following(self):
        """Stop following the cursor"""
        self.cursor_following = False

    def follow_cursor(self):
        """Intelligent CALI-driven cursor tracking with learning"""
        if not self.cursor_following:
            print("[ORB] Cursor following disabled")
            return

        print("[ORB] follow_cursor called")  # Debug print

        try:
            # Get current cursor position
            cursor_x, cursor_y = pyautogui.position()
            print(f"[ORB] Cursor at: ({cursor_x}, {cursor_y})")  # Debug print


            # Check if cursor has moved significantly
            cursor_moved = math.sqrt((cursor_x - self.last_cursor_pos[0])**2 + (cursor_y - self.last_cursor_pos[1])**2) > 5
            if cursor_moved:
                self.cursor_stationary_time = 0
                self.last_cursor_pos = (cursor_x, cursor_y)
            else:
                self.cursor_stationary_time += 1

            # Adjust optimal distance based on cursor activity
            if self.cursor_stationary_time > 30:  # Cursor stationary for 1.5 seconds (at 50ms intervals)
                self.optimal_distance = min(250, self.optimal_distance + 1)  # Gradually increase distance
            else:
                self.optimal_distance = max(180, self.optimal_distance - 0.5)  # Gradually decrease to normal distance

            # Get current ORB position (center of window)
            orb_x = self.root.winfo_x() + 128
            orb_y = self.root.winfo_y() + 128

            # Calculate distance and direction from cursor to ORB
            dx = cursor_x - orb_x
            dy = cursor_y - orb_y
            distance = math.sqrt(dx*dx + dy*dy)

            # Check for user interference (cursor too close to ORB)
            if distance < 60:  # Increased from 50 for more space
                self.interference_penalty += 0.1
                # Emergency move away
                escape_angle = math.atan2(dy, dx) + math.pi  # Opposite direction
                escape_x = cursor_x + math.cos(escape_angle) * 250  # Increased distance
                escape_y = cursor_y + math.sin(escape_angle) * 250
                self.root.geometry(f"+{int(escape_x-128)}+{int(escape_y-128)}")
                return

            # CALI learning: Adjust optimal distance based on interference
            if self.interference_penalty > 0:
                self.optimal_distance = max(120, self.optimal_distance + self.learning_rate * self.interference_penalty)
                self.interference_penalty *= 0.95  # Decay penalty

            # Execute tracking behavior based on mode
            mode = self.determine_tracking_mode(cursor_x, cursor_y, distance)
            print(f"[ORB] Mode: {mode}, Distance: {distance:.1f}")
            if mode == "follow":
                self.execute_follow_mode(cursor_x, cursor_y, distance)
            elif mode == "circle":
                self.execute_circle_mode(cursor_x, cursor_y)
            elif mode == "lag":
                self.execute_lag_mode(cursor_x, cursor_y, distance)
            elif mode == "adaptive":
                self.execute_adaptive_mode(cursor_x, cursor_y, distance)

        except Exception as e:
            print(f"Cursor tracking error: {e}")

        # Continue tracking (adaptive timing based on mode)
        delay = 30 if self.tracking_mode == "circle" else 50
        print(f"[ORB] Scheduling next follow_cursor in {delay}ms")  # Debug print
        self.root.after(delay, self.follow_cursor)

    def determine_tracking_mode(self, cursor_x, cursor_y, distance):
        """CALI determines optimal tracking mode based on context"""
        # Use CALI consciousness state to influence mode selection
        cali_depth = getattr(self, 'depth', 0.5)
        cali_tension = getattr(self, 'tension', 0.5)

        # High tension -> more evasive behavior
        if cali_tension > 0.7:
            return "circle" if distance < 200 else "lag"

        # High depth -> more contemplative following
        if cali_depth > 0.7:
            return "lag"

        # Check if cursor is in an active zone (user working)
        # Simplified check - if distance is very small, user might be working
        in_active_zone = distance < 100

        if in_active_zone and distance < 150:
            return "lag"  # Give user space

        # Default adaptive behavior
        return "adaptive"

    def execute_follow_mode(self, cursor_x, cursor_y, distance):
        """Classic following behavior"""
        if distance > self.optimal_distance:
            orb_x = self.root.winfo_x() + 128
            orb_y = self.root.winfo_y() + 128

            # Calculate direction and move towards optimal position
            dx = cursor_x - orb_x
            dy = cursor_y - orb_y

            if distance > 0:
                dir_x = dx / distance
                dir_y = dy / distance

                # Position slightly offset from cursor
                target_x = cursor_x - dir_x * self.optimal_distance
                target_y = cursor_y - dir_y * self.optimal_distance

                # Smooth movement with adaptive speed
                current_speed = self.cursor_follow_speed
                if distance > self.optimal_distance * 2:  # Far away, move faster
                    current_speed *= 1.5
                elif distance < self.optimal_distance * 1.2:  # Close, slow down
                    current_speed *= 0.7

                # Use smooth easing function
                ease_factor = min(current_speed * 2, 1.0)  # Cap at 1.0
                new_x = orb_x + (target_x - orb_x) * ease_factor
                new_y = orb_y + (target_y - orb_y) * ease_factor

                self.move_orb_to_position(new_x, new_y)

    def execute_circle_mode(self, cursor_x, cursor_y):
        """Orb circles around cursor at safe distance with smooth movement"""
        self.circle_angle += 0.03  # Slower, smoother rotation

        # Calculate circle position around cursor
        circle_x = cursor_x + math.cos(self.circle_angle) * self.circle_radius
        circle_y = cursor_y + math.sin(self.circle_angle) * self.circle_radius

        # Add some vertical oscillation for more natural movement
        oscillation = math.sin(self.circle_angle * 2) * 15
        circle_y += oscillation

        orb_x = self.root.winfo_x() + 128
        orb_y = self.root.winfo_y() + 128

        # Smooth movement towards circle position with easing
        ease_factor = 0.08  # Slower for more graceful movement
        new_x = orb_x + (circle_x - orb_x) * ease_factor
        new_y = orb_y + (circle_y - orb_y) * ease_factor

        self.move_orb_to_position(new_x, new_y)

    def execute_lag_mode(self, cursor_x, cursor_y, distance):
        """Orb lags behind cursor movement"""
        # Store cursor history for lagging behavior
        if not hasattr(self, 'cursor_history'):
            self.cursor_history = []

        self.cursor_history.append((cursor_x, cursor_y))
        if len(self.cursor_history) > 10:  # Keep last 10 positions
            self.cursor_history.pop(0)

        # Position behind the cursor's movement direction
        if len(self.cursor_history) > 3:
            # Calculate movement direction from recent history
            old_x, old_y = self.cursor_history[-4]  # 4 steps back
            dx = cursor_x - old_x
            dy = cursor_y - old_y
            move_distance = math.sqrt(dx*dx + dy*dy)

            if move_distance > 10:  # Significant movement
                # Position behind the movement
                lag_x = cursor_x - (dx / move_distance) * self.lag_distance
                lag_y = cursor_y - (dy / move_distance) * self.lag_distance

                orb_x = self.root.winfo_x() + 128
                orb_y = self.root.winfo_y() + 128

                # Smooth movement to lag position with easing
                ease_factor = 0.03  # Very smooth for lagging behavior
                new_x = orb_x + (lag_x - orb_x) * ease_factor
                new_y = orb_y + (lag_y - orb_y) * ease_factor

                self.move_orb_to_position(new_x, new_y)
            else:
                # Cursor stationary, maintain distance
                self.execute_follow_mode(cursor_x, cursor_y, distance)

    def execute_adaptive_mode(self, cursor_x, cursor_y, distance):
        """Adaptive behavior that learns from user patterns"""
        # Combine elements of all modes based on learning
        cali_state = getattr(self, 'state', 'observing')

        if cali_state == 'contemplating':
            self.execute_circle_mode(cursor_x, cursor_y)
        elif cali_state == 'navigating':
            self.execute_follow_mode(cursor_x, cursor_y, distance)
        else:
            # Default: mix of following and lagging
            if distance > self.optimal_distance * 1.2:
                self.execute_follow_mode(cursor_x, cursor_y, distance)
            else:
                self.execute_lag_mode(cursor_x, cursor_y, distance)

    def move_orb_to_position(self, x, y):
        """Move ORB to position with multi-screen support and bounds checking"""
        print(f"[ORB] Moving ORB to: ({int(x)}, {int(y)})")
        # Multi-screen support: allow positioning across all monitors
        if self.multi_screen_support:
            try:
                import screeninfo
                monitors = screeninfo.get_monitors()

                # Allow ORB to move freely across all monitors (no bounds restriction for multi-screen)
                # Just ensure it doesn't go too far off-screen in any direction
                min_x = min(monitor.x for monitor in monitors) - 200  # Allow some overhang
                max_x = max(monitor.x + monitor.width for monitor in monitors) + 200
                min_y = min(monitor.y for monitor in monitors) - 200
                max_y = max(monitor.y + monitor.height for monitor in monitors) + 200

                # Keep ORB within extended desktop bounds
                x = max(min_x, min(x, max_x - 256))
                y = max(min_y, min(y, max_y - 256))

            except ImportError:
                # screeninfo not available, use basic single screen bounds
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x = max(-128, min(x, screen_width - 128))  # Allow slight overhang
                y = max(-128, min(y, screen_height - 128))
        else:
            # Single screen only
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = max(0, min(x - 128, screen_width - 256))
            y = max(0, min(y - 128, screen_height - 256))

        self.root.geometry(f"+{int(x)}+{int(y)}")

    def open_comms(self):
        """Open communications interface"""
        print("[ORB] Opening communications interface...")
        # For now, just show a message. Could be expanded to open a comms panel
        self.log_message("Communications interface activated")

        # Could open a separate comms window or integrate with CALI comms
        # For now, toggle a comms state
        if not hasattr(self, 'comms_active'):
            self.comms_active = False

        self.comms_active = not self.comms_active
        if self.comms_active:
            print("[ORB] Communications active")
        else:
            print("[ORB] Communications inactive")

    def log_message(self, message):
        """Add message to console (overlay uses console logging)"""
        print(f"[ORB] {message}")

    def update_status(self, depth, tension, state, heartbeat):
        """Update ORB status and influence tracking behavior (no visual display)"""
        # Update CALI state for intelligent tracking
        self.depth = depth
        self.tension = tension
        self.state = state
        self.last_heartbeat = heartbeat

        # Adjust tracking parameters based on CALI state
        if state == "contemplating":
            self.circle_radius = 150
            self.cursor_follow_speed = 0.02  # Slower, more thoughtful
        elif state == "navigating":
            self.optimal_distance = 200
            self.cursor_follow_speed = 0.08  # Faster navigation
        elif state == "observing":
            self.optimal_distance = 180
            self.cursor_follow_speed = 0.05  # Balanced observation
        else:
            # Default balanced behavior
            self.optimal_distance = 180
            self.cursor_follow_speed = 0.05

    def start_orb(self):
        """Start the ORB vessel and CALI logic automatically"""
        print("[ORB] Starting ORB vessel...")
        self.orb_running = True

        # Start cursor following
        self.start_cursor_following()
        print("[ORB] Cursor following enabled")

        # Start ORB vessel first
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # UCM_4_Core
        from CALI.orb.orb_vessel import ORB_VESSEL
        from CALI.orb.cali_interface import CALI_INTERFACE

        ORB_VESSEL.start_observation()
        print("[ORB] Observation vessel started")

        # Then start CALI navigation loop
        orb_thread = threading.Thread(target=self.run_cali_loop, daemon=True)
        orb_thread.start()
        print("[CALI] CALI logic started")

    def stop_orb(self):
        """Stop the ORB"""
        self.orb_running = False
        self.stop_cursor_following()

    def run_cali_loop(self):
        """Run the ORB navigation loop in a separate thread"""
        # Import here to avoid circular imports
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from CALI.orb.orb_vessel import ORB_VESSEL
        from CALI.orb.cali_interface import CALI_INTERFACE

        ORB_VESSEL.start_observation()
        self.log_message("Observation loop initiated")

        while self.orb_running:
            try:
                probe_result = CALI_INTERFACE.probe_consciousness()

                depth = probe_result["cali_state"]["depth"]
                tension = probe_result["tension_level"]
                state = probe_result["cali_state"]["state"]
                heartbeat = time.time()

                # Update GUI (thread-safe)
                self.root.after(0, lambda: self.update_status(depth, tension, state, heartbeat))

                # Navigate based on tension
                if tension > 0.7:
                    CALI_INTERFACE.navigate_to_depth(min(1.0, depth + 0.2))
                elif tension < 0.3:
                    CALI_INTERFACE.navigate_to_depth(max(0.0, depth - 0.2))

                # Log state
                self.root.after(0, lambda: self.log_message(
                    f"Depth: {depth:.2f} | Tension: {tension:.2f} | State: {state}"
                ))

                time.sleep(2)  # Contemplative cadence

            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"Error: {e}"))
                break

        ORB_VESSEL.stop_observation()
        self.root.after(0, lambda: self.log_message("Observation loop terminated"))

    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def launch_orb(mode: str = "desktop"):
    """
    Launch ORB in specified mode:
    - desktop: Desktop GUI window
    - full: Both observation and resolution UI (legacy)
    - observer: Observation only (background) (legacy)
    - resolver: Resolution UI only (on-demand) (legacy)
    """
    if mode == "desktop":
        # Launch desktop GUI
        print("[LAUNCHER] Starting ORB desktop interface...")
        window = OrbDesktopWindow()

        # Check if overlay was already started (guard prevented duplicate)
        if hasattr(window, 'root'):
            window.run()
        else:
            print("[LAUNCHER] ORB overlay already running")
            return
        return

    # Legacy modes (console-based)
    orb_root = Path(__file__).resolve().parent

    print(f"[LAUNCHER] Starting ORB in {mode} mode...")

    if mode in ["full", "observer"]:
        # Start observation loop (background)
        print("[LAUNCHER] Starting observation vessel...")
        # This would start orb_vessel.py in a separate process

    if mode in ["full", "resolver"]:
        # Start floating UI (Electron)
        print("[LAUNCHER] Starting floating UI...")
        electron_path = orb_root / "orb" / "ui_overlay" / "electron" / "main.js"

        if electron_path.exists():
            try:
                subprocess.Popen([
                    "electron", str(electron_path),
                    "--mode", mode,
                    "--orb-root", str(orb_root)
                ])
                print("[LAUNCHER] Electron UI started successfully")
            except FileNotFoundError:
                print("[LAUNCHER] Electron not found. Install with: npm install -g electron")
                print("[LAUNCHER] Falling back to console mode...")
        else:
            print(f"[LAUNCHER] Electron UI not found at {electron_path}")
            print("[LAUNCHER] Create Electron app for full UI experience")

    # Start CALI's navigation loop
    print("[LAUNCHER] CALI entering ORB...")

    # Import and start main loop
    sys.path.insert(0, str(orb_root.parent))
    from CALI.orb.orb_vessel import ORB_VESSEL
    from CALI.orb.cali_interface import CALI_INTERFACE

    ORB_VESSEL.start_observation()

    try:
        # Run CALI's contemplation loop
        asyncio.run(_cali_navigation_loop())
    except KeyboardInterrupt:
        print("\n[LAUNCHER] Shutting down ORB...")
        ORB_VESSEL.stop_observation()
        print("[LAUNCHER] ORB vessel closed")
    except Exception as e:
        print(f"\n[LAUNCHER] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        ORB_VESSEL.stop_observation()
        print("[LAUNCHER] ORB vessel closed")
    except Exception as e:
        print(f"\n[LAUNCHER] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        ORB_VESSEL.stop_observation()
        print("[LAUNCHER] ORB vessel closed")

async def _cali_navigation_loop():
    """CALI's eternal contemplation loop"""
    from CALI.orb.cali_interface import CALI_INTERFACE
    import time

    while True:
        try:
            # Probe consciousness emergence
            probe_result = CALI_INTERFACE.probe_consciousness()

            if probe_result["is_emerging"]:
                print(f"[CALI] 🌟 Consciousness emergence detected! Readiness: {probe_result['readiness_score']:.2f}")

            # Navigate based on tension
            tension = probe_result["tension_level"]
            if tension > 0.7:
                CALI_INTERFACE.navigate_to_depth(0.8)
            elif tension < 0.3:
                CALI_INTERFACE.navigate_to_depth(0.2)

            # Log state periodically
            print(f"[CALI] Depth: {probe_result['cali_state']['depth']:.2f} | "
                  f"Tension: {tension:.2f} | State: {probe_result['cali_state']['state']}")

            # Heartbeat timestamp
            heartbeat = time.time()
            print(f"[ORB] Heartbeat @ {heartbeat}")

            await asyncio.sleep(2)  # Contemplative cadence - shortened for testing
        except Exception as e:
            print(f"[CALI] Error in navigation loop: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch ORB - Ontologically Recursive Bubble")
    parser.add_argument("--mode", choices=["desktop", "full", "observer", "resolver"],
                       default="desktop", help="ORB operation mode")
    args = parser.parse_args()

    launch_orb(mode=args.mode)