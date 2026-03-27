-- ===================================================================
-- 1. `feat_03` 테이블 생성
-- : 시간대별 승하차 패턴 비교 분석 (METRO-03)
-- ===================================================================
CREATE TABLE db_metro.`feat_03` (
	`연도` INT NULL DEFAULT null,
	`역명` VARCHAR(200) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`역번호` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`구분` VARCHAR(20) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`요일구분` VARCHAR(20) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`시간대` VARCHAR(20) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`평균인원` DECIMAL(15,2) DEFAULT 0,
	`혼잡도지수` DECIMAL(10,2) DEFAULT 0,
	INDEX `search_filter` (`연도`, `역명`, `구분`, `요일구분`)
)
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=INNODB
;


-- ===================================================================
-- 2. `feat_03` 테이블 정제 및 적재
-- ===================================================================

-- [ 1단계 : 가로형 시간대 컬럼을 세로 행으로 변환 (Unpivot) 및 임시 저장 ]

CREATE TABLE db_metro.`unpivot_table` AS
SELECT YEAR(`날짜`) AS 연도, `역명`, `역번호`, `구분`, 
       CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END AS 요일구분,
       '05~06' AS 시간대, IF(`05~06` REGEXP '^[0-9.]+$', CAST(`05~06` AS DECIMAL(15,2)), 0) AS 인원수 FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '06~07', IF(`06~07` REGEXP '^[0-9.]+$', CAST(`06~07` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '07~08', IF(`07~08` REGEXP '^[0-9.]+$', CAST(`07~08` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '08~09', IF(`08~09` REGEXP '^[0-9.]+$', CAST(`08~09` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '09~10', IF(`09~10` REGEXP '^[0-9.]+$', CAST(`09~10` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '10~11', IF(`10~11` REGEXP '^[0-9.]+$', CAST(`10~11` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '11~12', IF(`11~12` REGEXP '^[0-9.]+$', CAST(`11~12` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '12~13', IF(`12~13` REGEXP '^[0-9.]+$', CAST(`12~13` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '13~14', IF(`13~14` REGEXP '^[0-9.]+$', CAST(`13~14` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '14~15', IF(`14~15` REGEXP '^[0-9.]+$', CAST(`14~15` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '15~16', IF(`15~16` REGEXP '^[0-9.]+$', CAST(`15~16` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '16~17', IF(`16~17` REGEXP '^[0-9.]+$', CAST(`16~17` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '17~18', IF(`17~18` REGEXP '^[0-9.]+$', CAST(`17~18` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '18~19', IF(`18~19` REGEXP '^[0-9.]+$', CAST(`18~19` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '19~20', IF(`19~20` REGEXP '^[0-9.]+$', CAST(`19~20` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '20~21', IF(`20~21` REGEXP '^[0-9.]+$', CAST(`20~21` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '21~22', IF(`21~22` REGEXP '^[0-9.]+$', CAST(`21~22` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '22~23', IF(`22~23` REGEXP '^[0-9.]+$', CAST(`22~23` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '23~24', IF(`23~24` REGEXP '^[0-9.]+$', CAST(`23~24` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro UNION ALL
SELECT YEAR(`날짜`), `역명`, `역번호`, `구분`, CASE WHEN `요일` BETWEEN 0 AND 4 THEN '평일' ELSE '주말' END, '24~', IF(`24~` REGEXP '^[0-9.]+$', CAST(`24~` AS DECIMAL(15,2)), 0) FROM db_metro.seoul_metro
;


-- [ 2단계 : 연도/역/구분/시간대별 평균 인원 산출 및 집계 ]
CREATE TABLE db_metro.`avg_table` AS
SELECT
	`연도`, `역명`, `역번호`, `구분`, `요일구분`, `시간대`,
	-- AVG 결과를 소수점 2자리까지 반올림하고 타입을 고정해야 오류 안남
	-- AVG(인원수) AS avg_col <<< 오류 남
	CAST(ROUND(AVG(인원수), 2) AS DECIMAL(15,2)) AS avg_col
FROM db_metro.`unpivot_table`
GROUP BY `연도`, `역명`, `역번호`, `구분`, `요일구분`, `시간대`
;

-- join 최적화를 위한 임시 인덱스
ALTER TABLE db_metro.`avg_table` 
ADD INDEX idx_lookup (연도, 역명, 구분, 요일구분)
;


-- [ 3-1단계 : 혼잡도 지수 계산 및 최종 feat_03 테이블 적재 ]
-- 혼잡도지수 공식 : (특정 시간대 평균 인원  / 전체 시간대 평균 인원) * 100
-- !! 최소인원 기준 없이 적재 !!
INSERT INTO db_metro.`feat_03` (
	`연도`, `역명`, `역번호`, `구분`,
	`요일구분`, `시간대`, `평균인원`, `혼잡도지수`
)
SELECT
	a.`연도`,
	a.`역명`,
	a.`역번호`,
	a.`구분`,
	a.`요일구분`,
	a.`시간대`,
	ROUND(a.avg_col, 2) AS 평균인원,
	-- 공식 적용 : (특정 시간대 평균 / 전체 시간대 평균) * 100
	COALESCE(ROUND((a.avg_col / NULLIF(d.total_avg, 0)) * 100, 2), 0) AS 혼잡도지수
FROM db_metro.`avg_table` AS a
INNER JOIN (
	select
		`연도`, `역명`,`역번호`, `구분`, `요일구분`,
		AVG(avg_col) AS total_avg
	FROM db_metro.`avg_table`
	GROUP BY `연도`, `역명`, `역번호`, `구분`, `요일구분`
) AS d 
ON a.`연도` = d.`연도`
AND a.`역명` = d.`역명`
AND a.`역번호` = d.`역번호`
AND a.`구분` = d.`구분`
AND a.`요일구분` = d.`요일구분`
;


-- [ 3-2단계 : 혼잡도 지수 계산 및 최종 feat_03 테이블 적재 ]
-- 혼잡도지수 공식 : (특정 시간대 평균 인원  / 전체 시간대 평균 인원) * 100
-- !! 최소인원 기준 : 10명 !!
INSERT INTO db_metro.`feat_03` (
	`연도`, `역명`, `역번호`, `구분`,
	`요일구분`, `시간대`, `평균인원`, `혼잡도지수`
)
SELECT
	a.`연도`,
	a.`역명`,
	a.`역번호`,
	a.`구분`,
	a.`요일구분`,
	a.`시간대`,
	ROUND(a.avg_col, 2) AS 평균인원,
	-- 공식 적용 : (특정 시간대 평균 / 전체 시간대 평균) * 100
	COALESCE(ROUND((a.avg_col / NULLIF(d.total_avg, 0)) * 100, 2), 0) AS 혼잡도지수
FROM db_metro.`avg_table` AS a
INNER JOIN (
	-- 전체 평균 계산 시에도 10명 미만 데이터는 제외하여 분모의 왜곡을 방지
	select
		`연도`, `역명`,`역번호`, `구분`, `요일구분`,
		AVG(avg_col) AS total_avg
	FROM db_metro.`avg_table`
	WHERE avg_col >= 10	-- 기준점 설정
	GROUP BY `연도`, `역명`, `역번호`, `구분`, `요일구분`
) AS d 
ON a.`연도` = d.`연도`
AND a.`역명` = d.`역명`
AND a.`역번호` = d.`역번호`
AND a.`구분` = d.`구분`
AND a.`요일구분` = d.`요일구분`
WHERE a.avg_col >= 10
;


-- ===================================================================
-- 3. 검증 SQL문
-- ===================================================================

-- [ 1. `unpivot_table` 검증 ]

-- (1) 원본 행 수 * 20과 `unpivot_table`의 행 수가 일치하는지 확인
SELECT 
    (SELECT COUNT(*) FROM db_metro.seoul_metro) * 20 AS 예상_행수,
    (SELECT COUNT(*) FROM db_metro.unpivot_table) AS 실제_생성_행수
;

-- (2) 서울역(샘플)의 하루치 데이터가 20개 행으로 나오는지 확인
SELECT * FROM db_metro.unpivot_table 
WHERE 역명 = '서울역' 
ORDER BY 연도 DESC, 요일구분, 구분, 시간대 
LIMIT 20
;

-- (3) 인원수가 NULL이거나 0인 데이터의 비율 확인 (데이터 품질 체크)
SELECT 
    COUNT(*) AS 전체행수,
    SUM(CASE WHEN 인원수 = 0 THEN 1 ELSE 0 END) AS 인원수_0인_행수,
    SUM(CASE WHEN 인원수 IS NULL THEN 1 ELSE 0 END) AS 인원수_NULL인_행수
FROM db_metro.unpivot_table
;

-- (4) 모든 시간대('05~06' ~ '24~')가 고르게 들어갔는지 확인
-- 모든 시간대의 cnt 값이 동일해야 정상
SELECT 시간대, COUNT(*) as cnt
FROM db_metro.unpivot_table
GROUP BY 시간대
ORDER BY 시간대
;



-- [ 2. `avg_table` 검증 ]

-- (1) 데이터 소수점 2자리 확인
SELECT * FROM db_metro.`avg_table` 
ORDER BY 연도 DESC, 역명 ASC, 시간대 ASC 
LIMIT 20
;

-- (2) 행 개수 정합성 확인
-- 모든 역이 20개(05시~24시)의 시간대 데이터를 가지고 있는지
-- 환승역 같은 경우 역번호가 호선 별로 다르기때문에 역번호를 꼭 확인해줘야 함
SELECT 역명, 역번호, 연도, 구분, 요일구분, COUNT(*) as 시간대수
FROM db_metro.`avg_table`
GROUP BY 역명, 역번호, 연도, 구분, 요일구분
HAVING COUNT(*) <> 20
;

-- (3) 통계 요약 확인
-- 최대평균 값이 말도 안 되게 크거나(예: 수억 단위), 전체행수가 0이 아닌지 확인
SELECT 
    MIN(avg_col) AS 최소평균, 
    MAX(avg_col) AS 최대평균, 
    AVG(avg_col) AS 전체평균,
    COUNT(*) AS 전체행수
FROM db_metro.`avg_table`
;


-- [ 3. 최종 `feat_03` 검증 ]

-- (1) 전체 행 수 및 기본 통계 확인
-- 전체 데이터 양과 혼잡도지수의 범위
SELECT 
    COUNT(*) AS 전체행수,
    MIN(혼잡도지수) AS 최소_혼잡도,
    MAX(혼잡도지수) AS 최대_혼잡도,
    AVG(혼잡도지수) AS 평균_혼잡도
FROM db_metro.`feat_03`;

-- 환승역 노선별 분리 적재 확인
SELECT 역명, 역번호, 연도, 구분, 요일구분, COUNT(*) AS 시간대수
FROM db_metro.`feat_03`
WHERE 역명 = '가락시장'
GROUP BY 역명, 역번호, 연도, 구분, 요일구분
;

-- (2) 혼잡도지수 계산 논리 검증 (샘플 테스트)
-- 강남역의 특정 연도/요일/구분 데이터 20개 확인
SELECT *, 
       (SELECT AVG(평균인원) 
        FROM db_metro.`feat_03` AS sub 
        WHERE sub.역번호 = main.역번호 AND sub.연도 = main.연도 
          AND sub.구분 = main.구분 AND sub.요일구분 = main.요일구분) AS '해당그룹_전체평균'
FROM db_metro.`feat_03` AS main
WHERE 역명 = '강남' AND 연도 = 2021 AND 요일구분 = '평일' AND 구분 = '승차'
ORDER BY 시간대
;

-- (3) 혼잡도 상위 역 TOP 10 확인
-- 공식에서 분모의 오류가 발생 (분모가 0인 경우)
-- 10명 미만 데이터 제외해서 적재 또는 select시 제외해야 함
SELECT * FROM db_metro.`feat_03`
ORDER BY 혼잡도지수 DESC
LIMIT 10
;

-- (4) 평균 인원이 너무 적어 지수가 튀는 데이터 제외 후 확인
SELECT * FROM db_metro.`feat_03`
WHERE 평균인원 > 5 -- 최소 기준 설정
ORDER BY 혼잡도지수 DESC
LIMIT 10
;

