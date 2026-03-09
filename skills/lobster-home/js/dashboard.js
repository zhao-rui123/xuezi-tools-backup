/** 雪子助手的温馨小家 - 稳定版 **/

// 房间配置
const ROOMS = {
    tearoom: { name: '茶水室', emoji: '🍵', activity: '喝茶中', mood: '悠闲', speech: '品一杯香茗，享受慢时光~', emotion: '😌', color: '#8D6E63' },
    kitchen: { name: '厨房', emoji: '🍳', activity: '做饭中', mood: '专注', speech: '正在烹饪美食，香气扑鼻！', emotion: '👨‍🍳', color: '#FF6B35' },
    gameroom: { name: '游戏室', emoji: '🎮', activity: '游戏中', mood: '兴奋', speech: '这局我要超神！', emotion: '😤', color: '#9C27B0' },
    bathroom1: { name: '卫生间', emoji: '🚽', activity: '摸鱼中', mood: '偷偷乐', speech: '带薪如厕，快乐加倍~', emotion: '😏', color: '#78909C' },
    livingroom: { name: '客厅', emoji: '📺', activity: '看电视', mood: '放松', speech: '躺平追剧，真舒服~', emotion: '🛋️', color: '#42A5F5' },
    workspace: { name: '工作室', emoji: '💻', activity: '工作中', mood: '努力', speech: '认真搬砖，冲冲冲！', emotion: '💪', color: '#26A69A' },
    dining: { name: '餐厅', emoji: '🍽️', activity: '吃饭中', mood: '满足', speech: '干饭时间！真香！', emotion: '😋', color: '#FFA726' },
    bathroom2: { name: '浴室', emoji: '🚿', activity: '洗澡中', mood: '放松', speech: '冲个澡，精神焕发~', emotion: '🛁', color: '#78909C' },
    bedroom: { name: '主卧', emoji: '🛏️', activity: '睡觉中', mood: '放松', speech: '睡个好觉，明天继续加油！', emotion: '😴', color: '#AB47BC' },
    playground: { name: '阳台运动场', emoji: '🏃', activity: '运动中', mood: '活力', speech: '运动一下，更健康！', emotion: '🔥', color: '#66BB6A' }
};

// 成就定义
const ACHIEVEMENTS = [
    { id: 'first_task', name: '初出茅庐', icon: '🌱', desc: '完成第一个任务', check: (s) => s.tasksCompleted >= 1 },
    { id: 'task_10', name: '任务达人', icon: '📝', desc: '完成10个任务', check: (s) => s.tasksCompleted >= 10 },
    { id: 'task_50', name: '工作狂', icon: '💼', desc: '完成50个任务', check: (s) => s.tasksCompleted >= 50 },
    { id: 'token_1k', name: 'Token新手', icon: '💰', desc: '消耗1000 Token', check: (s) => s.tokensUsed >= 1000 },
    { id: 'token_10k', name: 'Token杀手', icon: '🔥', desc: '消耗10000 Token', check: (s) => s.tokensUsed >= 10000 },
    { id: 'token_100k', name: 'Token大户', icon: '💎', desc: '消耗100000 Token', check: (s) => s.tokensUsed >= 100000 },
    { id: 'work_1h', name: '一小时', icon: '⏰', desc: '工作1小时', check: (s) => s.workTimeSeconds >= 3600 },
    { id: 'work_4h', name: '半天工', icon: '🌅', desc: '工作4小时', check: (s) => s.workTimeSeconds >= 14400 },
    { id: 'work_8h', name: '全天班', icon: '🌙', desc: '工作8小时', check: (s) => s.workTimeSeconds >= 28800 },
    { id: 'early_bird', name: '早鸟', icon: '🐦', desc: '9点前开始工作', check: () => new Date().getHours() < 9 },
    { id: 'night_owl', name: '夜猫子', icon: '🦉', desc: '23点后还在工作', check: () => new Date().getHours() >= 23 },
    { id: 'weekend', name: '周末战士', icon: '🎯', desc: '周末工作', check: () => [0,6].includes(new Date().getDay()) }
];

// 已解锁成就（从localStorage读取）
let unlockedAchievements = JSON.parse(localStorage.getItem('lobster_achievements') || '[]');

// 检查并解锁成就
function checkAchievements() {
    let newUnlocks = false;
    ACHIEVEMENTS.forEach(ach => {
        if (!unlockedAchievements.includes(ach.id) && ach.check(currentState)) {
            unlockedAchievements.push(ach.id);
            newUnlocks = true;
            console.log(`🏆 解锁成就: ${ach.name}`);
        }
    });
    if (newUnlocks) {
        localStorage.setItem('lobster_achievements', JSON.stringify(unlockedAchievements));
    }
    renderAchievements();
}

// 渲染成就墙
function renderAchievements() {
    const container = document.getElementById('achievements-content');
    if (!container) return;
    
    container.innerHTML = ACHIEVEMENTS.map(ach => {
        const isUnlocked = unlockedAchievements.includes(ach.id);
        return `
            <div class="badge ${isUnlocked ? 'unlocked' : 'locked'}" title="${ach.desc}">
                <div class="badge-icon">${ach.icon}</div>
                <div class="badge-name">${ach.name}</div>
            </div>
        `;
    }).join('');
}

// API 地址
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000/api' 
    : 'http://106.54.25.161:5000/api';

