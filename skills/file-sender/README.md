# 文件发送技能

## 用途
发送文件到指定群聊（雪子和我的专属群聊）

## 使用方法

```javascript
// 发送文件到群聊
const fileSender = require('./skills/file-sender');

// 发送文件
await fileSender.sendFile('/path/to/file.xlsx', '可选的描述文字');
```

或者直接使用工具：
```bash
# 通过消息工具发送
message send --channel feishu --target chat:oc_aff1ecbfd382d2235daf1d60c922f041 --file /path/to/file
```

## 配置

群聊ID: `oc_aff1ecbfd382d2235daf1d60c922f041`

## 支持的文件类型
- Excel (.xlsx, .xls)
- Word (.docx, .doc)
- PDF (.pdf)
- 图片 (.png, .jpg, .jpeg, .gif)
- 文本 (.txt, .md)
- 压缩包 (.zip, .tar.gz)

## 示例

### 发送测算结果
```javascript
const fileSender = require('./skills/file-sender');
await fileSender.sendFile(
  '/root/.openclaw/workspace/江西10MWh储能项目测算.xlsx',
  '江西10MWh工商业储能项目测算结果'
);
```

### 发送多个文件
```javascript
const fileSender = require('./skills/file-sender');
await fileSender.sendFiles([
  { path: '/path/to/file1.xlsx', caption: '文件1说明' },
  { path: '/path/to/file2.xlsx', caption: '文件2说明' }
]);
```
