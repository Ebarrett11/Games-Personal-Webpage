CREATE TABLE IF NOT EXISTS `scores` (
`word_id`       int(11)  	      NOT NULL auto_increment	  COMMENT 'the id of this word',
`word`          varchar(10)     NOT NULL                   COMMENT 'word of the day',
`email`         varchar(100)    NOT NULL            		    COMMENT 'the email',
`turns`         int(11)  	      NOT NULL 	                COMMENT '# of turns',
`time`          varchar(100)  	NOT NULL 	                COMMENT 'time, when scored',

PRIMARY KEY (`word_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site user information";