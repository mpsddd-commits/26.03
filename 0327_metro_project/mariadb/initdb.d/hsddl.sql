-- feat_01 create_table
CREATE TABLE IF NOT EXISTS db_metro.feat_01 (
        id INT AUTO_INCREMENT PRIMARY KEY,

        년도 INT NOT NULL,
        월 INT NOT NULL,

        승차인원합계 BIGINT DEFAULT 0,
        하차인원합계 BIGINT DEFAULT 0,

        생성일 DATETIME DEFAULT CURRENT_TIMESTAMP,

        UNIQUE KEY uq_year_month (년도, 월),
        INDEX idx_year_month (년도, 월)
    );

-- feat_01 insert_table
 INSERT INTO feat_01 (년도, 월, 승차인원합계, 하차인원합계)
    SELECT
        YEAR(날짜) AS 년도,
        MONTH(날짜) AS 월,

        SUM(CASE 
            WHEN 구분 = '승차' THEN
                IFNULL(`05~06`,0)+IFNULL(`06~07`,0)+IFNULL(`07~08`,0)+
                IFNULL(`08~09`,0)+IFNULL(`09~10`,0)+IFNULL(`10~11`,0)+
                IFNULL(`11~12`,0)+IFNULL(`12~13`,0)+IFNULL(`13~14`,0)+
                IFNULL(`14~15`,0)+IFNULL(`15~16`,0)+IFNULL(`16~17`,0)+
                IFNULL(`17~18`,0)+IFNULL(`18~19`,0)+IFNULL(`19~20`,0)+
                IFNULL(`20~21`,0)+IFNULL(`21~22`,0)+IFNULL(`22~23`,0)+
                IFNULL(`23~24`,0)+IFNULL(`24~`,0)
            ELSE 0
        END),

        SUM(CASE 
            WHEN 구분 = '하차' THEN
                IFNULL(`05~06`,0)+IFNULL(`06~07`,0)+IFNULL(`07~08`,0)+
                IFNULL(`08~09`,0)+IFNULL(`09~10`,0)+IFNULL(`10~11`,0)+
                IFNULL(`11~12`,0)+IFNULL(`12~13`,0)+IFNULL(`13~14`,0)+
                IFNULL(`14~15`,0)+IFNULL(`15~16`,0)+IFNULL(`16~17`,0)+
                IFNULL(`17~18`,0)+IFNULL(`18~19`,0)+IFNULL(`19~20`,0)+
                IFNULL(`20~21`,0)+IFNULL(`21~22`,0)+IFNULL(`22~23`,0)+
                IFNULL(`23~24`,0)+IFNULL(`24~`,0)
            ELSE 0
        END)

    FROM db_metro.`seoul_metro`
    GROUP BY YEAR(날짜), MONTH(날짜);

-- feat_01 create_table
CREATE TABLE feat_02 (
    날짜 DATE NOT NULL,
    역명 VARCHAR(200) NOT NULL,
    시간대 VARCHAR(10) NOT NULL,   -- '05~06', '08~09', 'ALL'
    기준 VARCHAR(10) NOT NULL,     -- '승차', '하차'
    인원 INT NOT NULL,
    순위 INT NOT NULL,

    -- 중복 방지 (핵심)
    PRIMARY KEY (날짜, 역명, 시간대, 기준),

    -- 조회 성능 인덱스
    INDEX idx_date (날짜),
    INDEX idx_time (시간대),
    INDEX idx_type (기준),
    INDEX idx_rank (순위),

    -- 복합 조회 최적화 (차트용 핵심)
    INDEX idx_chart (날짜, 시간대, 기준, 순위)

    ) ENGINE=InnoDB
    DEFAULT CHARSET=utf8mb4
    COLLATE=utf8mb4_unicode_ci;

-- feat_02 insert_table

