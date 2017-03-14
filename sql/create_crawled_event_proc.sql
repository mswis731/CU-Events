DELIMITER $$
CREATE PROCEDURE CreateCrawledEvent(
	_name 			VARCHAR(60),
	_description 	VARCHAR(1000),
	_building 		VARCHAR(60),
	_street 		VARCHAR(30),
	_city 			VARCHAR(30),
	_zipcode 		INTEGER,
	_start_date 	DATE,
	_start_time 	TIME,
	_end_date 		DATE,
	_end_time 		TIME,
	_low_price		REAL,
	_high_price		REAL,
	_url			VARCHAR(150),
	_organizer		VARCHAR(30),
	_site			VARCHAR(40))
BEGIN

	SET sql_mode='';

	IF NOT EXISTS (
				SELECT *
				FROM Event
				WHERE name = _name AND startDate = _start_date AND startTime = _start_time
	) THEN
		INSERT INTO Event(name, description, building, addrAndStreet, city, zipcode,
							startDate, startTime, endDate, endTime, lowPrice, highPrice)
		VALUES (_name, _description, _building, _street, _city, _zipcode,
				_start_date, _start_time, _end_date, _end_time, _low_price, _high_price);
	END IF;

	IF NOT EXISTS (
				SELECT *
				FROM EventCrawled
				WHERE name = _name AND startDate = _start_date AND startTime = _start_time AND url = _url
	) THEN
		INSERT INTO EventCrawled(url, name, startDate, startTime, organizer, site)
		VALUES (_url, _name, _start_date, _start_time, _organizer, _site);
	END IF;
END $$
DELIMITER ;
