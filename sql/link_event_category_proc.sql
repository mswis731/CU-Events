DELIMITER $$
CREATE PROCEDURE LinkEventCategory(
	_event_name			VARCHAR(60),
	_event_start		DATETIME,
	_category_name		VARCHAR(40))
BEGIN

	SET sql_mode='';

	IF NOT EXISTS(
			SELECT *
			FROM HasCategory
			WHERE eventName = _event_name AND eventStartTime = _event_start AND categoryName = _category_name
	) THEN
		INSERT INTO HasCategory(eventName, eventStartTime, categoryName)
		VALUES (_event_name, _event_start, _category_name);
	END IF;
END $$
DELIMITER ;
