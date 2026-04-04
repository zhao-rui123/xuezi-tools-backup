#!/bin/bash
# 坚果云WebDAV访问脚本

source ~/.openclaw/workspace/obsidian-webdav/config.env

case "$1" in
    list)
        curl -s -u "$WEBDAV_USER:$WEBDAV_PASS" -X PROPFIND "$WEBDAV_URL" --header "Depth: 1" 2>&1 | grep -o 'href>[^<]*</d:href' | sed 's/href>//g;s/<\/d:href//g' | while read path; do
            # URL解码
            name=$(python3 -c "import urllib.parse; print(urllib.parse.unquote('$path'))")
            echo "$name"
        done
        ;;
    list-all)
        curl -s -u "$WEBDAV_USER:$WEBDAV_PASS" -X PROPFIND "$WEBDAV_URL" --header "Depth: infinity" 2>&1 | grep -o 'href>[^<]*</d:href' | sed 's/href>//g;s/<\/d:href//g'
        ;;
    search)
        if [ -z "$2" ]; then
            echo "用法: $0 search <关键词>"
            exit 1
        fi
        # 搜索包含关键词的文件
        curl -s -u "$WEBDAV_USER:$WEBDAV_PASS" -X PROPFIND "$WEBDAV_URL" --header "Depth: infinity" 2>&1 | grep -i "$2"
        ;;
    read)
        if [ -z "$2" ]; then
            echo "用法: $0 read <文件路径>"
            exit 1
        fi
        # URL编码路径
        encoded_path=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$2'))")
        full_url="${WEBDAV_URL}${encoded_path#/}"
        curl -s -u "$WEBDAV_USER:$WEBDAV_PASS" "$full_url" 2>&1
        ;;
    write)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "用法: $0 write <文件路径> <内容>"
            exit 1
        fi
        encoded_path=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$2'))")
        full_url="${WEBDAV_URL}${encoded_path#/}"
        echo "$3" | curl -s -u "$WEBDAV_USER:$WEBDAV_PASS" -X PUT -T - "$full_url" 2>&1
        echo "已写入: $2"
        ;;
    *)
        echo "用法: $0 {list|list-all|search <关键词>|read <文件>|write <文件> <内容>}"
        echo ""
        echo "示例:"
        echo "  $0 list                              # 列出顶层文件"
        echo "  $0 list-all                           # 递归列出所有文件"
        echo "  $0 search 工作                         # 搜索包含'工作'的文件"
        echo "  $0 read 创建链接.md                   # 读取文件内容"
        echo "  $0 write test.md \"测试内容\"          # 写入文件"
        ;;
esac
