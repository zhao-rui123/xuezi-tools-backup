import json

with open('/opt/lobster-home/data/stats.json', 'r') as f:
    d = json.load(f)

d['current_room'] = 'workspace'
d['current_status'] = 'working'

with open('/opt/lobster-home/data/stats.json', 'w') as f:
    json.dump(d, f)

print('🦞 小龙虾已回到工作室，开始工作！💻')
