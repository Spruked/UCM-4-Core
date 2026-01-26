#!/usr/bin/env python3
"""
ORB_X Connection Test
Test connectivity between ORB_X and UCM API endpoints
"""

import requests
import json
import time
from datetime import datetime

class ConnectionTester:
    """Test ORB_X to UCM connectivity"""

    def __init__(self, base_url="http://localhost:5050"):
        self.base_url = base_url
        self.endpoints = [
            "/health",
            "/orb/status",
            "/cali/status",
            "/workers/status"
        ]

    def test_endpoint(self, endpoint):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, str(e)

    def test_all_endpoints(self):
        """Test all endpoints"""
        print("🔗 Testing ORB_X to UCM connectivity...")
        print("=" * 50)

        results = {}
        all_passed = True

        for endpoint in self.endpoints:
            print(f"Testing {endpoint}...", end=" ")
            success, result = self.test_endpoint(endpoint)
            if success:
                print("✅ PASSED")
                results[endpoint] = {"status": "passed", "data": result}
            else:
                print(f"❌ FAILED: {result}")
                results[endpoint] = {"status": "failed", "error": result}
                all_passed = False

        return all_passed, results

    def test_command_endpoint(self):
        """Test command endpoint with POST"""
        print("\n⚡ Testing command endpoint...")
        url = f"{self.base_url}/orb/command"

        test_command = {
            "command": "status",
            "parameters": {},
            "timestamp": datetime.now().isoformat()
        }

        try:
            response = requests.post(url, json=test_command, timeout=10)
            if response.status_code == 200:
                print("✅ Command endpoint PASSED")
                return True, response.json()
            else:
                print(f"❌ Command endpoint FAILED: HTTP {response.status_code}")
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            print(f"❌ Command endpoint FAILED: {e}")
            return False, str(e)

    def run_full_test(self):
        """Run complete connectivity test"""
        print(f"🧪 ORB_X Connection Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Target: UCM API at", self.base_url)
        print()

        # Test GET endpoints
        all_passed, results = self.test_all_endpoints()

        # Test POST endpoint
        cmd_passed, cmd_result = self.test_command_endpoint()

        print("\n📊 Test Summary:")
        print("=" * 30)
        print(f"GET Endpoints: {'✅ All Passed' if all_passed else '❌ Some Failed'}")
        print(f"POST Endpoint: {'✅ Passed' if cmd_passed else '❌ Failed'}")

        if all_passed and cmd_passed:
            print("\n🎯 ORB_X is ready to connect to UCM!")
            return True
        else:
            print("\n⚠️  ORB_X connection issues detected. Check UCM service.")
            return False

def main():
    """Main test function"""
    tester = ConnectionTester()
    success = tester.run_full_test()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())