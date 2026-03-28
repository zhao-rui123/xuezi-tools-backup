# OpenClaw Makefile

.PHONY: help install install-dev test lint format clean build upload

help:
	@echo "OpenClaw 构建工具"
	@echo ""
	@echo "可用命令:"
	@echo "  make install      - 安装依赖"
	@echo "  make install-dev  - 安装开发依赖"
	@echo "  make test         - 运行测试"
	@echo "  make lint         - 代码检查"
	@echo "  make format       - 代码格式化"
	@echo "  make clean        - 清理构建文件"
	@echo "  make build        - 构建包"
	@echo "  make upload       - 上传到PyPI"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest black flake8 mypy

test:
	python -m unittest discover -s tests -v

lint:
	flake8 openclaw --max-line-length=120 --ignore=E501,W503

format:
	black openclaw --line-length=120

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -delete

build: clean
	python setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

# 开发命令
dev-test:
	python -m pytest tests/ -v --tb=short

dev-coverage:
	python -m pytest tests/ --cov=openclaw --cov-report=html

# 文档生成
docs:
	@echo "生成文档..."
	pydoc-markdown -p openclaw > docs/api.md
