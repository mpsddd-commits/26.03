import { useState, useEffect, useCallback } from 'react';
import { ResponsiveLine } from '@nivo/line';
import { Search, Clock, Zap, Users, AlertCircle } from 'lucide-react';
import { fetchTimePattern, fetchGoldenTime } from '@utils/network.js';
import LoadingOverlay from '@components/LoadingOverlay.jsx';
import styles from '@styles/HourlyPattern.module.css';

// ── 시간대 정렬 순서 ────────────────────────────────────────────
const TIME_ORDER = [
  '05~06','06~07','07~08','08~09','09~10','10~11',
  '11~12','12~13','13~14','14~15','15~16','16~17',
  '17~18','18~19','19~20','20~21','21~22','22~23','23~24','24~',
]

/**
 * Nivo Line의 data 배열을 TIME_ORDER 기준으로 정렬
 * 각 point는 { x, y, 혼잡도지수 } 형태
 */
const sortByTime = (arr) =>
  [...arr].sort((a, b) => TIME_ORDER.indexOf(a.x) - TIME_ORDER.indexOf(b.x));

// ── Nivo 차트 테마 ─────────────────────────────────────────────
const CHART_THEME = {
  background: 'transparent',
  textColor: '#8fa3c4',
  fontSize: 11,
  fontFamily: "'DM Sans', sans-serif",
  axis: {
    domain: { line: { stroke: '#1f2d47', strokeWidth: 1 } },
    ticks: {
      line: { stroke: '#1f2d47' },
      text: { fill: '#8fa3c4', fontSize: 11 },
    },
    legend: { text: { fill: '#4a6080', fontSize: 11 } },
  },
  grid: { line: { stroke: '#1f2d47', strokeWidth: 1 } },
  crosshair: { line: { stroke: '#3b82f6', strokeWidth: 1, strokeOpacity: 0.5 } },
  tooltip: {
    container: {
      background: '#141b2d',
      color: '#e8f0fe',
      fontSize: 12,
      borderRadius: 6,
      border: '1px solid #1f2d47',
      padding: '8px 12px',
    },
  },
};

// 2021 → 2008
const YEARS = []
for (let i = 0; i < 14; i++) {
  YEARS.push(String(2021 - i))
}

