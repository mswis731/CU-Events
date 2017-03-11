DELIMITER $$
CREATE PROCEDURE LinkEventType(
	_event_name		VARCHAR(60),
	_event_start	DATETIME,
	_event_type		VARCHAR(40))
BEGIN

	SET sql_mode='';

	IF NOT EXISTS(
			SELECT *
			FROM HasEventType
			WHERE eventName = _event_name AND eventStartTime = _event_start AND eventType = _event_type
	) THEN
		INSERT INTO HasEventType(eventName, eventStartTime, eventType)
		VALUES (_event_name, _event_start, _event_type);
	END IF;
END $$
DELIMITER ;
