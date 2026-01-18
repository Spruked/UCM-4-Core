#!/usr/bin/env python3
"""
Floating Assistant ORB - Legacy Interface
Redirects to unified Ontologically Recursive Bubble (ORB) implementation
"""

import sys
from pathlib import Path

# Import the unified ORB (Ontologically Recursive Bubble)
sys.path.append(str(Path(__file__).parent.parent))
from orb import OntologicallyRecursiveBubble

# Legacy compatibility - redirect to unified ORB
FloatingAssistantOrb = OntologicallyRecursiveBubble

if __name__ == "__main__":
    # Always redirect to unified ORB
    if len(sys.argv) > 1:
        repo_root = sys.argv[1]
    else:
        repo_root = str(Path(__file__).parent.parent.parent.resolve())

    print("🌀 Redirecting to unified Ontologically Recursive Bubble (ORB)...")
    orb = OntologicallyRecursiveBubble(repo_root=repo_root)
    orb.activate()
    for current_level in range(2, level + 1):
        scaling_factor = multiplier(current_level, sides)
        current_adjustment = radius * scaling_factor
        verts = generate_vertices(center, current_adjustment, sides)

        # For even sides, use vertex 0 (directly above center)
        if sides % 2 == 1:
            current_offset = np.array(midpoint(verts[0], verts[1])) - center3d
        else:
            current_offset = np.array(verts[0]) - center3d

        cumulative_offset += current_offset

    return center3d + cumulative_offset


def multiplier(level: int, sides: int) -> float:
    """Calculate radial scaling factor for symmetry points."""
    return 2 ** (level - 2) if sides % 2 == 0 else 1.5 ** (level - 2)


def generate_vertices(center, radius, sides):
    """Generate vertices for a regular polygon."""
    vertices = []
    angle = (2 * math.pi) / sides
    cx, cy = center

    for side in range(sides):
        theta = angle * side
        x = cx + radius * math.sin(theta)
        y = cy + radius * math.cos(theta)
        vertices.append((x, y, 0))

    return vertices


def midpoint(p1, p2):
    """Calculate midpoint between two 3D points."""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2)


def calculate_level_alpha(base_alpha: float, level: int, sides: int) -> float:
    """Calculate per-level alpha transparency."""
    if level == 1:
        return base_alpha
    return base_alpha / (1.2 * (sides ** (level / 2)))


def calculate_effective_alpha(sides: int, levels: int, base_alpha: float = 1.0) -> float:
    """Closed-form alpha calculation for multi-level overlays."""
    if levels < 1:
        return base_alpha

    mult_log = - (levels - 1) * math.log(1.2) - (math.log(sides) / 2) * ((levels * (levels + 1)) / 2 - 1)
    return base_alpha * math.exp(mult_log)


def estimate_max_overlaps(sides: int, levels: int) -> int:
    """Estimate maximum polygon overlaps for performance warnings."""
    if levels < 1:
        return 0
    overlaps = sides
    for level in range(2, levels + 1):
        overlaps += sides ** level
    return overlaps


def get_color_abbreviation(color_name: str) -> str:
    """Get standardized color abbreviation for symbolic codes."""
    color_map = {
        "White": "W", "Black": "Bl", "Red": "R", "Green": "G", "Blue": "B",
        "Yellow": "Y", "Pink": "Pi", "Purple": "P", "Orange": "O", "Cyan": "C",
        "Magenta": "M", "Lime": "Li", "Maroon": "Ma", "Navy": "Na",
        "Olive": "Ol", "Teal": "T", "Violet": "V", "Brown": "Br",
        "Gold": "Go", "Lightcoral": "Lc", "Darkkhaki": "Dk",
        "Darkgreen": "Dg", "Darkblue": "Db", "Darkred": "Dr",
        "Turquoise": "Tu", "Indigo": "In", "Darkorange": "Do",
        "Lightgreen": "Lg", "Tan": "Ta", "Salmon": "Sa",
        "Plum": "Pl", "Orchid": "Or", "Sienna": "Si",
        "Skyblue": "Sk", "Khaki": "K", "Slateblue": "Sb",
        "Goldenrod": "Gr", "Mediumblue": "Mb", "Greenyellow": "Gy",
        "Burlywood": "Bw", "Seagreen": "Sg", "Slategray": "Sg",
        "Cornflowerblue": "Cb", "Mediumorchid": "Mo", "Sandybrown": "Sb",
        "Tomato": "To", "Lightblue": "Lb", "Limegreen": "Lg",
        "Lightgrey": "Lg", "Lightpink": "Lp", "Thistle": "Th",
        "Palegreen": "Pg", "Azure": "Az", "Lavender": "Lv",
        "Honeydew": "Hd", "Mintcream": "Mc", "Aliceblue": "Ab"
    }
    standardized = color_name.capitalize()
    return color_map.get(standardized, color_name[:2].capitalize())


