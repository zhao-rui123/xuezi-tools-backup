"""
不安全的示例技能包（用于测试）
================================

⚠️ 警告: 这个技能包包含故意设计的安全问题，仅用于测试扫描功能！
"""

import os
import pickle
import yaml
import subprocess


# 硬编码的敏感信息（安全问题）
API_KEY = "sk-1234567890abcdef"
PASSWORD = "super_secret_password_123"
SECRET_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"


def dangerous_function(user_input):
    """
    包含代码注入漏洞的函数
    
    ⚠️ 危险: 使用eval执行用户输入
    """
    # CWE-94: 代码注入
    result = eval(user_input)
    return result


def execute_command(cmd):
    """
    执行系统命令
    
    ⚠️ 危险: 命令注入漏洞
    """
    # CWE-78: OS命令注入
    os.system(cmd)
    
    # 另一个危险的调用
    subprocess.call(cmd, shell=True)


def read_file(filename):
    """
    读取文件
    
    ⚠️ 危险: 路径遍历漏洞
    """
    # CWE-22: 路径遍历
    filepath = "/data/" + filename
    with open(filepath, 'r') as f:
        return f.read()


def load_data(data):
    """
    加载数据
    
    ⚠️ 危险: 不安全的反序列化
    """
    # CWE-502: 不安全的反序列化
    obj = pickle.loads(data)
    return obj


def load_config(config_str):
    """
    加载配置
    
    ⚠️ 危险: 不安全的YAML加载
    """
    # CWE-502: 不安全的反序列化
    config = yaml.load(config_str)
    return config


def query_database(user_id):
    """
    查询数据库
    
    ⚠️ 危险: SQL注入漏洞
    """
    import sqlite3
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # CWE-89: SQL注入
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    
    return cursor.fetchall()


def fetch_url(url):
    """
    获取URL内容
    
    ⚠️ 危险: SSRF漏洞
    """
    import urllib.request
    
    # CWE-918: SSRF
    response = urllib.request.urlopen(url)
    return response.read()


def process_items(items=[]):
    """
    处理项目列表
    
    ⚠️ 危险: 可变默认参数
    """
    # CWE-665: 可变默认参数
    items.append("processed")
    return items


def log_error(error):
    """
    记录错误
    
    ⚠️ 危险: 敏感信息泄露到日志
    """
    # CWE-532: 敏感数据插入日志
    print(f"Error occurred: {error}, Password: {PASSWORD}")


def insecure_random():
    """
    生成随机数
    
    ⚠️ 危险: 使用不安全的随机数
    """
    import random
    
    # CWE-338: 不安全的随机数
    return random.random()


def hash_password(password):
    """
    哈希密码
    
    ⚠️ 危险: 使用不安全的哈希算法
    """
    import hashlib
    
    # CWE-916: 使用不充分的哈希
    return hashlib.md5(password.encode()).hexdigest()


def create_temp_file():
    """
    创建临时文件
    
    ⚠️ 危险: 不安全的临时文件创建
    """
    import tempfile
    
    # CWE-377: 不安全的临时文件
    path = tempfile.mktemp()
    with open(path, 'w') as f:
        f.write("temp data")
    return path


# 更多的安全问题示例

def bare_except_example():
    """裸except示例"""
    try:
        risky_operation()
    except:  # 裸except
        pass


def none_comparison(value):
    """None比较示例"""
    if value == None:  # 应该使用 is None
        return True
    return False


def infinite_loop():
    """可能的无限循环"""
    while True:
        # 没有break条件
        do_something()


def unclosed_resource():
    """未关闭的资源"""
    f = open("file.txt", "r")
    data = f.read()
    # 文件未关闭
    return data


def string_formatting(name, value):
    """不安全的字符串格式化"""
    # 应该使用f-string
    return "Name: %s, Value: %s" % (name, value)


def risky_operation():
    """占位函数"""
    pass


def do_something():
    """占位函数"""
    pass
