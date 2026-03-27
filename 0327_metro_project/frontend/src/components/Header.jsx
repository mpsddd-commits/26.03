import { useLocation } from 'react-router-dom';
import { Database, Activity } from 'lucide-react';
import styles from '@styles/Header.module.css';

const PAGE_META = {
  '/yearly':   { title: '연도별 이용객 추이 분석', desc: '2008–2021 서울 지하철 전체 성장 흐름 파악' },
  '/stations': { title: '역별 혼잡도 TOP N',        desc: '인프라 투자 및 안전 배치가 우선시되는 HOT SPOT' },
  '/hourly':   { title: '시간대별 승하차 패턴 분석', desc: '출퇴근 피크 타임 정의 · 주거/업무 지역 특성 분류' },
  '/behavior': { title: '호선별 요일 이용행태',      desc: '평일·주말 이동 목적 차이 · 노선 운영 효율화' },
  '/seasonal': { title: '월별 성수기/비수기 지수',   desc: '성수기 및 비성수기에 대한 연간 최대 이용 월 포착' },
};

const Header = () => {
  const { pathname } = useLocation();
  const meta = PAGE_META[pathname] || { title: 'Seoul Metro Analytics', desc: '서울시 지하철 승하차 데이터 시각화 대시보드' };

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <h1 className={styles.title}>{meta.title}</h1>
        <p className={styles.desc}>{meta.desc}</p>
      </div>
      <div className={styles.right}>
        <div className={styles.badge}>
          <Database size={12} />
          <span>db_metro</span>
        </div>
        <div className={styles.badge}>
          <Activity size={12} />
          <span>LIVE</span>
        </div>
      </div>
    </header>
  );
}

export default Header
