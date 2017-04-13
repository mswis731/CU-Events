DROP PROCEDURE IF EXISTS CreateCommunity;

DELIMITER $$
CREATE PROCEDURE CreateCommunity(
	_groupname				VARCHAR(40),
	_uid					INTEGER,
	_categories_str			VARCHAR(500))
BEGIN 

	SET sql_mode='';

	INSERT INTO Community(name, uid) VALUES (_groupname, _uid);

	SET @cid = (SELECT cid 
		    FROM Community 
		    WHERE name=_groupname);

	categories:
	LOOP
		IF LENGTH(TRIM(_categories_str)) = 0 OR _categories_str IS NULL THEN
			LEAVE categories;
		END IF;

		SET @next = SUBSTRING_INDEX(_categories_str, ',', 1);
		SET @nextlen = LENGTH(@next);
		SET @value = TRIM(@next);

		INSERT INTO CommunityCategories(cid, categoryName) VALUES(@cid, @value);

		SET _categories_str = INSERT(_categories_str, 1, @nextlen + 1, '');
	END LOOP;
END $$
DELIMITER ;

