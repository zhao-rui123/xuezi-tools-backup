/**
 * 系统监控看板 - JavaScript
 * 功能：实时数据刷新、图表渲染、定时更新
 */

// ============================================
// 配置
// ============================================
const CONFIG = {
    refreshInterval: 30000, // 30秒刷新
    countdownInterval: 1000, // 1秒倒计时
    apiBaseUrl: '/api', // API基础路径
    defaultStocks: [
        { name: '中矿资源', code: '002738', market: 'SZ' },
        { name: '赣锋锂业', code: '002460', market: 'SZ' },
        { name: '盐湖股份', code: '000792', market: 'SZ' },
        { name: '盛新锂能', code: '002240', market: 'SZ' },
        { name: '京东方A', code: '000725', market: 'SZ' },
        { name: '彩虹股份', code: '600707', market: 'SH' },
        { name: '中芯国际', code: '00981', market: 'HK' },
        { name: '赣锋锂业', code: '01772', market: 'HK' }
    ]
};

// ============================================
// 状态管理
// ============================================
const state = {
    countdown: CONFIG.refreshInterval / 1000,
    lastUpdate: null,
    diskChart: null,
    isRefreshing: false
};

// ============================================
// 初始化
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

function initDashboard() {
    // 初始化时钟
    updateClock();
    setInterval(updateClock, 1000);
    
    // 初始化磁盘图表
    initDiskChart();
    
    // 加载初始数据
    refreshAllData();
    
    // 启动定时刷新
    startAutoRefresh();
    
    // 启动倒计时
    startCountdown();
    
    console.log('🚀 系统监控看板已启动');
}

// ============================================
// 时钟更新
// ============================================
function updateClock() {
    const now = new Date();
    
    // 时间
    const timeStr = now.toLocaleTimeString('zh-CN', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('currentTime').textContent = timeStr;
    
    // 日期
    const dateStr = now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        weekday: 'long'
    });
    document.getElementById('currentDate').textContent = dateStr;
}

// ============================================
// 自动刷新
// ============================================
function startAutoRefresh() {
    setInterval(() => {
        refreshAllData();
        state.countdown = CONFIG.refreshInterval / 1000;
    }, CONFIG.refreshInterval);
}

function startCountdown() {
    setInterval(() => {
        state.countdown--;
        if (state.countdown < 0) {
            state.countdown = CONFIG.refreshInterval / 1000;
        }
        updateCountdownDisplay();
    }, CONFIG.countdownInterval);
}

function updateCountdownDisplay() {
    const timerEl = document.getElementById('refreshTimer');
    if (timerEl) {
        timerEl.textContent = `${state.countdown}秒后刷新`;
    }
}

// ============================================
// 数据刷新
// ============================================
async function refreshAllData() {
    if (state.isRefreshing) return;
    
    state.isRefreshing = true;
    const refreshIcon = document.querySelector('.refresh-icon');
    if (refreshIcon) {
        refreshIcon.style.animationDuration = '0.5s';
    }
    
    try {
        // 并行加载所有数据
        await Promise.all([
            refreshMemoryData(),
            refreshTaskData(),
            refreshStockData(),
            refreshDiskData()
        ]);
        
        // 更新最后更新时间
        state.lastUpdate = new Date();
        updateLastUpdateTime();
        
        console.log('✅ 数据刷新完成');
    } catch (error) {
        console.error('❌ 数据刷新失败:', error);
    } finally {
        state.isRefreshing = false;
        if (refreshIcon) {
            refreshIcon.style.animationDuration = '2s';
        }
    }
}

