DELIMITER $$
CREATE PROCEDURE CreateCrawledEvent(
	_name 			VARCHAR(60),
	_description 	VARCHAR(1000),
	_building 		VARCHAR(60),
	_street 		VARCHAR(30),
	_city 			VARCHAR(30),
	_zipcode 		INTEGER,
	_start 			DATETIME,
	_end 			DATETIME,
	_low_price		REAL,
	_high_price		REAL,
	_url			VARCHAR(150),
	_organizer		VARCHAR(30))
BEGIN

	SET sql_mode='';

	IF NOT EXISTS (
				SELECT *
				FROM Event
				WHERE name = _name AND startTime = _start
	) THEN
		INSERT INTO Event(name, description, building, addrAndStreet, city, zipcode,
							startTime, endTime, lowPrice, highPrice)
		VALUES (_name, _description, _building, _street, _city, _zipcode,
				_start, _end, _low_price, _high_price);
	END IF;

	IF NOT EXISTS (
				SELECT *
				FROM EventCrawled
				WHERE name = _name AND startTime = _start AND url = _url
	) THEN
		INSERT INTO EventCrawled(url, name, startTime, organizer)
		VALUES (_url, _name, _start, _organizer);
	END IF;
END $$
DELIMITER ;
