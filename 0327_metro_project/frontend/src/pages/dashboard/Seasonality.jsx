import { useState, useEffect } from 'react'
import { ResponsiveBar } from '@nivo/bar'
// Line 계산 로직 (설치 필요: npm install d3-shape)
import { line } from 'd3-shape' 
import { fetchSeasonality } from '@utils/network'
import LoadingOverlay from '@components/LoadingOverlay'
import styles from '@styles/Seasonality.module.css' 

const Seasonality = () => {
  const [year1, setYear1] = useState(2021); // 대상연도
  const [year2, setYear2] = useState(2020); // 비교연도
  const [type, setType] = useState("전체");
  const [selectedMonth, setSelectedMonth] = useState(null);
  
  const [mainData, setMainData] = useState([]); 
  const [subData, setSubData] = useState([]); 
  const [loading, setLoading] = useState(false);

  // 연도 배열 생성 (2008 ~ 2021)
  const allYears = Array.from({ length: 2021 - 2008 + 1 }, (_, i) => 2008 + i).reverse();

  // 데이터 조회
  const fetchMainData = () => {
    setLoading(true);
    setSelectedMonth(null); // 조회 시 상세 보기 초기화
    fetchSeasonality({ year1, year2, type })
      .then(res => {
        // 백엔드 반환 데이터 구조에 맞게 매핑 (res.monthly: [{월: '1월', total: 100, growth_rate: 5.5}, ...])
        if (res.status) setMainData(res.monthly || []);
        else setMainData([]);
      })
      .catch(() => setMainData([]))
      .finally(() => setLoading(false));
  };

  // 컴포넌트 마운트 시 초기 데이터 조회
  useEffect(() => { fetchMainData(); }, []);

  // 대상연도(year1) 변경 시 호출
  const handleYear1Change = (e) => {
    const val = Number(e.target.value);
    setYear1(val);
    // 만약 대상연도와 비교연도가 같아지면 비교연도를 다른 값으로 자동 조정
    if (val === year2) {
      const nextAvailable = allYears.find(y => y !== val);
      setYear2(nextAvailable);
    }
  };

  // 막대 클릭 시 해당 월의 상세 역별 데이터 조회
  const handleBarClick = (bar) => {
    const monthStr = bar.indexValue;
    if(!monthStr) return;
    const monthNum = parseInt(monthStr.replace('월', ''));
    
    setSelectedMonth(monthNum);
    setLoading(true);
    
    fetchSeasonality({ year1, year2, month: monthNum, type })
      .then(res => {
        if (res.status) setSubData(res.stations || []);
        else setSubData([]);
      })
      .catch(() => setSubData([]))
      .finally(() => setLoading(false));
  };

  // =========================================================
  // 수정된 커스텀 레이어: 증감률 꺾은선 (Line & Point)
  // 막대 Y축 스케일을 기반으로 보정된 Y좌표 계산
  // =========================================================
  const LineAndPointLayer = ({ bars, innerHeight, yScale }) => {
    if (!bars || bars.length === 0) return null;

    // y축 데이터의 최대값 확인 (이용객 수 기준)
    const yDomainMax = yScale.domain()[1];

    const points = bars.map(bar => {
      const { data } = bar; 
      const x = bar.x + bar.width / 2;
      
      // 증감률 데이터 (%)
      const rate = data.data.growth_rate || 0;
      
      // 새로운 Y좌표 계산 로직: 
      // 막대의 중간 지점(0%)을 기준으로 증감률 비율만큼 yScale 상에서 이동
      const barCenterY = bar.y + bar.height / 2;
      
      // 증감률 1%당 전체 yScale 최대값의 1%만큼 이동하는 보정치 계산 (가시성 확보)
      // 예: 증감률이 +10%면, yScale 상에서 최대값의 10%에 해당하는 높이만큼 위로(-) 이동
      const offset = (rate / 100) * (yScale(0) - yScale(yDomainMax));
      
      // y 좌표 확정 (막대 중간 좌표 - 보정치)
      const y = barCenterY - offset;

      return { x, y, rate, label: data.indexValue };
    });

    const lineGenerator = line().x(d => d.x).y(d => d.y);

    return (
      <g>
        <path d={lineGenerator(points)} className={styles.chartLine} />
        {points.map((point, index) => (
          <circle
            key={index}
            cx={point.x}
            cy={point.y}
            r={5}
            className={styles.chartPoint}
          >
            <title>{`${point.label}: 증감률 ${point.rate}%`}</title>
          </circle>
        ))}
      </g>
    );
  };

  return (
    <div className={styles.page}>
      
      {/* 필터 영역 */}
      <div className={styles.filterGroup}>
        <div className={styles.filterItem}>
          <label>대상연도</label>
          <select value={year1} onChange={handleYear1Change}>
            {allYears.map(y => <option key={y} value={y}>{y}년</option>)}
          </select>
        </div>
        <div className={styles.filterItem}>
          <label>비교연도</label>
          <select value={year2} onChange={e => setYear2(Number(e.target.value))}>
            {/* 핵심: 대상연도(year1)에서 선택한 값은 제외하고 렌더링 */}
            {allYears.filter(y => y !== year1).map(y => (
              <option key={y} value={y}>{y}년</option>
            ))}
          </select>
        </div>
        <div className={styles.filterItem}>
          <label>구분</label>
          <select value={type} onChange={e => setType(e.target.value)}>
            <option value="전체">전체</option>
            <option value="성수기">성수기</option>
            <option value="비성수기">비성수기</option>
          </select>
        </div>
        <button className={styles.searchBtn} onClick={fetchMainData} disabled={loading}>
          {loading ? '조회 중...' : '데이터 조회'}
        </button>
      </div>

      {/* 차트 영역 */}
      <div className={styles.chartContainer}>
        {loading && <LoadingOverlay />}

        {!selectedMonth ? (
          // [메인] 월별 기본 막대 + 증감률 선
          mainData.length > 0 ? (
            <ResponsiveBar
              data={mainData}
              keys={['total']} // 막대차트 데이터 키
              indexBy="월"
              // 왼쪽 여백을 180으로 설정하여 큰 숫자가 짤리는 것 방지
              margin={{ top: 50, right: 50, bottom: 60, left: 180 }}
              padding={0.4}
              // 그라데이션 대신 기존의 밝은 하늘색 단색 적용
              colors={['#4da3ff']} 
              axisLeft={{ 
                legend: '총 이용객 수', 
                legendOffset: -140, // 마진 확대에 따른 범례 위치 조정
                format: v => v.toLocaleString()
              }}
              // 막대 위 라벨 숨김 (이미지처럼 숫자 길게 나오는 것 방지)
              enableLabel={false} 
              onClick={handleBarClick} // 클릭 이벤트
              
              // 레이어 순서 정의 (맨 뒤에 커스텀 선 레이어 추가)
              layers={['grid', 'axes', 'bars', LineAndPointLayer]}
              
              // 툴팁 설정
              tooltip={({ data }) => (
                <div className={styles.customTooltip}>
                  <div className={styles.tooltipTitle}>{data.월} 이용 현황</div>
                  <div>이용객: <strong>{data.total.toLocaleString()}명</strong></div>
                  <div>비교연도 대비 증감률: <strong className={data.growth_rate > 0 ? styles.growthPositive : styles.growthNegative}>
                    {data.growth_rate}%
                  </strong></div>
                  <div style={{ marginTop: '5px', fontSize: '10px', color: '#888' }}>(클릭 시 역별 상세 보기)</div>
                </div>
              )}
              
              // 테마 설정 (텍스트 색상 다크 테마 가시성 확보)
              theme={{
                axis: {
                  ticks: { text: { fill: "#8fa3c4", fontSize: 12, fontWeight: 500 } },
                  legend: { text: { fill: "#8fa3c4", fontSize: 14, fontWeight: 600 } }
                },
                grid: { line: { stroke: "#1f2d47" } }
              }}
            />
          ) : !loading && <div className={styles.placeholder}>데이터를 조회해주세요.</div>
        ) : (
          // [상세] 역별 상세 막대 차트
          <div className={styles.subChartWrapper}>
            <div className={styles.subChartHeader}>
              <h3 className={styles.subChartTitle}>{year1}년 {selectedMonth}월 역별 상세 (TOP 20)</h3>
              <button className={styles.backBtn} onClick={() => setSelectedMonth(null)}>← 돌아가기</button>
            </div>
            <div className={styles.subChartArea} style={{ height: '500px' }}> {/* 높이 강제 확보 */}
              {subData.length > 0 ? (
                <ResponsiveBar
                  data={subData}
                  keys={['value']}
                  indexBy="station"
                  margin={{ top: 20, right: 30, bottom: 100, left: 180 }}
                  padding={0.3}
                  colors={['#4da3ff']} // 막대 색상 통일
                  axisBottom={{ tickRotation: -45 }} // 역명 회전
                  axisLeft={{ 
                    format: v => v.toLocaleString(),
                    legend: '이용객 수',
                    legendOffset: -140
                  }}

                  // 툴팁 설정
                  tooltip={({ data }) => (
                    <div className={styles.customTooltip2}>
                      <div className={styles.tooltipTitle2}>
                        <strong>{data.station}역 이용 현황</strong>
                      </div>
                      <div>이용객: <strong>{data.value.toLocaleString()}명</strong></div>
                    </div>
                  )}
                  theme={{
                    axis: {
                      ticks: { text: { fill: "#8fa3c4", fontSize: 11 } },
                      legend: { text: { fill: "#8fa3c4" } }
                    },
                    grid: { line: { stroke: "#1f2d47" } }
                  }}
                  
                />
              ) : !loading && <div>해당 월의 상세 데이터가 없습니다.</div>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Seasonality;