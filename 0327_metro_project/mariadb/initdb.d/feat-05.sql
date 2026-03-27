-- 계절 및 분기 데이터 뷰 테이블 생성
CREATE OR REPLACE TABLE `feat_05` AS
SELECT
  `날짜`, YEAR(`날짜`) AS `연도`, MONTH(`날짜`) AS `월별`,  
	`성수기구분`, `역번호`, `역명`, `구분`,
  `05~06`, `06~07`, `07~08`, `08~09`, `09~10`, `10~11`, `11~12`,
	`12~13`, `13~14`, `14~15`, `15~16`, `16~17`, `17~18`, `18~19`,
	`19~20`, `20~21`, `21~22`, `22~23`, `23~24`, `24~`,
	QUARTER(`날짜`) AS `분기`,
  CONCAT(YEAR(`날짜`), '년 ', QUARTER(`날짜`), '분기') AS `년도분기`,
  CASE
    WHEN MONTH(`날짜`) IN (3,4,5) THEN '봄'
    WHEN MONTH(`날짜`) IN (6,7,8) THEN '여름'
    WHEN MONTH(`날짜`) IN (9,10,11) THEN '가을'
    ELSE '겨울'
  END AS `계절`,
  `요일`,
  (
    IFNULL(`05~06`,0) + IFNULL(`06~07`,0) + IFNULL(`07~08`,0) +
    IFNULL(`08~09`,0) + IFNULL(`09~10`,0) + IFNULL(`10~11`,0) +
    IFNULL(`11~12`,0)
  ) AS `AM`,
  (
    IFNULL(`12~13`,0) + IFNULL(`13~14`,0) + IFNULL(`14~15`,0) +
    IFNULL(`15~16`,0) + IFNULL(`16~17`,0) + IFNULL(`17~18`,0) +
    IFNULL(`18~19`,0) + IFNULL(`19~20`,0) + IFNULL(`20~21`,0) +
    IFNULL(`21~22`,0) + IFNULL(`22~23`,0) + IFNULL(`23~24`,0) +
    IFNULL(`24~`,0)
  ) AS `PM`,
  (
    IFNULL(`05~06`,0) + IFNULL(`06~07`,0) + IFNULL(`07~08`,0) +
    IFNULL(`08~09`,0) + IFNULL(`09~10`,0) + IFNULL(`10~11`,0) +
    IFNULL(`11~12`,0) + IFNULL(`12~13`,0) + IFNULL(`13~14`,0) + 
    IFNULL(`14~15`,0) + IFNULL(`15~16`,0) + IFNULL(`16~17`,0) + 
    IFNULL(`17~18`,0) + IFNULL(`18~19`,0) + IFNULL(`19~20`,0) + 
    IFNULL(`20~21`,0) + IFNULL(`21~22`,0) + IFNULL(`22~23`,0) + 
    IFNULL(`23~24`,0) + IFNULL(`24~`,0)
  ) AS `총 이용객 수`
FROM `seoul_metro`;

-- feat_05
CREATE INDEX idx_station ON `feat_05`(`역번호`);


-- 성수기 구분 추가
ALTER TABLE `feat_05`
ADD COLUMN `성수기구분` VARCHAR(10);

-- 역별 + 연도별 기준으로 성수기 구분 데이터 추가
UPDATE `feat_05` f
JOIN (
  SELECT `역번호`, YEAR(`날짜`) AS y, AVG(`총 이용객 수`) AS avg_total
  FROM `feat_05`
  GROUP BY `역번호`, YEAR(`날짜`)
) a
ON f.`역번호` = a.`역번호`
AND YEAR(f.`날짜`) = a.y
SET f.`성수기구분` =
  CASE
    WHEN f.`총 이용객 수` >= a.avg_total THEN '성수기'
    ELSE '비성수기'
  END;

-- 성수기 구분 인덱스 생성
CREATE INDEX idx_peak ON `feat_05`(`성수기구분`);

-- 총 이용객 수 인덱스 생성
CREATE INDEX idx_visitors ON `feat_05`(`총 이용객 수`);

-- 연도 추가
ALTER TABLE feat_05 ADD COLUMN `연도` INT;

