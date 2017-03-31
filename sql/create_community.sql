DROP PROCEDURE IF EXISTS CreateCommunity;

DELIMITER $$
CREATE PROCEDURE CreateCommunity(
	groupname		VARCHAR(40),
	categories		VARCHAR(40))
BEGIN 

	SET sql_mode='';
	-- IF NOT EXISTS(
	-- 	SELECT username
	-- 	FROM User	
	-- 	WHERE username = _username)
	-- THEN 
	INSERT INTO Community(name, uid) VALUES (groupname, 0);
	DECLARE @cid INTEGER;
	SET @cid = (SELECT cid 
		    FROM Community 
		    WHERE name=groupname);

	INSERT INTO CommunityCategories(cid, categoryName) VALUES(@cid, categories)
END $$
DELIMITER ;

