import json
from urllib.parse import urlparse


class HARParser:
    """HAR 文件解析器"""
    
    def __init__(self):
        self.supported_resource_types = ['xhr', 'document', 'other', 'stylesheet', 'script', 'image']
    
    def parse(self, har_file, resource_types=None):
        """
        解析 HAR 文件
        :param har_file: 上传的文件对象
        :param resource_types: 要导入的资源类型列表
        :return: 解析后的请求列表
        """
        if resource_types is None:
            resource_types = ['xhr', 'document']
        
        try:
            content = har_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            har_data = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"无效的 HAR 文件: {str(e)}")
        
        entries = har_data.get('log', {}).get('entries', [])
        requests = []
        
        for entry in entries:
            request_data = entry.get('request', {})
            response_data = entry.get('response', {})
            
            # 检查资源类型
            resource_type = self._get_resource_type(request_data, entry)
            if resource_type not in resource_types:
                continue
            
            # 跳过不成功的请求
            status = response_data.get('status', 0)
            if status >= 400:
                continue
            
            # 解析请求
            parsed_request = self._parse_request(request_data)
            if parsed_request:
                requests.append(parsed_request)
        
        return requests
    
    def _get_resource_type(self, request_data, entry):
        """获取资源类型"""
        # 尝试从 _resourceType 获取
        resource_type = entry.get('_resourceType', 'other')
        
        # 根据 MIME 类型推断
        if resource_type == 'other':
            mime_type = entry.get('response', {}).get('content', {}).get('mimeType', '').lower()
            if 'javascript' in mime_type or mime_type.endswith('js'):
                resource_type = 'script'
            elif 'css' in mime_type:
                resource_type = 'stylesheet'
            elif any(img in mime_type for img in ['image', 'png', 'jpg', 'jpeg', 'gif', 'svg']):
                resource_type = 'image'
            elif 'json' in mime_type or 'xml' in mime_type:
                resource_type = 'xhr'
            elif 'html' in mime_type:
                resource_type = 'document'
        
        return resource_type
    
    def _parse_request(self, request_data):
        """解析单个请求"""
        url = request_data.get('url', '')
        method = request_data.get('method', 'GET')
        
        if not url:
            return None
        
        # 解析 headers
        headers = {}
        for header in request_data.get('headers', []):
            name = header.get('name', '')
            value = header.get('value', '')
            # 跳过一些不必要的 header
            if name.lower() not in ['host', 'content-length']:
                headers[name] = value
        
        # 解析 body
        post_data = request_data.get('postData', {})
        body_type = 'none'
        body = ''
        
        if post_data:
            mime_type = post_data.get('mimeType', '').lower()
            
            if 'json' in mime_type:
                body_type = 'json'
                body = post_data.get('text', '')
            elif 'form' in mime_type:
                body_type = 'form'
                params = post_data.get('params', [])
                if params:
                    body = '&'.join([f"{p['name']}={p.get('value', '')}" for p in params])
                else:
                    body = post_data.get('text', '')
            else:
                body_type = 'json'
                body = post_data.get('text', '')
        
        return {
            'url': url,
            'method': method,
            'headers': headers,
            'body_type': body_type,
            'body': body
        }
    
    def replace_host(self, url, new_host):
        """替换 URL 的 host"""
        try:
            parsed = urlparse(url)
            # 保留 path、query、fragment
            new_url = f"{parsed.scheme}://{new_host}{parsed.path}"
            if parsed.query:
                new_url += f"?{parsed.query}"
            if parsed.fragment:
                new_url += f"#{parsed.fragment}"
            return new_url
        except Exception:
            return url
    
    def get_resource_types(self):
        """获取支持的资源类型"""
        return self.supported_resource_types
