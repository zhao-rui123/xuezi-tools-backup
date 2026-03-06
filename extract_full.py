import re

# Read the source JS file
with open('/tmp/y3_data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Count provinces
provinces = re.findall(r'name:"([^"]+)"', content)
print(f"Total provinces found: {len(provinces)}")
for i, p in enumerate(provinces, 1):
    print(f"{i}. {p}")
