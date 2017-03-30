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
	INSERT INTO CommunityCategories(cid, categoryName) VALUES(SELECT cid FROM Community WHERE name=groupname, categories)
END $$
DELIMITER ;

