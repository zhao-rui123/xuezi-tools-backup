#!/usr/bin/env python3
import urllib.request
import json

url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=hk00981,day,,,60,qfq"
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
response = urllib.request.urlopen(req, timeout=10)
data = json.loads(response.read().decode('utf-8'))

print("数据结构:")
print(json.dumps(data, indent=2)[:2000])
