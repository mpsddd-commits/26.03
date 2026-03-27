import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('[API Error]', error?.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ── FEAT-03: 시간대별 승하차 패턴 ──────────────────────────────
export const fetchTimePattern = (year, stationName, dayType) =>
  api.get('/Feat_03/metro_03_1', { params: { year, station_name: stationName, day_type: dayType } });

export const fetchGoldenTime = (year, stationName, dayType) =>
  api.get('/Feat_03/metro_03_2', { params: { year, station_name: stationName, day_type: dayType } });

// ── FEAT-04: 요일별 이용 행태 히트맵 ──────────────────────────────
export const fetchHeatmap = (year, onOff = '전체') =>
  api.get('/Feat_04/metro_04_1', { params: { year, on_off: onOff } });

export const fetchLineCharacteristics = (year, onOff = '전체') =>
  api.get('/Feat_04/metro_04_2', { params: { year, on_off: onOff } });

export const fetchClickRanking = (year, line, dayName, mode = 'total', onOff = '전체') =>
  api.get('/Feat_04/metro_04_3', { params: { year, line, day_name: dayName, mode, on_off: onOff } });

// ── FEAT-05: 성수기및비성수기별 이용 승객수 평균 패턴 ──────────────────────────────
export const fetchSeasonality = ({ year1, year2, month, type }) =>
  api.post('/Feat_05/metro_05_1', { year1, year2, month, type });

export default api;
