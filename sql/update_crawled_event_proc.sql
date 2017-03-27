DROP PROCEDURE IF EXISTS UpdateCrawledEvent;

DELIMITER $$
CREATE PROCEDURE UpdateCrawledEvent(
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
	_url			VARCHAR(150))
BEGIN

	SET sql_mode='';

	IF NOT EXISTS (
				SELECT *
				FROM Event
				WHERE name = _name AND startDate = _start_date AND startTime = _start_time AND description = _description AND building = _building AND addrAndStreet = _street
					  AND city = _city AND zipcode = _zipcode AND endDate = _end_date AND endTime = _end_time AND lowPrice = _low_price AND highPrice = _high_price
	) THEN
		UPDATE Event
		SET name = _name, startDate = _start_date, startTime = _start_time, description = _description, building = _building, addrAndStreet = _street,
			city = _city, zipcode = _zipcode, endDate = _end_date, endTime = _end_time, lowPrice = _low_price, highPrice = _high_price
		WHERE name = (SELECT name FROM EventCrawled WHERE url = _url);
	END IF;
END $$
DELIMITER ;
