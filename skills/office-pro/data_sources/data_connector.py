#!/usr/bin/env python3
"""
多数据源支持模块
支持数据库、API、云存储等多种数据源
"""

import os
import json
import sqlite3
from typing import Dict, List, Optional, Union, Any, Callable
from abc import ABC, abstractmethod
import pandas as pd
import requests
from urllib.parse import urlparse
import io
import base64


class DataSource(ABC):
    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def fetch(self, query: str = None, **kwargs) -> pd.DataFrame:
        pass

    @abstractmethod
    def disconnect(self):
        pass


class CSVDataSource(DataSource):
    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        self.file_path = file_path
        self.encoding = encoding

    def connect(self) -> bool:
        return os.path.exists(self.file_path)

    def fetch(self, query: str = None, **kwargs) -> pd.DataFrame:
        if self.file_path.endswith('.csv'):
            return pd.read_csv(self.file_path, encoding=self.encoding, **kwargs)
        elif self.file_path.endswith('.xlsx'):
            return pd.read_excel(self.file_path, **kwargs)
        elif self.file_path.endswith('.json'):
            return pd.read_json(self.file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {self.file_path}")

    def disconnect(self):
        pass


class APIDataSource(DataSource):
    def __init__(self, url: str, method: str = 'GET', headers: Dict = None,
                 params: Dict = None, auth: tuple = None, timeout: int = 30):
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.params = params or {}
        self.auth = auth
        self.timeout = timeout
        self.response = None

    def connect(self) -> bool:
        try:
            if self.method == 'GET':
                self.response = requests.get(self.url, headers=self.headers,
                                            params=self.params, auth=self.auth,
                                            timeout=self.timeout)
            elif self.method == 'POST':
                self.response = requests.post(self.url, headers=self.headers,
                                             params=self.params, json=self.params,
                                             auth=self.auth, timeout=self.timeout)
            return self.response.status_code == 200
        except:
            return False

    def fetch(self, query: str = None, **kwargs) -> pd.DataFrame:
        if self.response is None:
            self.connect()

        if self.response.status_code != 200:
            raise Exception(f"API request failed: {self.response.status_code}")

        content_type = self.response.headers.get('Content-Type', '')

        if 'json' in content_type:
            data = self.response.json()
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                if 'data' in data:
                    return pd.DataFrame(data['data'])
                return pd.DataFrame([data])
        elif 'csv' in content_type:
            return pd.read_csv(io.StringIO(self.response.text))
        else:
            return pd.DataFrame({'raw_data': [self.response.text]})

    def disconnect(self):
        self.response = None


class DatabaseDataSource(DataSource):
    def __init__(self, connection_string: str, db_type: str = 'sqlite'):
        self.connection_string = connection_string
        self.db_type = db_type.lower()
        self.connection = None
        self._connect_db()

    def _connect_db(self):
        if self.db_type == 'sqlite':
            self.connection = sqlite3.connect(self.connection_string)
        elif self.db_type == 'mysql':
            import pymysql
            self.connection = pymysql.connect(**self._parse_mysql_connection())
        elif self.db_type == 'postgresql':
            import psycopg2
            self.connection = psycopg2.connect(self.connection_string)

    def _parse_mysql_connection(self) -> Dict:
        parts = self.connection_string.split('://')[1].split(':')
        return {
            'host': parts[0].split('@')[1] if '@' in parts[0] else 'localhost',
            'user': parts[1],
            'password': parts[2].split('@')[0] if '@' in parts[2] else parts[2],
            'database': parts[2].split('/')[-1] if '/' in parts[2] else 'test'
        }

    def connect(self) -> bool:
        return self.connection is not None

    def fetch(self, query: str = None, **kwargs) -> pd.DataFrame:
        if query is None:
            raise ValueError("Query is required for database sources")

        return pd.read_sql(query, self.connection, **kwargs)

    def execute(self, query: str):
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    def disconnect(self):
        if self.connection:
            self.connection.close()


class CloudStorageDataSource(DataSource):
    def __init__(self, storage_type: str, bucket: str, key: str,
                 access_key: str = None, secret_key: str = None,
                 endpoint: str = None, region: str = None):
        self.storage_type = storage_type.lower()
        self.bucket = bucket
        self.key = key
        self.access_key = access_key or os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_key = secret_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.endpoint = endpoint
        self.region = region
        self.client = None
        self._connect_storage()

    def _connect_storage(self):
        if self.storage_type in ['s3', 'oss', 'minio']:
            try:
                import boto3
                kwargs = {
                    'aws_access_key_id': self.access_key,
                    'aws_secret_access_key': self.secret_key
                }
                if self.region:
                    kwargs['region_name'] = self.region
                if self.endpoint:
                    kwargs['endpoint_url'] = self.endpoint

                self.client = boto3.client('s3', **kwargs)
            except ImportError:
                print("boto3 not installed. Install with: pip install boto3")

    def connect(self) -> bool:
        if self.storage_type == 'local':
            return os.path.exists(self.key)
        return self.client is not None

    def fetch(self, query: str = None, **kwargs) -> pd.DataFrame:
        if self.storage_type == 'local':
            return CSVDataSource(self.key).fetch()

        if self.storage_type in ['s3', 'oss', 'minio']:
            response = self.client.get_object(Bucket=self.bucket, Key=self.key)
            body = response['Body'].read()

            if self.key.endswith('.csv'):
                return pd.read_csv(io.BytesIO(body), **kwargs)
            elif self.key.endswith('.xlsx'):
                return pd.read_excel(io.BytesIO(body), **kwargs)
            elif self.key.endswith('.json'):
                return pd.read_json(io.BytesIO(body), **kwargs)

        raise ValueError(f"Unsupported storage type: {self.storage_type}")

    def disconnect(self):
        self.client = None


class DataSourceManager:
    def __init__(self):
        self.sources: Dict[str, DataSource] = {}

    def register_source(self, name: str, source: DataSource) -> bool:
        try:
            if source.connect():
                self.sources[name] = source
                return True
            return False
        except Exception as e:
            print(f"Failed to register source {name}: {e}")
            return False

    def get_source(self, name: str) -> Optional[DataSource]:
        return self.sources.get(name)

    def fetch_data(self, source_name: str, query: str = None, **kwargs) -> pd.DataFrame:
        source = self.get_source(source_name)
        if source is None:
            raise ValueError(f"Source not found: {source_name}")
        return source.fetch(query, **kwargs)

    def disconnect_all(self):
        for source in self.sources.values():
            source.disconnect()
        self.sources.clear()

    def list_sources(self) -> List[str]:
        return list(self.sources.keys())


def create_data_source(source_config: Dict) -> DataSource:
    source_type = source_config.get('type', '').lower()

    if source_type == 'csv' or source_type == 'file':
        return CSVDataSource(
            file_path=source_config['path'],
            encoding=source_config.get('encoding', 'utf-8')
        )
    elif source_type == 'api' or source_type == 'http':
        return APIDataSource(
            url=source_config['url'],
            method=source_config.get('method', 'GET'),
            headers=source_config.get('headers'),
            params=source_config.get('params'),
            auth=source_config.get('auth'),
            timeout=source_config.get('timeout', 30)
        )
    elif source_type == 'database' or source_type == 'db':
        return DatabaseDataSource(
            connection_string=source_config['connection_string'],
            db_type=source_config.get('db_type', 'sqlite')
        )
    elif source_type in ['s3', 'oss', 'cloud']:
        return CloudStorageDataSource(
            storage_type=source_config.get('storage_type', 's3'),
            bucket=source_config['bucket'],
            key=source_config['key'],
            access_key=source_config.get('access_key'),
            secret_key=source_config.get('secret_key'),
            endpoint=source_config.get('endpoint'),
            region=source_config.get('region')
        )
    else:
        raise ValueError(f"Unknown source type: {source_type}")


def load_data_from_config(config_path: str, source_name: str = 'default') -> pd.DataFrame:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    source = create_data_source(config)
    manager = DataSourceManager()
    manager.register_source(source_name, source)

    return manager.fetch_data(source_name)


if __name__ == "__main__":
    sample_config = {
        "type": "csv",
        "path": "sample_data.csv"
    }

    manager = DataSourceManager()

    source = create_data_source(sample_config)
    if manager.register_source("test", source):
        print("Source connected successfully")
        df = manager.fetch_data("test")
        print(df.head())
