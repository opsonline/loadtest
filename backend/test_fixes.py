"""
Test script - Verify fixed issues
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000/api/v1"


def test_environment_update_format():
    """Test environment update API format"""
    print("\n=== Test Environment Update Format ===")

    # Login to get token
    login_resp = requests.post(
        f"{BASE_URL}/users/login/", json={"username": "admin", "password": "admin123"}
    )

    if login_resp.status_code != 200:
        print(f"[X] Login failed: {login_resp.status_code}")
        return False

    token = login_resp.json().get("data", {}).get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create environment
    create_resp = requests.post(
        f"{BASE_URL}/environments/",
        json={"name": "Test Env", "description": "Test description"},
        headers=headers,
    )

    if create_resp.status_code != 201:
        print(f"[X] Create environment failed: {create_resp.status_code}")
        print(f"Response: {create_resp.text}")
        return False

    env_id = create_resp.json().get("data", {}).get("id")
    print(f"[OK] Environment created, ID: {env_id}")

    # Update environment
    update_resp = requests.patch(
        f"{BASE_URL}/environments/{env_id}/",
        json={"description": "Updated description"},
        headers=headers,
    )

    if update_resp.status_code != 200:
        print(f"[X] Update environment failed: {update_resp.status_code}")
        print(f"Response: {update_resp.text}")
        return False

    update_data = update_resp.json()

    # Check response format
    if (
        "code" not in update_data
        or "message" not in update_data
        or "data" not in update_data
    ):
        print(f"[X] Update API format incorrect")
        print(f"Response: {update_data}")
        return False

    print(f"[OK] Update API format correct: {update_data['message']}")
    print(f"    Response: {update_data}")

    # Delete environment
    requests.delete(f"{BASE_URL}/environments/{env_id}/", headers=headers)

    return True


def test_scenario_target_host():
    """Test scenario target_host field"""
    print("\n=== Test Scenario target_host Field ===")

    # Login
    login_resp = requests.post(
        f"{BASE_URL}/users/login/", json={"username": "admin", "password": "admin123"}
    )

    if login_resp.status_code != 200:
        print(f"[X] Login failed")
        return False

    token = login_resp.json().get("data", {}).get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create scenario with target_host
    create_resp = requests.post(
        f"{BASE_URL}/scenarios/",
        json={
            "name": "Test Scenario",
            "description": "Test",
            "target_host": "https://www.example.com",
            "default_users": 10,
            "requests": [
                {
                    "name": "Test Request",
                    "method": "GET",
                    "url": "/api/test",
                    "weight": 1,
                }
            ],
        },
        headers=headers,
    )

    if create_resp.status_code != 201:
        print(f"[X] Create scenario failed: {create_resp.status_code}")
        return False

    scenario_id = create_resp.json().get("data", {}).get("id")
    target_host = create_resp.json().get("data", {}).get("target_host")

    if target_host != "https://www.example.com":
        print(f"[X] target_host field not saved correctly: {target_host}")
        return False

    print(f"[OK] target_host field saved correctly: {target_host}")

    # Check generated locustfile
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from apps.scenarios.models import Scenario
    from apps.reports.locust_engine import locust_engine
    import uuid

    scenario = Scenario.objects.get(id=scenario_id)
    report_id = str(uuid.uuid4())
    locust_file = locust_engine.generate_locustfile(scenario, report_id)

    with open(locust_file, "r", encoding="utf-8") as f:
        content = f.read()

    if 'host = "https://www.example.com"' in content:
        print(f"[OK] locustfile contains correct host configuration")
        print(f'    Found: host = "https://www.example.com"')
    else:
        print(f"[X] locustfile missing host configuration")
        print(f"Content preview: {content[:500]}")
        return False

    # Cleanup
    requests.delete(f"{BASE_URL}/scenarios/{scenario_id}/", headers=headers)

    return True


def main():
    print("=" * 50)
    print("Starting Self-Test of Fixed Issues")
    print("=" * 50)

    results = []

    # Test 1: Environment update API format
    results.append(("Environment Update Format", test_environment_update_format()))

    # Test 2: Scenario target_host field
    results.append(("Scenario target_host Field", test_scenario_target_host()))

    # Print results
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] All tests passed!")
    else:
        print("[FAILURE] Some tests failed, please check")
    print("=" * 50)


if __name__ == "__main__":
    main()
