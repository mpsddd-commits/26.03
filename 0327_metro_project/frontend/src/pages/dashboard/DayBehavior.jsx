import { useState, useEffect, useCallback } from 'react';
import { ResponsiveHeatMap } from '@nivo/heatmap';
import { BarChart2, List, X, AlertCircle, TrendingUp, Moon } from 'lucide-react';
import { fetchHeatmap, fetchClickRanking } from '@utils/network.js';
import LoadingOverlay from '@components/LoadingOverlay.jsx';
import styles from '@styles/DayBehavior.module.css';

const CHART_THEME = {
  background: 'transparent',
  textColor: '#8fa3c4',
  fontSize: 11,
  fontFamily: "'DM Sans', sans-serif",
  axis: {
    ticks: { text: { fill: '#8fa3c4', fontSize: 11 } },
    legend: { text: { fill: '#4a6080', fontSize: 12 } },
  },
  tooltip: {
    container: {
      background: '#141b2d',
      color: '#e8f0fe',
      fontSize: 12,
      borderRadius: 6,
      border: '1px solid #1f2d47',
    },
  },
};

const YEARS = []
for (let i = 0; i < 14; i++) {
  YEARS.push(String(2021 - i))
}

const ON_OFF = ['전체','승차','하차'];
const MODES = [
  { value: 'total', label: '전체 이용객', Icon: TrendingUp },
  { value: 'night', label: '심야 급증',   Icon: Moon },
];

