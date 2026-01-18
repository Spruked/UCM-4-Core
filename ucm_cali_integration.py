# ucm_cali_integration.py - Complete workflow
from pathlib import Path
from datetime import datetime
from cali_skg import CALISKGEngine
from cali_voice_bridge import CALIVoiceBridge
from pom_engine import POMEngine

class UCMWithCALIInterface:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.pom = POMEngine()
        self.cali = CALISKGEngine(base_path)
        self.voice_bridge = CALIVoiceBridge(self.cali, self.pom)

        print("✅ UCM-CALI Integration Active")
        print(f"📊 CALI Core Nodes: {len(self.cali.kg.nodes())}")
        print(f"🎤 Voice Engine: {self.pom.get_status()['engine']}")

    def process_user_query(self, query: str, user_id: str = None) -> Dict[str, Any]:
        """
        Complete UCM processing with elegant CALI response

        Args:
            query: User's query
            user_id: Optional user identifier

        Returns:
            Complete response package
        """

        context = {
            "session_id": f"ucm_{hash(query)[:8]}",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }

        # Generate CALI response
        response = self.cali.generate_orb_response(query, context)

        # Generate voice audio
        audio_path = self.base_path / "audio" / f"{response['response_id']}.mp3"
        audio_file = self.voice_bridge.generate_cali_speech(response, audio_path)

        response["audio_file"] = str(audio_file)
        response["voice_generated"] = True

        return response

    def system_announcement(self, event_type: str, event_data: Dict):
        """Make CALI announce system events"""

        audio_path = self.base_path / "audio" / f"announce_{event_type}.mp3"
        self.voice_bridge.generate_announcement(event_type, event_data, audio_path)

        print(f"📢 System Announcement: {event_type} -> {audio_path}")

# Usage
ucm = UCMWithCALIInterface(Path("."))

# Process a user query
result = ucm.process_user_query(
    "What is the status of the Epistemic Convergence Matrix?",
    user_id="developer_001"
)

print(f"Response: {result['text']}")
print(f"Audio: {result['audio_file']}")
print(f"Confidence: {result['ucm_confidence']:.2f}")

# System announcement
ucm.system_announcement("system_startup", {"initiated_by": "Core 4"})