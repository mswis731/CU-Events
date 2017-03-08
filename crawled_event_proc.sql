DELIMITER $$
CREATE PROCEDURE CreateCrawledEvent(
	_name 			VARCHAR(60),
	_description 	VARCHAR(300),
	_building 		VARCHAR(30),
	_street 		VARCHAR(30),
	_city 			VARCHAR(30),
	_zipcode 		INTEGER,
	_start_date 	DATE,
	_start_time 	TIME,
	_end_date 		DATE,
	_end_time 		TIME,
	_prices 		VARCHAR(20),
	_event_type 	VARCHAR(40),
	_url			VARCHAR(150),
	_organizer		VARCHAR(30))
BEGIN

	IF NOT EXISTS (
				SELECT *
				FROM Event
				WHERE name = _name AND startDate = _start_date
	) THEN
		INSERT INTO Event(name, description, building, addrAndStreet, city, zipcode,
							startDate, startTime, endDate, endTime, prices, eventType)
		VALUES (_name, _description, _building, _street, _city, _zipcode,
				_start_date, _start_time, _end_date, _end_time,_prices, _event_type);
	END IF;

	IF NOT EXISTS (
				SELECT *
				FROM EventCrawled
				WHERE name = _name AND startDate = _start_date AND url = _url
	) THEN
		INSERT INTO EventCrawled(url, name, startDate, organizer)
		VALUES (_url, _name, _start_date, _organizer);
	END IF;
END $$
DELIMITER ;
