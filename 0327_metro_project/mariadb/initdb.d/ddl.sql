-- DB 생성
CREATE DATABASE db_metro
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_uca1400_ai_ci;

-- 계정 생성
USE db_metro;

CREATE USER 'nyj'@'%' IDENTIFIED BY 'nyj';
CREATE USER 'lhs'@'%' IDENTIFIED BY 'lhs';
CREATE USER 'lnr'@'%' IDENTIFIED BY 'lnr';

GRANT ALL PRIVILEGES ON db_metro.* TO 'nyj'@'%';
GRANT ALL PRIVILEGES ON db_metro.* TO 'lhs'@'%';
GRANT ALL PRIVILEGES ON db_metro.* TO 'lnr'@'%';

COMMIT;

FLUSH PRIVILEGES;

-- seoul_metro TABLE 생성
USE db_metro;
CREATE TABLE `seoul_metro` (
	`날짜` DATE NULL DEFAULT NULL,
	`역번호` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`역명` VARCHAR(200) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`구분` VARCHAR(200) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`05~06` INT(11) NULL DEFAULT NULL,
	`06~07` INT(11) NULL DEFAULT NULL,
	`07~08` INT(11) NULL DEFAULT NULL,
	`08~09` INT(11) NULL DEFAULT NULL,
	`09~10` INT(11) NULL DEFAULT NULL,
	`10~11` INT(11) NULL DEFAULT NULL,
	`11~12` INT(11) NULL DEFAULT NULL,
	`12~13` INT(11) NULL DEFAULT NULL,
	`13~14` INT(11) NULL DEFAULT NULL,
	`14~15` INT(11) NULL DEFAULT NULL,
	`15~16` INT(11) NULL DEFAULT NULL,
	`16~17` INT(11) NULL DEFAULT NULL,
	`17~18` INT(11) NULL DEFAULT NULL,
	`18~19` INT(11) NULL DEFAULT NULL,
	`19~20` INT(11) NULL DEFAULT NULL,
	`20~21` INT(11) NULL DEFAULT NULL,
	`21~22` INT(11) NULL DEFAULT NULL,
	`22~23` INT(11) NULL DEFAULT NULL,
	`23~24` INT(11) NULL DEFAULT NULL,
	`24~` INT(11) NULL DEFAULT NULL,
	`요일` INT(11) NULL DEFAULT NULL,
	INDEX `idx_station` (`역번호`) USING BTREE
)
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=InnoDB
;

-- 파일 적재 시 필수 입력 필요
SET GLOBAL local_infile = 1;


-- 승하차용 오전 오후 및 전체 합계 함수 생성 SQL
USE db_metro;
DELIMITER //

CREATE FUNCTION get_total(
  a VARCHAR(100),
  b VARCHAR(100),
  c VARCHAR(100),
  d VARCHAR(100),
  e VARCHAR(10)
)
RETURNS INT
DETERMINISTIC
BEGIN
  DECLARE result INT;

  SELECT 
    CASE 
      WHEN e = 'AM' THEN
        (
          IFNULL(`05~06`,0) + IFNULL(`06~07`,0) + IFNULL(`07~08`,0) +
          IFNULL(`08~09`,0) + IFNULL(`09~10`,0) + IFNULL(`10~11`,0) +
          IFNULL(`11~12`,0)
        )
      WHEN e = 'PM' THEN
        (
          IFNULL(`12~13`,0) + IFNULL(`13~14`,0) + IFNULL(`14~15`,0) +
          IFNULL(`15~16`,0) + IFNULL(`16~17`,0) + IFNULL(`17~18`,0) +
          IFNULL(`18~19`,0) + IFNULL(`19~20`,0) + IFNULL(`20~21`,0) +
          IFNULL(`21~22`,0) + IFNULL(`22~23`,0) + IFNULL(`23~24`,0) +
          IFNULL(`24~`,0)
        )
      ELSE
        (
          IFNULL(`05~06`,0) + IFNULL(`06~07`,0) + IFNULL(`07~08`,0) +
          IFNULL(`08~09`,0) + IFNULL(`09~10`,0) + IFNULL(`10~11`,0) +
          IFNULL(`11~12`,0) + IFNULL(`12~13`,0) + IFNULL(`13~14`,0) +
          IFNULL(`14~15`,0) + IFNULL(`15~16`,0) + IFNULL(`16~17`,0) +
          IFNULL(`17~18`,0) + IFNULL(`18~19`,0) + IFNULL(`19~20`,0) +
          IFNULL(`20~21`,0) + IFNULL(`21~22`,0) + IFNULL(`22~23`,0) +
          IFNULL(`23~24`,0) + IFNULL(`24~`,0)
        )
    END
  INTO result
  FROM seoul_metro
  WHERE `날짜` COLLATE utf8mb4_unicode_ci = a
    AND `역번호` COLLATE utf8mb4_unicode_ci = b
    AND `역명` COLLATE utf8mb4_unicode_ci = c
    AND `구분` COLLATE utf8mb4_unicode_ci = d
  LIMIT 1;

  RETURN result;
