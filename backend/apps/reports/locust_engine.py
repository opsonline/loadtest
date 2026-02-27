import os
import subprocess
import json
import time
import signal
from pathlib import Path
from django.conf import settings
from apps.scenarios.models import Request


class LocustEngine:
    """Locust 压测引擎"""

    def __init__(self):
        self.processes = {}

    def generate_locustfile(self, scenario, report_id):
        """生成 Locust 测试文件"""
        requests = scenario.requests.filter(is_active=True).order_by("order")

        locust_code = self._generate_imports()
        locust_code += self._generate_test_class(scenario)
        locust_code += self._generate_tasks(requests)
        locust_code += self._generate_events(report_id)

        # 保存文件
        reports_dir = Path(settings.LOCUST_REPORTS_DIR)
        reports_dir.mkdir(parents=True, exist_ok=True)

        locust_file = reports_dir / f"locustfile_{report_id}.py"
        with open(locust_file, "w", encoding="utf-8") as f:
            f.write(locust_code)

        return str(locust_file)

    def _generate_imports(self):
        """生成导入语句"""
        return """from locust import HttpUser, task, between, events
import json
import time
import requests

"""

    def _generate_test_class(self, scenario):
        """生成测试类"""
        target_host = (
            scenario.target_host if scenario.target_host else "https://example.com"
        )
        return f'''class LoadTestUser(HttpUser):
    """压测用户"""
    host = "{target_host}"
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户启动时执行"""
        pass
    
    def on_stop(self):
        """用户停止时执行"""
        pass

'''

    def _generate_tasks(self, requests):
        """生成任务"""
        tasks_code = ""

        for i, req in enumerate(requests):
            task_name = f"task_{i + 1}"
            weight = req.weight

            # 处理 headers
            headers_str = (
                json.dumps(req.headers, ensure_ascii=False) if req.headers else "{}"
            )

            # 处理 body
            body_code = ""
            if req.body and req.body_type != "none":
                if req.body_type == "json":
                    try:
                        json.loads(req.body)
                        body_code = f"json={repr(req.body)}"
                    except:
                        body_code = f"data={repr(req.body)}"
                else:
                    body_code = f"data={repr(req.body)}"

            tasks_code += f'''    @task({weight})
    def {task_name}(self):
        """{req.name}"""
        headers = {headers_str}
        
        with self.client.{req.method.lower()}(
            '{req.url}',
            headers=headers,
            {body_code if body_code else ""}
            catch_response=True,
            timeout={req.timeout}
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {{response.status_code}}")

'''

        return tasks_code

    def _generate_events(self, report_id):
        """生成事件处理"""
        stats_file = Path(settings.LOCUST_REPORTS_DIR) / f"stats_{report_id}.json"

        return f'''
# 统计信息收集
stats_data = {{}}

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, 
               response, context, exception, start_time, url, **kwargs):
    """请求事件监听"""
    if name not in stats_data:
        stats_data[name] = {{
            'requests': 0,
            'failures': 0,
            'response_times': []
        }}
    
    stats_data[name]['requests'] += 1
    if exception:
        stats_data[name]['failures'] += 1
    else:
        stats_data[name]['response_times'].append(response_time)

@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """保存统计数据"""
    import json
    with open('{stats_file}', 'w') as f:
        json.dump(stats_data, f)
'''

    def run_load_test(self, report, locust_file):
        """运行压测"""
        reports_dir = Path(settings.LOCUST_REPORTS_DIR)
        stats_file = reports_dir / f"stats_{report.id}"

        cmd = [
            settings.LOCUST_BINARY,
            "-f",
            locust_file,
            "--headless",
            "-u",
            str(report.users),
            "-r",
            str(report.spawn_rate),
            "--run-time",
            f"{report.duration}s",
            "--csv",
            str(stats_file),
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )

        self.processes[str(report.id)] = {"process": process, "start_time": time.time()}

        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Locust stderr: {stderr}")
            raise Exception(f"Locust failed with return code {process.returncode}: {stderr}")
        
        return True

    def stop_load_test(self, report_id):
        """停止压测"""
        if str(report_id) in self.processes:
            process_info = self.processes[str(report_id)]
            process = process_info["process"]

            try:
                if os.name != "nt":
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()

                process.wait(timeout=10)
            except:
                try:
                    if os.name != "nt":
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    else:
                        process.kill()
                except:
                    pass

            del self.processes[str(report_id)]
            return True

        return False

    def get_stats(self, report_id):
        """获取统计数据"""
        stats_file = Path(settings.LOCUST_REPORTS_DIR) / f"stats_{report_id}.json"

        if stats_file.exists():
            try:
                with open(stats_file, "r") as f:
                    return json.load(f)
            except:
                return {}

        return {}

    def parse_csv_stats(self, report_id):
        """解析 CSV 统计数据"""
        reports_dir = Path(settings.LOCUST_REPORTS_DIR)
        stats_file = reports_dir / f"stats_{report_id}_stats.csv"
        stats_history_file = reports_dir / f"stats_{report_id}_stats_history.csv"

        stats = {"requests": {}, "history": []}

        print(f"Looking for stats file: {stats_file}")
        print(f"Stats file exists: {stats_file.exists()}")

        # 解析总体统计
        if stats_file.exists():
            try:
                with open(stats_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    print(f"CSV lines count: {len(lines)}")
                    if len(lines) > 1:
                        # 解析表头
                        headers = lines[0].strip().split(",")
                        # 解析数据行
                        for line in lines[1:]:
                            values = line.strip().split(",")
                            if len(values) == len(headers):
                                row = dict(zip(headers, values))
                                name = row.get("Name", "")
                                if name:
                                    stats["requests"][name] = {
                                        "num_requests": int(
                                            row.get("Request Count", 0)
                                        ),
                                        "num_failures": int(
                                            row.get("Failure Count", 0)
                                        ),
                                        "avg_response_time": float(
                                            row.get("Average Response Time", 0)
                                        ),
                                        "min_response_time": float(
                                            row.get("Min Response Time", 0)
                                        ),
                                        "max_response_time": float(
                                            row.get("Max Response Time", 0)
                                        ),
                                        "p50": float(row.get("50%", 0)),
                                        "p90": float(row.get("90%", 0)),
                                        "p95": float(row.get("95%", 0)),
                                        "p99": float(row.get("99%", 0)),
                                        "rps": float(row.get("Requests/s", 0)),
                                    }
                    else:
                        print("CSV file is empty or only has header")
            except Exception as e:
                import traceback

                print(f"Error parsing stats CSV: {e}")
                traceback.print_exc()
        else:
            print(f"Stats file not found: {stats_file}")

        # 解析历史数据
        if stats_history_file.exists():
            try:
                with open(stats_history_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        headers = lines[0].strip().split(",")
                        for line in lines[1:]:
                            values = line.strip().split(",")
                            if len(values) == len(headers):
                                row = dict(zip(headers, values))
                                stats["history"].append(
                                    {
                                        "timestamp": row.get("Timestamp", ""),
                                        "user_count": int(row.get("User Count", 0)),
                                        "rps": float(row.get("Requests/s", 0)),
                                        "failures": int(row.get("Failures/s", 0)),
                                        "avg_response_time": float(
                                            row.get("Average Response Time", 0)
                                        ),
                                        "p50": float(row.get("50%", 0)),
                                        "p95": float(row.get("95%", 0)),
                                    }
                                )
            except Exception as e:
                print(f"Error parsing history CSV: {e}")

        print(f"Parsed stats: {stats}")
        return stats


# 全局引擎实例
locust_engine = LocustEngine()