-- 연도 데이터 추가
UPDATE feat_05 SET `연도` = YEAR(`날짜`);

-- 성수기 비성수기용 인덱스 생성
CREATE INDEX idx_seasonality ON `feat_05`(`연도`, `성수기구분`, `역명`);

-- 월별 추가
ALTER TABLE feat_05 ADD COLUMN `월별` INT;

-- 월별 데이터 추가
UPDATE feat_05 SET `월별` = MONTH(`날짜`);


-- 계절 및 승하차별 변동성
SELECT
	sq.`날짜`, d.`요일`, sq.`구분`,
	SUM(sq.`05~06`) AS `05~06`, SUM(sq.`06~07`) AS `06~07`, 
	SUM(sq.`07~08`) AS `07~08`, SUM(sq.`08~09`) AS `08~09`, 
	SUM(sq.`09~10`) AS `09~10`, SUM(sq.`10~11`) AS `10~11`, 
	SUM(sq.`11~12`) AS `11~12`, SUM(sq.`12~13`) AS `12~13`, 
	SUM(sq.`13~14`) AS `13~14`, SUM(sq.`14~15`) AS `14~15`, 
	SUM(sq.`15~16`) AS `15~16`, SUM(sq.`16~17`) AS `16~17`, 
	SUM(sq.`17~18`) AS `17~18`, SUM(sq.`18~19`) AS `18~19`, 
	SUM(sq.`19~20`) AS `19~20`, SUM(sq.`20~21`) AS `20~21`, 
	SUM(sq.`21~22`) AS `21~22`, SUM(sq.`22~23`) AS `22~23`, 
	SUM(sq.`23~24`) AS `23~24`, SUM(sq.`24~`) AS `24~`
FROM `feat_05` AS sq
LEFT JOIN `요일` AS d
	ON sq.`요일` = d.`코드`
LEFT JOIN `metro_line` AS ml
	ON sq.`역번호` = ml.`역번호`
WHERE YEAR(`날짜`) = 2008
  AND `계절` = '봄'
GROUP BY sq.`날짜`, d.`요일`, sq.`구분`;

-- 순수 계절 및 년도별 변동성
SELECT
	YEAR(`날짜`) AS `년도`,
	SUM(sq.`05~06`) AS `05~06`, SUM(sq.`06~07`) AS `06~07`, 
	SUM(sq.`07~08`) AS `07~08`, SUM(sq.`08~09`) AS `08~09`, 
	SUM(sq.`09~10`) AS `09~10`, SUM(sq.`10~11`) AS `10~11`, 
	SUM(sq.`11~12`) AS `11~12`, SUM(sq.`12~13`) AS `12~13`, 
	SUM(sq.`13~14`) AS `13~14`, SUM(sq.`14~15`) AS `14~15`, 
	SUM(sq.`15~16`) AS `15~16`, SUM(sq.`16~17`) AS `16~17`, 
	SUM(sq.`17~18`) AS `17~18`, SUM(sq.`18~19`) AS `18~19`, 
	SUM(sq.`19~20`) AS `19~20`, SUM(sq.`20~21`) AS `20~21`, 
	SUM(sq.`21~22`) AS `21~22`, SUM(sq.`22~23`) AS `22~23`, 
	SUM(sq.`23~24`) AS `23~24`, SUM(sq.`24~`) AS `24~`
FROM `feat_05` AS sq
LEFT JOIN `요일` AS d
	ON sq.`요일` = d.`코드`
LEFT JOIN `metro_line` AS ml
	ON sq.`역번호` = ml.`역번호`	
WHERE YEAR(`날짜`) = 2020
  AND `계절` = '겨울'
GROUP BY `년도`;

