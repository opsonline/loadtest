import csv
import json
import io
from pathlib import Path


class DataProvider:
    """数据提供器"""
    
    def __init__(self, datasource):
        self.datasource = datasource
        self._data_cache = None
    
    def test_connection(self):
        """测试连接"""
        source_type = self.datasource.source_type
        
        if source_type in ['csv', 'json']:
            return self._test_file_connection()
        elif source_type in ['mysql', 'postgresql']:
            return self._test_db_connection()
        elif source_type == 'mongodb':
            return self._test_mongodb_connection()
        elif source_type == 'redis':
            return self._test_redis_connection()
        elif source_type == 'python':
            return self._test_python_script()
        
        return False
    
    def _test_file_connection(self):
        """测试文件连接"""
        try:
            file_path = self.datasource.file_path
            if not file_path:
                return False
            
            path = Path(file_path)
            return path.exists() and path.is_file()
        except:
            return False
    
    def _test_db_connection(self):
        """测试数据库连接"""
        try:
            if self.datasource.source_type == 'mysql':
                import pymysql
                conn = pymysql.connect(
                    host=self.datasource.db_host,
                    port=self.datasource.db_port or 3306,
                    user=self.datasource.db_user,
                    password=self.datasource.db_password or '',
                    database=self.datasource.db_name,
                    connect_timeout=5
                )
                conn.close()
                return True
            
            elif self.datasource.source_type == 'postgresql':
                import psycopg2
                conn = psycopg2.connect(
                    host=self.datasource.db_host,
                    port=self.datasource.db_port or 5432,
                    user=self.datasource.db_user,
                    password=self.datasource.db_password or '',
                    dbname=self.datasource.db_name,
                    connect_timeout=5
                )
                conn.close()
                return True
        except Exception as e:
            print(f"DB connection error: {e}")
            return False
    
    def _test_mongodb_connection(self):
        """测试 MongoDB 连接"""
        try:
            from pymongo import MongoClient
            client = MongoClient(
                host=self.datasource.db_host,
                port=self.datasource.db_port or 27017,
                username=self.datasource.db_user,
                password=self.datasource.db_password or '',
                serverSelectionTimeoutMS=5000
            )
            client.server_info()
            client.close()
            return True
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return False
    
    def _test_redis_connection(self):
        """测试 Redis 连接"""
        try:
            import redis
            r = redis.Redis(
                host=self.datasource.db_host,
                port=self.datasource.db_port or 6379,
                password=self.datasource.db_password or None,
                socket_connect_timeout=5
            )
            r.ping()
            return True
        except Exception as e:
            print(f"Redis connection error: {e}")
            return False
    
    def _test_python_script(self):
        """测试 Python 脚本"""
        try:
            script = self.datasource.python_script
            if not script:
                return False
            
            # 简单编译检查语法
            compile(script, '<string>', 'exec')
            return True
        except:
            return False
    
    def get_preview(self, limit=10):
        """获取预览数据"""
        data = self._get_all_data()
        return data[:limit] if data else []
    
    def get_total_count(self):
        """获取数据总数"""
        data = self._get_all_data()
        return len(data) if data else 0
    
    def get_by_index(self, index):
        """获取指定索引的数据"""
        data = self._get_all_data()
        if data and 0 <= index < len(data):
            return data[index]
        return None
    
    def _get_all_data(self):
        """获取所有数据"""
        if self._data_cache is not None:
            return self._data_cache
        
        source_type = self.datasource.source_type
        
        if source_type == 'csv':
            self._data_cache = self._get_csv_data()
        elif source_type == 'json':
            self._data_cache = self._get_json_data()
        elif source_type in ['mysql', 'postgresql']:
            self._data_cache = self._get_db_data()
        elif source_type == 'mongodb':
            self._data_cache = self._get_mongodb_data()
        elif source_type == 'redis':
            self._data_cache = self._get_redis_data()
        elif source_type == 'python':
            self._data_cache = self._get_python_data()
        else:
            self._data_cache = []
        
        return self._data_cache
    
    def _get_csv_data(self):
        """获取 CSV 数据"""
        try:
            file_path = self.datasource.file_path
            if not file_path:
                return []
            
            encoding = self.datasource.file_encoding or 'utf-8'
            delimiter = self.datasource.csv_delimiter or ','
            
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                return list(reader)
        except Exception as e:
            print(f"CSV read error: {e}")
            return []
    
    def _get_json_data(self):
        """获取 JSON 数据"""
        try:
            file_path = self.datasource.file_path
            if not file_path:
                return []
            
            encoding = self.datasource.file_encoding or 'utf-8'
            
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return [data]
        except Exception as e:
            print(f"JSON read error: {e}")
            return []
    
    def _get_db_data(self):
        """获取数据库数据"""
        try:
            if self.datasource.source_type == 'mysql':
                import pymysql
                conn = pymysql.connect(
                    host=self.datasource.db_host,
                    port=self.datasource.db_port or 3306,
                    user=self.datasource.db_user,
                    password=self.datasource.db_password or '',
                    database=self.datasource.db_name
                )
            elif self.datasource.source_type == 'postgresql':
                import psycopg2
                conn = psycopg2.connect(
                    host=self.datasource.db_host,
                    port=self.datasource.db_port or 5432,
                    user=self.datasource.db_user,
                    password=self.datasource.db_password or '',
                    dbname=self.datasource.db_name
                )
            else:
                return []
            
            query = self.datasource.db_query or 'SELECT 1'
            
            with conn.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
            
            conn.close()
            return data
        
        except Exception as e:
            print(f"DB query error: {e}")
            return []
    
    def _get_mongodb_data(self):
        """获取 MongoDB 数据"""
        try:
            from pymongo import MongoClient
            client = MongoClient(
                host=self.datasource.db_host,
                port=self.datasource.db_port or 27017,
                username=self.datasource.db_user,
                password=self.datasource.db_password or ''
            )
            
            db = client[self.datasource.db_name]
            collection = db[self.datasource.db_collection]
            
            data = list(collection.find().limit(1000))
            
            # 转换 ObjectId
            for item in data:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
            
            client.close()
            return data
        
        except Exception as e:
            print(f"MongoDB query error: {e}")
            return []
    
    def _get_redis_data(self):
        """获取 Redis 数据"""
        try:
            import redis
            r = redis.Redis(
                host=self.datasource.db_host,
                port=self.datasource.db_port or 6379,
                password=self.datasource.db_password or None,
                decode_responses=True
            )
            
            key = self.datasource.redis_key
            pattern = self.datasource.redis_pattern
            
            data = []
            
            if key:
                value = r.get(key)
                if value:
                    try:
                        data.append(json.loads(value))
                    except:
                        data.append({'value': value})
            
            elif pattern:
                keys = r.keys(pattern)
                for k in keys[:100]:  # 限制数量
                    value = r.get(k)
                    if value:
                        try:
                            data.append({'key': k, 'value': json.loads(value)})
                        except:
                            data.append({'key': k, 'value': value})
            
            return data
        
        except Exception as e:
            print(f"Redis query error: {e}")
            return []
    
    def _get_python_data(self):
        """执行 Python 脚本获取数据"""
        try:
            script = self.datasource.python_script
            if not script:
                return []
            
            # 创建局部命名空间
            local_ns = {}
            exec(script, {}, local_ns)
            
            # 查找返回的数据
            if 'data' in local_ns:
                data = local_ns['data']
                if isinstance(data, list):
                    return data
                return [data]
            
            return []
        
        except Exception as e:
            print(f"Python script error: {e}")
            return []
