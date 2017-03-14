DELIMITER $$
CREATE PROCEDURE LinkEventCategory(
	_event_name			VARCHAR(60),
	_event_start_date	DATE,
	_event_start_time	TIME,
	_category_name		VARCHAR(40))
BEGIN

	SET sql_mode='';

	IF NOT EXISTS (
			SELECT *
			FROM HasCategory
			WHERE eventName = _event_name AND eventStartDate = _event_start_date AND eventStartTime = _event_start_time AND categoryName = _category_name
	) THEN
		IF EXISTS (SELECT * FROM Category WHERE name = _category_name) THEN
			INSERT INTO HasCategory(eventName, eventStartDate, eventStartTime, categoryName)
			VALUES (_event_name, _event_start_date, _event_start_time, _category_name);
		END IF;
	END IF;
END $$
DELIMITER ;
