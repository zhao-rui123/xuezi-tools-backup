/**
 * A股股票筛选监控系统 - 前端主程序
 */

// API基础URL
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api' 
    : '/api';

// 全局状态
const state = {
    currentPage: 'screen',
    screenResults: [],
    portfolio: [],
    alerts: [],
    currentStock: null,
    klineChart: null,
    screenProgressInterval: null
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initScreenPage();
    initPortfolioPage();
    initModal();
    loadPortfolio();
    loadHistory();
});

// ============ 导航 ============
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            switchPage(page);
            
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchPage(page) {
    state.currentPage = page;
    document.querySelectorAll('.page-content').forEach(p => p.classList.add('hidden'));
    document.getElementById(`page-${page}`).classList.remove('hidden');
    
    if (page === 'portfolio') {
        loadPortfolio();
    } else if (page === 'history') {
        loadHistory();
    }
}

// ============ 股票筛选页面 ============
function initScreenPage() {
    // 开始筛选按钮
    document.getElementById('btn-start-screen').addEventListener('click', startScreening);
    
    // 等级筛选复选框
    document.querySelectorAll('.grade-filter').forEach(checkbox => {
        checkbox.addEventListener('change', filterResults);
    });
}

async function startScreening() {
    const months = document.getElementById('screen-months').value;
    
    // 显示进度
    document.getElementById('screen-progress').classList.remove('hidden');
    document.getElementById('screen-results').classList.add('hidden');
    
    try {
        // 开始筛选
        const response = await fetch(`${API_BASE_URL}/stocks/screen?recent_months=${months}`);
        const data = await response.json();
        
        if (data.success) {
            state.screenResults = data.data;
            displayResults(state.screenResults);
        } else {
            showError('筛选失败: ' + data.message);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    } finally {
        document.getElementById('screen-progress').classList.add('hidden');
    }
}

function updateProgress() {
    fetch(`${API_BASE_URL}/stocks/screen/progress`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const progress = data.data;
                const pct = progress.total > 0 ? (progress.current / progress.total * 100) : 0;
                
                document.getElementById('progress-text').textContent = `${progress.current}/${progress.total}`;
                document.getElementById('progress-fill').style.width = `${pct}%`;
                
                if (progress.status === 'completed') {
                    clearInterval(state.screenProgressInterval);
                }
            }
        });
}

function displayResults(results) {
    document.getElementById('screen-results').classList.remove('hidden');
    
    // 更新统计
    const stats = {
        A: results.filter(r => r.grade === 'A').length,
        B: results.filter(r => r.grade === 'B').length,
        C: results.filter(r => r.grade === 'C').length,
        total: results.length
    };
    
    document.getElementById('stat-total').textContent = stats.total;
    document.getElementById('stat-a').textContent = stats.A;
    document.getElementById('stat-b').textContent = stats.B;
    document.getElementById('stat-c').textContent = stats.C;
    
    filterResults();
}

