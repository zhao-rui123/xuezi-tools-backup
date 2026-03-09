import re

with open('/usr/share/nginx/html/index.html', 'r') as f:
    content = f.read()

# 小龙虾之家卡片HTML
new_card = '''                <!-- 小龙虾之家 -->
                <a href="/my-home/" class="glass-card rounded-3xl p-8 card-hover block group tilt-card glass-refraction" style="border-top: 3px solid #ef4444;">
                    <div class="tilt-card-inner">
                        <div class="flex items-start justify-between mb-6">
                            <div class="glow-icon w-16 h-16 rounded-2xl flex items-center justify-center transition-transform group-hover:scale-110" style="background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);">
                                <span class="text-3xl">🦞</span>
                            </div>
                            <span class="text-xs font-bold text-white tag-gradient-1 px-3 py-1.5 rounded-full">AI助手</span>
                        </div>
                        <h3 class="text-2xl font-bold text-white mb-3 group-hover:text-red-300 transition-colors">小龙虾之家</h3>
                        <p class="text-slate-400 text-sm leading-relaxed">雪子助手的工作状态看板，实时追踪任务、Token消耗、成就系统</p>
                        <div class="mt-6 flex items-center text-red-400 text-sm font-medium">
                            进入看板
                            <svg class="w-4 h-4 ml-2 transition-transform group-hover:translate-x-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                            </svg>
                        </div>
                    </div>
                </a>'''

# 在其他工具板块的grid中找到下载中心卡片的结束位置
pattern = r'(进入下载中心.*?<svg.*?</svg>\s*</div>\s*</div>\s*</a>)'
match = re.search(pattern, content, re.DOTALL)

if match:
    end_pos = match.end()
    new_content = content[:end_pos] + '\n' + new_card + content[end_pos:]
    with open('/usr/share/nginx/html/index.html', 'w') as f:
        f.write(new_content)
    print('✅ 小龙虾之家已添加到主页')
else:
    print('❌ 未找到插入位置')
