#!.cs411/bin/python
from flask_script import Manager
from app import app
from app.crawlers.eventful import crawl as eventful_crawl
from app.crawlers.county import crawl as county_crawl

manager = Manager(app)

@manager.command
def crawl(site):
	if site == 'all':
		eventful_crawl()
		county_crawl()
	elif site == 'eventful':
		eventful_crawl()
	elif site == 'county':
		county_crawl()


if __name__ == "__main__":
	manager.run()

