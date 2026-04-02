# image-understand - Claude Code 图像理解

## 功能
通过 Claude Code + MiniMax MCP 的 `understand_image` 工具进行图像识别。

**优势**：比 Tesseract OCR 准确率高很多，特别适合复杂图表、截图、手写文字、模糊图片等。

## 使用方法

### 方式1：直接调用 Python 脚本
```bash
python3 ~/.openclaw/workspace/skills/image-understand/skill.py <图片路径> [问题]

# 示例：提取图中所有文字
python3 ~/.openclaw/workspace/skills/image-understand/skill.py screenshot.png "请提取图中所有文字"

# 示例：提取表格数据
python3 ~/.openclaw/workspace/skills/image-understand/skill.py table.jpg "这是一个表格，请提取所有行列数据"

# 示例：识别中文内容
python3 ~/.openclaw/workspace/skills/image-understand/skill.py chinese.png "请提取图中所有中文文字"
```

### 方式2：在我（主Agent）中调用
```python
# 在对话中直接说"用识图能力分析这张图片"
```

## 适用场景
- 📊 表格图片 → 提取行列数据出 Excel
- 📄 文档截图 → 提取文字内容
- 📈 图表图片 → 提取图表中的数据
- 🖼️ 模糊图片 → 修复+识别
- ✍️ 手写文字 → 识别内容

## 不适用场景
- 简单二维码/条形码（用 zxing 或 qrencode）
- 纯色背景大字（用 Tesseract OCR 更快更省）

## 输出格式
Claude Code + MiniMax MCP 返回结构化的文字描述，表格数据以 Markdown 表格呈现。

## 注意事项
- 120秒超时，适合大多数图片
- 支持 PNG、JPG、JPEG、GIF、WebP 等格式
- base64 编码后传输，建议图片小于 10MB
