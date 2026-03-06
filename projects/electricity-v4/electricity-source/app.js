/**
 * 电价查询系统主逻辑
 * 处理UI交互、数据展示和图表渲染
 */

class ElectricityPriceApp {
  constructor() {
    this.currentProvince = '山东';
    this.currentYear = 2026;
    this.currentMonth = 2;
    this.chart = null;
    this.searchTerm = '';
    
    this.init();
  }

  init() {
    this.cacheElements();
    this.bindEvents();
    this.renderProvinceOptions();
    this.updateDisplay();
  }

  cacheElements() {
    this.provinceSelect = document.getElementById('provinceSelect');
    this.monthSelect = document.getElementById('monthSelect');
    this.searchInput = document.getElementById('searchInput');
    this.noteBox = document.getElementById('noteBox');
    this.cycleBadge = document.getElementById('cycleBadge');
    this.chartContainer = document.getElementById('chartContainer');
    this.tableContainer = document.getElementById('tableContainer');
    this.statsContainer = document.getElementById('statsContainer');
    this.noDataMessage = document.getElementById('noDataMessage');
  }

  bindEvents() {
    // 省份选择
    this.provinceSelect.addEventListener('change', (e) => {
      this.currentProvince = e.target.value;
      this.updateAvailableMonths();
      this.updateDisplay();
    });

    // 月份选择
    this.monthSelect.addEventListener('change', (e) => {
      this.currentMonth = parseInt(e.target.value);
      this.updateDisplay();
    });

    // 搜索功能
    this.searchInput.addEventListener('input', (e) => {
      this.searchTerm = e.target.value.trim().toLowerCase();
      this.renderProvinceOptions();
    });
  }

  renderProvinceOptions() {
    const provinces = priceService.getProvinces();
    const filtered = this.searchTerm 
      ? provinces.filter(p => p.toLowerCase().includes(this.searchTerm))
      : provinces;

    this.provinceSelect.innerHTML = filtered.map(province => 
      `<option value="${province}" ${province === this.currentProvince ? 'selected' : ''}>${province}</option>`
    ).join('');

    // 如果当前省份不在过滤结果中，选择第一个
    if (filtered.length > 0 && !filtered.includes(this.currentProvince)) {
      this.currentProvince = filtered[0];
      this.updateAvailableMonths();
    }
  }

  updateAvailableMonths() {
    const availableMonths = priceService.getAvailableMonths(this.currentProvince, this.currentYear);
    
    if (availableMonths.length === 0) {
      this.monthSelect.innerHTML = '<option value="">无数据</option>';
      this.monthSelect.disabled = true;
      return;
    }

    this.monthSelect.disabled = false;
    this.monthSelect.innerHTML = availableMonths.map(month => 
      `<option value="${month}" ${month === this.currentMonth ? 'selected' : ''}>${month}月</option>`
    ).join('');

    // 如果当前月份不可用，选择第一个可用月份
    if (!availableMonths.includes(this.currentMonth)) {
      this.currentMonth = availableMonths[0];
    }
  }

  updateDisplay() {
    const priceData = priceService.getPriceData(this.currentProvince, this.currentYear, this.currentMonth);
    
    if (!priceData) {
      this.showNoData();
      return;
    }

    this.hideNoData();
    this.updateNote();
    this.updateCycleBadge();
    this.renderChart();
    this.renderTable();
    this.renderStats();
  }

  showNoData() {
    this.chartContainer.style.display = 'none';
    this.tableContainer.style.display = 'none';
    this.statsContainer.style.display = 'none';
    this.cycleBadge.style.display = 'none';
    this.noDataMessage.style.display = 'block';
  }

  hideNoData() {
    this.chartContainer.style.display = 'block';
    this.tableContainer.style.display = 'block';
    this.statsContainer.style.display = 'grid';
    this.cycleBadge.style.display = 'flex';
    this.noDataMessage.style.display = 'none';
  }