function updateLastUpdateTime() {
    const lastUpdateEl = document.getElementById('lastUpdate');
    if (lastUpdateEl && state.lastUpdate) {
        lastUpdateEl.textContent = state.lastUpdate.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// ============================================
// Memory Suite 数据
// ============================================
async function refreshMemoryData() {
    try {
        // 模拟数据（实际应从API获取）
        const data = await fetchMemoryData();
        
        // 更新卡片数据
        document.getElementById('memoryToday').textContent = data.todayCount || 0;
        document.getElementById('memoryFiles').textContent = data.fileCount || 0;
        document.getElementById('memorySize').textContent = formatBytes(data.size || 0);
        document.getElementById('memorySync').textContent = data.lastSync || '--:--';
        document.getElementById('activeSessions').textContent = data.activeSessions || 0;
        document.getElementById('knowledgeEntries').textContent = data.knowledgeEntries || 0;
        
    } catch (error) {
        console.error('Memory数据加载失败:', error);
    }
}

async function fetchMemoryData() {
    // TODO: 替换为实际API调用
    // const response = await fetch(`${CONFIG.apiBaseUrl}/memory`);
    // return await response.json();
    
    // 模拟数据
    return {
        todayCount: Math.floor(Math.random() * 50) + 10,
        fileCount: Math.floor(Math.random() * 200) + 50,
        size: Math.floor(Math.random() * 500 * 1024 * 1024) + 100 * 1024 * 1024,
        lastSync: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
        activeSessions: Math.floor(Math.random() * 5) + 1,
        knowledgeEntries: Math.floor(Math.random() * 500) + 100
    };
}

// ============================================
// 定时任务数据
// ============================================
async function refreshTaskData() {
    try {
        const data = await fetchTaskData();
        
        // 更新统计
        document.getElementById('taskSuccess').textContent = data.success || 0;
        document.getElementById('taskFailed').textContent = data.failed || 0;
        document.getElementById('taskPending').textContent = data.pending || 0;
        document.getElementById('taskCount').textContent = `${data.running || 0} 运行中`;
        
        // 更新任务列表
        renderTaskList(data.tasks || []);
        
    } catch (error) {
        console.error('Task数据加载失败:', error);
    }
}

async function fetchTaskData() {
    // TODO: 替换为实际API调用
    
    // 模拟数据
    const tasks = [
        { name: '股票价格更新', schedule: '*/5 * * * *', status: 'success', lastRun: '2分钟前' },
        { name: '磁盘空间检查', schedule: '0 */6 * * *', status: 'success', lastRun: '1小时前' },
        { name: 'Memory同步', schedule: '0 */12 * * *', status: 'running', lastRun: '进行中' },
        { name: '日志清理', schedule: '0 0 * * *', status: 'pending', lastRun: '待执行' },
        { name: '备份任务', schedule: '0 2 * * *', status: 'success', lastRun: '昨天' },
        { name: '健康检查', schedule: '*/30 * * * *', status: 'success', lastRun: '5分钟前' }
    ];
    
    return {
        success: Math.floor(Math.random() * 50) + 20,
        failed: Math.floor(Math.random() * 5),
        pending: Math.floor(Math.random() * 3),
        running: tasks.filter(t => t.status === 'running').length,
        tasks: tasks
    };
}

function renderTaskList(tasks) {
    const taskListEl = document.getElementById('taskList');
    if (!taskListEl) return;
    
    taskListEl.innerHTML = tasks.map(task => `
        <div class="task-item">
            <div class="task-status ${task.status}"></div>
            <div class="task-info">
                <div class="task-name">${task.name}</div>
                <div class="task-schedule">${task.schedule}</div>
            </div>
            <div class="task-time">${task.lastRun}</div>
        </div>
    `).join('');
}

// ============================================
// 自选股数据
// ============================================
async function refreshStockData() {
    try {
        const data = await fetchStockData();
        renderStockTable(data);
        updateStockSummary(data);
    } catch (error) {
        console.error('股票数据加载失败:', error);
    }
}

async function fetchStockData() {
    // TODO: 替换为实际股票API调用
    
    // 模拟股票数据
    return CONFIG.defaultStocks.map(stock => {
        const basePrice = Math.random() * 50 + 10;
        const change = (Math.random() - 0.5) * 10;
        const changePercent = (change / basePrice) * 100;
        
        return {
            ...stock,
            price: basePrice.toFixed(2),
            change: change.toFixed(2),
            changePercent: changePercent.toFixed(2)
        };
    });
}

function renderStockTable(stocks) {
    const tbody = document.getElementById('stockTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = stocks.map(stock => {
        const changeClass = parseFloat(stock.change) > 0 ? 'up' : 
                           parseFloat(stock.change) < 0 ? 'down' : 'flat';
        const changeSymbol = parseFloat(stock.change) > 0 ? '+' : '';
        
        return `
            <tr>
                <td>
                    <div class="stock-name">${stock.name}</div>
                    <div class="stock-code">${stock.market}.${stock.code}</div>
                </td>
                <td class="stock-code">${stock.code}</td>
                <td class="stock-price">${stock.price}</td>
                <td class="stock-change ${changeClass}">${changeSymbol}${stock.change}</td>
                <td class="stock-percent ${changeClass}">${changeSymbol}${stock.changePercent}%</td>
            </tr>
        `;
    }).join('');
}

function updateStockSummary(stocks) {
    let up = 0, down = 0, flat = 0;
    
    stocks.forEach(stock => {
        const change = parseFloat(stock.change);
        if (change > 0) up++;
        else if (change < 0) down++;
        else flat++;
    });
    
    document.getElementById('stocksUp').textContent = up;
    document.getElementById('stocksDown').textContent = down;
    document.getElementById('stocksFlat').textContent = flat;
}

// ============================================
// 磁盘图表
// ============================================
function initDiskChart() {
    const ctx = document.getElementById('diskChart');
    if (!ctx) return;
    
    state.diskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['已使用', '可用空间'],
            datasets: [{
                data: [0, 100],
                backgroundColor: [
                    '#58a6ff',
                    '#21262d'
                ],
                borderColor: '#161b22',
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#161b22',
                    titleColor: '#e6edf3',
                    bodyColor: '#8b949e',
                    borderColor: '#30363d',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return `${label}: ${value.toFixed(1)}%`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 1000
            }
        }
    });
}

