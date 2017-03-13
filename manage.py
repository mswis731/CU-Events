#!.cs411/bin/python
from flask_script import Manager
from app import app
from app.crawlers.eventful import crawl as eventful_crawl, update_crawled_events as eventful_update
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

@manager.command
def update(site):
	if site == 'all':
		eventful_update()
	elif site == 'eventful':
		eventful_update()


if __name__ == "__main__":
	manager.run()

