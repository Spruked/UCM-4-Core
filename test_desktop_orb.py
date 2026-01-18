# UCM_4_Core/test_desktop_orb.py
"""
Test Desktop ORB Capabilities - VS Code Integration
Tests the ORB's ability to work desktop-first with VS Code capabilities.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from orb_perception_integration import StatelessORBField


async def test_desktop_capabilities():
    """Test VS Code desktop capabilities"""
    print("🧪 Testing Desktop ORB Capabilities")
    print("=" * 50)

    # Initialize ORB field
    orb = StatelessORBField("test_desktop_replica")

    # Test 1: Get workspace info
    print("\n1. Testing workspace info...")
    workspace_info = await orb.get_workspace_info()
    if workspace_info:
        print(f"✅ Workspace info retrieved: {len(workspace_info)} keys")
        for key, value in workspace_info.items():
            print(f"   {key}: {value}")
    else:
        print("❌ Failed to get workspace info")

    # Test 2: Search workspace
    print("\n2. Testing workspace search...")
    search_results = await orb.search_workspace("class")
    if search_results:
        print(f"✅ Found {len(search_results)} search results")
        for result in search_results[:3]:  # Show first 3
            print(f"   {result.get('file', 'unknown')}: {result.get('line', 'unknown')}")
    else:
        print("❌ No search results or search failed")

    # Test 3: Create a test file
    print("\n3. Testing file creation...")
    test_file = PROJECT_ROOT / "test_desktop_output.txt"
    test_content = "This file was created by the ORB's desktop capabilities!\n"
    success = await orb.create_file_in_vscode(str(test_file), test_content)
    if success:
        print(f"✅ Test file created: {test_file}")
    else:
        print("❌ Failed to create test file")

    # Test 4: Open the test file
    print("\n4. Testing file opening...")
    if test_file.exists():
        success = await orb.open_file_in_vscode(str(test_file))
        if success:
            print(f"✅ Test file opened in VS Code: {test_file}")
        else:
            print("❌ Failed to open test file")
    else:
        print("❌ Test file doesn't exist to open")

    # Test 5: Run a terminal command
    print("\n5. Testing terminal command...")
    success, output = await orb.run_terminal_command("echo 'ORB Desktop Test'")
    if success:
        print("✅ Terminal command executed successfully")
        print(f"   Output: {output.strip()}")
    else:
        print(f"❌ Terminal command failed: {output}")

    print("\n" + "=" * 50)
    print("🎉 Desktop ORB testing complete!")
    print("\nNext steps:")
    print("- The ORB can now work desktop-first with VS Code")
    print("- Add more adapters (Files, Browser, Terminal) for full desktop capabilities")
    print("- Once desktop works, extend to web apps with same consciousness")


if __name__ == "__main__":
    asyncio.run(test_desktop_capabilities())