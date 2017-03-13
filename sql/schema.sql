CREATE TABLE User (
	username			VARCHAR(20) PRIMARY KEY,
	password			VARCHAR(30)
);
CREATE TABLE Message (
	timestamp			DATETIME,
	text				VARCHAR(300),
	username			VARCHAR(20),
	PRIMARY KEY(timestamp, username)
);
CREATE TABLE Community (
	name				VARCHAR(40) PRIMARY KEY,
	creator				VARCHAR(20)
);
CREATE TABLE EventType (
	name				VARCHAR(40) PRIMARY KEY
);
CREATE TABLE Category (
	name				VARCHAR(40) PRIMARY KEY
);
CREATE TABLE Event (
	name				VARCHAR(60),
	description			VARCHAR(1000),
	building			VARCHAR(60),
	addrAndStreet		VARCHAR(30),
	city				VARCHAR(30),
	zipcode				INTEGER,
	startDate			DATE,
	startTime			TIME,
	endDate				DATE,
	endTime				TIME,
	lowPrice			REAL,
	highPrice			REAL,
	nonUserViews		INTEGER DEFAULT 0,
	PRIMARY KEY(name, startDate, startTime)
);
CREATE TABLE EventCrawled (
	url					VARCHAR(150),
	name				VARCHAR(60),
	startDate			DATE,
	startTime			TIME,
	organizer			VARCHAR(30),
	site				VARCHAR(40),
	PRIMARY KEY(url, name, startDate, startTime)
);
CREATE TABLE EventCreated (
	name				VARCHAR(60),
	startDate			DATE,
	startTime			TIME,
	username			VARCHAR(20),
	communityName		VARCHAR(40),
	PRIMARY KEY(name, startDate, startTime)
);
CREATE TABLE HasCategory (
	eventName			VARCHAR(60),
	eventStartDate			DATE,
	eventStartTime			TIME,
	categoryName		VARCHAR(40),
	PRIMARY KEY(eventName, eventStartDate, eventStartTime, categoryName)
);
CREATE TABLE HasEventType (
	eventName			VARCHAR(60),
	eventStartDate			DATE,
	eventStartTime			TIME,
	eventType			VARCHAR(40),
	PRIMARY KEY(eventName, eventStartDate, eventStartTime, eventType)
);
CREATE TABLE Interests (
	username			VARCHAR(20),
	categoryName		VARCHAR(40),
	PRIMARY KEY(username, categoryName)
);
CREATE TABLE RegisteredView (
	eventName			VARCHAR(60),
	eventStartDate			DATE,
	eventStartTime			TIME,
	username			VARCHAR(20),
	PRIMARY KEY(eventName, eventStartDate, eventStartTime, username)
);
CREATE TABLE CommunityMember (
	username			VARCHAR(20),
	communityName		VARCHAR(40),
	PRIMARY KEY(username, communityName)
);
CREATE TABLE SharedEvent (
	eventName			VARCHAR(60),
	eventStartDate			DATE,
	eventStartTime			TIME,
	eventUrl			VARCHAR(150),
	communityName		VARCHAR(40),
	PRIMARY KEY(eventName, eventStartDate, eventStartTime, eventUrl, communityName)
);