-- 계절 및 년월별 변동성
SELECT
	YEAR(`날짜`) AS `년도`, MONTH(sq.`날짜`) AS `월`,
	SUM(sq.`05~06`) AS `05~06`, SUM(sq.`06~07`) AS `06~07`, 
	SUM(sq.`07~08`) AS `07~08`, SUM(sq.`08~09`) AS `08~09`, 
	SUM(sq.`09~10`) AS `09~10`, SUM(sq.`10~11`) AS `10~11`, 
	SUM(sq.`11~12`) AS `11~12`, SUM(sq.`12~13`) AS `12~13`, 
	SUM(sq.`13~14`) AS `13~14`, SUM(sq.`14~15`) AS `14~15`, 
	SUM(sq.`15~16`) AS `15~16`, SUM(sq.`16~17`) AS `16~17`, 
	SUM(sq.`17~18`) AS `17~18`, SUM(sq.`18~19`) AS `18~19`, 
	SUM(sq.`19~20`) AS `19~20`, SUM(sq.`20~21`) AS `20~21`, 
	SUM(sq.`21~22`) AS `21~22`, SUM(sq.`22~23`) AS `22~23`, 
	SUM(sq.`23~24`) AS `23~24`, SUM(sq.`24~`) AS `24~`
FROM `feat_05` AS sq
LEFT JOIN `요일` AS d
	ON sq.`요일` = d.`코드`
LEFT JOIN `metro_line` AS ml
	ON sq.`역번호` = ml.`역번호`	
WHERE YEAR(`날짜`) = 2020
  AND `계절` = '겨울'
GROUP BY `년도`, `월`;

-- 계절 및 일별 변동성
SELECT
	`날짜`,
	SUM(sq.`05~06`) AS `05~06`, SUM(sq.`06~07`) AS `06~07`, 
	SUM(sq.`07~08`) AS `07~08`, SUM(sq.`08~09`) AS `08~09`, 
	SUM(sq.`09~10`) AS `09~10`, SUM(sq.`10~11`) AS `10~11`, 
	SUM(sq.`11~12`) AS `11~12`, SUM(sq.`12~13`) AS `12~13`, 
	SUM(sq.`13~14`) AS `13~14`, SUM(sq.`14~15`) AS `14~15`, 
	SUM(sq.`15~16`) AS `15~16`, SUM(sq.`16~17`) AS `16~17`, 
	SUM(sq.`17~18`) AS `17~18`, SUM(sq.`18~19`) AS `18~19`, 
	SUM(sq.`19~20`) AS `19~20`, SUM(sq.`20~21`) AS `20~21`, 
	SUM(sq.`21~22`) AS `21~22`, SUM(sq.`22~23`) AS `22~23`, 
	SUM(sq.`23~24`) AS `23~24`, SUM(sq.`24~`) AS `24~`
FROM `feat_05` AS sq
LEFT JOIN `요일` AS d
	ON sq.`요일` = d.`코드`
LEFT JOIN `metro_line` AS ml
	ON sq.`역번호` = ml.`역번호`	
WHERE YEAR(`날짜`) = 2020
  AND `계절` = '겨울'
GROUP BY `날짜`;


-- 월 및 승하차별 변동성
SELECT
	sq.`날짜`, d.`요일`, sq.`구분`,
	SUM(sq.`05~06`) AS `05~06`, SUM(sq.`06~07`) AS `06~07`, 
	SUM(sq.`07~08`) AS `07~08`, SUM(sq.`08~09`) AS `08~09`, 
	SUM(sq.`09~10`) AS `09~10`, SUM(sq.`10~11`) AS `10~11`, 
	SUM(sq.`11~12`) AS `11~12`, SUM(sq.`12~13`) AS `12~13`, 
	SUM(sq.`13~14`) AS `13~14`, SUM(sq.`14~15`) AS `14~15`, 
	SUM(sq.`15~16`) AS `15~16`, SUM(sq.`16~17`) AS `16~17`, 
	SUM(sq.`17~18`) AS `17~18`, SUM(sq.`18~19`) AS `18~19`, 
	SUM(sq.`19~20`) AS `19~20`, SUM(sq.`20~21`) AS `20~21`, 
	SUM(sq.`21~22`) AS `21~22`, SUM(sq.`22~23`) AS `22~23`, 
	SUM(sq.`23~24`) AS `23~24`, SUM(sq.`24~`) AS `24~`
FROM `feat_05` AS sq
LEFT JOIN `요일` AS d
	ON sq.`요일` = d.`코드`
LEFT JOIN `metro_line` AS ml
	ON sq.`역번호` = ml.`역번호`
