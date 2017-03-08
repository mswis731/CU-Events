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
	description			VARCHAR(300),
	building			VARCHAR(30),
	addrAndStreet		VARCHAR(30),
	city				VARCHAR(30),
	zipcode				INTEGER,
	startDate			DATE,
	startTime			TIME,
	endDate				DATE,
	endTime				TIME,
	prices				VARCHAR(20),
	nonUserViews		INTEGER DEFAULT 0,
	eventType			VARCHAR(40),
	PRIMARY KEY(name, startDate)
);
CREATE TABLE EventCrawled (
	url					VARCHAR(150),
	name				VARCHAR(60),
	startDate			DATE,
	organizer			VARCHAR(30),
	PRIMARY KEY(url, name, startDate)
);
CREATE TABLE EventCreated (
	name				VARCHAR(60),
	startDate			DATE,
	username			VARCHAR(20),
	communityName		VARCHAR(40),
	PRIMARY KEY(name, startDate)
);
CREATE TABLE HasCategory (
	eventName			VARCHAR(60),
	eventStartDate		DATE,
	categoryName		VARCHAR(40),
	PRIMARY KEY(eventName, eventStartDate, categoryName)
);
CREATE TABLE Interests (
	username			VARCHAR(20),
	categoryName		VARCHAR(40),
	PRIMARY KEY(username, categoryName)
);
CREATE TABLE RegisteredView (
	eventName			VARCHAR(60),
	eventStartDate		DATE,
	username			VARCHAR(20),
	PRIMARY KEY(eventName, eventStartDate, username)
);
CREATE TABLE CommunityMember (
	username			VARCHAR(20),
	communityName		VARCHAR(40),
	PRIMARY KEY(username, communityName)
);
CREATE TABLE SharedEvent (
	eventName			VARCHAR(60),
	eventStartDate		DATE,
	eventUrl			VARCHAR(150),
	communityName		VARCHAR(40),
	PRIMARY KEY(eventName, eventStartDate, eventUrl, communityName)
);