function filterResults() {
    const checkedGrades = Array.from(document.querySelectorAll('.grade-filter:checked'))
        .map(cb => cb.value);
    
    const filtered = state.screenResults.filter(r => checkedGrades.includes(r.grade));
    
    const tbody = document.getElementById('results-tbody');
    tbody.innerHTML = '';
    
    filtered.forEach(stock => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="grade-${stock.grade.toLowerCase()} px-2 py-1 rounded text-white text-xs font-bold">${stock.grade}</span></td>
            <td class="font-mono">${stock.code}</td>
            <td class="text-white">${stock.name}</td>
            <td class="text-white">¥${stock.current_price?.toFixed(2) || '--'}</td>
            <td>${stock.macd_golden_cross ? '<i class="fas fa-check text-green-400"></i>' : '<i class="fas fa-times text-gray-500"></i>'}</td>
            <td>${stock.kdj_golden_cross ? '<i class="fas fa-check text-green-400"></i>' : '<i class="fas fa-times text-gray-500"></i>'}</td>
            <td>${stock.ma_bullish ? '<i class="fas fa-check text-green-400"></i>' : '<i class="fas fa-times text-gray-500"></i>'}</td>
            <td>${stock.volume_increase ? '<i class="fas fa-check text-green-400"></i>' : '<i class="fas fa-times text-gray-500"></i>'}</td>
            <td>
                <button class="text-blue-400 hover:text-blue-300 mr-2" onclick="viewStockDetail('${stock.code}')">
                    <i class="fas fa-chart-line"></i>
                </button>
                <button class="text-green-400 hover:text-green-300" onclick="quickAddPosition('${stock.code}', '${stock.name}')">
                    <i class="fas fa-plus"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// ============ 持仓监控页面 ============
function initPortfolioPage() {
    document.getElementById('btn-check-portfolio').addEventListener('click', checkPortfolio);
    document.getElementById('btn-add-position').addEventListener('click', () => {
        document.getElementById('add-position-modal').classList.add('active');
    });
    
    // 添加持仓表单
    document.getElementById('btn-cancel-position').addEventListener('click', () => {
        document.getElementById('add-position-modal').classList.remove('active');
    });
    
    document.getElementById('btn-save-position').addEventListener('click', savePosition);
}

async function loadPortfolio() {
    try {
        const response = await fetch(`${API_BASE_URL}/portfolio`);
        const data = await response.json();
        
        if (data.success) {
            state.portfolio = data.data;
            displayPortfolio(state.portfolio);
            updatePortfolioSummary(state.portfolio);
        }
    } catch (error) {
        console.error('加载持仓失败:', error);
    }
}

function displayPortfolio(portfolio) {
    const tbody = document.getElementById('portfolio-tbody');
    tbody.innerHTML = '';
    
    portfolio.forEach(pos => {
        const pnlClass = pos.profit_loss >= 0 ? 'text-green-400' : 'text-red-400';
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="font-mono">${pos.stock_code}</td>
            <td class="text-white">${pos.stock_name}</td>
            <td class="text-white">${pos.position}</td>
            <td class="text-white">¥${pos.cost_price.toFixed(2)}</td>
            <td class="text-white">¥${pos.current_price?.toFixed(2) || '--'}</td>
            <td class="text-white">¥${pos.market_value?.toFixed(2) || '--'}</td>
            <td class="${pnlClass}">¥${pos.profit_loss?.toFixed(2) || '--'}</td>
            <td class="${pnlClass}">${pos.profit_loss_pct?.toFixed(2) || '--'}%</td>
            <td>
                <button class="text-blue-400 hover:text-blue-300 mr-2" onclick="viewStockDetail('${pos.stock_code}')">
                    <i class="fas fa-chart-line"></i>
                </button>
                <button class="text-red-400 hover:text-red-300" onclick="removePosition('${pos.stock_code}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updatePortfolioSummary(portfolio) {
    const totalValue = portfolio.reduce((sum, p) => sum + (p.market_value || 0), 0);
    const totalCost = portfolio.reduce((sum, p) => sum + (p.cost_price * p.position), 0);
    const totalPnl = totalValue - totalCost;
    const pnlPct = totalCost > 0 ? (totalPnl / totalCost * 100) : 0;
    
    document.getElementById('portfolio-count').textContent = portfolio.length;
    document.getElementById('portfolio-value').textContent = `¥${totalValue.toFixed(2)}`;
    document.getElementById('portfolio-pnl').textContent = `¥${totalPnl.toFixed(2)}`;
    document.getElementById('portfolio-pnl').className = `text-2xl font-bold ${totalPnl >= 0 ? 'text-green-400' : 'text-red-400'}`;
    document.getElementById('portfolio-pnl-pct').textContent = `${pnlPct.toFixed(2)}%`;
    document.getElementById('portfolio-pnl-pct').className = `text-2xl font-bold ${pnlPct >= 0 ? 'text-green-400' : 'text-red-400'}`;
}

async function savePosition() {
    const code = document.getElementById('position-stock-code').value.trim();
    const name = document.getElementById('position-stock-name').value.trim();
    const quantity = parseFloat(document.getElementById('position-quantity').value);
    const cost = parseFloat(document.getElementById('position-cost').value);
    const notes = document.getElementById('position-notes').value.trim();
    
    if (!code || !name || !quantity || !cost) {
        showError('请填写所有必填项');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/portfolio`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                stock_code: code,
                stock_name: name,
                position: quantity,
                cost_price: cost,
                notes: notes
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('add-position-modal').classList.remove('active');
            loadPortfolio();
            showSuccess('持仓添加成功');
        } else {
            showError('添加失败: ' + data.message);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

async function removePosition(stockCode) {
    if (!confirm('确定要删除这个持仓吗？')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/portfolio/${stockCode}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadPortfolio();
            showSuccess('持仓已删除');
        }
    } catch (error) {
        showError('删除失败: ' + error.message);
    }
}

async function checkPortfolio() {
    try {
        const response = await fetch(`${API_BASE_URL}/portfolio/check`);
        const data = await response.json();
        
        if (data.success) {
            state.alerts = data.data;
            displayAlerts(state.alerts);
        }
    } catch (error) {
        showError('检查持仓失败: ' + error.message);
    }
}

function displayAlerts(alerts) {
    const section = document.getElementById('alerts-section');
    const list = document.getElementById('alerts-list');
    
    if (alerts.length === 0) {
        section.classList.add('hidden');
        return;
    }
    
    section.classList.remove('hidden');
    list.innerHTML = '';
    
    alerts.forEach(alert => {
        const alertClass = alert.alert_level === 'danger' ? 'border-red-500/50 bg-red-500/10' : 
                          alert.alert_level === 'warning' ? 'border-yellow-500/50 bg-yellow-500/10' : 
                          'border-blue-500/50 bg-blue-500/10';
        
        const item = document.createElement('div');
        item.className = `p-4 rounded-xl border ${alertClass}`;
        item.innerHTML = `
            <div class="flex items-start justify-between">
                <div>
                    <div class="flex items-center mb-1">
                        <span class="text-white font-medium mr-2">${alert.stock_name} (${alert.stock_code})</span>
                        <span class="text-xs px-2 py-0.5 rounded ${alert.alert_level === 'danger' ? 'bg-red-500' : alert.alert_level === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'} text-white">${alert.alert_type}</span>
                    </div>
                    <p class="text-gray-300 text-sm">${alert.message}</p>
                    ${alert.current_price ? `<p class="text-gray-400 text-xs mt-1">当前价: ¥${alert.current_price.toFixed(2)}</p>` : ''}
                </div>
                <span class="text-gray-500 text-xs">${alert.created_at}</span>
            </div>
        `;
        list.appendChild(item);
    });
}

function quickAddPosition(code, name) {
    document.getElementById('position-stock-code').value = code;
    document.getElementById('position-stock-name').value = name;
    document.getElementById('add-position-modal').classList.add('active');
}

// ============ 历史记录 ============
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/history/screen-records`);
        const data = await response.json();
        
        if (data.success) {
            displayHistory(data.data);
        }
    } catch (error) {
        console.error('加载历史记录失败:', error);
    }
}

function displayHistory(records) {
    const tbody = document.getElementById('history-tbody');
    tbody.innerHTML = '';
    
    records.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.screen_date}</td>
            <td class="font-mono">${record.code}</td>
            <td class="text-white">${record.name}</td>
            <td><span class="grade-${record.grade.toLowerCase()} px-2 py-1 rounded text-white text-xs font-bold">${record.grade}</span></td>
            <td>${record.macd_golden_cross ? '<i class="fas fa-check text-green-400"></i>' : '<i class="fas fa-times text-gray-500"></i>'}</td>
            <td>${record.kdj_golden_cross ? '<i class="fas fa-check text-green-400"></i>' : '<i class="fas fa-times text-gray-500"></i>'}</td>
            <td>
                <button class="text-blue-400 hover:text-blue-300" onclick="viewStockDetail('${record.code}')">
                    <i class="fas fa-chart-line"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// ============ 股票详情模态框 ============
function initModal() {
    document.getElementById('btn-close-modal').addEventListener('click', closeModal);
    
    // 标签页切换
    document.querySelectorAll('.tab-item').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            switchTab(tabName);
            
            document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
        });
    });
    
    // K线周期切换
    document.getElementById('kline-period').addEventListener('change', (e) => {
        if (state.currentStock) {
            loadKlineData(state.currentStock, e.target.value);
        }
    });
}

