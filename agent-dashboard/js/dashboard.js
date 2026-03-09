/** 像素风小龙虾任务看板 - JavaScript **/

// 状态配置
const SCENES = {
    resting: {
        name: '休息中',
        emoji: '🏠',
        speech: '休息一下，充充电~',
        emotion: '😌',
        mood: '放松',
        showProp: null
    },
    working: {
        name: '工作中',
        emoji: '💻',
        speech: '努力工作中，冲冲冲！',
        emotion: '💪',
        mood: '专注',
        showProp: 'prop-computer'
    },
    thinking: {
        name: '思考中',
        emoji: '📚',
        speech: '看看书，充充电~',
        emotion: '🤔',
        mood: '好学',
        showProp: 'prop-book'
    },
    exercising: {
        name: '运动中',
        emoji: '🏃',
        speech: '运动一下，更健康！',
        emotion: '🔥',
        mood: '活力',
        showProp: 'prop-dumbbell'
    },
    eating: {
        name: '吃饭中',
        emoji: '🍜',
        speech: '好好吃饭，才有力气工作~',
        emotion: '😋',
        mood: '满足',
        showProp: 'prop-bowl'
    },
    sleeping: {
        name: '睡觉中',
        emoji: '😴',
        speech: 'Zzz... 做个好梦',
        emotion: '💤',
        mood: '沉睡',
        showProp: null
    }
};

// 当前状态
let currentState = {
    status: 'resting',
    lastActivity: new Date(),
    tasksCompleted: 0,
    tokensUsed: 0,
    workTimeSeconds: 0,
    currentTask: null
};

// 自动休息计时器
let restTimer = null;
const REST_DELAY = 5 * 60 * 1000; // 5分钟

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    loadData();
    startAutoUpdate();
});

// 初始化面板
function initDashboard() {
    // 绑定场景切换按钮
    document.querySelectorAll('.scene-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const scene = btn.dataset.scene;
            switchScene(scene);
        });
    });
    
    // 初始化显示
    updateDisplay();
    
    // 每分钟更新工作时长
    setInterval(updateWorkTime, 60000);
}

// 切换场景
function switchScene(sceneName) {
    if (!SCENES[sceneName]) return;
    
    currentState.status = sceneName;
    currentState.lastActivity = new Date();
    
    // 更新按钮状态
    document.querySelectorAll('.scene-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.scene === sceneName);
    });
    
    // 更新显示
    updateDisplay();
    
    // 保存状态
    saveData();
    
    // 如果是工作状态，启动休息计时器
    if (sceneName === 'working') {
        startRestTimer();
    } else {
        stopRestTimer();
    }
}

// 更新显示
function updateDisplay() {
    const scene = SCENES[currentState.status];
    
    // 更新状态标签
    const statusBadge = document.getElementById('current-status');
    statusBadge.textContent = scene.name;
    statusBadge.className = `stat-value status-badge ${currentState.status}`;
    
    // 更新对话气泡
    document.getElementById('speech-text').textContent = scene.speech;
    
    // 更新情绪表情
    document.getElementById('emotion').textContent = scene.emotion;
    
    // 更新心情
    document.getElementById('mood').textContent = scene.mood;
    
    // 更新统计
    document.getElementById('task-count').textContent = currentState.tasksCompleted;
    document.getElementById('token-count').textContent = formatNumber(currentState.tokensUsed);
    
    // 更新上次活动时间
    updateLastActivity();
    
    // 显示/隐藏道具
    document.querySelectorAll('.prop').forEach(prop => {
        prop.style.display = 'none';
    });
    if (scene.showProp) {
        const prop = document.getElementById(scene.showProp);
        if (prop) prop.style.display = 'block';
    }
    
    // 根据状态调整小龙虾动画
    updateLobsterAnimation();
}

// 更新小龙虾动画
function updateLobsterAnimation() {
    const leftClaw = document.getElementById('left-claw');
    const rightClaw = document.getElementById('right-claw');
    const lobster = document.querySelector('.pixel-lobster');
    
    // 重置动画
    leftClaw.style.animation = '';
    rightClaw.style.animation = '';
    lobster.style.animation = '';
    
    switch(currentState.status) {
        case 'working':
            // 快速敲击键盘
            leftClaw.style.animation = 'type-left 0.3s ease-in-out infinite';
            rightClaw.style.animation = 'type-right 0.3s ease-in-out infinite 0.15s';
            break;
        case 'exercising':
            // 举重动作
            leftClaw.style.animation = 'lift-left 1s ease-in-out infinite';
            rightClaw.style.animation = 'lift-right 1s ease-in-out infinite';
            break;
        case 'sleeping':
            // 呼吸动画
            lobster.style.animation = 'breathe 3s ease-in-out infinite';
            break;
        case 'eating':
            // 吃饭动作
            leftClaw.style.animation = 'eat 0.8s ease-in-out infinite';
            break;
        default:
            // 默认挥手
            leftClaw.style.animation = 'wave-left 2s ease-in-out infinite';
            rightClaw.style.animation = 'wave-right 2s ease-in-out infinite';
    }
}

// 更新工作时长
function updateWorkTime() {
    if (currentState.status === 'working') {
        currentState.workTimeSeconds += 60;
        const hours = Math.floor(currentState.workTimeSeconds / 3600);
        const minutes = Math.floor((currentState.workTimeSeconds % 3600) / 60);
        document.getElementById('work-time').textContent = `${hours}h ${minutes}m`;
        saveData();
    }
}

