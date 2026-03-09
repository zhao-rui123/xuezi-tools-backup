/** 像素风小龙虾之家 - 四室两厅布局 **/

// 房间配置 - 新家布局
const ROOMS = {
    bedroom: {
        name: '卧室',
        emoji: '🛏️',
        activity: '睡觉中',
        mood: '放松',
        speech: '睡个好觉，明天继续加油！',
        emotion: '😴',
        color: '#9B59B6'
    },
    gameroom: {
        name: '游戏室',
        emoji: '🎮',
        activity: '游戏中',
        mood: '兴奋',
        speech: '再来一把！这局一定赢！',
        emotion: '😤',
        color: '#E74C3C'
    },
    livingroom: {
        name: '客厅',
        emoji: '📺',
        activity: '看电视',
        mood: '悠闲',
        speech: '躺平看剧，真舒服~',
        emotion: '😌',
        color: '#3498DB'
    },
    workspace: {
        name: '工作室',
        emoji: '💻',
        activity: '工作中',
        mood: '专注',
        speech: '努力搬砖，冲冲冲！',
        emotion: '💪',
        color: '#1ABC9C'
    },
    dining: {
        name: '餐厅',
        emoji: '🍽️',
        activity: '吃饭中',
        mood: '满足',
        speech: '干饭时间！真香！',
        emotion: '😋',
        color: '#F39C12'
    },
    bathroom: {
        name: '卫生间',
        emoji: '🚽',
        activity: '摸鱼中',
        mood: '偷偷乐',
        speech: '带薪如厕，快乐翻倍~',
        emotion: '😏',
        color: '#95A5A6'
    },
    playground: {
        name: '运动场',
        emoji: '🏃',
        activity: '运动中',
        mood: '活力',
        speech: '运动一下，更健康！',
        emotion: '🔥',
        color: '#27AE60'
    }
};

// 状态到房间的映射
const STATUS_TO_ROOM = {
    sleeping: 'bedroom',
    resting: 'livingroom',
    gaming: 'gameroom',
    working: 'workspace',
    thinking: 'workspace',
    eating: 'dining',
    slacking: 'bathroom',
    exercising: 'playground'
};

// 当前状态
let currentState = {
    room: 'livingroom',  // 默认在客厅
    status: 'resting',
    lastActivity: new Date(),
    tasksCompleted: 0,
    tokensUsed: 0,
    workTimeSeconds: 0,
    roomTime: {},
    tasks: []
};

// 计时器
let restTimer = null;
let gamingTimer = null;
let slackingTimer = null;

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    initDashboard();
    await loadData();
    startAutoUpdate();
    
    // 初始化位置
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
    
    if (!room || !lobster) {
        console.error('Room or lobster not found:', roomId);
        return;
    }
    
    // 高亮房间
    document.querySelectorAll('.room, .playground-area').forEach(r => r.classList.remove('active'));
    room.classList.add('active');
    
    // 计算位置
    const houseRect = document.querySelector('.game-container').getBoundingClientRect();
    const roomRect = room.getBoundingClientRect();
    
    // 相对位置（房间中心）
    const left = roomRect.left - houseRect.left + roomRect.width / 2 - 25;
    const top = roomRect.top - houseRect.top + roomRect.height / 2 - 25;
    
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
    
    currentState.status = status;
    
    // 移动到新房间
    moveLobsterToRoom(roomId, true);
    
    // 特殊状态处理
    if (status === 'working') {
        stopAllTimers();
    } else if (status === 'resting') {
        startRestTimer();
        startGamingTimer();
    } else if (status === 'gaming') {
        startSlackingTimer();  // 打游戏也可能去摸鱼
    }
    
    updateDisplay();
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
        const hour = new Date().getHours();
        
        if (hour >= 11 && hour <= 13 || hour >= 17 && hour <= 19) {
            switchStatus('eating');
        } else {
            // 随机：看电视、打游戏、发呆
            const activities = ['resting', 'gaming'];
            const randomActivity = activities[Math.floor(Math.random() * activities.length)];
            switchStatus(randomActivity);
        }
    }
    
    currentState.currentTask = null;
    currentState.taskStartTime = null;
    
    // 摸鱼检测
    checkForSlacking();
    
    saveData();
}

// 摸鱼检测
function checkForSlacking() {
    if (Math.random() < 0.15) {  // 15%概率
        setTimeout(() => {
            switchStatus('slacking');
            showSpeech('带薪如厕中...🤫', 5000);
            
            // 3-5分钟后回来
            setTimeout(() => {
                const activities = ['resting', 'gaming'];
                switchStatus(activities[Math.floor(Math.random() * activities.length)]);
            }, 3000 + Math.random() * 2000);
        }, 1000);
    }
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

// 更新时间
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

// 计时器管理
function startRestTimer() {
    stopAllTimers();
    restTimer = setTimeout(() => {
        if (currentState.status === 'working') {
            switchStatus('resting');
            showSpeech('工作很久了，休息一下~');
        }
    }, 5 * 60 * 1000); // 5分钟
}

function startGamingTimer() {
    gamingTimer = setTimeout(() => {
        if (currentState.status === 'resting') {
            switchStatus('gaming');
            showSpeech('休息够了，打会游戏！');
        }
    }, 10 * 60 * 1000); // 10分钟
}

function startSlackingTimer() {
    slackingTimer = setTimeout(() => {
        if (currentState.status === 'gaming' && Math.random() < 0.3) {
            switchStatus('slacking');
            showSpeech('游戏打累了，去方便一下...');
        }
    }, 5 * 60 * 1000);
}

function stopAllTimers() {
    if (restTimer) clearTimeout(restTimer);
    if (gamingTimer) clearTimeout(gamingTimer);
    if (slackingTimer) clearTimeout(slackingTimer);
    restTimer = gamingTimer = slackingTimer = null;
}

// 加载数据
async function loadData() {
    // 优先从服务器加载
    try {
        const response = await fetch('data/stats.json?t=' + Date.now());
        if (response.ok) {
            const serverData = await response.json();
            
            if (serverData.current_room && ROOMS[serverData.current_room]) {
                currentState.room = serverData.current_room;
                currentState.status = serverData.current_status || 'resting';
            }
            
            if (serverData.today) {
                currentState.tasksCompleted = serverData.today.tasks_completed || 0;
                currentState.tokensUsed = serverData.today.tokens_used || 0;
                currentState.workTimeSeconds = serverData.today.work_time_seconds || 0;
            }
        }
    } catch (e) {
        console.log('使用默认状态');
    }
    
    // 检查深夜
    const hour = new Date().getHours();
    if (hour >= 23 || hour < 7) {
        currentState.status = 'sleeping';
        currentState.room = 'bedroom';
    }
}

// 保存数据
function saveData() {
    localStorage.setItem('lobsterHome', JSON.stringify(currentState));
}

// 自动更新
function startAutoUpdate() {
    setInterval(updateLastActivity, 1000);
    
    setInterval(() => {
        if (currentState.room) {
            currentState.roomTime[currentState.room] = 
                (currentState.roomTime[currentState.room] || 0) + 60;
        }
        saveData();
    }, 60000);
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
window.LobsterHome = {
    startTask,
    completeTask,
    switchStatus,
    getState: () => currentState
};
