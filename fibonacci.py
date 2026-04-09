#!/usr/bin/env python3
"""计算斐波那契数列第20项"""

def fibonacci(n):
    """计算斐波那契数列第n项（1-indexed）"""
    if n <= 0:
        return 0
    if n == 1 or n == 2:
        return 1
    a, b = 1, 1
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b

result = fibonacci(20)
print(f"斐波那契数列第20项 = {result}")
