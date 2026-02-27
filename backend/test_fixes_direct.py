"""
Direct test - No API required
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.scenarios.models import Scenario, Request
from apps.users.models import User
from apps.reports.locust_engine import locust_engine
import uuid


def test_scenario_target_host():
    """Test scenario target_host field"""
    print("\n=== Test Scenario target_host Field ===")

    # Get or create test user
    user = User.objects.filter(username="admin").first()
    if not user:
        print("[X] Admin user not found")
        return False

    # Create scenario with target_host
    scenario = Scenario.objects.create(
        name="Test Scenario",
        description="Test",
        target_host="https://www.example.com",
        default_users=10,
        default_spawn_rate=1,
        default_duration=60,
        created_by=user,
    )

    print(f"[OK] Scenario created, ID: {scenario.id}")
    print(f"    target_host: {scenario.target_host}")

    # Create request
    Request.objects.create(
        scenario=scenario, name="Test Request", method="GET", url="/api/test", weight=1
    )

    # Generate locustfile
    report_id = str(uuid.uuid4())
    locust_file = locust_engine.generate_locustfile(scenario, report_id)

    print(f"[OK] Locustfile generated: {locust_file}")

    # Check if host is in the file
    with open(locust_file, "r", encoding="utf-8") as f:
        content = f.read()

    if 'host = "https://www.example.com"' in content:
        print(f"[OK] locustfile contains correct host configuration")

        # Show relevant lines
        lines = content.split("\n")
        for i, line in enumerate(lines[:20], 1):
            if "host" in line.lower() or "class LoadTestUser" in line:
                print(f"    Line {i}: {line}")
    else:
        print(f"[X] locustfile missing host configuration")
        print(f"Content preview: {content[:500]}")
        scenario.delete()
        return False

    # Cleanup
    scenario.delete()
    print(f"[OK] Cleanup completed")

    return True


def test_locustfile_generation():
    """Test locustfile generation with host"""
    print("\n=== Test Locustfile Generation ===")

    user = User.objects.filter(username="admin").first()
    if not user:
        print("[X] Admin user not found")
        return False

    # Test 1: With host
    scenario1 = Scenario.objects.create(
        name="Scenario With Host", target_host="https://www.baidu.com", created_by=user
    )

    Request.objects.create(
        scenario=scenario1, name="Test Request", method="GET", url="/", weight=1
    )

    report_id1 = str(uuid.uuid4())
    locust_file1 = locust_engine.generate_locustfile(scenario1, report_id1)

    with open(locust_file1, "r", encoding="utf-8") as f:
        content1 = f.read()

    if 'host = "https://www.baidu.com"' in content1:
        print(f"[OK] Test 1 PASS: With host")
    else:
        print(f"[X] Test 1 FAIL: Host not found in locustfile")
        scenario1.delete()
        return False

    scenario1.delete()

    # Test 2: Without host (should use default)
    scenario2 = Scenario.objects.create(name="Scenario Without Host", created_by=user)

    Request.objects.create(
        scenario=scenario2, name="Test Request", method="GET", url="/", weight=1
    )

    report_id2 = str(uuid.uuid4())
    locust_file2 = locust_engine.generate_locustfile(scenario2, report_id2)

    with open(locust_file2, "r", encoding="utf-8") as f:
        content2 = f.read()

    if 'host = "https://example.com"' in content2:
        print(f"[OK] Test 2 PASS: Without host (default used)")
    else:
        print(f"[X] Test 2 FAIL: Default host not found")
        scenario2.delete()
        return False

    scenario2.delete()

    return True


def main():
    print("=" * 50)
    print("Direct Self-Test of Fixed Issues")
    print("=" * 50)

    results = []

    # Test 1: Scenario target_host field
    results.append(("Scenario target_host Field", test_scenario_target_host()))

    # Test 2: Locustfile generation
    results.append(("Locustfile Generation", test_locustfile_generation()))

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

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
