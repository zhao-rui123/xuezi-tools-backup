"""
OpenClaw 零碳园区建设技能包
安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openclaw-skill",
    version="1.0.0",
    author="OpenClaw Team",
    description="零碳园区建设技能包 - 专业的能源计算与方案设计工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/skill-package",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        # 纯Python实现，无额外依赖
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
        ],
    },
    keywords=[
        '零碳园区',
        '能源计算',
        '节能',
        '光伏',
        '风电',
        '余热回收',
        '碳排放',
        '谐波治理',
        '建筑节能',
    ],
)
