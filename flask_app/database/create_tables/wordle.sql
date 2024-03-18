CREATE TABLE IF NOT EXISTS `wordle` (
`word_id`         int(11)  	   NOT NULL auto_increment	  COMMENT 'the id of this word',
`word`            varchar(10)  NOT NULL                   COMMENT 'word of the day',
PRIMARY KEY (`word_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site user information";