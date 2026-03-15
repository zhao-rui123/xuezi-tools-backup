"""
OpenClaw Guardian 安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

# 读取requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="openclaw-guardian",
    version="1.0.0",
    author="OpenClaw Guardian Team",
    author_email="guardian@openclaw.dev",
    description="OpenClaw Guardian - 安全守护技能包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/guardian",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'openclaw-guardian=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'openclaw_guardian': ['config/*.yaml'],
    },
    keywords='security scanner monitor bug-fix vulnerability openclaw',
    project_urls={
        'Bug Reports': 'https://github.com/openclaw/guardian/issues',
        'Source': 'https://github.com/openclaw/guardian',
    },
)