  updateNote() {
    const note = priceService.getProvinceNote(this.currentProvince);
    if (note) {
      this.noteBox.innerHTML = `<div class="note-content">📌 ${note}</div>`;
      this.noteBox.style.display = 'block';
    } else {
      this.noteBox.style.display = 'none';
    }
  }

  updateCycleBadge() {
    const cycles = priceService.getCycles(this.currentProvince, this.currentYear, this.currentMonth);
    this.cycleBadge.innerHTML = `
      <span class="cycle-label">循环次数</span>
      <span class="cycle-value">${cycles}次</span>
    `;
  }

  renderChart() {
    const hourlyData = priceService.get24HourData(this.currentProvince, this.currentYear, this.currentMonth);
    
    if (!hourlyData) return;

    const labels = hourlyData.map(d => d.hourLabel);
    const prices = hourlyData.map(d => d.price);
    const colors = hourlyData.map(d => d.color);

    // 销毁旧图表
    if (this.chart) {
      this.chart.destroy();
    }

    const ctx = document.getElementById('priceChart').getContext('2d');
    
    this.chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: '电价 (元/kWh)',
          data: prices,
          backgroundColor: colors,
          borderRadius: 4,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            padding: 12,
            callbacks: {
              title: (context) => {
                return `${context[0].label} 时段`;
              },
              label: (context) => {
                const data = hourlyData[context.dataIndex];
                return [
                  `电价: ${context.raw.toFixed(4)} 元/kWh`,
                  `类型: ${data.typeName}`
                ];
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(255, 255, 255, 0.05)'
            },
            ticks: {
              color: '#94a3b8',
              callback: function(value) {
                return value.toFixed(2);
              }
            },
            title: {
              display: true,
              text: '电价 (元/kWh)',
              color: '#64748b'
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: '#94a3b8',
              maxRotation: 45,
              minRotation: 45
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    });
  }

  renderTable() {
    const timeSlots = priceService.getTimeSlots(this.currentProvince, this.currentYear, this.currentMonth);
    
    if (timeSlots.length === 0) {
      this.tableContainer.innerHTML = '<p class="no-data">暂无时段数据</p>';
      return;
    }

    const tbody = document.getElementById('priceTableBody');
    
    tbody.innerHTML = timeSlots.map(slot => `
      <tr class="price-row" data-type="${slot.type}">
        <td>
          <span class="type-badge" style="background: ${slot.color}20; color: ${slot.color}; border: 1px solid ${slot.color}40;">
            ${slot.typeName}
          </span>
        </td>
        <td class="price-cell">${slot.price.toFixed(4)}</td>
        <td>${slot.hourCount}小时</td>
        <td class="time-ranges">
          ${slot.ranges.map(range => `<span class="time-tag">${range}</span>`).join('')}
        </td>
      </tr>
    `).join('');
  }

  renderStats() {
    const stats = priceService.getStatistics(this.currentProvince, this.currentYear, this.currentMonth);
    
    if (!stats) return;

    const statsContainer = document.getElementById('statsContainer');
    
    statsContainer.innerHTML = `
      <div class="stat-card">
        <div class="stat-label">最高电价</div>
        <div class="stat-value" style="color: #ef4444;">${stats.maxPrice.toFixed(4)}</div>
        <div class="stat-unit">元/kWh</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">最低电价</div>
        <div class="stat-value" style="color: #6366f1;">${stats.minPrice.toFixed(4)}</div>
        <div class="stat-unit">元/kWh</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">平均电价</div>
        <div class="stat-value" style="color: #22c55e;">${stats.avgPrice}</div>
        <div class="stat-unit">元/kWh</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">峰谷价差</div>
        <div class="stat-value" style="color: #f97316;">${stats.priceDiff}</div>
        <div class="stat-unit">元/kWh</div>
      </div>
    `;
  }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
  window.app = new ElectricityPriceApp();
});
