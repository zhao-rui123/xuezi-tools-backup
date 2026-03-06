import { useState, useMemo, useEffect } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import {
  provinceList,
  electricityPriceData,
  priceTypeColors,
  generate24HourData,
  getProvinceData,
} from './data/electricityPriceData';
import './App.css';

// 月份列表
const months = Array.from({ length: 12 }, (_, i) => i + 1);

// 时段颜色配置
const PERIOD_COLORS: Record<string, string> = {
  '尖峰': '#ff4d4f',
  '高峰': '#fa8c16',
  '平段': '#52c41a',
  '低谷': '#1890ff',
  '深谷': '#722ed1',
};

// 时段顺序（用于排序）
const PERIOD_ORDER = ['尖峰', '高峰', '平段', '低谷', '深谷'];

// 自定义Tooltip组件
const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="custom-tooltip" style={{
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: '10px 15px',
        borderRadius: '8px',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        color: '#fff',
        fontSize: '14px'
      }}>
        <div style={{ marginBottom: '5px', fontWeight: 'bold' }}>
          {data.hour}:00 - {data.hour + 1}:00
        </div>
        <div style={{ color: PERIOD_COLORS[data.type] || '#fff' }}>
          时段类型: {data.type}
        </div>
      </div>
    );
  }
  return null;
};