async function viewStockDetail(stockCode) {
    state.currentStock = stockCode;
    
    try {
        // 获取股票详情
        const response = await fetch(`${API_BASE_URL}/stocks/${stockCode}/detail`);
        const data = await response.json();
        
        if (data.success) {
            const stock = data.data;
            document.getElementById('modal-stock-name').textContent = stock.name;
            document.getElementById('modal-stock-code').textContent = stock.code;
            
            // 加载K线数据
            loadKlineData(stockCode, 'daily');
            
            // 加载指标数据
            displayIndicators(stock.technical_indicators);
            
            // 加载基本面数据
            displayFundamental(stock.fundamental_data);
            
            // 加载研报数据
            loadResearchReports(stockCode);
            
            // 显示模态框
            document.getElementById('stock-modal').classList.add('active');
        }
    } catch (error) {
        showError('加载股票详情失败: ' + error.message);
    }
}

function closeModal() {
    document.getElementById('stock-modal').classList.remove('active');
    if (state.klineChart) {
        state.klineChart.dispose();
        state.klineChart = null;
    }
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
    document.getElementById(`tab-${tabName}`).classList.remove('hidden');
}

async function loadKlineData(stockCode, period) {
    try {
        const response = await fetch(`${API_BASE_URL}/stocks/${stockCode}/kline?period=${period}`);
        const data = await response.json();
        
        if (data.success) {
            renderKlineChart(data.data);
        }
    } catch (error) {
        console.error('加载K线数据失败:', error);
    }
}

