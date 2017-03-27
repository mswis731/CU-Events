DROP PROCEDURE IF EXISTS CreateCrawledEvent;

DELIMITER $$
CREATE PROCEDURE CreateCrawledEvent(
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
	_url			VARCHAR(150),
	_site			VARCHAR(40),
	_categories_str			VARCHAR(500),
	_event_types_str		VARCHAR(500))
BEGIN

	SET sql_mode='';

	IF NOT EXISTS (
				SELECT *
				FROM Event
				WHERE title = _title AND startDate = _start_date AND startTime = _start_time
	) THEN
		INSERT INTO Event(title, description, building, addrAndStreet, city, zipcode,
							startDate, startTime, endDate, endTime, lowPrice, highPrice)
		VALUES (_title, _description, _building, _street, _city, _zipcode,
				_start_date, _start_time, _end_date, _end_time, _low_price, _high_price);

		SET @eid = (SELECT eid FROM Event WHERE title = _title AND startDate = _start_date AND startTime = _start_time);

		INSERT INTO EventCrawled(eid, url, site)
		VALUES (@eid, _url,_site);

		SET @next = '';
		SET @nextlen = 0;
		SET @value = '';

		categories:
		LOOP
			IF LENGTH(TRIM(_categories_str)) = 0 OR _categories_str IS NULL THEN
				LEAVE categories;
			END IF;

			SET @next = SUBSTRING_INDEX(_categories_str, ',', 1);
			SET @nextlen = LENGTH(@next);
			SET @value = TRIM(@next);

			INSERT INTO HasCategory(eid, categoryName) VALUES (@eid, @value);

			SET _categories_str = INSERT(_categories_str, 1, @nextlen + 1, '');
		END LOOP;

		SET @next = '';
		SET @nextlen = 0;
		SET @value = '';

		event_types:
		LOOP
			IF LENGTH(TRIM(_event_types_str)) = 0 OR _event_types_str IS NULL THEN
				LEAVE event_types;
			END IF;

			SET @next = SUBSTRING_INDEX(_event_types_str, ',', 1);
			SET @nextlen = LENGTH(@next);
			SET @value = TRIM(@next);

			INSERT INTO HasEventType(eid, eventType) VALUES (@eid, @value);

			SET _event_types_str = INSERT(_event_types_str, 1, @nextlen + 1, '');
		END LOOP;
	END IF;
END $$
DELIMITER ;
