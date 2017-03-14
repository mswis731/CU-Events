DELIMITER $$
CREATE PROCEDURE LinkEventType(
	_event_title		VARCHAR(60),
	_event_start_date	DATE,
	_event_start_time	TIME,
	_event_type			VARCHAR(40))
BEGIN

	SET sql_mode='';

	IF EXISTS (SELECT * FROM Event WHERE title = _event_title AND startDate = _event_start_date AND startTime = _event_start_time)
				AND EXISTS (SELECT * FROM EventType WHERE name=_event_type)
	THEN
		SET @eid = (SELECT id FROM Event WHERE title = _event_title AND startDate = _event_start_date AND startTime = _event_start_time);
		IF NOT EXISTS (SELECT * FROM HasEventType WHERE eventID=@eid AND eventType = _event_type)
		THEN
			INSERT INTO HasEventType(eventID, eventType)
			VALUES (@eid, _event_type);
		END IF;
	END IF;
END $$
DELIMITER ;
