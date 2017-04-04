DROP PROCEDURE IF EXISTS CreateUser;

DELIMITER $$
CREATE PROCEDURE CreateUser(
	_firstname		VARCHAR(30),
	_lastname		VARCHAR(30),
	_email 			VARCHAR(50),
	_username		VARCHAR(20),
	_password		VARCHAR(100))
BEGIN 

	SET sql_mode='';
	-- IF NOT EXISTS(
	-- 	SELECT username
	-- 	FROM User	
	-- 	WHERE username = _username)
	-- THEN 
	INSERT INTO User(firstname, lastname, username, email, password) VALUES (_firstname, _lastname, _username, _email, _password); 
END $$
DELIMITER ;
