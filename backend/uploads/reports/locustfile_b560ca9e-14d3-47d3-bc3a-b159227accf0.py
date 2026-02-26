from locust import HttpUser, task, between, events
import json
import time
import requests

class LoadTestUser(HttpUser):
    """压测用户"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户启动时执行"""
        pass
    
    def on_stop(self):
        """用户停止时执行"""
        pass

    @task(1)
    def task_1(self):
        """Test Request"""
        headers = {}
        
        with self.client.get(
            'https://httpbin.org/get',
            headers=headers,
            
            catch_response=True,
            timeout=30
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


# 统计信息收集
stats_data = {}

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, 
               response, context, exception, start_time, url, **kwargs):
    """请求事件监听"""
    if name not in stats_data:
        stats_data[name] = {
            'requests': 0,
            'failures': 0,
            'response_times': []
        }
    
    stats_data[name]['requests'] += 1
    if exception:
        stats_data[name]['failures'] += 1
    else:
        stats_data[name]['response_times'].append(response_time)

@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """保存统计数据"""
    import json
    with open('/data/workspace/loadtest2/backend/uploads/reports/stats_b560ca9e-14d3-47d3-bc3a-b159227accf0.json', 'w') as f:
        json.dump(stats_data, f)
