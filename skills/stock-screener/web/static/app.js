// 月线趋势投资筛选器 - 前端应用（完整版）

// 全局状态
let screeningResults = [];
let watchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
let currentFilter = 'all';
let currentStock = null;
let klineChart = null;

// DOM 元素
const btnScreen = document.getElementById('btnScreen');
const btnHistory = document.getElementById('btnHistory');
const btnCloseModal = document.getElementById('btnCloseModal');
const btnAddWatch = document.getElementById('btnAddWatch');
const loadingPanel = document.getElementById('loadingPanel');
const resultsPanel = document.getElementById('resultsPanel');
const emptyPanel = document.getElementById('emptyPanel');
const detailModal = document.getElementById('detailModal');
const searchInput = document.getElementById('searchInput');
const gradeFilter = document.getElementById('gradeFilter');
const stockListBody = document.getElementById('stockListBody');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadLastUpdateTime();
    bindEvents();
    updateWatchlistCount();
});

// 绑定事件
function bindEvents() {
    btnScreen.addEventListener('click', startScreening);
    btnCloseModal.addEventListener('click', closeModal);
    btnAddWatch.addEventListener('click', toggleWatchlist);
    searchInput.addEventListener('input', filterStocks);
    gradeFilter.addEventListener('change', filterStocks);
    
    detailModal.addEventListener('click', (e) => {
        if (e.target === detailModal) closeModal();
    });
}

// 加载最后更新时间
function loadLastUpdateTime() {
    const lastUpdate = localStorage.getItem('lastScreeningTime');
    if (lastUpdate) {
        document.getElementById('lastUpdate').textContent = lastUpdate;
    }
}

// 更新监听数量
function updateWatchlistCount() {
    const count = watchlist.length;
    // 可以在这里显示监听数量
}

// 开始筛选
async function startScreening() {
    showLoading();
    
    try {
        const response = await fetch('/api/screen', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            throw new Error('筛选失败');
        }
        
        const data = await response.json();
        screeningResults = data.results || [];
        
        localStorage.setItem('screeningResults', JSON.stringify(screeningResults));
        localStorage.setItem('lastScreeningTime', new Date().toLocaleString());
        document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
        
        showResults();
    } catch (error) {
        console.error('筛选错误:', error);
        alert('筛选失败，请稍后重试');
        showEmpty();
    }
}

// 显示加载状态
function showLoading() {
    loadingPanel.classList.remove('hidden');
    resultsPanel.classList.add('hidden');
    emptyPanel.classList.add('hidden');
}

// 显示结果
function showResults() {
    loadingPanel.classList.add('hidden');
    resultsPanel.classList.remove('hidden');
    emptyPanel.classList.add('hidden');
    
    updateSummary();
    renderStockList();
}

// 显示空状态
function showEmpty() {
    loadingPanel.classList.add('hidden');
    resultsPanel.classList.add('hidden');
    emptyPanel.classList.remove('hidden');
}

// 更新汇总数据
function updateSummary() {
    const total = screeningResults.length;
    const gradeA = screeningResults.filter(r => r.grade === 'A').length;
    const gradeB = screeningResults.filter(r => r.grade === 'B').length;
    const gradeC = screeningResults.filter(r => r.grade === 'C').length;
    
    document.getElementById('totalCount').textContent = total;
    document.getElementById('gradeACount').textContent = gradeA;
    document.getElementById('gradeBCount').textContent = gradeB;
    document.getElementById('gradeCCount').textContent = gradeC;
}

