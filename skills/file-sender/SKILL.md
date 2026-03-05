# SKILL.md - 文件发送技能

## 名称
file-sender

## 描述
发送文件到指定群聊（雪子和我的专属群聊）

## 使用场景
- 发送测算结果Excel
- 发送分析报告Word/PDF
- 发送截图或图片
- 发送压缩包备份

## 使用方法

### 方式1：直接调用Python脚本
```bash
cd /root/.openclaw/workspace/skills/file-sender
python3 file-sender.py /path/to/file.xlsx "文件说明"
```

### 方式2：使用message工具
```bash
message send --channel feishu --target chat:oc_aff1ecbfd382d2235daf1d60c922f041 --file /path/to/file --message "说明"
```

### 方式3：在代码中调用
```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/file-sender')
from file_sender import send_file

# 发送单个文件
result = send_file('/path/to/file.xlsx', '江西10MWh测算结果')

# 批量发送
files = [
    {'path': '/path/file1.xlsx', 'caption': '文件1'},
    {'path': '/path/file2.xlsx', 'caption': '文件2'}
]
results = send_files(files)
```

## 配置

默认发送到群聊: `chat:oc_aff1ecbfd382d2235daf1d60c922f041`

## 示例

### 发送测算结果
```python
from file_sender import send_file

# 发送江西测算结果
send_file(
    '/root/.openclaw/workspace/江西10MWh储能项目测算.xlsx',
    '江西10MWh工商业储能项目测算结果'
)
```

## 注意事项
1. 文件必须存在且可读
2. 大文件可能需要较长时间上传
3. 支持的格式：xlsx, docx, pdf, png, jpg, txt, zip等
