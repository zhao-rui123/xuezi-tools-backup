#!/usr/bin/env python3
"""科学计算器 - 基础版"""
import math
import re

def calculate(expr):
    """计算表达式，支持 + - * / ^ () sin cos tan log sqrt"""
    # 替换数学函数
    expr = expr.replace('log', 'math.log10')
    expr = expr.replace('sin', 'math.sin')
    expr = expr.replace('cos', 'math.cos')
    expr = expr.replace('tan', 'math.tan')
    expr = expr.replace('sqrt', 'math.sqrt')
    expr = expr.replace('pi', 'math.pi')
    expr = expr.replace('e', 'math.e')
    expr = expr.replace('^', '**')

    # 安全检查：只允许数字和数学符号
    safe_chars = set('0123456789 +-*/().,mathlogsinconfigpi')
    if any(c not in safe_chars and not c.isalnum() for c in expr):
        return "错误：包含无效字符"

    try:
        result = eval(expr, {"__builtins__": {}}, {"math": math})
        return f"{result}"
    except ZeroDivisionError:
        return "错误：除数不能为零"
    except Exception as e:
        return f"错误：{e}"

def main():
    print("=" * 40)
    print("  🔢 科学计算器")
    print("  支持: + - * / ^ () sqrt sin cos tan log")
    print("  示例: sqrt(16) + sin(pi/2) * 2")
    print("  输入 quit 退出")
    print("=" * 40)

    while True:
        try:
            user_input = input("\n>>> ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见！👋")
                break
            if not user_input:
                continue
            result = calculate(user_input)
            print(f"= {result}")
        except KeyboardInterrupt:
            print("\n再见！👋")
            break

if __name__ == "__main__":
    main()