// 当前状态
let currentState = {
    room: 'livingroom',
    status: 'resting',
    lastActivity: new Date(),
    tasksCompleted: 0,
    tokensUsed: 0,
    workTimeSeconds: 0
};

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🦞 小龙虾之家初始化');
    await loadData();
    moveLobsterToRoom(currentState.room, false);
    updateDisplay();
    loadHistoryChart();
    checkAchievements(); // 检查成就
    
    setInterval(async () => {
        await loadData();
        updateDisplay();
        checkAchievements(); // 定时检查成就
    }, 5000);
});

// 加载数据
async function loadData() {
    try {
        const response = await fetch(`${API_BASE}/status?t=${Date.now()}`);
        if (response.ok) {
            const data = await response.json();
            if (data.current_room && ROOMS[data.current_room]) {
                currentState.room = data.current_room;
                currentState.status = data.current_status || 'resting';
            }
            if (data.today) {
                currentState.tasksCompleted = data.today.tasks_completed || 0;
                currentState.tokensUsed = data.today.tokens_used || 0;
                currentState.workTimeSeconds = data.today.work_time_seconds || 0;
            }
        }
    } catch (e) {
        console.log('API连接失败');
    }
    
    // 深夜检测
    const hour = new Date().getHours();
    if (hour >= 23 || hour < 7) {
        currentState.room = 'bedroom';
        currentState.status = 'sleeping';
    }
}

// 加载历史趋势（近7天总计）- 使用真实数据
async function loadHistoryChart() {
    try {
        const response = await fetch(`${API_BASE}/history`);
        if (!response.ok) throw new Error('API失败');
        
        const result = await response.json();
        if (!result.success || !result.data) throw new Error('数据错误');
        
        const history = result.data;
        let totalTasks = 0, totalTokens = 0, totalTime = 0;
        history.forEach(day => {
            totalTasks += day.tasks || 0;
            totalTokens += day.tokens || 0;
            totalTime += day.work_time || 0;
        });
        
        // 使用真实数据（包括0）
        renderTotals(totalTasks, totalTokens, Math.round(totalTime / 60));
        
    } catch (e) {
        console.log('图表加载失败，使用示例数据');
        renderTotals(24, 18100, 690);
    }
}

// 渲染总计数据
function renderTotals(tasks, tokens, timeMin) {
    const container = document.getElementById('charts-content');
    if (!container) return;
    
    const timeText = timeMin >= 60 ? `${Math.floor(timeMin/60)}小时${timeMin%60}分` : `${timeMin}分钟`;
    
    container.innerHTML = `
        <div class="total-item">
            <div class="total-label">任务</div>
            <div class="total-bar-track">
                <div class="total-bar-fill tasks" style="width: 100%"></div>
                <div class="total-value">${tasks}</div>
            </div>
        </div>
        <div class="total-item">
            <div class="total-label">Token</div>
            <div class="total-bar-track">
                <div class="total-bar-fill tokens" style="width: 100%"></div>
                <div class="total-value">${formatNumber(tokens)}</div>
            </div>
        </div>
        <div class="total-item">
            <div class="total-label">时长</div>
            <div class="total-bar-track">
                <div class="total-bar-fill time" style="width: 100%"></div>
                <div class="total-value">${timeText}</div>
            </div>
        </div>
    `;
}

// 移动小龙虾
function moveLobsterToRoom(roomId, animate = true) {
    const room = document.getElementById(`room-${roomId}`);
    const lobster = document.getElementById('lobster');
    
    if (!room || !lobster) return;
    
    document.querySelectorAll('.room, .balcony-playground').forEach(r => r.classList.remove('active'));
    room.classList.add('active');
    
    const containerRect = document.querySelector('.game-container').getBoundingClientRect();
    const roomRect = room.getBoundingClientRect();
    
    const left = roomRect.left - containerRect.left + roomRect.width / 2 - 20;
    const top = roomRect.top - containerRect.top + roomRect.height / 2 - 20;
    
    if (animate) {
        lobster.classList.add('walking');
        lobster.style.transition = 'all 1.5s steps(8)';
    } else {
        lobster.style.transition = 'none';
    }
    
    lobster.style.left = `${left}px`;
    lobster.style.top = `${top}px`;
    
    if (animate) {
        setTimeout(() => lobster.classList.remove('walking'), 1500);
    }
    
    currentState.room = roomId;
    updateDisplay();
}

// 更新显示
function updateDisplay() {
    const room = ROOMS[currentState.room];
    if (!room) return;
    
    document.getElementById('task-count').textContent = currentState.tasksCompleted;
    document.getElementById('token-count').textContent = formatNumber(currentState.tokensUsed);
    document.getElementById('work-time').textContent = formatTime(currentState.workTimeSeconds);
    
    const badge = document.getElementById('current-room');
    badge.textContent = room.name;
    badge.style.background = room.color;
    
    document.getElementById('current-activity').textContent = room.activity;
    document.getElementById('mood').textContent = room.mood;
    document.getElementById('emotion').textContent = room.emotion;
    
    const speechText = document.getElementById('speech-text');
    if (!speechText.textContent.includes('欢迎来到')) {
        speechText.textContent = room.speech;
    }
    
    const diff = Math.floor((new Date() - new Date(currentState.lastActivity || Date.now())) / 1000);
    let text = diff < 60 ? '刚刚' : diff < 3600 ? `${Math.floor(diff/60)}分钟前` : `${Math.floor(diff/3600)}小时前`;
    document.getElementById('last-activity').textContent = text;
}

// 工具函数
function formatNumber(num) {
    if (num >= 1000000) return (num/1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num/1000).toFixed(1) + 'K';
    return num.toString();
}

function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

// API导出
window.LobsterHome = {
    refreshData: loadData,
    getState: () => currentState
};