function renderKlineChart(klineData) {
    const chartDom = document.getElementById('kline-chart');
    
    if (state.klineChart) {
        state.klineChart.dispose();
    }
    
    state.klineChart = echarts.init(chartDom, 'dark');
    
    const data = klineData.kline;
    const dates = data.map(item => item[0]);
    const values = data.map(item => [item[1], item[2], item[3], item[4]]);
    const volumes = klineData.volume;
    
    const option = {
        backgroundColor: 'transparent',
        animation: false,
        legend: {
            bottom: 10,
            left: 'center',
            data: ['K线', 'MA5', 'MA10', 'MA20', 'MA60'],
            textStyle: { color: '#94a3b8' }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' },
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            textStyle: { color: '#e2e8f0' }
        },
        grid: [
            { left: '10%', right: '8%', height: '50%' },
            { left: '10%', right: '8%', top: '68%', height: '16%' }
        ],
        xAxis: [
            {
                type: 'category',
                data: dates,
                scale: true,
                boundaryGap: false,
                axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
                axisLabel: { color: '#94a3b8' },
                splitLine: { show: false }
            },
            {
                type: 'category',
                gridIndex: 1,
                data: dates,
                axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
                axisLabel: { show: false }
            }
        ],
        yAxis: [
            {
                scale: true,
                axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
                axisLabel: { color: '#94a3b8' },
                splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } }
            },
            {
                scale: true,
                gridIndex: 1,
                splitNumber: 2,
                axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
                axisLabel: { show: false },
                splitLine: { show: false }
            }
        ],
        dataZoom: [
            { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
            { show: true, xAxisIndex: [0, 1], type: 'slider', bottom: 10, start: 50, end: 100 }
        ],
        series: [
            {
                name: 'K线',
                type: 'candlestick',
                data: values,
                itemStyle: {
                    color: '#ef4444',
                    color0: '#10b981',
                    borderColor: '#ef4444',
                    borderColor0: '#10b981'
                }
            },
            {
                name: 'MA5',
                type: 'line',
                data: klineData.ma?.ma5 || [],
                smooth: true,
                lineStyle: { opacity: 0.5, width: 1 }
            },
            {
                name: 'MA10',
                type: 'line',
                data: klineData.ma?.ma10 || [],
                smooth: true,
                lineStyle: { opacity: 0.5, width: 1 }
            },
            {
                name: 'MA20',
                type: 'line',
                data: klineData.ma?.ma20 || [],
                smooth: true,
                lineStyle: { opacity: 0.5, width: 1 }
            },
            {
                name: 'MA60',
                type: 'line',
                data: klineData.ma?.ma60 || [],
                smooth: true,
                lineStyle: { opacity: 0.5, width: 1 }
            },
            {
                name: '成交量',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: volumes,
                itemStyle: {
                    color: (params) => {
                        const change = values[params.dataIndex][1] - values[params.dataIndex][0];
                        return change >= 0 ? '#ef4444' : '#10b981';
                    }
                }
            }
        ]
    };
    
    // 添加MACD指标（如果有）
    if (klineData.macd) {
        option.grid.push({ left: '10%', right: '8%', top: '86%', height: '12%' });
        option.xAxis.push({
            type: 'category',
            gridIndex: 2,
            data: dates,
            axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
            axisLabel: { show: false }
        });
        option.yAxis.push({
            scale: true,
            gridIndex: 2,
            splitNumber: 2,
            axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
            axisLabel: { show: false },
            splitLine: { show: false }
        });
        
        option.series.push(
            {
                name: 'MACD',
                type: 'bar',
                xAxisIndex: 2,
                yAxisIndex: 2,
                data: klineData.macd.bar,
                itemStyle: {
                    color: (params) => params.value >= 0 ? '#ef4444' : '#10b981'
                }
            },
            {
                name: 'DIF',
                type: 'line',
                xAxisIndex: 2,
                yAxisIndex: 2,
                data: klineData.macd.dif,
                lineStyle: { color: '#3b82f6', width: 1 }
            },
            {
                name: 'DEA',
                type: 'line',
                xAxisIndex: 2,
                yAxisIndex: 2,
                data: klineData.macd.dea,
                lineStyle: { color: '#f59e0b', width: 1 }
            }
        );
    }
    
    state.klineChart.setOption(option);
    
    window.addEventListener('resize', () => {
        state.klineChart && state.klineChart.resize();
    });
}

