/** 像素风小龙虾房子看板 v2.0 - JavaScript **/

// 房间配置
const ROOMS = {
    study: {
        name: '书房',
        emoji: '📚',
        activity: '思考中',
        mood: '专注',
        speech: '看看书，充充电~',
        emotion: '🤔',
        color: '#8E44AD'
    },
    workspace: {
        name: '工作室',
        emoji: '💻',
        activity: '工作中',
        mood: '努力',
        speech: '敲代码，冲冲冲！',
        emotion: '💪',
        color: '#3498DB'
    },
    gameroom: {
        name: '游戏室',
        emoji: '🎮',
        activity: '游戏中',
        mood: '兴奋',
        speech: '再来一把！',
        emotion: '😤',
        color: '#E74C3C'
    },
    bedroom: {
        name: '休息室',
        emoji: '🛏️',
        activity: '休息中',
        mood: '放松',
        speech: '休息一下~',
        emotion: '😌',
        color: '#1ABC9C'
    },
    bathroom: {
        name: '卫生间',
        emoji: '🚽',
        activity: '摸鱼中',
        mood: '偷偷乐',
        speech: '带薪如厕...🤫',
        emotion: '😏',
        color: '#95A5A6'
    },
    kitchen: {
        name: '厨房',
        emoji: '🍜',
        activity: '吃饭中',
        mood: '满足',
        speech: '干饭时间！',
        emotion: '😋',
        color: '#F39C12'
    },
    playground: {
        name: '操场',
        emoji: '🏃',
        activity: '运动中',
        mood: '活力',
        speech: '运动一下！',
        emotion: '🔥',
        color: '#27AE60'
    }
};

// 状态映射
const STATUS_TO_ROOM = {
    working: 'workspace',
    thinking: 'study',
    gaming: 'gameroom',
    resting: 'bedroom',
    sleeping: 'bedroom',
    slacking: 'bathroom',
    eating: 'kitchen',
    exercising: 'playground'
};

// 当前状态
let currentState = {
    room: 'bedroom',
    status: 'resting',
    lastActivity: new Date(),
    tasksCompleted: 0,
    tokensUsed: 0,
    workTimeSeconds: 0,
    roomTime: {}, // 每个房间的停留时间
    tasks: [] // 今日任务列表
};

// 计时器
let restTimer = null;
let gamingTimer = null;
const REST_DELAY = 5 * 60 * 1000; // 5分钟
const GAMING_DELAY = 10 * 60 * 1000; // 10分钟开始打游戏

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    initDashboard();
    await loadData(); // 等待数据加载完成
    initCharts();
    startAutoUpdate();
    
    // 数据加载完成后移动小龙虾到正确位置
    moveLobsterToRoom(currentState.room, false);
    updateDisplay();
});

// 初始化面板
function initDashboard() {
    // 初始化房间时间
    Object.keys(ROOMS).forEach(room => {
        if (!currentState.roomTime[room]) {
            currentState.roomTime[room] = 0;
        }
    });
}

// 移动小龙虾到房间
function moveLobsterToRoom(roomId, animate = true) {
    const room = document.getElementById(`room-${roomId}`);
    const lobster = document.getElementById('lobster');
    
    if (!room || !lobster) return;
    
    // 高亮房间
    document.querySelectorAll('.room').forEach(r => r.classList.remove('active'));
    room.classList.add('active');
    
    // 计算位置
    const houseRect = document.getElementById('house').getBoundingClientRect();
    const roomRect = room.getBoundingClientRect();
    
    // 计算相对位置（居中）
    const left = roomRect.left - houseRect.left + roomRect.width / 2 - 30;
    const top = roomRect.top - houseRect.top + roomRect.height / 2 - 30;
    
    // 移动小龙虾
    if (animate) {
        lobster.classList.add('walking');
        lobster.style.transition = 'all 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
    } else {
        lobster.style.transition = 'none';
    }
    
    lobster.style.left = `${left}px`;
    lobster.style.top = `${top}px`;
    
    // 停止走路动画
    if (animate) {
        setTimeout(() => {
            lobster.classList.remove('walking');
        }, 1500);
    }
    
    // 更新当前状态
    currentState.room = roomId;
    currentState.lastActivity = new Date();
    
    updateDisplay();
    saveData();
}

// 切换状态
function switchStatus(status) {
    const roomId = STATUS_TO_ROOM[status];
    if (!roomId) return;
    
    const prevStatus = currentState.status;
    currentState.status = status;
    
    // 移动到新房间
    moveLobsterToRoom(roomId, true);
    
    // 特殊状态处理
    if (status === 'working') {
        stopRestTimer();
        stopGamingTimer();
    } else if (status === 'resting') {
        startRestTimer();
        startGamingTimer();
    }
    
    // 更新显示
    updateDisplay();
    
    // 摸鱼检测
    if (status !== 'working' && status !== 'exercising') {
        checkForSlacking();
    }
}