// 更新上次活动时间
function updateLastActivity() {
    const now = new Date();
    const diff = Math.floor((now - new Date(currentState.lastActivity)) / 1000);
    
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

// 启动休息计时器
function startRestTimer() {
    stopRestTimer();
    restTimer = setTimeout(() => {
        // 5分钟无任务，自动切换到休息
        if (currentState.status === 'working') {
            switchScene('resting');
            showNotification('已经工作很久了，休息一下吧！');
        }
    }, REST_DELAY);
}

// 停止休息计时器
function stopRestTimer() {
    if (restTimer) {
        clearTimeout(restTimer);
        restTimer = null;
    }
}

// 记录完成任务
function recordTask(taskName, tokens = 0) {
    currentState.tasksCompleted++;
    currentState.tokensUsed += tokens;
    currentState.lastActivity = new Date();
    
    // 随机选择下一个状态（非工作）
    const nextStates = ['resting', 'thinking', 'exercising', 'eating'];
    const nextState = nextStates[Math.floor(Math.random() * nextStates.length)];
    switchScene(nextState);
    
    // 显示完成提示
    const messages = [
        `完成了"${taskName}"！真棒！`,
        `任务完成！休息一下吧~`,
        `又一个任务搞定！🎉`,
        `完成了！给自己点个赞！`
    ];
    document.getElementById('speech-text').textContent = 
        messages[Math.floor(Math.random() * messages.length)];
    
    saveData();
}

// 开始新任务
function startTask(taskName) {
    currentState.currentTask = taskName;
    currentState.lastActivity = new Date();
    switchScene('working');
    document.getElementById('speech-text').textContent = `开始工作：${taskName}`;
    saveData();
}

// 保存数据到本地存储
function saveData() {
    localStorage.setItem('agentDashboard', JSON.stringify(currentState));
    
    // 同时保存到服务器（如果可用）
    fetch('/api/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentState)
    }).catch(() => {}); // 忽略错误
}

// 加载数据
function loadData() {
    // 从本地存储加载
    const saved = localStorage.getItem('agentDashboard');
    if (saved) {
        currentState = { ...currentState, ...JSON.parse(saved) };
    }
    
    // 检查是否是新的一天
    const today = new Date().toDateString();
    const savedDate = new Date(currentState.lastActivity).toDateString();
    if (today !== savedDate) {
        // 新的一天，重置统计
        currentState.tasksCompleted = 0;
        currentState.tokensUsed = 0;
        currentState.workTimeSeconds = 0;
    }
    
    // 检查是否深夜
    const hour = new Date().getHours();
    if (hour >= 23 || hour < 7) {
        currentState.status = 'sleeping';
    }
    
    updateDisplay();
}

// 启动自动更新
function startAutoUpdate() {
    // 每秒更新活动时间
    setInterval(updateLastActivity, 1000);
    
    // 每分钟检查是否深夜
    setInterval(() => {
        const hour = new Date().getHours();
        if ((hour >= 23 || hour < 7) && currentState.status !== 'sleeping') {
            switchScene('sleeping');
        }
    }, 60000);
    
    // 从服务器获取最新数据
    loadServerData();
    setInterval(loadServerData, 30000); // 每30秒同步一次
}

// 从服务器加载数据
async function loadServerData() {
    try {
        const response = await fetch('/data/stats.json?t=' + Date.now());
        if (response.ok) {
            const data = await response.json();
            currentState.tasksCompleted = data.today?.tasks || currentState.tasksCompleted;
            currentState.tokensUsed = data.today?.tokens || currentState.tokensUsed;
            updateDisplay();
        }
    } catch (e) {
        // 忽略网络错误
    }
}

// 显示通知
function showNotification(message) {
    const bubble = document.getElementById('speech-bubble');
    const originalText = document.getElementById('speech-text').textContent;
    
    document.getElementById('speech-text').textContent = message;
    bubble.style.animation = 'pulse 0.5s ease-in-out 3';
    
    setTimeout(() => {
        document.getElementById('speech-text').textContent = originalText;
        bubble.style.animation = '';
    }, 5000);
}

// 格式化数字
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// 添加额外的CSS动画
const extraStyles = document.createElement('style');
extraStyles.textContent = `
    @keyframes type-left {
        0%, 100% { transform: rotate(-20deg) translateY(0); }
        50% { transform: rotate(-10deg) translateY(-5px); }
    }
    
    @keyframes type-right {
        0%, 100% { transform: rotate(20deg) translateY(0); }
        50% { transform: rotate(10deg) translateY(-5px); }
    }
    
    @keyframes lift-left {
        0%, 100% { transform: rotate(-30deg); }
        50% { transform: rotate(-60deg); }
    }
    
    @keyframes lift-right {
        0%, 100% { transform: rotate(30deg); }
        50% { transform: rotate(60deg); }
    }
    
    @keyframes eat {
        0%, 100% { transform: rotate(-10deg); }
        50% { transform: rotate(20deg) translateY(-10px); }
    }
    
    @keyframes breathe {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: translateX(-50%) scale(1); }
        50% { transform: translateX(-50%) scale(1.05); }
    }
`;
document.head.appendChild(extraStyles);

// 导出API供外部调用
window.AgentDashboard = {
    startTask,
    recordTask,
    switchScene,
    getState: () => currentState
};