WHERE YEAR(`날짜`) = 2008
  AND MONTH(`날짜`) = 05
GROUP BY sq.`날짜`, d.`요일`, sq.`구분`;

-- 월별 변동성
SELECT
	sq.`날짜`, d.`요일`,
	SUM(sq.`05~06`) AS `05~06`, SUM(sq.`06~07`) AS `06~07`, 
	SUM(sq.`07~08`) AS `07~08`, SUM(sq.`08~09`) AS `08~09`, 
	SUM(sq.`09~10`) AS `09~10`, SUM(sq.`10~11`) AS `10~11`, 
	SUM(sq.`11~12`) AS `11~12`, SUM(sq.`12~13`) AS `12~13`, 
	SUM(sq.`13~14`) AS `13~14`, SUM(sq.`14~15`) AS `14~15`, 
	SUM(sq.`15~16`) AS `15~16`, SUM(sq.`16~17`) AS `16~17`, 
	SUM(sq.`17~18`) AS `17~18`, SUM(sq.`18~19`) AS `18~19`, 
	SUM(sq.`19~20`) AS `19~20`, SUM(sq.`20~21`) AS `20~21`, 
	SUM(sq.`21~22`) AS `21~22`, SUM(sq.`22~23`) AS `22~23`, 
	SUM(sq.`23~24`) AS `23~24`, SUM(sq.`24~`) AS `24~`
FROM `feat_05` AS sq
LEFT JOIN `요일` AS d
	ON sq.`요일` = d.`코드`
LEFT JOIN `metro_line` AS ml
	ON sq.`역번호` = ml.`역번호`
WHERE YEAR(`날짜`) = 2008
  AND MONTH(`날짜`) = 05
GROUP BY sq.`날짜`, d.`요일`;



-- 계절 및 분기 데이터 뷰 테이블 생성 검증용 SQL

-- 1. 합계 산식 검증 (AM + PM = 총 이용객 수) AM과 PM의 합이 총 이용객 수와 일치하는지 확인
SELECT 
	COUNT(*) AS `total_rows`,
	SUM(CASE WHEN (`AM` + `PM`) = `총 이용객 수` THEN 1 ELSE 0 END) AS `match_count`,
	SUM(CASE WHEN (`AM` + `PM`) != `총 이용객 수` THEN 1 ELSE 0 END) AS `mismatch_count`
FROM `feat_05`;

-- 2. 계산된 컬럼의 Null값 및 범위 체크
-- IFNULL 처리를 하셨지만, 결과값인 AM, PM, 총 이용객 수가 음수이거나 비정상적으로 0인 경우가 있는지 확인
SELECT 
	MIN(`AM`) AS `min_am`, 
	MAX(`AM`) AS `max_am`,
	MIN(`PM`) AS `min_pm`, 
	MAX(`PM`) AS `max_pm`,
	-- COUNTIF(`총 이용객 수` IS NULL) AS null_total_count,
	-- COUNTIF(`총 이용객 수` = 0) AS zero_total_count
	SUM(CASE WHEN `총 이용객 수` IS NULL THEN 1 ELSE 0 END) AS `null_total_count`,
	SUM(CASE WHEN `총 이용객 수` = 0 THEN 1 ELSE 0 END) AS `zero_total_count`
FROM `feat_05`;

-- 3. 계절 및 분기 매핑 논리 검증
-- MONTH 함수와 QUARTER 함수가 의도한 대로 매핑되었는지 샘플링하여 확인
SELECT 
	DISTINCT EXTRACT(MONTH FROM `날짜`) AS month,
	`분기`,
	`계절`,
	COUNT(*) AS `row_count`
FROM `feat_05`
GROUP BY 1, 2, 3
ORDER BY 1;


-- 4. 원본 데이터와의 레코드 수 비교
-- CREATE TABLE 과정에서 데이터가 유실되지는 않았는지 원본 테이블(seoul_metro)과 대조

SELECT 
	(SELECT COUNT(*) FROM `seoul_metro`) AS `raw_count`,
	(SELECT COUNT(*) FROM `feat_05`) AS `feature_count`,
	(SELECT COUNT(*) FROM `seoul_metro`) - (SELECT COUNT(*) FROM `feat_05`) AS `difference`;

