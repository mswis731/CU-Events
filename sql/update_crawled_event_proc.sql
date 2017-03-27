DROP PROCEDURE IF EXISTS UpdateCrawledEvent;

DELIMITER $$
CREATE PROCEDURE UpdateCrawledEvent(
	_title 				VARCHAR(60),
	_description 		VARCHAR(1000),
	_building 			VARCHAR(60),
	_street 			VARCHAR(30),
	_city 				VARCHAR(30),
	_zipcode 			INTEGER,
	_start_date 		DATE,
	_start_time 		TIME,
	_end_date 			DATE,
	_end_time 			TIME,
	_low_price			REAL,
	_high_price			REAL,
	_url				VARCHAR(150),
	_categories_str		VARCHAR(500),
	_event_types_str	VARCHAR(500))
BEGIN

	SET sql_mode='';

	SET @eid = (SELECT eid FROM EventCrawled WHERE url = _url);
	IF @eid
	THEN
		UPDATE Event
		SET title = _title, startDate = _start_date, startTime = _start_time, description = _description, building = _building, addrAndStreet = _street,
			city = _city, zipcode = _zipcode, endDate = _end_date, endTime = _end_time, lowPrice = _low_price, highPrice = _high_price
		WHERE eid = @eid;

		DELETE FROM HasCategory WHERE eid = @eid;
		DELETE FROM HasEventType WHERE eid = @eid;

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