END;
//

DELIMITER ;

-- 요일용 VIEW 테이블 생성
CREATE VIEW `db_metro`.`요일` AS 
select '0' AS `코드`,'월요일' AS `요일` union all 
select '1' AS `코드`,'화요일' AS `요일` union all 
select '2' AS `코드`,'수요일' AS `요일` union all 
select '3' AS `코드`,'목요일' AS `요일` union all 
select '4' AS `코드`,'금요일' AS `요일` union all 
select '5' AS `코드`,'토요일' AS `요일` union all 
select '6' AS `코드`,'일요일' AS `요일`;

-- 서울교통공사 데이터 광장 공공데이터에서 가져오는 호선 데이터용 테이블
CREATE TABLE `db_metro`.`metro_line` (
    `역번호` VARCHAR(50) NOT NULL,
    `호선` VARCHAR(50) NOT NULL,
    `역명` VARCHAR(200) NULL DEFAULT NULL,
    `외부코드` VARCHAR(50) NULL DEFAULT NULL,

    PRIMARY KEY (`역번호`, `호선`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 전체 평균
SELECT AVG(salary) FROM employees; (salary 컬럼의 평균)

-- 조건부 평균
SELECT AVG(price) FROM products WHERE category = 'A';

-- 그룹별 평균
SELECT department, AVG(salary) FROM employees GROUP BY department;

-- 소수점 처리
SELECT ROUND(AVG(score), 2) FROM exams; (평균을 소수점 둘째 자리까지 반올림) 
## 주의사항
-- NULL 처리: AVG() 함수는 NULL 값을 무시합니다. NULL을 0으로 계산하려면 AVG(COALESCE(column, 0)) 또는 CASE 문을 사용해야 합니다.
-- 데이터 타입: 정수형 컬럼의 평균은 일부 DB에서 정수형으로 반환될 수 있으므로, 정확한 소수점 평균을 원하면 형변환(CAST)이 필요할 수 있습니다. 


-- 승하차 별 오전, 오후, 토탈 합계 불러오는 SQL문
SELECT `날짜`, `역번호`, `역명`, 
	get_total(`날짜`, `역번호`, `역명`, '승차','AM') AS AM승차합, 
	get_total(`날짜`, `역번호`, `역명`, '승차','PM') AS FM승차합, 
	get_total(`날짜`, `역번호`, `역명`, '승차','') AS 승차합, 
	get_total(`날짜`, `역번호`, `역명`, '하차','AM') AS AM하차합, 
	get_total(`날짜`, `역번호`, `역명`, '하차','PM') AS FM하차합,
	get_total(`날짜`, `역번호`, `역명`, '하차','') AS 하차합
FROM `db_metro`.`seoul_metro`
where `날짜` = '2008-01-01'
GROUP BY `날짜`, `역번호`, `역명`;


-- metro_line
CREATE INDEX idx_code ON metro_line(역번호);

-- seoul_metro
CREATE INDEX idx_station ON seoul_metro(역번호);

ALTER TABLE metro_line ADD PRIMARY KEY (역번호);
ALTER TABLE metro_line ADD PRIMARY KEY (호선);
