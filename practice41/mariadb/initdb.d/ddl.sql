use edu;

CREATE TABLE edu.`melon` (
	`no` INT(100) NOT NULL AUTO_INCREMENT COMMENT '번호',
	`id` VARCHAR(20) NOT NULL COMMENT '아이디' COLLATE 'utf8mb4_unicode_ci',
	`code` VARCHAR(30) NOT NULL COMMENT '장르' COLLATE 'utf8mb4_unicode_ci',
	`img` VARCHAR(255) NOT NULL COMMENT '이미지' COLLATE 'utf8mb4_unicode_ci',
	`title` VARCHAR(255) NOT NULL COMMENT '제목' COLLATE 'utf8mb4_unicode_ci',
	`album` VARCHAR(255) NOT NULL COMMENT '엘범명' COLLATE 'utf8mb4_unicode_ci',
	`cnt` INT NOT NULL COMMENT '곡수' DEFAULT '0' ,
	PRIMARY KEY (`no`) 
)
COMMENT='장르별 노래'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB
;