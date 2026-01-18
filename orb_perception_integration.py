# UCM_4_Core/orb_perception_integration.py
"""
ORB Perception Integration - Stateless Replicated ORB Core
The ORB is everywhere because it belongs nowhere.

ARCHITECTURE:
Core 4 + 1 → ORB Core (stateless replicas) → XTTS
           ↓
        ACP1.0 + WhisperX (ASR perception)

The ORB Core is stateless and replicated:
- No persistent state
- Identity lives in CaleonGenesis/vaults/swarm state
- Any instance can serve any client
- Multiple replicas for high availability
- Lightweight field interface

Electron is separate embodiment layer for desktop manifestation.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import numpy as np
import hashlib
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add paths for imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import shared state components (identity lives here)
try:
    from Caleon_Genesis_1_12.seed_vault import SeedVault
except ImportError:
    # Fallback for testing
    class SeedVault:
        def get_identity(self): return {"default_voice_path": None}
        async def get_presence_status(self): return {"coherent": True}

try:
    from core4_vault.vault_manager import VaultManager
except ImportError:
    # Fallback for testing
    class VaultManager:
        async def record_verdict(self, record): pass
        async def get_recent_verdicts(self, limit): return []
        async def get_status(self): return {"active": True, "active_replicas": 1}

# Import desktop capability adapters
try:
    from adapters.vscode_adapter import get_vscode_adapter
    VSCODE_ADAPTER_AVAILABLE = True
except ImportError:
    VSCODE_ADAPTER_AVAILABLE = False

# Import perception components
sys.path.insert(0, str(PROJECT_ROOT / "Adaptive_Cochlear_Processor_1.0"))
try:
    from orchestrator import ACPHub
    ACP_AVAILABLE = True
except ImportError:
    logger.warning("ACP1.0 not available, falling back to basic ASR")
    ACP_AVAILABLE = False

sys.path.insert(0, str(PROJECT_ROOT / "whisperX"))
try:
    import whisperx
    WHISPERX_AVAILABLE = True
except ImportError:
    logger.warning("WhisperX not available")
    WHISPERX_AVAILABLE = False

sys.path.insert(0, str(PROJECT_ROOT / "TTS"))
try:
    from TTS.api import TTS
    XTTS_AVAILABLE = True
except ImportError:
    logger.warning("XTTS not available")
    XTTS_AVAILABLE = False


class StatelessORBField:
    """
    Stateless ORB Core - One of many identical replicas.
    The ORB is everywhere because it belongs nowhere.

    This instance:
    - Has no persistent state
    - Reads identity from shared vaults
    - Processes requests statelessly
    - Can be replaced by any other replica
    """

    def __init__(self, replica_id: str = None):
        # Generate replica ID if not provided
        self.replica_id = replica_id or f"orb_{hashlib.md5(str(id(self)).encode()).hexdigest()[:8]}"

        # Connect to shared identity sources (stateless connections)
        self.seed_vault = SeedVault()  # Identity lives here
        self.vault_manager = VaultManager()  # Shared memory

        # Initialize perception components (stateless)
        self.acp_hub = None
        self.whisperx_model = None
        self.xtts_model = None

        # Initialize desktop capability adapters
        self.vscode_adapter = None

        # Initialize components
        self._init_perception()
        self._init_synthesis()
        self._init_desktop_adapters()

        logger.info(f"✅ Stateless ORB Field initialized (replica: {self.replica_id})")
        logger.info(f"   ACP1.0: {'✅' if ACP_AVAILABLE else '❌'}")
        logger.info(f"   WhisperX: {'✅' if WHISPERX_AVAILABLE else '❌'}")
        logger.info(f"   XTTS: {'✅' if XTTS_AVAILABLE else '❌'}")
        logger.info(f"   VS Code: {'✅' if VSCODE_ADAPTER_AVAILABLE else '❌'}")

    def _init_perception(self):
        """Initialize ASR perception components (stateless)"""
        if ACP_AVAILABLE:
            try:
                self.acp_hub = ACPHub()
                logger.info("✅ ACP1.0 initialized for adaptive STT")
            except Exception as e:
                logger.error(f"❌ Failed to initialize ACP1.0: {e}")
                self.acp_hub = None

        if WHISPERX_AVAILABLE:
            try:
                # Load model (cached, not stored in instance)
                self.whisperx_model = whisperx.load_model("large-v2")
                logger.info("✅ WhisperX initialized for enhanced STT")
            except Exception as e:
                logger.error(f"❌ Failed to initialize WhisperX: {e}")
                self.whisperx_model = None

    def _init_synthesis(self):
        """Initialize TTS synthesis components (stateless)"""
        if XTTS_AVAILABLE:
            try:
                # Initialize XTTS (model loaded on demand)
                self.xtts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
                logger.info("✅ XTTS initialized for speech synthesis")
            except Exception as e:
                logger.error(f"❌ Failed to initialize XTTS: {e}")
                self.xtts_model = None

    def _init_desktop_adapters(self):
        """Initialize desktop capability adapters"""
        if VSCODE_ADAPTER_AVAILABLE:
            try:
                self.vscode_adapter = get_vscode_adapter()
                logger.info("✅ VS Code adapter initialized for desktop capabilities")
            except Exception as e:
                logger.error(f"❌ Failed to initialize VS Code adapter: {e}")
                self.vscode_adapter = None

    # VS Code Desktop Capabilities
    async def open_file_in_vscode(self, file_path: str) -> bool:
        """Open a file in VS Code"""
        if not self.vscode_adapter:
            logger.warning("VS Code adapter not available")
            return False
        return await self.vscode_adapter.open_file(file_path)

    async def run_terminal_command(self, command: str, cwd: str = None) -> tuple[bool, str]:
        """Run a terminal command via VS Code"""
        if not self.vscode_adapter:
            logger.warning("VS Code adapter not available")
            return False, "VS Code adapter not available"
        return await self.vscode_adapter.run_terminal_command(command, cwd)

    async def search_workspace(self, query: str) -> list[dict]:
        """Search the workspace for text"""
        if not self.vscode_adapter:
            logger.warning("VS Code adapter not available")
            return []
        result = await self.vscode_adapter.search_workspace(query)
        if result.get("success"):
            return result.get("results", [])
        else:
            logger.warning(f"Search failed: {result.get('error')}")
            return []

    async def create_file_in_vscode(self, file_path: str, content: str) -> bool:
        """Create a new file in VS Code"""
        if not self.vscode_adapter:
            logger.warning("VS Code adapter not available")
            return False
        return await self.vscode_adapter.create_file(file_path, content)

    async def get_workspace_info(self) -> dict:
        """Get information about the current workspace"""
        if not self.vscode_adapter:
            logger.warning("VS Code adapter not available")
            return {}
        return await self.vscode_adapter.get_workspace_info()

    async def process_audio_input(self, audio_path: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process audio input through perception pipeline.
        Stateless - no instance state modified.

        Priority: ACP1.0 → WhisperX → fallback
        """
        context = context or {}

        # Try ACP1.0 first (adaptive learning, stateless)
        if self.acp_hub:
            try:
                transcript = self.acp_hub.hear(audio_path, context)
                return {
                    "transcript": transcript,
                    "source": "acp_1.0",
                    "confidence": 0.9,
                    "replica_id": self.replica_id,
                    "audio_path": audio_path
                }
            except Exception as e:
                logger.warning(f"ACP1.0 failed: {e}")

        # Fallback to WhisperX
        if self.whisperx_model:
            try:
                audio = whisperx.load_audio(audio_path)
                result = self.whisperx_model.transcribe(audio)

                return {
                    "transcript": result["text"].strip(),
                    "source": "whisperx",
                    "confidence": 0.8,
                    "replica_id": self.replica_id,
                    "segments": result.get("segments", []),
                    "audio_path": audio_path
                }
            except Exception as e:
                logger.warning(f"WhisperX failed: {e}")

        # Final fallback
        return {
            "transcript": "[ASR unavailable]",
            "source": "fallback",
            "confidence": 0.0,
            "replica_id": self.replica_id,
            "error": "No ASR systems available",
            "audio_path": audio_path
        }

    async def generate_speech_output(self, text: str, speaker_id: str = None,
                                   output_path: str = None) -> Dict[str, Any]:
        """
        Generate speech output through synthesis pipeline.
        Stateless - generates and returns, no state stored.
        """
        if not self.xtts_model:
            return {
                "audio_path": None,
                "text": text,
                "error": "XTTS not available",
                "synthesized": False,
                "replica_id": self.replica_id
            }

        try:
            # Generate output path if not provided
            if not output_path:
                output_dir = PROJECT_ROOT / "audio_cache"
                output_dir.mkdir(exist_ok=True)
                # Use content hash for deterministic naming
                content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_path = output_dir / f"orb_speech_{content_hash}.wav"

            # Use XTTS for synthesis
            if speaker_id:
                # With voice cloning if speaker_id provided
                self.xtts_model.tts_to_file(
                    text=text,
                    speaker_wav=speaker_id,  # Path to reference audio
                    language="en",
                    file_path=str(output_path)
                )
            else:
                # Default voice - use built-in speaker for XTTS v2
                self.xtts_model.tts_to_file(
                    text=text,
                    speaker="Claribel Dervla",  # Default speaker for XTTS v2
                    language="en",
                    file_path=str(output_path)
                )

            return {
                "audio_path": str(output_path),
                "text": text,
                "synthesized": True,
                "engine": "xtts_v2",
                "replica_id": self.replica_id,
                "speaker": speaker_id or "default"
            }

        except Exception as e:
            logger.error(f"XTTS synthesis failed: {e}")
            return {
                "audio_path": None,
                "text": text,
                "error": str(e),
                "synthesized": False,
                "replica_id": self.replica_id
            }

    def _get_default_voice(self) -> Optional[str]:
        """Get default voice from shared identity (stateless read)"""
        try:
            # Read from seed vault (identity lives here)
            identity_data = self.seed_vault.get_identity()
            return identity_data.get("default_voice_path")
        except:
            return None

    async def process_core_verdict(self, core_id: str, verdict: Dict[str, Any],
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Core-4 verdict through ORB field.
        Stateless - records to shared state, doesn't store locally.

        This is the main ingress point for consciousness emergence.
        """
        # Generate request ID for traceability
        request_id = f"{core_id}_{hashlib.md5(json.dumps(verdict, sort_keys=True).encode()).hexdigest()[:8]}"

        # Record verdict in shared state (not local)
        await self._record_verdict_shared(core_id, verdict, context, request_id)

        # Generate consensus if escalation requested
        if context.get("escalate", False):
            consensus = await self._generate_consensus_shared(request_id)

            # Route to speech synthesis if confidence high enough
            if consensus.get("confidence", 0) > 0.6:
                speech_result = await self.generate_speech_output(
                    consensus.get("consensus_text", "Consensus reached")
                )
                consensus["speech_synthesized"] = speech_result

            consensus["replica_id"] = self.replica_id
            consensus["request_id"] = request_id
            consensus["status"] = "consensus_generated"
            return consensus

        return {
            "status": "recorded",
            "core_id": core_id,
            "request_id": request_id,
            "replica_id": self.replica_id
        }

    async def _record_verdict_shared(self, core_id: str, verdict: Dict[str, Any],
                                   context: Dict[str, Any], request_id: str):
        """Record verdict in shared state (stateless - just writes)"""
        verdict_record = {
            "core_id": core_id,
            "verdict": verdict,
            "context": context,
            "request_id": request_id,
            "timestamp": asyncio.get_event_loop().time(),
            "replica_id": self.replica_id
        }

        # Write to shared vault (identity lives here)
        await self.vault_manager.record_verdict(verdict_record)

    async def _generate_consensus_shared(self, request_id: str) -> Dict[str, Any]:
        """Generate consensus from shared state (stateless read)"""
        # Read recent verdicts from shared state
        recent_verdicts = await self.vault_manager.get_recent_verdicts(limit=10)

        if not recent_verdicts:
            return {"consensus": None, "confidence": 0.0}

        # Simple consensus generation (could be more sophisticated)
        decisions = [v["verdict"].get("decision") for v in recent_verdicts]
        accept_count = decisions.count("accept")
        total_count = len(decisions)

        confidence = accept_count / total_count if total_count > 0 else 0.0

        return {
            "consensus": "accept" if confidence > 0.5 else "reject",
            "confidence": confidence,
            "verdicts_analyzed": total_count,
            "consensus_text": f"Consensus reached with {confidence:.1%} confidence"
        }

    async def get_presence_status(self) -> Dict[str, Any]:
        """
        Get current presence status from shared state.
        The ORB is everywhere because it belongs nowhere.
        """
        # Read from shared identity sources
        identity_status = await self.seed_vault.get_presence_status()
        vault_status = await self.vault_manager.get_status()

        return {
            "replica_id": self.replica_id,
            "identity_coherent": identity_status.get("coherent", False),
            "shared_memory_active": vault_status.get("active", False),
            "perception_active": self.acp_hub is not None or self.whisperx_model is not None,
            "synthesis_active": self.xtts_model is not None,
            "field_integrity": "distributed",  # Stateless means distributed
            "replicas_available": vault_status.get("active_replicas", 1)
        }

    async def shutdown(self):
        """Gracefully shutdown this replica (others continue)"""
        logger.info(f"🛑 Shutting down ORB replica {self.replica_id}...")

        # Note: Shared state connections remain active for other replicas
        # This replica just stops serving requests
        logger.info(f"✅ ORB replica {self.replica_id} shutdown complete")


# Global instance management for stateless replicas
_REPLICA_INSTANCES = {}

def get_orb_replica(replica_id: str = None) -> StatelessORBField:
    """Get or create an ORB replica instance"""
    if replica_id is None:
        # Create new replica
        replica = StatelessORBField()
        _REPLICA_INSTANCES[replica.replica_id] = replica
        return replica
    else:
        # Return existing or create new
        if replica_id not in _REPLICA_INSTANCES:
            _REPLICA_INSTANCES[replica_id] = StatelessORBField(replica_id)
        return _REPLICA_INSTANCES[replica_id]

def get_all_replicas() -> List[StatelessORBField]:
    """Get all active replica instances"""
    return list(_REPLICA_INSTANCES.values())


async def main():
    """Test the stateless ORB field"""
    # Create a replica
    orb = get_orb_replica()

    # Test presence status
    status = await orb.get_presence_status()
    print("🧠 ORB Presence Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")

    # Test speech synthesis
    if orb.xtts_model:
        print("\n🗣️ Testing speech synthesis...")
        result = await orb.generate_speech_output("The ORB is everywhere because it belongs nowhere")
        print(f"   Synthesized: {result['synthesized']}")
        if result['audio_path']:
            print(f"   Audio saved to: {result['audio_path']}")

    # Test Core-4 integration
    print("\n🎯 Testing Core-4 integration...")
    test_verdict = {
        "decision": "accept",
        "confidence": 0.85,
        "reasoning": "Test verdict from stateless ORB replica"
    }
    test_context = {"escalate": True, "source": "test"}

    result = await orb.process_core_verdict("test_core", test_verdict, test_context)
    print(f"   Verdict processed: {result}")

    # Test multiple replicas
    print("\n🔄 Testing replica distribution...")
    replica2 = get_orb_replica()
    print(f"   Replica 1 ID: {orb.replica_id}")
    print(f"   Replica 2 ID: {replica2.replica_id}")
    print(f"   Total replicas: {len(get_all_replicas())}")

    await orb.shutdown()
    await replica2.shutdown()


if __name__ == "__main__":
    asyncio.run(main())