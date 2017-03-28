DELETE FROM Category;

INSERT INTO Category(name)
VALUES ('Music'),
	   ('Sports'),
	   ('Academic'),
	   ('Technology'),
	   ('Family'),
	   ('Health and Wellness'),
	   ('Outdoors'),
	   ('University'),
	   ('Arts and Theatre'),
	   ('Holiday'),
	   ('Government'),
	   ('Home and Lifestyle'),
	   ('Food and Drink'),
	   ('Other');

DELETE FROM EventType;

INSERT INTO EventType(name)
VALUES ('Concerts'),
	   ('Conferences'),
	   ('Talks'),
	   ('Networking and Career Fairs'),
	   ('Galleries and Exhibits'),
	   ('Charity'),
	   ('Festivals and Fairs'),
	   ('Other');
