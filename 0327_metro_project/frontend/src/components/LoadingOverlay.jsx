import styles from '@styles/LoadingOverlay.module.css';

const LoadingOverlay = ({ message = '데이터 로딩 중...' }) => {
  return (
    <div className={styles.overlay}>
      <div className={styles.spinner} />
      <p className={styles.msg}>{message}</p>
    </div>
  );
}

export default LoadingOverlay

