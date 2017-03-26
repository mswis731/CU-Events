CREATE TABLE User (
	id					INTEGER NOT NULL AUTO_INCREMENT,
	firstname			VARCHAR(30)
	lastname			VARCHAR(30)
	username			VARCHAR(20) NOT NULL UNIQUE,
	password			VARCHAR(30),
	PRIMARY KEY(id)
);
CREATE TABLE Message (
	timestamp			DATETIME,
	text				VARCHAR(300),
	userID				INTEGER,
	FOREIGN KEY(userID) REFERENCES User(id) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(timestamp, userID)
);
CREATE TABLE Community (
	id					INTEGER NOT NULL AUTO_INCREMENT,
	name				VARCHAR(40),
	creatorID			INTEGER,
	FOREIGN KEY(creatorID) REFERENCES User(id) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(id)
);
CREATE TABLE EventType (
	name				VARCHAR(40),
	PRIMARY KEY(name)
);
CREATE TABLE Category (
	name				VARCHAR(40),
	PRIMARY KEY(name)
);
CREATE TABLE Event (
	id					INTEGER NOT NULL AUTO_INCREMENT,
	title				VARCHAR(60),
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
	PRIMARY KEY(id)
);
CREATE TABLE EventCrawled (
	eventID				INTEGER,
	url					VARCHAR(150) UNIQUE,
	site				VARCHAR(40),
	FOREIGN KEY(eventID) REFERENCES Event(id) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(eventID)
);
CREATE TABLE EventCreated (
	eventID				INTEGER,
	userID				INTEGER,
	communityID			INTEGER,
	FOREIGN KEY(eventID) REFERENCES Event(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(userID) REFERENCES User(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(communityID) REFERENCES Community(id) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(eventID)
);
CREATE TABLE HasCategory (
	eventID				INTEGER,
	categoryName		VARCHAR(40),
	FOREIGN KEY(eventID) REFERENCES Event(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(categoryName) REFERENCES Category(name) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(eventID, categoryName)
);
CREATE TABLE HasEventType (
	eventID				INTEGER,
	eventType			VARCHAR(40),
	FOREIGN KEY(eventID) REFERENCES Event(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(eventType) REFERENCES EventType(name) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(eventID, eventType)
);
CREATE TABLE Interests (
	userID				INTEGER,
	categoryName		VARCHAR(40),
	FOREIGN KEY(userID) REFERENCES User(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(categoryName) REFERENCES Category(name) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(userID, categoryName)
);
CREATE TABLE RegisteredView (
	eventID				INTEGER,
	userID				INTEGER,
	FOREIGN KEY(eventID) REFERENCES Event(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(userID) REFERENCES User(id) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(eventID, userID)
);
CREATE TABLE CommunityMember (
	userID				INTEGER,
	communityID			INTEGER,
	FOREIGN KEY(userID) REFERENCES User(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(communityID) REFERENCES Community(id) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(userID, communityID)
);
CREATE TABLE SharedEvent (
	eventID				INTEGER,
	communityID			INTEGER,
	FOREIGN KEY(eventID) REFERENCES EventCrawled(eventID) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(communityID) REFERENCES Community(id) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(eventID, communityID)
);
