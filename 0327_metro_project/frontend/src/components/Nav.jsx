import { NavLink } from 'react-router-dom';
import {
  TrendingUp, BarChart2, Clock, Grid, Calendar, Train
} from 'lucide-react';
import styles from '@styles/Nav.module.css';

const MENU = [
  { path: '/yearly',   label: '연도별 추이',       sub: 'METRO-01', Icon: TrendingUp  },
  { path: '/stations', label: '역별 혼잡도',        sub: 'METRO-02', Icon: BarChart2   },
  { path: '/hourly',   label: '시간대별 패턴',      sub: 'METRO-03', Icon: Clock       },
  { path: '/behavior', label: '요일별 이용행태',    sub: 'METRO-04', Icon: Grid        },
  { path: '/seasonal', label: '월별 성수기 분석',   sub: 'METRO-05', Icon: Calendar    },
];

const Nav = () => {
  return (
    <nav className={styles.nav}>
      <div className={styles.logo}>
        <Train size={20} className={styles.logoIcon} />
        <div>
          <span className={styles.logoMain}>SEOUL</span>
          <span className={styles.logoSub}>METRO ANALYTICS</span>
        </div>
      </div>

      <div className={styles.divider} />

      <ul className={styles.menu}>
        {MENU.map(({ path, label, sub, Icon }) => (
          <li key={path}>
            <NavLink
              to={path}
              className={({ isActive }) =>
                `${styles.item} ${isActive ? styles.active : ''}`
              }
            >
              <Icon size={16} className={styles.icon} />
              <div className={styles.labels}>
                <span className={styles.labelMain}>{label}</span>
                <span className={styles.labelSub}>{sub}</span>
              </div>
              <div className={styles.activeLine} />
            </NavLink>
          </li>
        ))}
      </ul>

      <div className={styles.footer}>
        <span className={styles.footerText}>Seoul Metro Open Data</span>
        <span className={styles.footerText}>2008 – 2021</span>
      </div>
    </nav>
  );
}
export default Nav
