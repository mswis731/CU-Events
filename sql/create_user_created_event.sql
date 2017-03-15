DROP PROCEDURE IF EXISTS CreateUserEvent;
DELIMITER $$
CREATE PROCEDURE CreateUserEvent(
	_id				INTEGER,
	_title 			VARCHAR(60),
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
	_category_name	VARCHAR(40),
	_event_type		VARCHAR(40))
BEGIN

	SET sql_mode='';
	
	IF _id=-1
	THEN
		INSERT INTO Event(title, description, building, addrAndStreet, city, zipcode,
							startDate, startTime, endDate, endTime, lowPrice, highPrice)
		VALUES (_title, _description, _building, _street, _city, _zipcode,
				_start_date, _start_time, _end_date, _end_time, _low_price, _high_price);
		SET @eid = (SELECT id FROM Event WHERE title = _title AND startDate = _start_date AND startTime = _start_time);
		INSERT INTO HasCategory(eventID, categoryName) VALUES (@eid, _category_name);
		INSERT INTO HasEventType(eventID, eventType) VALUES (@eid, _event_type);
	ELSE	
		UPDATE Event
		SET title = _title, startDate = _start_date, startTime = _start_time, description = _description, building = _building, addrAndStreet = _street,
		city = _city, zipcode = _zipcode, endDate = _end_date, endTime = _end_time, lowPrice = _low_price, highPrice = _high_price
		WHERE id=_id;
		DELETE FROM HasCategory WHERE eventID=_id;
		INSERT INTO HasCategory(eventID, categoryName) VALUES (_id, _category_name);
		DELETE FROM HasEventType WHERE eventID=_id;
		INSERT INTO HasEventType(eventID, eventType) VALUES (_id, _event_type);
	END IF;
END $$
DELIMITER ;
