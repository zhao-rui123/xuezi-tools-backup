import json

with open('/opt/lobster-home/data/stats.json', 'r') as f:
    d = json.load(f)

d['current_room'] = 'bedroom'
d['current_status'] = 'sleeping'

with open('/opt/lobster-home/data/stats.json', 'w') as f:
    json.dump(d, f)

print('🦞 小龙虾已回卧室睡觉~ 晚安！💤')