// 检查是否要摸鱼
function checkForSlacking() {
    // 10%概率去卫生间
    if (Math.random() < 0.1) {
        setTimeout(() => {
            switchStatus('slacking');
            showSpeech('带薪如厕中...🤫', 5000);
            
            // 3-5分钟后回来
            setTimeout(() => {
                switchStatus('resting');
            }, 3000 + Math.random() * 2000);
        }, 1000);
    }
}

// 开始任务
function startTask(taskName) {
    currentState.currentTask = taskName;
    currentState.taskStartTime = new Date();
    switchStatus('working');
    showSpeech(`开始工作：${taskName}`);
}

// 完成任务
function completeTask(tokensUsed = 0) {
    const taskDuration = currentState.taskStartTime 
        ? Math.floor((new Date() - currentState.taskStartTime) / 1000)
        : 0;
    
    // 记录任务
    currentState.tasks.push({
        name: currentState.currentTask,
        duration: taskDuration,
        tokens: tokensUsed,
        completedAt: new Date().toISOString()
    });
    
    currentState.tasksCompleted++;
    currentState.tokensUsed += tokensUsed;
    currentState.workTimeSeconds += taskDuration;
    
    // 判断任务强度
    if (taskDuration > 1800) { // 超过30分钟
        switchStatus('exercising');
        showSpeech('高强度工作完成！运动一下！');
    } else {
        // 随机选择休息状态
        const restStatuses = ['resting', 'thinking', 'eating'];
        const hour = new Date().getHours();
        
        if (hour >= 11 && hour <= 13) {
            switchStatus('eating');
        } else {
            const randomStatus = restStatuses[Math.floor(Math.random() * restStatuses.length)];
            switchStatus(randomStatus);
        }
    }
    
    currentState.currentTask = null;
    currentState.taskStartTime = null;
    
    saveData();
    updateCharts();
}

// 更新显示
function updateDisplay() {
    const room = ROOMS[currentState.room];
    if (!room) return;
    
    // 更新统计
    document.getElementById('task-count').textContent = currentState.tasksCompleted;
    document.getElementById('token-count').textContent = formatNumber(currentState.tokensUsed);
    document.getElementById('work-time').textContent = formatTime(currentState.workTimeSeconds);
    
    // 更新位置
    const locationBadge = document.getElementById('current-room');
    locationBadge.textContent = room.name;
    locationBadge.style.background = room.color;
    
    // 更新活动
    document.getElementById('current-activity').textContent = room.activity;
    document.getElementById('mood').textContent = room.mood;
    
    // 更新情绪
    document.getElementById('emotion').textContent = room.emotion;
    
    // 更新对话
    document.getElementById('speech-text').textContent = room.speech;
    
    // 更新时间
    updateLastActivity();
}

// 显示临时对话
function showSpeech(text, duration = 3000) {
    const speechText = document.getElementById('speech-text');
    const originalText = speechText.textContent;
    
    speechText.textContent = text;
    
    setTimeout(() => {
        speechText.textContent = originalText;
    }, duration);
}

// 更新活动时间
function updateLastActivity() {
    const diff = Math.floor((new Date() - new Date(currentState.lastActivity)) / 1000);
    
    let text;
    if (diff < 60) {
        text = '刚刚';
    } else if (diff < 3600) {
        text = `${Math.floor(diff / 60)}分钟前`;
    } else {
        text = `${Math.floor(diff / 3600)}小时前`;
    }
    
    document.getElementById('last-activity').textContent = text;
}

// 休息计时器
function startRestTimer() {
    stopRestTimer();
    restTimer = setTimeout(() => {
        if (currentState.status === 'working') {
            switchStatus('resting');
            showSpeech('工作很久了，休息一下~');
        }
    }, REST_DELAY);
}

function stopRestTimer() {
    if (restTimer) {
        clearTimeout(restTimer);
        restTimer = null;
    }
}

// 游戏计时器
function startGamingTimer() {
    stopGamingTimer();
    gamingTimer = setTimeout(() => {
        if (currentState.status === 'resting') {
            switchStatus('gaming');
            showSpeech('休息够了，打会游戏！');
        }
    }, GAMING_DELAY);
}

function stopGamingTimer() {
    if (gamingTimer) {
        clearTimeout(gamingTimer);
        gamingTimer = null;
    }
}

