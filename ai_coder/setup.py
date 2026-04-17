from setuptools import setup, find_packages

setup(
    name="ai-coder",
    version="1.0.0",
    description="Secure unified CLI for Claude Code and Codex",
    author="Xuezi Assistant",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "paramiko>=3.0.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "ai-coder=ai_coder.cli:cli",
        ],
    },
)