async function refreshDiskData() {
    try {
        const data = await fetchDiskData();
        
        // 更新图表
        if (state.diskChart) {
            const usedPercent = (data.used / data.total) * 100;
            const freePercent = 100 - usedPercent;
            
            state.diskChart.data.datasets[0].data = [usedPercent, freePercent];
            
            // 根据使用率调整颜色
            if (usedPercent > 90) {
                state.diskChart.data.datasets[0].backgroundColor[0] = '#f85149'; // 危险
            } else if (usedPercent > 70) {
                state.diskChart.data.datasets[0].backgroundColor[0] = '#d29922'; // 警告
            } else {
                state.diskChart.data.datasets[0].backgroundColor[0] = '#58a6ff'; // 正常
            }
            
            state.diskChart.update('active');
        }
        
        // 更新信息
        document.getElementById('diskTotal').textContent = formatBytes(data.total);
        document.getElementById('diskUsed').textContent = formatBytes(data.used);
        document.getElementById('diskFree').textContent = formatBytes(data.free);
        document.getElementById('diskPercent').textContent = `${((data.used / data.total) * 100).toFixed(1)}%`;
        
    } catch (error) {
        console.error('磁盘数据加载失败:', error);
    }
}

async function fetchDiskData() {
    // TODO: 替换为实际API调用
    
    // 模拟数据 (500GB 总容量)
    const total = 500 * 1024 * 1024 * 1024;
    const used = Math.floor(total * (0.3 + Math.random() * 0.4)); // 30-70% 使用
    const free = total - used;
    
    return { total, used, free };
}

// ============================================
// 工具函数
// ============================================
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// ============================================
// 手动刷新
// ============================================
function manualRefresh() {
    refreshAllData();
    state.countdown = CONFIG.refreshInterval / 1000;
}

// 暴露全局函数供调试
window.dashboard = {
    refresh: manualRefresh,
    getState: () => state
};

// 键盘快捷键
document.addEventListener('keydown', (e) => {
    // R 键手动刷新
    if (e.key === 'r' || e.key === 'R') {
        if (!e.ctrlKey && !e.metaKey) {
            manualRefresh();
        }
    }
});

console.log('📊 Dashboard JS loaded. Press "R" to refresh manually.');