function displayIndicators(indicators) {
    const container = document.getElementById('indicators-content');
    container.innerHTML = '';
    
    if (!indicators || !indicators.monthly) {
        container.innerHTML = '<p class="text-gray-400">暂无指标数据</p>';
        return;
    }
    
    const monthly = indicators.monthly;
    
    const sections = [
        {
            title: 'MACD指标（月线）',
            items: [
                { label: 'DIF', value: monthly.macd?.dif },
                { label: 'DEA', value: monthly.macd?.dea },
                { label: 'MACD柱', value: monthly.macd?.bar },
                { label: '金叉', value: monthly.macd?.golden_cross ? '是' : '否', class: monthly.macd?.golden_cross ? 'text-green-400' : '' },
                { label: '死叉', value: monthly.macd?.death_cross ? '是' : '否', class: monthly.macd?.death_cross ? 'text-red-400' : '' }
            ]
        },
        {
            title: 'KDJ指标（月线）',
            items: [
                { label: 'K值', value: monthly.kdj?.k },
                { label: 'D值', value: monthly.kdj?.d },
                { label: 'J值', value: monthly.kdj?.j },
                { label: '金叉', value: monthly.kdj?.golden_cross ? '是' : '否', class: monthly.kdj?.golden_cross ? 'text-green-400' : '' },
                { label: '超买', value: monthly.kdj?.overbought ? '是' : '否', class: monthly.kdj?.overbought ? 'text-red-400' : '' }
            ]
        },
        {
            title: '均线系统（月线）',
            items: [
                { label: 'MA5', value: monthly.ma?.ma5 },
                { label: 'MA10', value: monthly.ma?.ma10 },
                { label: 'MA20', value: monthly.ma?.ma20 },
                { label: 'MA60', value: monthly.ma?.ma60 },
                { label: '多头排列', value: monthly.ma?.bullish ? '是' : '否', class: monthly.ma?.bullish ? 'text-green-400' : '' }
            ]
        },
        {
            title: 'RSI指标（月线）',
            items: [
                { label: 'RSI6', value: monthly.rsi?.rsi6 },
                { label: 'RSI12', value: monthly.rsi?.rsi12 }
            ]
        }
    ];
    
    sections.forEach(section => {
        const card = document.createElement('div');
        card.className = 'glass p-4 rounded-xl';
        card.innerHTML = `
            <h4 class="text-white font-medium mb-3">${section.title}</h4>
            <div class="grid grid-cols-2 gap-2">
                ${section.items.map(item => `
                    <div class="flex justify-between">
                        <span class="text-gray-400 text-sm">${item.label}</span>
                        <span class="text-white text-sm ${item.class || ''}">${item.value !== undefined ? item.value : '--'}</span>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(card);
    });
}

