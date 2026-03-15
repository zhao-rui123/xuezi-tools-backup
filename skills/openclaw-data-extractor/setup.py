"""
OpenClaw 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# 读取requirements
with open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="openclaw",
    version="1.0.0",
    description="智能数据提取技能包 - 支持PDF、Excel、图片OCR",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OpenClaw Team",
    author_email="openclaw@example.com",
    url="https://github.com/yourusername/openclaw",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "ocr": ["paddleocr>=2.6.0", "easyocr>=1.6.0"],
        "all": ["paddleocr>=2.6.0", "easyocr>=1.6.0"],
    },
    entry_points={
        "console_scripts": [
            "openclaw=openclaw.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Office/Business",
    ],
    keywords="pdf excel ocr data-extraction data-cleaning pandas",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/openclaw/issues",
        "Source": "https://github.com/yourusername/openclaw",
    },
)
