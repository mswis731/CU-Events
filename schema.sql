CREATE TABLE User (
	username	VARCHAR(20) PRIMARY KEY,
	password	VARCHAR(20)
);
CREATE TABLE Message (
	timestamp	TIME,
	text		VARCHAR(140),
	username	VARCHAR(20),
	PRIMARY KEY(timestamp, username)
);
CREATE TABLE Community (
	name		VARCHAR(20) PRIMARY KEY,
	creator		VARCHAR(20)
);
CREATE TABLE EventType (
	name		VARCHAR(20) PRIMARY KEY
);
CREATE TABLE Category (
	name		VARCHAR(20) PRIMARY KEY
);
CREATE TABLE Event (
	name			VARCHAR(20),
	description		VARCHAR(140),
	location		VARCHAR(80),
	startdate		DATE,
	enddate			DATE,
	price			INTEGER,
	nonUserViews	INTEGER DEFAULT 0,
	typeName		VARCHAR(20),
	PRIMARY KEY(name, start)
);
CREATE TABLE EventCrawled (
	url				VARCHAR(60),
	name			VARCHAR(20),
	start			DATE,
	organizer		VARCHAR(20),
	PRIMARY KEY(url, name, start)
);
CREATE TABLE EventCreated (
	name			VARCHAR(20),
	start			DATE,
	username		VARCHAR(20),
	communityName	VARCHAR(20),
	PRIMARY KEY(name, start)
);
CREATE TABLE HasCategory (
	eventName		VARCHAR(20),
	eventStart		DATE,
	categoryName	VARCHAR(20),
	PRIMARY KEY(eventName, eventStart, categoryName)
);
CREATE TABLE Interests (
	username		VARCHAR(20),
	categoryName	VARCHAR(20),
	PRIMARY KEY(username, categoryName)
);
CREATE TABLE RegisteredView (
	eventName		VARCHAR(20),
	eventStart		DATE,
	username		VARCHAR(20),
	PRIMARY KEY(eventName, eventStart, username)
);
CREATE TABLE CommunityMember (
	username		VARCHAR(20),
	communityName	VARCHAR(20),
	PRIMARY KEY(username, communityName)
);
CREATE TABLE SharedEvent (
	eventName		VARCHAR(20),
	eventStart		DATE,
	eventUrl		VARCHAR(60),
	communityName	VARCHAR(20),
	PRIMARY KEY(eventName, eventStart, eventUrl, communityName)
);