function displayFundamental(data) {
    const container = document.getElementById('fundamental-content');
    container.innerHTML = '';
    
    if (!data || !data.basic_info) {
        container.innerHTML = '<p class="text-gray-400">暂无基本面数据</p>';
        return;
    }
    
    const basic = data.basic_info;
    const financial = data.financial_indicators || {};
    const valuation = data.valuation || {};
    
    container.innerHTML = `
        <div class="glass-card p-4">
            <h4 class="text-white font-medium mb-3">基本信息</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                    <span class="text-gray-400 text-sm">行业</span>
                    <p class="text-white">${basic.industry || '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">上市日期</span>
                    <p class="text-white">${basic.list_date || '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">总市值</span>
                    <p class="text-white">${basic.total_cap ? (basic.total_cap / 100000000).toFixed(2) + '亿' : '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">流通市值</span>
                    <p class="text-white">${basic.float_cap ? (basic.float_cap / 100000000).toFixed(2) + '亿' : '--'}</p>
                </div>
            </div>
        </div>
        
        <div class="glass-card p-4">
            <h4 class="text-white font-medium mb-3">财务指标</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                    <span class="text-gray-400 text-sm">每股收益(EPS)</span>
                    <p class="text-white">${financial.eps || '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">净资产收益率(ROE)</span>
                    <p class="text-white">${financial.roe ? financial.roe + '%' : '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">毛利率</span>
                    <p class="text-white">${financial.gross_margin ? financial.gross_margin + '%' : '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">净利率</span>
                    <p class="text-white">${financial.net_margin ? financial.net_margin + '%' : '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">营收增长率</span>
                    <p class="text-white">${financial.revenue_growth ? financial.revenue_growth + '%' : '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">净利润增长率</span>
                    <p class="text-white">${financial.profit_growth ? financial.profit_growth + '%' : '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">资产负债率</span>
                    <p class="text-white">${financial.debt_ratio ? financial.debt_ratio + '%' : '--'}</p>
                </div>
            </div>
        </div>
        
        <div class="glass-card p-4">
            <h4 class="text-white font-medium mb-3">估值信息</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                    <span class="text-gray-400 text-sm">市盈率(PE-TTM)</span>
                    <p class="text-white">${valuation.pe_ttm || '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">市净率(PB)</span>
                    <p class="text-white">${valuation.pb || '--'}</p>
                </div>
                <div>
                    <span class="text-gray-400 text-sm">市销率(PS)</span>
                    <p class="text-white">${valuation.ps || '--'}</p>
                </div>
            </div>
        </div>
    `;
}

async function loadResearchReports(stockCode) {
    const container = document.getElementById('reports-content');
    container.innerHTML = '<p class="text-gray-400">加载中...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/stocks/${stockCode}/research-reports`);
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            container.innerHTML = data.data.map(report => `
                <div class="glass p-4 rounded-xl">
                    <div class="flex items-start justify-between mb-2">
                        <h5 class="text-white font-medium">${report.title}</h5>
                        <span class="text-gray-400 text-xs">${report.publish_date}</span>
                    </div>
                    <p class="text-gray-400 text-sm mb-2">${report.source} | ${report.author}</p>
                    <p class="text-gray-300 text-sm">${report.summary || ''}</p>
                    ${report.target_price ? `<p class="text-blue-400 text-sm mt-2">目标价: ¥${report.target_price}</p>` : ''}
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="text-gray-400">暂无研报数据</p>';
        }
    } catch (error) {
        container.innerHTML = '<p class="text-gray-400">加载研报失败</p>';
    }
}

// ============ 工具函数 ============
function showError(message) {
    // 简单的错误提示
    alert('错误: ' + message);
}

function showSuccess(message) {
    // 简单的成功提示
    alert(message);
}

// 全局函数（供HTML调用）
window.viewStockDetail = viewStockDetail;
window.quickAddPosition = quickAddPosition;
window.removePosition = removePosition;
