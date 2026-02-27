from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.scenarios.models import Scenario, Request
from apps.reports.locust_engine import locust_engine
import uuid

User = get_user_model()


class ScenarioTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.scenario = Scenario.objects.create(
            name="Test Scenario",
            description="Test scenario description",
            target_host="https://www.baidu.com",
            default_users=10,
            default_spawn_rate=1,
            default_duration=60,
            created_by=self.user,
        )
        self.request = Request.objects.create(
            scenario=self.scenario,
            name="Test Request",
            method="GET",
            url="/api/test",
            weight=1,
            think_time=1.0,
            timeout=30,
        )

    def test_scenario_creation(self):
        self.assertEqual(self.scenario.name, "Test Scenario")
        self.assertEqual(self.scenario.target_host, "https://www.baidu.com")
        self.assertEqual(self.scenario.default_users, 10)

    def test_locustfile_generation_with_host(self):
        report_id = str(uuid.uuid4())
        locust_file = locust_engine.generate_locustfile(self.scenario, report_id)

        with open(locust_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('host = "https://www.baidu.com"', content)
        self.assertIn("class LoadTestUser(HttpUser):", content)

    def test_locustfile_generation_without_host(self):
        scenario_no_host = Scenario.objects.create(
            name="Scenario Without Host", created_by=self.user, default_users=1
        )
        report_id = str(uuid.uuid4())
        locust_file = locust_engine.generate_locustfile(scenario_no_host, report_id)

        with open(locust_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('host = "https://example.com"', content)
