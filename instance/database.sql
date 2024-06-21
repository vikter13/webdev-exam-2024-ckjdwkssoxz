PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE role (
	id INTEGER NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	description TEXT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO role VALUES(1,'Администратор','Полный доступ к системе');
INSERT INTO role VALUES(2,'Модератор','Может редактировать данные книг и производить модерацию рецензий');
INSERT INTO role VALUES(3,'Пользователь','Может оставлять рецензии');
CREATE TABLE cover (
	id INTEGER NOT NULL, 
	filename VARCHAR(200) NOT NULL, 
	mime_type VARCHAR(50) NOT NULL, 
	md5_hash VARCHAR(32) NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO cover VALUES(5,'ups.jpg','image/jpeg','537c890fc7369062c6639dd8e325a297');
INSERT INTO cover VALUES(6,'new-installed-in-the-server.png','image/png','6802660f7b89f6d798c814d859c3c538');
INSERT INTO cover VALUES(7,'was-in-the-server.png','image/png','d0c7962f04b37241c53813dd5e23e246');
INSERT INTO cover VALUES(8,'was-in-the-server2.png','image/png','1a018b31e79f14d1d0cdafd5b09bbab5');
CREATE TABLE genre (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO genre VALUES(1,'Fiction');
INSERT INTO genre VALUES(2,'Science Fiction');
INSERT INTO genre VALUES(3,'Drama');
INSERT INTO genre VALUES(4,'Dystopian');
CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(150) NOT NULL, 
	password_hash VARCHAR(256) NOT NULL, 
	last_name VARCHAR(150) NOT NULL, 
	first_name VARCHAR(150) NOT NULL, 
	middle_name VARCHAR(150), 
	role_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	FOREIGN KEY(role_id) REFERENCES role (id)
);
INSERT INTO user VALUES(0,'justwaste','fasdfas','ddd','d','d',2);
INSERT INTO user VALUES(1,'waste','asdfasdf','asdf','sdf','ds',1);
INSERT INTO user VALUES(2,'wate','asdfasdf','asdf','asdf','sadf',2);
INSERT INTO user VALUES(4,'vikter','scrypt:32768:8:1$loEicwM8URM3HlDn$545a152a19c7f9241d163d7501eeaa745c2a9775fa5b047a16c33cadfe39d383ced7dfc102950d01674c575e9741c638bf6abbebd7ba0c9161aa2c822a4b0e99','tenyaev','victor','middlename',1);
INSERT INTO user VALUES(5,'user','scrypt:32768:8:1$NTOW9wAJadKninYL$338e5ff8156f8323394c4a0833a31b937cdc87229ae9e4ef5515cb95cd9a81fc7aaf7824563ea4f0413ddb1b48e2bf692ddaa7a7299f54c54406c5c8b2b7bcf7','justauser','justauser','middlenameuser',3);
INSERT INTO user VALUES(6,'moderator','scrypt:32768:8:1$maBqAjMxCKu3nDQ5$d5c680a43a98241f82a2615bee04a3c1d121dc2b8a6fdaedc7d0463ef023c3f50d8b47c62d95c5829007eaefe529e1f45847c06c041f0383c81a129a249b8018','justamoderator','justamoderator','middlenamemoderator',2);
INSERT INTO user VALUES(7,'newuser','scrypt:32768:8:1$WaYXAoKIWPbwZmfe$d1072b5f55167748a078f67e41b9e7f27207710f9877d70faeb34bc969137023c5f6ea46800747a1f5b3c1f9d179cc213cd11af73f5662d54eab597bef5a6b17','newuser','newuser','newuser',3);
INSERT INTO user VALUES(8,'admin','scrypt:32768:8:1$yor7SdzNt6e8KJEK$23af5aa20ebb8d652297152d498afeccf838a6cd805233e6c629355f8668331f26a88227834197c9a313df4c68d89cfc1785a658ba17687f44b080aa1807dade','admin','admin','admin',1);
INSERT INTO user VALUES(9,'moderation','scrypt:32768:8:1$Ro0ZNnevKOiefWAY$6a6f26dae89864f812f82e9d9ce69c19fac1f3622a3e1405cc101adb49f05e11dd53f247a3fbc6d3eb2ca5fed7680d48258104fb1880ca297914626472047679','moderation','moderation','moderation',2);
CREATE TABLE book (
	id INTEGER NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	description TEXT NOT NULL, 
	year INTEGER NOT NULL, 
	publisher VARCHAR(200) NOT NULL, 
	author VARCHAR(200) NOT NULL, 
	pages INTEGER NOT NULL, 
	cover_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cover_id) REFERENCES cover (id)
);
INSERT INTO book VALUES(1,'To Kill a Mockingbird','A novel about moral growth and transformation',1960,'Harper & Brothers','Harper Lee',281,1);
INSERT INTO book VALUES(2,'1984','A dystopian novel about the dangers of totalitarianism',2030,'Secker & Warburg','George Orwell',328,2);
INSERT INTO book VALUES(7,'ups eshka','asdf',23,'me','notme',333,5);
INSERT INTO book VALUES(8,'testnew','here is the desc',3000,'me','notme',333,6);
INSERT INTO book VALUES(9,'testold','here is old book',2000,'me','notme',44,7);
INSERT INTO book VALUES(10,'waste1','waste',40,'me','notme',44,8);
INSERT INTO book VALUES(11,'waste2','waste2',49,'me','notme',444,6);
INSERT INTO book VALUES(12,'waste3','dfdf',4999,'menot','notme',5555,7);
INSERT INTO book VALUES(13,'waste4','9999',9999,'heh','future',95,6);
INSERT INTO book VALUES(14,'watexxxxxXX','xxx',101010,'notme','hehe',95,8);
INSERT INTO book VALUES(15,'finaly','a;lsdkf',49494,'wow','wow',4,8);
INSERT INTO book VALUES(16,'notfinally((','what',66,'dsf','fa',44,7);
INSERT INTO book VALUES(17,'nothehealready','a;sldkfj',494,'me','notme',494,6);
INSERT INTO book VALUES(18,'rollback','a;dlskfj',4944,'sldjkf','aldskfj',494,8);
CREATE TABLE book_genre (
	book_id INTEGER NOT NULL, 
	genre_id INTEGER NOT NULL, 
	PRIMARY KEY (book_id, genre_id), 
	FOREIGN KEY(book_id) REFERENCES book (id), 
	FOREIGN KEY(genre_id) REFERENCES genre (id)
);
INSERT INTO book_genre VALUES(1,3);
INSERT INTO book_genre VALUES(2,4);
INSERT INTO book_genre VALUES(2,1);
INSERT INTO book_genre VALUES(2,2);
INSERT INTO book_genre VALUES(2,3);
INSERT INTO book_genre VALUES(7,1);
INSERT INTO book_genre VALUES(8,2);
INSERT INTO book_genre VALUES(8,4);
INSERT INTO book_genre VALUES(9,1);
INSERT INTO book_genre VALUES(9,2);
INSERT INTO book_genre VALUES(10,2);
INSERT INTO book_genre VALUES(10,4);
INSERT INTO book_genre VALUES(11,1);
INSERT INTO book_genre VALUES(12,1);
INSERT INTO book_genre VALUES(13,2);
INSERT INTO book_genre VALUES(14,2);
INSERT INTO book_genre VALUES(15,1);
INSERT INTO book_genre VALUES(16,2);
INSERT INTO book_genre VALUES(16,3);
INSERT INTO book_genre VALUES(17,3);
INSERT INTO book_genre VALUES(18,2);
CREATE TABLE review (
	id INTEGER NOT NULL, 
	book_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	rating INTEGER NOT NULL, 
	text TEXT NOT NULL, 
	date_added DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(book_id) REFERENCES book (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO review VALUES(1,1,1,5,'very interesting book i think!','2024-06-08 10:00:00');
INSERT INTO review VALUES(2,2,2,4,'classic but boring already!','2024-06-08 11:00:00');
INSERT INTO review VALUES(3,1,4,2,'не знаю почему неуд. Я просто не читал эту книгу если честно','2024-06-09 11:08:13.033162');
INSERT INTO review VALUES(4,7,4,5,'ну мне зашло если честно. Классный бесперебойник был так то, жаль сломался и пришлось ставить новый','2024-06-09 11:42:32.198846');
INSERT INTO review VALUES(5,7,5,1,'он сломался поэтму плохой ващето','2024-06-09 11:43:18.146086');
INSERT INTO review VALUES(6,7,6,5,replace('# тест а че с md\n\n**what the...**\n*????*','\n',char(10)),'2024-06-09 12:06:58.106890');
INSERT INTO review VALUES(7,18,4,5,'new review','2024-06-13 12:02:51.265344');
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
COMMIT;
