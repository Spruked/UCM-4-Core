#!/usr/bin/env python3
"""
Test CALI SKG initialization
"""

from CALI.cali_skg import CALISKGEngine
from pathlib import Path

def test_cali_init():
    print("🔬 Testing CALI SKG initialization...")

    try:
        cali = CALISKGEngine(Path('.'))
        print("✅ CALI SKG initialized successfully")
        print(f"📊 Core nodes: {len(cali.kg.nodes())}")
        print(f"🎭 Personality: {cali.core_personality['archetype']}")
        print(f"🎤 Voice: {cali.core_personality['voice_characteristics']['gender']}")
        print(f"🧠 Knowledge domains: {len(cali.core_personality['knowledge_domains']['primary'])}")

        # Test basic functionality
        status = cali.get_system_status()
        print(f"🔐 Vault integrity: {status['vault_integrity']}")
        print(f"📈 User trust level: {status['user_trust_level']}")

        print("\n🎉 CALI SKG test completed successfully!")

    except Exception as e:
        print(f"❌ CALI SKG initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cali_init()