-- 5. 만약 특정 행에서 합계가 맞지 않는다면 아래 쿼리를 통해 어떤 데이터가 문제인지 직접 식별

SELECT `날짜`, `역명`, `AM`, `PM`, `총 이용객 수`
FROM `feat_05`
WHERE (`AM` + `PM`) != `총 이용객 수`
LIMIT 10;

-- 2008년 봄 시즌의 날짜/요일/구분별 이용객 합계
-- A. 조인 누락 확인 (데이터 유실 체크)
SELECT 
	SUM(CASE WHEN d.`요일` IS NULL THEN 1 ELSE 0 END) AS `missing_day_name`,
	SUM(CASE WHEN ml.`역번호` IS NULL THEN 1 ELSE 0 END) AS `missing_line_info`
FROM `feat_05` AS sq
LEFT JOIN `요일` AS d ON sq.`요일` = d.`코드`
LEFT JOIN `metro_line` AS ml ON sq.`역번호` = ml.`역번호`
WHERE YEAR(`날짜`) = 2008 AND `계절` = '봄';

-- B. 중복 집계 확인
-- 원본 feat_05의 총합과 조인 후 총합 비교
SELECT 
	(SELECT SUM(`총 이용객 수`) FROM feat_05 WHERE YEAR(`날짜`) = 2008 AND `계절` = '봄') AS `original_sum`,
	SUM(sq.`총 이용객 수`) AS `joined_sum`
FROM `feat_05` AS sq
LEFT JOIN `metro_line` AS ml ON sq.`역번호` = ml.`역번호`
WHERE YEAR(`날짜`) = 2008 AND `계절` = '봄';



# ---------------------------------------------------------------------
# 1. 월별 (month 없음)
# ---------------------------------------------------------------------

if month is None:

SELECT
	`월별`,
	SUM(`총 이용객 수`) AS `총 이용객 수`
FROM feat_05
WHERE `연도` = {year1}
{type_filter}
GROUP BY `월별`

SELECT
	`월별`,
	SUM(`총 이용객 수`) AS `총 이용객 수`
FROM feat_05
WHERE `연도` = {year2}
{type_filter}
GROUP BY `월별`

# ---------------------------------------------------------------------
# 2. 역별 (month 있음)
# ---------------------------------------------------------------------
else:

SELECT
	`역명`,
	SUM(`총 이용객 수`) AS `총 이용객 수`
FROM feat_05
WHERE `연도` = {year1}
AND `월별` = {month}
{type_filter}
GROUP BY `역명`

SELECT
	`역명`,
	SUM(`총 이용객 수`) AS `총 이용객 수`
FROM feat_05
WHERE `연도` = {year2}
AND `월별` = {month}
{type_filter}
GROUP BY `역명`


-- 최종으로 사용한 쿼리

---------------------------------------------------------------------
-- 1. 월별 조회 (메인 차트: 기본 막대 + 증감률 선)
---------------------------------------------------------------------
   
-- [A] 대상 연도(year1) 월별+역별 데이터 (기본 막대)
-- 데이터 양 조절을 위해 이용객 수 상위 역 10개만 예시로 사용 (필요시 조정)
SELECT `월별`, `역명`, SUM(`총 이용객 수`) as cnt
FROM feat_05
WHERE `연도` = {year1} {type_filter}
GROUP BY `월별`, `역명`

-- [B] 비교 연도(year2) 월별 총합 (전체 증감률 계산용) 
-- 추가 데이터 가공은 .py 참조

SELECT `월별`, SUM(`총 이용객 수`) as total_cnt
FROM feat_05
WHERE `연도` = {year2} {type_filter}
GROUP BY `월별`
      

---------------------------------------------------------------------
-- 2. 역별 조회 (클릭 시 하위 차트: 기본 막대)
---------------------------------------------------------------------
SELECT `역명` as station, SUM(`총 이용객 수`) as value
FROM feat_05
WHERE `연도` = {year1} 
	AND `월별` = {month} {type_filter}
GROUP BY `역명`
ORDER BY value DESC
LIMIT 20