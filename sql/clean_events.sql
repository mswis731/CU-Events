DELIMITER $$
CREATE PROCEDURE CleanEvents()
BEGIN

	SET sql_mode='';

	DELETE FROM Event WHERE (endDate IS NULL AND DATEDIFF(CURRENT_DATE(), startDate) > 7)
						OR  (endDate IS NOT NULL and DATEDIFF(CURRENT_DATE(), endDate) > 7);
END $$
DELIMITER ;
