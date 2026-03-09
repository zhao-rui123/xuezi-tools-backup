# 安装指南

## 快速安装

### 1. 解压到指定目录
```bash
cd ~/.your-ai/workspace/skills/
tar -xzf unified-memory-universal.tar.gz
```

### 2. 安装依赖
```bash
pip install numpy jieba
```

### 3. 配置路径
复制 `config.json.template` 为 `config.json`，修改为您的实际路径。

### 4. 添加到 PATH
```bash
export PATH="$PATH:~/.your-ai/workspace/skills/unified-memory-universal/bin"
```

### 5. 测试
```bash
ums status
```

## 使用说明

```bash
ums status           # 查看状态
ums daily save       # 保存每日记忆
ums analyze          # 月度分析
ums recall store     # 存储记忆
ums recall search    # 搜索记忆
ums session save     # 保存会话
```
