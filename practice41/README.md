## Mariadb 구성하기

- Docker 볼륨 생성
```bash
docker volume create data-mariadb
```

- Docker Container 생성
```bash
docker run -d -p 3306:3306 -v data-mariadb:/var/lib/mysql -e MARIADB_ROOT_PASSWORD=1234 -e MARIADB_DATABASE=edu -e TZ=Asia/Seoul -e LC_ALL=en_US.UTF-8 --name mariadb mariadb:12.1.2
```

- Database Table 생성
```sql
CREATE TABLE `melon` (
	`id` 			INT 				  NOT NULL,
	`img` 		VARCHAR(255)	NULL,
	`title`		VARCHAR(100)	NOT NULL,
	`album`		VARCHAR(100)	NOT NULL,
	`cnt`			INT				    NOT NULL,
	`regDate`	DATETIME 		  NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`modDate`	DATETIME			NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

- Table Insert문
```python
sql = f"""
    INSERT INTO edu.`melon` 
    (`id`, `img`, `title`, `album`, `cnt`)
    VALUE
    ('{id}', '{img}', '{title}', '{album}', {cnt});
"""
```

- 장르 코드명
```sql
CREATE VIEW edu.`category` AS
SELECT 'GN0100' AS `code`, '발라드' AS `name`
UNION ALL
SELECT 'GN0200' AS `code`, '댄스' AS `name`
UNION ALL
SELECT 'GN0300' AS `code`, '랩/힙합' AS `name`
UNION ALL
SELECT 'GN0400' AS `code`, 'R&B/Soul' AS `name`
UNION ALL
SELECT 'GN0500' AS `code`, '인디음악' AS `name`
UNION ALL
SELECT 'GN0600' AS `code`, '록/메탈' AS `name`
UNION ALL
SELECT 'GN0700' AS `code`, '트로트' AS `name`
UNION ALL
SELECT 'GN0800' AS `code`, '포크/블루스' AS `name`;
```
