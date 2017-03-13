DELIMITER $$
CREATE PROCEDURE LinkEventType(
	_event_name			VARCHAR(60),
	_event_start_date	DATE,
	_event_start_time	TIME,
	_event_type		VARCHAR(40))
BEGIN

	SET sql_mode='';

	IF NOT EXISTS(
			SELECT *
			FROM HasEventType
			WHERE eventName = _event_name AND eventStartDate = _event_start_date AND eventStartTime = _event_start_time AND eventType = _event_type
	) THEN
		INSERT INTO HasEventType(eventName, eventStartDate, eventStartTime, eventType)
		VALUES (_event_name, _event_start_date, _event_start_time, _event_type);
	END IF;
END $$
DELIMITER ;