function App() {
  const [selectedProvince, setSelectedProvince] = useState<string>('JS');
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);

  // 过滤省份列表
  const filteredProvinces = useMemo(() => {
    if (!searchQuery.trim()) return provinceList;
    return provinceList.filter(p =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [searchQuery]);

  // 获取当前省份数据
  const provinceData = useMemo(() => {
    return getProvinceData(selectedProvince, selectedMonth);
  }, [selectedProvince, selectedMonth]);

  // 生成24小时图表数据
  const chartData = useMemo(() => {
    if (!provinceData || !provinceData.hasTimeOfUse) return [];
    return generate24HourData(selectedProvince, selectedMonth);
  }, [selectedProvince, selectedMonth, provinceData]);

  // 获取时段统计（合并连续时段）
  const timeSlotStats = useMemo(() => {
    if (!provinceData || !provinceData.hasTimeOfUse) return [];
    
    const slots = provinceData.timeSlots;
    const stats: { 
      type: string; 
      hours: number; 
      label: string; 
      color: string;
      timeRanges: string[];
    }[] = [];
    
    Object.entries(priceTypeColors).forEach(([type, config]) => {
      const typeSlots = slots.filter(s => s.type === type);
      if (typeSlots.length > 0) {
        const hours = typeSlots.reduce((sum, s) => {
          if (s.end < s.start) { // 跨天
            return sum + (24 - s.start + s.end);
          }
          return sum + (s.end - s.start);
        }, 0);
        
        // 格式化时间范围
        const timeRanges = typeSlots.map(s => {
          if (s.end < s.start) { // 跨天
            return `${s.start}:00-次日${s.end}:00`;
          }
          return `${s.start}:00-${s.end}:00`;
        });
        
        stats.push({
          type,
          hours,
          label: config.label,
          color: config.color,
          timeRanges,
        });
      }
    });
    
    // 按时段优先级排序
    return stats.sort((a, b) => {
      return PERIOD_ORDER.indexOf(a.type) - PERIOD_ORDER.indexOf(b.type);
    });
  }, [provinceData]);

  // 点击外部关闭下拉菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.province-selector')) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 选择省份
  const handleProvinceSelect = (code: string) => {
    setSelectedProvince(code);
    setIsDropdownOpen(false);
    setSearchQuery('');
  };

  // 获取当前省份名称
  const currentProvinceName = provinceList.find(p => p.code === selectedProvince)?.name || '';

  return (
    <div className="app">
      {/* 头部 */}
      <header className="header">
        <h1 className="title">
          <span className="gradient-text">⚡ 分时电价查询系统</span>
        </h1>
        <p className="subtitle">全国各省工商业分时电价时段分布</p>
      </header>

      {/* 控制面板 */}
      <div className="control-panel">
        {/* 省份选择器 */}
        <div className="control-group province-selector">
          <label className="control-label">选择省份</label>
          <div className="dropdown-container">
            <button
              className="dropdown-trigger"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              <span>{currentProvinceName}</span>
              <svg
                className={`dropdown-arrow ${isDropdownOpen ? 'open' : ''}`}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>
            {isDropdownOpen && (
              <div className="dropdown-menu">
                <div className="search-box">
                  <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.35-4.35" />
                  </svg>
                  <input
                    type="text"
                    placeholder="搜索省份..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                    autoFocus
                  />
                </div>
                <div className="dropdown-list">
                  {filteredProvinces.map((province) => (
                    <button
                      key={province.code}
                      className={`dropdown-item ${selectedProvince === province.code ? 'active' : ''}`}
                      onClick={() => handleProvinceSelect(province.code)}
                    >
                      {province.name}
                      {electricityPriceData[province.code]?.hasTimeOfUse === false && (
                        <span className="no-tou-badge">无分时</span>
                      )}
                    </button>
                  ))}
                  {filteredProvinces.length === 0 && (
                    <div className="dropdown-empty">未找到匹配的省份</div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 月份选择器 */}
        <div className="control-group">
          <label className="control-label">选择月份</label>
          <div className="month-selector">
            {months.map((month) => (
              <button
                key={month}
                className={`month-btn ${selectedMonth === month ? 'active' : ''}`}
                onClick={() => setSelectedMonth(month)}
              >
                {month}月
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <main className="main-content">
        {!provinceData?.hasTimeOfUse ? (
          /* 无分时电价提示 */
          <div className="no-tou-message">
            <div className="no-tou-icon">⚠️</div>
            <h3>该省份暂不执行分时电价政策</h3>
            <p>{provinceData?.note || '当前省份暂无分时电价数据。'}</p>
          </div>
        ) : (
          <>
            {/* 时段分布图表 */}
            <div className="chart-container">
              <h3 className="section-title">
                <span className="title-icon">📊</span>
                24小时时段分布
              </h3>
              
              {/* 时段颜色图例 */}
              <div className="chart-legend">
                {Object.entries(PERIOD_COLORS).map(([type, color]) => (
                  <div key={type} className="chart-legend-item">
                    <span className="chart-legend-color" style={{ backgroundColor: color }} />
                    <span className="chart-legend-label">{type}</span>
                  </div>
                ))}
              </div>
              
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
                    <defs>
                      <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1890ff" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#1890ff" stopOpacity={0.05} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                      dataKey="hour"
                      stroke="rgba(255,255,255,0.5)"
                      tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
                      tickFormatter={(value) => `${value}h`}
                      interval={1}
                    />
                    <YAxis hide />
                    <Tooltip content={<CustomTooltip />} />
                    <Area
                      type="stepAfter"
                      dataKey="value"
                      stroke="#1890ff"
                      strokeWidth={2}
                      fill="url(#priceGradient)"
                      dot={{ fill: '#1890ff', strokeWidth: 2, r: 3 }}
                      activeDot={{ r: 5, fill: '#40a9ff' }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 时段详情 */}
            <div className="time-slots-section">
              <h3 className="section-title">
                <span className="title-icon">⏰</span>
                时段详情
              </h3>
              <div className="time-slots-grid">
                {timeSlotStats.map((slot) => (
                  <div
                    key={slot.type}
                    className="time-slot-card"
                    style={{ borderColor: slot.color }}
                  >
                    <div className="slot-header" style={{ backgroundColor: `${slot.color}20` }}>
                      <span className="slot-type" style={{ color: slot.color }}>
                        {slot.label}
                      </span>
                      <span className="slot-hours">{slot.hours}小时</span>
                    </div>
                    <div className="slot-body">
                      <div className="slot-time-ranges">
                        {slot.timeRanges.map((range, idx) => (
                          <span key={idx} className="time-range-tag">
                            {range}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 省份备注 */}
            {provinceData?.note && (
              <div className="note-section">
                <h3 className="section-title">
                  <span className="title-icon">📝</span>
                  政策说明
                </h3>
                <div className="note-content">
                  <p>{provinceData.note}</p>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* 图例 */}
      <footer className="footer">
        <div className="legend">
          <span className="legend-title">时段类型：</span>
          {Object.entries(priceTypeColors).map(([type, config]) => (
            <div key={type} className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: config.color }} />
              <span className="legend-label">{config.label}</span>
            </div>
          ))}
        </div>
        <p className="footer-note">数据仅供参考，实际电价以当地电网公司公布为准</p>
      </footer>
    </div>
  );
}

export default App;