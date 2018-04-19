
use emarosti_db;

DROP TABLE if exists user;
CREATE TABLE user(
    email varchar(50) PRIMARY KEY NOT NULL,
    name varchar(50) NOT NULL,
    role enum('student', 'client', 'administrator') NOT NULL
);


DROP TABLE if exists password;
CREATE TABLE password(
	email varchar(50) NOT NULL,
	hashed varchar(100) NOT NULL,
	INDEX (email),
	foreign key (email) on delete cascade
);

DROP TABLE if exists project;
CREATE TABLE project(
	pid int not null AUTO_INCREMENT,
	name varchar(50) not null,
	duration enum('Unknown', 'Less than a month', '1-3 months', '3-6 months', 'More than 6 months', 'Over a year') not null
);