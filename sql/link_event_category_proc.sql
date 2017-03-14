DELIMITER $$
CREATE PROCEDURE LinkEventCategory(
	_event_title		VARCHAR(60),
	_event_start_date	DATE,
	_event_start_time	TIME,
	_category_name		VARCHAR(40))
BEGIN

	SET sql_mode='';

	IF EXISTS (SELECT * FROM Event WHERE title = _event_title AND startDate = _event_start_date AND startTime = _event_start_time)
				AND EXISTS (SELECT * FROM Category WHERE name=_category_name)
	THEN
		SET @eid = (SELECT id FROM Event WHERE title = _event_title AND startDate = _event_start_date AND startTime = _event_start_time);
		IF NOT EXISTS (SELECT * FROM HasCategory WHERE eventID=@eid AND categoryName = _category_name)
		THEN
			INSERT INTO HasCategory(eventID, categoryName)
			VALUES (@eid, _category_name);
		END IF;
	END IF;
END $$
DELIMITER ;