# ==================== HEADLESS ORB CLASS ====================

class FloatingAssistantOrb:
    """
    Headless HLSF-FFT Orb for KayGee Cognitive System
    Bridge-only mode - no GUI, no rendering
    """

    def __init__(self, repo_root: str, cali_state_hub: Any = None):
        self.repo_root = Path(repo_root)
        self.hub = cali_state_hub
        self.is_running = False

        # Spatial configuration
        self.config = {
            'center': [0.0, 0.0],
            'radius': 1.0,
            'sides': 4,
            'levels': 4,
            'alpha': 0.444,
            'rotation_speed': 5.0,
            'edges_only': True,
        }

        # Computational state
        self.vertices = np.array([])
        self.spatial_state = {}
        self.last_update = time.time()

        # Health metrics
        self.health_score = 1.0
        self.error_count = 0
        self.query_count = 0

        logger.info(f"FloatingAssistantOrb initialized (headless) - repo: {self.repo_root}")

    def start(self):
        """Start orb in headless bridge mode."""
        logger.info("Starting headless HLSF-FFT Orb...")
        self.is_running = True
        self._recompute_state()
        self._start_bridge()
        logger.info("✓ Headless orb active and listening")

    def _start_bridge(self):
        """Main bridge loop - JSON over stdin/stdout."""
        print(json.dumps({"type": "ready", "status": "headless_orb_active", "health": self.health_score}), flush=True)

        for line in sys.stdin:
            try:
                msg = json.loads(line.strip())

                if msg.get("type") == "query":
                    result = self.process_query(msg.get("text", ""), msg.get("session"))
                    print(json.dumps(result), flush=True)

                elif msg.get("type") == "config_update":
                    self.config.update(msg.get("config", {}))
                    self._recompute_state()
                    logger.info(f"Config updated: {msg.get('config', {})}")

                elif msg.get("type") == "status":
                    status = self.get_status()
                    print(json.dumps({"type": "status_response", "data": status}), flush=True)

                elif msg.get("type") == "shutdown":
                    logger.info("Shutdown requested via bridge")
                    break

            except json.JSONDecodeError:
                logger.error("Invalid JSON from bridge")
                print(json.dumps({"type": "error", "error": "invalid_json"}), flush=True)
            except Exception as e:
                logger.error(f"Bridge error: {e}", exc_info=True)
                print(json.dumps({"type": "error", "error": str(e)}), flush=True)
                self.error_count += 1
                self.health_score = max(0.0, self.health_score - 0.05)

    def stop(self):
        """Graceful shutdown."""
        logger.info("Stopping headless orb...")
        self.is_running = False
        logger.info("✓ Headless orb stopped")

    def process_query(self, text: str, session: Optional[str] = None) -> dict:
        """
        Process HLSF-FFT query through symbolic reasoning.
        This is the cognitive entry point.
        """
        try:
            self.query_count += 1

            sides_match = re.search(r'(\d+)\s*sides?', text or '', re.IGNORECASE)
            level_match = re.search(r'level\s*(\d+)', text or '', re.IGNORECASE)

            if sides_match:
                self.config['sides'] = max(3, int(sides_match.group(1)))
            if level_match:
                self.config['levels'] = max(0, int(level_match.group(1)))

            # Recompute spatial state
            self._recompute_state()

            # Generate symbolic code
            code = self._generate_symbolic_code()

            return {
                "type": "orb_result",
                "state": {
                    "sides": self.config['sides'],
                    "levels": self.config['levels'],
                    "alpha": self.config['alpha'],
                },
                "code": code,
                "spatial_state": self.spatial_state,
                "confidence": round(self.health_score, 3),
                "health": "ok" if self.is_healthy() else "degraded",
                "timestamp": time.time(),
                "session": session,
                "reasoning_path": ["hlsf_parse", "spatial_generation", "symbolic_encoding"],
                "skeptic_checks": 1,
            }

        except Exception as e:
            logger.error(f"Query processing failed: {e}", exc_info=True)
            self.error_count += 1
            self.health_score = max(0.0, self.health_score - 0.1)
            return {
                "type": "error",
                "error": str(e),
                "timestamp": time.time(),
                "session": session,
            }

    def _recompute_state(self):
        """Headless spatial state recomputation (no rendering)."""
        start_time = time.time()

        # Recompute vertices
        start_angle = math.pi / self.config['sides'] if self.config['sides'] % 2 != 0 else 0
        angles = np.linspace(start_angle, start_angle + 2 * math.pi,
                             self.config['sides'], endpoint=False)
        self.vertices = np.array([
            np.array(self.config['center']) + self.config['radius'] *
            np.array([math.cos(angle), math.sin(angle)]) for angle in angles
        ])

        # Compute symmetry points
        symmetry_points = []
        for level in range(1, self.config['levels'] + 1):
            point = calculate_symmetry_point_adjusted(
                self.config['center'], self.config['radius'],
                self.config['sides'], level
            )
            symmetry_points.append(point.tolist())

        # Estimate alpha for visibility
        effective_alpha = calculate_effective_alpha(
            self.config['sides'], self.config['levels'], self.config['alpha']
        )

        self.spatial_state = {
            'vertices': self.vertices.tolist(),
            'symmetry_points': symmetry_points,
            'effective_alpha': effective_alpha,
            'overlaps': estimate_max_overlaps(self.config['sides'], self.config['levels']),
            'compute_time_ms': (time.time() - start_time) * 1000
        }

        self.last_update = time.time()
        logger.debug(f"Spatial state recomputed: {len(symmetry_points)} levels")

    def _generate_symbolic_code(self) -> str:
        """Generate HLSF symbolic code string."""
        n = self.config['sides']
        radial_level = self.config['levels']
        level_code = f"O{n}CC{'' if radial_level > 0 else '0'}"

        if not self.config.get('edges_only', True):
            color_count = min(n // 2 - 1, len(DEFAULT_COLORS))
            color_abbr = "".join(get_color_abbreviation(c) for c in DEFAULT_COLORS[:color_count])
            code_string = f"{level_code}_{color_abbr}xx{radial_level}" if color_abbr else f"{level_code}xx{radial_level}"
        else:
            code_string = level_code

        return code_string

    # Health & Status API (for CALI integration)
    def is_healthy(self) -> bool:
        """Check if orb is operational."""
        return self.is_running and self.health_score > 0.6 and (time.time() - self.last_update) < 60

    def get_status(self) -> dict:
        """Get comprehensive status for monitoring."""
        return {
            "status": "running" if self.is_running else "stopped",
            "health_score": self.health_score,
            "error_count": self.error_count,
            "query_count": self.query_count,
            "last_update": self.last_update,
            "config": self.config,
            "spatial_state": self.spatial_state,
            "mode": "headless_bridge"
        }

    def get_component_status(self) -> dict:
        """Get component-level status."""
        return {
            "hlsf_engine": {
                "initialized": self.is_running,
                "status": {
                    "sides": self.config['sides'],
                    "levels": self.config['levels'],
                    "compute_time_ms": self.spatial_state.get('compute_time_ms', 0)
                },
                "last_update": self.last_update,
                "error_count": self.error_count,
                "confidence_score": self.health_score
            }
        }


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    # Always headless mode
    if len(sys.argv) > 1:
        repo_root = sys.argv[1]
    else:
        repo_root = str(Path(__file__).parent.parent.parent.resolve())

    orb = FloatingAssistantOrb(repo_root=repo_root)
    orb.start()