// 图表初始化
function initCharts() {
    // 任务趋势图
    const tasksCtx = document.getElementById('tasks-chart');
    if (tasksCtx) {
        window.tasksChart = new Chart(tasksCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '完成任务数',
                    data: [],
                    borderColor: '#F39C12',
                    backgroundColor: 'rgba(243, 156, 18, 0.2)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#ECF0F1' } },
                    x: { ticks: { color: '#ECF0F1' } }
                }
            }
        });
    }
    
    // Token消耗图
    const tokensCtx = document.getElementById('tokens-chart');
    if (tokensCtx) {
        window.tokensChart = new Chart(tokensCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Token消耗',
                    data: [],
                    backgroundColor: '#E74C3C'
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#ECF0F1' } },
                    x: { ticks: { color: '#ECF0F1' } }
                }
            }
        });
    }
    
    // 房间停留时间图
    const roomsCtx = document.getElementById('rooms-chart');
    if (roomsCtx) {
        window.roomsChart = new Chart(roomsCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#8E44AD', '#3498DB', '#E74C3C', 
                        '#1ABC9C', '#95A5A6', '#F39C12', '#27AE60'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#ECF0F1', font: { size: 12 } }
                    }
                }
            }
        });
    }
    
    updateCharts();
}

// 更新图表
function updateCharts() {
    // 模拟7天数据
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    const taskData = [5, 8, 6, 9, 7, 4, currentState.tasksCompleted || 3];
    const tokenData = [8000, 12000, 9500, 15000, 11000, 6000, currentState.tokensUsed || 5000];
    
    // 更新任务图
    if (window.tasksChart) {
        window.tasksChart.data.labels = days;
        window.tasksChart.data.datasets[0].data = taskData;
        window.tasksChart.update();
    }
    
    // 更新Token图
    if (window.tokensChart) {
        window.tokensChart.data.labels = days;
        window.tokensChart.data.datasets[0].data = tokenData;
        window.tokensChart.update();
    }
    
    // 更新房间图
    if (window.roomsChart) {
        const roomNames = Object.values(ROOMS).map(r => r.name);
        const roomTimes = Object.keys(ROOMS).map(r => 
            Math.floor((currentState.roomTime[r] || 0) / 60)
        );
        window.roomsChart.data.labels = roomNames;
        window.roomsChart.data.datasets[0].data = roomTimes;
        window.roomsChart.update();
    }
}

// 保存数据
function saveData() {
    localStorage.setItem('agentDashboardV2', JSON.stringify(currentState));
}

// 加载数据
async function loadData() {
    // 优先从服务器加载
    try {
        const response = await fetch('data/stats.json?t=' + Date.now());
        if (response.ok) {
            const serverData = await response.json();
            
            // 使用服务器状态
            if (serverData.current_room) {
                currentState.room = serverData.current_room;
                currentState.status = serverData.current_status || 'resting';
            }
            
            // 使用服务器统计
            if (serverData.today) {
                currentState.tasksCompleted = serverData.today.tasks_completed || 0;
                currentState.tokensUsed = serverData.today.tokens_used || 0;
                currentState.workTimeSeconds = serverData.today.work_time_seconds || 0;
            }
            
            console.log('🦞 已从服务器加载状态:', currentState.room);
        }
    } catch (e) {
        console.log('无法从服务器加载，使用本地存储');
    }
    
    // 本地存储作为补充
    const saved = localStorage.getItem('agentDashboardV2');
    if (saved) {
        const data = JSON.parse(saved);
        const today = new Date().toDateString();
        const savedDate = new Date(data.lastActivity || Date.now()).toDateString();
        
        // 如果不是同一天，不覆盖服务器数据
        if (today === savedDate) {
            // 合并数据（服务器优先）
            currentState = { ...data, ...currentState };
        }
    }
    
    // 检查深夜
    const hour = new Date().getHours();
    if (hour >= 23 || hour < 7) {
        currentState.status = 'sleeping';
        currentState.room = 'bedroom';
    }
}
    if (hour >= 23 || hour < 7) {
        currentState.status = 'sleeping';
        moveLobsterToRoom('bedroom', false);
    }
}

// 归档旧数据
function archiveOldData(data) {
    // 这里可以将历史数据发送到服务器保存
    console.log('归档数据:', data);
}

// 自动更新
function startAutoUpdate() {
    // 每秒更新时间
    setInterval(updateLastActivity, 1000);
    
    // 每分钟记录房间时间
    setInterval(() => {
        if (currentState.room) {
            currentState.roomTime[currentState.room] = 
                (currentState.roomTime[currentState.room] || 0) + 60;
            saveData();
        }
    }, 60000);
    
    // 每5分钟更新图表
    setInterval(updateCharts, 300000);
}

// 工具函数
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
}

// API导出
window.AgentDashboard = {
    startTask,
    completeTask,
    switchStatus,
    getState: () => currentState
};