// ──────────────────────────────────────────────────────────────
const HourlyPattern = () => {
  const [year,       setYear]       = useState('2021');
  const [station,    setStation]    = useState('강남');
  const [inputVal,   setInputVal]   = useState('강남');
  const [dayType,    setDayType]    = useState('평일');
  const [chartData,  setChartData]  = useState([]);
  const [goldenTime, setGoldenTime] = useState([]);
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState(null);

  const load = useCallback(async () => {
    if (!station.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const [patternRes, goldenRes] = await Promise.all([
        fetchTimePattern(year, station, dayType),
        fetchGoldenTime(year, station, dayType),
      ]);

      const raw = patternRes?.result ?? [];

      const formatted = raw.map(line => ({
        id: line.id,                        
        data: sortByTime(line.data ?? []),
      }));

      setChartData(formatted);
      setGoldenTime(goldenRes?.result ?? []);

    } catch {
      setError('데이터를 불러오지 못했습니다. API 서버를 확인해주세요.');
    } finally {
      setLoading(false);
    }
  }, [year, station, dayType]);

  useEffect(() => { load(); }, [load]);

  const handleSearch = () => setStation(inputVal.trim());

  const peakEmoji = (i) => ['🥇', '🥈', '🥉'][i] ?? '';

  return (
    <div className={styles.page}>

      {/* ── 컨트롤 바 ─────────────────────────────────────── */}
      <div className={styles.controls}>

        {/* 역명 검색 */}
        <div className={styles.searchBox}>
          <Search size={14} className={styles.searchIcon} />
          <input
            className={styles.searchInput}
            value={inputVal}
            onChange={e => setInputVal(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="역명 입력 (예: 강남, 홍대입구)"
          />
          <button className={styles.searchBtn} onClick={handleSearch}>검색</button>
        </div>

        {/* 연도 필터 */}
        <div className={styles.filterGroup}>
          {YEARS.map(y => (
            <button
              key={y}
              className={`${styles.filterBtn} ${year === y ? styles.active : ''}`}
              onClick={() => setYear(y)}
            >{y}</button>
          ))}
        </div>

        {/* 평일/주말 필터 */}
        <div className={styles.filterGroup}>
          {['평일', '주말'].map(d => (
            <button
              key={d}
              className={`${styles.filterBtn} ${dayType === d ? styles.active : ''}`}
              onClick={() => setDayType(d)}
            >{d}</button>
          ))}
        </div>
      </div>

      {/* ── 골든타임 카드 ──────────────────────────────────── */}
      {goldenTime.length > 0 && (
        <div className={styles.goldenRow}>
          <div className={styles.goldenLabel}>
            <Zap size={13} />
            <span>골든 타임 (혼잡도 TOP 3)</span>
          </div>
          {goldenTime.map((g, i) => (
            <div key={g['시간대']} className={styles.goldenCard}>
              <span className={styles.goldenRank}>{peakEmoji(i)}</span>
              <span className={styles.goldenTime}>{g['시간대']}</span>
              <span className={styles.goldenValue}>
                <Users size={11} />
                {Math.round(g['총인원']).toLocaleString()}명
              </span>
              <span className={styles.goldenCongestion}>
                혼잡도 {g['최대혼잡도']}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* ── 메인 차트 카드 ──────────────────────────────────── */}
      <div className={styles.chartCard}>

        <div className={styles.cardHeader}>
          <Clock size={14} color="var(--text-muted)" />
          <span className={styles.cardTitle}>
            {station} · {year}년 · {dayType} — 시간대별 평균 승하차 인원
          </span>
          <span className={styles.cardNote}>
            혼잡도 지수 = (시간대 평균 / 전체 시간대 평균) × 100
          </span>
        </div>

        <div className={styles.chartArea}>
          {loading && <LoadingOverlay message="데이터 집계 중..." />}

          {!loading && error && (
            <div className={styles.errorBox}>
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          {!loading && !error && chartData.length === 0 && (
            <div className={styles.empty}>조회된 데이터가 없습니다.</div>
          )}

          {!loading && !error && chartData.length > 0 && (
            <ResponsiveLine
              data={chartData}
              theme={CHART_THEME}
              margin={{ top: 24, right: 130, bottom: 80, left: 90 }}
              xScale={{ type: 'point' }}
              yScale={{ type: 'linear', min: 'auto', max: 'auto', stacked: false }}
              curve="monotoneX"
              axisBottom={{
                tickSize: 5,
                tickPadding: 6,
                tickRotation: -45,
                legend: '시간대',
                legendOffset: 68,
                legendPosition: 'middle',
              }}
              axisLeft={{
                tickSize: 5,
                tickPadding: 10,
                legend: '평균 인원 (명)',
                legendOffset: -78, 
                legendPosition: 'middle',
                format: v =>
                  v >= 1_000_000 ? `${(v / 1_000_000).toFixed(1)}M`
                  : v >= 1_000  ? `${(v / 1_000).toFixed(0)}k`
                  : String(v),
              }}
              colors={['#3b82f6', '#10d9a0']}
              lineWidth={2}
              pointSize={5}
              pointColor={{ theme: 'background' }}
              pointBorderWidth={2}
              pointBorderColor={{ from: 'serieColor' }}
              enableArea
              areaOpacity={0.08}
              useMesh
              legends={[{
                anchor: 'right',
                direction: 'column',
                justify: false,
                translateX: 120,
                translateY: 0,
                itemWidth: 80,
                itemHeight: 22,
                itemTextColor: '#8fa3c4',
                symbolSize: 10,
                symbolShape: 'circle',
                effects: [{ on: 'hover', style: { itemTextColor: '#e8f0fe' } }],
              }]}
              tooltip={({ point }) => (
                <div style={{
                  background: '#141b2d',
                  border: '1px solid #1f2d47',
                  borderRadius: 6,
                  padding: '8px 12px',
                  fontSize: 12,
                  color: '#e8f0fe',
                  lineHeight: 1.7,
                }}>
                  <strong style={{ color: point.serieColor }}>{point.serieId}</strong>
                  <div>시간대: {point.data.xFormatted}</div>
                  <div>평균 인원: <strong>{Math.round(point.data.y).toLocaleString()}명</strong></div>
                  {point.data['혼잡도지수'] != null && (
                    <div>혼잡도 지수: <strong>{point.data['혼잡도지수']}</strong></div>
                  )}
                </div>
              )}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default HourlyPattern