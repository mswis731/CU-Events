DELIMITER $$
CREATE PROCEDURE CreateCrawledEvent(
	_name VARCHAR(20),
	_description VARCHAR(140),
	_location VARCHAR(80),
	_start DATE,
	_end DATE,
	_price INTEGER,
	_typeName VARCHAR(20))
BEGIN

	IF NOT EXISTS (
				SELECT *
				FROM Event
				WHERE name = _name AND start = _start
	) THEN
		INSERT INTO Event(name, description, location, start, end, price, typeName)
		VALUES (_name, _description, _location, _start, _end, _price, _typeName);
	END IF;
END $$
DELIMITER ;
