
use wprojdb_db;

DROP TABLE if exists user;
CREATE TABLE user(
	uid int(10) unsigned AUTO_INCREMENT PRIMARY KEY NOT NULL,
    email varchar(50) NOT NULL,
    name varchar(50) NOT NULL,
    role set('student', 'client', 'administrator') NOT NULL,
	hashed char(60) NOT NULL
) engine=InnoDB;

DROP TABLE if exists project;
CREATE TABLE project(
	pid int(10) unsigned AUTO_INCREMENT PRIMARY KEY NOT NULL,
	creator int(10) unsigned NOT NULL,
	approver int(10) unsigned, 
	name varchar(50) NOT NULL,
	requirements varchar(150) NOT NULL,
	compensation varchar(100) NOT NULL,
	rolesOpen int(3) NOT NULL,
	description varchar(300) NOT NULL,
	duration enum('Unknown', 'Less than a month', '1-3 months', '3-6 months', 'More than 6 months', 'Over a year') not null,
	foreign key (creator) references user(uid) on delete cascade on update cascade,
	foreign key (approver) references user(uid) on delete set null on update cascade
) engine=InnoDB;

DROP TABLE if exists application;
CREATE TABLE application(
	uid int(10) unsigned NOT NULL,
	pid int(10) unsigned NOT NULL,
	foreign key (uid) references user(uid) on delete cascade on update cascade, 
	foreign key (pid) references project(pid) on delete cascade on update cascade
) engine=InnoDB;