INSERT INTO feat_02 (날짜, 역명, 시간대, 기준, 인원, 순위)

    -- =========================
    -- 1 시간대 TOP50
    -- =========================
    SELECT *
    FROM (
        SELECT
            DATE(t.날짜) AS 날짜,
            m.역명,
        t.시간대,
        t.구분 AS 기준,
        SUM(t.인원) AS 인원,

        ROW_NUMBER() OVER (
            PARTITION BY DATE(t.날짜), t.시간대, t.구분
            ORDER BY SUM(t.인원) DESC
        ) AS 순위

    FROM (
        SELECT 날짜, 역번호, 구분, '05~06' AS 시간대, IFNULL(`05~06`,0) AS 인원 FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '06~07', IFNULL(`06~07`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '07~08', IFNULL(`07~08`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '08~09', IFNULL(`08~09`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '09~10', IFNULL(`09~10`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '10~11', IFNULL(`10~11`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '11~12', IFNULL(`11~12`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '12~13', IFNULL(`12~13`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '13~14', IFNULL(`13~14`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '14~15', IFNULL(`14~15`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '15~16', IFNULL(`15~16`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '16~17', IFNULL(`16~17`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '17~18', IFNULL(`17~18`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '18~19', IFNULL(`18~19`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '19~20', IFNULL(`19~20`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '20~21', IFNULL(`20~21`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '21~22', IFNULL(`21~22`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '22~23', IFNULL(`22~23`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '23~24', IFNULL(`23~24`,0) FROM db_metro.seoul_metro
        UNION ALL
        SELECT 날짜, 역번호, 구분, '24~', IFNULL(`24~`,0) FROM db_metro.seoul_metro
    ) t

    INNER JOIN metro_line m
        ON t.역번호 = m.역번호

        GROUP BY 
            DATE(t.날짜),
            m.역명,
            t.시간대,
            t.구분
    ) time_ranked
    WHERE 순위 <= 50

    UNION ALL

    -- =========================
    -- 2 일일 TOP50 (시간대 = ALL)
    -- =========================
    SELECT *
    FROM (
        SELECT
            DATE(s.날짜) AS 날짜,
            m.역명,
        'ALL' AS 시간대,
        s.구분 AS 기준,

        SUM(
            IFNULL(`05~06`,0)+IFNULL(`06~07`,0)+IFNULL(`07~08`,0)+
            IFNULL(`08~09`,0)+IFNULL(`09~10`,0)+IFNULL(`10~11`,0)+
            IFNULL(`11~12`,0)+IFNULL(`12~13`,0)+IFNULL(`13~14`,0)+
            IFNULL(`14~15`,0)+IFNULL(`15~16`,0)+IFNULL(`16~17`,0)+
            IFNULL(`17~18`,0)+IFNULL(`18~19`,0)+IFNULL(`19~20`,0)+
            IFNULL(`20~21`,0)+IFNULL(`21~22`,0)+IFNULL(`22~23`,0)+
            IFNULL(`23~24`,0)+IFNULL(`24~`,0)
        ) AS 인원,

        ROW_NUMBER() OVER (
            PARTITION BY DATE(s.날짜), s.구분
            ORDER BY SUM(
                IFNULL(`05~06`,0)+IFNULL(`06~07`,0)+IFNULL(`07~08`,0)+
                IFNULL(`08~09`,0)+IFNULL(`09~10`,0)+IFNULL(`10~11`,0)+
                IFNULL(`11~12`,0)+IFNULL(`12~13`,0)+IFNULL(`13~14`,0)+
                IFNULL(`14~15`,0)+IFNULL(`15~16`,0)+IFNULL(`16~17`,0)+
                IFNULL(`17~18`,0)+IFNULL(`18~19`,0)+IFNULL(`19~20`,0)+
                IFNULL(`20~21`,0)+IFNULL(`21~22`,0)+IFNULL(`22~23`,0)+
                IFNULL(`23~24`,0)+IFNULL(`24~`,0)
            ) DESC
        ) AS 순위

    FROM db_metro.seoul_metro s
    INNER JOIN metro_line m
        ON s.역번호 = m.역번호

    GROUP BY 
        DATE(s.날짜),
        m.역명,
        s.구분
) daily_ranked
WHERE 순위 <= 50;