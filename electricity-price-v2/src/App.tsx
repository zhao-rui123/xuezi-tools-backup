import { useState, useMemo, useEffect } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
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

// 自定义Tooltip组件
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const typeInfo = priceTypeColors[data.type as keyof typeof priceTypeColors];
    return (
      <div className="custom-tooltip">
        <p className="tooltip-time">{label}</p>
        <p className="tooltip-price" style={{ color: typeInfo?.color || '#fff' }}>
          电价: {data.price.toFixed(4)} 元/kWh
        </p>
        <p className="tooltip-type" style={{ color: typeInfo?.color || '#fff' }}>
          类型: {typeInfo?.label || '平段'}
        </p>
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
    return getProvinceData(selectedProvince);
  }, [selectedProvince]);

  // 生成24小时图表数据
  const chartData = useMemo(() => {
    if (!provinceData || !provinceData.hasTimeOfUse) return [];
    return generate24HourData(selectedProvince);
  }, [selectedProvince, provinceData]);

  // 计算统计数据
  const stats = useMemo(() => {
    if (!provinceData || !provinceData.hasTimeOfUse || chartData.length === 0) {
      return { max: 0, min: 0, avg: 0, diff: 0 };
    }
    const prices = chartData.map(d => d.price);
    const max = Math.max(...prices);
    const min = Math.min(...prices);
    const avg = prices.reduce((a, b) => a + b, 0) / prices.length;
    return { max, min, avg, diff: max - min };
  }, [chartData, provinceData]);

  // 获取时段统计
  const timeSlotStats = useMemo(() => {
    if (!provinceData || !provinceData.hasTimeOfUse) return [];
    
    const slots = provinceData.timeSlots;
    const stats: { type: string; hours: number; avgPrice: number; label: string; color: string }[] = [];
    
    Object.entries(priceTypeColors).forEach(([type, config]) => {
      const typeSlots = slots.filter(s => s.type === type);
      if (typeSlots.length > 0) {
        const hours = typeSlots.reduce((sum, s) => sum + (s.end - s.start), 0);
        const avgPrice = typeSlots.reduce((sum, s) => sum + s.price * (s.end - s.start), 0) / hours;
        stats.push({
          type,
          hours,
          avgPrice,
          label: config.label,
          color: config.color,
        });
      }
    });
    
    return stats.sort((a, b) => b.avgPrice - a.avgPrice);
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
        <p className="subtitle">全国各省工商业分时电价查询工具</p>
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
            {/* 统计卡片 */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">最高电价</div>
                <div className="stat-value" style={{ color: priceTypeColors.peak.color }}>
                  {stats.max.toFixed(4)}
                </div>
                <div className="stat-unit">元/kWh</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">最低电价</div>
                <div className="stat-value" style={{ color: priceTypeColors.valley.color }}>
                  {stats.min.toFixed(4)}
                </div>
                <div className="stat-unit">元/kWh</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">平均电价</div>
                <div className="stat-value" style={{ color: priceTypeColors.normal.color }}>
                  {stats.avg.toFixed(4)}
                </div>
                <div className="stat-unit">元/kWh</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">峰谷价差</div>
                <div className="stat-value highlight">{stats.diff.toFixed(4)}</div>
                <div className="stat-unit">元/kWh</div>
              </div>
            </div>

            {/* 电价图表 */}
            <div className="chart-container">
              <h3 className="section-title">
                <span className="title-icon">📊</span>
                24小时电价走势
              </h3>
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height={350}>
                  <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
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
                      interval={2}
                    />
                    <YAxis
                      stroke="rgba(255,255,255,0.5)"
                      tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
                      domain={[0, 'auto']}
                      tickFormatter={(value) => value.toFixed(2)}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Area
                      type="stepAfter"
                      dataKey="price"
                      stroke="#1890ff"
                      strokeWidth={2}
                      fill="url(#priceGradient)"
                      dot={{ fill: '#1890ff', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, fill: '#40a9ff' }}
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
                      <div className="slot-price">
                        <span className="price-value" style={{ color: slot.color }}>
                          {slot.avgPrice.toFixed(4)}
                        </span>
                        <span className="price-unit">元/kWh</span>
                      </div>
                      <div className="slot-time">
                        {provinceData?.timeSlots
                          .filter(s => s.type === slot.type)
                          .map(s => `${s.start}:00-${s.end}:00`)
                          .join(', ')}
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
          <span className="legend-title">电价类型：</span>
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