const DayBehavior = () => {
  const [year,    setYear]    = useState('2021');
  const [onOff,   setOnOff]   = useState('전체');
  const [heatData, setHeatData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const [sidebar,     setSidebar]     = useState(null);
  const [rankData,    setRankData]    = useState([]);
  const [rankMode,    setRankMode]    = useState('total');
  const [rankLoading, setRankLoading] = useState(false);

  const loadHeatmap = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchHeatmap(year, onOff);
      setHeatData(res?.result ?? []);
    } catch {
      setError('히트맵 데이터를 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  }, [year, onOff]);

  useEffect(() => { loadHeatmap(); }, [loadHeatmap]);

  const loadRanking = useCallback(async (line, dayName, mode) => {
    setRankLoading(true);
    try {
      const res = await fetchClickRanking(year, line, dayName, mode, onOff);
      setRankData(res?.result ?? []);
    } catch {
      setRankData([]);
    } finally {
      setRankLoading(false);
    }
  }, [year, onOff]);

  const handleCellClick = (cell) => {
    const line    = cell.serieId;
    const dayName = cell.data.x;
    setSidebar({ line, dayName });
    loadRanking(line, dayName, rankMode);
  };

  const handleModeChange = (mode) => {
    setRankMode(mode);
    if (sidebar) loadRanking(sidebar.line, sidebar.dayName, mode);
  };

  const rankValueKey = rankMode === 'total' ? '총이용량' : '심야이용량';
  const rankMax = rankData.length > 0
    ? Math.max(...rankData.map(r => r[rankValueKey] ?? 0))
    : 1;

  return (
    <div className={styles.page}>
      {/* ── 컨트롤 바 ─────────────────────────────────────── */}
      <div className={styles.controls}>
        <div className={styles.filterGroup}>
          {YEARS.map(y => (
            <button
              key={y}
              className={`${styles.filterBtn} ${year === y ? styles.active : ''}`}
              onClick={() => setYear(y)}
            >{y}</button>
          ))}
        </div>

        <div className={styles.filterGroup}>
          {ON_OFF.map(o => (
            <button
              key={o}
              className={`${styles.filterBtn} ${onOff === o ? styles.activeGreen : ''}`}
              onClick={() => setOnOff(o)}
            >{o}</button>
          ))}
        </div>

        <span className={styles.hint}>
          셀 클릭 시 해당 노선·요일의 역별 랭킹을 확인할 수 있습니다
        </span>
      </div>

      {/* ── 본문 레이아웃 ──────────────────────────────────── */}
      <div className={`${styles.layout} ${sidebar ? styles.withSidebar : ''}`}>

        {/* ── 히트맵 카드 ─────────────────────────────────── */}
        <div className={styles.chartCard}>
          <div className={styles.cardHeader}>
            <BarChart2 size={14} />
            <span className={styles.cardTitle}>
              {year}년 · {onOff} — 호선별 요일 이용객 히트맵
            </span>
            <span className={styles.cardNote}>Y축: 호선 | X축: 요일 | 색상: 합계 인원</span>
          </div>

          <div className={styles.chartArea}>
            {loading && <LoadingOverlay message="히트맵 집계 중..." />}
            {!loading && error && (
              <div className={styles.errorBox}><AlertCircle size={16} /><span>{error}</span></div>
            )}
            {!loading && !error && heatData.length === 0 && (
              <div className={styles.empty}>조회된 데이터가 없습니다.</div>
            )}
            {!loading && !error && heatData.length > 0 && (
              <ResponsiveHeatMap
                data={heatData}
                theme={CHART_THEME}
                margin={{ top: 20, right: 20, bottom: 70, left: 100 }}
                valueFormat=">-.2s"
                axisTop={null}
                axisRight={null}
                axisBottom={{
                  tickSize: 4,
                  tickPadding: 8,
                  tickRotation: -20,
                  legend: '요일',
                  legendOffset: 58, 
                  legendPosition: 'middle',
                }}
                axisLeft={{
                  tickSize: 4,
                  tickPadding: 10,
                  legend: '호선',
                  legendOffset: -88,
                  legendPosition: 'middle',
                }}
                colors={{
                  type: 'sequential',
                  scheme: 'blues',
                  minValue: 0,
                }}
                emptyColor="#0e1420"
                borderRadius={3}
                borderWidth={2}
                borderColor="#080c12"
                labelTextColor={{ from: 'color', modifiers: [['brighter', 3]] }}
                annotations={[]}
                onClick={handleCellClick}
                hoverTarget="cell"
                cellHoverOthersOpacity={0.5}
                tooltip={({ cell }) => (
                  <div style={{
                    background: '#141b2d', border: '1px solid #1f2d47',
                    borderRadius: 6, padding: '10px 14px', fontSize: 12, color: '#e8f0fe',
                  }}>
                    <div style={{ fontWeight: 700, marginBottom: 4 }}>
                      {cell.serieId} · {cell.data.x}
                    </div>
                    <div>합계 인원: <strong>{Math.round(cell.value).toLocaleString()}명</strong></div>
                    {cell.data['평균이용객수'] != null && (
                      <div>평균 이용객: {Math.round(cell.data['평균이용객수']).toLocaleString()}명</div>
                    )}
                    {cell.data['심야이용객수'] != null && (
                      <div>심야 이용객: {Math.round(cell.data['심야이용객수']).toLocaleString()}명</div>
                    )}
                    <div style={{ color: '#4a6080', marginTop: 4, fontSize: 10 }}>
                      클릭하여 역별 랭킹 보기
                    </div>
                  </div>
                )}
              />
            )}
          </div>
        </div>

        {/* ── 사이드바 랭킹 ──────────────────────────────── */}
        {sidebar && (
          <div className={styles.sidebar}>
            <div className={styles.sideHeader}>
              <div>
                <span className={styles.sideTitle}>
                  <List size={13} /> 역별 이용객 랭킹
                </span>
                <span className={styles.sideSub}>
                  {sidebar.line} · {sidebar.dayName} · TOP 20
                </span>
              </div>
              <button className={styles.closeBtn} onClick={() => setSidebar(null)}>
                <X size={14} />
              </button>
            </div>

            <div className={styles.modeToggle}>
              {MODES.map(({ value, label, Icon }) => (
                <button
                  key={value}
                  className={`${styles.modeBtn} ${rankMode === value ? styles.modeActive : ''}`}
                  onClick={() => handleModeChange(value)}
                >
                  <Icon size={11} /> {label}
                </button>
              ))}
            </div>

            <div className={styles.rankList} style={{ position: 'relative' }}>
              {rankLoading && <LoadingOverlay message="랭킹 집계 중..." />}
              {!rankLoading && rankData.length === 0 && (
                <div className={styles.empty}>데이터가 없습니다.</div>
              )}
              {!rankLoading && rankData.map((r, i) => {
                const val = r[rankValueKey] ?? 0;
                const pct = rankMax > 0 ? (val / rankMax) * 100 : 0;
                const 구분 = r['구분'];
                return (
                  <div key={`${r['역명']}-${구분}-${i}`} className={styles.rankItem}>
                    <span className={styles.rankNo}>{i + 1}</span>
                    <div className={styles.rankInfo}>
                      <div className={styles.rankName}>
                        {r['역명']}
                        {구분 && <span className={styles.rankTag}>{구분}</span>}
                      </div>
                      <div className={styles.rankBar}>
                        <div className={styles.rankBarFill} style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                    <span className={styles.rankVal}>
                      {Math.round(val).toLocaleString()}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DayBehavior