// 渲染股票列表
function renderStockList() {
    const filtered = getFilteredStocks();
    
    if (filtered.length === 0) {
        stockListBody.innerHTML = `
            <tr>
                <td colspan="7" class="px-4 py-8 text-center text-slate-500">
                    没有符合条件的股票
                </td>
            </tr>
        `;
        return;
    }
    
    stockListBody.innerHTML = filtered.map(stock => {
        const indicators = stock.indicators || {};
        const signals = stock.signals || {};
        const sellSignals = stock.sell_signals || {};
        
        const gradeClass = {
            'A': 'tag-grade-a',
            'B': 'tag-grade-b',
            'C': 'tag-grade-c'
        }[stock.grade] || 'tag-grade-c';
        
        const macdDot = signals.macd_golden_cross ? 'signal-active' : 'signal-inactive';
        const kdjDot = signals.kdj_golden_cross ? 'signal-active' : 'signal-inactive';
        const maDot = signals.ma_alignment ? 'signal-active' : 'signal-inactive';
        
        const hasSellSignal = sellSignals.suggestions && sellSignals.suggestions.length > 0;
        const sellWarning = hasSellSignal ? '<span class="signal-dot signal-danger"></span>' : '';
        
        const isWatched = watchlist.includes(stock.code);
        const watchIcon = isWatched ? '★' : '';
        
        return `
            <tr class="stock-row border-b border-slate-700/30 transition-colors cursor-pointer" onclick="showStockDetail('${stock.code}')">
                <td class="px-4 py-4">
                    <span class="inline-flex items-center justify-center w-8 h-8 rounded-lg text-xs font-bold text-white ${gradeClass}">
                        ${stock.grade}
                    </span>
                </td>
                <td class="px-4 py-4">
                    <div class="font-medium text-white">${stock.name} ${watchIcon}</div>
                    <div class="text-xs text-slate-400">${stock.code}</div>
                </td>
                <td class="px-4 py-4">
                    <div class="text-white">¥${indicators.close || '--'}</div>
                    <div class="text-xs text-slate-400">MA5: ${indicators.ma5 || '--'}</div>
                </td>
                <td class="px-4 py-4">
                    <div class="flex items-center gap-2">
                        <span class="signal-dot ${macdDot}"></span>
                        <span class="text-slate-300">${indicators.macd_dif ? indicators.macd_dif.toFixed(3) : '--'}</span>
                    </div>
                </td>
                <td class="px-4 py-4">
                    <div class="flex items-center gap-2">
                        <span class="signal-dot ${kdjDot}"></span>
                        <span class="text-slate-300">K:${indicators.kdj_k ? indicators.kdj_k.toFixed(1) : '--'} D:${indicators.kdj_d ? indicators.kdj_d.toFixed(1) : '--'}</span>
                    </div>
                </td>
                <td class="px-4 py-4">
                    <div class="flex items-center gap-2">
                        <span class="signal-dot ${maDot}"></span>
                        ${sellWarning}
                    </div>
                </td>
                <td class="px-4 py-4">
                    <button class="text-indigo-400 hover:text-indigo-300 text-sm font-medium">
                        详情 →
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// 获取过滤后的股票
function getFilteredStocks() {
    let filtered = screeningResults;
    
    if (currentFilter !== 'all') {
        filtered = filtered.filter(s => s.grade === currentFilter);
    }
    
    const searchTerm = searchInput.value.toLowerCase();
    if (searchTerm) {
        filtered = filtered.filter(s => 
            s.code.toLowerCase().includes(searchTerm) ||
            s.name.toLowerCase().includes(searchTerm)
        );
    }
    
    return filtered;
}

// 过滤股票
function filterStocks() {
    currentFilter = gradeFilter.value;
    renderStockList();
}

// 显示股票详情
async function showStockDetail(stockCode) {
    const stock = screeningResults.find(s => s.code === stockCode);
    if (!stock) return;
    
    currentStock = stock;
    
    document.getElementById('modalStockName').textContent = stock.name;
    document.getElementById('modalStockCode').textContent = stock.code;
    
    // 更新评级徽章
    const gradeBadge = document.getElementById('modalGradeBadge');
    const gradeSpan = gradeBadge.querySelector('span');
    gradeBadge.classList.remove('hidden');
    gradeSpan.textContent = stock.grade + '级';
    gradeSpan.className = `inline-flex items-center justify-center px-3 py-1 rounded-lg text-sm font-bold text-white ${
        stock.grade === 'A' ? 'tag-grade-a' : stock.grade === 'B' ? 'tag-grade-b' : 'tag-grade-c'
    }`;
    
    // 更新监听按钮
    updateWatchButton();
    
    // 获取K线数据并渲染图表
    await loadKlineChart(stockCode);
    
    // 渲染详情内容
    renderDetailContent(stock);
    
    detailModal.classList.remove('hidden');
}

// 加载K线图
async function loadKlineChart(stockCode) {
    try {
        const response = await fetch(`/api/stock/${stockCode}/kline`);
        const data = await response.json();
        
        if (!data.success) return;
        
        const chartData = data.data;
        
        // 销毁旧图表
        if (klineChart) {
            klineChart.remove();
        }
        
        // 创建新图表
        const chartContainer = document.getElementById('klineChart');
        chartContainer.innerHTML = '';
        
        klineChart = LightweightCharts.createChart(chartContainer, {
            width: chartContainer.clientWidth,
            height: 320,
            layout: {
                background: { color: 'transparent' },
                textColor: '#94a3b8',
            },
            grid: {
                vertLines: { color: 'rgba(255, 255, 255, 0.1)' },
                horzLines: { color: 'rgba(255, 255, 255, 0.1)' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
            },
            timeScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
            },
        });
        
        // 添加K线系列
        const candlestickSeries = klineChart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderUpColor: '#10b981',
            borderDownColor: '#ef4444',
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        });
        
        candlestickSeries.setData(chartData.candles);
        
        // 添加MA线
        if (chartData.ma5) {
            const ma5Series = klineChart.addLineSeries({ color: '#fbbf24', lineWidth: 1 });
            ma5Series.setData(chartData.ma5);
        }
        if (chartData.ma10) {
            const ma10Series = klineChart.addLineSeries({ color: '#60a5fa', lineWidth: 1 });
            ma10Series.setData(chartData.ma10);
        }
        if (chartData.ma20) {
            const ma20Series = klineChart.addLineSeries({ color: '#a78bfa', lineWidth: 1 });
            ma20Series.setData(chartData.ma20);
        }
        
        klineChart.timeScale().fitContent();
        
    } catch (error) {
        console.error('加载K线失败:', error);
    }
}

// 渲染详情内容
function renderDetailContent(stock) {
    const indicators = stock.all_indicators || stock.indicators || {};
    const signals = stock.all_signals || stock.signals || {};
    const sellSignals = stock.sell_signals || {};
    const patterns = stock.patterns || [];
    const fundamental = stock.fundamental_analysis || {};
    const cyclical = stock.cyclical_analysis || {};
    
    let content = `
        <!-- 信号总览 -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            ${renderSignalCard('MACD金叉', signals.macd_golden_cross, 'macd_bearish_cross')}
            ${renderSignalCard('KDJ金叉', signals.kdj_golden_cross, 'kdj_bearish_cross')}
            ${renderSignalCard('均线多头', signals.ma_bullish, 'ma_bearish)}
            ${renderSignalCard('成交量放大', signals.volume_increase, 'volume_decrease')}
            ${renderSignalCard('RSI超买', null, signals.rsi_overbought)}
            ${renderSignalCard('RSI超卖', signals.rsi_oversold, null)}
            ${renderSignalCard('KDJ超买', null, signals.kdj_overbought)}
            ${renderSignalCard('KDJ超卖', signals.kdj_oversold, null)}
        </div>
        
        <!-- 技术指标详情 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- MACD -->
            <div class="glass-panel rounded-xl p-4">
                <h3 class="text-lg font-semibold text-white mb-4">MACD指标</h3>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-slate-400">DIF</span>
                        <span class="text-white">${indicators.macd_dif !== null ? indicators.macd_dif.toFixed(4) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">DEA</span>
                        <span class="text-white">${indicators.macd_dea !== null ? indicators.macd_dea.toFixed(4) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">柱状图</span>
                        <span class="${indicators.macd_hist > 0 ? 'text-emerald-400' : 'text-red-400'}">${indicators.macd_hist !== null ? indicators.macd_hist.toFixed(4) : '--'}</span>
                    </div>
                </div>
            </div>
            
            <!-- KDJ -->
            <div class="glass-panel rounded-xl p-4">
                <h3 class="text-lg font-semibold text-white mb-4">KDJ指标 (23,3,3)</h3>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-slate-400">K值</span>
                        <span class="text-white">${indicators.kdj_k !== null ? indicators.kdj_k.toFixed(2) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">D值</span>
                        <span class="text-white">${indicators.kdj_d !== null ? indicators.kdj_d.toFixed(2) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">J值</span>
                        <span class="${indicators.kdj_j > 100 ? 'text-red-400' : indicators.kdj_j < 0 ? 'text-emerald-400' : 'text-white'}">${indicators.kdj_j !== null ? indicators.kdj_j.toFixed(2) : '--'}</span>
                    </div>
                </div>
            </div>
            
            <!-- RSI -->
            <div class="glass-panel rounded-xl p-4">
                <h3 class="text-lg font-semibold text-white mb-4">RSI指标</h3>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-slate-400">RSI6</span>
                        <span class="${indicators.rsi6 > 70 ? 'text-red-400' : indicators.rsi6 < 30 ? 'text-emerald-400' : 'text-white'}">${indicators.rsi6 !== null ? indicators.rsi6.toFixed(2) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">RSI12</span>
                        <span class="${indicators.rsi12 > 70 ? 'text-red-400' : indicators.rsi12 < 30 ? 'text-emerald-400' : 'text-white'}">${indicators.rsi12 !== null ? indicators.rsi12.toFixed(2) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">RSI24</span>
                        <span class="${indicators.rsi24 > 70 ? 'text-red-400' : indicators.rsi24 < 30 ? 'text-emerald-400' : 'text-white'}">${indicators.rsi24 !== null ? indicators.rsi24.toFixed(2) : '--'}</span>
                    </div>
                </div>
            </div>
            
            <!-- 布林带 -->
            <div class="glass-panel rounded-xl p-4">
                <h3 class="text-lg font-semibold text-white mb-4">布林带</h3>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-slate-400">上轨</span>
                        <span class="text-white">${indicators.boll_up !== null ? indicators.boll_up.toFixed(2) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">中轨</span>
                        <span class="text-white">${indicators.boll_mid !== null ? indicators.boll_mid.toFixed(2) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">下轨</span>
                        <span class="text-white">${indicators.boll_down !== null ? indicators.boll_down.toFixed(2) : '--'}</span>
                    </div>
                </div>
            </div>
            
            <!-- DMI -->
            <div class="glass-panel rounded-xl p-4">
                <h3 class="text-lg font-semibold text-white mb-4">DMI指标</h3>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-slate-400">+DI</span>
                        <span class="text-white">${indicators.plus_di !== null ? indicators.plus_di.toFixed(2) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">-DI</span>
                        <span class="text-white">${indicators.minus_di !== null ? indicators.minus_di.toFixed(2) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">ADX</span>
                        <span class="${indicators.adx > 25 ? 'text-emerald-400' : 'text-white'}">${indicators.adx !== null ? indicators.adx.toFixed(2) : '--'}</span>
                    </div>
                </div>
            </div>
            
            <!-- 其他指标 -->
            <div class="glass-panel rounded-xl p-4">
                <h3 class="text-lg font-semibold text-white mb-4">其他指标</h3>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-slate-400">CCI</span>
                        <span class="${indicators.cci > 100 ? 'text-red-400' : indicators.cci < -100 ? 'text-emerald-400' : 'text-white'}">${indicators.cci !== null ? indicators.cci.toFixed(2) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">ATR14</span>
                        <span class="text-white">${indicators.atr14 !== null ? indicators.atr14.toFixed(2) : '--'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">量比</span>
                        <span class="${indicators.vol_ratio > 1.5 ? 'text-emerald-400' : 'text-white'}">${indicators.vol_ratio !== null ? indicators.vol_ratio.toFixed(2) : '--'}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 添加K线形态
    if (patterns && patterns.length > 0) {
        content += `
            <div class="glass-panel rounded-xl p-4 border border-indigo-500/30">
                <h3 class="text-lg font-semibold text-indigo-400 mb-4">📊 K线形态识别</h3>
                <div class="space-y-3">
                    ${patterns.map(p => `
                        <div class="p-3 rounded-lg ${p.signal.includes('看涨') ? 'bg-emerald-500/10 border border-emerald-500/30' : p.signal.includes('看跌') ? 'bg-red-500/10 border border-red-500/30' : 'bg-slate-700/30'}">
                            <div class="flex items-center justify-between mb-1">
                                <span class="font-medium text-white">${p.pattern}</span>
                                <span class="text-xs ${p.signal.includes('看涨') ? 'text-emerald-400' : p.signal.includes('看跌') ? 'text-red-400' : 'text-slate-400'}">${p.signal}</span>
                            </div>
                            ${p.target_price ? `<p class="text-xs text-slate-400">目标价: ¥${p.target_price}</p>` : ''}
                            ${p.description ? `<p class="text-xs text-slate-500 mt-1">${p.description}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // 添加支撑压力位分析
    const sr = stock.support_resistance || {};
    if (sr.support_resistance_levels) {
        const srLevels = sr.support_resistance_levels;
        const trendLines = sr.trend_lines || {};
        const pivotPoints = sr.pivot_points || {};
        const fibonacci = sr.fibonacci || {};
        
        content += `
            <div class="glass-panel rounded-xl p-4 border border-amber-500/30">
                <h3 class="text-lg font-semibold text-amber-400 mb-4">📐 支撑压力位与趋势线</h3>
                
                <!-- 关键价位 -->
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div class="p-3 rounded-lg bg-emerald-500/10">
                        <p class="text-xs text-slate-400 mb-1">最近支撑</p>
                        <p class="text-lg font-bold text-emerald-400">¥${srLevels.nearest_support || '--'}</p>
                    </div>
                    <div class="p-3 rounded-lg bg-red-500/10">
                        <p class="text-xs text-slate-400 mb-1">最近压力</p>
                        <p class="text-lg font-bold text-red-400">¥${srLevels.nearest_resistance || '--'}</p>
                    </div>
                </div>
                
                <!-- 支撑位列表 -->
                ${srLevels.supports && srLevels.supports.length > 0 ? `
                    <div class="mb-4">
                        <p class="text-xs text-slate-400 mb-2">支撑位</p>
                        <div class="space-y-1">
                            ${srLevels.supports.map(s => `
                                <div class="flex justify-between text-sm">
                                    <span class="text-emerald-400">¥${s.price}</span>
                                    <span class="text-slate-500">${s.distance}%</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <!-- 压力位列表 -->
                ${srLevels.resistances && srLevels.resistances.length > 0 ? `
                    <div class="mb-4">
                        <p class="text-xs text-slate-400 mb-2">压力位</p>
                        <div class="space-y-1">
                            ${srLevels.resistances.map(r => `
                                <div class="flex justify-between text-sm">
                                    <span class="text-red-400">¥${r.price}</span>
                                    <span class="text-slate-500">+${r.distance}%</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <!-- 趋势线 -->
                ${trendLines.short_term ? `
                    <div class="mb-4">
                        <p class="text-xs text-slate-400 mb-2">趋势分析</p>
                        <div class="grid grid-cols-3 gap-2 text-xs">
                            <div class="p-2 rounded bg-slate-700/30 text-center">
                                <p class="text-slate-500">短期</p>
                                <p class="${trendLines.short_term.trend.includes('上升') ? 'text-emerald-400' : trendLines.short_term.trend.includes('下降') ? 'text-red-400' : 'text-slate-400'}">${trendLines.short_term.trend}</p>
                                <p class="text-slate-600">${trendLines.short_term.angle}°</p>
                            </div>
                            <div class="p-2 rounded bg-slate-700/30 text-center">
                                <p class="text-slate-500">中期</p>
                                <p class="${trendLines.mid_term.trend.includes('上升') ? 'text-emerald-400' : trendLines.mid_term.trend.includes('下降') ? 'text-red-400' : 'text-slate-400'}">${trendLines.mid_term.trend}</p>
                            </div>
                            <div class="p-2 rounded bg-slate-700/30 text-center">
                                <p class="text-slate-500">长期</p>
                                <p class="${trendLines.long_term.trend.includes('上升') ? 'text-emerald-400' : trendLines.long_term.trend.includes('下降') ? 'text-red-400' : 'text-slate-400'}">${trendLines.long_term.trend}</p>
                            </div>
                        </div>
                    </div>
                ` : ''}
                
                <!-- 斐波那契 -->
                ${fibonacci.levels ? `
                    <div>
                        <p class="text-xs text-slate-400 mb-2">斐波那契回撤位</p>
                        <div class="flex flex-wrap gap-2">
                            ${Object.entries(fibonacci.levels).slice(0, 5).map(([level, price]) => `
                                <span class="px-2 py-1 rounded text-xs bg-slate-700/50 text-slate-300">${level}: ¥${price}</span>
                            `).join('')}
                        </div>
                        ${fibonacci.current_zone ? `<p class="text-xs text-slate-500 mt-2">当前区间: ${fibonacci.current_zone}</p>` : ''}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // 添加卖出信号
    if (sellSignals.suggestions && sellSignals.suggestions.length > 0) {
        content += `
            <div class="glass-panel rounded-xl p-4 border border-red-500/30">
                <h3 class="text-lg font-semibold text-red-400 mb-4">⚠️ 卖出/减仓信号</h3>
                <div class="space-y-2">
                    ${sellSignals.suggestions.map(s => `
                        <div class="flex items-center gap-3 p-2 rounded bg-red-500/10">
                            <span class="text-xs font-bold text-red-400">[${s.priority}]</span>
                            <span class="text-sm text-slate-300">${s.type}: ${s.action}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // 添加基本面
    if (fundamental.financial) {
        const fin = fundamental.financial;
        content += `
            <div class="glass-panel rounded-xl p-4">
                <h3 class="text-lg font-semibold text-white mb-4">财务指标</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="text-center">
                        <p class="text-xs text-slate-400">ROE</p>
                        <p class="text-lg font-semibold text-white">${fin.roe || '--'}%</p>
                    </div>
                    <div class="text-center">
                        <p class="text-xs text-slate-400">毛利率</p>
                        <p class="text-lg font-semibold text-white">${fin.gross_margin || '--'}%</p>
                    </div>
                    <div class="text-center">
                        <p class="text-xs text-slate-400">营收增长</p>
                        <p class="text-lg font-semibold ${fin.revenue_growth > 0 ? 'text-emerald-400' : 'text-red-400'}">${fin.revenue_growth || '--'}%</p>
                    </div>
                    <div class="text-center">
                        <p class="text-xs text-slate-400">利润增长</p>
                        <p class="text-lg font-semibold ${fin.profit_growth > 0 ? 'text-emerald-400' : 'text-red-400'}">${fin.profit_growth || '--'}%</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    document.getElementById('modalContent').innerHTML = content;
}

// 渲染信号卡片
function renderSignalCard(name, positive, negative) {
    let status, color;
    if (positive) {
        status = '✓ 是';
        color = 'text-emerald-400';
    } else if (negative) {
        status = '✗ 是';
        color = 'text-red-400';
    } else {
        status = '--';
        color = 'text-slate-500';
    }
    
    return `
        <div class="glass-panel rounded-lg p-3 text-center">
            <p class="text-xs text-slate-400 mb-1">${name}</p>
            <p class="text-sm font-medium ${color}">${status}</p>
        </div>
    `;
}

// 更新监听按钮
function updateWatchButton() {
    if (!currentStock) return;
    
    const isWatched = watchlist.includes(currentStock.code);
    btnAddWatch.innerHTML = isWatched ? `
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
        已监听
    ` : `
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        加入监听
    `;
    btnAddWatch.className = isWatched 
        ? 'px-4 py-2 rounded-lg text-white text-sm font-medium flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700'
        : 'btn-primary px-4 py-2 rounded-lg text-white text-sm font-medium flex items-center gap-2';
}

// 切换监听状态
function toggleWatchlist() {
    if (!currentStock) return;
    
    const index = watchlist.indexOf(currentStock.code);
    if (index > -1) {
        watchlist.splice(index, 1);
    } else {
        watchlist.push(currentStock.code);
    }
    
    localStorage.setItem('watchlist', JSON.stringify(watchlist));
    updateWatchButton();
    renderStockList();
    updateWatchlistCount();
}

// 关闭模态框
function closeModal() {
    detailModal.classList.add('hidden');
    if (klineChart) {
        klineChart.remove();
        klineChart = null;
    }
}

// 加载历史数据
function loadHistory() {
    const saved = localStorage.getItem('screeningResults');
    if (saved) {
        screeningResults = JSON.parse(saved);
        showResults();
    } else {
        alert('暂无历史数据');
    }
}