#!/usr/bin/env python3
"""
示例：包含各种问题的代码
用于测试代码审查和自动修复功能
"""

import os
import sys

# 硬编码敏感信息（安全问题）
API_KEY = "sk-1234567890abcdef1234567890abcdef"
DATABASE_PASSWORD = "super_secret_password_123"
SECRET_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"


def process_data(data):
    """处理数据 - 包含多个问题"""
    # 使用危险函数（安全问题）
    result = eval(data)
    
    # 使用exec（安全问题）
    exec("print('Hello')")
    
    return result


def get_user(user_id):
    """获取用户信息 - SQL注入风险"""
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # SQL注入风险（安全问题）
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    return cursor.fetchone()


def calculate_sum(numbers):
    """计算总和 - 性能问题"""
    # 低效实现（性能问题）
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total


def find_item(items, target):
    """查找项目 - 性能问题"""
    # O(n)查找（性能问题）
    for item in items:
        if item == target:
            return True
    return False


def long_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7):
    """参数过多的函数（可维护性问题）"""
    # 这是一个很长的函数，应该被拆分
    x = arg1 + arg2
    y = arg3 + arg4
    z = arg5 + arg6
    
    if x > 0:
        if y > 0:
            if z > 0:
                if arg7 > 0:
                    return x + y + z + arg7
    
    return 0


def bad_exception_handling():
    """糟糕的异常处理"""
    try:
        result = 1 / 0
    except:  # 裸except（正确性问题）
        pass  # 空的except块（正确性问题）
    
    return None


def compare_with_none(value):
    """None比较（风格问题）"""
    if value == None:  # 应该使用 is None
        return True
    
    if value != None:  # 应该使用 is not None
        return False
    
    return None


def mutable_default(arg=[]):
    """可变默认参数（正确性问题）"""
    arg.append(1)
    return arg


def list_builder(items):
    """列表构建（Pythonic问题）"""
    # 应该使用列表推导式
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result


def range_len_pattern(data):
    """range(len())模式（Pythonic问题）"""
    # 应该使用enumerate或直接迭代
    for i in range(len(data)):
        print(data[i])


def truthiness_check(value):
    """真值判断（风格问题）"""
    if value == True:  # 应该直接使用 if value:
        return True
    
    if value == False:  # 应该使用 if not value:
        return False
    
    return None


def print_debug(message):
    """使用print（最佳实践问题）"""
    print(f"DEBUG: {message}")  # 应该使用logging


def trailing_whitespace_example():
    """尾随空格示例（风格问题）"""
    x = 1    
    y = 2    
    return x + y


# TODO: 需要重构这个函数（TODO标记）
def function_needs_refactoring():
    pass


# FIXME: 这里有bug（FIXME标记）
def function_with_bug():
    return 1 / 0


class BadClass:
    """不符合规范的类"""
    
    def __init__(self):
        self.x = 1
    
    def method_with_no_self_use():
        """没有使用self的方法"""
        return 42


if __name__ == '__main__':
    # 测试代码
    print("Running example code...")
    
    # 调用有问题的函数
    result = process_data("1 + 2")
    print(f"Result: {result}")
    
    # 测试可变默认参数
    print(mutable_default())
    print(mutable_default())
    
    # 测试列表构建
    print(list_builder([1, -2, 3, -4, 5]))
